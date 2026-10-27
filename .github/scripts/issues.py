"""Read the requirements (issues) and how they sit inside each other, and the naming rules shared by the helpers."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "requirements"
# R012-W02b-version-compare: requirement 12, wireframe 2, version b
WIREFRAME = re.compile(r"^R(\d{3,})-W(\d{2,})([a-z]?)(?:-.*)?$")

QUERY = """query($owner:String!,$name:String!,$after:String){repository(owner:$owner,name:$name){
  issues(first:100,after:$after){pageInfo{hasNextPage endCursor}
    nodes{number title state labels(first:20){nodes{name}} parent{number}}}}}"""


def gh(*args):
    return subprocess.run(["gh", *args], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8").stdout


def all_issues():
    """{number: {n, title, open, labels, parent}} for every issue."""
    repo = json.loads(gh("repo", "view", "--json", "owner,name"))
    found, after = {}, None
    while True:
        args = ["api", "graphql", "-f", f"query={QUERY}", "-f", f"owner={repo['owner']['login']}", "-f", f"name={repo['name']}"]
        if after:
            args += ["-f", f"after={after}"]
        page = json.loads(gh(*args))["data"]["repository"]["issues"]
        for i in page["nodes"]:
            found[i["number"]] = dict(n=i["number"], title=i["title"].strip(), open=i["state"] == "OPEN",
                                      labels={l["name"] for l in i["labels"]["nodes"]},
                                      parent=(i["parent"] or {}).get("number"))
        if not page["pageInfo"]["hasNextPage"]:
            return found
        after = page["pageInfo"]["endCursor"]


def code(n):
    """12 -> 'R012'"""
    return f"R{n:03d}"


def top(issues, n):
    """The top requirement a requirement or sub-requirement belongs to."""
    seen = set()
    while n in issues and issues[n]["parent"] in issues and n not in seen:
        seen.add(n)
        n = issues[n]["parent"]
    return n


def folder_name(issue):
    slug = re.sub(r"[^a-z0-9]+", "-", issue["title"].lower()).strip("-")[:50].strip("-")
    return f"{code(issue['n'])}-{slug}" if slug else code(issue["n"])


def folder_of(n):
    """The requirement's folder, whatever words follow its code."""
    if not REQUIREMENTS.is_dir():
        return None
    return next((p for p in sorted(REQUIREMENTS.iterdir()) if p.is_dir() and re.match(code(n) + r"(-|$)", p.name)), None)


def trail(issues, n):
    """'#12 · Contract version history › #16 · Filters' for a sub-requirement."""
    chain = []
    while n in issues and n not in [c["n"] for c in chain]:
        chain.insert(0, issues[n])
        n = issues[n]["parent"]
    return " › ".join(f"#{c['n']} · {c['title']}" for c in chain)
