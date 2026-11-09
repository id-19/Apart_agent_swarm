#include <algorithm>
#include <cctype>
#include <array>
#include <cstdio>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_set>
#include <vector>

namespace {

constexpr int K = 3;
constexpr int MAXD = 3;
constexpr int MAX_REPS = 1000000;
constexpr int PER_SOURCE_CAP = 1000000;

struct Record {
    std::string id;
    std::string kind;
    std::string text;
    int len = 0;
};

static constexpr int WIDTH = 2 * MAXD + 3;

int levenshteinThreshold(const std::string& a, const std::string& b, int maxd) {
    int m = static_cast<int>(a.size());
    int n = static_cast<int>(b.size());
    int dd = m - n;
    if (dd < 0) dd = -dd;
    if (dd > maxd) return maxd + 1;
    if (m == 0) return (n <= maxd) ? n : maxd + 1;
    if (n == 0) return (m <= maxd) ? m : maxd + 1;

    static thread_local std::array<int, WIDTH> bandA{};
    static thread_local std::array<int, WIDTH> bandB{};
    int* prev = bandA.data();
    int* cur = bandB.data();

    int prevLo = 0;
    int prevHi = std::min(n, maxd);
    for (int j = prevLo; j <= prevHi; ++j) prev[j - prevLo] = j;

    for (int i = 1; i <= m; ++i) {
        int curLo = std::max(0, i - maxd);
        int curHi = std::min(n, i + maxd);
        int width = curHi - curLo + 1;
        for (int t = 0; t < width; ++t) cur[t] = maxd + 1;

        int best = maxd + 1;
        if (curLo == 0) {
            cur[0] = i;
            if (i < best) best = i;
        }

        char ca = a[i - 1];
        for (int j = std::max(1, curLo); j <= curHi; ++j) {
            int cost = (ca == b[j - 1]) ? 0 : 1;

            int pv_j = (prevLo <= j && j <= prevHi) ? prev[j - prevLo] : maxd + 1;
            int pv_jm1 = (prevLo <= j - 1 && j - 1 <= prevHi) ? prev[(j - 1) - prevLo] : maxd + 1;
            int cur_jm1 = (curLo <= j - 1 && j - 1 <= curHi) ? cur[(j - 1) - curLo] : maxd + 1;

            int val = pv_j + 1;
            int s = pv_jm1 + cost;
            int ins = cur_jm1 + 1;
            if (s < val) val = s;
            if (ins < val) val = ins;

            if (val > maxd + 1) val = maxd + 1;
            cur[j - curLo] = val;
            if (val < best) best = val;
        }

        if (best > maxd) return maxd + 1;

        std::swap(prev, cur);
        prevLo = curLo;
        prevHi = curHi;
    }

    if (prevLo <= n && n <= prevHi) {
        int v = prev[n - prevLo];
        if (v > maxd) v = maxd + 1;
        return v;
    }
    return maxd + 1;
}

static unsigned char h2v(char c) {
    if (c >= '0' && c <= '9') return static_cast<unsigned char>(c - '0');
    if (c >= 'a' && c <= 'f') return static_cast<unsigned char>(c - 'a' + 10);
    if (c >= 'A' && c <= 'F') return static_cast<unsigned char>(c - 'A' + 10);
    return 0;
}

std::string parseJsonString(const std::string& s, size_t& i) {
    std::string out;
    if (i >= s.size() || s[i] != '"') return out;
    ++i;
    while (i < s.size()) {
        char c = s[i++];
        if (c == '"') return out;
        if (c == '\\') {
            if (i >= s.size()) break;
            char e = s[i++];
            switch (e) {
                case '"': out.push_back('"'); break;
                case '\\': out.push_back('\\'); break;
                case '/': out.push_back('/'); break;
                case 'b': out.push_back('\b'); break;
                case 'f': out.push_back('\f'); break;
                case 'n': out.push_back('\n'); break;
                case 'r': out.push_back('\r'); break;
                case 't': out.push_back('\t'); break;
                case 'u': {
                    if (i + 4 > s.size()) break;
                    uint32_t cp = (h2v(s[i]) << 12) | (h2v(s[i + 1]) << 8) |
                                  (h2v(s[i + 2]) << 4) | h2v(s[i + 3]);
                    i += 4;
                    if (cp >= 0xD800 && cp <= 0xDBFF) {
                        if (i + 6 <= s.size() && s[i] == '\\' && s[i + 1] == 'u') {
                            uint32_t cp2 = (h2v(s[i + 2]) << 12) | (h2v(s[i + 3]) << 8) |
                                           (h2v(s[i + 4]) << 4) | h2v(s[i + 5]);
                            if (cp2 >= 0xDC00 && cp2 <= 0xDFFF) {
                                cp = 0x10000 + ((cp - 0xD800) << 10) + (cp2 - 0xDC00);
                                i += 6;
                            }
                        }
                    }
                    if (cp < 0x80) {
                        out.push_back(static_cast<char>(cp));
                    } else if (cp < 0x800) {
                        out.push_back(static_cast<char>(0xC0 | (cp >> 6)));
                        out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
                    } else if (cp < 0x10000) {
                        out.push_back(static_cast<char>(0xE0 | (cp >> 12)));
                        out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
                        out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
                    } else {
                        out.push_back(static_cast<char>(0xF0 | (cp >> 18)));
                        out.push_back(static_cast<char>(0x80 | ((cp >> 12) & 0x3F)));
                        out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
                        out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
                    }
                    break;
                }
                default:
                    out.push_back('\\');
                    out.push_back(e);
                    break;
            }
        } else {
            out.push_back(c);
        }
    }
    return out;
}

void skipWhitespace(const std::string& s, size_t& i) {
    while (i < s.size() && (s[i] == ' ' || s[i] == '\t' || s[i] == '\n' || s[i] == '\r')) ++i;
}

void skipJsonValue(const std::string& s, size_t& i) {
    skipWhitespace(s, i);
    if (i >= s.size()) return;
    if (s[i] == '"') {
        parseJsonString(s, i);
        return;
    }
    if (s[i] == '{') {
        int depth = 0;
        bool inStr = false;
        for (; i < s.size(); ++i) {
            if (inStr) {
                if (s[i] == '\\') { ++i; continue; }
                if (s[i] == '"') inStr = false;
                continue;
            }
            if (s[i] == '"') { inStr = true; continue; }
            if (s[i] == '{') ++depth;
            else if (s[i] == '}') { --depth; if (depth == 0) { ++i; return; } }
        }
        return;
    }
    if (s[i] == '[') {
        int depth = 0;
        bool inStr = false;
        for (; i < s.size(); ++i) {
            if (inStr) {
                if (s[i] == '\\') { ++i; continue; }
                if (s[i] == '"') inStr = false;
                continue;
            }
            if (s[i] == '"') { inStr = true; continue; }
            if (s[i] == '[') ++depth;
            else if (s[i] == ']') { --depth; if (depth == 0) { ++i; return; } }
        }
        return;
    }
    while (i < s.size() && s[i] != ',' && s[i] != '}' && s[i] != ']' &&
           s[i] != ' ' && s[i] != '\t' && s[i] != '\n' && s[i] != '\r') {
        ++i;
    }
}

std::string replaceToken(const std::string& src, const std::string& from, const std::string& to) {
    std::string out;
    out.reserve(src.size());
    size_t i = 0;
    while (true) {
        auto pos = src.find(from, i);
        if (pos == std::string::npos) { out += src.substr(i); break; }
        bool leftBoundary = (pos == 0) || !(std::isalnum(static_cast<unsigned char>(src[pos - 1])) || src[pos - 1] == '_' || src[pos - 1] == '-');
        bool rightBoundary = (pos + from.size() >= src.size()) || !(std::isalnum(static_cast<unsigned char>(src[pos + from.size()])) || src[pos + from.size()] == '_' || src[pos + from.size()] == '-');
        out += src.substr(i, pos - i);
        out += (leftBoundary && rightBoundary) ? to : from;
        i = pos + from.size();
    }
    return out;
}

std::string normalizeSemantics(std::string s) {
    std::string collapsed;
    collapsed.reserve(s.size());
    bool lastSpace = true;
    for (unsigned char c : s) {
        if (std::isspace(c)) {
            if (!lastSpace && !collapsed.empty()) collapsed.push_back(' ');
            lastSpace = true;
        } else {
            collapsed.push_back(static_cast<char>(std::tolower(c)));
            lastSpace = false;
        }
    }
    while (!collapsed.empty() && collapsed.back() == ' ') collapsed.pop_back();

    std::string s2 = replaceToken(collapsed, "hugging face", "huggingface");
    s2 = replaceToken(s2, "hf", "huggingface");

    std::string out;
    out.reserve(s2.size());
    lastSpace = true;
    for (char c : s2) {
        if (c == ' ') {
            if (!out.empty() && out.back() != ' ') out.push_back(' ');
        } else {
            out.push_back(c);
        }
        lastSpace = (c == ' ');
    }
    while (!out.empty() && out.back() == ' ') out.pop_back();
    return out;
}


bool parseRow(const std::string& line, Record& out) {
    size_t i = 0;
    skipWhitespace(line, i);
    if (i >= line.size() || line[i] != '{') return false;
    ++i;
    for (;;) {
        skipWhitespace(line, i);
        if (i >= line.size()) return false;
        if (line[i] == '}') { ++i; return true; }
        if (line[i] != '"') return false;
        std::string key = parseJsonString(line, i);
        skipWhitespace(line, i);
        if (i >= line.size() || line[i] != ':') return false;
        ++i;
        skipWhitespace(line, i);
        if (key == "id" || key == "kind" || key == "text") {
            std::string val = parseJsonString(line, i);
            if (key == "id") out.id = val;
            else if (key == "kind") out.kind = val;
            else out.text = normalizeSemantics(val);
        } else {
            skipJsonValue(line, i);
        }
        skipWhitespace(line, i);
        if (i < line.size() && line[i] == ',') { ++i; continue; }
        if (i < line.size() && line[i] == '}') { ++i; return true; }
        return false;
    }
}

std::string esc(const std::string& s) {
    std::string r;
    r.reserve(s.size() + 8);
    for (unsigned char c : s) {
        switch (c) {
            case '"': r += "\\\""; break;
            case '\\': r += "\\\\"; break;
            case '\b': r += "\\b"; break;
            case '\f': r += "\\f"; break;
            case '\n': r += "\\n"; break;
            case '\r': r += "\\r"; break;
            case '\t': r += "\\t"; break;
            default:
                if (c < 0x20) {
                    char buf[8];
                    std::snprintf(buf, sizeof(buf), "\\u%04x", c);
                    r += buf;
                } else {
                    r.push_back(static_cast<char>(c));
                }
                break;
        }
    }
    return r;
}


} // namespace

int main(int argc, char** argv) {
    std::string inputPath = "/Users/id19/Programming/AI_research/Apart_agent_swarm/Data/redacted_filtered.jsonl";
    std::string outDir = "/Users/id19/scratchpad/binned_levenshtein";
    if (argc > 1 && argv[1] && argv[1][0] != '\0') inputPath = argv[1];
    if (argc > 2 && argv[2] && argv[2][0] != '\0') outDir = argv[2];

    std::vector<Record> rows;
    rows.reserve(200000);

    std::ifstream in(inputPath);
    if (!in) {
        std::cerr << "cannot open input: " << inputPath << "\n";
        return 1;
    }
    std::string line;
    long long linesRead = 0;
    long long parsed = 0;
    while (std::getline(in, line)) {
        ++linesRead;
        if (line.empty()) continue;
        Record r;
        if (parseRow(line, r)) {
            r.len = static_cast<int>(r.text.size());
            rows.push_back(std::move(r));
            ++parsed;
        }
    }
    in.close();

    std::sort(rows.begin(), rows.end(), [](const Record& a, const Record& b) {
        if (a.len != b.len) return a.len < b.len;
        if (a.text != b.text) return a.text < b.text;
        return a.id < b.id;
    });

    std::vector<size_t> active;
    active.reserve(rows.size());
    long long hugeGroups = 0;
    size_t i = 0;
    const size_t nRows = rows.size();
    while (i < nRows) {
        size_t j = i;
        while (j < nRows && rows[j].len == rows[i].len) ++j;
        size_t groupSize = j - i;
        if (groupSize <= MAX_REPS) {
            for (size_t k = i; k < j; ++k) active.push_back(k);
        } else {
            ++hugeGroups;
            std::unordered_set<std::string> seen;
            seen.reserve(groupSize * 2);
            int reps = 0;
            for (size_t k = i; k < j && reps < MAX_REPS; ++k) {
                if (seen.insert(rows[k].text).second) {
                    active.push_back(k);
                    ++reps;
                }
            }
        }
        i = j;
    }

    std::ofstream cand(outDir + "/candidates.ndjson", std::ios::trunc);
    if (!cand) {
        std::cerr << "cannot open output candidates\n";
        return 1;
    }

    long long candidates = 0;
    long long pairsConsidered = 0;
    for (size_t a = 0; a < active.size(); ++a) {
        const Record& ra = rows[active[a]];
        int emittedThisSource = 0;
        for (size_t b = a + 1; b < active.size(); ++b) {
            const Record& rb = rows[active[b]];
            int diff = rb.len - ra.len;
            if (diff > K) break;
            if (emittedThisSource >= PER_SOURCE_CAP) break;

            ++pairsConsidered;

            bool exact = (ra.len == rb.len && ra.text == rb.text);
            int d = exact ? 0 : levenshteinThreshold(ra.text, rb.text, MAXD);
            bool ok = exact || (d <= MAXD);
            if (ok) {
                if (d > MAXD) d = 0;
                cand << "{\"source_id\":\"" << esc(ra.id) << "\",\"target_id\":\"" << esc(rb.id)
                     << "\",\"source_kind\":\"" << esc(ra.kind) << "\",\"target_kind\":\"" << esc(rb.kind)
                     << "\",\"levenshtein_distance\":" << d
                     << ",\"source_length\":" << ra.len
                     << ",\"target_length\":" << rb.len << "}\n";
                ++candidates;
                ++emittedThisSource;
            }
        }
    }
    cand.close();

    std::ofstream rep(outDir + "/report.md", std::ios::trunc);
    rep << "# Binned Levenshtein candidate report\n\n";
    rep << "- Input: `" << inputPath << "`\n";
    rep << "- Candidates: `" << outDir << "/candidates.ndjson`\n";
    rep << "- K (length window): " << K << "\n";
    rep << "- Candidate threshold: distance <= " << MAXD << " or exact text equal\n";
    rep << "- Per-source pair cap: " << PER_SOURCE_CAP << "\n";
    rep << "- Huge length groups (> " << MAX_REPS << " members, representatives only): " << hugeGroups << "\n";
    rep << "- Compile command: `g++ -O2 -std=c++17 -Wall -Wextra -o binned_levenshtein main.cpp` (or `make`)\n";
    rep << "- Rows read (non-empty lines): " << linesRead << "\n";
    rep << "- Rows parsed: " << parsed << "\n";
    rep << "- Rows in active representative set: " << active.size() << "\n";
    rep << "- Pairs considered: " << pairsConsidered << "\n";
    rep << "- Candidate pairs emitted: " << candidates << "\n";
    rep << "\n## Notes\n\n";
    rep << "- No external dependencies; C++17.\n";
    rep << "- Input was treated read-only.\n";
    rep << "- Output is candidate generation only; no deduplication/clustering or semantic judgment.\n";
    rep.close();

    std::cout << "input=" << inputPath << "\n";
    std::cout << "rows_read=" << linesRead << " parsed=" << parsed << "\n";
    std::cout << "active_rows=" << active.size() << " huge_groups=" << hugeGroups << "\n";
    std::cout << "pairs_considered=" << pairsConsidered << " candidates=" << candidates << "\n";
    std::cout << "wrote " << outDir << "/candidates.ndjson and report.md\n";
    return 0;
}
