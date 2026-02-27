# TDental Implementation Tasks - Complete Surgical Checklist

This document provides an extensive, step-by-step task list to complete the TDental replica to 100%.

---

## PHASE 1: CORE INFRASTRUCTURE (Complete ✅)

### 1.1 Database Setup
- [x] PostgreSQL database on Railway
- [x] 27 tables created with proper schemas
- [x] Indexes on frequently queried columns
- [x] Foreign key relationships established

### 1.2 Backend API
- [x] FastAPI server running on port 8899
- [x] Authentication (JWT-based)
- [x] 35+ API endpoints implemented
- [x] Session management

### 1.3 Data Sync
- [x] TDental API client with JWT auth
- [x] Customer sync (~31K records)
- [x] Appointment sync (~212K records)
- [x] Sale order sync (~56K records)

**Status: PHASE 1 COMPLETE** ✅

---

## PHASE 2: FRONTEND PAGES (Complete ✅)

### 2.1 COMPLETED PAGES

#### ✅ Login Page
- [x] Login form with email/password
- [x] JWT token handling
- [x] Session cookie management
- [x] Error handling for invalid credentials
- [x] Redirect to dashboard on success

#### ✅ Dashboard (Tổng quan)
- [x] Revenue donut chart
- [x] Reception panel (Tiếp Nhận)
- [x] Appointments panel (Lịch Hẹn)
- [x] Services table (Dịch Vụ)
- [x] Quick action buttons
- [x] Fallback data when API unavailable

#### ✅ Customers Page (Khách hàng)
- [x] Customer list with pagination
- [x] Search functionality
- [x] Filter by status
- [x] Filter by branch
- [x] Add new customer modal
- [x] Edit customer modal
- [x] Delete customer with confirmation
- [x] Customer detail panel

#### ✅ Appointments Page (Lịch hẹn)
- [x] Calendar view
- [x] Appointment list
- [x] Create appointment modal
- [x] Edit appointment modal
- [x] Change appointment status
- [x] Filter by branch
- [x] Search appointments

#### ✅ Reception Page (Tiếp nhận)
- [x] Reception check-in
- [x] Customer selection modal
- [x] Status tracking (Chờ khám, Đang khám, etc.)
- [x] Quick actions

#### ✅ Treatments Page (Điều trị)
- [x] Treatment list
- [x] Treatment status tracking
- [x] Search and filter

#### ✅ Reports Page (Báo cáo)
- [x] Revenue report
- [x] Overview report
- [x] Date range filters

#### ✅ Locations/Branches Page (Chi nhánh)
- [x] Branch listing
- [x] Branch selection

#### ✅ Inventory Page (Kho)
- [x] Backend API: /api/stock-pickings, /api/stock-moves
- [x] Frontend: loadInventory() function
- [x] HTML page with inventory tabs

#### ✅ HR/Salary Page (Nhân sự)
- [x] Backend API: /api/employees
- [x] Frontend: loadSalary() function
- [x] Employee list with pagination
- [x] Filter by branch

#### ✅ Finance/Cashbook Page (Kế toán)
- [x] Backend API: /api/payments
- [x] Frontend: loadCashbook() function
- [x] Payment list with filters

#### ✅ Settings Page (Cài đặt)
- [x] Backend API: /api/settings (GET/PUT)
- [x] Backend API: /api/export/customers, /api/export/appointments
- [x] Frontend: loadSettings() function with dynamic settings
- [x] Excel/CSV export buttons
- [x] Save settings functionality

#### ✅ Logout
- [x] Backend: POST /api/auth/logout
- [x] Frontend: logout button in header

### 2.2 ALL PAGES IMPLEMENTED ✅

---

## PHASE 3: QUALITY ASSURANCE (To Do)
async def create_stock_picking(data: dict):
    # Implement: Validate data, create record, return success
    pass

# 4. PUT /api/stock-pickings/{id} (update transfer)
@app.put("/stock-pickings/{picking_id}")
async def update_stock_picking(picking_id: str, data: dict):
    # Implement: Update picking status, validate quantities
    pass

# 5. GET /api/inventory/analytics (inventory stats)
@app.get("/inventory/analytics")
async def get_inventory_analytics(company_id: str = Query("")):
    # Implement: Total products, low stock alerts, movements
    pass

# 6. GET /api/inventory/products (product stock levels)
@app.get("/inventory/products")
async def get_product_stock_levels(
    company_id: str = Query(""),
    low_stock: bool = Query(False)
):
    # Implement: List products with current stock
    pass
```

**Frontend Tasks:**
```javascript
// File: static/tdental.html - Add inventory page

// 1. Add sidebar navigation for Inventory
case 'inventory':
    showPage('inventory');
    loadInventory();
    break;

// 2. Create inventory HTML section
// - Stock levels table
// - Stock movements list
// - Transfer creation form
// - Low stock alerts
// - Search and filter

// 3. Add JavaScript functions
function loadInventory() { /* Fetch from /api/inventory/analytics */ }
function loadStockMovements() { /* Fetch from /api/stock-moves */ }
function createStockPicking() { /* POST to /api/stock-pickings */ }
function filterInventory() { /* Filter by category, branch */ }
```

---

#### ❌ HR Page (Nhân sự) - HIGH PRIORITY
**Estimated Time: 8-12 hours**

**Backend Tasks:**
```python
# File: app/api/routes.py - Add endpoints

# 1. GET /api/employees (enhanced)
@app.get("/employees")
async def get_employees(
    company_id: str = Query(""),
    department: str = Query(""),
    search: str = Query("")
):
    # Return: All employees with department, position, status
    pass

# 2. GET /api/employees/{id} (employee detail)
@app.get("/employees/{employee_id}")
async def get_employee_detail(employee_id: str = Path(...)):
    # Return: Full employee profile, work history, schedule
    pass

# 3. POST /api/employees (create employee)
@app.post("/employees")
async def create_employee(data: dict, authorization: str = Header(None)):
    # Require: admin role
    pass

# 4. PUT /api/employees/{id} (update employee)
@app.put("/employees/{employee_id}")
async def update_employee(employee_id: str, data: dict):
    pass

# 5. DELETE /api/employees/{id} (deactivate)
@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    # Soft delete - set active = false

# 6. GET /api/departments (list departments)
@app.get("/departments")
async def get_departments(company_id: str = Query("")):
    pass

# 7. GET /api/positions (job positions)
@app.get("/positions")
async def get_positions():
    pass

# 8. GET /api/work-schedules (employee schedules)
@app.get("/work-schedules")
async def get_work_schedules(
    employee_id: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query("")
):
    pass
```

**Frontend Tasks:**
```javascript
// File: static/tdental.html - Add HR page

// 1. Add sidebar navigation
case 'hr':
    showPage('hr');
    loadEmployees();
    break;

// 2. Create HR HTML section
// - Employee list with photo, name, position, department
// - Employee detail modal
// - Add employee form
// - Department filter
// - Position filter
// - Work schedule view
// - Attendance tracking

// 3. Add JavaScript functions
function loadEmployees() { /* Fetch from /api/employees */ }
function loadDepartments() { /* Fetch from /api/departments */ }
function showEmployeeDetail(id) { /* Show modal with employee info */ }
function createEmployee() { /* POST to /api/employees */ }
function updateEmployee() { /* PUT to /api/employees/{id} */ }
```

---

#### ❌ Finance Page (Kế toán) - HIGH PRIORITY
**Estimated Time: 8-12 hours**

**Backend Tasks:**
```python
# File: app/api/routes.py - Add endpoints

# 1. GET /api/payments (all payments)
@app.get("/payments")
async def get_payments(
    company_id: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
    payment_method: str = Query("")
):
    pass

# 2. GET /api/payments/{id} (payment detail)
@app.get("/payments/{payment_id}")
async def get_payment_detail(payment_id: str = Path(...)):
    pass

# 3. POST /api/payments (create payment)
@app.post("/payments")
async def create_payment(data: dict):
    pass

# 4. GET /api/account-reports (accounting reports)
@app.get("/account-reports/balance")
async def get_balance_report(
    company_id: str = Query(""),
    date: str = Query("")
):
    # Return: Balance sheet, receivables, payables
    pass

# 5. GET /api/account-reports/profit-loss
@app.get("/account-reports/profit-loss")
async def get_profit_loss_report(
    company_id: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query("")
):
    pass

# 6. GET /api/invoices (customer invoices)
@app.get("/invoices")
async def get_invoices(
    customer_id: str = Query(""),
    status: str = Query("")
):
    pass

# 7. POST /api/invoices (create invoice)
@app.post("/invoices")
async def create_invoice(data: dict):
    pass
```

**Frontend Tasks:**
```javascript
// File: static/tdental.html - Add Finance page

// 1. Add sidebar navigation
case 'finance':
    showPage('finance');
    loadFinanceData();
    break;

// 2. Create Finance HTML section
// - Payment list with method, amount, date
// - Invoice management
// - Balance report
// - Profit/Loss report
// - Receivables tracking
// - Payment creation form

// 3. Add JavaScript functions
function loadFinanceData() { /* Fetch payments, invoices */ }
function loadBalanceReport() { /* Fetch from /api/account-reports/balance */ }
function createInvoice() { /* POST to /api/invoices */ }
```

---

#### ❌ Settings Page (Cài đặt) - MEDIUM PRIORITY
**Estimated Time: 4-6 hours**

**Backend Tasks:**
```python
# File: app/api/routes.py

# 1. GET /api/settings (get all settings)
@app.get("/settings")
async def get_settings(authorization: str = Header(None)):
    # Return: All application settings
    pass

# 2. PUT /api/settings (update settings)
@app.put("/settings")
async def update_settings(data: dict, authorization: str = Header(None)):
    # Require: admin role
    pass

# 3. GET /api/settings/company (company info)
@app.get("/settings/company")
async def get_company_settings(company_id: str = Query("")):
    pass

# 4. PUT /api/settings/company (update company)
@app.put("/settings/company/{company_id}")
async def update_company_settings(company_id: str, data: dict):
    pass
```

**Frontend Tasks:**
```javascript
// File: static/tdental.html - Add Settings page

// 1. Add sidebar navigation
case 'settings':
    showPage('settings');
    loadSettings();
    break;

// 2. Create Settings HTML section
// - Company information
// - Branch settings
// - User preferences
// - Notification settings

// 3. Add JavaScript functions
function loadSettings() { /* Fetch from /api/settings */ }
function saveSettings() { /* PUT to /api/settings */ }
```

---

#### ❌ Chat Widget - MEDIUM PRIORITY
**Estimated Time: 6-8 hours**

**Backend Tasks:**
```python
# File: app/api/routes.py

# 1. WebSocket for real-time chat
# 2. Message storage in database
# 3. User online/offline status

# Database table for chat
"""
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY,
    sender_id UUID,
    recipient_id UUID,
    message TEXT,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
```

**Frontend Tasks:**
```javascript
// File: static/tdental.html - Enhance Chat Widget

// 1. Replace alert with actual chat UI
// 2. Message input
// 3. Conversation list
// 4. Real-time updates via polling or WebSocket
```

---

#### ❌ Excel Export - MEDIUM PRIORITY
**Estimated Time: 4-6 hours**

**Backend Tasks:**
```python
# File: app/api/routes.py

# 1. GET /api/export/customers (export to Excel)
@app.get("/export/customers")
async def export_customers(
    company_id: str = Query(""),
    status: str = Query("")
):
    # Return: Excel file with customer data
    pass

# 2. GET /api/export/appointments
@app.get("/export/appointments")
async def export_appointments(
    date_from: str = Query(""),
    date_to: str = Query("")
):
    pass

# 3. GET /api/export/invoices
@app.get("/export/invoices")
async def export_invoices(...):
    pass
```

**Frontend Tasks:**
```javascript
// Replace alert with actual export functionality

function exportToExcel(type) {
    window.location.href = `/api/export/${type}?token=${getToken()}`;
}
```

---

## PHASE 3: QUALITY ASSURANCE (To Do)

### 3.1 Unit Tests (8-10 hours)
```python
# File: scraper-web/tests/

# test_auth.py
def test_login_success():
    # Test successful login
    pass

def test_login_invalid_credentials():
    # Test wrong password
    pass

def test_session_validation():
    # Test token validation
    pass

# test_customers.py
def test_create_customer():
    pass

def test_update_customer():
    pass

def test_delete_customer():
    pass

def test_customer_search():
    pass

# test_appointments.py
def test_create_appointment():
    pass

def test_update_appointment_status():
    pass

# test_database.py
def test_database_connection():
    pass

def test_pagination():
    pass
```

### 3.2 Integration Tests
- Test full user flow (login → view customers → create appointment)
- Test error handling across all endpoints

### 3.3 Performance Tests
- Load test with 100+ concurrent users
- Database query optimization

---

## PHASE 4: DEPLOYMENT & OPTIMIZATION (To Do)

### 4.1 Bug Fixes
- [ ] Add logout endpoint
- [ ] Fix broad exception handling
- [ ] Add proper loading states
- [ ] Improve error messages

### 4.2 Security
- [ ] Add rate limiting
- [ ] Add input validation (use Pydantic models)
- [ ] Add audit logging

### 4.3 Performance
- [ ] Add database connection pooling
- [ ] Add caching for frequently accessed data
- [ ] Optimize slow queries

### 4.4 Documentation
- [ ] Update API documentation
- [ ] Add user manual
- [ ] Add deployment guide

---

## TASK PRIORITY MATRIX

| Priority | Task | Hours | Dependencies |
|----------|------|-------|--------------|
| P0 | Inventory Backend | 4 | None |
| P0 | Inventory Frontend | 8 | Inventory Backend |
| P1 | HR Backend | 4 | None |
| P1 | HR Frontend | 8 | HR Backend |
| P1 | Finance Backend | 4 | None |
| P1 | Finance Frontend | 8 | Finance Backend |
| P2 | Settings | 6 | None |
| P2 | Excel Export | 5 | Finance Backend |
| P2 | Chat Widget | 8 | WebSocket setup |
| P3 | Unit Tests | 10 | All features |
| P3 | Bug Fixes | 5 | Testing |
| P3 | Performance | 8 | Production load |

---

## ESTIMATED TOTAL TIME TO 100%

| Phase | Hours |
|-------|-------|
| Phase 1: Infrastructure | ✅ Complete |
| Phase 2: Frontend Pages | ~50 hours |
| Phase 3: Testing | ~18 hours |
| Phase 4: Deployment | ~27 hours |
| **TOTAL** | **~95 hours** |

---

## QUICK START - WHAT TO DO NEXT

1. **Start with Inventory page** - It's the most similar to existing code
2. **Copy the pattern** from Customers/Appointments pages
3. **Test incrementally** - Verify each feature works before moving on
4. **Use the comparison tool** at `/compare.html` to match TDental's look

---

**Document Version**: 1.0
**Last Updated**: 2026-02-26
**Status**: Active Development