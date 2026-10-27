# UX process · Requirements first

A demo project for our UX documentation process, starting the way real work does: with requirements, not features. Features will be added later, as tags.

## Where everything lives

| What | Where |
|---|---|
| Requirements and sub-requirements | **Issues**, with the **Requirement** form |
| Wireframes and flowcharts | `requirements/`: one folder per requirement (sub-requirements inside it), each with `wireframes/` and `flowcharts/`, made automatically |
| Journey maps, user stories, user understanding | `product/` |
| Wireframes not placed yet | `drafts/` |

## Requirements

- **New requirement:** Issues → New issue → **Requirement**. Type only its name in the title.
- **Sub-requirement:** open the requirement → **Create sub-issue** → **Requirement**.
- **Codes:** you type only the name; within a minute the code is added to the title. Requirements are **R001, R002 …** (counting only requirements; the next is the one after the highest ever used). Sub-requirements are counted inside their requirement: **R015-S01, R015-S02 …** A code never changes and is never reused. (GitHub's own issue numbers, like #27, also show on GitHub; we don't use them.)
- Within a minute of creating a requirement, its folder appears, with `wireframes` and `flowcharts` inside:

```
requirements/
└── R001-contract-list-page/
    ├── wireframes/
    ├── flowcharts/
    └── R001-S01-filters-on-the-contract-list/   ← a sub-requirement, inside its requirement
        ├── wireframes/
        └── flowcharts/
```

- If a requirement is later moved inside another one, its folder moves with it.

## Naming

| Name | Means |
|---|---|
| `R012-W01-version-list` | Requirement R012, wireframe 1 |
| `R012-W02a-…`, `R012-W02b-…` | Versions of wireframe 2 (their pages go in a folder `wireframes/R012-W02/`) |
| `R001-S01-W01-filter-panel` | Sub-requirement R001-S01, wireframe 1, in its own folder |
| `R012-C01-version-history-flow` | Requirement R012, flowchart 1 |

## Adding a wireframe

In VS Code: **Terminal → Run Task… → New wireframe**. Type the requirement (e.g. `12` for R012, or `15-1` for the sub-requirement R015-S01) and a short name (e.g. `version compare`). The wireframe number is worked out, and the picture and its page open side by side: draw, write the description and open questions, then **Commit** (it sends by itself).

**A new version of a screen:** **Terminal → Run Task… → New version of a screen**, then type the screen (e.g. `R012-W02` or `R015-S01-W02`). It starts as a copy of the latest version.

Renaming a picture (e.g. adding `-final` or `-cancel`) renames its page too. Wrongly named pictures are listed in `PICTURES-NOT-ADDED.md` in that folder.

## Adding a flowchart

In the requirement's `flowcharts` folder, create a file like `R012-C01-version-history-flow.md`, type `flowchart` and press **Tab** for the layout: the chart, then **Description** and **Open questions**.

## Don't want to wait?

The helpers also check once an hour. To run them now: **Actions** tab → **Organise requirements and wireframes** → **Run workflow**.
