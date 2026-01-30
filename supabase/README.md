# VisaSight - Supabase Configuration

This directory contains database migrations and configuration for Supabase.

## Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)

2. Get your project credentials:
   - Go to Settings → API
   - Copy the Project URL and anon/public key

3. Run the migration:
   - Go to SQL Editor in your Supabase dashboard
   - Copy the contents of `migrations/001_initial_schema.sql`
   - Execute the SQL

4. Configure environment variables:
   - Copy `.env.example` to `.env` in both frontend and backend directories
   - Add your Supabase credentials

## Database Structure

### Tables

- **profiles** - Extended user profiles (linked to Supabase Auth)
- **visa_cases** - User visa applications with metadata
- **prediction_results** - AI prediction outputs
- **visa_rules** - Monitored visa rules and policies
- **update_events** - Rule change tracking
- **alerts** - User notifications

### Row Level Security (RLS)

All tables have RLS enabled:
- Users can only access their own cases, predictions, and alerts
- Visa rules are publicly readable by authenticated users

## Realtime

Enable realtime for live updates:
1. Go to Database → Replication
2. Enable the tables you want to subscribe to:
   - `visa_rules` - for rule change alerts
   - `alerts` - for notifications
   - `prediction_results` - for prediction updates
