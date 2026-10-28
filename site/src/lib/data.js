// Everything the website shows, read once when the site is built:
// requirements and their comments from the GitHub issues, wireframes and flowcharts from the requirement folders.
import fs from "node:fs";
import path from "node:path";
import { Marked } from "marked";

export const REPO = process.env.GITHUB_REPOSITORY || "saanchi365/ux-process-requirements";
export const REPO_URL = `https://github.com/${REPO}`;
const ROOT = path.resolve(process.cwd(), "..");
const REQUIREMENTS = path.join(ROOT, "requirements");

// the six statuses, in the order they're shown
export const ST = { todo: "To do", prog: "In progress", done: "Completed", paused: "Paused", closed: "Closed", input: "Needs input" };
export const ORDER = ["todo", "prog", "done", "paused", "closed", "input"];
// a status label on the issue, e.g. "status: in progress"; an open issue without one is To do,
// a closed one is Completed, or Closed when it was closed as "not planned"
const STATUS_LABEL = { "in progress": "prog", "paused": "paused", "needs input": "input" };

const CODE = /^\s*(R\d+(?:\s*-\s*S\d+)*)\b[\s·:.\-–—]*(.*)$/i;
const tidy = c => { const p = c.match(/\d+/g); return `R${p[0].padStart(3, "0")}` + p.slice(1).map(x => `-S${x.padStart(2, "0")}`).join(""); };

// comments and descriptions are written by people on GitHub: render them as markdown, but never as raw page code
const md = new Marked({ gfm: true, breaks: true });
md.use({ renderer: {
  html: t => esc(t.text),
  link({ href, text }) { return /^(https?:|mailto:|#|\/)/.test(href) ? `<a href="${esc(href)}" target="_blank" rel="noopener">${text}</a>` : text; },
} });
export const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
export const html = s => md.parse(String(s ?? ""));

const QUERY = `query($owner:String!,$name:String!,$after:String){repository(owner:$owner,name:$name){
  issues(first:50,after:$after,orderBy:{field:CREATED_AT,direction:ASC}){pageInfo{hasNextPage endCursor}
    nodes{number title url state stateReason body createdAt updatedAt author{login} labels(first:30){nodes{name}} parent{number}
      comments(first:100){nodes{id url body createdAt author{login avatarUrl}}}}}}}`;

async function issues() {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error("GITHUB_TOKEN is needed to read the requirements from GitHub");
  const [owner, name] = REPO.split("/"), out = [];
  for (let after = null; ;) {
    const res = await fetch("https://api.github.com/graphql", {
      method: "POST", headers: { Authorization: `bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ query: QUERY, variables: { owner, name, after } }),
    });
    const j = await res.json();
    if (j.errors) throw new Error(JSON.stringify(j.errors));
    const page = j.data.repository.issues;
    out.push(...page.nodes);
    if (!page.pageInfo.hasNextPage) return out;
    after = page.pageInfo.endCursor;
  }
}

// the issue form's sections: "### Requirement", "### Given by", "### Done when" ...
function sections(body) {
  const out = {};
  for (const part of String(body || "").split(/^###\s+/m).slice(1)) {
    const [head, ...rest] = part.split("\n");
    const text = rest.join("\n").trim();
    out[head.trim().toLowerCase()] = text === "_No response_" ? "" : text;
  }
  return out;
}
const bullets = t => String(t || "").split("\n").map(l => l.replace(/^\s*[-*]\s*/, "").trim()).filter(Boolean);

// a comment's first line can say what it's about: "On wireframe R001-W01a" or "On flowchart R001-C01".
// ❓ marks an open question; once it's answered, the person who asked changes it to ✅.
const ABOUT = /^\s*(?:💬\s*)?\**on (wireframe|flowchart)\s+(R[\w-]+?)\**\s*[:.]?\s*$/im;
function comment(c) {
  let body = c.body.replace(/\r/g, ""), on = null;
  const first = body.split("\n")[0];
  const m = first.match(ABOUT);
  if (m) { on = { kind: m[1].toLowerCase(), key: m[2].toUpperCase().replace(/-W(\d+)([A-Z])$/, (_, n, l) => `-W${n}${l.toLowerCase()}`) }; body = body.slice(first.length).trim(); }
  const question = /^\s*(❓|✅)/.test(body) ? (body.trim().startsWith("✅") ? "closed" : "open") : null;
  if (question) body = body.trim().replace(/^(❓|✅)\s*(open question:?|closed question:?)?\s*/i, "");
  return { id: c.id, url: c.url, who: c.author?.login || "someone", when: c.createdAt, on, question, html: html(body), text: body };
}

/* ---------- files in the requirement folders ---------- */
const walk = dir => fs.existsSync(dir) ? fs.readdirSync(dir, { withFileTypes: true }).flatMap(d => d.isDirectory() ? walk(path.join(dir, d.name)) : [path.join(dir, d.name)]) : [];
const rel = p => path.relative(ROOT, p).split(path.sep).join("/");
function mdSection(text, name) {
  const m = text.match(new RegExp(`^##\\s+${name}\\s*$([\\s\\S]*?)(?=^##\\s|(?![\\s\\S]))`, "im"));
  return m ? m[1].trim() : "";
}
const pretty = slug => { const s = slug.replace(/-/g, " ").trim(); return s ? s[0].toUpperCase() + s.slice(1) : ""; };
const editUrl = p => `${REPO_URL}/blob/main/${rel(p)}`;

// wireframe pages, e.g. wireframes/R001-W01/R001-W01a-contract-list-table.md (versions) or wireframes/R012-W02-reason-box.md
function wireframes() {
  const out = [];
  for (const p of walk(REQUIREMENTS)) {
    const f = path.basename(p), m = f.match(/^(R\d{3,}(?:-S\d{2,})*)-W(\d{2,})([a-z]?)(?:-(.*))?\.md$/);
    if (!m || !rel(p).includes("/wireframes/") || m[4] === "compare") continue;  // the compare page is made automatically
    const text = fs.readFileSync(p, "utf8");
    const img = text.match(/!\[[^\]]*\]\(([^)\s]+)\)/);
    const status = /-final$/.test(m[4] || "") ? "final" : /-cancel$/.test(m[4] || "") ? "cancel" : null;
    out.push({
      req: m[1], screen: `${m[1]}-W${m[2]}`, key: `${m[1]}-W${m[2]}${m[3]}`, version: m[3] || null, status,
      name: pretty((m[4] || "").replace(/-(final|cancel)$/, "")) || `Wireframe W${m[2]}`,
      image: img ? rel(path.resolve(path.dirname(p), decodeURI(img[1]))) : null,
      description: html(mdSection(text, "Description")), questions: bullets(mdSection(text, "Open questions")),
      file: editUrl(p), updated: fs.statSync(p).mtime.toISOString(),
    });
  }
  return out.sort((a, b) => a.key.localeCompare(b.key));
}

// flowchart pages, e.g. flowcharts/R012-C01-approval-steps.md: a mermaid chart, then Description and Open questions
function flowcharts() {
  const out = [];
  for (const p of walk(REQUIREMENTS)) {
    const f = path.basename(p), m = f.match(/^(R\d{3,}(?:-S\d{2,})*)-C(\d{2,})(?:-(.*))?\.md$/);
    if (!m || !rel(p).includes("/flowcharts/")) continue;
    const text = fs.readFileSync(p, "utf8");
    const chart = text.match(/```mermaid\s*\n([\s\S]*?)```/);
    const title = (text.match(/^#\s+(.*)$/m) || [])[1] || "";
    out.push({
      req: m[1], key: `${m[1]}-C${m[2]}`, name: title.split("›").pop().trim() || pretty(m[3] || "") || `Flowchart C${m[2]}`,
      chart: chart ? chart[1].trim() : "", description: html(mdSection(text, "Description")), questions: bullets(mdSection(text, "Open questions")),
      file: editUrl(p),
    });
  }
  return out.sort((a, b) => a.key.localeCompare(b.key));
}

/* ---------- putting it together ---------- */
let cache;
export async function load() {
  if (cache) return cache;
  const raw = await issues(), wfs = wireframes(), fcs = flowcharts();
  const byNumber = {}, all = [];
  for (const i of raw) {
    const m = i.title.match(CODE);
    if (!m) continue;  // not a requirement (yet): it gets its code within a minute of being added
    const labels = i.labels.nodes.map(l => l.name), sec = sections(i.body);
    const sl = labels.map(l => l.match(/^status:\s*(.+)$/i)).find(Boolean);
    const st = i.state === "CLOSED" ? (i.stateReason === "NOT_PLANNED" ? "closed" : "done") : (sl && STATUS_LABEL[sl[1].toLowerCase()]) || "todo";
    const r = {
      code: tidy(m[1]), name: m[2].trim(), number: i.number, url: i.url, st, parentNumber: i.parent?.number || null,
      features: labels.map(l => l.match(/^feature:\s*(.+)$/i)).filter(Boolean).map(x => x[1].trim()),
      what: html(sec.requirement), done: bullets(sec["done when"]), details: bullets(sec.details), questions: bullets(sec["open questions"]),
      givenBy: sec["given by"] || i.author?.login || "", source: sec["where it came from"] || "", sure: sec["how sure are we?"] || "",
      created: i.createdAt, updated: i.updatedAt, author: i.author?.login || "",
      comments: i.comments.nodes.map(comment), subs: [], parent: null,
    };
    r.wireframes = wfs.filter(w => w.req === r.code);
    r.flowcharts = fcs.filter(f => f.req === r.code);
    byNumber[i.number] = r; all.push(r);
  }
  for (const r of all) if (r.parentNumber && byNumber[r.parentNumber]) { r.parent = byNumber[r.parentNumber]; r.parent.subs.push(r); }
  for (const r of all) r.subs.sort((a, b) => a.code.localeCompare(b.code));
  const reqs = all.filter(r => !r.parent).sort((a, b) => a.code.localeCompare(b.code));

  // recent activity: requirements added and comments made, newest first
  const activity = [
    ...all.map(r => ({ type: "added", who: r.author, when: r.created, req: r })),
    ...all.flatMap(r => r.comments.map(c => ({ type: "comment", who: c.who, when: c.when, req: r, text: c.text.split("\n")[0].slice(0, 140), question: c.question }))),
  ].sort((a, b) => b.when.localeCompare(a.when));

  const features = [...new Set(reqs.flatMap(r => r.features))].sort();
  cache = { reqs, all, activity, features, builtAt: new Date().toISOString() };
  return cache;
}

// a wireframe's screens: versions of the same screen sit side by side
export function screens(list) {
  const out = [];
  for (const w of list) {
    let s = out.find(x => x.key === w.screen);
    if (!s) out.push(s = { key: w.screen, name: w.name, versions: [] });
    s.versions.push(w);
  }
  return out;
}

export function summary(list) {
  const c = Object.fromEntries(ORDER.map(k => [k, 0]));
  list.forEach(r => c[r.st]++);
  return c;
}

// "3 min ago", "Yesterday", "12 Oct"
export function ago(iso, now = Date.now()) {
  const d = new Date(iso), m = Math.round((now - d) / 60000);
  if (m < 1) return "Just now";
  if (m < 60) return `${m} min ago`;
  if (m < 60 * 24) return `${Math.round(m / 60)} h ago`;
  if (m < 60 * 48) return "Yesterday";
  if (m < 60 * 24 * 7) return `${Math.round(m / 1440)} days ago`;
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}
export const day = iso => { const d = new Date(iso), t = new Date(), y = new Date(Date.now() - 864e5);
  const same = (a, b) => a.toDateString() === b.toDateString();
  return same(d, t) ? "Today" : same(d, y) ? "Yesterday" : d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "short" }); };
