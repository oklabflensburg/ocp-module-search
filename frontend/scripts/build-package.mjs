import { cp, mkdir, rm } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(root, "dist");
await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

await cp(resolve(root, "src/index.js"), resolve(dist, "index.js"));
await cp(resolve(root, "module.json"), resolve(dist, "module.json"));
