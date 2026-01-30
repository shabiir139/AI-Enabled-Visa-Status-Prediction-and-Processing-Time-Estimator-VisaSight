import { createBrowserClient } from '@supabase/ssr';

// Browser client for client components
export function createClient() {
    return createBrowserClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );
}

// Export singleton instance for convenience
export const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://wrzvcytxueeppukahhdk.supabase.co',
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndyenZjeXR4dWVlcHB1a2FoaGRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MDY4ODIsImV4cCI6MjA4NTI4Mjg4Mn0.i_SIXx0ZL6TmeE0JjS9YvBGw0V5hG_9w6tAQOCQ3BoY'
);
