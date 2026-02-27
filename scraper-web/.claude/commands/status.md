# Status Command

This command updates TASKS.md with the current task status.

## Usage

```
/status <task_name> <status> [notes]
```

## Status Values

| Symbol | Meaning |
|--------|---------|
| 🔒 | IN PROGRESS - Currently working on |
| ✅ | DONE - Completed and verified |
| ❌ | FAILED - Error encountered |
| ⏳ | TODO - Not started |
| ⏸️ | BLOCKED - Waiting on something |

## Examples

```
/status "Deep customer sync" 🔒 "Starting sync process"
/status "Fix login auth" ✅ "Login works with JWT tokens"
/status "API endpoint" ❌ "Database connection error"
/status "New feature" ⏳ "Planned for next sprint"
/status "Bug fix" ⏸️ "Waiting for TDental API fix"
```

## Workflow

### Step 1: Read Current TASKS.md
- Check current task statuses
- Identify task to update
- Verify ownership

### Step 2: Update Status
- Change status symbol
- Add timestamp
- Include verification notes

### Step 3: Verify Update
- Confirm TASKS.md was updated correctly
- Check no other tasks affected
- Verify file saved

## Task Status Template

```
| Task | Status | Owner | Files Touched | Verified |
|------|--------|-------|---------------|----------|
| [Task Name] | [Status] | [Owner] | [Files] | [Verified] |
```

## Examples

### Starting a Task
```
| Deep customer sync | 🔒 IN PROGRESS | agent-3 | app/services/sync.py | ❌ |
```

### Completing a Task
```
| Fix login auth | ✅ DONE | agent-1 | app/api/auth.py, app/main.py | ✅ tested |
```

### Failing a Task
```
| Bridge timeout | ❌ FAILED | agent-2 | docker-compose.yml | ❌ |
Reason: TDental API rate limiting
```

## Important

- **Always** claim task before starting (🔒 IN PROGRESS)
- **Always** update status after completion (✅ DONE)
- **Always** include verification status
- **Never** overwrite other tasks
- **Always** use exact task name from TASKS.md

---

**Created**: 2026-02-26
**Enforced By**: Project Standards