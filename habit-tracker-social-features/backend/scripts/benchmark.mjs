const baseUrl = process.env.API_BASE_URL ?? "http://localhost:4000";

async function login() {
  const response = await fetch(`${baseUrl}/auth/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email: "maya@example.com" })
  });
  return response.json();
}

async function run() {
  const { token } = await login();
  const startedAt = performance.now();
  const count = 25;

  for (let index = 0; index < count; index += 1) {
    const response = await fetch(`${baseUrl}/users/me`, {
      headers: { authorization: `Bearer ${token}` }
    });
    if (!response.ok) {
      throw new Error(`Request failed at ${index}`);
    }
    await response.json();
  }

  const elapsed = performance.now() - startedAt;
  console.log(JSON.stringify({
    requests: count,
    totalMs: Number(elapsed.toFixed(2)),
    averageMs: Number((elapsed / count).toFixed(2))
  }, null, 2));
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
