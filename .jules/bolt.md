## 2024-05-22 - Supabase N+1 Optimization
**Learning:** Supabase/PostgREST allows fetching total count alongside data using `.select('*, count="exact"')`, eliminating the need for a separate count query.
**Action:** Always check if the client library supports combined data+count fetching for paginated endpoints to halve the number of DB round-trips.
