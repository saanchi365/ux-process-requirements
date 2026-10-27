"""Keep the requirements tidy.

- Every open requirement gets a folder with wireframes/ and flowcharts/ inside, e.g.
  requirements/R001-contract-list-page/. A sub-requirement's folder sits inside its requirement's folder,
  e.g. requirements/R001-contract-list-page/R021-filters-on-the-contract-list/.
- If a requirement is moved inside another one later, its folder moves with it.
- Requirements inside another requirement get the "sub-requirement" label; the label is removed if they're taken out.
"""
import os
import shutil

from issues import REQUIREMENTS, all_issues, folder_name, gh, requirement_folders

DRY = os.environ.get("DRY_RUN") == "1"  # only show what would change


def depth(n):
    d = 0
    while issues.get(n, {}).get("parent") in issues and d < 20:
        n, d = issues[n]["parent"], d + 1
    return d


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
    is_sub = i["parent"] in issues
    if is_sub != ("sub-requirement" in i["labels"]):
        if not DRY:
            gh("issue", "edit", str(i["n"]), "--add-label" if is_sub else "--remove-label", "sub-requirement")
        print(f"#{i['n']}: {'added' if is_sub else 'removed'} the sub-requirement label")

    home = folders.get(i["parent"]) if is_sub else REQUIREMENTS
    if home is None:
        continue  # its requirement has no folder yet (e.g. it's closed)
    current = folders.get(i["n"])
    if current and current.parent != home:  # moved inside another requirement (or taken out): move its folder
        target = home / current.name
        if not DRY:
            shutil.move(str(current), str(target))
        print(f"moved {current.relative_to(REQUIREMENTS)} -> {target.relative_to(REQUIREMENTS)}")
        folders = requirement_folders() if not DRY else {**folders, i["n"]: target}
        current = target
    if not current:
        if not i["open"]:
            continue
        current = home / folder_name(i)
        print(f"made folder {current.relative_to(REQUIREMENTS.parent)}/")
        folders[i["n"]] = current
    if not DRY:
        keep(current)
