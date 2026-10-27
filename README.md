# UX process · Requirements first

A demo project for our UX documentation process, starting the way real work does: with requirements, not features. Features will be added later, as tags.

## Where everything lives

| What | Where |
|---|---|
| Requirements and sub-requirements | **Issues**, with the **Requirement** form |
| Wireframes and flowcharts | `requirements/`: one folder per requirement, made automatically |
| Journey maps, user stories, user understanding | `product/` |
| Wireframes not placed yet | `drafts/` |

## Requirements

- **New requirement:** Issues → New issue → **Requirement**. Type only its name in the title.
- **Sub-requirement:** open the requirement → **Create sub-issue** → **Requirement**.
- Every requirement has its **number** from GitHub (e.g. #12). In file names it's written **R012**.
- Within a minute of creating a requirement, its folder appears: `requirements/R012-contract-version-history/`. Sub-requirements use their parent's folder.

## Naming

| Name | Means |
|---|---|
| `R012-W01-version-list` | Requirement #12, wireframe 1 |
| `R012-W02a-…`, `R012-W02b-…` | Versions of wireframe 2 (their pages go in a folder `R012-W02/`) |
| `R016-W01-filter-panel` | Sub-requirement #16, wireframe 1, kept in its parent's folder |
| `R012-C01-version-history-flow` | Requirement #12, flowchart 1 |

## Adding a wireframe

In VS Code: **Terminal → Run Task… → New wireframe**. Type the requirement's number (e.g. `12`) and a short name (e.g. `version compare`). The wireframe number is worked out, and the picture and its page open side by side: draw, write the description and open questions, then **Commit** (it sends by itself).

**A new version of a screen:** **Terminal → Run Task… → New version of a screen**, then type the screen (e.g. `R012-W02`). It starts as a copy of the latest version.

Renaming a picture (e.g. adding `-final` or `-cancel`) renames its page too. Wrongly named pictures are listed in `PICTURES-NOT-ADDED.md` in that folder.

## Adding a flowchart

In the requirement's folder, create a file like `R012-C01-version-history-flow.md`, type `flowchart` and press **Tab** for the layout: the chart, then **Description** and **Open questions**.

## Don't want to wait?

The helpers also check once an hour. To run them now: **Actions** tab → **Organise requirements and wireframes** → **Run workflow**.
