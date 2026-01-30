"""
Supabase Client Configuration

Database client for VisaSight backend.
"""

import os
from supabase import create_client, Client
from functools import lru_cache

# Supabase configuration
SUPABASE_URL = os.getenv(
    "SUPABASE_URL", 
    "https://wrzvcytxueeppukahhdk.supabase.co"
)
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndyenZjeXR4dWVlcHB1a2FoaGRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MDY4ODIsImV4cCI6MjA4NTI4Mjg4Mn0.i_SIXx0ZL6TmeE0JjS9YvBGw0V5hG_9w6tAQOCQ3BoY"
)


@lru_cache()
def get_supabase() -> Client:
    """
    Get cached Supabase client instance.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# Convenience export
supabase = get_supabase()
