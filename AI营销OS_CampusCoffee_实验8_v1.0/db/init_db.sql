CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, version TEXT NOT NULL, started_at TEXT NOT NULL, status TEXT NOT NULL, input_manifest TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS brand_profile (brand TEXT PRIMARY KEY, version TEXT NOT NULL, profile_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS consumer_feedback (feedback_id TEXT PRIMARY KEY, segment TEXT, topic TEXT, sentiment TEXT, rating REAL, evidence_quote TEXT, source TEXT, consent_status TEXT, is_mock INTEGER);
CREATE TABLE IF NOT EXISTS competitor_snapshot (competitor TEXT PRIMARY KEY, category TEXT, availability_score REAL, price_index REAL, brand_heat_index REAL, content_coverage_pct REAL, student_fit_score REAL, source TEXT, is_mock INTEGER);
CREATE TABLE IF NOT EXISTS experiment_result (user_id TEXT PRIMARY KEY, variant TEXT, clicked_coupon INTEGER, purchased INTEGER, order_value_rmb REAL, feedback_score REAL, trial_intent REAL, purchase_intent REAL, brand_fit REAL, consent_status TEXT, is_mock INTEGER);
CREATE TABLE IF NOT EXISTS evidence_trace (evidence_id TEXT PRIMARY KEY, module TEXT NOT NULL, source TEXT NOT NULL, claim TEXT NOT NULL, verification_status TEXT NOT NULL);
