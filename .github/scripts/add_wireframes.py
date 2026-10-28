"""Give every wireframe picture its own page, in its requirement's wireframes folder.

A picture in requirements/R012-.../wireframes/images/ named like R012-W02-version-compare.excalidraw.svg gets
the page requirements/R012-.../wireframes/R012-W02-version-compare.md: its name, which requirement it is for,
the picture, then Description and Open questions. Versions of a screen (R012-W02a-..., R012-W02b-...) get their
pages inside a folder named after the screen, wireframes/R012-W02/. Sub-requirements work the same way in their
own folder (inside their requirement's folder).

Pages that already exist keep everything written in them; only the line saying which requirement they are
for is kept up to date. If a picture is renamed (e.g. ...-final), its page is renamed with it. Pictures whose
names don't fit are listed in PICTURES-NOT-ADDED.md in that folder, which disappears once they are fixed.

Every wireframe page and every flowchart page (flowcharts/R012-C01-....md) gets a line under its title,
"💬 Comment on this wireframe on the website ↗", that opens it on the handbook website, where people comment.
"""
import json
import os
import re

from issues import REQUIREMENTS, WIREFRAME, all_issues, by_code, gh, requirement_folders, trail

LINK = re.compile(r"!\[[^\]]*\]\((?:\.\./)?images/([^)]+)\)")
FLOWCHART = re.compile(r"^(R\d{3,}(?:-S\d{2,})*)-C(\d{2,})(?:-.*)?$")
COMMENT_LINE = "💬 [Comment on this"


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


def website():
    """The handbook website's address, e.g. https://saanchi365.github.io/ux-process-requirements/"""
    repo = os.environ.get("GITHUB_REPOSITORY") or json.loads(gh("repo", "view", "--json", "nameWithOwner"))["nameWithOwner"]
    owner, name = repo.split("/")
    return f"https://{owner.lower()}.github.io/{name}/"


def comment_line(page, owner, kind, key):
    """A line under a file's title that opens this wireframe or flowchart on the website, where people comment on it."""
    old = page.read_text(encoding="utf-8")
    lines = old.split("\n")
    had = [i for i, l in enumerate(lines) if l.startswith(COMMENT_LINE)]
    for i in reversed(had):  # take out the old line (and the empty line after it) before adding it fresh
        del lines[i:i + 2 if i + 1 < len(lines) and not lines[i + 1].strip() else i + 1]
    # it goes after the title, and after the line naming the requirement when there is one
    at = 2 if len(lines) > 1 and lines[1].strip() else 1
    while at < len(lines) and not lines[at].strip():
        del lines[at]
    letter = "w" if kind == "wireframe" else "c"
    lines[at:at] = ["", f"{COMMENT_LINE} {kind} on the website ↗]({SITE}r/{owner}/#{letter}={key})", ""]
    text = "\n".join(lines)
    if text != old:
        page.write_text(text, encoding="utf-8", newline="\n")
        print(f"comment line in {page.name}")


issues = all_issues() if REQUIREMENTS.is_dir() else {}
SITE = website()
codes = by_code(issues)
for owner, requirement in requirement_folders().items():
    folder = requirement / "wireframes"
    pics = folder / "images"
    if not pics.is_dir():
        continue
    have = {p.name for p in pics.glob("*.svg")}
    pages = {p.stem: p for p in folder.rglob("*.md")
             if WIREFRAME.match(p.stem) and not p.stem.endswith("-compare") and pics not in p.parents}
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

    # the comment line on every wireframe page
    for stem, page in pages.items():
        if page.exists():
            comment_line(page, owner, "wireframe", screen(stem))

    # a compare page in every versions folder: all versions of the screen side by side
    for sub in [d for d in folder.iterdir() if d.is_dir() and d != pics]:
        compare = sub / f"{sub.name}-compare.md"
        versions = sorted((p for p in sub.glob("*.md") if p != compare and WIREFRAME.match(p.stem)),
                          key=lambda p: WIREFRAME.match(p.stem).group(3))
        if not versions:
            if compare.exists():
                compare.unlink()
            continue
        cells = []
        for p in versions:
            letter = WIREFRAME.match(p.stem).group(3)
            status = ("✅ <b>Chosen</b>" if p.stem.endswith("-final") else
                      "Not chosen" if p.stem.endswith("-cancel") else "Not decided yet")
            cells.append((f"Version {letter}", status, picture_of(p), p.name))
        text = (f"# {sub.name} · compare versions\n{trail(issues, owner) if owner in codes else owner}\n\n"
                "Made automatically: every version of this screen side by side. Open a version for its notes.\n\n"
                "<table>\n<tr>" + "".join(f"<th>{v}<br>{s}</th>" for v, s, _, _ in cells) + "</tr>\n<tr>"
                + "".join(f'<td valign="top"><a href="{page}"><img src="../images/{pic}" width="360"></a></td>'
                          for _, _, pic, page in cells) + "</tr>\n<tr>"
                + "".join(f'<td><a href="{page}">{page.removesuffix(".md")}</a></td>' for _, _, _, page in cells)
                + "</tr>\n</table>\n")
        if not compare.exists() or compare.read_text(encoding="utf-8") != text:
            compare.write_text(text, encoding="utf-8", newline="\n")
            print(f"compare page {compare.name}")

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

# the comment line on every flowchart page
for owner, requirement in requirement_folders().items():
    for page in sorted((requirement / "flowcharts").glob("*.md")):
        m = FLOWCHART.match(page.stem)
        if m and m.group(1) == owner:
            comment_line(page, owner, "flowchart", f"{owner}-C{m.group(2)}")
