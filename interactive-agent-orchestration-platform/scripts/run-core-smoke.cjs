const { readFileSync, writeFileSync, mkdirSync } = require('node:fs');
const { join } = require('node:path');

async function main() {
  const { OrchestrationEngine, summarizeRuns } = await import('../packages/core/dist/src/index.js');

  const engine = new OrchestrationEngine();
  const run = engine.createRun({
    agentName: 'support-agent',
    userIntent: 'download the latest invoice and email it to the finance alias',
    tags: ['billing', 'demo']
  });

  await engine.executeRun(run.id, { minStepLatencyMs: 1, maxStepLatencyMs: 1 });

  const runs = engine.listRuns();
  const summary = summarizeRuns(runs);
  const output = { summary, latestRun: runs[0], events: engine.getEvents(run.id) };

  const outDir = join(__dirname, '..', 'data');
  mkdirSync(outDir, { recursive: true });
  writeFileSync(join(outDir, 'sample-run-output.json'), JSON.stringify(output, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
