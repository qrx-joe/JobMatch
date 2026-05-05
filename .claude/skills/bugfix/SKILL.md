---
description: Systematic bug investigation for JobMatch
---

Before fixing any JobMatch bug, verify these in order:

1. **Reproduce** — Confirm you can see the failure. Ask user for screenshot description if visual.
2. **Check console** — Browser DevTools console for JS errors; terminal for build errors.
3. **Check cache/state** — If data/display issue: clear localStorage (`jobmatch_profile`, `jobmatch_result`), hard refresh (Ctrl+F5).
4. **Check Excel parsing** — If fields blank or missing: log `detectColumn` results, verify header patterns match user's Excel format.
5. **Check join logic** — If stats (paid/competition) missing: verify `buildJobJoinKey` has non-empty unit+position; check normalizeUnitName behavior.
6. **Check matcher** — If wrong match level: log `parseOther()` output, verify profile values.

After fixing:
1. Clear localStorage and reload to verify with clean state
2. Run `/validate` (build check)
3. Test the actual user flow end-to-end
4. Do not declare success until verified with clean state

Scope: JobMatch frontend only. For backend/DB issues, use different protocol.
