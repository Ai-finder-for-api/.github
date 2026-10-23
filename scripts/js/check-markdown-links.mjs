import { readFile, access } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
// This repository is a personal GitHub profile: validate the README only.
// Do not require deleted documentation pages or unrelated project READMEs.
const files = [".github/profile/README.md"];
const missing = [];

for (const file of files) {
  const absoluteFile = path.join(root, file);
  let source;
  try {
    source = await readFile(absoluteFile, "utf8");
  } catch (error) {
    console.error(`Unable to read ${file}: ${error.message}`);
    process.exit(1);
  }

  for (const match of source.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    const target = match[1].trim().split(/\s+/)[0].replace(/^<|>$/g, "");
    if (/^(?:https?:|mailto:|#|data:)/i.test(target)) continue;

    const clean = decodeURIComponent(target.split("#")[0].split("?")[0]);
    if (!clean) continue;

    try {
      await access(path.resolve(path.dirname(absoluteFile), clean));
    } catch {
      missing.push(`${file} -> ${target}`);
    }
  }
}

if (missing.length) {
  console.error("Missing Markdown links:\n" + missing.join("\n"));
  process.exit(1);
}
console.log("Personal profile Markdown links checked.");
