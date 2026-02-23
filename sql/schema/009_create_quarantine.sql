-- ============================================================================
-- File:        009_create_quarantine.sql
-- Description: Creates the _quarantine table for rejected records.
--              Records that fail critical or high-severity DQ validation
--              rules are routed here with full error context instead of
--              being silently dropped, enabling investigation and replay.
-- Table:       people_analytics._quarantine
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_analytics._quarantine (
  quarantine_date     TIMESTAMP NOT NULL,
  source_table        STRING NOT NULL,
  record_json         STRING,           -- Original record as JSON string
  failure_rule_id     STRING,
  failure_reason      STRING,
  _batch_id           STRING
);
