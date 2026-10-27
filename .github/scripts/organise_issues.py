"""Keep the requirements tidy.

- Every open requirement that isn't inside another one gets a folder, e.g. requirements/R012-contract-version-history/
  with an images/ folder inside. Sub-requirements use their parent's folder.
- Requirements inside another requirement get the "sub-requirement" label; the label is removed if they're taken out.
"""
import os

from issues import REQUIREMENTS, all_issues, folder_name, folder_of, gh

DRY = os.environ.get("DRY_RUN") == "1"  # only show what would change

issues = all_issues()
for i in sorted(issues.values(), key=lambda x: x["n"]):
    if "requirement" not in i["labels"]:
        continue
    is_sub = i["parent"] in issues
    if is_sub != ("sub-requirement" in i["labels"]):
        if not DRY:
            gh("issue", "edit", str(i["n"]), "--add-label" if is_sub else "--remove-label", "sub-requirement")
        print(f"#{i['n']}: {'added' if is_sub else 'removed'} the sub-requirement label")
    if is_sub or not i["open"] or folder_of(i["n"]):
        continue
    folder = REQUIREMENTS / folder_name(i)
    if not DRY:
        (folder / "images").mkdir(parents=True, exist_ok=True)
        (folder / "images" / ".gitkeep").write_text("", encoding="utf-8")
    print(f"made folder requirements/{folder.name}/")
