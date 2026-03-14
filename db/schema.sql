CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.events_inbox (
  id BIGSERIAL PRIMARY KEY,
  request_id TEXT NOT NULL UNIQUE,
  source TEXT NOT NULL,
  event_id TEXT NOT NULL,
  idempotency_key TEXT,
  trace_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'received'
    CHECK (status IN ('received', 'processing', 'processed', 'failed', 'reprocessable')),
  attempts INT NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  last_error TEXT
);

CREATE TABLE IF NOT EXISTS app.processing_runs (
  id BIGSERIAL PRIMARY KEY,
  request_id TEXT NOT NULL,
  inbox_id BIGINT NOT NULL REFERENCES app.events_inbox(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  status TEXT NOT NULL
    CHECK (status IN ('running', 'succeeded', 'failed')),
  error_code TEXT,
  error_message TEXT
);

CREATE TABLE IF NOT EXISTS app.events_results (
  id BIGSERIAL PRIMARY KEY,
  request_id TEXT NOT NULL,
  inbox_id BIGINT NOT NULL UNIQUE REFERENCES app.events_inbox(id) ON DELETE CASCADE,
  result JSONB,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL
    CHECK (status IN ('success', 'error'))
);

CREATE INDEX IF NOT EXISTS idx_events_inbox_request_id
  ON app.events_inbox(request_id);

CREATE INDEX IF NOT EXISTS idx_events_inbox_status
  ON app.events_inbox(status);

CREATE INDEX IF NOT EXISTS idx_events_inbox_source_event
  ON app.events_inbox(source, event_id);

CREATE INDEX IF NOT EXISTS idx_processing_runs_request_id
  ON app.processing_runs(request_id);

CREATE INDEX IF NOT EXISTS idx_processing_runs_inbox_id
  ON app.processing_runs(inbox_id);

CREATE INDEX IF NOT EXISTS idx_events_results_request_id
  ON app.events_results(request_id);

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