#!/usr/bin/env python3
"""Language-aware parser / validity validator for the Swarm Traces payload dataset."""
import argparse, ast, csv, html.parser, json, os, re, subprocess, sys, tempfile
from collections import Counter, OrderedDict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INPUT = os.path.join(REPO_ROOT, "Data", "redacted.jsonl")
DEFAULT_OUTPUT = "/Users/id19/scratchpad/payload_parser_validation"

JS_MARKERS = ("fetch(", "document.", "XMLHttpRequest", "new Image")
PY_MARKERS = ("import ", "pushblob")
PY_TOKEN_MARKERS = ("socket", "ssl", "base64")
DOCKER_MARKERS = ("schemaVersion", '"mediaType"', '"rootfs"', "'config'")
HTML_MARKERS = ("<iframe", "<script", "<img")
SHELL_COMMAND_MARKERS = ("curl", "echo", "python3", "src/main.c")


def detect_families(text):
    families = []
    if any(m in text for m in JS_MARKERS) or (
        "eval(" in text and "atob(" in text and "location.hash" in text
    ):
        families.append("JavaScript")
    if (any(m in text for m in PY_MARKERS)
            or re.search(r"\bimport\b", text)
            or any(m in text.lower() for m in PY_TOKEN_MARKERS)):
        families.append("Python")
    if any(m in text for m in DOCKER_MARKERS):
        families.append("DockerJSON")
    if any(m in text for m in HTML_MARKERS):
        families.append("HTML")
    if ";" in text and any(m in text for m in SHELL_COMMAND_MARKERS):
        families.append("Shell")
    if not families:
        families.append("Unknown")
    return families


def primary_family(text, families):
    low = text.lstrip()
    if low.startswith(("<iframe", "<script", "<img")) or low.startswith("X<"):
        return "HTML"
    if low.startswith(("import ", "from ", "pushblob")):
        return "Python"
    if (low.startswith("{") or low.startswith("[")) and "DockerJSON" in families:
        return "DockerJSON"
    if re.fullmatch(r"[ \t\r\n]*https?://[^\n]*", text.strip()):
        return "BareURL"
    if "JavaScript" in families:
        return "JavaScript"
    if "Shell" in families:
        return "Shell"
    return "Unknown"


def redaction_defect_flags(text):
    flags = []
    if "[ENCODED BLOB]" in text:
        flags.append("encoded_blob_token")
    if re.search(r"\]\"", text):
        flags.append("missing_backslash_escape")
    if re.search(r"\[[A-Z][^\]]* [^\]]*\]", text):
        flags.append("redaction_token_with_space")
    return flags


def scan_balance(text):
    single = double = back = 0
    stack = []
    closers = {")": "(", "]": "[", "}": "{"}
    in_str = None
    escape = False
    malformed = False
    for c in text:
        if in_str is not None:
            if escape:
                escape = False
                continue
            if c == "\\":
                escape = True
                continue
            if c == in_str:
                in_str = None
            continue
        if c in ("'", '"', "`"):
            in_str = c
            if c == "'":
                single += 1
            elif c == '"':
                double += 1
            else:
                back += 1
            continue
        if c in "([ {":
            stack.append(c)
        elif c in ")]}":
            if not stack or stack[-1] != closers[c]:
                malformed = True
            else:
                stack.pop()
    quote_ok = (single % 2 == 0) and (double % 2 == 0) and (back % 2 == 0)
    bracket_ok = (len(stack) == 0) and (not malformed)
    return {
        "quote_ok": quote_ok,
        "bracket_ok": bracket_ok,
        "balanced": bool(quote_ok and bracket_ok),
        "final_open_quotes": {"single": single % 2, "double": double % 2, "backtick": back % 2},
        "unclosed_groups": len(stack),
        "malformed_nesting": malformed,
    }


def extract_json_candidates(text):
    cands = []
    n = len(text)
    i = 0
    while i < n:
        if text[i] in "{[":
            depth = 0
            in_str = False
            escape = False
            start = i
            j = i
            while j < n:
                ch = text[j]
                if in_str:
                    if escape:
                        escape = False
                    elif ch == "\\":
                        escape = True
                    elif ch == '"':
                        in_str = False
                else:
                    if ch == '"':
                        in_str = True
                    elif ch in "{[":
                        depth += 1
                    elif ch in "}]":
                        depth -= 1
                        if depth == 0 and j > start:
                            cands.append(text[start:j + 1])
                            i = j
                            break
                j += 1
            if j >= n:
                break
        i += 1
    out = []
    seen = set()
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def run_python_parse(text):
    try:
        ast.parse(text)
        return {"status": "success", "error": None}
    except SyntaxError as e:
        return {
            "status": "fail",
            "error": str(e),
            "line": e.lineno,
            "offset": e.offset,
            "text": (e.text or "").strip()[:160],
        }
    except ValueError as e:
        return {"status": "fail", "error": "ValueError: %s" % e}


def extract_js_string_candidates(text):
    """Extract JS string-literal contents (single/double/backtick) with escape decoding."""
    cands = []
    n = len(text)
    i = 0
    while i < n:
        if text[i] in "\x27\"`\"":
            quote = text[i]
            i += 1
            buf = []
            while i < n:
                c = text[i]
                if c == "\\":
                    nxt = text[i + 1] if (i + 1 < n) else ""
                    table = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "'": "'", "`": "`", "\\": "\\"}
                    buf.append(table.get(nxt, nxt))
                    i += 2
                    continue
                if c == quote:
                    break
                buf.append(c)
                i += 1
            if i < n:
                cands.append("".join(buf))
                i += 1
            else:
                break
        else:
            i += 1
    return cands



def run_json_parse(text):
    try:
        json.loads(text)
        return {"status": "success", "mode": "whole_text", "candidates": 0, "candidates_ok": 1}
    except Exception as whole_err:
        # Prefer JS string-literal contents (Docker/JSON manifests are embedded
        # as quoted JS strings). Fall back to brace-slice scanner if needed.
        js_str_cands = extract_js_string_candidates(text)
        cands = []
        for s in js_str_cands:
            ss = s.strip()
            if (ss.startswith("{") or ss.startswith("[")):
                cands.append(ss)
        if not cands:
            cands = [c for c in extract_json_candidates(text) if DOCKER_MARKERS and any(m in c for m in DOCKER_MARKERS)]
        ok = 0
        first_fail = None
        first_ok = None
        for c in cands:
            try:
                json.loads(c)
                ok += 1
                if first_ok is None:
                    first_ok = c[:120]
            except Exception as e:
                if first_fail is None:
                    first_fail = str(e)
        if cands and ok > 0:
            return {
                "status": "success_embedded",
                "mode": "embedded_candidates",
                "candidates": len(cands),
                "candidates_ok": ok,
                "whole_error": str(whole_err)[:200],
                "first_ok_snippet": first_ok,
            }
        return {
            "status": "fail",
            "mode": "embedded_candidates",
            "candidates": len(cands),
            "candidates_ok": ok,
            "whole_error": str(whole_err)[:200],
            "first_fail": first_fail,
        }


def node_check(text, tmpdir, timeout=15):
    path = os.path.join(tmpdir, "node_check_tmp.js")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        proc = subprocess.run(
            ["node", "--check", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        if proc.returncode == 0:
            return {"status": "success", "returncode": 0, "error": None}
        err_lines = [ln for ln in proc.stderr.splitlines() if ln.strip()]
        msg = "\n".join(err_lines[-4:])[:1000]
        return {"status": "fail", "returncode": proc.returncode, "error": msg}
    except FileNotFoundError:
        return {"status": "skipped", "returncode": None, "error": "node binary not found"}
    except subprocess.TimeoutExpired:
        return {"status": "fail", "returncode": -1, "error": "timeout after %ss" % timeout}
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def html_fragment_check(text):
    class _P(html.parser.HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self._ok = True
    p = _P()
    try:
        p.feed(text)
        p.close()
        return {"status": "success", "error": None}
    except Exception as e:
        return {"status": "fail", "error": str(e)[:300]}


def classify_js_failure(text, node_result):
    if node_result.get("status") == "success":
        return "none"
    flags = redaction_defect_flags(text)
    if flags:
        if "missing_backslash_escape" in flags and "encoded_blob_token" in flags:
            return "redaction_defect:missing_backslash+encoded_blob"
        if "missing_backslash_escape" in flags:
            return "redaction_defect:missing_backslash_escape"
        if "encoded_blob_token" in flags:
            return "redaction_defect:encoded_blob_token"
        return "redaction_defect:" + "+".join(flags)
    err = (node_result.get("error") or "").lower()
    if "unexpected identifier" in err or "unexpected token" in err:
        return "likely_redaction_defect:unquoted_expanded_token"
    if "unexpected end of input" in err:
        return "likely_redaction_defect:truncated_template"
    return "genuine_or_unclassified_syntax"


def validate_row(row, tmpdir, node_timeout):
    text = row["text"]
    families = detect_families(text)
    prim = primary_family(text, families)
    result = OrderedDict()
    result["id"] = row["id"]
    result["cite"] = row.get("cite")
    result["dataset_kind"] = row.get("kind")
    result["parent_id"] = row.get("parent_id")
    result["text_length"] = len(text)
    result["families"] = families
    result["primary_family"] = prim
    result["redaction_defect_flags"] = redaction_defect_flags(text)
    result["parse"] = OrderedDict()
    parse_ok = {}
    if "Python" in families:
        pr = run_python_parse(text)
        result["parse"]["python"] = pr
        parse_ok["python"] = (pr["status"] == "success")
    if "DockerJSON" in families:
        jr = run_json_parse(text)
        result["parse"]["docker_json"] = jr
        parse_ok["docker_json"] = (str(jr["status"]).startswith("success"))
    if "JavaScript" in families:
        nr = node_check(text, tmpdir, node_timeout)
        result["parse"]["javascript"] = nr
        result["js_failure_class"] = classify_js_failure(text, nr)
        parse_ok["javascript"] = (nr["status"] == "success")
    if "Shell" in families:
        br = scan_balance(text)
        result["parse"]["shell_heuristic"] = br
        parse_ok["shell"] = (br["balanced"] is True)
    if "HTML" in families:
        hr = html_fragment_check(text)
        result["parse"]["html_fragment"] = hr
        parse_ok["html"] = (hr["status"] == "success")
    result["parse_ok"] = parse_ok
    result["text_snippet"] = text[:240].replace("\n", " ")
    return result


def summarize(results):
    families_count = Counter()
    primary_count = Counter()
    dataset_kind_count = Counter()
    for r in results:
        for f in r["families"]:
            families_count[f] += 1
        primary_count[r["primary_family"]] += 1
        dataset_kind_count[r["dataset_kind"]] += 1
    family_parse = {}
    for famkey, parsekey in (("JavaScript", "javascript"), ("Python", "python"),
                             ("DockerJSON", "docker_json"), ("Shell", "shell"),
                             ("HTML", "html")):
        rows = [r for r in results if famkey in r["families"]]
        if parsekey == "shell":
            ok = sum(1 for r in rows if r["parse"].get("shell_heuristic", {}).get("balanced") is True)
        elif parsekey == "html":
            ok = sum(1 for r in rows if r["parse"].get("html_fragment", {}).get("status") == "success")
        else:
            ok = sum(1 for r in rows if str(r["parse"].get(parsekey, {}).get("status", "")).startswith("success"))
        family_parse[famkey] = {
            "rows_detected": len(rows),
            "parse_success": ok,
            "parse_fail": len(rows) - ok,
            "success_rate": (round(100.0 * ok / len(rows), 1) if rows else 0.0),
        }
    js_reason = Counter()
    for r in results:
        if "JavaScript" in r["families"]:
            js_reason[r.get("js_failure_class", "n/a")] += 1
    defect_flag_counts = Counter()
    for r in results:
        for f in r.get("redaction_defect_flags", []):
            defect_flag_counts[f] += 1
    return {
        "sample_rows": len(results),
        "dataset_kind_counts": dict(dataset_kind_count),
        "family_marker_counts_multi_label": dict(families_count),
        "primary_family_counts": dict(primary_count),
        "family_parse_summary": family_parse,
        "js_failure_class_counts": dict(js_reason),
        "redaction_defect_flag_counts": dict(defect_flag_counts),
    }


def find_representatives(all_rows, start_index, already_ids, criteria, max_rows=5):
    found = []
    found_criteria = set()
    for idx in range(start_index, len(all_rows)):
        if len(found) >= max_rows:
            break
        row = all_rows[idx]
        if row["id"] in already_ids:
            continue
        for crit in criteria:
            if crit["name"] in found_criteria:
                continue
            try:
                if crit["predicate"](row):
                    found.append({"criterion": crit["name"], "index": idx + 1, "row": row})
                    found_criteria.add(crit["name"])
                    break
            except Exception:
                continue
    return found


def read_rows(path):
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--output-dir", default=DEFAULT_OUTPUT)
    ap.add_argument("--sample-start", type=int, default=1)
    ap.add_argument("--sample-end", type=int, default=500)
    ap.add_argument("--node-timeout", type=int, default=15)
    ap.add_argument("--include-representatives", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    tmpdir = os.path.join(args.output_dir, "_js_tmp")
    os.makedirs(tmpdir, exist_ok=True)

    all_rows = read_rows(args.input)
    total = len(all_rows)
    s = max(1, args.sample_start)
    e = min(total, args.sample_end)
    sample_rows = [all_rows[i] for i in range(s - 1, e)]
    print("[validator] input=%s total_rows=%d" % (args.input, total), flush=True)
    print("[validator] sample rows %d..%d count=%d" % (s, e, len(sample_rows)), flush=True)

    results = []
    n = len(sample_rows)
    for k, row in enumerate(sample_rows, 1):
        r = validate_row(row, tmpdir, args.node_timeout)
        r["source"] = "sample"
        r["sample_index"] = (s + k - 1)
        results.append(r)
        if k % 50 == 0 or k == n:
            print("[validator] validated %d/%d" % (k, n), flush=True)

    extra_results = []
    if args.include_representatives:
        criteria = [
            {"name": "first recovered_text row (late dataset)", "predicate": lambda r: r.get("kind") == "recovered_text"},
            {"name": "first response row (late dataset)", "predicate": lambda r: r.get("kind") == "response"},
            {"name": "first Docker-marker row after sample", "predicate": lambda r: any(m in r["text"] for m in DOCKER_MARKERS)},
            {"name": "first [ENCODED BLOB] row after sample", "predicate": lambda r: "[ENCODED BLOB]" in r["text"]},
        ]
        reps = find_representatives(all_rows, e, {r["id"] for r in sample_rows}, criteria, max_rows=5)
        print("[validator] representatives selected: %d" % len(reps), flush=True)
        for rep in reps:
            rr = validate_row(rep["row"], tmpdir, args.node_timeout)
            rr["source"] = "representative"
            rr["representative_criterion"] = rep["criterion"]
            rr["sample_index"] = rep["index"]
            extra_results.append(rr)
        results_for_summary = results + extra_results
    else:
        results_for_summary = results

    write_json(os.path.join(args.output_dir, "sample_validation_results.json"), results)
    if extra_results:
        write_json(os.path.join(args.output_dir, "representative_validation_results.json"), extra_results)

    failure_examples = []
    for r in results:
        has_fail = False
        for pkey, pval in (r.get("parse") or {}).items():
            if isinstance(pval, dict):
                if pval.get("balanced") is True:
                    continue
                if str(pval.get("status", "")).startswith("success"):
                    continue
                has_fail = True
        if has_fail:
            failure_examples.append({
                "id": r["id"],
                "families": r["families"],
                "primary_family": r["primary_family"],
                "parse": r["parse"],
                "js_failure_class": r.get("js_failure_class"),
                "redaction_defect_flags": r["redaction_defect_flags"],
                "snippet": r["text_snippet"],
            })
    write_json(os.path.join(args.output_dir, "failure_examples_sample.json"), failure_examples)

    summary_sample = summarize(results)
    summary_sample["scope"] = "rows %d..%d" % (s, e)
    write_json(os.path.join(args.output_dir, "summary_sample_1_500.json"), summary_sample)
    write_jsonl(os.path.join(args.output_dir, "sample_validation_results.jsonl"), results)

    csv_path = os.path.join(args.output_dir, "family_counts_sample.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["family", "rows_detected", "parse_success", "parse_fail", "success_rate"])
        for fam, info in summary_sample["family_parse_summary"].items():
            w.writerow([fam, info["rows_detected"], info["parse_success"], info["parse_fail"], info["success_rate"]])

    if extra_results:
        write_json(os.path.join(args.output_dir, "summary_representatives.json"), summarize(extra_results))

    try:
        for fn in os.listdir(tmpdir):
            os.unlink(os.path.join(tmpdir, fn))
        os.rmdir(tmpdir)
    except OSError:
        pass

    print("\n[validator] SUMMARY (sample):", flush=True)
    print(json.dumps(summary_sample, indent=2), flush=True)
    if extra_results:
        print("\n[validator] representative summary:", flush=True)
        print(json.dumps(summarize(extra_results), indent=2), flush=True)
    print("\n[validator] outputs in %s" % args.output_dir, flush=True)


if __name__ == "__main__":
    main()
