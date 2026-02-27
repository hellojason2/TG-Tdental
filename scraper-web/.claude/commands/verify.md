# Verify Command

This command runs tests on only the files that were changed, ensuring targeted verification.

## Usage

```
/verify [files...]
```

## Examples

```
/verify                    # Verify current changes
/verify app/api/auth.py    # Verify specific file
/verify app/api/*.py       # Verify multiple files
```

## Workflow

### Step 1: Identify Changed Files
- Check git diff for modified files
- Include both new and modified files
- List all files to be tested

### Step 2: Run Targeted Tests

#### For Backend Files (Python)
```bash
# Test specific API endpoint
curl -X POST http://localhost:8899/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@tdental.vn", "password": "admin123"}'

# Test customer API
curl http://localhost:8899/api/customers \
  -H "Authorization: Bearer <token>"

# Test appointment API
curl http://localhost:8899/api/appointments \
  -H "Authorization: Bearer <token>"
```

#### For Frontend Files (HTML/CSS/JS)
```bash
# Check for JavaScript errors
# 1. Open browser console
# 2. Navigate to page
# 3. Check for red errors

# Test navigation
# 1. Click each sidebar link
# 2. Verify page loads
# 3. Check console for errors
```

#### For Database Changes
```bash
# Test database connection
python -c "from app.core.database import get_conn; conn=get_conn(); print('DB OK'); conn.close()"

# Test specific query
python -c "from app.core.database import get_conn, get_cursor; conn=get_conn(); cur=get_cursor(conn); cur.execute('SELECT COUNT(*) FROM customers'); print(cur.fetchone()); conn.close()"
```

### Step 3: Verify No Regressions

#### Check Dependent Modules
- If changed `app/api/auth.py`, also test `/api/customers` (depends on auth)
- If changed `app/core/database.py`, test all API endpoints
- If changed `static/js/app.js`, test all pages

#### Run Integration Tests
```bash
# Full API test suite
curl http://localhost:8899/api/auth/login -X POST -H "Content-Type: application/json" -d '{"email":"admin@tdental.vn","password":"admin123"}'

# Store token and test protected endpoints
TOKEN="your_token_here"
curl http://localhost:8899/api/customers -H "Authorization: Bearer $TOKEN"
curl http://localhost:8899/api/appointments -H "Authorization: Bearer $TOKEN"
```

### Step 4: Report Results

#### Success Format
```
✅ Verification Passed
Files tested: app/api/auth.py
Tests run: 3
- Login endpoint: ✅
- Logout endpoint: ✅  
- Session validation: ✅
```

#### Failure Format
```
❌ Verification Failed
Files tested: app/api/routes.py
Tests run: 3
- Customer list: ✅
- Customer create: ❌ (500 error)
- Customer update: ⏳ (not tested)

Error: psycopg2.OperationalError - connection refused
```

## Important

- **Always** test changed files, not the entire codebase
- **Never** skip dependent module tests
- **Always** update TASKS.md with verification results
- **Never** mark task as done without verification

---

**Created**: 2026-02-26
**Enforced By**: Project Standards