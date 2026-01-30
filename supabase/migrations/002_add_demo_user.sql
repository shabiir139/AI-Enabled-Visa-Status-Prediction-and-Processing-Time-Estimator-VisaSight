-- Create Demo User Profile for Testing
-- This allows the application to work in demo mode without authentication

-- Insert demo user profile (if not exists)
INSERT INTO profiles (id, email, full_name, role)
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'demo@visasight.app',
    'Demo User',
    'user'
)
ON CONFLICT (id) DO NOTHING;

-- Optional: Temporarily disable RLS for demo/testing
-- Uncomment these lines if you want to allow unauthenticated access for testing

-- ALTER TABLE visa_cases DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE prediction_results DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE alerts DISABLE ROW LEVEL SECURITY;

-- OR: Add policies to allow demo user access
CREATE POLICY IF NOT EXISTS "Demo mode: allow demo user access"
    ON visa_cases FOR ALL
    USING (user_id = '00000000-0000-0000-0000-000000000000'::uuid);

CREATE POLICY IF NOT EXISTS "Demo mode: allow demo user insert"
    ON visa_cases FOR INSERT
    WITH CHECK (user_id = '00000000-0000-0000-0000-000000000000'::uuid);
