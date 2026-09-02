import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { searchModule } from "../src/index.js";

const manifest = JSON.parse(readFileSync(new URL("../module.json", import.meta.url), "utf8"));
const discover = (enabled) => (enabled ? manifest.contributions : []);

describe("Search frontend module", () => {
  it("has a valid identity and neutral bootstrap entrypoint", () => {
    assert.equal(manifest.id, "search");
    assert.equal(manifest.version, "0.1.0");
    assert.equal(manifest.entrypoint, "./index.js");
    assert.equal(searchModule.status, "bootstrap");
  });

  it("contributes nothing while disabled", () => assert.deepEqual(discover(false), []));

  it("exposes only its bootstrap capability while enabled", () => {
    assert.deepEqual(discover(true), [
      { type: "capability", id: "search.bootstrap", title: "Search module bootstrap" },
    ]);
  });
});
