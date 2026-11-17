import pathlib, re, sys
R = pathlib.Path(sys.argv[1])

def section(path, heading):
    text = (R / path).read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip().lstrip("#").strip() == heading)
    out = []
    for l in lines[start + 1:]:
        if l.startswith("#"):
            break
        out.append(l)
    return "\n".join(out).strip("\n")

def paras(block):
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", block) if p.strip()]

def sents(block):
    flat = re.sub(r"\s+", " ", block).strip()
    return re.split(r"(?<=\.) +(?=[A-Z`])", flat)

print("### README System requirements sentences")
blk = section("repo_README.md", "System requirements")
for i, s in enumerate(sents(blk), 1):
    print(f"  s{i}: {s[:100]}")
print("### propagation.md opening paragraphs")
text = (R / "repo_docs_propagation.md").read_text(encoding="utf-8")
opening = text.split("<!-- END GENERATED TOC -->")[1].split("## Use the CLI")[0]
for i, p in enumerate(paras(opening), 1):
    print(f"  p{i}: {p[:120]}")
print("### MODEL_CARD Technical requirements sentences")
blk = section("repo_MODEL_CARD.md", "Technical requirements and integration guidance")
for i, p in enumerate(paras(blk), 1):
    print(f"  p{i}: {p[:90]}")
for i, s in enumerate(sents(blk), 1):
    print(f"  s{i}: {s[:90]}")
print("### MODEL_CARD Out-of-scope closing paragraphs")
blk = section("repo_MODEL_CARD.md", "Out-of-scope use cases")
for i, p in enumerate(paras(blk), 1):
    print(f"  p{i}: {p[:90]}")
