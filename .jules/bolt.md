## 2025-02-19 - [Supabase Count Optimization]
**Learning:** Supabase/PostgREST allows fetching the count of total rows along with the data in a single request using `.select("*", count="exact")`.
**Action:** When needing pagination with total counts, always check if the client/ORM supports retrieving count in the initial query to avoid a second round-trip.
