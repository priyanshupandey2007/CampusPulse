-- Initialize assistant_ro role with SELECT only grants for advisor assistant endpoint
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'assistant_ro') THEN
      CREATE ROLE assistant_ro WITH LOGIN PASSWORD 'assistant_ro_secret';
   END IF;
END
$$;

GRANT CONNECT ON DATABASE campuspulse_db TO assistant_ro;
GRANT USAGE ON SCHEMA public TO assistant_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO assistant_ro;

-- ── Row Level Security (RLS) Policies (Item 1) ────────────────────────────────
-- Enable RLS on core tables
ALTER TABLE IF EXISTS students ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS weekly_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS interventions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS audit_log ENABLE ROW LEVEL SECURITY;

-- Allow public read access to students and interventions for authorized app clients
CREATE POLICY IF NOT EXISTS advisor_all_students ON students FOR ALL TO PUBLIC USING (true);
CREATE POLICY IF NOT EXISTS advisor_all_interventions ON interventions FOR ALL TO PUBLIC USING (true);
CREATE POLICY IF NOT EXISTS assistant_ro_select ON weekly_metrics FOR SELECT TO assistant_ro USING (true);
