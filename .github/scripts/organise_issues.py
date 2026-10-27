"""Keep the requirements tidy.

- Codes: a new requirement titled just "Contract renewal" becomes "R021 · Contract renewal" (the next requirement
  number, counting only requirements). A new sub-requirement inside R015 becomes "R015-S03 · ..." (counted inside
  its requirement). A code is never changed or given out twice, even if the item is closed or moved later.
- Folders: every open requirement gets a folder with wireframes/ and flowcharts/ inside, e.g.
  requirements/R001-contract-list-page/. A sub-requirement's folder sits inside its requirement's folder, e.g.
  requirements/R001-contract-list-page/R001-S01-filters-on-the-contract-list/. If a requirement is moved inside
  another one later, its folder moves with it.
- Labels: requirements inside another requirement get the "sub-requirement" label; it's removed if they're taken out.
"""
import os
import re
import shutil

from issues import REQUIREMENTS, all_issues, folder_name, gh, requirement_folders

DRY = os.environ.get("DRY_RUN") == "1"  # only show what would change


def depth(n):
    d = 0
    while issues.get(n, {}).get("parent") in issues and d < 20:
        n, d = issues[n]["parent"], d + 1
    return d


def next_code(prefix, pattern):
    """The next number after the highest ever used, e.g. prefix 'R015-S', pattern for two digits."""
    used = [int(m.group(1)) for c in (x["code"] for x in issues.values()) if c and (m := re.fullmatch(re.escape(prefix) + r"(\d+)", c))]
    return prefix + pattern.format(max(used, default=0) + 1)


def keep(folder):
    """GitHub doesn't keep empty folders: a placeholder file holds the place until something else is added."""
    for sub in ("wireframes", "flowcharts"):
        (folder / sub).mkdir(parents=True, exist_ok=True)
        placeholder = folder / sub / ".gitkeep"
        others = [p for p in (folder / sub).iterdir() if p.name != ".gitkeep"]
        if others and placeholder.exists():
            placeholder.unlink()
        elif not others and not placeholder.exists():
            placeholder.write_text("", encoding="utf-8")


issues = all_issues()
folders = requirement_folders()
for i in sorted((x for x in issues.values() if "requirement" in x["labels"]), key=lambda x: (depth(x["n"]), x["n"])):
    parent = issues.get(i["parent"])
    is_sub = parent is not None
    if is_sub != ("sub-requirement" in i["labels"]):
        if not DRY:
            gh("issue", "edit", str(i["n"]), "--add-label" if is_sub else "--remove-label", "sub-requirement")
        print(f"#{i['n']}: {'added' if is_sub else 'removed'} the sub-requirement label")

    # its code: kept if it has one, otherwise the next free one
    if is_sub and not parent["code"]:
        continue  # wait until its requirement has a code
    if not i["code"]:
        i["code"] = next_code(parent["code"] + "-S", "{:02d}") if is_sub else next_code("R", "{:03d}")
    title = f"{i['code']} · {i['name'][:1].upper()}{i['name'][1:]}"
    if title != i["title"]:
        if not DRY:
            gh("issue", "edit", str(i["n"]), "--title", title)
        print(f"#{i['n']}: {i['title']!r} -> {title!r}")
        i["title"] = title

    # its folder: inside its requirement's folder if it's a sub-requirement
    home = folders.get(parent["code"]) if is_sub else REQUIREMENTS
    if home is None:
        continue  # its requirement has no folder (e.g. it's closed)
    current = folders.get(i["code"])
    if current and current.parent != home:
        target = home / current.name
        if not DRY:
            shutil.move(str(current), str(target))
        print(f"moved {current.relative_to(REQUIREMENTS)} -> {target.relative_to(REQUIREMENTS)}")
        folders = requirement_folders() if not DRY else {**folders, i["code"]: target}
        current = target
    if not current:
        if not i["open"]:
            continue
        current = home / folder_name(i)
        print(f"made folder {current.relative_to(REQUIREMENTS.parent)}/")
        folders[i["code"]] = current
    if not DRY:
        keep(current)
