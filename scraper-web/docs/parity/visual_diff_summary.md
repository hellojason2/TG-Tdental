# Visual Parity Analysis - TDental Local vs Live

**Date:** 2026-02-27
**Status:** COMPLETE - Local server screenshots captured

---

## Captured Screenshots

| Route | Local | Live |
|-------|-------|------|
| Dashboard (#/dashboard) | `local_dashboard.png` | `live_dashboard.png` |
| Customers (#/partners/customers) | `local_customers.png` | `live_customers.png` |
| Calendar (#/calendar) | `local_calendar.png` | `live_calendar.png` |
| Reception (#/work) | `local_reception.png` | `live_work.png` |
| Treatments/Labo (#/treatments) | `local_treatments.png` | NOT CAPTURED |
| Reports (#/reports) | `local_reports.png` | NOT CAPTURED |

---

## Visual Differences Found

### 1. Dashboard (#/dashboard)

| Aspect | Live (TDental.vn) | Local (localhost:8899) |
|--------|-----------------|----------------------|
| **Status Badge Colors** | Orange/amber for "Chờ khám", Blue for "Đang khám", Green for "Hoàn thành" | Light blue for "Chờ khám", Green for "Đang khám", Green for "Hoàn thành" |
| **Patient Avatars** | Round circle with person silhouette icon | Similar but slightly different styling |
| **Header Bar** | Dark blue (#1A6DE3 approx) | Same dark blue |
| **DOANH THU Section** | Shows same values: Tổng doanh thu: 193.414.180.714, Tiền mặt: 94.050.553.504, Ngân hàng: 99.361.627.210, Khác: 2.000.000 | Identical values |
| **Layout** | Three panels: TIẾP NHẬN KHÁCH HÀNG (left), DỊCH VỤ TRONG NGÀY (center), LỊCH HẸN HÔM NAY + DOANH THU (right) | Same layout |

**Difference Summary:** Badge colors differ slightly - Local uses more muted colors while Live uses vibrant colors.

---

### 2. Customers (#/partners/customers)

| Aspect | Live (TDental.vn) | Local (localhost:8899) |
|--------|-----------------|----------------------|
| **Header** | "Khách hàng" with "Thêm mới" button | Identical |
| **Filter Buttons** | "Tất cả", "Đang điều trị", "Hoàn thành", "Chưa phát sinh" | Identical |
| **Branch Filter** | Dropdown with branch options | Identical |
| **Table Columns** | 15 columns: #, Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Công nợ, Tổng tiền ĐT, Tổng doanh thu, Dự kiến thu, Thẻ thành viên, Nhãn, Chi nhánh, Thao tác | Identical |
| **Customer Cards** | Avatar, Name + ID, Status badges | Same styling |

**Difference Summary:** Nearly identical - no significant visual differences observed.

---

### 3. Calendar (#/calendar)

| Aspect | Live (TDental.vn) | Local (localhost:8899) |
|--------|-----------------|----------------------|
| **View** | Full calendar grid with month view | Different content - shows appointment list |
| **Time Slots** | 6:00 - 23:00 visible | Different layout |
| **Navigation** | Month navigation with arrows | Different - shows list view |
| **Day Filters** | "Tất cả", "Sáng", "Chiều", "Tối" | Not present in local version |

**Difference Summary:** MAJOR DIFFERENCE - Local shows appointment list instead of calendar grid view.

---

### 4. Reception / Tiếp nhận (#/work)

| Aspect | Live (TDental.vn) | Local (localhost:8899) |
|--------|-----------------|----------------------|
| **Title** | "Lịch sử khám bệnh" | "Tiếp nhận" |
| **Stats Display** | Patient cards with avatar, name, date, doctor, branch | "Chờ khám: 22.524", "Đang điều trị: 0", "Hoàn thành: 185.288", "Đã thanh toán: 0" |
| **Status Badge Colors** | "Đã đến" = green, "Hủy" = red, "Chờ khám" = yellow | Shows "confirmed" = blue |
| **Layout** | Card-based list with patient details | Table-based layout |
| **Filter Buttons** | "Tất cả", "Chờ khám", "Xác nhận", "Đang khám", "Hoàn thành", "Hủy" | Identical |
| **Table Columns** | Not a table (card view) | Table with #, Khách hàng, SĐT, Bác sĩ, Chi nhánh, Ngày hẹn, Ghi chú, Trạng thái |
| **Services Section** | Shows "Dịch vụ" with treatment details | Not present |

**Difference Summary:** Major structural difference - Live shows card-based patient history, Local shows table-based reception list.

---

### 5. Treatments/Labo (#/treatments)

| Aspect | Live | Local (localhost:8899) |
|--------|------|----------------------|
| **Status** | Not captured | Shows fallback content: "Danh sách phiếu Labo" with "Quản lý phiếu Labo" and "Đơn hàng Labo" tabs |
| **Data** | N/A | API error - using fallback static content |

**Difference Summary:** Local shows fallback content due to API error.

---

### 6. Reports (#/reports)

| Aspect | Live | Local (localhost:8899) |
|--------|------|----------------------|
| **Status** | Not captured | Shows sidebar with report options: "Doanh thu", "Dịch vụ", "Khách hàng", "Nhân viên", "Công nợ" |
| **Content** | N/A | Main content area shows report placeholder |

**Difference Summary:** Local shows basic report sidebar structure.

---

## Summary of Key Differences

### High Priority (User-Facing):
1. **Calendar View**: Local shows list view instead of calendar grid
2. **Reception Page**: Local shows table view instead of card-based patient history
3. **Status Badge Colors**: Slight color variations between Live and Local

### Medium Priority:
1. **Treatments/Labo**: API errors result in fallback content on Local

### Low Priority:
1. Minor styling differences in avatars and buttons
2. Slightly different shade of green for "Hoàn thành" badge

---

## Files Saved

### Live Screenshots:
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/live_dashboard.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/live_customers.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/live_calendar.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/live_work.png`

### Local Screenshots:
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/local_dashboard.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/local_customers.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/local_calendar.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/local_reception.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/local_treatments.png`
- `/Users/thuanle/Documents/TamTMV/Tdental/scraper-web/docs/parity/visual_capture/local_reports.png`

---

## Next Steps

1. **Fix Calendar view** - Implement full calendar grid (currently shows list)
2. **Fix Reception view** - Convert table to card-based patient history
3. **Match badge colors** - Update CSS to match Live color scheme:
   - "Chờ khám": Should be orange/amber (#F59E0B)
   - "Đang khám": Should be blue (#3B82F6)
   - "Hoàn thành": Keep green (#10B981)
4. **Fix Treatments API** - Resolve API errors for Labo page
5. **Implement Reports** - Build out report pages with actual data
