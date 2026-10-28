// Copies the pictures from the requirement folders into the website, so wireframes can be shown.
import fs from "node:fs";
import path from "node:path";
const from = path.resolve("..", "requirements"), to = path.resolve("public", "files", "requirements");
fs.rmSync(to, { recursive: true, force: true });
const walk = d => fs.existsSync(d) ? fs.readdirSync(d, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]) : [];
let n = 0;
for (const p of walk(from)) {
  if (!/\.(svg|png|jpe?g|gif|webp)$/i.test(p)) continue;
  const out = path.join(to, path.relative(from, p));
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.copyFileSync(p, out); n++;
}
console.log(`Copied ${n} pictures`);
