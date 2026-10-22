import { readFile, writeFile, readdir, stat } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const output = path.join(root, "assets", "generated", "daily-report.json");
async function countFiles(dir) {
  let count = 0;
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if ([".git", "node_modules", ".venv", "venv", "__pycache__"].includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) count += await countFiles(full);
    else count += 1;
  }
  return count;
}
const readme = await readFile(path.join(root, "README.md"), "utf8");
const logo = await stat(path.join(root, "assets", "images", "quantum-suite-logo.jpeg"));
const report = {
  generated_at: new Date().toISOString(),
  repository_files: await countFiles(root),
  readme_characters: readme.length,
  quantum_suite_logo_bytes: logo.size,
  checks: {
    has_profile_sections: ["## ✦ What I'm working on", "## ✦ GitHub activity", "## ✦ Thanks for stopping by"].every((s) => readme.includes(s)),
    no_old_personal_heading: !/^#\s+[^#\n]+\s+—\s+building things that do things/im.test(readme),
    has_logo_reference: readme.includes("assets/images/quantum-suite-logo.jpeg")
  }
};
await writeFile(output, JSON.stringify(report, null, 2) + "\n", "utf8");
if (Object.values(report.checks).some((value) => value !== true)) {
  console.error("Daily profile checks failed:", report.checks);
  process.exitCode = 1;
} else {
  console.log(JSON.stringify(report, null, 2));
}
