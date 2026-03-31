import { AgentRun } from "./types";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";

export async function fetchRuns(): Promise<{ data: AgentRun[] }> {
  const response = await fetch(`${baseUrl}/runs`);
  if (!response.ok) {
    throw new Error(`Failed to load runs: ${response.status}`);
  }
  return response.json();
}
