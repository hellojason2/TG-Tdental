# SPA Scraping Report: https://tamdentist.tdental.vn
**Scraped at:** 2026-02-08T02:43:43.556544

## Overview
| Metric | Count |
|--------|-------|
| Routes Discovered | 31 |
| Routes Visited | 5 |
| API Calls Captured | 34 |
| Unique API Endpoints | 23 |
| Forms Found | 0 |
| Tables Found | 479 |

## Discovered Routes
- `#/calendar`
- `#/dashboard`
- `#/partners`
- `#/partners/customers/2089438f-145c-4deb-84da-b3eb00830d52`
- `#/partners/customers/37216657-1f19-4902-ac02-b3eb007ce83b`
- `#/partners/customers/3e0fea46-4def-4687-83d9-b3eb006d738d`
- `#/partners/customers/3fa541db-c40c-446a-a2ea-b3eb0080c1a6`
- `#/partners/customers/46ddb0db-285a-499b-947f-b3eb007a4552`
- `#/partners/customers/59f96fda-78c5-43a7-af56-b3eb006b103e`
- `#/partners/customers/5f24540c-383d-477a-b071-b3eb0065fb8a`
- `#/partners/customers/69348a0e-9aea-40e3-8727-b3eb00676a7e`
- `#/partners/customers/7d47407f-767d-42f7-a3e0-b3eb008993f1`
- `#/partners/customers/7ea111f8-bcf8-4e8e-9546-b3eb007caeac`
- `#/partners/customers/91b97472-1e7d-4ef8-9568-b3eb006a8f81`
- `#/partners/customers/9bf56248-d668-404f-b3e3-b3eb0087ca22`
- `#/partners/customers/9cf704e1-cf5c-4c52-89f7-b3eb006abf75`
- `#/partners/customers/9e0aa846-ca45-4b67-8fa2-b3eb0069d801`
- `#/partners/customers/a58e8fb1-2841-427f-aa1d-b3eb006f7dd6`
- `#/partners/customers/c0970d96-19c7-4620-b5dd-b3eb006b6487`
- `#/partners/customers/c9c0af9f-55ed-41ad-92e9-b3eb00696473`
- `#/partners/customers/e4e2b1d6-ed74-42af-9f7a-b3eb0068c105`
- `#/partners/customers/edfd71b4-80ac-4b6d-bf85-b3eb0063f690`
- `#/partners/customers/f6a84d2d-02d1-41f7-b6f8-b3eb00651333`
- `#/warehouse`
- `#/warehouse/check`
- `#/warehouse/export`
- `#/warehouse/import`
- `#/warehouse/import-export-inventory`
- `#/warehouse/in-out-history`
- `#/warehouse/request-product`
- `#/work`

## API Endpoints

### `GET /Web/Session/GetSessionInfo`
- Status codes: [200]
- Call count: 2

### `GET /api/ApplicationUsers`
- Status codes: [200]
- Call count: 2

### `GET /api/Appointments`
- Status codes: [200]
- Call count: 3

### `GET /api/CardTypes`
- Status codes: [200]
- Call count: 1

### `GET /api/Companies`
- Status codes: [200]
- Call count: 1

### `GET /api/CrmTaskCategories`
- Status codes: [200]
- Call count: 1

### `GET /api/CrmTasks/CountTasksByType`
- Status codes: [200]
- Call count: 1

### `GET /api/CrmTasks/GetPagedV2`
- Status codes: [200]
- Call count: 1

### `GET /api/CustomerReceipts`
- Status codes: [200]
- Call count: 2

### `GET /api/Employees`
- Status codes: [200]
- Call count: 4

### `GET /api/IrConfigParameters/GetParam`
- Status codes: [200]
- Call count: 1

### `GET /api/Partners/GetPagedPartnersCustomer`
- Status codes: [200]
- Call count: 1

### `GET /api/SaleOrderLines`
- Status codes: [200]
- Call count: 2

### `GET /api/productcategories`
- Status codes: [200]
- Call count: 1

### `GET /mail/inbox/messages`
- Status codes: [200]
- Call count: 1

### `GET /mail/init_messaging`
- Status codes: [200]
- Call count: 1

### `GET /mail/load_message_failures`
- Status codes: [200]
- Call count: 1

### `POST /api/Account/Login`
- Status codes: [200]
- Call count: 1
- Has request body: Yes

### `POST /api/DashboardReports/GetSumary`
- Status codes: [200]
- Call count: 2
- Has request body: Yes

### `POST /api/PartnerSources/Autocomplete`
- Status codes: [200]
- Call count: 1
- Has request body: Yes

### `POST /api/Partnercategories/Autocomplete`
- Status codes: [200]
- Call count: 2
- Has request body: Yes

### `POST /api/StockReports/GetExportImportInventoryReport`
- Status codes: [200]
- Call count: 1
- Has request body: Yes

### `POST /api/products/autocomplete2`
- Status codes: [200]
- Call count: 1
- Has request body: Yes

## Forms Found

## Inferred Database Schema

### Table: `Session`
Source: `GET /Web/Session/GetSessionInfo`

| Field | Type | Sample |
|-------|------|--------|
| id | str | ec0a8cd2-44b9-4501-987f-992eb2e94756 |
| name | str | dataconnect |
| userName | str | dataconnect |
| userPartnerId | str | 17ded27a-f066-475b-9ab9-b3e900ae6fc1 |
| partnerId | str | 17ded27a-f066-475b-9ab9-b3e900ae6fc1 |
| userCompanies | dict | {'currentCompany': {'id': 'dde8b85e-e35a-41fa-4a6b |
| expirationDate | str | 2026-09-19T10:43:29 |
| isAdmin | bool |  |
| permissions | list | ['Basic.Overview.Read', 'System.Company.Create', ' |
| groups | list | ['base.group_multi_company', 'base.group_user', 'b |
| rules | list |  |
| modules | list |  |
| settings | NoneType |  |
| expiredIn | int | 320820 |
| tenantId | str | tamdentist |
| isUppercasePartnerName | bool |  |
| features | list | [{'name': 'AccountMoveSequenceMixin', 'value': Tru |
| totpEnabled | bool |  |

### Table: `IrConfigParameters`
Source: `GET /api/IrConfigParameters/GetParam`

| Field | Type | Sample |
|-------|------|--------|
| value | str | Removed |

### Table: `mail`
Source: `GET /mail/init_messaging`

| Field | Type | Sample |
|-------|------|--------|
| needactionInboxCount | int |  |

### Table: `Autocomplete`
Source: `POST /api/Partnercategories/Autocomplete`

| Field | Type | Sample |
|-------|------|--------|
| id | uuid | 4c91d2d6-e689-4640-b859-b2f4009c4d2f |
| name | string | MKT |
| completeName | nullable |  |
| color | string | 7 |
| type | string | normal |
| isCollaborators | boolean |  |
| isActive | boolean | True |

### Table: `Companies`
Source: `GET /api/Companies`

| Field | Type | Sample |
|-------|------|--------|
| id | uuid | dde8b85e-e35a-41fa-4a6b-08de107d59ec |
| name | string | Nha khoa Tấm Dentist |
| logo | nullable |  |
| active | boolean | True |
| isHead | boolean |  |
| periodLockDate | nullable |  |
| medicalFacilityCode | nullable |  |
| hotline | string |  |
| phone | nullable |  |
| address | string |  |
| addressV2 | string |  |
| usedAddressV2 | boolean | True |
| taxCode | nullable |  |
| taxUnitName | nullable |  |
| taxUnitAddress | nullable |  |
| taxBankName | nullable |  |
| taxBankAccount | nullable |  |
| taxPhone | nullable |  |
| householdBusinesses | array/relation |  |

### Table: `productcategories`
Source: `GET /api/productcategories`

| Field | Type | Sample |
|-------|------|--------|
| id | uuid | bc794e7c-75cb-4e62-a1c5-b2e800760a4d |
| name | string | BỘC LỘ |
| completeName | string | BỘC LỘ |
| parentId | nullable |  |
| parent | nullable |  |

### Table: `autocomplete2`
Source: `POST /api/products/autocomplete2`

| Field | Type | Sample |
|-------|------|--------|
| id | uuid | c2f42776-fac3-4813-bb7a-b05b00a64ec1 |
| name | string | Niềng Mắc Cài Kim Loại Tiêu Chuẩn |
| nameNoSign | string | Niềng Mắc Cài Kim Loại Tiêu Chuẩn|Nieng Mac Cai Ki |
| defaultCode | string | DV0001 |
| priceUnit | nullable |  |
| purchasePrice | nullable |  |
| standardPrice | decimal |  |
| categId | uuid | cb4cb417-9778-4416-8d5a-afe30053b73c |
| categ | object/relation | {'id': 'cb4cb417-9778-4416-8d5a-afe30053b73c', 'na |
| type | string | service |
| type2 | string | service |
| listPrice | decimal | 28000000.0 |
| firm | nullable |  |
| laboPrice | nullable |  |
| uomId | uuid | f9284d91-daa3-4d12-b956-b05b00a64ec2 |
| uom | object/relation | {'id': 'f9284d91-daa3-4d12-b956-b05b00a64ec2', 'na |
| quantity | decimal |  |
| isLabo | boolean |  |
| displayName | string | [DV0001] Niềng Mắc Cài Kim Loại Tiêu Chuẩn |
| stepConfigs | nullable |  |
| taxId | nullable |  |
| tax | nullable |  |
| companyName | string | Tấm Dentist Thủ Đức |

### Table: `GetPagedPartnersCustomer`
Source: `GET /api/Partners/GetPagedPartnersCustomer`

| Field | Type | Sample |
|-------|------|--------|
| id | uuid | 7d47407f-767d-42f7-a3e0-b3eb008993f1 |
| ref | string | T059709 |
| avatar | nullable |  |
| displayName | nullable |  |
| name | string | Lương Thị Diệu Linh |
| phone | string | 0822961512 |
| email | nullable |  |
| street | nullable |  |
| cityName | nullable |  |
| districtName | nullable |  |
| wardName | nullable |  |
| cityNameV2 | nullable |  |
| wardNameV2 | nullable |  |
| birthYear | integer | 2006 |
| birthMonth | nullable |  |
| birthDay | nullable |  |
| orderState | string | none |
| orderResidual | decimal |  |
| totalDebit | decimal |  |
| amountTreatmentTotal | decimal |  |
| amountRevenueTotal | decimal |  |
| jobTitle | nullable |  |
| cardType | nullable |  |
| sourceId | uuid | 82fc6269-37a3-4702-8889-afe3007cf044 |
| sourceName | nullable |  |
| companyName | string | Tấm Dentist Thủ Đức |
| date | datetime | 2026-02-08T08:20:10.498 |
| companyId | uuid | b178d5ee-d9ac-477e-088e-08db9a4c4cf4 |
| appointmentDate | nullable |  |
| nextAppointmentDate | nullable |  |
| saleOrderDate | nullable |  |
| lastTreatmentCompleteDate | nullable |  |
| memberLevel | nullable |  |
| amountBalance | decimal |  |
| customerType | nullable |  |
| categories | array/relation |  |
| dateOfBirth | string | --/--/2006 |
| age | string | 20 |
| address | string |  |
| addressV2 | string |  |
| active | boolean | True |
| userId | nullable |  |
| saleName | nullable |  |
| gender | string | female |
| genderDisplay | string | Nữ |
| comment | nullable |  |
| treatmentStatus | string | none |
| usedAddressV2 | boolean | True |
| marketingStaffId | nullable |  |
| contactStatusId | nullable |  |
| potentialLevel | nullable |  |
| serviceInterests | nullable |  |
| marketingStaff | nullable |  |
| contactStatus | nullable |  |
| countryId | uuid | 1ab9c25c-c6ca-4c05-9042-b0670114aee9 |
| country | nullable |  |
| salePartnerId | nullable |  |
| customerStatus | nullable |  |
| unActiveBy | nullable |  |
| unActiveDate | nullable |  |
| unActiveReason | nullable |  |

### Table: `CountTasksByType`
Source: `GET /api/CrmTasks/CountTasksByType`

| Field | Type | Sample |
|-------|------|--------|
| stage | nullable |  |
| total | integer |  |

### Table: `ApplicationUsers`
Source: `GET /api/ApplicationUsers`

| Field | Type | Sample |
|-------|------|--------|
| id | uuid | b19424da-e016-41c8-b992-17181969c924 |
| name | string | Admin |
| userName | string | admin |
| partnerId | uuid | 733fd0dc-ec01-4933-8a94-afc7006cf360 |
| active | boolean | True |
| phoneNumber | nullable |  |
| jobId | nullable |  |
| jobName | nullable |  |
| ref | nullable |  |
| avatar | nullable |  |
| employees | array/relation |  |
| teamMembers | array/relation |  |

## Tables Found in UI

### Table on `#/calendar`
Headers: , Không xác định
Row count: 20

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/calendar`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 2

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 2

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 2

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 2

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 1

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 1

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 1

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 1

### Table on `#/dashboard`
Headers: Dịch vụ, Khách hàng, Số lượng, Bác sĩ, Thành tiền, Thanh toán, Còn lại, Răng, Chẩn đoán, Trạng thái
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/dashboard`
Headers: 
Row count: 1

### Table on `#/dashboard`
Headers: 
Row count: 1

### Table on `#/dashboard`
Headers: 
Row count: 1

### Table on `#/dashboard`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 22

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 22

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 22

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 22

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 1

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 1

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 1

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 1

### Table on `#/partners`
Headers: , Họ và tên, Ngày sinh, Ngày hẹn gần nhất, Ngày hẹn sắp tới, Ngày điều trị gần nhất, Tình trạng điều trị, Dự kiến thu, Công nợ, Tổng tiền điều trị, Tổng doanh thu, Thẻ thành viên, Nhãn khách hàng, Chi nhánh tạo, Thao tác
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 21

### Table on `#/partners`
Headers: 
Row count: 21

### Table on `#/partners`
Headers: 
Row count: 21

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/partners`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 4

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 4

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 4

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 4

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền
Row count: 2

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền
Row count: 2

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền
Row count: 2

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền
Row count: 2

### Table on `#/warehouse`
Headers: , Tên sản phẩm, Đơn vị tính, Tồn đầu kỳ, Nhập trong kỳ, Xuất trong kỳ, Tồn cuối kỳ
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền, Số lượng, Thành tiền
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 1

### Table on `#/warehouse`
Headers: 
Row count: 1

### Table on `#/warehouse`
Headers: 
Row count: 1

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 1

### Table on `#/warehouse`
Headers: , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 1

### Table on `#/warehouse`
Headers: , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 1

### Table on `#/warehouse`
Headers: , , Tổng, 0, 0, 0, 0, 0, 0, 0, 0
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/warehouse`
Headers: 
Row count: 0

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 2

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 2

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 2

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 2

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 1

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 1

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 1

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 1

### Table on `#/work`
Headers: , Tiêu đề, Loại công việc, Hành động, Người phụ trách, Người theo dõi, Khách hàng, Nội dung CV, Trạng thái CV, Ngày tạo, Thời hạn, Thao tác
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 0

### Table on `#/work`
Headers: 
Row count: 1

### Table on `#/work`
Headers: 
Row count: 1

### Table on `#/work`
Headers: 
Row count: 1

### Table on `#/work`
Headers: 
Row count: 0
