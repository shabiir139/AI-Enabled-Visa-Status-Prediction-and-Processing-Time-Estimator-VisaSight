## 2026-02-07 - [Synchronous Database Calls in Async Handlers]
**Learning:** The codebase uses the synchronous `supabase-py` client's `execute()` method within `async` FastAPI route handlers. This blocks the event loop during database operations, negating the benefits of async I/O and limiting concurrency.
**Action:** Future optimizations should prioritize migrating to `AsyncClient` (via `create_async_client`) to enable true non-blocking database operations, or at least run these blocking calls in a thread pool.
