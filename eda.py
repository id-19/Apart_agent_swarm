"""Basic EDA for the swarm-agent samples dataset (Data/redacted.jsonl).

Run:  python3 eda.py
Uses Polars; streams the JSONL without materializing proxies of the text.
"""
from __future__ import annotations

import collections
import hashlib
import re
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Data" / "redacted.jsonl"
GZ = ROOT / "Data" / "redacted.jsonl.gz"


def section(title: str) -> None:
    print(f"\n{'=' * 20} {title} {'=' * 20}")


def main() -> None:
    section("LOAD")
    schema_overrides = {"parent_id": pl.Utf8, "time_utc": pl.Utf8}
    df = pl.read_ndjson(DATA, schema_overrides=schema_overrides)
    print(f"file: {DATA}")
    print(f"shape: {df.shape[0]:,} rows x {df.shape[1]} cols")
    print(f"columns: {', '.join(df.columns)}")
    print(f"estimated size in memory: {df.estimated_size('mb'):.1f} MB")

    section("NULLS / COMPLETENESS")
    for col in df.columns:
        n_null = int(df[col].is_null().sum()) + int((df[col] == "").sum()) if col == "tags" else int(df[col].is_null().sum())
        # For tags, empty string is the "missing" sentinel in this dataset.
        miss = int(df[col].is_null().sum())
        if col == "tags":
            miss = int((df[col].is_null() | (df[col] == "")).sum())
        print(f"  {col:10s} null/empty = {miss:7,} / {df.height:,}  ({miss / df.height:.1%})")

    section("IDENTIFIERS")
    print("  unique id    :", df["id"].n_unique())
    print("  unique cite  :", df["cite"].n_unique())
    print("  duplicate ids:", df.height - df["id"].n_unique())
    print("  cite matches id prefix for all rows:",
          bool((df["cite"].str.split(":").list.get(0) == df["id"]).all()))

    section("KIND DISTRIBUTION")
    kinds = df.group_by("kind").agg(pl.len().alias("n")).sort("n", descending=True)
    for row in kinds.iter_rows(named=True):
        print(f"  {row['kind']:16s} {row['n']:7,}  ({row['n'] / df.height:.1%})")

    section("LINEAGE / PARENT GRAPH")
    has_parent = df.filter(pl.col("parent_id").is_not_null())
    id2kind = dict(zip(df["id"].to_list(), df["kind"].to_list()))
    print(f"  records with parent_id : {has_parent.height:,} ({has_parent.height / df.height:.1%})")
    print(f"  records without parent  : {df.height - has_parent.height:,}")
    print(f"  unique parents cited    : {has_parent['parent_id'].n_unique():,}")
    exists = has_parent["parent_id"].is_in(df["id"].implode())
    print(f"  all cited parents exist : {bool(exists.all())} (dangling={int((~exists).sum())})")
    child_parent = has_parent.with_columns(
        pl.col("parent_id").map_elements(lambda x: id2kind.get(x), return_dtype=pl.Utf8).alias("parent_kind")
    )
    cp = child_parent.group_by(["kind", "parent_kind"]).agg(pl.len().alias("n")).sort(["kind", "parent_kind"])
    for row in cp.iter_rows(named=True):
        print(f"    child={row['kind']:16s} parent={row['parent_kind']:16s} n={row['n']:,}")
    pc = has_parent.group_by("parent_id").agg(pl.len().alias("children"))
    print(f"  parents with >1 child   : {pc.filter(pl.col('children') > 1).height:,}")
    print(f"  max children per parent : {pc['children'].max()}")
    print(f"  median children/parent  : {pc['children'].median()}")

    section("TEXT LENGTH (bytes)")
    df = df.with_columns(pl.col("text").str.len_bytes().alias("text_len"))
    print(df.group_by("kind").agg([
        pl.col("text_len").min().alias("min"),
        pl.col("text_len").quantile(0.25).alias("p25"),
        pl.col("text_len").median().alias("median"),
        pl.col("text_len").mean().round(1).alias("mean"),
        pl.col("text_len").quantile(0.9).alias("p90"),
        pl.col("text_len").quantile(0.99).alias("p99"),
        pl.col("text_len").max().alias("max"),
        pl.len().alias("n"),
    ]).sort("n", descending=True))

    buckets = df.with_columns(
        pl.when(pl.col("text_len") < 100).then(pl.lit("<100"))
        .when(pl.col("text_len") < 500).then(pl.lit("100-499"))
        .when(pl.col("text_len") < 1000).then(pl.lit("500-999"))
        .when(pl.col("text_len") < 5000).then(pl.lit("1k-5k"))
        .otherwise(pl.lit("5k+")).alias("bucket")
    ).group_by("bucket").agg(pl.len().alias("n")).sort("n", descending=True)
    print("\n  length buckets:")
    for row in buckets.iter_rows(named=True):
        print(f"    {row['bucket']:8s} {row['n']:7,}")

    section("TAGS")
    n_tagged = int((df["tags"] != "").sum())
    print(f"  tagged rows: {n_tagged:,} ({n_tagged / df.height:.3%})")
    if n_tagged:
        tag_rows = df.filter(pl.col("tags") != "")
        print("  distinct tag strings:", tag_rows["tags"].n_unique())
        # top-level tag components
        comp = collections.Counter()
        for t in tag_rows["tags"].to_list():
            for part in t.split(";"):
                comp[part.strip()] += 1
        for k, v in comp.most_common(15):
            print(f"    {v:5,}  {k}")

    section("REDACTION / PLACEHOLDER TAXONOMY")
    text_blob = " ".join(df["text"].to_list())
    toks = collections.Counter(re.findall(r"\[[^\]]+\]", text_blob))
    norm = collections.Counter()
    for t, c in toks.items():
        norm[re.sub(r"\d+", "N", t)] += c
    print(f"  placeholder occurrences: {sum(toks.values()):,}")
    print(f"  distinct placeholders  : {len(toks):,}")
    print("  top normalized placeholders:")
    for k, v in norm.most_common(20):
        print(f"    {v:7,}  {k}")

    section("EXTREME RECORDS")
    for kind in ("payload", "recovered_text", "response"):
        sub = df.filter(pl.col("kind") == kind)
        top = sub.sort("text_len", descending=True).head(1)[["id", "text_len"]].to_dicts()[0]
        print(f"  longest {kind:14s}: {top['id']}  ({top['text_len']:,} bytes)")

    section("COMPANION FILE")
    if GZ.exists():
        with open(DATA, "rb") as f:
            h_data = hashlib.sha256(f.read()).hexdigest()
        # compare decompressed gz to data
        import gzip
        with gzip.open(GZ, "rb") as f:
            gz_bytes = f.read()
        with open(DATA, "rb") as f:
            data_bytes = f.read()
        print(f"  gz rows == data rows : decompressed size {len(gz_bytes):,} vs data {len(data_bytes):,}")
        print(f"  gz is byte-identical to jsonl: {gz_bytes == data_bytes}")
        print(f"  sha256(jsonl) = {h_data}")

    # Return the augmented frame for callers / notebooks.
    return None


if __name__ == "__main__":
    main()
