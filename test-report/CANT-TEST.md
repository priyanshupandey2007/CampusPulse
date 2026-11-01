# Items Not Verifiable in Automated Sandbox (CANT-TEST)

The following areas could not be deterministically exercised to production standards due to missing live external credentials, sandbox hardware isolation, or external third-party infrastructure:

| Item | What is missing | Why it matters | Recommended Manual Step |
|---|---|---|---|
| **Live Google OAuth Provider** | Valid Google Cloud Client Secret / interactive browser consent screen | Firebase popup authentication mocks local users if network popup fails | Sign in with real institutional Google account at `https://campuspulse-tau.vercel.app` and verify JWT claims. |
| **PostgreSQL Connection Pool** | Running PostgreSQL 15+ cluster | Local tests execute against SQLite `campuspulse_local.db` | Point `DATABASE_URL` to staging Supabase/RDS Postgres instance and verify pg_stat_activity connection limits. |
| **Vercel Edge Deployment** | Remote git push restriction / production Vercel token | Changes committed locally on `hardcore-test/2026-11-01` must not be pushed per operating constraints | Review local git diff on `hardcore-test/2026-11-01` and merge to `main` when ready to trigger Vercel deployment. |
| **High Concurrency Load (1000+ RPS)** | Distributed load test harness (e.g. k6 / Locust cluster) | Local machine tests verify sub-10ms single-client response time, but not 1,000 parallel WebSocket/SSE clients | Run k6 script against staging server to verify Uvicorn worker process concurrency. |

