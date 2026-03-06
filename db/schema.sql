CREATE SCHEMA IF NOT EXISTS app;

-- Ingestion inbox (Project A)
CREATE TABLE IF NOT EXISTS app.events_inbox (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  event_id TEXT NOT NULL,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'received',
  attempts INT NOT NULL DEFAULT 0,
  last_error TEXT
);

CREATE TABLE IF NOT EXISTS app.events_results (
  id BIGSERIAL PRIMARY KEY,
  inbox_id BIGINT REFERENCES app.events_inbox(id),
  result JSONB,
  processed_at TIMESTAMPTZ DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'done'
);

-- Agent audit log (Project C placeholder)
CREATE TABLE IF NOT EXISTS app.agent_audit_log (
  id BIGSERIAL PRIMARY KEY,
  requested_by TEXT,
  proposed_action TEXT NOT NULL,
  payload JSONB NOT NULL,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'proposed'
);
