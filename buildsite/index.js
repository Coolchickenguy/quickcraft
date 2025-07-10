import pm from "picomatch";
import { dirMapFlat } from "./dirmap.js";
import {
  readFileSync,
  copyFileSync,
  existsSync,
  rmSync,
  mkdirSync,
  statSync,
} from "fs";
import { resolve, dirname } from "path";
const mainDir = dirname(import.meta.dirname);
// Find all non-.git dir files
const gitGlob = pm(".git/**");
const files = dirMapFlat(mainDir).filter((path) => !gitGlob(path));
const globs = readFileSync(resolve(mainDir, ".buildignore"))
  .toString()
  .split("\n");
const distDir = resolve(mainDir, "dist");
if (existsSync(distDir)) {
  rmSync(distDir, { force: true, recursive: true });
}
mkdirSync(distDir);
for (const file of files) {
  if (!pm.isMatch(file, globs, { dot: true })) {
    // This works because the parent dir always comes before the children
    const filePath = resolve(mainDir, file);
    const outPath = resolve(distDir, file);
    if (statSync(filePath).isFile()) {
      copyFileSync(filePath, outPath);
    } else {
      mkdirSync(outPath);
    }
  }
}
