-- ============================================
-- VisaSight Database Schema
-- Supabase PostgreSQL
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Users (extends Supabase Auth)
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'consultant', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Visa Cases
-- ============================================
CREATE TABLE IF NOT EXISTS visa_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    nationality TEXT NOT NULL,
    visa_type TEXT NOT NULL CHECK (visa_type IN ('F-1', 'H-1B', 'B1/B2', 'L-1', 'O-1', 'J-1')),
    consulate TEXT NOT NULL,
    submission_date DATE NOT NULL,
    documents_submitted TEXT[] DEFAULT '{}',
    sponsor_type TEXT NOT NULL CHECK (sponsor_type IN ('employer', 'university', 'self', 'family', 'government')),
    prior_travel BOOLEAN DEFAULT FALSE,
    current_status TEXT DEFAULT 'pending' CHECK (current_status IN ('pending', 'in_review', 'rfe_issued', 'approved', 'denied', 'withdrawn')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Prediction Results
-- ============================================
CREATE TABLE IF NOT EXISTS prediction_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visa_case_id UUID REFERENCES visa_cases(id) ON DELETE CASCADE NOT NULL,
    predicted_approved DECIMAL(5,4) NOT NULL,
    predicted_rfe DECIMAL(5,4) NOT NULL,
    predicted_denied DECIMAL(5,4) NOT NULL,
    estimated_days_remaining INTEGER NOT NULL,
    confidence_lower INTEGER NOT NULL,
    confidence_upper INTEGER NOT NULL,
    model_version TEXT NOT NULL,
    explanation JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Visa Rules
-- ============================================
CREATE TABLE IF NOT EXISTS visa_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country TEXT NOT NULL DEFAULT 'USA',
    visa_type TEXT NOT NULL,
    rule_category TEXT NOT NULL CHECK (rule_category IN ('eligibility', 'documentation', 'processing', 'fees', 'interview', 'travel_advisory')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    effective_date DATE NOT NULL,
    source_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Update Events (Rule Changes)
-- ============================================
CREATE TABLE IF NOT EXISTS update_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID REFERENCES visa_rules(id) ON DELETE CASCADE NOT NULL,
    change_type TEXT NOT NULL CHECK (change_type IN ('created', 'updated', 'deprecated', 'reinstated')),
    previous_value TEXT,
    new_value TEXT,
    impact_score DECIMAL(3,2) DEFAULT 0,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Alerts / Notifications
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('rule_change', 'processing_update', 'prediction_update', 'case_status_change', 'system')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_entity_id UUID,
    related_entity_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Row Level Security Policies
-- ============================================

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE visa_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can only read/update their own profile
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- Visa Cases: Users can only access their own cases
CREATE POLICY "Users can view own cases"
    ON visa_cases FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own cases"
    ON visa_cases FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cases"
    ON visa_cases FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own cases"
    ON visa_cases FOR DELETE
    USING (auth.uid() = user_id);

-- Predictions: Users can only view predictions for their cases
CREATE POLICY "Users can view own predictions"
    ON prediction_results FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM visa_cases
            WHERE visa_cases.id = prediction_results.visa_case_id
            AND visa_cases.user_id = auth.uid()
        )
    );

-- Alerts: Users can only view their own alerts
CREATE POLICY "Users can view own alerts"
    ON alerts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own alerts"
    ON alerts FOR UPDATE
    USING (auth.uid() = user_id);

-- Rules are public read
ALTER TABLE visa_rules ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view rules"
    ON visa_rules FOR SELECT
    TO authenticated
    USING (true);

ALTER TABLE update_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view updates"
    ON update_events FOR SELECT
    TO authenticated
    USING (true);

-- ============================================
-- Indexes for Performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_visa_cases_user_id ON visa_cases(user_id);
CREATE INDEX IF NOT EXISTS idx_visa_cases_visa_type ON visa_cases(visa_type);
CREATE INDEX IF NOT EXISTS idx_visa_cases_status ON visa_cases(current_status);
CREATE INDEX IF NOT EXISTS idx_prediction_results_case_id ON prediction_results(visa_case_id);
CREATE INDEX IF NOT EXISTS idx_visa_rules_visa_type ON visa_rules(visa_type);
CREATE INDEX IF NOT EXISTS idx_visa_rules_category ON visa_rules(rule_category);
CREATE INDEX IF NOT EXISTS idx_update_events_detected_at ON update_events(detected_at);
CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read);

-- ============================================
-- Functions
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_visa_cases_updated_at
    BEFORE UPDATE ON visa_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_visa_rules_updated_at
    BEFORE UPDATE ON visa_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- Initial Seed Data (Sample Rules)
-- ============================================
INSERT INTO visa_rules (country, visa_type, rule_category, title, description, effective_date) VALUES
('USA', 'H-1B', 'processing', 'H-1B Cap Season Processing Priority', 'USCIS processes cap-subject H-1B petitions with priority during the annual filing window starting April 1.', '2026-01-15'),
('USA', 'F-1', 'documentation', 'F-1 STEM OPT Extension Requirements', 'Students applying for STEM OPT extension must submit I-765 with updated employer attestation form I-983.', '2026-01-10'),
('USA', 'B1/B2', 'interview', 'Interview Waiver Program Extended', 'Renewal applicants who previously held B1/B2 visas may qualify for interview waiver through December 2026.', '2026-01-05'),
('USA', 'H-1B', 'fees', 'Premium Processing Fee Update', 'Premium processing fee for H-1B petitions increased to $2,805 effective January 2026.', '2026-01-01'),
('USA', 'F-1', 'eligibility', 'SEVIS Status Verification', 'All F-1 students must maintain active SEVIS status. Grace period is 60 days after program completion.', '2025-12-01')
ON CONFLICT DO NOTHING;
