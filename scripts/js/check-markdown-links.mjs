import { readFile, access } from "node:fs/promises";
import path from "node:path";
const root = process.cwd();
const files = ["README.md", "docs/INTERACTIVE_STATS.md", "docs/MEDIA_GUIDE.md", "player/README.md"];
const missing = [];
for (const file of files) {
  const source = await readFile(path.join(root, file), "utf8");
  for (const match of source.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    const target = match[1].trim().split(/\s+/)[0].replace(/^<|>$/g, "");
    if (/^(?:https?:|mailto:|#)/i.test(target)) continue;
    const clean = target.split("#")[0];
    if (!clean) continue;
    try { await access(path.resolve(path.dirname(path.join(root, file)), clean)); }
    catch { missing.push(file + " -> " + target); }
  }
}
if (missing.length) { console.error("Missing Markdown links:\n" + missing.join("\n")); process.exit(1); }
console.log("Markdown links checked.");
