"""Make a new wireframe (or a new version of one) with its page, and open both in VS Code.

Run it from VS Code: Terminal > Run Task... > "New wireframe" or "New version of a screen".

  new_wireframe.py new 12 "version compare"   ->  R012-W<next number>-version-compare
  new_wireframe.py new 15-1 "reason box"      ->  R015-S01-W<next number>-reason-box (a sub-requirement)
  new_wireframe.py version R012-W02           ->  the next version (a, b, c ...) of that screen
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github" / "scripts"))
from issues import requirement_folders, tidy  # noqa: E402

LINK = re.compile(r"!\[[^\]]*\]\((?:\.\./)?images/[^)]+\)")
TYPED = re.compile(r"\s*R?0*\d+(?:\s*[-./ ]\s*S?0*\d+)*\s*", re.I)  # 15, R015, 15-1, R015-S01 ...


def stop(message):
    print(f"\n  {message}\n")
    sys.exit(1)


def folder_for(code):
    """The wireframes folder of a requirement or sub-requirement, e.g. R015-S01."""
    folder = requirement_folders().get(code)
    if not folder:
        stop(f"There is no folder for {code} yet. Check the code, or click Sync Changes and try again.")
    (folder / "wireframes" / "images").mkdir(parents=True, exist_ok=True)
    return folder / "wireframes"


def write_page(path, name, link):
    # the second line (the bare code) is replaced by the requirement's name on GitHub
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {name}\n{name[:name.index('-W')]}\n\n![{name}]({link})\n\n## Description\n\n\n## Open questions\n- \n",
                    encoding="utf-8", newline="\n")


def open_files(*files):
    if os.environ.get("NO_OPEN"):
        return
    try:
        subprocess.run(["code", "-r", *map(str, files)], shell=True, check=False)
    except OSError:
        print("  Open them from the file list on the left.")


def new_screen(typed, name):
    if not TYPED.fullmatch(typed):
        stop("Type the requirement, e.g. 12 for R012, or 15-1 for the sub-requirement R015-S01.")
    code = tidy(typed)
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    if len(slug) > 30:  # kept short: Windows can't handle very long file locations
        slug = re.sub(r"(?<=-)(a|an|the)-", "", slug)
    if len(slug) > 30:
        slug = slug[:31].rsplit("-", 1)[0]
        slug = re.sub(r"(-(a|an|the|of|for|with|to|and|by|on|in|from|through|each|both))+$", "", slug)
    if not slug:
        stop("Give the screen a short name, e.g. version compare.")
    folder = folder_for(code)
    images = folder / "images"
    numbers = [int(w.group(1)) for p in images.glob("*.svg") if (w := re.match(re.escape(code) + r"-W(\d+)", p.name))]
    stem = f"{code}-W{max(numbers, default=0) + 1:02d}-{slug}"
    pic = images / f"{stem}.excalidraw.svg"
    pic.write_text("", encoding="utf-8")
    page = folder / f"{stem}.md"
    write_page(page, stem, f"images/{pic.name}")
    print(f"\n  Made {stem} in {folder.parent.name}\n"
          "  Draw in the picture, write the description and open questions in its page, then Commit.\n")
    open_files(page, pic)


def new_version(screen):
    m = re.fullmatch(r"\s*(R?\d+(?:\s*-\s*S?\d+)*)\s*-\s*W0*(\d+)\s*", screen, re.I)
    if not m:
        stop("Type the screen like R012-W02 (or R015-S01-W02), without a version letter.")
    code = tidy(m.group(1))
    screen = f"{code}-W{int(m.group(2)):02d}"
    folder = folder_for(code)
    images = folder / "images"
    pattern = re.compile(re.escape(screen) + r"([a-z]?)(?=[-.])(.*?)(?:\.excalidraw)?\.svg$")

    def found():
        return sorted((p, v) for p in images.glob("*.svg") if (v := pattern.match(p.name)))

    if not found():
        stop(f"There is no screen {screen} yet. Use 'New wireframe' to make it first.")
    versions_folder = folder / screen

    # the first time: the existing screen becomes version a, and its page moves into the screen's folder
    plain = next(((p, v) for p, v in found() if not v.group(1)), None)
    if plain:
        pic, v = plain
        stem = f"{screen}a{v.group(2)}"
        new_pic = images / f"{stem}.excalidraw.svg"
        pic.rename(new_pic)
        old_page = folder / f"{screen}{v.group(2)}.md"
        versions_folder.mkdir(exist_ok=True)
        if old_page.exists():
            text = re.sub(r"^# .*$", f"# {stem}", old_page.read_text(encoding="utf-8"), count=1, flags=re.M)
            text = LINK.sub(f"![{stem}](../images/{new_pic.name})", text, count=1)
            (versions_folder / f"{stem}.md").write_text(text, encoding="utf-8", newline="\n")
            old_page.unlink()
        else:
            write_page(versions_folder / f"{stem}.md", stem, f"../images/{new_pic.name}")
        print(f"\n  {screen} is now version a: {stem}")

    versions = found()
    latest, v = versions[-1]
    letter = chr(max(ord(x.group(1)) for _, x in versions) + 1)
    rest = re.sub(r"-(final|cancel)$", "", v.group(2))
    stem = f"{screen}{letter}{rest}"
    pic = images / f"{stem}.excalidraw.svg"
    shutil.copy(latest, pic)  # starts as a copy of the latest version
    page = versions_folder / f"{stem}.md"
    write_page(page, stem, f"../images/{pic.name}")
    print(f"\n  Made version {letter} of {screen}: {stem}\n"
          f"  It starts as a copy of {latest.name.removesuffix('.svg').removesuffix('.excalidraw')}. Change what you need.\n")
    open_files(page, pic)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "new":
        new_screen(sys.argv[2], " ".join(sys.argv[3:]))
    elif len(sys.argv) == 3 and sys.argv[1] == "version":
        new_version(sys.argv[2])
    else:
        stop(__doc__)
