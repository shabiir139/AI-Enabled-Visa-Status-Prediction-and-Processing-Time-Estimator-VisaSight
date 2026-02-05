## 2025-02-18 - Supabase Pagination Optimization
**Learning:** The codebase was making two separate Supabase requests for pagination (data + count). The Python Supabase client supports `count='exact'` in the `.select()` method, allowing retrieval of both in a single round-trip.
**Action:** Always check for redundant count queries when seeing pagination logic with Supabase/PostgREST. Use `.select('*', count='exact')`.
## 2025-02-18 - GitHub Actions Working Directory
**Learning:** The previous CI workflow was failing because it referenced `./visasight/frontend` and `./visasight/backend`, which do not exist in this repo structure. The correct paths are `./frontend` and `./backend`.
**Action:** When working with GitHub Actions, always verify the repository structure using `ls -R` or `tree` before setting `working-directory`.
