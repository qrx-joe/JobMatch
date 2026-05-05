---
description: Commit with pre-commit validation and conventional message
---

Commit changes for the current project:

1. Run `git status` to see what's changed
2. Run validation (choose based on project):
   - If `package.json` has `lint` script: `npm run lint`
   - If `package.json` has `type-check` script: `npm run type-check`
   - If `package.json` has `build` script: `npm run build`
   - For Python: `uv run python -m py_compile` or check syntax
3. Check for leftover `console.log`, `TODO`, `FIXME` in modified files
4. Stage files: `git add <files>` (ask user if unsure which files)
5. Write conventional commit message:
   - `feat:` new feature
   - `fix:` bug fix
   - `refactor:` code restructuring
   - `docs:` documentation
   - `chore:` build/tooling changes
   - `style:` formatting only
6. Commit: `git commit -m "<message>"`
7. Push: `git push` (confirm branch with user first)

Do not skip validation. Do not commit secrets (.env, credentials).
