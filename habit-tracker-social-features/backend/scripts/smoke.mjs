const baseUrl = process.env.API_BASE_URL ?? "http://localhost:4000";

async function run() {
  const loginResponse = await fetch(`${baseUrl}/auth/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email: "maya@example.com" })
  });
  const login = await loginResponse.json();

  const profileResponse = await fetch(`${baseUrl}/users/me`, {
    headers: { authorization: `Bearer ${login.token}` }
  });

  const profile = await profileResponse.json();
  console.log(JSON.stringify({
    loginStatus: loginResponse.status,
    profileStatus: profileResponse.status,
    user: profile.user?.name,
    streak: profile.stats?.streak
  }, null, 2));
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
