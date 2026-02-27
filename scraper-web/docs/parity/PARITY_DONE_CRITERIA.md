# TDental Parity Done Criteria

## Per-Route Acceptance Criteria

This document defines the exact criteria that must be met for each route to be considered "parity complete."

---

## Login Page (`/login`)

### Layout (Required)
- [ ] Centered login card on page
- [ ] Logo at top of card
- [ ] Email input field visible
- [ ] Password input field visible
- [ ] Login button at bottom
- [ ] Card width: ~400px

### Typography (Required)
- [ ] Font family matches live (system fonts acceptable)
- [ ] Input labels above inputs
- [ ] Button text: "Đăng nhập" or "Đăng nhập / Login"

### Interactions (Required)
- [ ] Email validation (required, email format)
- [ ] Password required validation
- [ ] Loading state on submit
- [ ] Error message display on failed login
- [ ] Redirect to dashboard on success

### Visual (Required)
- [ ] Input focus state visible (border color change)
- [ ] Button hover state visible
- [ ] Error state shows red border/text

---

## Dashboard (`#dashboard`)

### Layout (Required)
- [ ] Tab bar present (Doanh thu, Lịch hẹn, Khách hàng, Kho)
- [ ] Metrics cards row (4 cards minimum)
- [ ] Content area below tabs
- [ ] Sidebar visible on left
- [ ] Topbar visible on top

### Typography (Required)
- [ ] Tab labels match live exactly
- [ ] Card titles readable
- [ ] Numbers prominent in metrics

### Interactions (Required)
- [ ] Tab switching works
- [ ] Sidebar navigation works
- [ ] Clicking cards navigates to detail views

### Visual (Required)
- [ ] Active tab visually distinct
- [ ] Card hover states work
- [ ] Icons visible in cards

---

## Customers (`#customers`)

### Layout (Required)
- [ ] Toolbar with action buttons (Thêm mới, Xuất Excel)
- [ ] Tab bar (Tất cả, Tiềm năng, Chính thức)
- [ ] Search/filter bar
- [ ] Data table with columns
- [ ] Pagination at bottom

### Table Columns (Required)
- [ ] STT (#)
- [ ] Tên khách hàng (Customer name)
- [ ] Số điện thoại (Phone)
- [ ] Nguồn (Source)
- [ ] Trạng thái (State)
- [ ] Ngày tạo (Created date)
- [ ] Thao tác (Actions)

### Interactions (Required)
- [ ] Add new customer modal opens
- [ ] Edit customer works
- [ ] Delete customer with confirmation
- [ ] Search filters results
- [ ] Tab switching filters data
- [ ] Pagination works

### Visual (Required)
- [ ] Table row hover highlight
- [ ] Status badges colored correctly
- [ ] Action icons visible
- [ ] Empty state message when no data

---

## Reception (`#reception`)

### Layout (Required)
- [ ] Queue display area
- [ ] Status counters (Chờ, Đang khám, Hoàn thành, Cancel)
- [ ] Refresh button
- [ ] Add new button

### Interactions (Required)
- [ ] Clicking patient opens detail
- [ ] Status change works
- [ ] Queue refreshes data

### Visual (Required)
- [ ] Cards for each patient
- [ ] Status indicators colored
- [ ] Time displayed correctly

---

## Calendar (`#calendar`)

### Layout (Required)
- [ ] Date navigation (prev/next, today)
- [ ] View toggle (list/calendar)
- [ ] Status filter buttons
- [ ] Appointments list/grid
- [ ] Add appointment button

### Interactions (Required)
- [ ] Date navigation works
- [ ] Filter by status works
- [ ] Click appointment shows detail
- [ ] Create appointment modal works
- [ ] Edit appointment works

### Visual (Required)
- [ ] Current day highlighted
- [ ] Status colors match badges
- [ ] Time slots displayed
- [ ] Doctor assigned shown

---

## Treatments (`#treatments`)

### Layout (Required)
- [ ] Tab bar (Tất cả, Đang điều trị, Hoàn thành, Hủy)
- [ ] Data table
- [ ] Pagination

### Table Columns (Required)
- [ ] STT
- [ ] Tên khách hàng
- [ ] Ngày bắt đầu
- [ ] Bác sĩ
- [ ] Trạng thái
- [ ] Thao tác

### Interactions (Required)
- [ ] Tab filtering works
- [ ] View detail works
- [ ] Edit treatment works

### Visual (Required)
- [ ] Status badges colored
- [ ] Row hover highlight
- [ ] Empty state handled

---

## Sale Orders (`#purchase`)

### Layout (Required)
- [ ] Tab bar (Tất cả, Chờ xác nhận, Đang xử lý, Hoàn thành, Hủy)
- [ ] Data table
- [ ] Totals row
- [ ] Filter bar

### Table Columns (Required)
- [ ] STT
- [ ] Mã đơn
- [ ] Khách hàng
- [ ] Ngày
- [ ] Tổng tiền
- [ ] Trạng thái
- [ ] Thao tác

### Visual (Required)
- [ ] Money formatted correctly (VND)
- [ ] Status badges colored
- [ ] Totals calculate correctly

---

## Inventory (`#inventory`)

### Layout (Required)
- [ ] Summary cards (Tổng kho, Kho nhập, Kho xuất)
- [ ] Tab bar (Tất cả, Nhập kho, Xuất kho)
- [ ] Data table
- [ ] Filter bar

### Interactions (Required)
- [ ] Tab filtering works
- [ ] View details works

### Visual (Required)
- [ ] Summary numbers display
- [ ] In/out indicators colored

---

## HR (`#salary`)

### Layout (Required)
- [ ] Employee table
- [ ] Search box
- [ ] Pagination

### Table Columns (Required)
- [ ] STT
- [ ] Tên nhân viên
- [ ] Chức vụ
- [ ] Số điện thoại
- [ ] Trạng thái

---

## Accounting (`#cashbook`)

### Layout (Required)
- [ ] Date filter
- [ ] Payment table
- [ ] Amount totals

### Table Columns (Required)
- [ ] STT
- [ ] Ngày
- [ ] Loại (Thu/Chi)
- [ ] Số tiền
- [ ] Mô tả
- [ ] Trạng thái

### Visual (Required)
- [ ] Money formatted with VND
- [ ] Thu (income) and Chi (expense) colored differently

---

## Global Shell (All Routes)

### Sidebar
- [ ] Width matches live (or within 10px)
- [ ] Logo visible
- [ ] Menu items list correct
- [ ] Active item highlighted
- [ ] Hover states work
- [ ] Collapse/expand works
- [ ] Submenu items appear on click

### Topbar
- [ ] Search box visible
- [ ] Branch selector visible
- [ ] Bell icon with count
- [ ] User avatar/name
- [ ] Logout option

### Global
- [ ] No console errors on any route
- [ ] Loading states display correctly
- [ ] Error handling shows user-friendly messages

---

## Testing Protocol

### Pre-Flight Checklist
1. [ ] Login works with admin credentials
2. [ ] All routes accessible from sidebar
3. [ ] No 404 or 500 errors
4. [ ] No JavaScript console errors
5. [ ] Data loads in all tables

### Per-Route Testing Steps
1. Navigate to route via sidebar
2. Verify page title/heading matches
3. Check all expected widgets present
4. Test at least one interaction (click, filter, etc.)
5. Verify no console errors
6. Take screenshot for baseline

### Sign-Off Requirements
- [ ] All CRITICAL issues resolved
- [ ] HIGH issues below threshold
- [ ] Screenshots captured for each route
- [ ] Test report generated
- [ ] Reviewer approves
