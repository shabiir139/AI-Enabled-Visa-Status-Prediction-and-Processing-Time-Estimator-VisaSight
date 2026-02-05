## 2026-01-31 - Independent Fetch Components
**Learning:** Components that handle their own data fetching and have no props (like `LiveWaitTimeFeed`) are often re-rendered by parent updates, wasting cycles and potentially resetting animations.
**Action:** Isolate these components with `React.memo` to ensure they only update on their own schedule.
