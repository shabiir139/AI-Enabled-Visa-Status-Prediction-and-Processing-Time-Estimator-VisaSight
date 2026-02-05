## 2025-02-18 - Supabase Pagination Optimization
**Learning:** The codebase was making two separate Supabase requests for pagination (data + count). The Python Supabase client supports `count='exact'` in the `.select()` method, allowing retrieval of both in a single round-trip.
**Action:** Always check for redundant count queries when seeing pagination logic with Supabase/PostgREST. Use `.select('*', count='exact')`.
