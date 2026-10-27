"""Give every wireframe picture its own page, in its requirement's wireframes folder.

A picture in requirements/R012-.../wireframes/images/ named like R012-W02-version-compare.excalidraw.svg gets
the page requirements/R012-.../wireframes/R012-W02-version-compare.md: its name, which requirement it is for,
the picture, then Description and Open questions. Versions of a screen (R012-W02a-..., R012-W02b-...) get their
pages inside a folder named after the screen, wireframes/R012-W02/. Sub-requirements work the same way in their
own folder (inside their requirement's folder).

Pages that already exist keep everything written in them; only the line saying which requirement they are
for is kept up to date. If a picture is renamed (e.g. ...-final), its page is renamed with it. Pictures whose
names don't fit are listed in PICTURES-NOT-ADDED.md in that folder, which disappears once they are fixed.
"""
import re

from issues import REQUIREMENTS, WIREFRAME, all_issues, by_code, requirement_folders, trail

LINK = re.compile(r"!\[[^\]]*\]\((?:\.\./)?images/([^)]+)\)")


def screen(name, version=True):
    """R015-S01-W02b-reason-box-final -> R015-S01-W02b (or R015-S01-W02 without the version letter)."""
    m = WIREFRAME.match(name)
    return f"{m.group(1)}-W{m.group(2)}" + (m.group(3) if version else "")


def place(folder, name):
    """Where a picture's page goes, and how that page points to the images folder."""
    if WIREFRAME.match(name).group(3):  # a version: inside the screen's own folder
        return folder / screen(name, version=False), "../images/"
    return folder, "images/"


def picture_of(page):
    m = LINK.search(page.read_text(encoding="utf-8"))
    return m.group(1) if m else None


issues = all_issues() if REQUIREMENTS.is_dir() else {}
codes = by_code(issues)
for owner, requirement in requirement_folders().items():
    folder = requirement / "wireframes"
    pics = folder / "images"
    if not pics.is_dir():
        continue
    have = {p.name for p in pics.glob("*.svg")}
    pages = {p.stem: p for p in folder.rglob("*.md") if WIREFRAME.match(p.stem) and pics not in p.parents}
    lost = {screen(c): p for c, p in pages.items() if picture_of(p) not in have}

    wrong = []
    for name in sorted(have):
        stem = name.removesuffix(".svg").removesuffix(".excalidraw")
        m = WIREFRAME.match(stem)
        if not m or m.group(1) != owner:
            wrong.append(name)
            continue
        if stem in pages:
            continue
        where, prefix = place(folder, stem)
        where.mkdir(exist_ok=True)
        old = lost.pop(screen(stem), None) or lost.pop(screen(stem, version=False), None)
        if old:  # the picture was renamed: rename its page and point it at the new name
            text = old.read_text(encoding="utf-8")
            text = re.sub(r"^# .*$", f"# {stem}", text, count=1, flags=re.M)
            text = LINK.sub(f"![{stem}]({prefix}{name})", text, count=1)
            old.unlink()
            pages[stem] = where / f"{stem}.md"
            pages[stem].write_text(text, encoding="utf-8", newline="\n")
            print(f"renamed {old.name} -> {stem}.md")
        else:
            pages[stem] = where / f"{stem}.md"
            pages[stem].write_text(f"# {stem}\n{owner}\n\n![{stem}]({prefix}{name})\n\n"
                                   "## Description\n\n\n## Open questions\n- \n", encoding="utf-8", newline="\n")
            print(f"added {pages[stem].relative_to(REQUIREMENTS.parent)}")

    # keep the line saying which requirement a page is for up to date (it starts as just the code, e.g. R015-S01)
    for stem, page in pages.items():
        if not page.exists():
            continue
        lines = page.read_text(encoding="utf-8").split("\n")
        if owner in codes and len(lines) > 1 and re.fullmatch(r"R\d{3,}(-S\d{2,})*( · .*)?", lines[1].strip()):
            named = trail(issues, owner)
            if lines[1] != named:
                lines[1] = named
                page.write_text("\n".join(lines), encoding="utf-8", newline="\n")
                print(f"named {page.name}")

    for sub in [d for d in folder.iterdir() if d.is_dir() and d != pics]:
        if not any(sub.iterdir()):
            sub.rmdir()

    note = folder / "PICTURES-NOT-ADDED.md"
    if wrong:
        note.write_text("# Pictures not added\n\nTheir names don't fit this folder. Name them like "
                        f"`{owner}-W01-screen-name.excalidraw.svg` (a sub-requirement's pictures go in its own "
                        "folder) and their pages will be made.\n\n"
                        + "".join(f"- `images/{w}`\n" for w in wrong), encoding="utf-8", newline="\n")
    elif note.exists():
        note.unlink()
