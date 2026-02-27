# Self-Review Command

This command enforces the self-review loop before marking any task as complete.

## Usage

```
/review
```

## Workflow

Before marking any code change as complete, you MUST:

1. **Re-read CLAUDE.md**
   - Understand project context
   - Check for any conflicting rules
   - Verify file ownership

2. **Re-read TASKS.md**
   - Confirm task is properly claimed
   - Check dependencies
   - Verify completion criteria

3. **Run tests on changed files only**
   - Use targeted testing, not full suite
   - Verify API endpoints work
   - Check database operations

4. **Verify no regression on dependent modules**
   - Check related API endpoints
   - Verify frontend integration
   - Test database relationships

5. **Update TASKS.md**
   - Mark task as ✅ DONE
   - Add verification notes
   - Document any issues found

## Examples

### Before
```
Task: Fix login auth
Status: 🔒 IN PROGRESS
Files: app/api/auth.py
```

### After (if successful)
```
Task: Fix login auth
Status: ✅ DONE
Files: app/api/auth.py, app/main.py
Verified: ✅ tested - login works with JWT tokens
```

### After (if failed)
```
Task: Fix login auth
Status: ❌ FAILED
Reason: JWT token verification fails
Next: Investigate token parsing in auth.py
```

## Important

**DO NOT** proceed to next task until current task passes all tests.

**DO NOT** mark task as done without:
- Running actual tests
- Checking dependent modules
- Updating TASKS.md

---

**Created**: 2026-02-26
**Enforced By**: Project Standards