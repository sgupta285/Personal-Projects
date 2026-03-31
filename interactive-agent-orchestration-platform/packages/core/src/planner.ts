import { CreateRunInput, StepTrace } from "./types.js";
import { uid } from "./utils.js";

function inferStepsFromIntent(intent: string): Array<Pick<StepTrace, "name" | "toolName" | "rationale" | "input">> {
  const normalized = intent.toLowerCase();

  if (normalized.includes("invoice")) {
    return [
      {
        name: "Load account workspace",
        toolName: "browser.navigate",
        rationale: "The agent needs the authenticated workspace before it can inspect billing data.",
        input: { url: "https://example.test/account" }
      },
      {
        name: "Open billing screen",
        toolName: "browser.click",
        rationale: "Billing pages usually contain the latest statement or downloadable invoice.",
        input: { selector: "[data-nav='billing']" }
      },
      {
        name: "Download latest invoice",
        toolName: "browser.download",
        rationale: "The user asked for the latest invoice, so the agent should capture the most recent artifact.",
        input: { selector: "[data-testid='latest-invoice']" }
      }
    ];
  }

  if (normalized.includes("email") || normalized.includes("send")) {
    return [
      {
        name: "Collect result context",
        toolName: "context.read",
        rationale: "The agent gathers the material that needs to be included in the outgoing summary.",
        input: { scope: "latest_results" }
      },
      {
        name: "Draft operator summary",
        toolName: "llm.summarize",
        rationale: "A concise, operator-readable summary improves oversight before anything is sent externally.",
        input: { format: "email_brief" }
      },
      {
        name: "Send notification",
        toolName: "email.send",
        rationale: "The final action delivers the result to the intended recipient.",
        input: { template: "run_summary_v1" }
      }
    ];
  }

  return [
    {
      name: "Read task context",
      toolName: "context.read",
      rationale: "The agent needs the current task context before it can choose a tool.",
      input: { scope: "run_context" }
    },
    {
      name: "Choose next action",
      toolName: "planner.plan",
      rationale: "The orchestrator records the planning decision so operators can inspect it later.",
      input: { intent }
    },
    {
      name: "Produce final output",
      toolName: "llm.respond",
      rationale: "The run ends by returning a user-facing result.",
      input: { style: "operator_friendly" }
    }
  ];
}

export function buildInitialSteps(input: CreateRunInput): StepTrace[] {
  const stepDrafts = input.steps && input.steps.length > 0 ? input.steps : inferStepsFromIntent(input.userIntent);

  return stepDrafts.map((step) => ({
    id: uid("step"),
    name: step.name,
    rationale: step.rationale,
    toolName: step.toolName,
    status: "pending",
    input: step.input,
    costUsd: 0,
    latencyMs: 0,
    retryCount: 0
  }));
}
