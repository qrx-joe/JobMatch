---
description: Clear JobMatch browser cache and localStorage
---

Clear all cached state for JobMatch to ensure clean testing:

1. Remove localStorage keys:
   - `jobmatch_profile`
   - `jobmatch_result`
2. Instruct user to:
   - Hard refresh: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
   - Or open in Incognito/Private window
   - Or DevTools → Application → Storage → Clear site data
3. Verify: ask user to reload the page and confirm filters/fields are reset to defaults

Use this AFTER any fix involving:
- Default form values changed
- Data structures changed
- Display issues persisting after code fix
- localStorage corruption suspected

Do not use this casually; warn user it will erase saved profile and last results.
