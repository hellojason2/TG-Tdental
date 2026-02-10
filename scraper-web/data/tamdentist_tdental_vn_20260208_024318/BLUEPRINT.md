# Replication Blueprint
## Source: https://tamdentist.tdental.vn

## Tech Stack Recommendation
- **Frontend:** React + TypeScript + Ant Design (or Element UI if Vue detected)
- **Backend:** Node.js + Express (or FastAPI/Python)
- **Database:** PostgreSQL
- **Auth:** JWT-based (tokens found in localStorage)
- **Framework detected:** Angular

## Architecture Overview

### Routes (31)
- `#/calendar` → `CalendarPage`
- `#/dashboard` → `DashboardPage`
- `#/partners` → `PartnersPage`
- `#/partners/customers/2089438f-145c-4deb-84da-b3eb00830d52` → `PartnersCustomers2089438f-145c-4deb-84da-b3eb00830d52Page`
- `#/partners/customers/37216657-1f19-4902-ac02-b3eb007ce83b` → `PartnersCustomers37216657-1f19-4902-ac02-b3eb007ce83bPage`
- `#/partners/customers/3e0fea46-4def-4687-83d9-b3eb006d738d` → `PartnersCustomers3e0fea46-4def-4687-83d9-b3eb006d738dPage`
- `#/partners/customers/3fa541db-c40c-446a-a2ea-b3eb0080c1a6` → `PartnersCustomers3fa541db-c40c-446a-a2ea-b3eb0080c1a6Page`
- `#/partners/customers/46ddb0db-285a-499b-947f-b3eb007a4552` → `PartnersCustomers46ddb0db-285a-499b-947f-b3eb007a4552Page`
- `#/partners/customers/59f96fda-78c5-43a7-af56-b3eb006b103e` → `PartnersCustomers59f96fda-78c5-43a7-af56-b3eb006b103ePage`
- `#/partners/customers/5f24540c-383d-477a-b071-b3eb0065fb8a` → `PartnersCustomers5f24540c-383d-477a-b071-b3eb0065fb8aPage`
- `#/partners/customers/69348a0e-9aea-40e3-8727-b3eb00676a7e` → `PartnersCustomers69348a0e-9aea-40e3-8727-b3eb00676a7ePage`
- `#/partners/customers/7d47407f-767d-42f7-a3e0-b3eb008993f1` → `PartnersCustomers7d47407f-767d-42f7-a3e0-b3eb008993f1Page`
- `#/partners/customers/7ea111f8-bcf8-4e8e-9546-b3eb007caeac` → `PartnersCustomers7ea111f8-bcf8-4e8e-9546-b3eb007caeacPage`
- `#/partners/customers/91b97472-1e7d-4ef8-9568-b3eb006a8f81` → `PartnersCustomers91b97472-1e7d-4ef8-9568-b3eb006a8f81Page`
- `#/partners/customers/9bf56248-d668-404f-b3e3-b3eb0087ca22` → `PartnersCustomers9bf56248-d668-404f-b3e3-b3eb0087ca22Page`
- `#/partners/customers/9cf704e1-cf5c-4c52-89f7-b3eb006abf75` → `PartnersCustomers9cf704e1-cf5c-4c52-89f7-b3eb006abf75Page`
- `#/partners/customers/9e0aa846-ca45-4b67-8fa2-b3eb0069d801` → `PartnersCustomers9e0aa846-ca45-4b67-8fa2-b3eb0069d801Page`
- `#/partners/customers/a58e8fb1-2841-427f-aa1d-b3eb006f7dd6` → `PartnersCustomersA58e8fb1-2841-427f-aa1d-b3eb006f7dd6Page`
- `#/partners/customers/c0970d96-19c7-4620-b5dd-b3eb006b6487` → `PartnersCustomersC0970d96-19c7-4620-b5dd-b3eb006b6487Page`
- `#/partners/customers/c9c0af9f-55ed-41ad-92e9-b3eb00696473` → `PartnersCustomersC9c0af9f-55ed-41ad-92e9-b3eb00696473Page`
- `#/partners/customers/e4e2b1d6-ed74-42af-9f7a-b3eb0068c105` → `PartnersCustomersE4e2b1d6-ed74-42af-9f7a-b3eb0068c105Page`
- `#/partners/customers/edfd71b4-80ac-4b6d-bf85-b3eb0063f690` → `PartnersCustomersEdfd71b4-80ac-4b6d-bf85-b3eb0063f690Page`
- `#/partners/customers/f6a84d2d-02d1-41f7-b6f8-b3eb00651333` → `PartnersCustomersF6a84d2d-02d1-41f7-b6f8-b3eb00651333Page`
- `#/warehouse` → `WarehousePage`
- `#/warehouse/check` → `WarehouseCheckPage`
- `#/warehouse/export` → `WarehouseExportPage`
- `#/warehouse/import` → `WarehouseImportPage`
- `#/warehouse/import-export-inventory` → `WarehouseImport-export-inventoryPage`
- `#/warehouse/in-out-history` → `WarehouseIn-out-historyPage`
- `#/warehouse/request-product` → `WarehouseRequest-productPage`
- `#/work` → `WorkPage`

### API Endpoints (23)
- `GET /Web/Session/GetSessionInfo` (called 2x)
- `GET /api/ApplicationUsers` (called 2x)
- `GET /api/Appointments` (called 3x)
- `GET /api/CardTypes` (called 1x)
- `GET /api/Companies` (called 1x)
- `GET /api/CrmTaskCategories` (called 1x)
- `GET /api/CrmTasks/CountTasksByType` (called 1x)
- `GET /api/CrmTasks/GetPagedV2` (called 1x)
- `GET /api/CustomerReceipts` (called 2x)
- `GET /api/Employees` (called 4x)
- `GET /api/IrConfigParameters/GetParam` (called 1x)
- `GET /api/Partners/GetPagedPartnersCustomer` (called 1x)
- `GET /api/SaleOrderLines` (called 2x)
- `GET /api/productcategories` (called 1x)
- `GET /mail/inbox/messages` (called 1x)
- `GET /mail/init_messaging` (called 1x)
- `GET /mail/load_message_failures` (called 1x)
- `POST /api/Account/Login` (called 1x)
- `POST /api/DashboardReports/GetSumary` (called 2x)
- `POST /api/PartnerSources/Autocomplete` (called 1x)
- `POST /api/Partnercategories/Autocomplete` (called 2x)
- `POST /api/StockReports/GetExportImportInventoryReport` (called 1x)
- `POST /api/products/autocomplete2` (called 1x)

### Database Tables (10)
- `Session`: id, name, userName, userPartnerId, partnerId, userCompanies, expirationDate, isAdmin...
- `IrConfigParameters`: value
- `mail`: needactionInboxCount
- `Autocomplete`: id, name, completeName, color, type, isCollaborators, isActive
- `Companies`: id, name, logo, active, isHead, periodLockDate, medicalFacilityCode, hotline...
- `productcategories`: id, name, completeName, parentId, parent
- `autocomplete2`: id, name, nameNoSign, defaultCode, priceUnit, purchasePrice, standardPrice, categId...
- `GetPagedPartnersCustomer`: id, ref, avatar, displayName, name, phone, email, street...
- `CountTasksByType`: stage, total
- `ApplicationUsers`: id, name, userName, partnerId, active, phoneNumber, jobId, jobName...

### Frontend Pages
- `#/calendar`: 📊 Table
  - Table columns: , Không xác định
- `#/dashboard`: 📊 Table | 📑 Tabs
  - Table columns: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
- `#/partners`: 📊 Table
  - Table columns: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị
- `#/warehouse`: 📊 Table
  - Table columns: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng
- `#/work`: 📊 Table | 📑 Tabs
  - Table columns: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo

## Implementation Order
1. **Database:** Create tables from `database_schema.sql`
2. **Backend API:** Implement endpoints from `api_specification.json`
3. **Auth:** JWT login/logout based on captured auth flow
4. **Layout:** Sidebar + topbar + breadcrumbs shell
5. **CRUD Pages:** Implement each route with its forms/tables
6. **Advanced Features:** Modals, tabs, filters, search

## Files Generated
- `full_report.json` - Complete scrape data
- `database_schema.sql` - PostgreSQL schema
- `api_specification.json` - API endpoint specs
- `component_tree.json` - Frontend component hierarchy
- `screenshots/` - Visual reference for each page
- `api_responses/` - Sample API response data
- `dom_snapshots/` - HTML snapshots per route
