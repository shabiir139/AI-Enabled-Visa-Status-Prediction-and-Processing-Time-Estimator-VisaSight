## 2024-05-22 - Supabase N+1 Pagination Anti-Pattern
**Learning:** Found an N+1 query pattern where pagination count was fetched in a separate query (re-applying all filters) instead of using `count="exact"` in the data query. This doubles DB load and risks filter drift.
**Action:** Always check `supabase.table().select()` calls. If paginating, ensure `count="exact"` is used in the main query to get both data and count in one round-trip.
