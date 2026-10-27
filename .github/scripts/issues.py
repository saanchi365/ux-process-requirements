"""Read the requirements (issues) and how they sit inside each other, and the naming rules shared by the helpers.

Codes are our own, not GitHub's issue numbers: requirements are R001, R002 ... (counting only requirements),
sub-requirements are counted inside their requirement: R015-S01, R015-S02 ... The code is the start of the
issue's title, e.g. "R015-S01 · Reason is required".
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "requirements"
CODE = r"R\d{3,}(?:-S\d{2,})*"
# R015-S01-W02b-reason-box: sub-requirement R015-S01, wireframe 2, version b
WIREFRAME = re.compile(rf"^({CODE})-W(\d{{2,}})([a-z]?)(?:-.*)?$")
TITLE = re.compile(r"^\s*(R\d+(?:\s*-\s*S\d+)*)\b[\s·:.\-–—]*(.*)$", re.I)
FOLDER = re.compile(rf"^({CODE})(?:-(?!S\d)|$)")

QUERY = """query($owner:String!,$name:String!,$after:String){repository(owner:$owner,name:$name){
  issues(first:100,after:$after){pageInfo{hasNextPage endCursor}
    nodes{number title state labels(first:20){nodes{name}} parent{number}}}}}"""


def gh(*args):
    return subprocess.run(["gh", *args], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8").stdout


def tidy(code):
    """'r15-s1' -> 'R015-S01'"""
    parts = re.findall(r"\d+", code)
    return f"R{int(parts[0]):03d}" + "".join(f"-S{int(p):02d}" for p in parts[1:])


def split(title):
    """'R015-S01 · Reason is required' -> ('R015-S01', 'Reason is required'); no code -> (None, title)"""
    m = TITLE.match(title)
    return (tidy(m.group(1)), m.group(2).strip()) if m else (None, title.strip())


def all_issues():
    """{issue number: {n, title, code, name, open, labels, parent}} for every issue."""
    repo = json.loads(gh("repo", "view", "--json", "owner,name"))
    found, after = {}, None
    while True:
        args = ["api", "graphql", "-f", f"query={QUERY}", "-f", f"owner={repo['owner']['login']}", "-f", f"name={repo['name']}"]
        if after:
            args += ["-f", f"after={after}"]
        page = json.loads(gh(*args))["data"]["repository"]["issues"]
        for i in page["nodes"]:
            code, name = split(i["title"])
            found[i["number"]] = dict(n=i["number"], title=i["title"].strip(), code=code, name=name,
                                      open=i["state"] == "OPEN", labels={l["name"] for l in i["labels"]["nodes"]},
                                      parent=(i["parent"] or {}).get("number"))
        if not page["pageInfo"]["hasNextPage"]:
            return found
        after = page["pageInfo"]["endCursor"]


def by_code(issues):
    return {i["code"]: i for i in issues.values() if i["code"]}


def folder_name(issue):
    # kept short: Windows can't handle a file whose full location is longer than about 260 letters
    slug = re.sub(r"[^a-z0-9]+", "-", issue["name"].lower()).strip("-")
    if len(slug) > 30:
        slug = re.sub(r"(?<=-)(a|an|the)-", "", slug)  # drop small words first
    if len(slug) > 30:
        slug = slug[:31].rsplit("-", 1)[0]
        slug = re.sub(r"(-(a|an|the|of|for|with|to|and|by|on|in|from|through|each|both))+$", "", slug)
    return f"{issue['code']}-{slug}" if slug else issue["code"]


def requirement_folders():
    """Every requirement and sub-requirement folder, at any depth: {code: folder}."""
    found = {}
    if REQUIREMENTS.is_dir():
        for p in sorted(REQUIREMENTS.rglob("R*")):
            m = FOLDER.match(p.name)
            inside = p.relative_to(REQUIREMENTS).parts[:-1]
            if p.is_dir() and m and not WIREFRAME.match(p.name) and not {"wireframes", "flowcharts"} & set(inside):
                found.setdefault(m.group(1), p)
    return found


def trail(issues, code):
    """'R015 · Reject a contract version › R015-S01 · Reason is required' for a sub-requirement."""
    codes = by_code(issues)
    chain, i = [], codes.get(code)
    while i and i not in chain:
        chain.insert(0, i)
        i = issues.get(i["parent"])
    return " › ".join(f"{c['code']} · {c['name']}" for c in chain) if chain else code
