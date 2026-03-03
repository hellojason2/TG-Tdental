/* ==========================================================================
   TDental SPA - Main Application
   ========================================================================== */

(function () {
  'use strict';

  var TODAY_ISO = formatDateInput(new Date());
  var MONTH_START_ISO = formatDateInput(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  // Use 30 days ago as default range start (MONTH_START can equal today on 1st of month)
  var RANGE_START_ISO = formatDateInput(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000));
  var RECENT_CALLS_STORAGE_KEY = 'tds_recent_calls';

  var REPORT_TABS = {
    daily: {
      label: 'Báo cáo ngày',
      endpoint: '/api/reports/daily',
      columns: [
        { key: 'reportDate', label: 'Ngày', type: 'date' },
        { key: 'paymentCount', label: 'Số giao dịch', type: 'number' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
      ],
      exportResource: 'payments',
      exportColumns: ['date', 'amount', 'paymentType', 'journalName', 'partnerName', 'state', 'companyName'],
    },
    service: {
      label: 'Dịch vụ',
      endpoint: '/api/reports/services',
      columns: [
        { key: 'serviceName', label: 'Dịch vụ', type: 'text' },
        { key: 'orderCount', label: 'Số phiếu', type: 'number' },
        { key: 'quantity', label: 'Số lượng', type: 'number' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
      ],
      exportResource: 'sale-orders',
      exportColumns: ['name', 'date', 'state', 'amountTotal', 'partnerName', 'doctorName', 'companyName'],
    },
    customer: {
      label: 'Khách hàng',
      endpoint: '/api/reports/customers',
      columns: [
        { key: 'customerName', label: 'Khách hàng', type: 'text' },
        { key: 'paymentCount', label: 'Số giao dịch', type: 'number' },
        { key: 'totalAmount', label: 'Chi tiêu', type: 'currency' },
      ],
      exportResource: 'customers',
      exportColumns: ['ref', 'name', 'phone', 'dateOfBirth', 'totalDebit', 'amountTreatmentTotal', 'amountRevenueTotal', 'companyName'],
    },
    source: {
      label: 'Nguồn KH',
      endpoint: '/api/reports/sources',
      columns: [
        { key: 'sourceName', label: 'Nguồn', type: 'text' },
        { key: 'customerCount', label: 'Số khách', type: 'number' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
      ],
      exportResource: 'customers',
      exportColumns: ['ref', 'name', 'phone', 'categories', 'companyName'],
    },
    staff: {
      label: 'Nhân viên',
      endpoint: '/api/reports/staff',
      columns: [
        { key: 'staffName', label: 'Nhân viên', type: 'text' },
        { key: 'orderCount', label: 'Số phiếu', type: 'number' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
      ],
      exportResource: 'sale-orders',
      exportColumns: ['name', 'date', 'state', 'amountTotal', 'partnerName', 'doctorName', 'companyName'],
    },
    branch: {
      label: 'Chi nhánh',
      endpoint: '/api/reports/branches',
      columns: [
        { key: 'branchName', label: 'Chi nhánh', type: 'text' },
        { key: 'transactionCount', label: 'Số giao dịch', type: 'number' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
      ],
      exportResource: 'payments',
      exportColumns: ['date', 'amount', 'paymentType', 'journalName', 'partnerName', 'state', 'companyName'],
    },
  };

  var CATEGORY_TYPES = [
    { key: 'services', label: 'Dịch vụ' },
    { key: 'products', label: 'Sản phẩm' },
    { key: 'doctors', label: 'Bác sĩ' },
    { key: 'branches', label: 'Chi nhánh' },
    { key: 'partner-categories', label: 'Nhóm khách hàng' },
    { key: 'partner-sources', label: 'Nguồn khách hàng' },
    { key: 'card-types', label: 'Loại thẻ' },
  ];

  // ---------------------------------------------------------------------------
  // Global State
  // ---------------------------------------------------------------------------
  var APP = {
    user: null,
    token: null,
    currentRoute: null,
    // sidebarCollapsed removed - sidebar is always icon-only
    dashboardCache: {},
    dashboardRequestSeq: 0,
    dashboardData: null,
    toastLimit: 5,
    notifications: {
      open: false,
      unreadCount: 0,
      items: [],
      requestId: 0,
      loaded: false,
      loading: false,
    },
    reports: {
      tab: 'daily',
      dateFrom: RANGE_START_ISO,
      dateTo: TODAY_ISO,
      rowsByTab: {},
      overviewRequestId: 0,
      tableRequestId: 0,
      loading: false,
    },
    partners: {
      search: '',
      items: [],
      loading: false,
      requestId: 0,
      page: 1,
      pageSize: 20,
      total: 0,
      filterTab: 'all',
    },
    customerDetail: {
      id: null,
      data: null,
      loading: false,
      activeTab: 'info',
      appointments: [],
      treatments: [],
      exams: [],
      payments: [],
    },
    tasks: {
      search: '',
      stage: '',
      items: [],
      counts: [],
      loading: false,
      requestId: 0,
    },
    labo: {
      search: '',
      status: '',
      items: [],
      loading: false,
      requestId: 0,
      page: 1,
      pageSize: 20,
      total: 0,
    },
    purchase: {
      pickingType: '',
      state: '',
      items: [],
      loading: false,
      requestId: 0,
    },
    warehouse: {
      search: '',
      items: [],
      summary: [],
      loading: false,
      requestId: 0,
    },
    cashbook: {
      dateFrom: RANGE_START_ISO,
      dateTo: TODAY_ISO,
      paymentType: '',
      items: [],
      loading: false,
      requestId: 0,
    },
    commission: {
      search: '',
      tab: 'overview',
      commissionType: '',
      dateFrom: RANGE_START_ISO,
      dateTo: TODAY_ISO,
      items: [],
      loading: false,
      requestId: 0,
    },
    callcenter: {
      search: '',
      items: [],
      loading: false,
      requestId: 0,
      recentCalls: [],
    },
    salary: {
      dateFrom: RANGE_START_ISO,
      dateTo: TODAY_ISO,
      month: (new Date().getMonth() + 1),
      year: new Date().getFullYear(),
      data: null,
      loading: false,
      requestId: 0,
    },
    categories: {
      kind: 'services',
      search: '',
      dataByKind: {},
      loading: false,
      requestId: 0,
    },
    catProducts: {
      tab: 'services',
      selectedGroup: null,
      groupSearch: '',
      rightSearch: '',
      statusFilter: 'active',
      items: [],
      groups: [],
      loading: false,
      loaded: false,
      companyId: null,
      requestId: 0,
      page: 1,
      pageSize: 20,
      total: 0,
    },
    catPage: {
      search: '',
      items: [],
      loading: false,
      requestId: 0,
      page: 1,
      pageSize: 20,
      total: 0,
    },
    settings: {
      tab: 'branches',
      search: '',
      users: null,
      branches: [],
      branchStatus: 'active',
      branchPage: 1,
      branchPageSize: 20,
      config: null,
      companies: [],
      loading: false,
      requestId: 0,
    },
    calendar: {
      view: 'day',
      segment: 'all',
      date: startOfDay(new Date()),
      dayData: null,
      weekData: null,
      monthData: null,
      requestId: 0,
    },
    reception: {
      date: startOfDay(new Date()),
      data: null,
      requestId: 0,
      busyById: {},
    },
  };

  APP.callcenter.recentCalls = loadRecentCalls();

  // ---------------------------------------------------------------------------
  // Route Definitions
  // ---------------------------------------------------------------------------
  var routes = {
    '#/dashboard': { title: 'Tổng quan', page: 'dashboard', render: renderDashboard },
    '#/partners': { title: 'Khách hàng', page: 'partners', render: renderPartners },
    '#/partners/customers': { title: 'Chi tiết khách hàng', page: 'customer-detail', render: renderCustomerDetail },
    '#/work': { title: 'Công việc', page: 'work', render: renderWork },
    '#/tasks': { title: 'Tác vụ', page: 'tasks', render: renderTasks },
    '#/calendar': { title: 'Lịch hẹn', page: 'calendar', render: renderCalendar },
    '#/labo': { title: 'Labo', page: 'labo', render: renderLabo },
    '#/purchase': { title: 'Mua hàng', page: 'purchase', render: renderPurchase },
    '#/warehouse': { title: 'Kho', page: 'warehouse', render: renderWarehouse },
    '#/salary': { title: 'Lương', page: 'salary', render: renderSalary },
    '#/cashbook': { title: 'Sổ quỹ', page: 'cashbook', render: renderCashbook },
    '#/callcenter': { title: 'Tổng đài', page: 'callcenter', render: renderCallCenter },
    '#/commission': { title: 'Hoa hồng', page: 'commission', render: renderCommission },
    '#/reports': { title: 'Báo cáo', page: 'reports', render: renderReports },
    '#/categories': { title: 'Thông tin KH', page: 'categories', render: renderCatCustomerInfo },
    '#/settings': { title: 'Cài đặt', page: 'settings', render: function () { APP.settings.tab = 'branches'; renderSettings(); } },
    // --- Submenu routes ---
    '#/labo-orders': { title: 'Đặt hàng Labo', page: 'labo', render: renderLaboOrders },
    '#/purchase-refund': { title: 'Trả hàng', page: 'purchase', render: renderPurchaseRefund },
    '#/timekeeping': { title: 'Chấm công', page: 'salary', render: renderTimekeeping },
    '#/salary-payment': { title: 'Thanh toán lương', page: 'salary', render: renderSalaryPayment },
    '#/salary-reports': { title: 'Báo cáo lương', page: 'salary', render: renderSalaryReports },
    '#/receipts': { title: 'Phiếu thu', page: 'cashbook', render: renderReceipts },
    '#/payments': { title: 'Phiếu chi', page: 'cashbook', render: renderPaymentsVoucher },
    '#/account-payment': { title: 'Thanh toán nội bộ', page: 'cashbook', render: renderAccountPayment },
    '#/call-history': { title: 'Lịch sử cuộc gọi', page: 'callcenter', render: renderCallHistory },
    '#/commission-employee': { title: 'Hoa hồng nhân viên', page: 'commission', render: renderCommissionEmployee },
    '#/report-daily': { title: 'Báo cáo ngày', page: 'reports', render: renderReportDaily },
    '#/report-revenue': { title: 'Báo cáo doanh thu', page: 'reports', render: renderReportRevenue },
    '#/report-services': { title: 'Báo cáo dịch vụ', page: 'reports', render: renderReportServices },
    '#/report-customers': { title: 'Báo cáo khách hàng', page: 'reports', render: renderReportCustomers },
    '#/report-reception': { title: 'Báo cáo tiếp nhận', page: 'reports', render: renderReportReception },
    '#/report-supplier-debt': { title: 'Công nợ NCC', page: 'reports', render: renderReportSupplierDebt },
    '#/report-appointments': { title: 'Báo cáo lịch hẹn', page: 'reports', render: renderReportAppointments },
    '#/report-tasks': { title: 'Báo cáo công việc', page: 'reports', render: renderReportTasks },
    '#/report-insurance': { title: 'Công nợ bảo hiểm', page: 'reports', render: renderReportInsurance },
    '#/customer-stage': { title: 'Trạng thái KH', page: 'categories', render: renderCatCustomerStage },
    '#/partner-catalog': { title: 'Đối tác', page: 'categories', render: renderCatPartners },
    '#/products': { title: 'Dịch vụ/Vật tư/Thuốc', page: 'categories', render: renderCatProducts },
    '#/prescriptions': { title: 'Đơn thuốc mẫu', page: 'categories', render: renderCatPrescriptions },
    '#/price-list': { title: 'Bảng giá', page: 'categories', render: renderCatPriceList },
    '#/commission-table': { title: 'Bảng hoa hồng', page: 'categories', render: renderCatCommissionTable },
    '#/employees': { title: 'Nhân viên', page: 'categories', render: renderCatEmployees },
    '#/labo-params': { title: 'Thông số Labo', page: 'categories', render: renderCatLaboParams },
    '#/income-expense-types': { title: 'Loại thu chi', page: 'categories', render: renderCatIncomeExpense },
    '#/stock-criteria': { title: 'Tiêu chí kiểm kho', page: 'categories', render: renderCatStockCriteria },
    '#/tooth-diagnosis': { title: 'Chẩn đoán răng', page: 'categories', render: renderCatToothDiagnosis },
    '#/settings-config': { title: 'Cấu hình chung', page: 'settings', render: function () { APP.settings.tab = 'config'; renderSettings(); } },
    '#/settings-team': { title: 'Cấu hình Team', page: 'settings', render: function () { APP.settings.tab = 'team'; renderSettings(); } },
    '#/settings-other': { title: 'Cấu hình khác', page: 'settings', render: function () { APP.settings.tab = 'other'; renderSettings(); } },
    '#/settings-logs': { title: 'Lịch sử hoạt động', page: 'settings', render: function () { APP.settings.tab = 'logs'; renderSettings(); } },
  };

  // ---------------------------------------------------------------------------
  // API Helper
  // ---------------------------------------------------------------------------
  async function api(endpoint, options) {
    options = options || {};
    var headers = Object.assign({ 'Content-Type': 'application/json' }, options.headers || {});
    var token = localStorage.getItem('token');
    var hadAuthHeader = false;
    if (token) {
      headers.Authorization = 'Bearer ' + token;
      hadAuthHeader = true;
    }
    var fetchOpts = Object.assign({}, options, { headers: headers });
    delete fetchOpts.raw;

    try {
      var res = await fetch(endpoint, fetchOpts);
      if (res.status === 401 && hadAuthHeader) {
        // Recover from stale localStorage token by retrying with cookie session only.
        localStorage.removeItem('token');
        APP.token = null;
        delete headers.Authorization;
        fetchOpts = Object.assign({}, fetchOpts, { headers: headers });
        res = await fetch(endpoint, fetchOpts);
      }

      if (res.status === 401) {
        var authEndpoint = String(endpoint || '');
        var skipRedirect =
          authEndpoint.indexOf('/api/auth/login') === 0 ||
          authEndpoint.indexOf('/api/auth/logout') === 0 ||
          authEndpoint.indexOf('/api/auth/session') === 0;
        if (!skipRedirect && window.location.pathname !== '/login') {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          localStorage.removeItem('selected_branch');
          window.location.href = '/login';
        }
        return null;
      }
      if (options.raw) return res;

      var data = null;
      var contentType = res.headers.get('content-type') || '';
      if (contentType.indexOf('application/json') !== -1) {
        data = await res.json();
      } else {
        var text = await res.text();
        data = text ? { message: text } : {};
      }
      if (!res.ok) {
        throw new Error((data && (data.detail || data.message)) || 'Request failed');
      }
      return data;
    } catch (err) {
      if (err.message !== 'Failed to fetch') {
        throw err;
      }
      showToast('error', 'Không thể kết nối đến máy chủ.');
      return null;
    }
  }

  // ---------------------------------------------------------------------------
  // Toast System
  // ---------------------------------------------------------------------------
  var toastIcons = {
    success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
  };

  function showToast(type, message, duration) {
    duration = typeof duration === 'number' ? duration : 3000;
    type = toastIcons[type] ? type : 'info';
    var container = document.getElementById('toast-container');
    if (!container || !message) return;

    while (container.childElementCount >= APP.toastLimit) {
      removeToast(container.firstElementChild, true);
    }

    var toast = document.createElement('div');
    toast.className = 'tds-toast tds-toast-' + type;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');

    toast.innerHTML =
      '<span class="toast-icon">' + (toastIcons[type] || toastIcons.info) + '</span>' +
      '<span class="toast-message">' + escapeHtml(message) + '</span>' +
      '<button class="toast-close" title="Đóng">&times;</button>' +
      '<div class="tds-toast-progress" style="--toast-dur:' + duration + 'ms"></div>';
    toast.style.position = 'relative';
    toast.style.overflow = 'hidden';

    var closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', function () {
      removeToast(toast);
    });

    container.appendChild(toast);
    requestAnimationFrame(function () {
      toast.classList.add('visible');
    });

    if (duration > 0) {
      toast._timer = setTimeout(function () {
        removeToast(toast);
      }, duration);
    }
  }

  function removeToast(toast, immediate) {
    if (!toast || toast._removing) return;
    toast._removing = true;
    clearTimeout(toast._timer);
    toast.classList.remove('visible');
    toast.classList.add('removing');
    if (immediate) {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
      return;
    }
    setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 240);
  }

  // ---------------------------------------------------------------------------
  // Modal System
  // ---------------------------------------------------------------------------
  function showModal(title, content, options) {
    options = options || {};
    var overlay = document.getElementById('modal-overlay');
    var container = document.getElementById('modal-container');
    if (!overlay || !container) return;

    var width = options.width || 560;
    container.style.maxWidth = width + 'px';

    var footerHtml = '';
    if (options.footer) {
      footerHtml = '<div class="modal-footer">' + options.footer + '</div>';
    }

    container.innerHTML =
      '<div class="modal-header">' +
      '<h3>' + escapeHtml(title) + '</h3>' +
      '<button class="modal-close-btn" id="modal-close-btn">&times;</button>' +
      '</div>' +
      '<div class="modal-body">' + content + '</div>' +
      footerHtml;

    overlay.style.display = 'flex';
    void overlay.offsetHeight;
    overlay.classList.add('visible');

    document.getElementById('modal-close-btn').addEventListener('click', closeModal);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });

    document.addEventListener('keydown', modalEscHandler);

    if (typeof options.onOpen === 'function') {
      options.onOpen(container);
    }
  }

  function closeModal() {
    var overlay = document.getElementById('modal-overlay');
    if (!overlay) return;
    overlay.classList.remove('visible');
    document.removeEventListener('keydown', modalEscHandler);
    setTimeout(function () {
      overlay.style.display = 'none';
      var container = document.getElementById('modal-container');
      if (container) container.innerHTML = '';
    }, 200);
  }

  function modalEscHandler(e) {
    if (e.key === 'Escape') closeModal();
  }
  // ---------------------------------------------------------------------------
  // Treatment Plan Modal - P6
  // ---------------------------------------------------------------------------
  var _treatmentModalState = { selectedTeeth: [], multiSelectMode: false, services: [], currentCustomer: null };

  async function openTreatmentPlanModal(customer) {
    var servicesData = [];
    try {
      var prodResp = await api('/api/products' + toQueryString({ limit: 200 }));
      servicesData = safeItems(prodResp);
    } catch (e) { console.error('Failed to load services:', e); }
    _treatmentModalState = { selectedTeeth: [], multiSelectMode: false, services: servicesData, currentCustomer: customer || null };
    var content = renderTreatmentPlanForm(customer, servicesData);
    showModal('Tạo phiếu điều trị', content, {
      width: 720,
      footer: '<button class="tds-btn tds-btn-ghost" onclick="closeModal()">Hủy</button><button class="tds-btn tds-btn-primary" id="tp-create-btn">Tạo mới</button>',
      onOpen: function() { bindTreatmentPlanModalEvents(customer, servicesData); }
    });
  }

  function renderTreatmentPlanForm(customer, services) {
    var c = customer || {};
    var svcOptions = '<option value="">-- Chọn dịch vụ --</option>';
    for (var i = 0; i < services.length; i++) { svcOptions += '<option value="' + escapeHtml(services[i].id || '') + '" data-name="' + escapeHtml(services[i].name || '') + '" data-price="' + (services[i].price || services[i].unitPrice || services[i].listPrice || 0) + '">' + escapeHtml(services[i].name || '') + '</option>'; }
    var html = '<form id="treatment-plan-form" class="treatment-plan-form">' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group"><label class="tds-label">Bệnh nhân *</label><input type="text" class="tds-input" id="tp-customer-search" placeholder="Tìm kiếm bệnh nhân..." value="' + escapeHtml(c.name || c.partnerName || '') + '" autocomplete="off"><input type="hidden" id="tp-customer-id" value="' + escapeHtml(c.id || c.partnerId || '') + '"><div id="tp-customer-dropdown" class="tp-customer-dropdown" style="display:none"></div></div>' +
      '<div class="tds-form-group"><label class="tds-label">Bác sĩ phụ trách</label><select class="tds-select" id="tp-doctor"><option value="">-- Chọn bác sĩ --</option></select></div>' +
      '</div>' +
      '<div class="tp-section-title">Sơ đồ răng - Chọn răng cần điều trị</div>' +
      '<div class="tp-dental-toolbar"><button type="button" class="tds-btn tds-btn-sm ' + (_treatmentModalState.multiSelectMode ? 'tds-btn-primary' : 'tds-btn-ghost') + '" id="tp-multi-select-btn"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg> Chọn nhiều răng</button><span class="tp-selected-count" id="tp-selected-count" style="display:none">Đã chọn: <strong id="tp-selected-teeth-list"></strong></span></div>' +
      '<div class="tp-dental-chart-wrapper" id="tp-dental-chart">' + renderTreatmentPlanDentalChart() + '</div>' +
      '<div class="tp-selected-teeth-panel" id="tp-selected-teeth-panel" style="display:none"><div class="tp-section-title">Chi tiết điều trị theo răng</div><div id="tp-teeth-details"></div></div>' +
      '<div class="tds-form-row"><div class="tds-form-group"><label class="tds-label">Ghi chú</label><textarea class="tds-textarea" id="tp-notes" rows="3" placeholder="Nhập ghi chú cho phiếu điều trị..."></textarea></div></div>' +
      '<div class="tp-total-row"><span>Tổng tiền:</span><span class="tp-total-amount" id="tp-total-amount">0 ₫</span></div></form>';
    return html;
  }

  function renderTreatmentPlanDentalChart() {
    var UPPER = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28];
    var LOWER = [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38];
    var toothW = 34, toothH = 44, gap = 4, padX = 24, padY = 20;
    var totalW = UPPER.length * (toothW + gap) - gap + padX * 2;
    var svgH = 2 * toothH + 80 + padY * 2;
    var midX = totalW / 2;
    function renderRow(teeth, startY, isUpper) {
      var s = '';
      for (var i = 0; i < teeth.length; i++) {
        var tn = teeth[i];
        var tx = padX + i * (toothW + gap);
        var isSelected = _treatmentModalState.selectedTeeth.indexOf(tn) >= 0;
        var fill = isSelected ? '#1A6DE3' : '#E2E8F0';
        var stroke = isSelected ? '#1557b0' : '#94A3B8';
        var textFill = isSelected ? '#fff' : '#475569';
        s += '<g class="tp-dental-tooth-g" data-tooth="' + tn + '" style="cursor:pointer">';
        s += '<rect x="' + tx + '" y="' + startY + '" width="' + toothW + '" height="' + toothH + '" rx="5" fill="' + fill + '" stroke="' + stroke + '" stroke-width="1.5"/>';
        if (isUpper) { s += '<line x1="' + (tx + toothW / 2) + '" y1="' + (startY + toothH) + '" x2="' + (tx + toothW / 2) + '" y2="' + (startY + toothH + 10) + '" stroke="#94A3B8" stroke-width="1"/>'; }
        else { s += '<line x1="' + (tx + toothW / 2) + '" y1="' + startY + '" x2="' + (tx + toothW / 2) + '" y2="' + (startY - 10) + '" stroke="#94A3B8" stroke-width="1"/>'; }
        s += '<text x="' + (tx + toothW / 2) + '" y="' + (startY + toothH / 2 + 5) + '" text-anchor="middle" font-size="11" font-weight="600" fill="' + textFill + '" font-family="Inter,sans-serif">' + tn + '</text></g>';
      }
      return s;
    }
    var svg = '<svg class="tp-dental-chart-svg" viewBox="0 0 ' + totalW + ' ' + svgH + '" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto">';
    svg += '<rect width="' + totalW + '" height="' + svgH + '" fill="#fff" rx="8"/>';
    svg += '<text x="' + midX + '" y="' + (padY + 2) + '" text-anchor="middle" font-size="11" font-weight="600" fill="#64748B" font-family="Inter,sans-serif">HÀM TRÊN</text>';
    svg += '<line x1="' + midX + '" y1="' + padY + '" x2="' + midX + '" y2="' + (padY + toothH + 20) + '" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="3,3"/>';
    var upperStartY = padY + 12;
    svg += renderRow(UPPER, upperStartY, true);
    var jawSepY = upperStartY + toothH + 30;
    svg += '<line x1="' + padX + '" y1="' + jawSepY + '" x2="' + (totalW - padX) + '" y2="' + jawSepY + '" stroke="#CBD5E1" stroke-width="1"/>';
    svg += '<text x="' + midX + '" y="' + (jawSepY + 12) + '" text-anchor="middle" font-size="11" font-weight="600" fill="#64748B" font-family="Inter,sans-serif">HÀM DƯỚI</text>';
    svg += '<line x1="' + midX + '" y1="' + (jawSepY + 16) + '" x2="' + midX + '" y2="' + (jawSepY + 16 + toothH + 10) + '" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="3,3"/>';
    var lowerStartY = jawSepY + 26;
    svg += renderRow(LOWER, lowerStartY, false);
    svg += '</svg>';
    return svg;
  }

  function bindTreatmentPlanModalEvents(customer, services) {
    var state = _treatmentModalState;
    var multiBtn = document.getElementById('tp-multi-select-btn');
    if (multiBtn) {
      multiBtn.addEventListener('click', function() {
        state.multiSelectMode = !state.multiSelectMode;
        multiBtn.classList.toggle('tds-btn-primary', state.multiSelectMode);
        multiBtn.classList.toggle('tds-btn-ghost', !state.multiSelectMode);
        if (!state.multiSelectMode && state.selectedTeeth.length > 1) { state.selectedTeeth = [state.selectedTeeth[0]]; updateTreatmentPlanTeethUI(); }
      });
    }
    var toothGroups = document.querySelectorAll('.tp-dental-tooth-g');
    for (var i = 0; i < toothGroups.length; i++) {
      toothGroups[i].addEventListener('click', function() {
        var tn = parseInt(this.getAttribute('data-tooth'), 10);
        if (state.multiSelectMode) {
          var idx = state.selectedTeeth.indexOf(tn);
          if (idx >= 0) { state.selectedTeeth.splice(idx, 1); }
          else { state.selectedTeeth.push(tn); }
        } else { state.selectedTeeth = [tn]; }
        updateTreatmentPlanTeethUI();
      });
    }
    var custSearch = document.getElementById('tp-customer-search');
    if (custSearch) {
      var searchTimer = null;
      custSearch.addEventListener('input', function() {
        var q = this.value.trim();
        clearTimeout(searchTimer);
        if (q.length < 2) { var dropdown = document.getElementById('tp-customer-dropdown'); if (dropdown) dropdown.style.display = 'none'; return; }
        searchTimer = setTimeout(async function() {
          try {
            var resp = await api('/api/customers' + toQueryString({ search: q, limit: 10 }));
            var items = safeItems(resp);
            var dropdown = document.getElementById('tp-customer-dropdown');
            if (!dropdown) return;
            if (!items.length) { dropdown.innerHTML = '<div class="tp-customer-empty">Không tìm thấy bệnh nhân</div>'; dropdown.style.display = 'block'; return; }
            var html = '';
            for (var j = 0; j < items.length; j++) { html += '<div class="tp-customer-item" data-id="' + escapeHtml(items[j].id) + '" data-name="' + escapeHtml(items[j].name) + '"><div class="tp-customer-name">' + escapeHtml(items[j].name) + '</div><div class="tp-customer-phone">' + escapeHtml(items[j].phone || '') + '</div></div>'; }
            dropdown.innerHTML = html;
            dropdown.style.display = 'block';
            var custItems = dropdown.querySelectorAll('.tp-customer-item');
            for (var k = 0; k < custItems.length; k++) {
              custItems[k].addEventListener('click', function() {
                var cid = this.getAttribute('data-id');
                var cname = this.getAttribute('data-name');
                custSearch.value = cname;
                document.getElementById('tp-customer-id').value = cid;
                state.currentCustomer = { id: cid, name: cname };
                dropdown.style.display = 'none';
              });
            }
          } catch (e) { console.error('Customer search error:', e); }
        }, 300);
      });
    }
    var createBtn = document.getElementById('tp-create-btn');
    if (createBtn) { createBtn.addEventListener('click', async function() { await createTreatmentPlan(); }); }
    if (customer && customer.id) { document.getElementById('tp-customer-id').value = customer.id; }
  }

  function updateTreatmentPlanTeethUI() {
    var state = _treatmentModalState;
    var chart = document.getElementById('tp-dental-chart');
    if (chart) {
      chart.innerHTML = renderTreatmentPlanDentalChart();
      var toothGroups = document.querySelectorAll('.tp-dental-tooth-g');
      for (var i = 0; i < toothGroups.length; i++) {
        toothGroups[i].addEventListener('click', function() {
          var tn = parseInt(this.getAttribute('data-tooth'), 10);
          if (state.multiSelectMode) {
            var idx = state.selectedTeeth.indexOf(tn);
            if (idx >= 0) { state.selectedTeeth.splice(idx, 1); }
            else { state.selectedTeeth.push(tn); }
          } else { state.selectedTeeth = [tn]; }
          updateTreatmentPlanTeethUI();
        });
      }
    }
    var countEl = document.getElementById('tp-selected-count');
    var teethListEl = document.getElementById('tp-selected-teeth-list');
    var panel = document.getElementById('tp-selected-teeth-panel');
    var detailsEl = document.getElementById('tp-teeth-details');
    if (state.selectedTeeth.length > 0) {
      if (countEl) countEl.style.display = 'inline-flex';
      if (teethListEl) teethListEl.textContent = state.selectedTeeth.sort(function(a,b){return a-b}).join(', ');
      if (panel) panel.style.display = 'block';
      var detailsHtml = '<div class="tp-teeth-details-list">';
      var sortedTeeth = state.selectedTeeth.slice().sort(function(a,b){return a-b});
      for (var j = 0; j < sortedTeeth.length; j++) {
        var tn = sortedTeeth[j];
        var svcOptions = '<option value="">-- Chọn dịch vụ --</option>';
        for (var k = 0; k < state.services.length; k++) { svcOptions += '<option value="' + escapeHtml(state.services[k].id || '') + '" data-name="' + escapeHtml(state.services[k].name || '') + '" data-price="' + (state.services[k].price || state.services[k].unitPrice || state.services[k].listPrice || 0) + '">' + escapeHtml(state.services[k].name || '') + '</option>'; }
        detailsHtml += '<div class="tp-tooth-detail-row" data-tooth="' + tn + '"><div class="tp-tooth-number">Răng ' + tn + '</div><div class="tp-tooth-fields"><select class="tp-tooth-service" data-tooth="' + tn + '">' + svcOptions + '</select><input type="text" class="tp-tooth-type" placeholder="Loại điều trị" value=""><select class="tp-tooth-status"><option value="draft">Chờ xử lý</option><option value="sale">Đang làm</option><option value="done">Hoàn thành</option><option value="cancel">Hủy</option></select><input type="number" class="tp-tooth-cost" placeholder="Giá" value="0" min="0"><button type="button" class="tp-tooth-remove" data-tooth="' + tn + '" title="Xóa">&times;</button></div></div>';
      }
      detailsHtml += '</div>';
      if (detailsEl) detailsEl.innerHTML = detailsHtml;
      var removeBtns = document.querySelectorAll('.tp-tooth-remove');
      for (var m = 0; m < removeBtns.length; m++) { removeBtns[m].addEventListener('click', function() { var t = parseInt(this.getAttribute('data-tooth'), 10); var idx = state.selectedTeeth.indexOf(t); if (idx >= 0) state.selectedTeeth.splice(idx, 1); updateTreatmentPlanTeethUI(); }); }
      var costInputs = document.querySelectorAll('.tp-tooth-cost');
      for (var n = 0; n < costInputs.length; n++) { costInputs[n].addEventListener('input', updateTreatmentPlanTotal); }
    } else { if (countEl) countEl.style.display = 'none'; if (panel) panel.style.display = 'none'; }
  }

  function updateTreatmentPlanTotal() {
    var costInputs = document.querySelectorAll('.tp-tooth-cost');
    var total = 0;
    for (var i = 0; i < costInputs.length; i++) { total += parseFloat(costInputs[i].value) || 0; }
    var totalEl = document.getElementById('tp-total-amount');
    if (totalEl) totalEl.textContent = formatCurrency(total);
  }

  async function createTreatmentPlan() {
    var customerId = document.getElementById('tp-customer-id').value;
    var customerName = document.getElementById('tp-customer-search').value;
    var doctorId = document.getElementById('tp-doctor').value;
    var notes = document.getElementById('tp-notes').value;
    var state = _treatmentModalState;
    if (!customerId) { showToast('error', 'Vui lòng chọn bệnh nhân'); return; }
    if (state.selectedTeeth.length === 0) { showToast('error', 'Vui lòng chọn ít nhất một răng'); return; }
    var lines = [];
    var toothRows = document.querySelectorAll('.tp-tooth-detail-row');
    for (var i = 0; i < toothRows.length; i++) {
      var tn = parseInt(toothRows[i].getAttribute('data-tooth'), 10);
      var svcSelect = toothRows[i].querySelector('.tp-tooth-service');
      var typeInput = toothRows[i].querySelector('.tp-tooth-type');
      var statusSelect = toothRows[i].querySelector('.tp-tooth-status');
      var costInput = toothRows[i].querySelector('.tp-tooth-cost');
      var svcOpt = svcSelect.options[svcSelect.selectedIndex];
      var cost = parseFloat(costInput.value) || 0;
      lines.push({ teeth: [tn], productId: svcSelect.value || null, productName: svcOpt ? svcOpt.getAttribute('data-name') || '' : '', treatmentType: typeInput.value, state: statusSelect.value, unitPrice: cost, qty: 1 });
    }
    try {
      var payload = { name: 'Phiếu điều trị - ' + customerName + ' - ' + new Date().toLocaleDateString('vi-VN'), partnerId: customerId, partnerName: customerName, doctorId: doctorId || null, state: 'sale', notes: notes, lines: JSON.stringify(lines) };
      var result = await api('/api/sale-orders', { method: 'POST', body: JSON.stringify(payload) });
      showToast('success', 'Tạo phiếu điều trị thành công');
      closeModal();
      if (APP.customerDetail && APP.customerDetail.id === customerId) { loadCustomerDetail(customerId); }
    } catch (e) { showToast('error', 'Không thể tạo phiếu điều trị: ' + (e.message || 'Lỗi không xác định')); }
  }

  // ---------------------------------------------------------------------------
  // Tooth History Popup - P10
  // ---------------------------------------------------------------------------
  function showToothHistoryPopup(toothNumber, treatments) {
    var toothTreatments = [];
    for (var i = 0; i < treatments.length; i++) {
      var lines = treatments[i].lines || treatments[i].lineItems || [];
      for (var j = 0; j < lines.length; j++) {
        var rawTeeth = String(lines[j].teeth || lines[j].toothNumber || '').split(/[,;\s]+/).filter(Boolean);
        if (rawTeeth.indexOf(String(toothNumber)) >= 0) { toothTreatments.push({ date: treatments[i].date || treatments[i].orderDate || '', name: treatments[i].name || '', service: lines[j].productName || lines[j].name || '', state: treatments[i].state || '', amount: lines[j].unitPrice || lines[j].subtotal || 0 }); }
      }
    }
    var content = '<div class="tooth-history-popup"><div class="tooth-history-header"><h4>Lịch sử điều trị răng #' + toothNumber + '</h4></div>';
    if (!toothTreatments.length) { content += '<div class="tooth-history-empty">Chưa có điều trị cho răng này</div>'; }
    else {
      content += '<div class="tooth-history-list">';
      for (var k = 0; k < toothTreatments.length; k++) {
        var t = toothTreatments[k];
        var badgeClass = t.state === 'done' ? 'partners-badge-green' : t.state === 'sale' ? 'partners-badge-blue' : 'partners-badge-orange';
        content += '<div class="tooth-history-item"><div class="tooth-history-date">' + formatDate(t.date) + '</div><div class="tooth-history-service">' + escapeHtml(t.service) + '</div><div class="tooth-history-amount">' + formatCurrency(t.amount) + '</div><span class="partners-badge ' + badgeClass + '">' + escapeHtml(translateState(t.state)) + '</span></div>';
      }
      content += '</div>';
    }
    content += '<div class="tooth-history-actions"><button class="tds-btn tds-btn-primary tds-btn-sm" id="tooth-history-add-btn">Thêm điều trị cho răng #' + toothNumber + '</button></div></div>';
    showModal('Lịch sử răng #' + toothNumber, content, { width: 480, footer: '' });
    var addBtn = document.getElementById('tooth-history-add-btn');
    if (addBtn) { addBtn.addEventListener('click', function() { closeModal(); if (APP.customerDetail) { _treatmentModalState.selectedTeeth = [toothNumber]; openTreatmentPlanModal(APP.customerDetail); } }); }
  }

  // ---------------------------------------------------------------------------
  // Enhanced Dental Chart - P10
  // ---------------------------------------------------------------------------
  function bindEnhancedDentalChartClicks(treatments) {
    var selector = document.getElementById('dental-selector');
    var multiSelectEnabled = false;
    var existingToggle = document.getElementById('dental-multi-select-toggle');
    if (!existingToggle) {
      var toolbar = document.querySelector('.cdetail-overview-toolbar');
      if (toolbar) {
        var toggleBtn = document.createElement('button');
        toggleBtn.id = 'dental-multi-select-toggle';
        toggleBtn.className = 'tds-btn tds-btn-sm tds-btn-ghost';
        toggleBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg> Chọn nhiều';
        toggleBtn.style.marginLeft = 'auto';
        toolbar.appendChild(toggleBtn);
        toggleBtn.addEventListener('click', function() {
          multiSelectEnabled = !multiSelectEnabled;
          toggleBtn.classList.toggle('tds-btn-primary', multiSelectEnabled);
          toggleBtn.classList.toggle('tds-btn-ghost', !multiSelectEnabled);
          if (!multiSelectEnabled) { document.querySelectorAll('.dental-tooth-g').forEach(function(g) { g.querySelector('rect').setAttribute('stroke', '#94A3B8'); }); }
        });
      }
    }
    var toothGroups = document.querySelectorAll('.dental-tooth-g');
    for (var i = 0; i < toothGroups.length; i++) {
      toothGroups[i].addEventListener('click', function(e) {
        var selectedTooth = parseInt(this.getAttribute('data-tooth'), 10);
        if (multiSelectEnabled) {
          var rect = this.querySelector('rect');
          rect.setAttribute('stroke', rect.getAttribute('stroke') === '#1A6DE3' ? '#94A3B8' : '#1A6DE3');
        } else { e.preventDefault(); e.stopPropagation(); showToothHistoryPopup(selectedTooth, treatments); }
      });
      toothGroups[i].addEventListener('mouseenter', function() {
        var tn = parseInt(this.getAttribute('data-tooth'), 10);
        var treatedInfo = getToothTreatments(tn, treatments);
        if (treatedInfo.length) {
          var tooltip = document.getElementById('dental-tooltip');
          if (!tooltip) { tooltip = document.createElement('div'); tooltip.id = 'dental-tooltip'; tooltip.style.cssText = 'position:fixed;background:#1e293b;color:#fff;padding:8px 12px;border-radius:6px;font-size:12px;z-index:10000;pointer-events:none;max-width:200px;box-shadow:0 4px 12px rgba(0,0,0,0.15)'; document.body.appendChild(tooltip); }
          tooltip.innerHTML = '<strong>Răng ' + tn + '</strong><br>' + treatedInfo.map(function(t){return t.product + ' (' + formatDate(t.date) + ')';}).join('<br>');
          tooltip.style.display = 'block';
        }
      });
      toothGroups[i].addEventListener('mousemove', function(e) { var tooltip = document.getElementById('dental-tooltip'); if (tooltip) { tooltip.style.left = (e.clientX + 10) + 'px'; tooltip.style.top = (e.clientY + 10) + 'px'; } });
      toothGroups[i].addEventListener('mouseleave', function() { var tooltip = document.getElementById('dental-tooltip'); if (tooltip) tooltip.style.display = 'none'; });
    }
    var addTreatmentBtn = document.getElementById('dental-add-treatment-btn');
    if (!addTreatmentBtn && document.getElementById('dental-multi-select-toggle')) {
      addTreatmentBtn = document.createElement('button');
      addTreatmentBtn.id = 'dental-add-treatment-btn';
      addTreatmentBtn.className = 'tds-btn tds-btn-primary tds-btn-sm';
      addTreatmentBtn.style.marginLeft = '8px';
      addTreatmentBtn.style.display = 'none';
      addTreatmentBtn.textContent = 'Thêm điều trị';
      document.getElementById('dental-multi-select-toggle').parentNode.appendChild(addTreatmentBtn);
      addTreatmentBtn.addEventListener('click', function() {
        var selected = [];
        document.querySelectorAll('.dental-tooth-g').forEach(function(g) { var rect = g.querySelector('rect'); if (rect.getAttribute('stroke') === '#1A6DE3') { selected.push(parseInt(g.getAttribute('data-tooth'), 10)); } });
        if (selected.length > 0 && APP.customerDetail) { _treatmentModalState.selectedTeeth = selected; openTreatmentPlanModal(APP.customerDetail); }
      });
    }
    var toggleBtn = document.getElementById('dental-multi-select-toggle');
    if (toggleBtn) { toggleBtn.addEventListener('click', function() { var btn = document.getElementById('dental-add-treatment-btn'); if (btn) { setTimeout(function() { btn.style.display = toggleBtn.classList.contains('tds-btn-primary') ? 'inline-flex' : 'none'; }, 50); } }); }
    if (selector) selector.style.display = 'none';
  }

  function getToothTreatments(toothNumber, treatments) {
    var result = [];
    for (var i = 0; i < treatments.length; i++) {
      var lines = treatments[i].lines || treatments[i].lineItems || [];
      for (var j = 0; j < lines.length; j++) {
        var rawTeeth = String(lines[j].teeth || lines[j].toothNumber || '').split(/[,;\s]+/).filter(Boolean);
        if (rawTeeth.indexOf(String(toothNumber)) >= 0) { result.push({ product: lines[j].productName || lines[j].name || 'Dịch vụ', date: treatments[i].date || treatments[i].orderDate || '', state: treatments[i].state || '' }); }
      }
    }
    return result;
  }

  // ---------------------------------------------------------------------------
  // Drawer System
  // ---------------------------------------------------------------------------
  function openDrawer(content, width) {
    width = width || 420;
    var overlay = document.getElementById('drawer-overlay');
    var container = document.getElementById('drawer-container');
    if (!overlay || !container) return;

    container.style.width = width + 'px';
    container.innerHTML = content;
    overlay.style.display = 'block';
    void overlay.offsetHeight;
    overlay.classList.add('visible');

    overlay.addEventListener('click', function handler(e) {
      if (e.target === overlay) {
        closeDrawer();
        overlay.removeEventListener('click', handler);
      }
    });

    document.addEventListener('keydown', drawerEscHandler);
  }

  function closeDrawer() {
    var overlay = document.getElementById('drawer-overlay');
    if (!overlay) return;
    overlay.classList.remove('visible');
    document.removeEventListener('keydown', drawerEscHandler);
    setTimeout(function () {
      overlay.style.display = 'none';
      var container = document.getElementById('drawer-container');
      if (container) container.innerHTML = '';
    }, 250);
  }

  function drawerEscHandler(e) {
    if (e.key === 'Escape') closeDrawer();
  }

  // ---------------------------------------------------------------------------
  // P1: Global Search (Ctrl+K / F2)
  // ---------------------------------------------------------------------------
  var globalSearchState = {
    open: false,
    query: '',
    selectedIndex: 0,
    results: { customers: [], appointments: [], tasks: [] },
    loading: false,
    searchTimer: null,
  };

  function initGlobalSearch() {
    var overlay = document.getElementById('global-search-overlay');
    if (!overlay) return;

    // Keyboard shortcut handler
    document.addEventListener('keydown', function (e) {
      // Open search: Ctrl+K or F2
      if ((e.ctrlKey && e.key === 'k') || e.key === 'F2') {
        e.preventDefault();
        openGlobalSearch();
      }
    });

    // Close on overlay click
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) {
        closeGlobalSearch();
      }
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && globalSearchState.open) {
        closeGlobalSearch();
      }
    });

    // Search input handler
    var input = document.getElementById('global-search-input');
    if (input) {
      input.addEventListener('input', function () {
        clearTimeout(globalSearchState.searchTimer);
        globalSearchState.searchTimer = setTimeout(function () {
          performGlobalSearch(input.value);
        }, 300);
      });

      // Keyboard navigation
      input.addEventListener('keydown', function (e) {
        var resultsEl = document.getElementById('global-search-results');
        if (!resultsEl) return;

        var totalItems = getGlobalSearchItemCount();

        if (e.key === 'ArrowDown') {
          e.preventDefault();
          globalSearchState.selectedIndex = Math.min(globalSearchState.selectedIndex + 1, totalItems - 1);
          renderGlobalSearchResults();
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          globalSearchState.selectedIndex = Math.max(globalSearchState.selectedIndex - 1, 0);
          renderGlobalSearchResults();
        } else if (e.key === 'Enter') {
          e.preventDefault();
          executeGlobalSearchItem();
        }
      });
    }
  }

  function openGlobalSearch() {
    globalSearchState.open = true;
    globalSearchState.query = '';
    globalSearchState.selectedIndex = 0;
    globalSearchState.results = { customers: [], appointments: [], tasks: [] };

    var overlay = document.getElementById('global-search-overlay');
    var input = document.getElementById('global-search-input');
    var resultsEl = document.getElementById('global-search-results');

    if (overlay) {
      overlay.classList.add('visible');
      if (input) {
        input.value = '';
        setTimeout(function () { input.focus(); }, 50);
      }
      if (resultsEl) {
        resultsEl.innerHTML = '<div class="global-search-empty">Nhập từ khóa để tìm kiếm...</div>';
      }
    }
  }

  function closeGlobalSearch() {
    globalSearchState.open = false;
    var overlay = document.getElementById('global-search-overlay');
    if (overlay) {
      overlay.classList.remove('visible');
    }
  }

  function getGlobalSearchItemCount() {
    var count = 0;
    if (globalSearchState.results.customers) count += globalSearchState.results.customers.length;
    if (globalSearchState.results.appointments) count += globalSearchState.results.appointments.length;
    if (globalSearchState.results.tasks) count += globalSearchState.results.tasks.length;
    return count;
  }

  async function performGlobalSearch(query) {
    if (!query || query.length < 2) {
      globalSearchState.results = { customers: [], appointments: [], tasks: [] };
      renderGlobalSearchResults();
      return;
    }

    globalSearchState.loading = true;
    renderGlobalSearchLoading();

    var companyId = getSelectedBranchId() || '';
    var searchParams = { search: query, limit: 5 };
    if (companyId) searchParams.companyId = companyId;

    try {
      // Search customers
      var customersReq = api('/api/customers?' + toQueryString(searchParams));
      // Search appointments
      var appointmentsReq = api('/api/appointments?' + toQueryString(Object.assign({}, searchParams, { limit: 5 })));
      // Search tasks
      var tasksReq = api('/api/tasks?' + toQueryString(searchParams));

      var customersRes = await customersReq;
      var appointmentsRes = await appointmentsReq;
      var tasksRes = await tasksReq;

      globalSearchState.results = {
        customers: safeItems(customersRes).slice(0, 5),
        appointments: safeItems(appointmentsRes).slice(0, 5),
        tasks: safeItems(tasksRes).slice(0, 5),
      };
    } catch (err) {
      console.error('Global search error:', err);
      globalSearchState.results = { customers: [], appointments: [], tasks: [] };
    }

    globalSearchState.loading = false;
    globalSearchState.selectedIndex = 0;
    renderGlobalSearchResults();
  }

  function renderGlobalSearchLoading() {
    var resultsEl = document.getElementById('global-search-results');
    if (resultsEl) {
      resultsEl.innerHTML = '<div class="global-search-loading">Đang tìm kiếm...</div>';
    }
  }

  function renderGlobalSearchResults() {
    var resultsEl = document.getElementById('global-search-results');
    if (!resultsEl) return;

    var results = globalSearchState.results;
    var selectedIdx = globalSearchState.selectedIndex;
    var currentIdx = 0;

    var html = '';

    // Customers section
    if (results.customers && results.customers.length > 0) {
      html += '<div class="global-search-section"><div class="global-search-section-title">Khách hàng</div>';
      for (var i = 0; i < results.customers.length; i++) {
        var c = results.customers[i];
        var selected = currentIdx === selectedIdx ? ' selected' : '';
        html += '<div class="global-search-item' + selected + '" data-type="customer" data-id="' + escapeHtml(String(c.id)) + '">' +
          '<div class="global-search-item-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>' +
          '<div class="global-search-item-content"><div class="global-search-item-title">' + escapeHtml(c.name || '—') + '</div>' +
          '<div class="global-search-item-subtitle">' + escapeHtml(c.phone || '—') + '</div></div></div>';
        currentIdx++;
      }
      html += '</div>';
    }

    // Appointments section
    if (results.appointments && results.appointments.length > 0) {
      html += '<div class="global-search-section"><div class="global-search-section-title">Lịch hẹn</div>';
      for (var j = 0; j < results.appointments.length; j++) {
        var a = results.appointments[j];
        var aSelected = currentIdx === selectedIdx ? ' selected' : '';
        html += '<div class="global-search-item' + aSelected + '" data-type="appointment" data-id="' + escapeHtml(String(a.id)) + '">' +
          '<div class="global-search-item-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div>' +
          '<div class="global-search-item-content"><div class="global-search-item-title">' + escapeHtml(a.customerName || '—') + '</div>' +
          '<div class="global-search-item-subtitle">' + escapeHtml(formatDate(a.date) + ' ' + (a.time || '')) + '</div></div></div>';
        currentIdx++;
      }
      html += '</div>';
    }

    // Tasks section
    if (results.tasks && results.tasks.length > 0) {
      html += '<div class="global-search-section"><div class="global-search-section-title">Công việc</div>';
      for (var k = 0; k < results.tasks.length; k++) {
        var t = results.tasks[k];
        var tSelected = currentIdx === selectedIdx ? ' selected' : '';
        html += '<div class="global-search-item' + tSelected + '" data-type="task" data-id="' + escapeHtml(String(t.id)) + '">' +
          '<div class="global-search-item-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div>' +
          '<div class="global-search-item-content"><div class="global-search-item-title">' + escapeHtml(t.title || '—') + '</div>' +
          '<div class="global-search-item-subtitle">' + escapeHtml(t.customerName || '—') + '</div></div></div>';
        currentIdx++;
      }
      html += '</div>';
    }

    // Empty state
    if (!html) {
      html = '<div class="global-search-empty">Không tìm thấy kết quả nào</div>';
    }

    resultsEl.innerHTML = html;

    // Add click handlers
    var items = resultsEl.querySelectorAll('.global-search-item');
    for (var m = 0; m < items.length; m++) {
      items[m].addEventListener('click', function () {
        var type = this.getAttribute('data-type');
        var id = this.getAttribute('data-id');
        navigateToGlobalSearchResult(type, id);
      });
    }
  }

  function executeGlobalSearchItem() {
    var results = globalSearchState.results;
    var selectedIdx = globalSearchState.selectedIndex;
    var currentIdx = 0;

    if (results.customers && selectedIdx < results.customers.length) {
      navigateToGlobalSearchResult('customer', results.customers[selectedIdx].id);
      return;
    }
    if (results.customers) currentIdx += results.customers.length;

    if (results.appointments && selectedIdx < currentIdx + results.appointments.length) {
      navigateToGlobalSearchResult('appointment', results.appointments[selectedIdx - currentIdx].id);
      return;
    }
    if (results.appointments) currentIdx += results.appointments.length;

    if (results.tasks && selectedIdx < currentIdx + results.tasks.length) {
      navigateToGlobalSearchResult('task', results.tasks[selectedIdx - currentIdx].id);
    }
  }

  function navigateToGlobalSearchResult(type, id) {
    closeGlobalSearch();
    if (type === 'customer') {
      // Keep canonical customer-detail hash shape aligned with tasks.md.
      navigateTo('#/partners/customers/' + id + '/overview');
    } else if (type === 'appointment') {
      navigateTo('#/calendar');
    } else if (type === 'task') {
      navigateTo('#/work');
    }
  }

  // ---------------------------------------------------------------------------
  // Router
  // ---------------------------------------------------------------------------
  function navigateTo(hash) {
    if (window.location.hash !== hash) {
      window.location.hash = hash;
    } else {
      handleRoute();
    }
  }

  function handleRoute() {
    var hash = window.location.hash || '#/dashboard';
    var route = routes[hash];

    // Support parameterized routes like #/partners/customers/123
    if (!route && hash.indexOf('#/partners/customers/') === 0) {
      route = routes['#/partners/customers'];
      hash = '#/partners/customers';
    }

    if (!route) {
      hash = '#/dashboard';
      route = routes[hash];
      window.location.hash = hash;
      return;
    }

    var pages = document.querySelectorAll('.page-container');
    for (var i = 0; i < pages.length; i++) {
      pages[i].style.display = 'none';
    }

    var target = document.getElementById('page-' + route.page);
    if (target) target.style.display = 'block';

    document.title = 'TDental - ' + route.title;

    // Update sidebar nav active states
    var navItems = document.querySelectorAll('.sidebar-nav-item');
    for (var j = 0; j < navItems.length; j++) {
      var item = navItems[j];
      var itemRoute = item.getAttribute('data-route');
      // Check if this nav item OR any of its submenu items match the hash
      var isActive = itemRoute === hash || (itemRoute && hash.indexOf(itemRoute + '/') === 0);
      if (!isActive) {
        var subItems = item.querySelectorAll('.submenu-item');
        for (var k = 0; k < subItems.length; k++) {
          if (subItems[k].getAttribute('data-route') === hash) {
            isActive = true;
            break;
          }
        }
      }
      item.classList.toggle('active', isActive);
    }

    // Update submenu item active states
    var submenuItems = document.querySelectorAll('.submenu-item');
    for (var m = 0; m < submenuItems.length; m++) {
      submenuItems[m].classList.toggle('active', submenuItems[m].getAttribute('data-route') === hash);
    }

    var sidebar = document.getElementById('sidebar');
    var backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (backdrop) backdrop.style.display = 'none';

    var fullHash = window.location.hash || '#/dashboard';
    if (APP.currentRoute !== fullHash) {
      APP.currentRoute = fullHash;
      if (typeof route.render === 'function') route.render();
    }
  }

  // ---------------------------------------------------------------------------
  // Sidebar Logic
  // ---------------------------------------------------------------------------
  function isSidebarExpanded() {
    return document.getElementById('sidebar').classList.contains('expanded');
  }

  function isMobileView() {
    return window.innerWidth <= 1024;
  }

  function initSidebar() {
    var sidebar = document.getElementById('sidebar');
    var toggleBtn = document.getElementById('sidebar-toggle');
    var backdrop = document.getElementById('sidebar-backdrop');

    // Restore expanded state from localStorage (desktop only)
    if (!isMobileView()) {
      var savedState = localStorage.getItem('tds-sidebar-expanded');
      if (savedState === 'true') {
        sidebar.classList.add('expanded');
      }
    }

    // Toggle button click handler
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        if (isMobileView()) {
          // Mobile: overlay mode
          var isOpen = sidebar.classList.contains('mobile-open');
          sidebar.classList.toggle('mobile-open', !isOpen);
          backdrop.style.display = isOpen ? 'none' : 'block';
        } else {
          // Desktop: toggle expanded/collapsed
          var isExpanded = sidebar.classList.contains('expanded');
          sidebar.classList.toggle('expanded', !isExpanded);
          localStorage.setItem('tds-sidebar-expanded', !isExpanded ? 'true' : 'false');
          // When collapsing, close all inline submenus
          if (isExpanded) {
            var expandedMenus = sidebar.querySelectorAll('.submenu-expanded');
            for (var k = 0; k < expandedMenus.length; k++) {
              expandedMenus[k].classList.remove('submenu-expanded');
            }
          }
        }
      });
    }

    if (backdrop) {
      backdrop.addEventListener('click', function () {
        sidebar.classList.remove('mobile-open');
        backdrop.style.display = 'none';
      });
    }

    // Nav item click handlers
    var navItems = document.querySelectorAll('.sidebar-nav-item');
    for (var i = 0; i < navItems.length; i++) {
      (function (item) {
        // For items WITHOUT sub-menus, click navigates directly
        if (!item.classList.contains('has-submenu')) {
          var isHelpItem = item.id === 'sidebar-help-btn';
          if (isHelpItem) {
            item.setAttribute('role', 'button');
            item.setAttribute('tabindex', '0');
            item.setAttribute('aria-label', 'Hỗ trợ');
          }
          item.addEventListener('click', function (e) {
            e.preventDefault();
            var route = this.getAttribute('data-route');
            if (route) {
              navigateTo(route);
              return;
            }
            if (isHelpItem) {
              showToast('info', 'Trung tâm hỗ trợ: vui lòng liên hệ quản trị hệ thống.');
            }
          });
          if (isHelpItem) {
            item.addEventListener('keydown', function (e) {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                showToast('info', 'Trung tâm hỗ trợ: vui lòng liên hệ quản trị hệ thống.');
              }
            });
          }
        }

        // For items WITH sub-menus
        if (item.classList.contains('has-submenu')) {
          var showTimer = null;
          var hideTimer = null;

          function showSubmenu() {
            // Only use hover popups in collapsed mode
            if (isSidebarExpanded() || sidebar.classList.contains('mobile-open')) return;
            clearTimeout(hideTimer);
            showTimer = setTimeout(function () {
              item.classList.add('submenu-open');
            }, 50);
          }

          function hideSubmenu() {
            if (isSidebarExpanded() || sidebar.classList.contains('mobile-open')) return;
            clearTimeout(showTimer);
            hideTimer = setTimeout(function () {
              item.classList.remove('submenu-open');
            }, 150);
          }

          item.addEventListener('mouseenter', showSubmenu);
          item.addEventListener('mouseleave', hideSubmenu);

          // Click on nav item toggles inline submenu in expanded/mobile mode
          // OR shows popup submenu in collapsed mode
          item.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (isSidebarExpanded() || sidebar.classList.contains('mobile-open')) {
              // Expanded mode: toggle inline submenu
              item.classList.toggle('submenu-expanded');
            } else {
              // Collapsed mode: toggle popup submenu
              item.classList.toggle('submenu-open');
            }
          });

          // Clicking the icon: in collapsed mode toggles popup submenu, in expanded mode toggles inline submenu
          item.querySelector('.nav-icon').addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (isSidebarExpanded() || sidebar.classList.contains('mobile-open')) {
              // Expanded mode: toggle inline submenu
              item.classList.toggle('submenu-expanded');
              return; // Don't navigate when toggling submenu in expanded mode
            }
            // Collapsed mode: toggle popup submenu instead of navigating
            item.classList.toggle('submenu-open');
          });
        }
      })(navItems[i]);
    }

    // Sub-menu item click handlers
    var submenuItems = document.querySelectorAll('.submenu-item');
    for (var j = 0; j < submenuItems.length; j++) {
      submenuItems[j].addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var route = this.getAttribute('data-route');
        if (route) navigateTo(route);
        // Close submenu popup (collapsed mode)
        var parent = this.closest('.has-submenu');
        if (parent) parent.classList.remove('submenu-open');
        // On mobile, also close sidebar
        if (isMobileView() && sidebar.classList.contains('mobile-open')) {
          sidebar.classList.remove('mobile-open');
          backdrop.style.display = 'none';
        }
      });
    }

    // Logo click → navigate to dashboard (original behavior)
    var logoEl = document.getElementById('sidebar-logo');
    if (logoEl) {
      logoEl.addEventListener('click', function () {
        navigateTo('#/dashboard');
      });
      logoEl.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          navigateTo('#/dashboard');
        }
      });
    }

    // ESC key closes mobile sidebar overlay
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isMobileView() && sidebar.classList.contains('mobile-open')) {
        sidebar.classList.remove('mobile-open');
        backdrop.style.display = 'none';
      }
    });

    // Click outside sidebar closes submenu popups in collapsed mode
    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target)) {
        var openMenus = sidebar.querySelectorAll('.submenu-open');
        for (var m = 0; m < openMenus.length; m++) {
          openMenus[m].classList.remove('submenu-open');
        }
      }
    });

    // Handle window resize: clean up states
    window.addEventListener('resize', function () {
      if (!isMobileView()) {
        sidebar.classList.remove('mobile-open');
        backdrop.style.display = 'none';
        var saved = localStorage.getItem('tds-sidebar-expanded');
        if (saved === 'true' && !sidebar.classList.contains('expanded')) {
          sidebar.classList.add('expanded');
        }
      } else {
        sidebar.classList.remove('expanded');
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Topbar Logic
  // ---------------------------------------------------------------------------
  function initTopbar() {
    var userNameEl = document.getElementById('user-name');
    var avatarEl = document.getElementById('user-avatar');
    if (userNameEl && APP.user) {
      userNameEl.textContent = APP.user.name || APP.user.email || 'Admin';
    }
    if (avatarEl && APP.user) {
      avatarEl.textContent = getUserInitials(APP.user.name || APP.user.email || 'A');
    }

    var logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

    // Branch selector toggle
    var branchBtn = document.getElementById('branch-btn');
    var branchSelector = document.getElementById('branch-selector');
    var branchDropdown = document.getElementById('branch-dropdown');
    if (branchBtn && branchSelector && branchDropdown) {
      if (!branchBtn._boundBranchToggle) {
        branchBtn.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          toggleBranchSelector();
        });
        branchBtn._boundBranchToggle = true;
      }

      if (!branchDropdown._boundBranchClick) {
        branchDropdown.addEventListener('click', function (e) {
          e.stopPropagation();
          var item = e.target.closest('.branch-dropdown-item');
          if (!item) return;
          selectBranchValue(item.getAttribute('data-branch-value') || '');
        });
        branchDropdown._boundBranchClick = true;
      }

      if (!branchBtn._boundBranchKeyboard) {
        branchBtn.addEventListener('keydown', function (e) {
          if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (!isBranchSelectorOpen()) {
              toggleBranchSelector();
            } else {
              focusBranchOption();
            }
          }
        });
        branchBtn._boundBranchKeyboard = true;
      }

      if (!document._boundBranchOutsideClick) {
        document.addEventListener('click', function () {
          closeBranchSelector();
        });
        document._boundBranchOutsideClick = true;
      }

      if (!document._boundBranchEsc) {
        document.addEventListener('keydown', function (e) {
          if (e.key === 'Escape') closeBranchSelector();
        });
        document._boundBranchEsc = true;
      }
    }

    // F2 shortcut for search focus
    document.addEventListener('keydown', function (e) {
      if (e.key === 'F2') {
        e.preventDefault();
        openGlobalSearch();
      }
    });

    // Wire topbar search input to open global search overlay
    var topbarSearchInput = document.getElementById('topbar-search-input');
    if (topbarSearchInput) {
      topbarSearchInput.addEventListener('focus', function () {
        openGlobalSearch();
        // Transfer any typed text to the global search input
        var gsInput = document.getElementById('global-search-input');
        if (gsInput && topbarSearchInput.value) {
          gsInput.value = topbarSearchInput.value;
          performGlobalSearch(topbarSearchInput.value);
        }
        topbarSearchInput.blur();
      });
      topbarSearchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          openGlobalSearch();
          var gsInput = document.getElementById('global-search-input');
          if (gsInput && topbarSearchInput.value) {
            gsInput.value = topbarSearchInput.value;
            performGlobalSearch(topbarSearchInput.value);
          }
        }
      });
    }

    // Timer - counts from a reference date (e.g., account creation or start of year)
    initTopbarTimer();

    loadBranches();
    initNotificationPanel();
    loadNotificationCount();
  }

  function initTopbarTimer() {
    var timerEl = document.getElementById('topbar-timer');
    if (!timerEl) return;

    // Reference date: start of the current year
    var refDate = new Date(new Date().getFullYear(), 0, 1);

    function updateTimer() {
      var now = new Date();
      var diff = now.getTime() - refDate.getTime();
      var days = Math.floor(diff / 86400000);
      var hours = Math.floor((diff % 86400000) / 3600000);
      var minutes = Math.floor((diff % 3600000) / 60000);
      timerEl.textContent = days + ' ngày ' + hours + ' giờ ' + minutes + ' phút';
    }

    updateTimer();
    setInterval(updateTimer, 60000);
  }

  async function loadBranches() {
    var selector = document.getElementById('branch-selector');
    var dropdown = document.getElementById('branch-dropdown');
    if (!selector || !dropdown) return;

    var savedBranch = localStorage.getItem('selected_branch') || '';
    selector.innerHTML = '<option value="">Tất cả chi nhánh</option>';

    try {
      var data = await api('/api/companies?limit=0');
      var branches = Array.isArray(data) ? data : safeItems(data);
      branches.sort(function (a, b) {
        return String(a.name || a.companyName || '').localeCompare(String(b.name || b.companyName || ''), 'vi');
      });
      branches.forEach(function (branch) {
        var opt = document.createElement('option');
        opt.value = branch.id || branch.companyId || '';
        opt.textContent = branch.name || branch.companyName || 'N/A';
        selector.appendChild(opt);
      });
    } catch (_e) {
      // Branch filter is optional.
    }

    if (savedBranch) {
      var exists = selector.querySelector('option[value="' + cssEscape(savedBranch) + '"]');
      selector.value = exists ? savedBranch : '';
      if (!exists) localStorage.removeItem('selected_branch');
    }
    rebuildBranchDropdown();
    syncBranchLabel();

    if (!selector._boundChange) {
      selector.addEventListener('change', function () {
        if (this.value) {
          localStorage.setItem('selected_branch', this.value);
        } else {
          localStorage.removeItem('selected_branch');
        }
        syncBranchLabel();
        closeBranchSelector();
        loadNotificationCount();
        var route = routes[APP.currentRoute];
        if (route && typeof route.render === 'function') route.render();
      });
      selector._boundChange = true;
    }
  }

  function rebuildBranchDropdown() {
    var selector = document.getElementById('branch-selector');
    var dropdown = document.getElementById('branch-dropdown');
    if (!selector || !dropdown) return;
    dropdown.innerHTML = '';

    if (!selector.options || !selector.options.length) {
      var empty = document.createElement('div');
      empty.className = 'branch-dropdown-empty';
      empty.textContent = 'Không có chi nhánh';
      dropdown.appendChild(empty);
      return;
    }

    Array.prototype.forEach.call(selector.options, function (option) {
      var value = option.value || '';
      var item = document.createElement('button');
      item.type = 'button';
      item.className = 'branch-dropdown-item';
      item.setAttribute('role', 'option');
      item.setAttribute('data-branch-value', value);

      var check = document.createElement('span');
      check.className = 'branch-dropdown-item-check';
      check.textContent = '✓';

      var label = document.createElement('span');
      label.className = 'branch-dropdown-item-label';
      label.textContent = option.textContent || 'N/A';

      item.appendChild(check);
      item.appendChild(label);
      dropdown.appendChild(item);
    });

    syncBranchDropdownSelection();
  }

  function syncBranchDropdownSelection() {
    var selector = document.getElementById('branch-selector');
    var dropdown = document.getElementById('branch-dropdown');
    if (!selector || !dropdown) return;

    Array.prototype.forEach.call(dropdown.querySelectorAll('.branch-dropdown-item'), function (item) {
      var isSelected = item.getAttribute('data-branch-value') === (selector.value || '');
      item.classList.toggle('is-selected', isSelected);
      item.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      item.tabIndex = isSelected ? 0 : -1;
    });
  }

  function selectBranchValue(rawValue) {
    var selector = document.getElementById('branch-selector');
    if (!selector) return;
    var value = rawValue || '';
    var exists = selector.querySelector('option[value="' + cssEscape(value) + '"]');
    var nextValue = exists ? value : '';

    if (selector.value === nextValue) {
      syncBranchLabel();
      closeBranchSelector();
      return;
    }

    selector.value = nextValue;
    var changeEvent;
    try {
      changeEvent = new Event('change', { bubbles: true });
    } catch (_e) {
      changeEvent = document.createEvent('HTMLEvents');
      changeEvent.initEvent('change', true, false);
    }
    selector.dispatchEvent(changeEvent);
  }

  function isBranchSelectorOpen() {
    var dropdown = document.getElementById('branch-dropdown');
    return !!(dropdown && dropdown.classList.contains('open'));
  }

  function focusBranchOption() {
    var dropdown = document.getElementById('branch-dropdown');
    if (!dropdown) return;
    var selected = dropdown.querySelector('.branch-dropdown-item.is-selected');
    var first = dropdown.querySelector('.branch-dropdown-item');
    if (selected) {
      selected.focus();
    } else if (first) {
      first.focus();
    }
  }

  function toggleBranchSelector() {
    var wrap = document.querySelector('.branch-wrap');
    var button = document.getElementById('branch-btn');
    var dropdown = document.getElementById('branch-dropdown');
    if (!wrap || !button || !dropdown) return;
    var isOpen = dropdown.classList.contains('open');
    if (isOpen) {
      closeBranchSelector();
      return;
    }
    dropdown.classList.add('open');
    wrap.classList.add('open');
    button.setAttribute('aria-expanded', 'true');
    focusBranchOption();
  }

  function closeBranchSelector() {
    var wrap = document.querySelector('.branch-wrap');
    var button = document.getElementById('branch-btn');
    var dropdown = document.getElementById('branch-dropdown');
    if (dropdown) dropdown.classList.remove('open');
    if (wrap) wrap.classList.remove('open');
    if (button) button.setAttribute('aria-expanded', 'false');
  }

  function syncBranchLabel() {
    var selector = document.getElementById('branch-selector');
    var label = document.getElementById('branch-label');
    if (!selector || !label) return;
    var selected = selector.options[selector.selectedIndex];
    label.textContent = selected ? (selected.textContent || 'Tất cả chi nhánh') : 'Tất cả chi nhánh';
    syncBranchDropdownSelection();
  }

  function initNotificationPanel() {
    var bell = document.getElementById('notification-bell');
    var panel = document.getElementById('notification-panel');
    var refreshBtn = document.getElementById('notification-refresh');
    if (!bell || !panel) return;

    if (!bell._boundClick) {
      bell.addEventListener('click', function (e) {
        e.stopPropagation();
        APP.notifications.open = !APP.notifications.open;
        syncNotificationPanelState();
        if (APP.notifications.open) {
          loadNotificationsInbox(APP.notifications.loaded ? false : true);
        }
      });
      bell._boundClick = true;
    }

    if (!panel._boundClick) {
      panel.addEventListener('click', function (e) {
        e.stopPropagation();
      });
      panel._boundClick = true;
    }

    if (!document._notifOutsideBound) {
      document.addEventListener('click', function () {
        if (!APP.notifications.open) return;
        APP.notifications.open = false;
        syncNotificationPanelState();
      });
      document._notifOutsideBound = true;
    }

    if (refreshBtn && !refreshBtn._boundClick) {
      refreshBtn.addEventListener('click', function () {
        loadNotificationsInbox(true);
      });
      refreshBtn._boundClick = true;
    }

    syncNotificationPanelState();
  }

  function syncNotificationPanelState() {
    var bell = document.getElementById('notification-bell');
    var panel = document.getElementById('notification-panel');
    if (!bell || !panel) return;
    bell.classList.toggle('active', APP.notifications.open);
    panel.classList.toggle('open', APP.notifications.open);
  }

  async function loadNotificationCount() {
    var badge = document.getElementById('notif-count');
    if (!badge) return;

    badge.textContent = '0';
    badge.classList.remove('visible');

    try {
      var data = await api('/api/notifications/init');
      var count = data && typeof data.count === 'number' ? data.count : 0;
      APP.notifications.unreadCount = count;
      if (count > 0) {
        badge.textContent = count > 99 ? '99+' : String(count);
        badge.classList.add('visible');
      }
    } catch (_e) {
      APP.notifications.unreadCount = 0;
    }
  }

  async function loadNotificationsInbox(forceReload) {
    if (APP.notifications.loading) return;
    if (!forceReload && APP.notifications.loaded) {
      renderNotificationInbox();
      return;
    }

    APP.notifications.loading = true;
    APP.notifications.requestId += 1;
    var requestId = APP.notifications.requestId;
    renderNotificationInbox();

    try {
      var data = await api('/api/notifications/inbox?limit=20&offset=0');
      if (requestId !== APP.notifications.requestId) return;
      APP.notifications.items = safeItems(data);
      APP.notifications.loaded = true;
    } catch (_e) {
      if (requestId !== APP.notifications.requestId) return;
      APP.notifications.items = [];
      APP.notifications.loaded = true;
    } finally {
      if (requestId === APP.notifications.requestId) {
        APP.notifications.loading = false;
        renderNotificationInbox();
      }
    }
  }

  function renderNotificationInbox() {
    var listEl = document.getElementById('notification-list');
    if (!listEl) return;

    if (APP.notifications.loading) {
      listEl.innerHTML =
        '<div class="notif-panel-loading">' +
        '<div class="tds-spinner"></div>' +
        '<span>Đang tải thông báo...</span>' +
        '</div>';
      return;
    }

    if (!APP.notifications.items.length) {
      listEl.innerHTML = '<div class="notif-panel-empty">Không có thông báo mới</div>';
      return;
    }

    listEl.innerHTML = APP.notifications.items.map(function (item, idx) {
      var title = escapeHtml(item.title || item.subject || 'Thông báo');
      var preview = escapeHtml(item.preview || item.content || '');
      var dateText = formatDateTime(item.createdAt || item.date);
      var stateClass = item.isRead ? 'read' : 'unread';
      return (
        '<div class="notif-item ' + stateClass + ' notification-item" data-notif-idx="' + idx + '">' +
        '<div class="notif-item-title">' + title + '</div>' +
        '<div class="notif-item-preview">' + preview + '</div>' +
        '<div class="notif-item-meta">' + escapeHtml(dateText) + '</div>' +
        '</div>'
      );
    }).join('');

    // P11: Add click handlers to mark notifications as read
    var notifItems = listEl.querySelectorAll('.notification-item');
    for (var i = 0; i < notifItems.length; i++) {
      notifItems[i].addEventListener('click', function() {
        var idx = parseInt(this.getAttribute('data-notif-idx'), 10);
        var item = APP.notifications.items[idx];
        if (item && !item.isRead) {
          markNotificationAsRead(idx, item);
        }
      });
    }
  }

  // P11: Mark notification as read
  async function markNotificationAsRead(idx, item) {
    var notifId = item.id || item.notificationId;
    try {
      // Try to call API if available
      await api('/api/notifications/' + encodeURIComponent(notifId) + '/read', { method: 'POST' });
    } catch (_e) {
      // API may not exist, just update local state
    }
    // Update local state
    item.isRead = true;
    APP.notifications.unreadCount = Math.max(0, (APP.notifications.unreadCount || 1) - 1);
    // Update badge
    var badge = document.getElementById('notif-count');
    if (badge) {
      badge.textContent = APP.notifications.unreadCount > 0 ? APP.notifications.unreadCount : '';
      badge.style.display = APP.notifications.unreadCount > 0 ? 'block' : 'none';
    }
    // Re-render inbox to show read state
    renderNotificationInbox();
  }

  async function handleLogout() {
    try {
      await api('/api/auth/logout', { method: 'POST' });
    } catch (_e) {
      // Continue client cleanup.
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('selected_branch');
    window.location.href = '/login';
  }

  // ---------------------------------------------------------------------------
  // Auth Check
  // ---------------------------------------------------------------------------
  async function checkAuth() {
    var token = localStorage.getItem('token');
    if (token) APP.token = token;

    var cachedUser = localStorage.getItem('user');
    if (cachedUser) {
      try {
        APP.user = JSON.parse(cachedUser);
      } catch (_e) {
        APP.user = null;
      }
    }

    try {
      var data = await api('/api/auth/session');
      if (data && data.user) {
        APP.user = data.user;
        localStorage.setItem('user', JSON.stringify(data.user));
      } else {
        APP.user = null;
        localStorage.removeItem('user');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
          return false;
        }
      }
    } catch (_e) {
      APP.user = null;
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
        return false;
      }
    }

    return true;
  }

  // ---------------------------------------------------------------------------
  // Page Renderers
  // ---------------------------------------------------------------------------
  function renderDashboard() {
    var host = document.getElementById('page-dashboard');
    if (!host) return;

    var branchId = getSelectedBranchId();
    var branchName = getSelectedBranchName();
    var cacheKey = dashboardCacheKey(branchId);
    var cached = APP.dashboardCache[cacheKey];

    if (cached) {
      APP.dashboardData = cached;
      host.innerHTML = dashboardMarkup(cached, true);
      dashboardBindEvents();
      dashboardRenderCharts(cached);
    } else {
      host.innerHTML = dashboardLoadingMarkup(branchName);
    }

    var requestSeq = ++APP.dashboardRequestSeq;
    dashboardFetchData(branchId, branchName)
      .then(function (data) {
        if (requestSeq !== APP.dashboardRequestSeq) return;
        if (APP.currentRoute !== '#/dashboard') return;
        APP.dashboardCache[cacheKey] = data;
        APP.dashboardData = data;
        host.innerHTML = dashboardMarkup(data, false);
        dashboardBindEvents();
        dashboardRenderCharts(data);
      })
      .catch(function (err) {
        console.error('[dashboard] fetch failed', err);
        if (requestSeq !== APP.dashboardRequestSeq) return;
        if (cached) {
          showToast('warning', 'Không thể cập nhật dashboard, đang hiển thị dữ liệu gần nhất.');
          return;
        }
        host.innerHTML =
          '<div class="tds-card">' +
          '<h2>Tổng quan</h2>' +
          '<p class="text-secondary mt-md">Không thể tải dữ liệu dashboard. Vui lòng thử lại.</p>' +
          '</div>';
        showToast('error', 'Tải dữ liệu dashboard thất bại.');
      });
  }

  function dashboardCacheKey(branchId) {
    return branchId || '__all__';
  }

  function dashboardLoadingMarkup(branchName) {
    return (
      '<div class="db-container">' +
      '<div class="db-stat-cards">' +
      '<div class="stat-card"><div class="stat-icon"></div><div class="stat-content"><div class="stat-value">...</div><div class="stat-label">Khách hàng</div></div></div>' +
      '<div class="stat-card"><div class="stat-icon"></div><div class="stat-content"><div class="stat-value">...</div><div class="stat-label">Lịch hẹn</div></div></div>' +
      '<div class="stat-card"><div class="stat-icon"></div><div class="stat-content"><div class="stat-value">...</div><div class="stat-label">Doanh thu</div></div></div>' +
      '<div class="stat-card"><div class="stat-icon"></div><div class="stat-content"><div class="stat-value">...</div><div class="stat-label">Công việc</div></div></div>' +
      '</div>' +
      '<div class="db-grid">' +
      '<div class="db-left"><div class="db-panel" style="padding:32px;text-align:center">' +
      '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải dữ liệu cho ' + escapeHtml(branchName) + '...</span></div>' +
      '</div></div>' +
      '<div class="db-right"></div>' +
      '</div>' +
      '</div>'
    );
  }

  function dashboardTodayISO() {
    var now = new Date();
    return [
      now.getFullYear(),
      String(now.getMonth() + 1).padStart(2, '0'),
      String(now.getDate()).padStart(2, '0'),
    ].join('-');
  }

  function dashboardShiftDate(iso, dayOffset) {
    var date = parseDateInput((iso || '') + 'T00:00:00');
    if (!date || isNaN(date.getTime()) || date.getFullYear() < 1971) {
      date = new Date();
    }
    date.setDate(date.getDate() + dayOffset);
    return [
      date.getFullYear(),
      String(date.getMonth() + 1).padStart(2, '0'),
      String(date.getDate()).padStart(2, '0'),
    ].join('-');
  }

  function dashboardDailyRange(startISO, endISO) {
    var rows = [];
    var cursor = startISO;
    while (cursor <= endISO) {
      rows.push({
        date: cursor,
        cash: 0,
        bank: 0,
        other: 0,
        totalAmount: 0,
      });
      cursor = dashboardShiftDate(cursor, 1);
    }
    return rows;
  }

  function dashboardDirection(row) {
    var text = String((row && row.paymentType) || '').toLowerCase();
    if (
      text.indexOf('outbound') >= 0 ||
      text.indexOf('outgoing') >= 0 ||
      text.indexOf('chi') >= 0 ||
      text.indexOf('expense') >= 0 ||
      text.indexOf('refund') >= 0
    ) {
      return 'out';
    }
    if (
      text.indexOf('inbound') >= 0 ||
      text.indexOf('incoming') >= 0 ||
      text.indexOf('thu') >= 0 ||
      text.indexOf('income') >= 0 ||
      text.indexOf('receipt') >= 0
    ) {
      return 'in';
    }
    return toNumber(row && row.amount) < 0 ? 'out' : 'in';
  }

  function dashboardBucket(row) {
    var text = (
      String((row && row.paymentType) || '') + ' ' +
      String((row && row.journalName) || '')
    ).toLowerCase();
    if (
      text.indexOf('cash') >= 0 ||
      text.indexOf('tiền mặt') >= 0 ||
      text.indexOf('tien mat') >= 0
    ) {
      return 'cash';
    }
    if (
      text.indexOf('bank') >= 0 ||
      text.indexOf('chuyển khoản') >= 0 ||
      text.indexOf('chuyen khoan') >= 0 ||
      text.indexOf('transfer') >= 0 ||
      text.indexOf('card') >= 0 ||
      text.indexOf('pos') >= 0
    ) {
      return 'bank';
    }
    return 'other';
  }

  function dashboardAggregatePayments(items, startISO, endISO) {
    var daily = dashboardDailyRange(startISO, endISO);
    var byDate = {};
    for (var i = 0; i < daily.length; i++) {
      byDate[daily[i].date] = daily[i];
    }

    var totals = {
      totalCash: 0,
      totalBank: 0,
      totalOther: 0,
      totalAmount: 0,
      daily: daily,
    };

    for (var j = 0; j < items.length; j++) {
      var row = items[j] || {};
      if (dashboardDirection(row) === 'out') continue;
      var dateKey = String(row.date || '').slice(0, 10);
      if (!byDate[dateKey]) continue;

      var amount = Math.abs(toNumber(row.amount));
      var bucket = dashboardBucket(row);
      if (bucket === 'cash') {
        totals.totalCash += amount;
        byDate[dateKey].cash += amount;
      } else if (bucket === 'bank') {
        totals.totalBank += amount;
        byDate[dateKey].bank += amount;
      } else {
        totals.totalOther += amount;
        byDate[dateKey].other += amount;
      }
      totals.totalAmount += amount;
      byDate[dateKey].totalAmount += amount;
    }

    return totals;
  }

  async function dashboardSafeApi(path, options) {
    try {
      return await api(path, options);
    } catch (_err) {
      return null;
    }
  }

  async function dashboardFetchPayments(startISO, endISO, branchId) {
    var query = toQueryString({
      offset: 0,
      limit: 0,
      dateFrom: startISO,
      dateTo: endISO,
      companyId: branchId || undefined,
    });
    var payload = await dashboardSafeApi('/api/payments' + query);
    if (!payload) return [];
    return safeItems(payload);
  }

  async function dashboardSummaryFallback(branchId, todayISO) {
    var todayRows = await dashboardFetchPayments(todayISO, todayISO, branchId);
    var todayAgg = dashboardAggregatePayments(todayRows, todayISO, todayISO);

    var yesterdayISO = dashboardShiftDate(todayISO, -1);
    var yesterdayRows = await dashboardFetchPayments(yesterdayISO, yesterdayISO, branchId);
    var yesterdayAgg = dashboardAggregatePayments(yesterdayRows, yesterdayISO, yesterdayISO);

    return {
      totalCash: todayAgg.totalCash,
      totalBank: todayAgg.totalBank,
      totalOther: todayAgg.totalOther,
      totalAmount: todayAgg.totalAmount,
      totalAmountYesterday: yesterdayAgg.totalAmount,
      daily: todayAgg.daily,
    };
  }

  async function dashboardFetchData(branchId, branchName) {
    var todayISO = dashboardTodayISO();

    var summaryPromise = dashboardSafeApi('/api/reports/summary', {
      method: 'POST',
      body: JSON.stringify({
        companyId: branchId || null,
        dateFrom: todayISO,
        dateTo: todayISO,
      }),
    });

    var receptionPromise = dashboardSafeApi('/api/appointments/reception' + toQueryString({
      date: todayISO,
      companyId: branchId || undefined,
    }));

    var servicesPromise = dashboardSafeApi('/api/sale-orders' + toQueryString({
      dateFrom: todayISO,
      dateTo: todayISO,
      companyId: branchId || undefined,
      limit: 200,
    }));

    // Fetch customer count
    var customersPromise = dashboardSafeApi('/api/customers' + toQueryString({
      companyId: branchId || undefined,
      limit: 1,
      offset: 0,
    }));

    var result = await Promise.all([summaryPromise, receptionPromise, servicesPromise, customersPromise]);
    var summary = result[0];
    var reception = result[1];
    var services = result[2];
    var customersData = result[3];

    if (!summary) summary = await dashboardSummaryFallback(branchId, todayISO);

    var groups = (reception && reception.groups) || { waiting: [], in_progress: [], done: [] };
    var totals = (reception && reception.totals) || { waiting: 0, in_progress: 0, done: 0, all: 0 };

    var allReception = [].concat(groups.waiting || [], groups.in_progress || [], groups.done || []);
    allReception.sort(function (a, b) {
      var ta = a.startTime || '99:99';
      var tb = b.startTime || '99:99';
      return ta < tb ? 1 : ta > tb ? -1 : 0;
    });

    var svcItems = [];
    if (services && services.items) {
      svcItems = services.items;
    } else if (Array.isArray(services)) {
      svcItems = services;
    }

    // Get customer count from response
    var customerCount = 0;
    if (customersData && customersData.totalItems !== undefined) {
      customerCount = customersData.totalItems;
    }

    return {
      branchId: branchId || '',
      branchName: branchName || 'Tất cả chi nhánh',
      fetchedAt: new Date(),
      customerCount: customerCount,
      kpis: {
        cash: toNumber(summary.totalCash),
        bank: toNumber(summary.totalBank),
        other: toNumber(summary.totalOther),
        total: toNumber(summary.totalAmount),
      },
      reception: {
        groups: groups,
        totals: {
          waiting: toNumber(totals.waiting),
          in_progress: toNumber(totals.in_progress),
          done: toNumber(totals.done),
          all: toNumber(totals.all),
        },
        all: allReception,
      },
      services: svcItems,
    };
  }

  /* ----- Dashboard markup helpers ----- */

  var DB_SVG = {
    search: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    refresh: '<svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>',
    plus: '<svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    doctor: '<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    clock: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    phone: '<svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    edit: '<svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
    trash: '<svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
    calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    money: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    work: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
  };

  function dbReceptionStatusClass(state) {
    if (state === 'in_progress') return 'in-progress';
    if (state === 'done') return 'done';
    return 'waiting';
  }

  function dbReceptionStatusLabel(state) {
    if (state === 'in_progress') return 'Đang khám';
    if (state === 'done') return 'Hoàn thành';
    return 'Chờ khám';
  }

  function dbApptStateClass(state) {
    var s = String(state || '').toLowerCase();
    if (s === 'done' || s === 'completed' || s.indexOf('done') >= 0) return 'arrived';
    if (s === 'cancel' || s === 'cancelled' || s.indexOf('cancel') >= 0) return 'cancelled';
    return 'scheduled';
  }

  function dbApptStateLabel(state) {
    var s = String(state || '').toLowerCase();
    if (s === 'done' || s === 'completed' || s.indexOf('done') >= 0) return 'Đã đến';
    if (s === 'cancel' || s === 'cancelled' || s.indexOf('cancel') >= 0) return 'Hủy hẹn';
    return 'Đang hẹn';
  }

  function dashboardMarkup(data, isRefreshing) {
    var rec = data.reception || {};
    var totals = rec.totals || {};
    var allCards = rec.all || [];
    var services = data.services || [];
    var kpis = data.kpis || {};

    // Stat cards data
    var customerCount = data.customerCount || totals.all || 0;
    var appointmentCount = totals.all || 0;
    var revenueAmount = kpis.total || 0;
    var workCount = services.length || 0;

    return (
      '<div class="db-container">' +
      /* ===== STAT CARDS ===== */
      '<div class="db-stat-cards">' +
      '<div class="stat-card">' +
      '<div class="stat-icon">' + DB_SVG.user + '</div>' +
      '<div class="stat-content">' +
      '<div class="stat-value">' + formatNumber(customerCount) + '</div>' +
      '<div class="stat-label">Khách hàng</div>' +
      '</div>' +
      '</div>' +
      '<div class="stat-card">' +
      '<div class="stat-icon">' + DB_SVG.calendar + '</div>' +
      '<div class="stat-content">' +
      '<div class="stat-value">' + formatNumber(appointmentCount) + '</div>' +
      '<div class="stat-label">Lịch hẹn</div>' +
      '</div>' +
      '</div>' +
      '<div class="stat-card">' +
      '<div class="stat-icon">' + DB_SVG.money + '</div>' +
      '<div class="stat-content">' +
      '<div class="stat-value">' + formatCurrency(revenueAmount) + '</div>' +
      '<div class="stat-label">Doanh thu</div>' +
      '</div>' +
      '</div>' +
      '<div class="stat-card">' +
      '<div class="stat-icon">' + DB_SVG.work + '</div>' +
      '<div class="stat-content">' +
      '<div class="stat-value">' + formatNumber(workCount) + '</div>' +
      '<div class="stat-label">Công việc</div>' +
      '</div>' +
      '</div>' +
      '</div>' +

      /* ===== MAIN GRID ===== */
      '<div class="db-grid">' +

      /* ===== LEFT COLUMN ===== */
      '<div class="db-left">' +

      /* -- Reception panel -- */
      '<div class="db-panel db-reception-panel">' +
      '<div class="db-panel-head">' +
      '<span class="db-panel-title">Tiếp nhận khách hàng</span>' +
      '<div class="db-panel-actions">' +
      '<div class="db-search-wrap">' + DB_SVG.search +
      '<input id="db-rec-search" placeholder="Tìm kiếm theo họ tên, sđt">' +
      '</div>' +
      '<button class="db-icon-btn db-icon-btn-filter" id="db-rec-filter" title="Lọc">' +
      '<svg viewBox="0 0 24 24"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>' +
      '</button>' +
      '<button class="db-icon-btn db-icon-btn-refresh" id="db-rec-refresh" title="Làm mới">' + DB_SVG.refresh + '</button>' +
      '<button class="db-icon-btn db-icon-btn-add" id="db-rec-add" title="Thêm" style="background:#1976D2;color:#fff;border-radius:50%;width:32px;height:32px;flex-shrink:0">' + DB_SVG.plus + '</button>' +
      '</div>' +
      '</div>' +
      '<div class="db-tabs" id="db-rec-tabs">' +
      '<button class="db-tab active" data-filter="all">Tất cả<span class="db-tab-count">' + escapeHtml(formatNumber(totals.all || 0)) + '</span></button>' +
      '<button class="db-tab" data-filter="waiting">Chờ khám<span class="db-tab-count">' + escapeHtml(formatNumber(totals.waiting || 0)) + '</span></button>' +
      '<button class="db-tab" data-filter="in_progress">Đang khám<span class="db-tab-count">' + escapeHtml(formatNumber(totals.in_progress || 0)) + '</span></button>' +
      '<button class="db-tab" data-filter="done">Hoàn thành<span class="db-tab-count">' + escapeHtml(formatNumber(totals.done || 0)) + '</span></button>' +
      '</div>' +
      '<div class="db-card-list" id="db-rec-list">' +
      dbBuildReceptionCards(allCards) +
      '</div>' +
      '</div>' +

      /* -- Services panel -- */
      '<div class="db-panel db-svc-panel">' +
      '<div class="db-panel-head">' +
      '<span class="db-panel-title">Dịch vụ trong ngày</span>' +
      '<div class="db-panel-actions">' +
      '<button class="db-icon-btn" id="db-svc-refresh" title="Làm mới">' + DB_SVG.refresh + '</button>' +
      '<div class="db-search-wrap">' + DB_SVG.search +
      '<input id="db-svc-search" placeholder="Tìm kiếm nhanh">' +
      '</div>' +
      '</div>' +
      '</div>' +
      '<div class="db-svc-table-wrap">' +
      dbBuildServicesTable(services) +
      '</div>' +
      '</div>' +

      '</div>' + /* end .db-left */

      /* ===== RIGHT COLUMN ===== */
      '<div class="db-right">' +

      /* -- Appointments panel -- */
      '<div class="db-panel db-appt-panel">' +
      '<div class="db-panel-head">' +
      '<span class="db-panel-title">Lịch hẹn hôm nay</span>' +
      '<div class="db-panel-actions">' +
      '<button class="db-icon-btn db-icon-btn-refresh" id="db-appt-refresh" title="Làm mới">' + DB_SVG.refresh + '</button>' +
      '<button class="db-icon-btn db-icon-btn-add" id="db-appt-add" title="Thêm lịch hẹn" style="background:#1976D2;color:#fff;border-radius:50%;width:32px;height:32px;flex-shrink:0">' + DB_SVG.plus + '</button>' +
      '</div>' +
      '</div>' +
      '<div class="db-panel-head" style="padding-top:4px">' +
      '<div class="db-search-wrap" style="flex:1">' + DB_SVG.search +
      '<input id="db-appt-search" placeholder="Tìm kiếm theo bác sĩ, họ tên, sđt">' +
      '</div>' +
      '<button class="db-icon-btn db-icon-btn-palette" title="Lọc màu" style="margin-left:4px">' +
      '<svg viewBox="0 0 24 24" width="18" height="18"><circle cx="6" cy="12" r="3" fill="#F97316"/><circle cx="12" cy="6" r="3" fill="#3B82F6"/><circle cx="18" cy="12" r="3" fill="#10B981"/><circle cx="12" cy="18" r="3" fill="#8B5CF6"/></svg>' +
      '</button>' +
      '</div>' +
      '<div class="db-tabs" id="db-appt-tabs">' +
      dbBuildApptTabs(allCards) +
      '<button class="db-icon-btn db-tab-overflow" title="Thêm" style="margin-left:auto;padding:0 6px;font-size:18px;letter-spacing:1px;line-height:1">&#8943;</button>' +
      '</div>' +
      '<div class="db-card-list" id="db-appt-list">' +
      dbBuildApptCards(allCards) +
      '</div>' +
      '</div>' +

      /* -- Revenue panel -- */
      '<div class="db-panel db-revenue-panel">' +
      '<div class="db-revenue-title">Doanh thu</div>' +
      '<div class="db-revenue-total">' +
      '<h3>' + escapeHtml(formatCurrency(data.kpis.total)) + '</h3>' +
      '<p>Tổng doanh thu</p>' +
      '</div>' +
      '<canvas id="db-revenue-canvas" class="db-revenue-canvas"></canvas>' +
      '<div id="db-revenue-legend" class="db-revenue-legend"></div>' +
      '</div>' +

      '</div>' + /* end .db-right */

      '</div>' + /* end .db-grid */

      '</div>' /* end .db-container */
    );
  }

  var DB_EMPTY_SVG_RECEPTION = (
    '<div style="text-align:center;padding:40px 0">' +
    '<div style="margin:0 auto;width:120px;height:120px;background:#f5f5f5;border-radius:12px;display:flex;align-items:center;justify-content:center;margin-bottom:12px">' +
    '<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5"><rect x="5" y="2" width="14" height="20" rx="2"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="9" x2="12" y2="11"/><circle cx="12" cy="13.5" r="0.5" fill="#ccc"/></svg>' +
    '</div>' +
    '<p style="color:#999;font-size:14px;margin:0">Không có dữ liệu</p>' +
    '</div>'
  );

  var DB_EMPTY_SVG_APPT = (
    '<div style="text-align:center;padding:40px 0">' +
    '<div style="margin:0 auto;width:120px;height:120px;background:#f5f5f5;border-radius:12px;display:flex;align-items:center;justify-content:center;margin-bottom:12px">' +
    '<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="8" y1="14" x2="8" y2="14" stroke-linecap="round"/><circle cx="8" cy="14" r="0.5" fill="#ccc"/></svg>' +
    '</div>' +
    '<p style="color:#999;font-size:14px;margin:0">Không có dữ liệu</p>' +
    '</div>'
  );

  function dbBuildReceptionCards(items) {
    if (!items || !items.length) return DB_EMPTY_SVG_RECEPTION;
    var html = '';
    for (var i = 0; i < items.length; i++) {
      html += dbReceptionCard(items[i]);
    }
    return html;
  }

  function dbReceptionCard(item) {
    var state = item.state || 'waiting';
    var bucket = (state === 'in_progress' || state === 'done') ? state : 'waiting';
    var cls = dbReceptionStatusClass(bucket);
    var label = dbReceptionStatusLabel(bucket);
    var name = item.patientName || 'Không rõ tên';
    var doctor = item.doctorName || '---';
    var time = item.startTime || '--:--';
    var patientId = '';
    if (item.id) {
      patientId = item.id;
    }
    return (
      '<div class="db-rcard" data-state="' + escapeHtml(bucket) + '" data-name="' + escapeHtml(name.toLowerCase()) + '" data-phone="' + escapeHtml((item.patientPhone || '').toLowerCase()) + '">' +
      '<span class="db-rcard-status ' + cls + '">' + escapeHtml(label) + '</span>' +
      '<div class="db-rcard-info">' +
      '<img class="db-rcard-avatar" src="data:image/svg+xml,' + encodeURIComponent('<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'%2394A3B8\'><circle cx=\'12\' cy=\'8\' r=\'4\'/><path d=\'M20 21a8 8 0 1 0-16 0\'/></svg>') + '">' +
      '<a href="#/partners/customers/' + escapeHtml(patientId) + '/overview">' + escapeHtml(name) + '</a>' +
      '</div>' +
      '<span class="db-rcard-doctor">' + DB_SVG.doctor + ' ' + escapeHtml(doctor) + '</span>' +
      '<span class="db-rcard-time">' + DB_SVG.clock + ' ' + escapeHtml(time) + '</span>' +
      '</div>'
    );
  }

  function dbBuildApptTabs(allCards) {
    var counts = { all: 0, scheduled: 0, arrived: 0, cancelled: 0 };
    for (var i = 0; i < allCards.length; i++) {
      var cls = dbApptStateClass(allCards[i].state);
      counts.all++;
      if (cls === 'scheduled') counts.scheduled++;
      else if (cls === 'arrived') counts.arrived++;
      else if (cls === 'cancelled') counts.cancelled++;
    }
    return (
      '<button class="db-tab active" data-filter="all">Tất cả<span class="db-tab-count">' + counts.all + '</span></button>' +
      '<button class="db-tab" data-filter="scheduled">Đang hẹn<span class="db-tab-count">' + counts.scheduled + '</span></button>' +
      '<button class="db-tab" data-filter="arrived">Đã đến<span class="db-tab-count">' + counts.arrived + '</span></button>' +
      '<button class="db-tab" data-filter="cancelled">Hủy hẹn<span class="db-tab-count">' + counts.cancelled + '</span></button>'
    );
  }

  function dbBuildApptCards(items) {
    if (!items || !items.length) return DB_EMPTY_SVG_APPT;
    var html = '';
    for (var i = 0; i < items.length; i++) {
      html += dbApptCard(items[i]);
    }
    return html;
  }

  function dbApptCard(item) {
    var name = item.patientName || 'Không rõ tên';
    var doctor = item.doctorName || '---';
    var time = item.startTime || '--:--';
    var phone = item.patientPhone || '';
    var stateClass = dbApptStateClass(item.state);
    var stateLabel = dbApptStateLabel(item.state);
    var patientId = item.id || '';
    return (
      '<div class="db-acard" data-id="' + escapeHtml(item.id || '') + '" data-appt-state="' + escapeHtml(stateClass) + '" data-name="' + escapeHtml(name.toLowerCase()) + '" data-doctor="' + escapeHtml(doctor.toLowerCase()) + '" data-phone="' + escapeHtml(phone.toLowerCase()) + '">' +
      '<div class="db-acard-top">' +
      '<div class="db-acard-patient">' +
      '<img class="db-acard-avatar" src="data:image/svg+xml,' + encodeURIComponent('<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'%2394A3B8\'><circle cx=\'12\' cy=\'8\' r=\'4\'/><path d=\'M20 21a8 8 0 1 0-16 0\'/></svg>') + '">' +
      '<a href="#/partners/customers/' + escapeHtml(patientId) + '/overview">' + escapeHtml(name) + '</a>' +
      '</div>' +
      '<div class="db-acard-actions">' +
      '<button class="db-icon-btn db-acard-edit" title="Chỉnh sửa" data-id="' + escapeHtml(item.id || '') + '">' + DB_SVG.edit + '</button>' +
      '<button class="db-icon-btn db-acard-delete" title="Xóa" data-id="' + escapeHtml(item.id || '') + '">' + DB_SVG.trash + '</button>' +
      '</div>' +
      '</div>' +
      '<div class="db-acard-meta">' +
      '<div class="db-acard-meta-left">' +
      '<span class="db-acard-meta-item">' + DB_SVG.doctor + ' ' + escapeHtml(doctor) + '</span>' +
      '<span class="db-acard-meta-item">' + DB_SVG.clock + ' ' + escapeHtml(time) + '</span>' +
      (phone ? '<span class="db-acard-meta-item">' + DB_SVG.phone + ' ' + escapeHtml(phone) + '</span>' : '') +
      '</div>' +
      '<button class="db-acard-state-btn ' + stateClass + '">' + escapeHtml(stateLabel) + '</button>' +
      '</div>' +
      '</div>'
    );
  }

  function dbBuildServicesTable(items) {
    var html = '<table class="db-svc-table"><thead><tr>' +
      '<th>Dịch vụ</th>' +
      '<th>Khách hàng</th>' +
      '<th>Số lượng</th>' +
      '<th>Bác sĩ</th>' +
      '<th class="text-right">Thành tiền</th>' +
      '<th class="text-right">Thanh toán</th>' +
      '</tr></thead><tbody>';

    if (!items || !items.length) {
      html += '<tr><td colspan="6" style="text-align:center;padding:0">' +
        '<div style="text-align:center;padding:40px 0">' +
        '<div style="margin:0 auto;width:120px;height:120px;background:#f5f5f5;border-radius:12px;display:flex;align-items:center;justify-content:center;margin-bottom:12px">' +
        '<svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/></svg>' +
        '</div>' +
        '<p style="color:#999;font-size:14px;margin:0">Không có dữ liệu</p>' +
        '</div>' +
        '</td></tr>';
    } else {
      for (var i = 0; i < items.length; i++) {
        var row = items[i];
        html += '<tr>' +
          '<td><div class="db-svc-name"><span>' + escapeHtml(row.name || '---') + '</span></div></td>' +
          '<td><a href="#/partners/customers/' + escapeHtml(row.partnerId || '') + '/overview">' + escapeHtml(row.partnerName || '---') + '</a></td>' +
          '<td>1</td>' +
          '<td>' + escapeHtml(row.doctorName || '---') + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(toNumber(row.amountTotal))) + '</td>' +
          '<td class="text-right">0</td>' +
          '</tr>';
      }
    }
    html += '</tbody></table>';
    return html;
  }

  /* Revenue donut drawing */
  function dashboardPrepareCanvas(canvas, heightHint) {
    if (!canvas) return null;
    var width = Math.max(Math.floor(canvas.clientWidth || 0), 120);
    var height = Math.max(Math.floor(heightHint || canvas.clientHeight || 0), 140);
    var ratio = window.devicePixelRatio || 1;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    var ctx = canvas.getContext('2d');
    if (!ctx) return null;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    return { ctx: ctx, width: width, height: height };
  }

  function dashboardDrawRevenue(kpis) {
    var canvas = document.getElementById('db-revenue-canvas');
    var prepared = dashboardPrepareCanvas(canvas, 180);
    if (!prepared) return;
    var ctx = prepared.ctx;
    var width = prepared.width;
    var height = prepared.height;

    var slices = [
      { label: 'Tiền mặt', value: toNumber(kpis.cash), color: '#F97316' },
      { label: 'Chuyển khoản', value: toNumber(kpis.bank), color: '#3B82F6' },
      { label: 'Khác', value: toNumber(kpis.other), color: '#8B5CF6' },
    ].filter(function (s) { return s.value > 0; });

    var total = slices.reduce(function (sum, s) { return sum + s.value; }, 0);

    var centerX = width / 2;
    var centerY = height / 2;
    var radius = Math.min(width, height) * 0.38;
    var inner = radius * 0.6;

    if (total <= 0) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.fillStyle = '#E2E8F0';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(centerX, centerY, inner, 0, Math.PI * 2);
      ctx.fillStyle = '#FFFFFF';
      ctx.fill();
      return;
    }

    var start = -Math.PI / 2;
    for (var i = 0; i < slices.length; i++) {
      var angle = (slices[i].value / total) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, start, start + angle);
      ctx.closePath();
      ctx.fillStyle = slices[i].color;
      ctx.fill();
      start += angle;
    }

    ctx.beginPath();
    ctx.arc(centerX, centerY, inner, 0, Math.PI * 2);
    ctx.fillStyle = '#FFFFFF';
    ctx.fill();

    /* Legend */
    var legend = document.getElementById('db-revenue-legend');
    if (legend) {
      legend.innerHTML = slices.map(function (s) {
        return (
          '<div class="db-revenue-legend-item">' +
          '<span class="db-revenue-legend-label">' +
          '<span class="db-revenue-dot" style="background:' + s.color + '"></span>' +
          escapeHtml(s.label) +
          '</span>' +
          '<strong>' + escapeHtml(formatCurrency(s.value)) + '</strong>' +
          '</div>'
        );
      }).join('');
    }
  }

  function dashboardRenderCharts(data) {
    dashboardDrawRevenue(data.kpis || {});
  }

  function dashboardHandleResize() {
    if (APP.currentRoute === '#/dashboard' && APP.dashboardData) {
      dashboardRenderCharts(APP.dashboardData);
    }
  }

  /* Dashboard event binding */
  function dashboardBindEvents() {
    var host = document.getElementById('page-dashboard');
    if (!host) return;

    /* Reception tab filtering */
    var recTabs = host.querySelector('#db-rec-tabs');
    if (recTabs) {
      recTabs.addEventListener('click', function (e) {
        var tab = e.target.closest('.db-tab');
        if (!tab) return;
        recTabs.querySelectorAll('.db-tab').forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        var filter = tab.getAttribute('data-filter');
        var cards = host.querySelectorAll('#db-rec-list .db-rcard');
        cards.forEach(function (card) {
          card.style.display = (filter === 'all' || card.getAttribute('data-state') === filter) ? '' : 'none';
        });
      });
    }

    /* Reception search */
    var recSearch = host.querySelector('#db-rec-search');
    if (recSearch) {
      recSearch.addEventListener('input', debounce(function () {
        var q = recSearch.value.trim().toLowerCase();
        var cards = host.querySelectorAll('#db-rec-list .db-rcard');
        cards.forEach(function (card) {
          if (!q) { card.style.display = ''; return; }
          var name = card.getAttribute('data-name') || '';
          var phone = card.getAttribute('data-phone') || '';
          card.style.display = (name.indexOf(q) >= 0 || phone.indexOf(q) >= 0) ? '' : 'none';
        });
      }, 200));
    }

    /* Appointment tab filtering */
    var apptTabs = host.querySelector('#db-appt-tabs');
    if (apptTabs) {
      apptTabs.addEventListener('click', function (e) {
        var tab = e.target.closest('.db-tab');
        if (!tab) return;
        apptTabs.querySelectorAll('.db-tab').forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        var filter = tab.getAttribute('data-filter');
        var cards = host.querySelectorAll('#db-appt-list .db-acard');
        cards.forEach(function (card) {
          card.style.display = (filter === 'all' || card.getAttribute('data-appt-state') === filter) ? '' : 'none';
        });
      });
    }

    /* Appointment search */
    var apptSearch = host.querySelector('#db-appt-search');
    if (apptSearch) {
      apptSearch.addEventListener('input', debounce(function () {
        var q = apptSearch.value.trim().toLowerCase();
        var cards = host.querySelectorAll('#db-appt-list .db-acard');
        cards.forEach(function (card) {
          if (!q) { card.style.display = ''; return; }
          var name = card.getAttribute('data-name') || '';
          var doctor = card.getAttribute('data-doctor') || '';
          var phone = card.getAttribute('data-phone') || '';
          card.style.display = (name.indexOf(q) >= 0 || doctor.indexOf(q) >= 0 || phone.indexOf(q) >= 0) ? '' : 'none';
        });
      }, 200));
    }

    /* Services search */
    var svcSearch = host.querySelector('#db-svc-search');
    if (svcSearch) {
      svcSearch.addEventListener('input', debounce(function () {
        var q = svcSearch.value.trim().toLowerCase();
        var rows = host.querySelectorAll('.db-svc-table tbody tr');
        rows.forEach(function (row) {
          if (!q) { row.style.display = ''; return; }
          row.style.display = (row.textContent || '').toLowerCase().indexOf(q) >= 0 ? '' : 'none';
        });
      }, 200));
    }

    /* Refresh buttons */
    var recRefresh = host.querySelector('#db-rec-refresh');
    if (recRefresh) recRefresh.addEventListener('click', function () { renderDashboard(); });
    var svcRefresh = host.querySelector('#db-svc-refresh');
    if (svcRefresh) svcRefresh.addEventListener('click', function () { renderDashboard(); });
    var apptRefresh = host.querySelector('#db-appt-refresh');
    if (apptRefresh) apptRefresh.addEventListener('click', function () { renderDashboard(); });

    /* db-rec-add: Open customer modal to create new customer/appointment */
    var recAddBtn = host.querySelector('#db-rec-add');
    if (recAddBtn) {
      recAddBtn.addEventListener('click', function () {
        openCustomerModal(null);
      });
    }

    /* db-rec-filter: Toggle filter dropdown for reception cards */
    var recFilterBtn = host.querySelector('#db-rec-filter');
    if (recFilterBtn) {
      recFilterBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        var existingDropdown = host.querySelector('.db-rec-filter-dropdown');
        if (existingDropdown) {
          existingDropdown.remove();
          return;
        }
        var dropdown = document.createElement('div');
        dropdown.className = 'db-rec-filter-dropdown';
        dropdown.innerHTML =
          '<div class="db-filter-option" data-filter="all">Tất cả</div>' +
          '<div class="db-filter-option" data-filter="waiting">Chờ tiếp nhận</div>' +
          '<div class="db-filter-option" data-filter="arrived">Đã tiếp nhận</div>' +
          '<div class="db-filter-option" data-filter="done">Hoàn thành</div>' +
          '<div class="db-filter-option" data-filter="cancel">Hủy</div>';
        dropdown.style.cssText = 'position:absolute;top:100%;right:0;margin-top:4px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:1000;min-width:150px;overflow:hidden';
        recFilterBtn.parentElement.style.position = 'relative';
        recFilterBtn.parentElement.appendChild(dropdown);
        dropdown.querySelectorAll('.db-filter-option').forEach(function (opt) {
          opt.style.cssText = 'padding:10px 16px;cursor:pointer;font-size:14px;color:#334155';
          opt.addEventListener('mouseenter', function () { this.style.background = '#f1f5f9'; });
          opt.addEventListener('mouseleave', function () { this.style.background = ''; });
          opt.addEventListener('click', function () {
            var filter = this.getAttribute('data-filter');
            var cards = host.querySelectorAll('#db-rec-list .db-rcard');
            cards.forEach(function (card) {
              card.style.display = (filter === 'all' || card.getAttribute('data-state') === filter) ? '' : 'none';
            });
            dropdown.remove();
          });
        });
        document.addEventListener('click', function docClick(e) {
          if (!dropdown.contains(e.target) && e.target !== recFilterBtn) {
            dropdown.remove();
            document.removeEventListener('click', docClick);
          }
        });
      });
    }

    /* db-appt-add: Open appointment form modal */
    var apptAddBtn = host.querySelector('#db-appt-add');
    if (apptAddBtn) {
      apptAddBtn.addEventListener('click', function () {
        showAppointmentFormModal(null);
      });
    }

    /* Appointment card edit/delete buttons */
    var apptList = host.querySelector('#db-appt-list');
    if (apptList) {
      apptList.addEventListener('click', function (e) {
        var editBtn = e.target.closest('.db-acard-edit');
        if (editBtn) {
          e.stopPropagation();
          var apptId = editBtn.getAttribute('data-id');
          if (!apptId) return;
          // Find the appointment data from dashboard data
          var apptData = null;
          var today = APP.dashboardData;
          if (today && today.appointments) {
            for (var i = 0; i < today.appointments.length; i++) {
              if (String(today.appointments[i].id) === String(apptId)) {
                apptData = today.appointments[i];
                break;
              }
            }
          }
          if (apptData) {
            showAppointmentFormModal(apptData);
          } else {
            // If not found in dashboard data, try to load it
            api('/api/appointments/' + encodeURIComponent(apptId)).then(function (data) {
              if (data && data.id) {
                showAppointmentFormModal(data);
              } else {
                showToast('error', 'Khong tim thay lich hen');
              }
            }).catch(function () {
              showToast('error', 'Khong tim thay lich hen');
            });
          }
          return;
        }

        var deleteBtn = e.target.closest('.db-acard-delete');
        if (deleteBtn) {
          e.stopPropagation();
          var apptId = deleteBtn.getAttribute('data-id');
          if (!apptId) return;
          tdsConfirm('B\u1ea1n c\u00f3 ch\u1eafc ch\u1eafn mu\u1ed1n x\u00f3a l\u1ecbch h\u1eb9n n\u00e0y?', { title: 'X\u00f3a l\u1ecbch h\u1eb9n', okText: 'X\u00f3a' }).then(function (ok) {
            if (!ok) return;
            api('/api/appointments/' + encodeURIComponent(apptId), { method: 'DELETE' }).then(function () {
              showToast('success', '\u0110\u00e3 x\u00f3a l\u1ecbch h\u1eb9n th\u00e0nh c\u00f4ng');
              renderDashboard();
            }).catch(function (err) {
              showToast('error', 'Kh\u00f4ng th\u1ec3 x\u00f3a l\u1ecbch h\u1eb9n: ' + (err.message || 'L\u1ed7i kh\u00f4ng x\u00e1c \u0111\u1ecbnh'));
            });
          });
        }
      });
    }
  }

  // ---------------------------------------------------------------------------
  // Phase 4: Customer List Page (redesigned)
  // ---------------------------------------------------------------------------
  function getPartnerStatus(item) {
    var state = (item.orderState || '').toLowerCase();
    if (state === 'sale' || state === 'done' || state.indexOf('dang') !== -1 || state.indexOf('điều trị') !== -1) return 'treating';
    if (state === 'draft' || state === 'new' || state.indexOf('moi') !== -1 || state.indexOf('mới') !== -1) return 'new';
    return 'inactive';
  }

  function getPartnerStatusLabel(status) {
    if (status === 'treating') return 'Đang điều trị';
    if (status === 'new') return 'Mới';
    return 'Chưa phát sinh';
  }

  function getPartnerStatusClass(status) {
    if (status === 'treating') return 'partners-badge-blue';
    if (status === 'new') return 'partners-badge-green';
    return 'partners-badge-gray';
  }

  function getFilteredPartners() {
    var all = APP.partners.items || [];
    var tab = APP.partners.filterTab;
    // Hidden tab no longer exists in UI - default to 'all'
    if (tab === 'hidden') {
      tab = 'all';
      APP.partners.filterTab = 'all';
    }
    // Filter out hidden customers
    var visible = all.filter(function (item) {
      return !item.hidden;
    });
    if (tab === 'all') return visible;
    return visible.filter(function (item) {
      return getPartnerStatus(item) === tab;
    });
  }

  // Get all partners including hidden ones (for counts)
  function getAllPartnersIncludingHidden() {
    return APP.partners.items || [];
  }

  function getPartnerTabCounts() {
    var all = APP.partners.items || [];
    var counts = { all: 0, treating: 0, new: 0, inactive: 0, hidden: 0 };
    for (var i = 0; i < all.length; i++) {
      if (all[i].hidden) {
        counts.hidden = (counts.hidden || 0) + 1;
      } else {
        counts.all = (counts.all || 0) + 1;
        var s = getPartnerStatus(all[i]);
        counts[s] = (counts[s] || 0) + 1;
      }
    }
    return counts;
  }

  function renderPartners() {
    var el = document.getElementById('page-partners');
    if (!el) return;

    el.innerHTML =
      '<div class="partners-page">' +
      '<div class="partners-page-header">' +
      '<h2 class="partners-page-title">Khách hàng</h2>' +
      '<div class="partners-header-actions">' +
      '<button class="tds-btn partners-add-btn" id="partners-add-btn">' +
      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Thêm mới' +
      '</button>' +
      '</div>' +
      '</div>' +
      '<div class="tds-card partners-shell">' +
      '<div class="partners-filter-bar">' +
      '<div class="partners-tabs" id="partners-tabs"></div>' +
      '<div class="partners-search-wrap">' +
      '<svg class="partners-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' +
      '<input class="partners-search-input" id="partners-search" placeholder="Tìm theo tên, mã, điện thoại" value="' + escapeHtml(APP.partners.search || '') + '">' +
      '</div>' +
      '</div>' +
      '<div id="partners-table"></div>' +
      '<div class="partners-pagination" id="partners-pagination"></div>' +
      '</div>' +
      '</div>';

    var searchInput = document.getElementById('partners-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.partners.search = searchInput.value.trim();
        APP.partners.page = 1;
        loadPartnersData();
      }, 250));
    }

    var addBtn = document.getElementById('partners-add-btn');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        openCustomerModal(null);
      });
    }

    loadPartnersData();
  }

  function renderPartnersTabs() {
    var tabsWrap = document.getElementById('partners-tabs');
    if (!tabsWrap) return;
    var counts = getPartnerTabCounts();
    var tabs = [
      { key: 'all', label: 'Tất cả', count: counts.all },
      { key: 'treating', label: 'Đang điều trị', count: counts.treating },
      { key: 'new', label: 'Hoàn thành', count: counts.new },
      { key: 'inactive', label: 'Chưa phát sinh', count: counts.inactive },
    ];
    tabsWrap.innerHTML = tabs.map(function (t) {
      var active = APP.partners.filterTab === t.key ? ' partners-tab-active' : '';
      return '<button class="partners-tab' + active + '" data-tab="' + t.key + '">' +
        escapeHtml(t.label) + ' <span class="partners-tab-count">' + t.count + '</span></button>';
    }).join('');

    var btns = tabsWrap.querySelectorAll('.partners-tab');
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', function () {
        APP.partners.filterTab = this.getAttribute('data-tab');
        APP.partners.page = 1;
        renderPartnersTabs();
        renderPartnersTable();
        renderPartnersPagination();
      });
    }
  }

  async function loadPartnersData() {
    APP.partners.loading = true;
    APP.partners.requestId += 1;
    var requestId = APP.partners.requestId;
    renderPartnersTable();

    try {
      var query = toQueryString({
        search: APP.partners.search,
        limit: 200,
        offset: 0,
        companyId: getSelectedBranchId(),
      });
      var data = await api('/api/customers' + query);
      if (requestId !== APP.partners.requestId) return;
      APP.partners.items = safeItems(data);
      APP.partners.total = APP.partners.items.length;
    } catch (_err) {
      if (requestId !== APP.partners.requestId) return;
      APP.partners.items = [];
      APP.partners.total = 0;
    } finally {
      if (requestId === APP.partners.requestId) {
        APP.partners.loading = false;
        renderPartnersTabs();
        renderPartnersTable();
        renderPartnersPagination();
      }
    }
  }

  function renderPartnersTable() {
    var tableWrap = document.getElementById('partners-table');
    if (!tableWrap) return;

    if (APP.partners.loading) {
      tableWrap.innerHTML = renderLoadingState('Đang tải danh sách khách hàng...');
      return;
    }

    var filtered = getFilteredPartners();

    var pageSize = APP.partners.pageSize;
    var page = APP.partners.page;
    var start = (page - 1) * pageSize;
    var end = Math.min(start + pageSize, filtered.length);
    var rows = filtered.slice(start, end);

    // Calculate index for STT column based on current page
    var startIndex = start;

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table partners-table">' +
      '<thead><tr>' +
      '<th style="width:40px">STT</th>' +
      '<th>Thông tin khách hàng</th>' +
      '<th style="width:90px">Ngày sinh</th>' +
      '<th style="width:110px">Số điện thoại</th>' +
      '<th style="width:180px">Email</th>' +
      '<th style="width:100px">Ngày tạo</th>' +
      '<th style="width:80px">Thao tác</th>' +
      '</tr></thead>' +
      '<tbody>' +
      rows.map(function (item, idx) {
        var status = getPartnerStatus(item);
        var statusLabel = getPartnerStatusLabel(status);
        var statusClass = getPartnerStatusClass(status);
        var nameDisplay = item.name || item.displayName || 'N/A';
        var initials = getUserInitials(nameDisplay);
        var avatarColor = item.gender === 'male' ? '#1A6DE3' : item.gender === 'female' ? '#EC4899' : '#94A3B8';
        var ref = item.ref || item.code || '';
        var nameWithRef = ref ? nameDisplay + ' <span class="partners-cell-ref">(' + escapeHtml(ref) + ')</span>' : escapeHtml(nameDisplay);
        var genderIcon = item.gender === 'male' ? '<svg class="gender-icon gender-male" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' : item.gender === 'female' ? '<svg class="gender-icon gender-female" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' : '';
        var hasMemberCard = item.memberCard && item.memberCard !== '—';
        var hasCategory = item.categories && item.categories !== '—';
        var memberBadge = hasMemberCard ? '<span class="partners-badge partners-badge-blue">THẺ TV</span>' : '';
        var categoryBadge = hasCategory ? '<span class="partners-badge partners-badge-pink">Nhãn KH</span>' : '';
        var badges = [memberBadge, categoryBadge].filter(Boolean).join(' ');
        return (
          '<tr class="partners-row" data-id="' + escapeHtml(item.id || '') + '">' +
          '<td class="text-center">' + (startIndex + idx + 1) + '</td>' +
          '<td><div class="partners-name-cell">' +
          '<span class="partners-avatar-sm" style="background:' + avatarColor + '">' + escapeHtml(initials) + '</span>' +
          '<div class="partners-info-wrap">' +
          '<a href="#/partners/customers/' + encodeURIComponent(item.id || '') + '/overview" class="partners-name-link">' + nameWithRef + '</a>' +
          '<div class="partners-badges">' + genderIcon + badges + '</div>' +
          '</div></div></td>' +
          '<td>' + escapeHtml(formatDate(item.dateOfBirth)) + '</td>' +
          '<td>' + escapeHtml(item.phone || item.mobile || '—') + '</td>' +
          '<td>' + escapeHtml(item.email || '—') + '</td>' +
          '<td>' + escapeHtml(formatDate(item.createdAt || item.createDate)) + '</td>' +
          '<td onclick="event.stopPropagation()">' +
          '<div class="partners-actions">' +
          '<button class="db-icon-btn partners-action-edit" data-id="' + escapeHtml(item.id || '') + '" title="Sửa">' +
          '<svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>' +
          '</button>' +
          '<button class="db-icon-btn partners-action-view" data-id="' + escapeHtml(item.id || '') + '" title="Xem">' +
          '<svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>' +
          '</button>' +
          '<button class="db-icon-btn partners-action-delete" data-id="' + escapeHtml(item.id || '') + '" title="Xóa">' +
          '<svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>' +
          '</button>' +
          '</div>' +
          '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    // Click on name link navigates via hash, no extra JS needed
    // Click on row also navigates
    var rowEls = tableWrap.querySelectorAll('.partners-row');
    for (var k = 0; k < rowEls.length; k++) {
      rowEls[k].addEventListener('click', function (e) {
        if (e.target.tagName === 'A') return; // let link handle it
        if (e.target.closest('.partners-action-edit')) {
          var editId = e.target.closest('button').getAttribute('data-id');
          var editItem = (APP.partners.items || []).find(function (it) { return it.id === editId; });
          if (editItem) openCustomerModal(editItem);
          return;
        }
        if (e.target.closest('.partners-action-view')) {
          var viewId = e.target.closest('button').getAttribute('data-id');
          if (viewId) navigateTo('#/partners/customers/' + encodeURIComponent(viewId) + '/overview');
          return;
        }
        if (e.target.closest('.partners-action-delete')) {
          var delId = e.target.closest('button').getAttribute('data-id');
          if (delId) { tdsConfirm('Bạn có chắc muốn xóa khách hàng này?', { title: 'Xóa khách hàng' }).then(function (ok) { if (!ok) return;
            api('/api/customers/' + encodeURIComponent(delId), { method: 'DELETE' })
              .then(function () { loadPartnersData(); showToast('success', 'Đã xóa khách hàng.'); })
              .catch(function () { showToast('error', 'Xóa thất bại.'); });
          }); }
          return;
        }
        var id = this.getAttribute('data-id');
        if (id) navigateTo('#/partners/customers/' + encodeURIComponent(id) + '/overview');
      });
    }
  }

  function renderPartnersPagination() {
    var paginationWrap = document.getElementById('partners-pagination');
    if (!paginationWrap) return;

    var filtered = getFilteredPartners();
    var total = filtered.length;
    var pageSize = APP.partners.pageSize;
    var page = APP.partners.page;
    var totalPages = Math.max(1, Math.ceil(total / pageSize));
    var start = Math.min((page - 1) * pageSize + 1, total);
    var end = Math.min(page * pageSize, total);

    if (total === 0) {
      paginationWrap.innerHTML =
        '<div class="partners-pagination-left">' +
        '<select class="partners-pagesize-select" id="partners-pagesize">' +
        '<option value="20"' + (pageSize === 20 ? ' selected' : '') + '>20</option>' +
        '<option value="50"' + (pageSize === 50 ? ' selected' : '') + '>50</option>' +
        '<option value="100"' + (pageSize === 100 ? ' selected' : '') + '>100</option>' +
        '</select>' +
        '<span class="partners-pagesize-label">hàng trên trang</span>' +
        '</div>' +
        '<div class="partners-pagination-right">' +
        '<span>Hiển thị 0-0 / 0</span>' +
        '</div>';
      return;
    }

    var pageButtons = '';
    var maxVisible = 5;
    var startPage = Math.max(1, page - Math.floor(maxVisible / 2));
    var endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    pageButtons += '<button class="partners-page-btn' + (page <= 1 ? ' disabled' : '') + '" data-page="' + (page - 1) + '">&laquo;</button>';
    for (var i = startPage; i <= endPage; i++) {
      pageButtons += '<button class="partners-page-btn' + (i === page ? ' partners-page-active' : '') + '" data-page="' + i + '">' + i + '</button>';
    }
    pageButtons += '<button class="partners-page-btn' + (page >= totalPages ? ' disabled' : '') + '" data-page="' + (page + 1) + '">&raquo;</button>';

    paginationWrap.innerHTML =
      '<div class="partners-pagination-left">' +
      pageButtons +
      '<select class="partners-pagesize-select" id="partners-pagesize">' +
      '<option value="20"' + (pageSize === 20 ? ' selected' : '') + '>20</option>' +
      '<option value="50"' + (pageSize === 50 ? ' selected' : '') + '>50</option>' +
      '<option value="100"' + (pageSize === 100 ? ' selected' : '') + '>100</option>' +
      '</select>' +
      '<span class="partners-pagesize-label">hàng trên trang</span>' +
      '</div>' +
      '<div class="partners-pagination-right">' +
      '<span>Hiển thị ' + start + '-' + end + ' / ' + total + '</span>' +
      '</div>';

    var pageBtns = paginationWrap.querySelectorAll('.partners-page-btn');
    for (var j = 0; j < pageBtns.length; j++) {
      pageBtns[j].addEventListener('click', function () {
        if (this.classList.contains('disabled')) return;
        var p = parseInt(this.getAttribute('data-page'), 10);
        if (p >= 1 && p <= totalPages) {
          APP.partners.page = p;
          renderPartnersTable();
          renderPartnersPagination();
        }
      });
    }

    var pageSizeSelect = document.getElementById('partners-pagesize');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', function () {
        APP.partners.pageSize = parseInt(this.value, 10);
        APP.partners.page = 1;
        renderPartnersTable();
        renderPartnersPagination();
      });
    }
  }

  // ---------------------------------------------------------------------------
  // Phase 5: Customer Detail Page
  // ---------------------------------------------------------------------------
  async function renderCustomerDetail() {
    var el = document.getElementById('page-customer-detail');
    if (!el) return;
    var hashParts = (window.location.hash || '').split('/');
    var customerId = hashParts[3] ? decodeURIComponent(hashParts[3]) : null;
    if (!customerId) { navigateTo('#/partners'); return; }
    APP.customerDetail.id = customerId;
    APP.customerDetail.loading = true;
    APP.customerDetail.activeTab = 'info';
    el.innerHTML = '<div class="cdetail-page"><div class="cdetail-loading">' + renderLoadingState('Đang tải thông tin khách hàng...') + '</div></div>';
    try {
      var result = await Promise.all([
        api('/api/customers/' + encodeURIComponent(customerId)),
        api('/api/customers/' + encodeURIComponent(customerId) + '/appointments?limit=20&offset=0').catch(function () { return { items: [] }; }),
        api('/api/customers/' + encodeURIComponent(customerId) + '/treatments?limit=20&offset=0').catch(function () { return { items: [] }; }),
        api('/api/dot-khams' + toQueryString({ partnerId: customerId, companyId: getSelectedBranchId(), limit: 20, offset: 0 })).catch(function () { return { items: [] }; }),
        api('/api/payments' + toQueryString({ partnerId: customerId, companyId: getSelectedBranchId(), limit: 20, offset: 0 })).catch(function () { return { items: [] }; }),
      ]);
      APP.customerDetail.data = result[0] || {};
      APP.customerDetail.appointments = safeItems(result[1]);
      APP.customerDetail.treatments = safeItems(result[2]);
      APP.customerDetail.exams = safeItems(result[3]);
      APP.customerDetail.payments = safeItems(result[4]);
      // Also fetch images in parallel (non-blocking)
      APP.customerDetail.images = [];
      api('/api/customers/' + encodeURIComponent(customerId) + '/images?limit=100&offset=0').then(function (imgData) {
        APP.customerDetail.images = safeItems(imgData);
      }).catch(function () { APP.customerDetail.images = []; });
      APP.customerDetail.loading = false;
      buildCustomerDetailDOM(el);
    } catch (err) {
      APP.customerDetail.loading = false;
      el.innerHTML = '<div class="cdetail-page"><div class="cdetail-header-bar"><button class="cdetail-back-btn" id="cdetail-back"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg></button><div class="cdetail-breadcrumb">Khách hàng</div></div>' + renderEmptyState('Không thể tải thông tin khách hàng') + '</div>';
      var bb = document.getElementById('cdetail-back');
      if (bb) bb.addEventListener('click', function () { navigateTo('#/partners'); });
    }
  }

  function buildCustomerDetailDOM(el) {
    var d = APP.customerDetail.data || {};
    var nameDisplay = d.name || d.displayName || 'Khách hàng';
    var initials = getUserInitials(nameDisplay);
    var refDisplay = d.ref ? '[' + d.ref + '] ' : '';
    var totalRevenue = Number(d.amountRevenueTotal || 0);
    var totalDebt = Number(d.totalDebit || 0);
    var visitCount = (APP.customerDetail.exams || []).length;
    var h = '';
    h += '<div class="cdetail-page">';
    h += '<div class="cdetail-header-bar"><button class="cdetail-back-btn" id="cdetail-back"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg></button>';
    h += '<div class="cdetail-breadcrumb"><a href="#/partners" class="cdetail-breadcrumb-link">Khách hàng</a> <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg> <span>' + escapeHtml(refDisplay + nameDisplay) + '</span></div></div>';
    h += '<h3 class="cdetail-page-title">Thông tin khách hàng ' + escapeHtml(nameDisplay) + '</h3>';
    h += '<div class="cdetail-patient-header"><div class="cdetail-patient-info"><div class="cdetail-avatar">' + escapeHtml(initials) + '</div>';
    h += '<div class="cdetail-patient-meta"><h2 class="cdetail-patient-name">' + escapeHtml(refDisplay + nameDisplay) + '</h2>';
    h += '<div class="cdetail-patient-details">';
    if (d.phone) h += '<span class="cdetail-meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.81.36 1.6.7 2.35a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.74.33 1.54.57 2.35.7A2 2 0 0 1 22 16.92z"/></svg> ' + escapeHtml(d.phone) + '</span>';
    var genderDisplay = d.gender === 'female' ? 'Nữ' : d.gender === 'male' ? 'Nam' : d.gender || '';
    if (genderDisplay) h += '<span class="cdetail-meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> ' + escapeHtml(genderDisplay) + '</span>';
    if (d.categories) h += '<span class="cdetail-meta-item cdetail-tag">' + escapeHtml(d.categories) + '</span>';
    h += '</div>';
    h += '<div class="cdetail-loyalty"><span class="cdetail-loyalty-label">Điểm tích lũy</span><span class="cdetail-loyalty-value">' + (d.loyaltyPoints || 0) + '</span></div>';
    h += '</div></div>';
    h += '<div class="cdetail-patient-actions"><button class="tds-btn tds-btn-icon tds-btn-secondary tds-btn-sm" id="cdetail-print-btn" title="In"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg></button> <button class="tds-btn tds-btn-icon tds-btn-secondary tds-btn-sm" id="cdetail-edit-btn" title="Sửa"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></button> <button class="tds-btn tds-btn-primary cdetail-add-treatment-btn" id="cdetail-add-treatment">+ Thêm phiếu điều trị</button></div></div>';
    h += '<div class="cdetail-metrics">';
    var expectedRevenue = Number(d.amountTreatmentTotal || 0) - Number(d.amountRevenueTotal || totalRevenue || 0);
    if (expectedRevenue < 0) expectedRevenue = 0;
    h += '<div class="cdetail-metric-card cdetail-metric-blue"><div class="cdetail-metric-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div><div class="cdetail-metric-label">Tổng tiền điều trị</div><div class="cdetail-metric-value">' + escapeHtml(formatCurrency(d.amountTreatmentTotal || 0)) + '</div></div>';
    h += '<div class="cdetail-metric-card cdetail-metric-orange"><div class="cdetail-metric-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div><div class="cdetail-metric-label">Dự kiến thu</div><div class="cdetail-metric-value">' + escapeHtml(formatCurrency(expectedRevenue)) + '</div></div>';
    h += '<div class="cdetail-metric-card cdetail-metric-green"><div class="cdetail-metric-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg></div><div class="cdetail-metric-label">Doanh thu</div><div class="cdetail-metric-value">' + escapeHtml(formatCurrency(totalRevenue)) + '</div></div>';
    h += '<div class="cdetail-metric-card cdetail-metric-red"><div class="cdetail-metric-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div><div class="cdetail-metric-label">Công nợ</div><div class="cdetail-metric-value">' + escapeHtml(formatCurrency(totalDebt)) + '</div></div>';
    h += '<div class="cdetail-metric-card cdetail-metric-purple"><div class="cdetail-metric-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg></div><div class="cdetail-metric-label">Tạm ứng</div><div class="cdetail-metric-value">' + escapeHtml(formatCurrency(d.advanceBalance || 0)) + '</div></div>';
    h += '<div class="cdetail-metric-card cdetail-metric-cyan"><div class="cdetail-metric-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div><div class="cdetail-metric-label">Điểm tích lũy</div><div class="cdetail-metric-value">' + (d.loyaltyPoints || 0) + '</div></div>';
    h += '</div>';
    h += '<div class="cdetail-main"><div class="cdetail-content">';
    h += '<div class="cdetail-tabs" id="cdetail-tabs">';
    var tabList = [['info','Thông tin'],['appointments','Cuộc hẹn'],['treatments','Điều trị'],['prescriptions','Đơn thuốc'],['images','Hình ảnh'],['payments','Phiếu thu chi'],['debt','Công nợ'],['notes','Ghi chú'],['teeth','Sơ đồ răng'],['history','Lịch sử']];
    for (var ti = 0; ti < tabList.length; ti++) {
      h += '<button class="cdetail-tab' + (ti === 0 ? ' cdetail-tab-active' : '') + '" data-ctab="' + tabList[ti][0] + '">' + tabList[ti][1] + '</button>';
    }
    h += '</div><div class="cdetail-tab-panels" id="cdetail-panels"></div></div>';
    h += '<div class="cdetail-sidebar"><div class="cdetail-sidebar-header"><button class="cdetail-sidebar-tab cdetail-sidebar-tab-active">Lịch sử</button><button class="cdetail-sidebar-tab">Công việc</button><button class="cdetail-sidebar-tab">Ghi chú</button></div>';
    h += '<div class="cdetail-sidebar-filter"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg> <span>Lọc</span></div>';
    h += '<div class="cdetail-timeline" id="cdetail-timeline"></div></div></div></div>';
    el.innerHTML = h;
    var backBtn = document.getElementById('cdetail-back');
    if (backBtn) backBtn.addEventListener('click', function () { navigateTo('#/partners'); });
    var editBtn = document.getElementById('cdetail-edit-btn');
    if (editBtn) editBtn.addEventListener('click', function () { openCustomerModal(APP.customerDetail.data); });
    var printBtn = document.getElementById('cdetail-print-btn');
    if (printBtn) printBtn.addEventListener('click', function () { window.print(); });
    var addTreatmentBtn = document.getElementById('cdetail-add-treatment');
    if (addTreatmentBtn) addTreatmentBtn.addEventListener('click', function () { openTreatmentPlanModal(APP.customerDetail.data); });
    var tabBtns = document.querySelectorAll('.cdetail-tab');
    for (var i = 0; i < tabBtns.length; i++) {
      tabBtns[i].addEventListener('click', function () {
        APP.customerDetail.activeTab = this.getAttribute('data-ctab');
        var allTabs = document.querySelectorAll('.cdetail-tab');
        for (var j = 0; j < allTabs.length; j++) allTabs[j].classList.toggle('cdetail-tab-active', allTabs[j] === this);
        renderCDTabContent();
      });
    }
    renderCDTabContent();
    renderCDTimeline();
  }

  function renderCDTabContent() {
    var panel = document.getElementById('cdetail-panels');
    if (!panel) return;
    var tab = APP.customerDetail.activeTab;
    var d = APP.customerDetail.data || {};
    var treatments = APP.customerDetail.treatments || [];
    var appointments = APP.customerDetail.appointments || [];
    var payments = APP.customerDetail.payments || [];

    // ---- Tab 1: Thong tin (Info) ----
    if (tab === 'info') {
      var genderDisplay = d.gender === 'female' ? 'N\u1eef' : d.gender === 'male' ? 'Nam' : d.gender || '\u2014';
      var ih = '<h3 class="cdetail-section-title">Th\u00f4ng tin c\u01a1 b\u1ea3n</h3>';
      ih += '<div class="cdetail-info-grid">';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">M\u00e3 kh\u00e1ch h\u00e0ng</div><div class="cdetail-info-value">' + escapeHtml(d.ref || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">H\u1ecd v\u00e0 t\u00ean</div><div class="cdetail-info-value">' + escapeHtml(d.name || d.displayName || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">S\u1ed1 \u0111i\u1ec7n tho\u1ea1i</div><div class="cdetail-info-value">' + escapeHtml(d.phone || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">Email</div><div class="cdetail-info-value">' + escapeHtml(d.email || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">Gi\u1edbi t\u00ednh</div><div class="cdetail-info-value">' + escapeHtml(genderDisplay) + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">Ng\u00e0y sinh</div><div class="cdetail-info-value">' + escapeHtml(formatDate(d.dateOfBirth || d.birthDate || d.dob) || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">Nh\u00f3m kh\u00e1ch h\u00e0ng</div><div class="cdetail-info-value">' + escapeHtml(d.categories || d.partnerCategory || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">Ngu\u1ed3n</div><div class="cdetail-info-value">' + escapeHtml(d.source || d.partnerSource || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item cdetail-info-full"><div class="cdetail-info-label">\u0110\u1ecba ch\u1ec9</div><div class="cdetail-info-value">' + escapeHtml(d.address || d.street || '\u2014') + '</div></div>';
      ih += '<div class="cdetail-info-item cdetail-info-full"><div class="cdetail-info-label">Ghi ch\u00fa</div><div class="cdetail-info-value">' + escapeHtml(d.comment || d.notes || d.note || '\u2014') + '</div></div>';
      ih += '</div>';
      ih += '<h3 class="cdetail-section-title" style="margin-top:20px">T\u1ed5ng quan t\u00e0i ch\u00ednh</h3>';
      ih += '<div class="cdetail-info-grid">';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">T\u1ed5ng ti\u1ec1n \u0111i\u1ec1u tr\u1ecb</div><div class="cdetail-info-value">' + escapeHtml(formatCurrency(d.amountTreatmentTotal || 0)) + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">Doanh thu</div><div class="cdetail-info-value">' + escapeHtml(formatCurrency(d.amountRevenueTotal || 0)) + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">C\u00f4ng n\u1ee3</div><div class="cdetail-info-value" style="color:#EF4444;font-weight:600">' + escapeHtml(formatCurrency(d.totalDebit || 0)) + '</div></div>';
      ih += '<div class="cdetail-info-item"><div class="cdetail-info-label">\u0110i\u1ec3m t\u00edch l\u0169y</div><div class="cdetail-info-value">' + (d.loyaltyPoints || 0) + '</div></div>';
      ih += '</div>';
      panel.innerHTML = ih;

    // ---- Tab 2: Cuoc hen (Appointments) ----
    } else if (tab === 'appointments') {
      if (appointments.length) {
        var stateMap = { draft: 'Nh\u00e1p', confirmed: 'X\u00e1c nh\u1eadn', done: 'Ho\u00e0n th\u00e0nh', cancel: 'H\u1ee7y', arrived: '\u0110\u00e3 \u0111\u1ebfn', waiting: 'Ch\u1edd kh\u00e1m', examining: '\u0110ang kh\u00e1m' };
        panel.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ng\u00e0y h\u1eb9n</th><th>Gi\u1edd</th><th>B\u00e1c s\u0129</th><th>Tr\u1ea1ng th\u00e1i</th><th>Ghi ch\u00fa</th></tr></thead><tbody>' +
          appointments.map(function (a) {
            var dt = a.appointmentDate || a.date || '';
            var timeStr = dt.length > 10 ? dt.slice(11, 16) : (a.time || '\u2014');
            var stateLabel = stateMap[a.state || a.status] || a.state || a.status || '\u2014';
            var badgeClass = (a.state === 'done' || a.status === 'done') ? 'partners-badge-green' : (a.state === 'cancel') ? 'partners-badge-red' : (a.state === 'confirmed') ? 'partners-badge-blue' : 'partners-badge-orange';
            return '<tr><td>' + escapeHtml(formatDate(dt)) + '</td><td>' + escapeHtml(timeStr) + '</td><td>' + escapeHtml(a.doctorName || '\u2014') + '</td><td><span class="partners-badge ' + badgeClass + '">' + escapeHtml(stateLabel) + '</span></td><td>' + escapeHtml(a.notes || a.note || '\u2014') + '</td></tr>';
          }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 cu\u1ed9c h\u1eb9n'); }

    // ---- Tab 3: Dieu tri (Treatments) ----
    } else if (tab === 'treatments') {
      var toolbarHtml = '<div class="cdetail-overview-toolbar"><h3 class="cdetail-section-title">L\u1ecbch s\u1eed \u0111i\u1ec1u tr\u1ecb</h3><div class="cdetail-toolbar-actions"><button class="cdetail-toolbar-btn cdetail-toolbar-btn-active" title="Danh s\u00e1ch"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg></button><button class="cdetail-toolbar-btn" title="Xu\u1ea5t"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button><span class="cdetail-toolbar-sep"></span><span class="cdetail-toolbar-link">In h\u1ed3 s\u01a1 \u0111i\u1ec1u tr\u1ecb</span></div></div>';
      if (treatments.length) {
        panel.innerHTML = toolbarHtml + '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ng\u00e0y</th><th>D\u1ecbch v\u1ee5</th><th>S\u1ed1 l\u01b0\u1ee3ng</th><th>Th\u00e0nh ti\u1ec1n</th><th>Thanh to\u00e1n</th><th>C\u00f2n l\u1ea1i</th><th>R\u0103ng & ch\u1ea9n \u0111o\u00e1n</th><th>B\u00e1c s\u0129</th><th>Tr\u1ea1ng th\u00e1i</th></tr></thead><tbody>' +
          treatments.map(function (t) {
            var lines = safeItems(t.lines || t.lineItems || []);
            var sn = lines.length ? (lines[0].name || lines[0].productName || '\u2014') : '\u2014';
            var qtyDisplay = lines.length ? ((lines[0].quantity || 0) + (lines[0].teethCount ? ' R\u0103ng' : '')) : '\u2014';
            var teethInfo = (t.teeth || t.toothDiagnosis || '---');
            var soRef = t.name || t.ref || '';
            return '<tr><td><div>' + escapeHtml(formatDate(t.date || t.orderDate || t.createdAt)) + '</div>' + (soRef ? '<div class="cdetail-so-link">' + escapeHtml(soRef) + '</div>' : '') + '</td><td>' + escapeHtml(sn) + '</td><td>' + escapeHtml(qtyDisplay) + '</td><td class="text-right">' + escapeHtml(formatCurrency(t.totalAmount || t.amountTotal || 0)) + '</td><td class="text-right">' + escapeHtml(formatCurrency(t.paidAmount || t.amountPaid || 0)) + '</td><td class="text-right">' + escapeHtml(formatCurrency((t.totalAmount || t.amountTotal || 0) - (t.paidAmount || t.amountPaid || 0))) + '</td><td>' + escapeHtml(teethInfo) + '</td><td>' + escapeHtml(t.doctorName || '\u2014') + '</td><td><span class="partners-badge partners-badge-blue">' + escapeHtml(t.state || t.status || '\u2014') + '</span></td></tr>';
          }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = toolbarHtml + renderEmptyState('Ch\u01b0a c\u00f3 phi\u1ebfu \u0111i\u1ec1u tr\u1ecb'); }

    // ---- Tab 4: Don thuoc (Prescriptions) ----
    } else if (tab === 'prescriptions') {
      panel.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 d\u1eef li\u1ec7u \u0111\u01a1n thu\u1ed1c');

    // ---- Tab 5: Hinh anh (Images) ----
    } else if (tab === 'images') {
      var images = APP.customerDetail.images || [];
      if (images.length) {
        var imgHtml = '<h3 class="cdetail-section-title">H\u00ecnh \u1ea3nh b\u1ec7nh nh\u00e2n</h3><div class="cdetail-images-grid">';
        images.forEach(function (img) {
          var src = img.url || img.imageUrl || img.filePath || '';
          var caption = img.name || img.description || img.caption || '';
          var dateStr = formatDate(img.date || img.createdAt || '');
          imgHtml += '<div class="cdetail-image-card">';
          if (src) {
            imgHtml += '<img src="' + escapeHtml(src) + '" alt="' + escapeHtml(caption) + '" class="cdetail-image-thumb" onerror="this.style.display=\'none\'">';
          } else {
            imgHtml += '<div class="cdetail-image-placeholder"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg></div>';
          }
          imgHtml += '<div class="cdetail-image-info"><div class="cdetail-image-caption">' + escapeHtml(caption || 'H\u00ecnh \u1ea3nh') + '</div>';
          if (dateStr) imgHtml += '<div class="cdetail-image-date">' + escapeHtml(dateStr) + '</div>';
          imgHtml += '</div></div>';
        });
        imgHtml += '</div>';
        panel.innerHTML = imgHtml;
      } else {
        panel.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 h\u00ecnh \u1ea3nh');
      }

    // ---- Tab 6: Phieu thu chi (Receipts/Payments) ----
    } else if (tab === 'payments') {
      if (payments.length) {
        var totalIn = 0, totalOut = 0;
        payments.forEach(function (p) {
          var amt = Number(p.amount || 0);
          if (p.paymentType === 'inbound' || p.paymentType === 'thu') totalIn += amt;
          else totalOut += amt;
        });
        var summaryHtml = '<div class="cdetail-info-grid" style="margin-bottom:12px">' +
          '<div class="cdetail-info-item"><div class="cdetail-info-label">T\u1ed5ng thu</div><div class="cdetail-info-value" style="color:#10B981;font-weight:600">' + escapeHtml(formatCurrency(totalIn)) + '</div></div>' +
          '<div class="cdetail-info-item"><div class="cdetail-info-label">T\u1ed5ng chi</div><div class="cdetail-info-value" style="color:#EF4444;font-weight:600">' + escapeHtml(formatCurrency(totalOut)) + '</div></div>' +
          '</div>';
        panel.innerHTML = summaryHtml + '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ng\u00e0y</th><th>Lo\u1ea1i</th><th class="text-right">S\u1ed1 ti\u1ec1n</th><th>S\u1ed5 qu\u1ef9</th><th>Ghi ch\u00fa</th><th>Tr\u1ea1ng th\u00e1i</th></tr></thead><tbody>' +
          payments.map(function (p) {
            return '<tr><td>' + escapeHtml(formatDate(p.date || p.createdAt)) + '</td><td>' + escapeHtml(normalizePaymentTypeLabel(p.paymentType)) + '</td><td class="text-right">' + escapeHtml(formatCurrency(p.amount || 0)) + '</td><td>' + escapeHtml(p.journalName || '\u2014') + '</td><td>' + escapeHtml(p.memo || p.communication || p.notes || '\u2014') + '</td><td><span class="tds-badge ' + stateBadgeClass(p.state) + '">' + escapeHtml(translateState(p.state)) + '</span></td></tr>';
          }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 phi\u1ebfu thu chi'); }

    // ---- Tab 7: Cong no (Debt) ----
    } else if (tab === 'debt') {
      var debts = APP.customerDetail.debts || [];
      var totalDebtAmt = Number(d.totalDebit || 0);
      var totalCreditAmt = Number(d.amountRevenueTotal || 0);
      var balance = totalDebtAmt;
      var debtHtml = '<div class="cdetail-info-grid" style="margin-bottom:12px">' +
        '<div class="cdetail-info-item"><div class="cdetail-info-label">T\u1ed5ng c\u00f4ng n\u1ee3 hi\u1ec7n t\u1ea1i</div><div class="cdetail-info-value" style="color:#EF4444;font-weight:700;font-size:18px">' + escapeHtml(formatCurrency(totalDebtAmt)) + '</div></div>' +
        '<div class="cdetail-info-item"><div class="cdetail-info-label">T\u1ed5ng \u0111\u00e3 thanh to\u00e1n</div><div class="cdetail-info-value" style="color:#10B981;font-weight:600">' + escapeHtml(formatCurrency(totalCreditAmt)) + '</div></div>' +
        '</div>';
      // Build debt ledger from treatments and payments
      var debtRows = [];
      treatments.forEach(function (t) { debtRows.push({ date: t.date || t.orderDate || t.createdAt || '', desc: 'Phi\u1ebfu \u0111i\u1ec1u tr\u1ecb: ' + (t.name || t.ref || ''), debit: Number(t.totalAmount || t.amountTotal || 0), credit: 0 }); });
      payments.forEach(function (p) { debtRows.push({ date: p.date || p.createdAt || '', desc: 'Thanh to\u00e1n: ' + (p.name || p.ref || normalizePaymentTypeLabel(p.paymentType)), debit: 0, credit: Number(p.amount || 0) }); });
      debtRows.sort(function (a, b) { return (a.date || '').localeCompare(b.date || ''); });
      if (debtRows.length) {
        var runBal = 0;
        debtHtml += '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ng\u00e0y</th><th>Di\u1ec5n gi\u1ea3i</th><th class="text-right">N\u1ee3 (Debit)</th><th class="text-right">C\u00f3 (Credit)</th><th class="text-right">S\u1ed1 d\u01b0</th></tr></thead><tbody>' +
          debtRows.map(function (r) {
            runBal += r.debit - r.credit;
            return '<tr><td>' + escapeHtml(formatDate(r.date)) + '</td><td>' + escapeHtml(r.desc) + '</td><td class="text-right">' + (r.debit ? escapeHtml(formatCurrency(r.debit)) : '---') + '</td><td class="text-right">' + (r.credit ? escapeHtml(formatCurrency(r.credit)) : '---') + '</td><td class="text-right" style="' + (runBal > 0 ? 'color:#EF4444' : 'color:#10B981') + '">' + escapeHtml(formatCurrency(runBal)) + '</td></tr>';
          }).join('') + '</tbody></table></div>';
      } else {
        debtHtml += renderEmptyState('Ch\u01b0a c\u00f3 d\u1eef li\u1ec7u c\u00f4ng n\u1ee3');
      }
      panel.innerHTML = debtHtml;

    // ---- Tab 8: Ghi chu (Notes) ----
    } else if (tab === 'notes') {
      var noteText = d.comment || d.notes || d.note || '';
      var nh = '<h3 class="cdetail-section-title">Ghi ch\u00fa kh\u00e1ch h\u00e0ng</h3>';
      nh += '<div class="cdetail-notes-area">';
      if (noteText) {
        nh += '<div class="cdetail-note-content" style="white-space:pre-wrap;padding:12px;background:var(--tds-bg-secondary,#f8fafc);border-radius:8px;font-size:14px;color:var(--tds-text-primary,#1e293b)">' + escapeHtml(noteText) + '</div>';
      } else {
        nh += renderEmptyState('Ch\u01b0a c\u00f3 ghi ch\u00fa');
      }
      nh += '</div>';
      panel.innerHTML = nh;

    // ---- Tab 9: So do rang (Dental Chart) ----
    } else if (tab === 'teeth') {
      panel.innerHTML = renderDentalChartSVG(treatments);
      setTimeout(function () { bindEnhancedDentalChartClicks(treatments); }, 0);

    // ---- Tab 10: Lich su (History) ----
    } else if (tab === 'history') {
      var histEvents = [];
      (APP.customerDetail.treatments || []).forEach(function (t) {
        histEvents.push({ date: t.date || t.orderDate || t.createdAt || '', type: 'treatment', title: 'Phi\u1ebfu \u0111i\u1ec1u tr\u1ecb', desc: (t.name || t.ref || '') + ' - ' + formatCurrency(t.totalAmount || t.amountTotal || 0), author: t.createdBy || t.doctorName || '' });
      });
      (APP.customerDetail.payments || []).forEach(function (p) {
        histEvents.push({ date: p.date || p.createdAt || '', type: 'payment', title: 'Thanh to\u00e1n', desc: formatCurrency(p.amount || 0), author: p.createdBy || '' });
      });
      (APP.customerDetail.appointments || []).forEach(function (a) {
        histEvents.push({ date: a.appointmentDate || a.date || a.createdAt || '', type: 'appointment', title: 'L\u1ecbch h\u1eb9n', desc: (a.doctorName ? 'BS: ' + a.doctorName : '') + (a.notes || a.note ? ' - ' + (a.notes || a.note) : ''), author: a.createdBy || '' });
      });
      (APP.customerDetail.exams || []).forEach(function (e) {
        histEvents.push({ date: e.date || e.examDate || e.createdAt || '', type: 'exam', title: '\u0110\u1ee3t kh\u00e1m', desc: e.diagnosis || e.reason || '', author: e.doctorName || e.createdBy || '' });
      });
      histEvents.sort(function (a, b) { return (b.date || '').localeCompare(a.date || ''); });
      if (!histEvents.length) {
        panel.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 l\u1ecbch s\u1eed ho\u1ea1t \u0111\u1ed9ng');
      } else {
        var histGrouped = {};
        histEvents.forEach(function (ev) { var dk = (ev.date || '').slice(0, 10) || 'unknown'; if (!histGrouped[dk]) histGrouped[dk] = []; histGrouped[dk].push(ev); });
        var hh = '<h3 class="cdetail-section-title">L\u1ecbch s\u1eed ho\u1ea1t \u0111\u1ed9ng</h3>';
        Object.keys(histGrouped).sort(function (a, b) { return b.localeCompare(a); }).forEach(function (dk) {
          var dayLabel = dk === new Date().toISOString().slice(0, 10) ? 'H\u00f4m nay' : formatDate(dk);
          hh += '<div class="cdetail-timeline-group"><div class="cdetail-timeline-date">' + escapeHtml(dayLabel) + '</div>';
          histGrouped[dk].forEach(function (ev) {
            var ic = ev.type === 'payment' ? '#8B5CF6' : ev.type === 'treatment' ? '#1A6DE3' : ev.type === 'exam' ? '#10B981' : '#F59E0B';
            hh += '<div class="cdetail-timeline-item"><div class="cdetail-timeline-dot" style="background:' + ic + '"></div><div class="cdetail-timeline-content"><div class="cdetail-timeline-time">' + escapeHtml((ev.date || '').slice(11, 16) || '') + '</div><div class="cdetail-timeline-title">' + escapeHtml(ev.title) + '</div><div class="cdetail-timeline-desc">' + escapeHtml(ev.desc) + '</div>' + (ev.author ? '<div class="cdetail-timeline-author">Ng\u01b0\u1eddi th\u1ef1c hi\u1ec7n: ' + escapeHtml(ev.author) + '</div>' : '') + '</div></div>';
          });
          hh += '</div>';
        });
        panel.innerHTML = hh;
      }

    // ---- Fallback ----
    } else {
      panel.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 d\u1eef li\u1ec7u');
    }
  }

  // ---------------------------------------------------------------------------
  // Dental Chart SVG (Tab 9 - So do rang)
  // ---------------------------------------------------------------------------
  function renderDentalChartSVG(treatmentRows) {
    var treatedTeeth = {};
    for (var ci = 0; ci < treatmentRows.length; ci++) {
      var clines = safeItems(treatmentRows[ci].lines || treatmentRows[ci].lineItems || []);
      for (var cj = 0; cj < clines.length; cj++) {
        var rawTeeth = String(clines[cj].teeth || clines[cj].toothNumber || '').split(/[,;\s]+/).filter(Boolean);
        for (var ck = 0; ck < rawTeeth.length; ck++) {
          var tnum = parseInt(rawTeeth[ck], 10);
          if (tnum >= 11 && tnum <= 48) {
            if (!treatedTeeth[tnum]) treatedTeeth[tnum] = [];
            treatedTeeth[tnum].push({ product: clines[cj].productName || clines[cj].name || 'D\u1ecbch v\u1ee5', state: treatmentRows[ci].state || 'done', date: treatmentRows[ci].date || treatmentRows[ci].orderDate || '' });
          }
        }
      }
    }
    if (!APP.customerDetail._toothState) APP.customerDetail._toothState = {};
    var toothState = APP.customerDetail._toothState;

    var CONDITIONS = [
      { key: 'normal', label: 'B\u00ecnh th\u01b0\u1eddng', color: '#E2E8F0' },
      { key: 'treated', label: '\u0110\u00e3 \u0111i\u1ec1u tr\u1ecb', color: '#1A6DE3' },
      { key: 'cavity', label: 'S\u00e2u r\u0103ng', color: '#EF4444' },
      { key: 'filling', label: 'Tr\u00e1m', color: '#3B82F6' },
      { key: 'crown', label: 'B\u1ecdc r\u0103ng s\u1ee9', color: '#F59E0B' },
      { key: 'extraction', label: 'Nh\u1ed5', color: '#6B7280' },
      { key: 'implant', label: 'Implant', color: '#8B5CF6' },
      { key: 'rootcanal', label: 'L\u1ea5y t\u1ee7y', color: '#EC4899' },
      { key: 'missing', label: 'M\u1ea5t r\u0103ng', color: '#1F2937' }
    ];

    var UPPER = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28];
    var LOWER = [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38];
    var toothW = 34, toothH = 44, gap = 4, padX = 24, padY = 28;
    var totalW = UPPER.length * (toothW + gap) - gap + padX * 2;
    var svgH = 2 * toothH + 100 + padY * 2;
    var midX = totalW / 2;

    function getToothColor(tn) {
      if (toothState[tn]) {
        var c = CONDITIONS.find(function (cc) { return cc.key === toothState[tn]; });
        return c ? c.color : '#E2E8F0';
      }
      if (treatedTeeth[tn]) return '#1A6DE3';
      return '#E2E8F0';
    }

    var svg = '<svg class="dental-chart-svg" viewBox="0 0 ' + totalW + ' ' + svgH + '" xmlns="http://www.w3.org/2000/svg">';
    svg += '<rect width="' + totalW + '" height="' + svgH + '" fill="var(--tds-card-bg, #fff)" rx="8"/>';
    svg += '<text x="' + midX + '" y="' + (padY - 4) + '" text-anchor="middle" font-size="12" font-weight="600" fill="#64748B" font-family="Inter,sans-serif">H\u00c0M TR\u00caN</text>';
    svg += '<line x1="' + midX + '" y1="' + padY + '" x2="' + midX + '" y2="' + (padY + toothH + 20) + '" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="3,3"/>';

    function renderRow(teeth, startY, isUpper) {
      var s = '';
      for (var i = 0; i < teeth.length; i++) {
        var tn = teeth[i];
        var tx = padX + i * (toothW + gap);
        var fill = getToothColor(tn);
        var isTr = treatedTeeth[tn] || (toothState[tn] && toothState[tn] !== 'normal');
        var stroke = isTr ? '#1557b0' : '#94A3B8';
        var textFill = (fill === '#E2E8F0') ? '#475569' : '#fff';
        s += '<g class="dental-tooth-g" data-tooth="' + tn + '" style="cursor:pointer">';
        s += '<rect x="' + tx + '" y="' + startY + '" width="' + toothW + '" height="' + toothH + '" rx="5" fill="' + fill + '" stroke="' + stroke + '" stroke-width="1.5"/>';
        if (isUpper) {
          s += '<line x1="' + (tx + toothW / 2) + '" y1="' + (startY + toothH) + '" x2="' + (tx + toothW / 2) + '" y2="' + (startY + toothH + 10) + '" stroke="#94A3B8" stroke-width="1"/>';
        } else {
          s += '<line x1="' + (tx + toothW / 2) + '" y1="' + startY + '" x2="' + (tx + toothW / 2) + '" y2="' + (startY - 10) + '" stroke="#94A3B8" stroke-width="1"/>';
        }
        s += '<text x="' + (tx + toothW / 2) + '" y="' + (startY + toothH / 2 + 5) + '" text-anchor="middle" font-size="11" font-weight="600" fill="' + textFill + '" font-family="Inter,sans-serif">' + tn + '</text>';
        var numY = isUpper ? (startY + toothH + 22) : (startY - 14);
        s += '<text x="' + (tx + toothW / 2) + '" y="' + numY + '" text-anchor="middle" font-size="9" fill="#94A3B8" font-family="Inter,sans-serif">' + tn + '</text>';
        if (treatedTeeth[tn]) { s += '<title>R\u0103ng ' + tn + ': ' + treatedTeeth[tn].map(function (ti) { return ti.product; }).join(', ') + '</title>'; }
        s += '</g>';
      }
      return s;
    }

    var upperStartY = padY + 8;
    svg += renderRow(UPPER, upperStartY, true);
    var jawSepY = upperStartY + toothH + 34;
    svg += '<line x1="' + padX + '" y1="' + jawSepY + '" x2="' + (totalW - padX) + '" y2="' + jawSepY + '" stroke="#CBD5E1" stroke-width="1"/>';
    svg += '<text x="' + midX + '" y="' + (jawSepY + 16) + '" text-anchor="middle" font-size="12" font-weight="600" fill="#64748B" font-family="Inter,sans-serif">H\u00c0M D\u01af\u1edcI</text>';
    svg += '<line x1="' + midX + '" y1="' + (jawSepY + 20) + '" x2="' + midX + '" y2="' + (jawSepY + 20 + toothH + 10) + '" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="3,3"/>';
    var lowerStartY = jawSepY + 30;
    svg += renderRow(LOWER, lowerStartY, false);
    svg += '</svg>';

    var html = '<div class="cdetail-overview-toolbar"><h3 class="cdetail-section-title">S\u01a1 \u0111\u1ed3 r\u0103ng</h3></div>';
    // Legend
    html += '<div class="cdetail-dental-legend" style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px;padding:0 4px">';
    CONDITIONS.forEach(function (c) {
      html += '<span style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:#64748B"><span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:' + c.color + ';border:1px solid rgba(0,0,0,0.1)"></span>' + c.label + '</span>';
    });
    html += '</div>';
    // Condition selector
    html += '<div id="dental-selector" style="display:none;background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px;margin-bottom:16px;box-shadow:0 4px 12px rgba(0,0,0,0.1)">';
    html += '<div id="dental-selector-title" style="font-weight:600;margin-bottom:8px;color:#1e293b">R\u0103ng #</div>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:6px">';
    CONDITIONS.forEach(function (c) {
      html += '<button class="dental-cond-btn" data-cond="' + c.key + '" style="padding:4px 10px;border:1px solid #e2e8f0;border-left:3px solid ' + c.color + ';border-radius:4px;background:#fff;cursor:pointer;font-size:12px;transition:background 0.15s">' + c.label + '</button>';
    });
    html += '<button id="dental-close-btn" style="padding:4px 10px;border:1px solid #e2e8f0;border-radius:4px;background:#f8fafc;cursor:pointer;font-size:12px">\u0110\u00f3ng</button>';
    html += '</div></div>';
    html += '<div class="dental-chart-wrapper" style="overflow-x:auto">' + svg + '</div>';

    // Detail table for treated teeth
    var treatedKeys = Object.keys(treatedTeeth);
    if (treatedKeys.length) {
      html += '<h4 class="cdetail-section-title" style="margin-top:16px">Chi ti\u1ebft \u0111i\u1ec1u tr\u1ecb theo r\u0103ng (' + treatedKeys.length + ' r\u0103ng)</h4>';
      html += '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>R\u0103ng</th><th>D\u1ecbch v\u1ee5</th><th>Ng\u00e0y</th><th>Tr\u1ea1ng th\u00e1i</th></tr></thead><tbody>';
      treatedKeys.sort(function (a, b) { return Number(a) - Number(b); }).forEach(function (key) {
        treatedTeeth[key].forEach(function (info) {
          var tBadge = info.state === 'done' ? 'partners-badge-green' : info.state === 'sale' ? 'partners-badge-blue' : 'partners-badge-orange';
          html += '<tr><td><strong>R\u0103ng ' + escapeHtml(key) + '</strong></td><td>' + escapeHtml(info.product) + '</td><td>' + escapeHtml(formatDate(info.date)) + '</td><td><span class="partners-badge ' + tBadge + '">' + escapeHtml(translateState(info.state)) + '</span></td></tr>';
        });
      });
      html += '</tbody></table></div>';
    }
    return html;
  }


  function renderCDTimeline() {
    var timeline = document.getElementById('cdetail-timeline');
    if (!timeline) return;
    var sideTab = APP.customerDetail.sidebarTab || 'history';

    if (sideTab === 'tasks') {
      timeline.innerHTML = '<div class="cdetail-timeline-empty"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom:8px"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg><br>Chưa có công việc nào</div>';
      return;
    }
    if (sideTab === 'notes') {
      var existingNote = (APP.customerDetail.data && (APP.customerDetail.data.comment || APP.customerDetail.data.notes || APP.customerDetail.data.note)) || '';
      timeline.innerHTML = '<div class="cdetail-timeline-notes"><textarea class="cdetail-notes-input" placeholder="Nhập ghi chú cho bệnh nhân..." rows="4">' + escapeHtml(existingNote) + '</textarea><button class="tds-btn tds-btn-primary tds-btn-sm cdetail-notes-save">Lưu ghi chú</button>' + (existingNote ? '' : '<div class="cdetail-timeline-empty" style="margin-top:16px">Chưa có ghi chú</div>') + '</div>';
      var saveBtn = timeline.querySelector('.cdetail-notes-save');
      if (saveBtn) saveBtn.addEventListener('click', async function () {
        var noteArea = timeline.querySelector('.cdetail-notes-input');
        if (noteArea && APP.customerDetail && APP.customerDetail.id) {
          try {
            await api('/api/customers/' + encodeURIComponent(APP.customerDetail.id), { method: 'PUT', body: JSON.stringify({ comment: noteArea.value }) });
            showToast('success', 'Đã lưu ghi chú');
          } catch (err) { showToast('error', (err && err.message) || 'Không thể lưu ghi chú'); }
        }
      });
      return;
    }

    var events = [];
    (APP.customerDetail.treatments || []).forEach(function (t) { events.push({ date: t.date || t.orderDate || t.createdAt || '', type: 'treatment', title: 'Phiếu điều trị', desc: (t.name || t.ref || '') + ' - ' + formatCurrency(t.totalAmount || t.amountTotal || 0), author: t.createdBy || t.doctorName || '' }); });
    (APP.customerDetail.payments || []).forEach(function (p) { events.push({ date: p.date || p.createdAt || '', type: 'payment', title: 'Thanh toán', desc: formatCurrency(p.amount || 0), author: p.createdBy || '' }); });
    (APP.customerDetail.appointments || []).forEach(function (a) { events.push({ date: a.appointmentDate || a.date || a.createdAt || '', type: 'appointment', title: 'Lịch hẹn', desc: (a.doctorName ? 'BS: ' + a.doctorName : '') + (a.notes || a.note ? ' - ' + (a.notes || a.note) : ''), author: a.createdBy || '' }); });
    (APP.customerDetail.exams || []).forEach(function (e) { events.push({ date: e.date || e.examDate || e.createdAt || '', type: 'exam', title: 'Đợt khám', desc: e.diagnosis || e.reason || '', author: e.doctorName || '' }); });
    events.sort(function (a, b) { return (b.date || '').localeCompare(a.date || ''); });
    if (!events.length) { timeline.innerHTML = '<div class="cdetail-timeline-empty">Chưa có hoạt động</div>'; return; }
    var grouped = {};
    events.forEach(function (ev) { var dk = (ev.date || '').slice(0, 10) || 'unknown'; if (!grouped[dk]) grouped[dk] = []; grouped[dk].push(ev); });
    var html = '';
    Object.keys(grouped).sort(function (a, b) { return b.localeCompare(a); }).forEach(function (dk) {
      var dayLabel = dk === new Date().toISOString().slice(0, 10) ? 'Hôm nay' : formatDate(dk);
      html += '<div class="cdetail-timeline-group"><div class="cdetail-timeline-date">' + escapeHtml(dayLabel) + '</div>';
      grouped[dk].forEach(function (ev) {
        var ic = ev.type === 'payment' ? '#8B5CF6' : ev.type === 'treatment' ? '#1A6DE3' : ev.type === 'exam' ? '#10B981' : '#F59E0B';
        html += '<div class="cdetail-timeline-item"><div class="cdetail-timeline-dot" style="background:' + ic + '"></div><div class="cdetail-timeline-content"><div class="cdetail-timeline-time">' + escapeHtml((ev.date || '').slice(11, 16) || '') + '</div><div class="cdetail-timeline-title">' + escapeHtml(ev.title) + '</div><div class="cdetail-timeline-desc">' + escapeHtml(ev.desc) + '</div>' + (ev.author ? '<div class="cdetail-timeline-author">Người tạo: ' + escapeHtml(ev.author) + '</div>' : '') + '</div></div>';
      });
      html += '</div>';
    });
    timeline.innerHTML = html;
  }


  // Customer Create / Edit Modal (T-021)

  // Bind dental chart click events (called after tab content renders)
  function bindDentalChartClicks() {
    var selector = document.getElementById('dental-selector');
    var selectorTitle = document.getElementById('dental-selector-title');
    var closeBtn = document.getElementById('dental-close-btn');
    var selectedTooth = null;
    var toothGroups = document.querySelectorAll('.dental-tooth-g');
    for (var i = 0; i < toothGroups.length; i++) {
      toothGroups[i].addEventListener('click', function () {
        selectedTooth = this.getAttribute('data-tooth');
        if (selectorTitle) selectorTitle.textContent = 'Răng #' + selectedTooth;
        if (selector) selector.style.display = 'block';
      });
    }
    var condBtns = document.querySelectorAll('.dental-cond-btn');
    for (var j = 0; j < condBtns.length; j++) {
      condBtns[j].addEventListener('click', function () {
        if (!selectedTooth) return;
        if (!APP.customerDetail._toothState) APP.customerDetail._toothState = {};
        APP.customerDetail._toothState[selectedTooth] = this.getAttribute('data-cond');
        if (selector) selector.style.display = 'none';
        renderCDTabContent(); // re-render to update colors
        bindDentalChartClicks();
      });
    }
    if (closeBtn) closeBtn.addEventListener('click', function () { if (selector) selector.style.display = 'none'; selectedTooth = null; });
  }

  // ---------------------------------------------------------------------------
  function openCustomerModal(customer) {
    var editing = !!customer;
    var c = customer || {};

    var content =
      '<form id="customer-form" class="customer-modal-form">' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tên khách hàng *</label>' +
      '<input class="tds-input" id="cust-name" required value="' + escapeHtml(c.name || '') + '" placeholder="Nhập họ tên">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Số điện thoại *</label>' +
      '<input class="tds-input" id="cust-phone" required value="' + escapeHtml(c.phone || '') + '" placeholder="0xx xxx xxxx">' +
      '</div>' +
      '</div>' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Email</label>' +
      '<input class="tds-input" id="cust-email" type="email" value="' + escapeHtml(c.email || '') + '" placeholder="email@example.com">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Ngày sinh</label>' +
      '<input class="tds-input" id="cust-dob" type="date" value="' + escapeHtml((c.dateOfBirth || c.birthdate || '').slice(0, 10)) + '">' +
      '</div>' +
      '</div>' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Giới tính</label>' +
      '<select class="tds-select" id="cust-gender">' +
      '<option value="">-- Chọn --</option>' +
      '<option value="male"' + (c.gender === 'male' ? ' selected' : '') + '>Nam</option>' +
      '<option value="female"' + (c.gender === 'female' ? ' selected' : '') + '>Nữ</option>' +
      '<option value="other"' + (c.gender === 'other' ? ' selected' : '') + '>Khác</option>' +
      '</select>' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Chi nhánh</label>' +
      '<select class="tds-select" id="cust-company"></select>' +
      '</div>' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Địa chỉ</label>' +
      '<input class="tds-input" id="cust-address" value="' + escapeHtml(c.address || c.street || '') + '" placeholder="Số nhà, đường, quận">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Ghi chú</label>' +
      '<textarea class="tds-input" id="cust-notes" rows="3" placeholder="Ghi chú về khách hàng">' + escapeHtml(c.comment || c.notes || '') + '</textarea>' +
      '</div>' +
      '</form>';

    showModal(editing ? 'Cập nhật khách hàng' : 'Thêm khách hàng mới', content, {
      width: 640,
      footer:
        '<button class="tds-btn tds-btn-ghost" id="cust-modal-cancel">Hủy</button>' +
        '<button class="tds-btn tds-btn-primary" id="cust-modal-save">' + (editing ? 'Cập nhật' : 'Tạo mới') + '</button>',
      onOpen: function () {
        // Populate branch dropdown
        var companySelect = document.getElementById('cust-company');
        if (companySelect) {
          var branchSelector = document.getElementById('branch-selector');
          if (branchSelector) {
            companySelect.innerHTML = branchSelector.innerHTML;
          }
          if (c.companyId) companySelect.value = c.companyId;
          else if (getSelectedBranchId()) companySelect.value = getSelectedBranchId();
        }

        var cancelBtn = document.getElementById('cust-modal-cancel');
        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

        var saveBtn = document.getElementById('cust-modal-save');
        if (!saveBtn) return;

        saveBtn.addEventListener('click', async function () {
          var name = getInputValue('cust-name');
          var phone = getInputValue('cust-phone');
          if (!name) { showToast('warning', 'Tên khách hàng là bắt buộc'); return; }
          if (!phone) { showToast('warning', 'Số điện thoại là bắt buộc'); return; }
          if (!/^0\d{8,10}$/.test(phone.replace(/\s+/g, ''))) {
            showToast('warning', 'Số điện thoại không hợp lệ (bắt đầu bằng 0, 9-11 chữ số)');
            return;
          }

          var payload = {
            name: name,
            phone: phone.replace(/\s+/g, ''),
            email: getInputValue('cust-email') || null,
            dateOfBirth: getInputValue('cust-dob') || null,
            gender: getInputValue('cust-gender') || null,
            companyId: getInputValue('cust-company') || null,
            address: getInputValue('cust-address') || null,
            comment: getInputValue('cust-notes') || null,
          };

          saveBtn.disabled = true;
          saveBtn.textContent = 'Đang lưu...';

          try {
            if (editing && c.id) {
              await api('/api/customers/' + encodeURIComponent(c.id), {
                method: 'PUT',
                body: JSON.stringify(payload),
              });
              showToast('success', 'Lưu thành công');
            } else {
              await api('/api/customers', {
                method: 'POST',
                body: JSON.stringify(payload),
              });
              showToast('success', 'Đã tạo khách hàng mới');
            }
            closeModal();
            loadPartnersData();
          } catch (err) {
            showToast('error', (err && err.message) || 'Không thể lưu khách hàng');
            saveBtn.disabled = false;
            saveBtn.textContent = editing ? 'Cập nhật' : 'Tạo mới';
          }
        });
      },
    });
  }

  function renderTasks() {
    var el = document.getElementById('page-tasks');
    if (!el) return;

    el.innerHTML =
      '<div class="tds-card tasks-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Quản lý tác vụ</h2>' +
      '<button class="tds-btn tds-btn-primary" id="tasks-add-btn">Thêm tác vụ</button>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="tasks-search" placeholder="Tìm tiêu đề tác vụ" value="' + escapeHtml(APP.tasks.search || '') + '">' +
      '<select class="tds-select" id="tasks-stage-filter">' +
      '<option value="">Tất cả giai đoạn</option>' +
      '<option value="0"' + (String(APP.tasks.stage) === '0' ? ' selected' : '') + '>Mới</option>' +
      '<option value="1"' + (String(APP.tasks.stage) === '1' ? ' selected' : '') + '>Đang xử lý</option>' +
      '<option value="2"' + (String(APP.tasks.stage) === '2' ? ' selected' : '') + '>Theo dõi</option>' +
      '<option value="3"' + (String(APP.tasks.stage) === '3' ? ' selected' : '') + '>Hoàn thành</option>' +
      '<option value="4"' + (String(APP.tasks.stage) === '4' ? ' selected' : '') + '>Đã hủy</option>' +
      '</select>' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-secondary" id="tasks-refresh-btn">Làm mới</button>' +
      '</div>' +
      '</div>' +
      '<div id="tasks-stats"></div>' +
      '<div id="tasks-table"></div>' +
      '</div>';

    var searchInput = document.getElementById('tasks-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.tasks.search = searchInput.value.trim();
        loadTasksData();
      }, 250));
    }

    var stageSelect = document.getElementById('tasks-stage-filter');
    if (stageSelect) {
      stageSelect.addEventListener('change', function () {
        APP.tasks.stage = this.value;
        loadTasksData();
      });
    }

    var refreshBtn = document.getElementById('tasks-refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function () {
        loadTasksStats();
        loadTasksData();
      });
    }

    var addBtn = document.getElementById('tasks-add-btn');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        openTaskModal(null);
      });
    }

    loadTasksStats();
    loadTasksData();
  }

  async function loadTasksStats() {
    try {
      var query = toQueryString({
        companyId: getSelectedBranchId(),
      });
      var data = await api('/api/tasks/counts' + query);
      APP.tasks.counts = Array.isArray(data) ? data : [];
    } catch (_err) {
      APP.tasks.counts = [];
    }
    renderTasksStats();
  }

  function renderTasksStats() {
    var statsEl = document.getElementById('tasks-stats');
    if (!statsEl) return;

    var rows = APP.tasks.counts || [];
    if (!rows.length) {
      statsEl.innerHTML = '<div class="tds-empty mt-md"><p>Chưa có thống kê tác vụ</p></div>';
      return;
    }

    statsEl.innerHTML =
      '<div class="dashboard-grid mt-md">' +
      rows.map(function (row) {
        return (
          '<div class="kpi-card">' +
          '<div class="kpi-label">' + escapeHtml(taskStageLabel(row.stage)) + '</div>' +
          '<div class="kpi-value">' + escapeHtml(formatNumber(row.total || 0)) + '</div>' +
          '</div>'
        );
      }).join('') +
      '</div>';
  }

  async function loadTasksData() {
    APP.tasks.loading = true;
    APP.tasks.requestId += 1;
    var requestId = APP.tasks.requestId;
    renderTasksTable();

    try {
      var query = toQueryString({
        search: APP.tasks.search,
        stage: APP.tasks.stage,
        companyId: getSelectedBranchId(),
        limit: 50,
        offset: 0,
      });
      var data = await api('/api/tasks' + query);
      if (requestId !== APP.tasks.requestId) return;
      APP.tasks.items = safeItems(data);
    } catch (_err) {
      if (requestId !== APP.tasks.requestId) return;
      APP.tasks.items = [];
    } finally {
      if (requestId === APP.tasks.requestId) {
        APP.tasks.loading = false;
        renderTasksTable();
      }
    }
  }

  function renderTasksTable() {
    var tableWrap = document.getElementById('tasks-table');
    if (!tableWrap) return;

    if (APP.tasks.loading) {
      tableWrap.innerHTML = renderLoadingState('Đang tải tác vụ...');
      return;
    }

    var rows = APP.tasks.items || [];
    if (!rows.length) {
      tableWrap.innerHTML = renderEmptyState('Chưa có tác vụ');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper mt-md">' +
      '<table class="tds-table tasks-table">' +
      '<thead><tr><th>Tiêu đề</th><th>Giai đoạn</th><th>Ưu tiên</th><th>Hạn</th><th>Ngày tạo</th><th></th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(item.title || 'N/A') + '</td>' +
          '<td>' + escapeHtml(taskStageLabel(item.stage)) + '</td>' +
          '<td>' + (item.priority ? '<span class="tds-badge tds-badge-warning">Cao</span>' : '<span class="tds-badge tds-badge-gray">Thường</span>') + '</td>' +
          '<td>' + escapeHtml(formatDate(item.dateExpire)) + '</td>' +
          '<td>' + escapeHtml(formatDateTime(item.dateCreated)) + '</td>' +
          '<td class="text-right">' +
          '<button class="tds-btn tds-btn-sm tds-btn-secondary task-edit" data-id="' + escapeHtml(item.id || '') + '">Sửa</button> ' +
          '<button class="tds-btn tds-btn-sm tds-btn-danger task-delete" data-id="' + escapeHtml(item.id || '') + '">Xóa</button>' +
          '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    var editBtns = tableWrap.querySelectorAll('.task-edit');
    for (var i = 0; i < editBtns.length; i++) {
      editBtns[i].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        var task = findItemById(APP.tasks.items || [], id);
        if (!task) return;
        openTaskModal(task);
      });
    }

    var deleteBtns = tableWrap.querySelectorAll('.task-delete');
    for (var j = 0; j < deleteBtns.length; j++) {
      deleteBtns[j].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        deleteTask(id);
      });
    }
  }

  function openTaskModal(task) {
    var editing = !!task;
    var dateExpireValue = task && task.dateExpire ? formatDateInput(task.dateExpire) : '';

    var content =
      '<form id="task-form">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tiêu đề</label>' +
      '<input class="tds-input" id="task-title-input" required value="' + escapeHtml((task && task.title) || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Mô tả</label>' +
      '<textarea class="tds-input" id="task-description-input" rows="3">' + escapeHtml((task && task.description) || '') + '</textarea>' +
      '</div>' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Giai đoạn</label>' +
      '<select class="tds-select" id="task-stage-input">' +
      '<option value="0"' + (Number((task && task.stage) || 0) === 0 ? ' selected' : '') + '>Mới</option>' +
      '<option value="1"' + (Number((task && task.stage) || 0) === 1 ? ' selected' : '') + '>Đang xử lý</option>' +
      '<option value="2"' + (Number((task && task.stage) || 0) === 2 ? ' selected' : '') + '>Theo dõi</option>' +
      '<option value="3"' + (Number((task && task.stage) || 0) === 3 ? ' selected' : '') + '>Hoàn thành</option>' +
      '<option value="4"' + (Number((task && task.stage) || 0) === 4 ? ' selected' : '') + '>Đã hủy</option>' +
      '</select>' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Hạn xử lý</label>' +
      '<input class="tds-input" id="task-expire-input" type="date" value="' + escapeHtml(dateExpireValue) + '">' +
      '</div>' +
      '</div>' +
      '<label class="tds-checkbox-label"><input type="checkbox" id="task-priority-input" ' + ((task && task.priority) ? 'checked' : '') + '> Ưu tiên cao</label>' +
      '<label class="tds-checkbox-label"><input type="checkbox" id="task-active-input" ' + (((task ? task.active : true) !== false) ? 'checked' : '') + '> Đang hoạt động</label>' +
      '</form>';

    showModal(editing ? 'Cập nhật tác vụ' : 'Thêm tác vụ', content, {
      footer:
        '<button class="tds-btn tds-btn-ghost" id="task-modal-cancel">Hủy</button>' +
        '<button class="tds-btn tds-btn-primary" id="task-modal-save">' + (editing ? 'Cập nhật' : 'Thêm mới') + '</button>',
      onOpen: function () {
        var cancelBtn = document.getElementById('task-modal-cancel');
        var saveBtn = document.getElementById('task-modal-save');
        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
        if (!saveBtn) return;

        saveBtn.addEventListener('click', async function () {
          var title = getInputValue('task-title-input');
          if (!title) {
            showToast('warning', 'Tiêu đề tác vụ là bắt buộc');
            return;
          }

          var expireRaw = getInputValue('task-expire-input');
          var payload = {
            title: title,
            description: getInputValue('task-description-input') || null,
            stage: Number(getInputValue('task-stage-input') || 0),
            priority: !!(document.getElementById('task-priority-input') || {}).checked,
            active: !!(document.getElementById('task-active-input') || {}).checked,
            companyId: getSelectedBranchId() || null,
            dateExpire: expireRaw ? new Date(expireRaw + 'T23:59:59').toISOString() : null,
          };

          try {
            if (editing && task && task.id) {
              await api('/api/tasks/' + encodeURIComponent(task.id), {
                method: 'PUT',
                body: JSON.stringify(payload),
              });
              showToast('success', 'Đã cập nhật tác vụ');
            } else {
              await api('/api/tasks', {
                method: 'POST',
                body: JSON.stringify(payload),
              });
              showToast('success', 'Đã tạo tác vụ');
            }

            closeModal();
            loadTasksStats();
            loadTasksData();
          } catch (err) {
            showToast('error', (err && err.message) || 'Không thể lưu tác vụ');
          }
        });
      },
    });
  }

  async function deleteTask(taskId) {
    if (!taskId) return;
    var ok = await tdsConfirm('Xóa tác vụ này?', { title: 'Xóa tác vụ' });
    if (!ok) return;

    try {
      await api('/api/tasks/' + encodeURIComponent(taskId), { method: 'DELETE' });
      showToast('success', 'Đã xóa tác vụ');
      loadTasksStats();
      loadTasksData();
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể xóa tác vụ');
    }
  }

  function taskStageLabel(stage) {
    var value = Number(stage || 0);
    if (value === 0) return 'Mới';
    if (value === 1) return 'Đang xử lý';
    if (value === 2) return 'Theo dõi';
    if (value === 3) return 'Hoàn thành';
    if (value === 4) return 'Đã hủy';
    return 'Giai đoạn ' + String(value);
  }

  function renderWork() {
    var el = document.getElementById('page-work');
    if (!el) return;
    var state = getWorkViewState();
    state.companyId = getSelectedBranchId();

    var now = new Date();
    var monthStart = String(now.getFullYear()) + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-01';
    var monthEnd = String(now.getFullYear()) + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()).padStart(2, '0');
    var dateFromDisplay = monthStart.slice(8, 10) + '/' + monthStart.slice(5, 7) + '/' + monthStart.slice(0, 4);
    var dateToDisplay = monthEnd.slice(8, 10) + '/' + monthEnd.slice(5, 7) + '/' + monthEnd.slice(0, 4);

    var statusTabs = [
      { key: 'all', label: 'Tất cả' },
      { key: 'priority', label: 'Ưu tiên' },
      { key: 'new', label: 'Mới' },
      { key: 'in_progress', label: 'Đang làm' },
      { key: 'need_info', label: 'Cần thêm thông tin' },
      { key: 'done', label: 'Hoàn thành' },
      { key: 'cancelled', label: 'Hủy' },
      { key: 'unassigned', label: 'Chưa phân công' }
    ];

    var tabsHtml = '';
    for (var i = 0; i < statusTabs.length; i++) {
      var active = state.statusFilter === statusTabs[i].key ? ' work-tab-active' : '';
      tabsHtml += '<button class="work-status-tab' + active + '" data-work-status="' + statusTabs[i].key + '">' + statusTabs[i].label + '</button>';
    }

    // Status filter options for dropdown
    var statusFilterOptions = [
      { key: '', label: 'Tất cả trạng thái' },
      { key: 'new', label: 'Mới' },
      { key: 'in_progress', label: 'Đang xử lý' },
      { key: 'done', label: 'Hoàn thành' },
      { key: 'cancelled', label: 'Hủy' }
    ];
    var statusFilterHtml = statusFilterOptions.map(function (opt) {
      return '<option value="' + opt.key + '"' + (state.filterStatus === opt.key ? ' selected' : '') + '>' + opt.label + '</option>';
    }).join('');

    // Employee options
    var employeeOptions = [{ key: '', label: 'Tất cả nhân viên' }];
    if (state.employees && state.employees.length > 0) {
      for (var j = 0; j < state.employees.length; j++) {
        employeeOptions.push({ key: state.employees[j].id, label: state.employees[j].name });
      }
    }
    var employeeFilterHtml = employeeOptions.map(function (opt) {
      return '<option value="' + escapeHtml(opt.key) + '"' + (String(state.filterAssignee) === String(opt.key) ? ' selected' : '') + '>' + escapeHtml(opt.label) + '</option>';
    }).join('');

    var filtersPanelVisible = state.showFiltersPanel ? ' visible' : '';
    var viewMode = state.viewMode || 'list';

    el.innerHTML =
      '<section class="work-page">' +
      '<div class="work-header">' +
      '<div class="work-header-left">' +
      '<div class="work-sub-tabs">' +
      '<button class="work-sub-tab' + (state.subTab === 'tasks' ? ' work-sub-tab-active' : '') + '" data-work-subtab="tasks">Công việc</button>' +
      '<button class="work-sub-tab' + (state.subTab === 'types' ? ' work-sub-tab-active' : '') + '" data-work-subtab="types">Loại công việc</button>' +
      '</div>' +
      '</div>' +
      '<div class="work-header-right">' +
      '<div class="work-date-range">' +
      '<span>' + dateFromDisplay + '</span>' +
      '<span class="work-date-sep">&ndash;</span>' +
      '<span>' + dateToDisplay + '</span>' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>' +
      '</div>' +
      '<div class="work-search-box">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' +
      '<input type="text" class="work-search-input" id="work-search-input" placeholder="Tìm kiếm theo tiêu đề, #ID, khách hàng" />' +
      '</div>' +
      '<button class="tds-btn tds-btn-primary work-create-btn" id="work-create-btn">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>' +
      ' Tạo công việc' +
      '</button>' +
      '</div>' +
      '</div>' +
      '<div class="work-filters-bar">' +
      '<div class="work-status-tabs">' + tabsHtml + '</div>' +
      '<div class="work-filter-actions">' +
      '<div class="work-view-toggle">' +
      '<button class="work-view-btn' + (viewMode === 'list' ? ' active' : '') + '" data-view="list" title="Danh sách">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>' +
      '</button>' +
      '<button class="work-view-btn' + (viewMode === 'kanban' ? ' active' : '') + '" data-view="kanban" title="Kanban">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="18" rx="1"/><rect x="14" y="3" width="7" height="12" rx="1"/></svg>' +
      '</button>' +
      '<button class="work-view-btn' + (viewMode === 'calendar' ? ' active' : '') + '" data-view="calendar" title="Lịch">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>' +
      '</button>' +
      '</div>' +
      '<button class="tds-btn tds-btn-ghost tds-btn-icon work-filter-btn' + (state.showFiltersPanel ? ' active' : '') + '" title="Lọc">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>' +
      '</button>' +
      '</div>' +
      '</div>' +
      '<div class="work-filters-panel' + filtersPanelVisible + '">' +
      '<div class="work-filters-grid">' +
      '<div class="work-filter-group">' +
      '<label class="work-filter-label">Trạng thái</label>' +
      '<select class="tds-select" id="work-filter-status">' + statusFilterHtml + '</select>' +
      '</div>' +
      '<div class="work-filter-group">' +
      '<label class="work-filter-label">Từ ngày</label>' +
      '<input class="tds-input" type="date" id="work-filter-date-from" value="' + escapeHtml(state.filterDateFrom || monthStart) + '" />' +
      '</div>' +
      '<div class="work-filter-group">' +
      '<label class="work-filter-label">Đến ngày</label>' +
      '<input class="tds-input" type="date" id="work-filter-date-to" value="' + escapeHtml(state.filterDateTo || monthEnd) + '" />' +
      '</div>' +
      '<div class="work-filter-group">' +
      '<label class="work-filter-label">Người phụ trách</label>' +
      '<select class="tds-select" id="work-filter-assignee">' + employeeFilterHtml + '</select>' +
      '</div>' +
      '</div>' +
      '</div>' +
      '<div class="work-table-wrap' + (viewMode !== 'list' ? ' hidden' : '') + '">' +
      '<table class="work-table">' +
      '<thead>' +
      '<tr>' +
      '<th>Tiêu đề</th>' +
      '<th>Loại công việc</th>' +
      '<th>Hành động</th>' +
      '<th>Người phụ trách</th>' +
      '<th>Người theo dõi</th>' +
      '<th>Khách hàng</th>' +
      '<th>Nội dung CV</th>' +
      '<th>Trạng thái</th>' +
      '<th>Thao tác</th>' +
      '</tr>' +
      '</thead>' +
      '<tbody id="work-table-body"></tbody>' +
      '</table>' +
      '<div id="work-empty-state" class="work-empty-state">' +
      '<div class="work-empty-illustration">' +
      '<svg width="120" height="120" viewBox="0 0 120 120" fill="none">' +
      '<rect x="30" y="20" width="60" height="80" rx="6" fill="#E8EDF2" stroke="#B0BEC5" stroke-width="2"/>' +
      '<rect x="40" y="35" width="40" height="4" rx="2" fill="#B0BEC5"/>' +
      '<rect x="40" y="45" width="30" height="4" rx="2" fill="#B0BEC5"/>' +
      '<rect x="40" y="55" width="35" height="4" rx="2" fill="#B0BEC5"/>' +
      '<circle cx="80" cy="80" r="18" fill="#fff" stroke="#B0BEC5" stroke-width="2"/>' +
      '<circle cx="80" cy="80" r="12" fill="#E8EDF2"/>' +
      '<path d="M75 80 L78 83 L85 76" stroke="#2196F3" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
      '</svg>' +
      '</div>' +
      '<p>Chưa có công việc nào</p>' +
      '</div>' +
      '</div>' +
      '<div id="work-kanban-container" class="work-kanban-container' + (viewMode === 'kanban' ? ' visible' : '') + '"></div>' +
      '<div id="work-calendar-container" class="work-calendar-container' + (viewMode === 'calendar' ? ' visible' : '') + '"></div>' +
      '</section>';

    bindWorkInteractions(el);
    loadWorkData();
    loadWorkEmployees();
    if (viewMode === 'kanban') renderWorkKanban();
    if (viewMode === 'calendar') renderWorkCalendar();
  }

  function getWorkViewState() {
    if (!APP.work) {
      APP.work = {
        companyId: getSelectedBranchId(),
        subTab: 'tasks',
        statusFilter: 'all',
        searchQuery: '',
        tasks: [],
        requestSeq: 0,
        viewMode: 'list', // list, kanban, calendar
        filterStatus: '',
        filterDateFrom: '',
        filterDateTo: '',
        filterAssignee: '',
        employees: [],
        showFiltersPanel: false,
      };
    }
    return APP.work;
  }

  function bindWorkInteractions(root) {
    var state = getWorkViewState();

    var subTabBtns = root.querySelectorAll('[data-work-subtab]');
    for (var i = 0; i < subTabBtns.length; i++) {
      subTabBtns[i].addEventListener('click', function () {
        state.subTab = this.getAttribute('data-work-subtab') || 'tasks';
        renderWork();
      });
    }

    var statusBtns = root.querySelectorAll('[data-work-status]');
    for (var j = 0; j < statusBtns.length; j++) {
      statusBtns[j].addEventListener('click', function () {
        state.statusFilter = this.getAttribute('data-work-status') || 'all';
        renderWork();
      });
    }

    // View toggle buttons
    var viewBtns = root.querySelectorAll('[data-view]');
    for (var v = 0; v < viewBtns.length; v++) {
      viewBtns[v].addEventListener('click', function () {
        state.viewMode = this.getAttribute('data-view') || 'list';
        renderWork();
      });
    }

    // Filter toggle button
    var filterBtn = root.querySelector('.work-filter-btn');
    if (filterBtn) {
      filterBtn.addEventListener('click', function () {
        state.showFiltersPanel = !state.showFiltersPanel;
        renderWork();
      });
    }

    // Filter dropdowns
    var statusFilter = root.querySelector('#work-filter-status');
    if (statusFilter) {
      statusFilter.addEventListener('change', function () {
        state.filterStatus = this.value;
        renderWorkTableBody();
        if (state.viewMode === 'kanban') renderWorkKanban();
        if (state.viewMode === 'calendar') renderWorkCalendar();
      });
    }

    var dateFromFilter = root.querySelector('#work-filter-date-from');
    if (dateFromFilter) {
      dateFromFilter.addEventListener('change', function () {
        state.filterDateFrom = this.value;
        renderWorkTableBody();
        if (state.viewMode === 'kanban') renderWorkKanban();
        if (state.viewMode === 'calendar') renderWorkCalendar();
      });
    }

    var dateToFilter = root.querySelector('#work-filter-date-to');
    if (dateToFilter) {
      dateToFilter.addEventListener('change', function () {
        state.filterDateTo = this.value;
        renderWorkTableBody();
        if (state.viewMode === 'kanban') renderWorkKanban();
        if (state.viewMode === 'calendar') renderWorkCalendar();
      });
    }

    var assigneeFilter = root.querySelector('#work-filter-assignee');
    if (assigneeFilter) {
      assigneeFilter.addEventListener('change', function () {
        state.filterAssignee = this.value;
        renderWorkTableBody();
        if (state.viewMode === 'kanban') renderWorkKanban();
        if (state.viewMode === 'calendar') renderWorkCalendar();
      });
    }

    var searchInput = root.querySelector('#work-search-input');
    if (searchInput) {
      searchInput.value = state.searchQuery || '';
      var searchTimer = null;
      searchInput.addEventListener('input', function () {
        var val = this.value;
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () {
          state.searchQuery = val;
          renderWorkTableBody();
        }, 300);
      });
    }

    var createBtn = root.querySelector('#work-create-btn');
    if (createBtn) {
      createBtn.addEventListener('click', function () {
        openTaskModal(null);
      });
    }

    // Date range click handler - toggle filters and focus date input
    var dateRange = root.querySelector('.work-date-range');
    if (dateRange) {
      dateRange.style.cursor = 'pointer';
      dateRange.addEventListener('click', function (e) {
        e.preventDefault();
        // Toggle filters panel if not visible
        if (!state.showFiltersPanel) {
          state.showFiltersPanel = true;
          renderWork();
          // Need to re-query after render
          setTimeout(function () {
            var dateFrom = document.getElementById('work-filter-date-from');
            if (dateFrom) dateFrom.focus();
          }, 50);
        } else {
          // Just focus the date input
          var dateFrom = document.getElementById('work-filter-date-from');
          if (dateFrom) dateFrom.focus();
        }
      });
    }
  }

  async function loadWorkData() {
    var state = getWorkViewState();
    state.companyId = getSelectedBranchId();
    var requestSeq = ++state.requestSeq;

    try {
      var data = await api('/api/tasks' + toQueryString({ companyId: state.companyId || '' }));
      if (requestSeq !== state.requestSeq) return;
      state.tasks = Array.isArray(data) ? data : (data && data.items ? data.items : []);
    } catch (_err) {
      state.tasks = [];
    }

    renderWorkTableBody();
  }

  function renderWorkTableBody() {
    var state = getWorkViewState();
    var tbody = document.getElementById('work-table-body');
    var emptyEl = document.getElementById('work-empty-state');
    if (!tbody || !emptyEl) return;

    var tasks = state.tasks || [];

    // Apply status filter (from tabs)
    if (state.statusFilter && state.statusFilter !== 'all') {
      tasks = tasks.filter(function (t) {
        return t.status === state.statusFilter || t.state === state.statusFilter;
      });
    }

    // Apply status filter (from dropdown)
    if (state.filterStatus) {
      tasks = tasks.filter(function (t) {
        return t.status === state.filterStatus || t.state === state.filterStatus;
      });
    }

    // Apply search query
    if (state.searchQuery) {
      var q = state.searchQuery.toLowerCase();
      tasks = tasks.filter(function (t) {
        return (
          (t.title && t.title.toLowerCase().indexOf(q) >= 0) ||
          (t.id && String(t.id).indexOf(q) >= 0) ||
          (t.customerName && t.customerName.toLowerCase().indexOf(q) >= 0)
        );
      });
    }

    // Apply assignee filter
    if (state.filterAssignee) {
      tasks = tasks.filter(function (t) {
        return t.assigneeId == state.filterAssignee || t.userId == state.filterAssignee;
      });
    }

    // Apply date range filter
    if (state.filterDateFrom) {
      tasks = tasks.filter(function (t) {
        var taskDate = t.date || t.createdAt;
        if (!taskDate) return true;
        return taskDate >= state.filterDateFrom;
      });
    }
    if (state.filterDateTo) {
      tasks = tasks.filter(function (t) {
        var taskDate = t.date || t.createdAt;
        if (!taskDate) return true;
        return taskDate <= state.filterDateTo;
      });
    }

    if (!tasks.length) {
      tbody.innerHTML = '';
      emptyEl.style.display = '';
      return;
    }

    emptyEl.style.display = 'none';
    var html = '';
    for (var i = 0; i < tasks.length; i++) {
      var t = tasks[i];
      var statusLabel = t.statusLabel || t.status || '';
      var statusClass = 'work-status-badge work-status-' + (t.status || 'new');
      html +=
        '<tr>' +
        '<td>' + escapeHtml(t.title || '') + '</td>' +
        '<td>' + escapeHtml(t.type || '') + '</td>' +
        '<td>' + escapeHtml(t.action || '') + '</td>' +
        '<td>' + escapeHtml(t.assignee || '') + '</td>' +
        '<td>' + escapeHtml(t.watcher || '') + '</td>' +
        '<td>' + escapeHtml(t.customerName || '') + '</td>' +
        '<td>' + escapeHtml(t.content || '') + '</td>' +
        '<td><span class="' + statusClass + '">' + escapeHtml(statusLabel) + '</span></td>' +
        '<td class="work-action-cell" style="position:relative"><button class="tds-btn tds-btn-ghost tds-btn-sm work-action-btn" data-task-idx="' + i + '">...</button></td>' +
        '</tr>';
    }
    tbody.innerHTML = html;

    // Wire work "..." action buttons
    var actionBtns = tbody.querySelectorAll('.work-action-btn');
    for (var ab = 0; ab < actionBtns.length; ab++) {
      actionBtns[ab].addEventListener('click', function (e) {
        e.stopPropagation();
        var tIdx = parseInt(this.getAttribute('data-task-idx'), 10);
        var task = tasks[tIdx];
        if (!task) return;
        // Remove any existing dropdown
        var existing = document.querySelector('.work-action-dropdown');
        if (existing) existing.remove();
        // Create dropdown
        var dd = document.createElement('div');
        dd.className = 'work-action-dropdown';
        dd.style.cssText = 'position:absolute;right:0;top:100%;z-index:100;background:#fff;border:1px solid #E2E8F0;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1);min-width:140px;padding:4px 0;';
        dd.innerHTML =
          '<div class="work-action-item" data-action="view" style="padding:8px 16px;cursor:pointer;font-size:13px;">Xem chi ti\u1ebft</div>' +
          '<div class="work-action-item" data-action="edit" style="padding:8px 16px;cursor:pointer;font-size:13px;">S\u1eeda</div>' +
          '<div class="work-action-item" data-action="delete" style="padding:8px 16px;cursor:pointer;font-size:13px;color:#EF4444;">X\u00f3a</div>';
        this.parentElement.appendChild(dd);

        dd.querySelector('[data-action="view"]').addEventListener('click', function () {
          dd.remove();
          openWorkDetailDrawer(task);
        });
        dd.querySelector('[data-action="edit"]').addEventListener('click', function () {
          dd.remove();
          openTaskModal(task);
        });
        dd.querySelector('[data-action="delete"]').addEventListener('click', async function () {
          dd.remove();
          var ok = await tdsConfirm('X\u00f3a c\u00f4ng vi\u1ec7c "' + (task.title || '') + '"?', { title: 'X\u00f3a c\u00f4ng vi\u1ec7c' });
          if (!ok) return;
          try {
            await api('/api/tasks/' + encodeURIComponent(task.id), { method: 'DELETE' });
            showToast('success', '\u0110\u00e3 x\u00f3a c\u00f4ng vi\u1ec7c');
            renderWork();
          } catch (err) { showToast('error', (err && err.message) || 'Kh\u00f4ng th\u1ec3 x\u00f3a'); }
        });

        // Close dropdown on outside click
        setTimeout(function () {
          document.addEventListener('click', function closeDD() {
            dd.remove();
            document.removeEventListener('click', closeDD);
          });
        }, 0);
      });
    }
  }

  function openWorkDetailDrawer(task) {
    var content =
      '<div class="drawer-header">' +
      '<h3>Chi ti\u1ebft c\u00f4ng vi\u1ec7c</h3>' +
      '<button class="drawer-close" onclick="TDS.closeDrawer()">&times;</button>' +
      '</div>' +
      '<div class="drawer-content">' +
      '<div class="drawer-field"><label>Ti\u00eau \u0111\u1ec1</label><span>' + escapeHtml(task.title || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Lo\u1ea1i</label><span>' + escapeHtml(task.type || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Ng\u01b0\u1eddi ph\u1ee5 tr\u00e1ch</label><span>' + escapeHtml(task.assignee || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Kh\u00e1ch h\u00e0ng</label><span>' + escapeHtml(task.customerName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Tr\u1ea1ng th\u00e1i</label><span class="work-status-badge work-status-' + (task.status || 'new') + '">' + escapeHtml(task.statusLabel || task.status || '\u2014') + '</span></div>' +
      (task.content ? '<div class="drawer-field"><label>N\u1ed9i dung</label><span>' + escapeHtml(task.content) + '</span></div>' : '') +
      (task.description ? '<div class="drawer-field"><label>M\u00f4 t\u1ea3</label><span style="white-space:pre-wrap">' + escapeHtml(task.description) + '</span></div>' : '') +
      '</div>';
    openDrawer(content, 480);
  }

  async function loadWorkEmployees() {
    var state = getWorkViewState();
    try {
      var data = await api('/api/employees?companyId=' + (getSelectedBranchId() || ''));
      state.employees = safeItems(data);
    } catch (err) {
      state.employees = [];
    }
  }

  function renderWorkKanban() {
    var state = getWorkViewState();
    var container = document.getElementById('work-kanban-container');
    if (!container) return;

    var tasks = getFilteredTasks();

    var columns = [
      { key: 'new', label: 'Mới', color: '#3B82F6' },
      { key: 'in_progress', label: 'Đang xử lý', color: '#8B5CF6' },
      { key: 'need_info', label: 'Cần thêm thông tin', color: '#F59E0B' },
      { key: 'done', label: 'Hoàn thành', color: '#10B981' }
    ];

    var html = '';
    for (var c = 0; c < columns.length; c++) {
      var col = columns[c];
      var colTasks = tasks.filter(function (t) { return t.status === col.key || t.state === col.key; });

      html += '<div class="work-kanban-column">' +
        '<div class="work-kanban-header" style="border-left: 3px solid ' + col.color + '">' +
        '<span>' + col.label + '</span>' +
        '<span class="work-kanban-count">' + colTasks.length + '</span>' +
        '</div>' +
        '<div class="work-kanban-body">';

      for (var i = 0; i < colTasks.length; i++) {
        var t = colTasks[i];
        html += '<div class="work-kanban-card" data-task-id="' + escapeHtml(String(t.id)) + '">' +
          '<div class="work-kanban-card-title">' + escapeHtml(t.title || '') + '</div>' +
          '<div class="work-kanban-card-meta">' +
          (t.customerName ? '<span class="work-kanban-card-customer"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' + escapeHtml(t.customerName) + '</span>' : '') +
          '</div>' +
          '</div>';
      }

      html += '</div></div>';
    }

    container.innerHTML = html;
  }

  function renderWorkCalendar() {
    var state = getWorkViewState();
    var container = document.getElementById('work-calendar-container');
    if (!container) return;

    var tasks = getFilteredTasks();
    var now = new Date();
    var currentMonth = now.getMonth();
    var currentYear = now.getFullYear();

    var firstDay = new Date(currentYear, currentMonth, 1);
    var lastDay = new Date(currentYear, currentMonth + 1, 0);
    var startDay = firstDay.getDay();
    var daysInMonth = lastDay.getDate();

    var prevMonthLastDay = new Date(currentYear, currentMonth, 0).getDate();

    var dayNames = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];

    var html = '<div class="work-calendar-grid">';

    // Header row
    for (var d = 0; d < 7; d++) {
      html += '<div class="work-calendar-header-cell">' + dayNames[d] + '</div>';
    }

    // Previous month days
    for (var p = startDay - 1; p >= 0; p--) {
      var prevDay = prevMonthLastDay - p;
      html += '<div class="work-calendar-cell other-month"><div class="work-calendar-date">' + prevDay + '</div></div>';
    }

    // Current month days
    for (var day = 1; day <= daysInMonth; day++) {
      var isToday = day === now.getDate() && currentMonth === now.getMonth() && currentYear === now.getFullYear();
      var dateStr = currentYear + '-' + String(currentMonth + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0');

      var dayTasks = tasks.filter(function (t) {
        var taskDate = t.date || t.deadline;
        if (!taskDate) return false;
        return taskDate.indexOf(dateStr) === 0;
      });

      html += '<div class="work-calendar-cell' + (isToday ? ' today' : '') + '">' +
        '<div class="work-calendar-date' + (isToday ? ' today' : '') + '">' + day + '</div>';

      for (var t = 0; t < Math.min(dayTasks.length, 3); t++) {
        var task = dayTasks[t];
        var statusClass = task.status || 'new';
        html += '<div class="work-calendar-event ' + statusClass + '" title="' + escapeHtml(task.title) + '">' + escapeHtml(task.title) + '</div>';
      }

      if (dayTasks.length > 3) {
        html += '<div class="work-calendar-event" style="background:#e2e8f0;color:#64748b;">+' + (dayTasks.length - 3) + ' more</div>';
      }

      html += '</div>';
    }

    // Next month days
    var totalCells = startDay + daysInMonth;
    var remainingCells = 7 - (totalCells % 7);
    if (remainingCells < 7) {
      for (var n = 1; n <= remainingCells; n++) {
        html += '<div class="work-calendar-cell other-month"><div class="work-calendar-date">' + n + '</div></div>';
      }
    }

    html += '</div>';
    container.innerHTML = html;
  }

  function getFilteredTasks() {
    var state = getWorkViewState();
    var tasks = state.tasks || [];

    // Apply status filter (from tabs)
    if (state.statusFilter && state.statusFilter !== 'all') {
      tasks = tasks.filter(function (t) {
        return t.status === state.statusFilter || t.state === state.statusFilter;
      });
    }

    // Apply status filter (from dropdown)
    if (state.filterStatus) {
      tasks = tasks.filter(function (t) {
        return t.status === state.filterStatus || t.state === state.filterStatus;
      });
    }

    // Apply search query
    if (state.searchQuery) {
      var q = state.searchQuery.toLowerCase();
      tasks = tasks.filter(function (t) {
        return (
          (t.title && t.title.toLowerCase().indexOf(q) >= 0) ||
          (t.id && String(t.id).indexOf(q) >= 0) ||
          (t.customerName && t.customerName.toLowerCase().indexOf(q) >= 0)
        );
      });
    }

    // Apply assignee filter
    if (state.filterAssignee) {
      tasks = tasks.filter(function (t) {
        return t.assigneeId == state.filterAssignee || t.userId == state.filterAssignee;
      });
    }

    // Apply date range filter
    if (state.filterDateFrom) {
      tasks = tasks.filter(function (t) {
        var taskDate = t.date || t.createdAt;
        if (!taskDate) return true;
        return taskDate >= state.filterDateFrom;
      });
    }
    if (state.filterDateTo) {
      tasks = tasks.filter(function (t) {
        var taskDate = t.date || t.createdAt;
        if (!taskDate) return true;
        return taskDate <= state.filterDateTo;
      });
    }

    return tasks;
  }

  function renderCalendar() {
    var el = document.getElementById('page-calendar');
    if (!el) return;
    var state = getCalendarViewState();
    state.companyId = getSelectedBranchId();

    el.innerHTML =
      '<section class="tds-card calendar-page">' +
      '<div class="calendar-title-bar">' +
      '<h2 class="calendar-page-title">Lịch hẹn</h2>' +
      '<div class="calendar-title-actions">' +
      '<button class="tds-btn tds-btn-primary calendar-add-btn" id="calendar-add-btn">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>' +
      ' Thêm mới' +
      '</button>' +
      '<button class="tds-btn tds-btn-secondary calendar-export-btn" id="calendar-export-btn">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>' +
      ' Xuất Excel' +
      '</button>' +
      '</div>' +
      '</div>' +
      '<div class="calendar-toolbar">' +
      '<div class="calendar-toolbar-left">' +
      '<div class="calendar-view-switch">' +
      '<button class="tds-btn tds-btn-sm ' + (state.view === 'day' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-view="day">Ngày</button>' +
      '<button class="tds-btn tds-btn-sm ' + (state.view === 'week' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-view="week">Tuần</button>' +
      '<button class="tds-btn tds-btn-sm ' + (state.view === 'month' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-view="month">Tháng</button>' +
      '</div>' +
      '<div class="calendar-nav-group">' +
      '<button class="tds-btn tds-btn-secondary tds-btn-icon" data-calendar-nav="prev" title="Trước">&lsaquo;</button>' +
      '<span class="calendar-date-label" id="calendar-date-label"></span>' +
      '<button class="tds-btn tds-btn-secondary tds-btn-icon" data-calendar-nav="next" title="Sau">&rsaquo;</button>' +
      '<button class="tds-btn tds-btn-secondary" data-calendar-nav="today">Hôm nay</button>' +
      '</div>' +
      '</div>' +
      '<div class="calendar-toolbar-right">' +
      '<div class="calendar-search-box">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' +
      '<input type="text" class="calendar-search-input" id="calendar-search-input" placeholder="Tìm kiếm theo họ tên, số điện thoại khách hàng" />' +
      '</div>' +
      '<div class="calendar-filter-icons">' +
      '<button class="tds-btn tds-btn-ghost tds-btn-icon calendar-filter-icon" title="Bác sĩ">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' +
      '</button>' +
      '<button class="tds-btn tds-btn-ghost tds-btn-icon calendar-filter-icon" title="Thời gian">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' +
      '</button>' +
      '<button class="tds-btn tds-btn-ghost tds-btn-icon calendar-filter-icon calendar-filter-badge" title="Dịch vụ">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>' +
      '</button>' +
      '<button class="tds-btn tds-btn-ghost tds-btn-icon calendar-filter-icon" title="Danh sách">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>' +
      '</button>' +
      '</div>' +
      '</div>' +
      '</div>' +
      '<div id="calendar-body">' + renderLoadingState('Đang tải lịch hẹn...') + '</div>' +
      '</section>';

    bindCalendarInteractions(el);
    loadCalendarViewData();
  }

  function getReceptionViewState() {
    if (!APP.reception) {
      APP.reception = {
        date: TODAY_ISO,
        companyId: getSelectedBranchId(),
        data: null,
        requestSeq: 0,
        busyById: {},
      };
    }
    if (typeof APP.reception.date !== 'string' || APP.reception.date.length < 10) {
      APP.reception.date = formatDateInput(APP.reception.date || new Date());
    }
    if (typeof APP.reception.requestSeq !== 'number' || !isFinite(APP.reception.requestSeq)) {
      APP.reception.requestSeq =
        typeof APP.reception.requestId === 'number' && isFinite(APP.reception.requestId)
          ? APP.reception.requestId
          : 0;
    }
    return APP.reception;
  }

  function getCalendarViewState() {
    if (!APP.calendar) {
      APP.calendar = {
        date: TODAY_ISO,
        companyId: getSelectedBranchId(),
        view: 'day',
        segment: 'all',
        dayData: null,
        weekData: null,
        monthData: null,
        requestSeq: 0,
        itemMap: {},
        searchQuery: '',
        filters: {
          doctor: null,
          time: null,
          service: null,
        },
      };
    }
    if (typeof APP.calendar.date !== 'string' || APP.calendar.date.length < 10) {
      APP.calendar.date = formatDateInput(APP.calendar.date || new Date());
    }
    if (typeof APP.calendar.requestSeq !== 'number' || !isFinite(APP.calendar.requestSeq)) {
      APP.calendar.requestSeq =
        typeof APP.calendar.requestId === 'number' && isFinite(APP.calendar.requestId)
          ? APP.calendar.requestId
          : 0;
    }
    return APP.calendar;
  }

  function bindReceptionInteractions(root) {
    var state = getReceptionViewState();

    var prevBtn = root.querySelector('[data-reception-nav="prev"]');
    var todayBtn = root.querySelector('[data-reception-nav="today"]');
    var nextBtn = root.querySelector('[data-reception-nav="next"]');

    if (prevBtn) {
      prevBtn.addEventListener('click', function () {
        state.date = shiftDateInput(state.date, -1);
        loadReceptionBoardData();
      });
    }
    if (todayBtn) {
      todayBtn.addEventListener('click', function () {
        state.date = TODAY_ISO;
        loadReceptionBoardData();
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        state.date = shiftDateInput(state.date, 1);
        loadReceptionBoardData();
      });
    }

    var board = root.querySelector('#reception-board');
    if (!board) return;
    board.addEventListener('click', function (event) {
      var actionBtn = event.target.closest('[data-reception-next]');
      if (actionBtn) {
        event.preventDefault();
        var appointmentId = actionBtn.getAttribute('data-appointment-id');
        var nextState = actionBtn.getAttribute('data-reception-next');
        if (appointmentId && nextState) {
          transitionReceptionAppointmentState(appointmentId, nextState);
        }
        return;
      }

      var detailBtn = event.target.closest('[data-reception-detail]');
      if (detailBtn) {
        event.preventDefault();
        var detailId = detailBtn.getAttribute('data-appointment-id');
        var detailItem = findReceptionAppointmentById(detailId);
        if (detailItem) showAppointmentDetailModal(detailItem);
        return;
      }

      var card = event.target.closest('.reception-card');
      if (!card) return;
      var cardId = card.getAttribute('data-appointment-id');
      var cardItem = findReceptionAppointmentById(cardId);
      if (cardItem) showAppointmentDetailModal(cardItem);
    });
  }

  async function loadReceptionBoardData() {
    var state = getReceptionViewState();
    state.companyId = getSelectedBranchId();

    var label = document.getElementById('reception-date-label');
    if (label) label.textContent = formatDateLongVN(state.date);

    var summary = document.getElementById('reception-summary');
    var board = document.getElementById('reception-board');
    if (summary) summary.innerHTML = '';
    if (board) board.innerHTML = renderLoadingState('Đang tải lịch tiếp nhận...');

    var requestSeq = ++state.requestSeq;
    var payload = null;
    try {
      payload = await api('/api/appointments/reception' + toQueryString({
        date: state.date,
        companyId: state.companyId || '',
      }));
    } catch (_err) {
      payload = null;
    }

    if (requestSeq !== state.requestSeq) return;
    if (!payload) {
      if (board) board.innerHTML = renderErrorState('Không tải được dữ liệu tiếp nhận.');
      showToast('error', 'Không tải được dữ liệu tiếp nhận.');
      return;
    }

    state.data = normalizeReceptionData(payload);
    renderReceptionBoard();
  }

  function normalizeReceptionData(payload) {
    var groups = payload && payload.groups ? payload.groups : {};
    var waiting = normalizeAppointmentList(groups.waiting);
    var inProgress = normalizeAppointmentList(groups.in_progress);
    var done = normalizeAppointmentList(groups.done);

    waiting.sort(sortAppointmentsByStart);
    inProgress.sort(sortAppointmentsByStart);
    done.sort(sortAppointmentsByStart);

    return {
      date: payload && payload.date ? payload.date : TODAY_ISO,
      groups: {
        waiting: waiting,
        in_progress: inProgress,
        done: done,
      },
      totals: {
        waiting: waiting.length,
        in_progress: inProgress.length,
        done: done.length,
        all: waiting.length + inProgress.length + done.length,
      },
    };
  }

  function renderReceptionBoard() {
    var state = getReceptionViewState();
    if (!state.data) return;
    var summary = document.getElementById('reception-summary');
    var board = document.getElementById('reception-board');
    if (!summary || !board) return;

    summary.innerHTML =
      '<div class="reception-stat waiting"><span>Chờ khám</span><strong>' + formatNumber(state.data.totals.waiting) + '</strong></div>' +
      '<div class="reception-stat in-progress"><span>Đang khám</span><strong>' + formatNumber(state.data.totals.in_progress) + '</strong></div>' +
      '<div class="reception-stat done"><span>Hoàn thành</span><strong>' + formatNumber(state.data.totals.done) + '</strong></div>' +
      '<div class="reception-stat all"><span>Tổng</span><strong>' + formatNumber(state.data.totals.all) + '</strong></div>';

    if (state.data.totals.all <= 0) {
      board.innerHTML = renderEmptyState('Không có lịch hẹn trong ngày đã chọn.');
      return;
    }

    board.innerHTML =
      '<div class="reception-columns">' +
      renderReceptionColumn('waiting', 'Chờ khám', state.data.groups.waiting) +
      renderReceptionColumn('in_progress', 'Đang khám', state.data.groups.in_progress) +
      renderReceptionColumn('done', 'Hoàn thành', state.data.groups.done) +
      '</div>';
  }

  function renderReceptionColumn(groupKey, label, items) {
    var cards = '';
    for (var i = 0; i < items.length; i++) {
      cards += renderReceptionCard(groupKey, items[i]);
    }
    if (!cards) {
      cards = '<div class="reception-column-empty">Không có bệnh nhân</div>';
    }

    var groupClass = groupKey === 'in_progress' ? 'in-progress' : groupKey;
    return (
      '<section class="reception-column ' + groupClass + '">' +
      '<header class="reception-column-head">' +
      '<h3>' + escapeHtml(label) + '</h3>' +
      '<span class="tds-badge tds-badge-gray">' + formatNumber(items.length) + '</span>' +
      '</header>' +
      '<div class="reception-card-list">' + cards + '</div>' +
      '</section>'
    );
  }

  function renderReceptionCard(groupKey, item) {
    var statusMeta = appointmentStatusMeta(item.state);
    var initials = getUserInitials(item.patientName || 'BN');
    var services = item.services.length ? item.services.slice(0, 2).join(' • ') : 'Chưa có dịch vụ';
    var action = receptionActionByGroup(groupKey);
    var busy = !!getReceptionViewState().busyById[item.id];

    var actionHtml = '';
    if (action) {
      actionHtml =
        '<button class="tds-btn tds-btn-sm ' + action.buttonClass + '" data-reception-next="' + escapeHtml(action.nextState) + '" data-appointment-id="' + escapeHtml(item.id) + '" ' + (busy ? 'disabled' : '') + '>' +
        escapeHtml(action.label) +
        '</button>';
    }

    return (
      '<article class="reception-card" data-appointment-id="' + escapeHtml(item.id) + '">' +
      '<div class="reception-card-head">' +
      '<div class="reception-avatar">' + escapeHtml(initials) + '</div>' +
      '<div class="reception-card-patient">' +
      '<h4>' + escapeHtml(item.patientName || 'Không rõ tên') + '</h4>' +
      '<p>' + escapeHtml(item.doctorName || 'Chưa chỉ định bác sĩ') + '</p>' +
      '</div>' +
      '<span class="tds-badge ' + statusMeta.badgeClass + '">' + escapeHtml(statusMeta.label) + '</span>' +
      '</div>' +
      '<div class="reception-card-meta">' +
      '<span>' + escapeHtml(item.startTime || '--:--') + '</span>' +
      '<span>' + escapeHtml(services) + '</span>' +
      '</div>' +
      '<div class="reception-card-actions">' +
      actionHtml +
      '<button class="tds-btn tds-btn-ghost tds-btn-sm" data-reception-detail="1" data-appointment-id="' + escapeHtml(item.id) + '">Chi tiết</button>' +
      '</div>' +
      '</article>'
    );
  }

  function receptionActionByGroup(groupKey) {
    if (groupKey === 'waiting') {
      return { label: 'Bắt đầu khám', nextState: 'in_progress', buttonClass: 'tds-btn-primary' };
    }
    if (groupKey === 'in_progress') {
      return { label: 'Hoàn thành', nextState: 'done', buttonClass: 'tds-btn-secondary' };
    }
    return null;
  }

  function findReceptionAppointmentById(id) {
    var state = getReceptionViewState();
    if (!state.data) return null;
    var keys = ['waiting', 'in_progress', 'done'];
    for (var i = 0; i < keys.length; i++) {
      var rows = state.data.groups[keys[i]] || [];
      for (var j = 0; j < rows.length; j++) {
        if (String(rows[j].id) === String(id)) return rows[j];
      }
    }
    return null;
  }

  async function transitionReceptionAppointmentState(id, nextState) {
    var state = getReceptionViewState();
    if (!state.data) return;

    state.busyById[id] = true;
    renderReceptionBoard();

    var payload = null;
    try {
      payload = await api('/api/appointments/' + encodeURIComponent(id) + '/state', {
        method: 'PATCH',
        body: JSON.stringify({ state: nextState }),
      });
    } catch (_err) {
      payload = null;
    }

    delete state.busyById[id];

    if (!payload) {
      renderReceptionBoard();
      showToast('error', 'Không thể cập nhật trạng thái lịch hẹn.');
      return;
    }

    updateReceptionItemLocal(normalizeAppointmentItem(payload));
    renderReceptionBoard();
    showToast('success', 'Đã cập nhật trạng thái lịch hẹn.');
  }

  function updateReceptionItemLocal(item) {
    var state = getReceptionViewState();
    if (!state.data) return;

    var groups = state.data.groups;
    var keys = ['waiting', 'in_progress', 'done'];
    for (var i = 0; i < keys.length; i++) {
      groups[keys[i]] = (groups[keys[i]] || []).filter(function (row) {
        return String(row.id) !== String(item.id);
      });
    }

    var bucket = receptionBucketForStatus(item.state);
    groups[bucket].push(item);
    groups[bucket].sort(sortAppointmentsByStart);

    state.data.totals.waiting = groups.waiting.length;
    state.data.totals.in_progress = groups.in_progress.length;
    state.data.totals.done = groups.done.length;
    state.data.totals.all = groups.waiting.length + groups.in_progress.length + groups.done.length;
  }

  function receptionBucketForStatus(status) {
    var key = normalizeAppointmentStatus(status);
    if (key === 'in_progress') return 'in_progress';
    if (key === 'done' || key === 'cancel') return 'done';
    return 'waiting';
  }

  function bindCalendarInteractions(root) {
    var state = getCalendarViewState();

    var viewBtns = root.querySelectorAll('[data-calendar-view]');
    for (var i = 0; i < viewBtns.length; i++) {
      viewBtns[i].addEventListener('click', function () {
        var nextView = this.getAttribute('data-calendar-view') || 'day';
        if (nextView === state.view) return;
        state.view = nextView;
        renderCalendar();
      });
    }

    var segBtns = root.querySelectorAll('[data-calendar-segment]');
    for (var j = 0; j < segBtns.length; j++) {
      segBtns[j].addEventListener('click', function () {
        var nextSegment = this.getAttribute('data-calendar-segment') || 'all';
        if (nextSegment === state.segment) return;
        state.segment = nextSegment;
        renderCalendar();
      });
    }

    var prevBtn = root.querySelector('[data-calendar-nav="prev"]');
    var todayBtn = root.querySelector('[data-calendar-nav="today"]');
    var nextBtn = root.querySelector('[data-calendar-nav="next"]');

    if (prevBtn) {
      prevBtn.addEventListener('click', function () {
        if (state.view === 'month') {
          state.date = shiftMonthInput(state.date, -1);
        } else if (state.view === 'week') {
          state.date = shiftDateInput(state.date, -7);
        } else {
          state.date = shiftDateInput(state.date, -1);
        }
        loadCalendarViewData();
      });
    }
    if (todayBtn) {
      todayBtn.addEventListener('click', function () {
        state.date = TODAY_ISO;
        loadCalendarViewData();
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        if (state.view === 'month') {
          state.date = shiftMonthInput(state.date, 1);
        } else if (state.view === 'week') {
          state.date = shiftDateInput(state.date, 7);
        } else {
          state.date = shiftDateInput(state.date, 1);
        }
        loadCalendarViewData();
      });
    }

    var body = root.querySelector('#calendar-body');
    if (!body) return;
    body.addEventListener('click', function (event) {
      var apptBtn = event.target.closest('[data-calendar-appointment]');
      if (apptBtn) {
        var apptId = apptBtn.getAttribute('data-calendar-appointment');
        var item = state.itemMap[apptId];
        if (item) showAppointmentDetailModal(item);
        return;
      }

      var dayBtn = event.target.closest('[data-calendar-day]');
      if (dayBtn && state.view === 'month') {
        var targetDate = dayBtn.getAttribute('data-calendar-day');
        if (!targetDate) return;
        state.date = targetDate;
        state.view = 'day';
        renderCalendar();
      }
    });

    var addBtn = root.querySelector('#calendar-add-btn');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        showAppointmentFormModal(null);
      });
    }

    var exportBtn = root.querySelector('#calendar-export-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        var companyId = getSelectedBranchId();
        var href = '/api/export/appointments?limit=500' + (companyId ? '&companyId=' + encodeURIComponent(companyId) : '');
        window.open(href, '_blank');
      });
    }

    // Search input handler
    var searchInput = root.querySelector('#calendar-search-input');
    if (searchInput) {
      var searchTimeout;
      searchInput.addEventListener('input', function () {
        var query = this.value.trim().toLowerCase();
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function () {
          state.searchQuery = query;
          // Re-render current view with filter
          if (state.view === 'day' && state.dayData) {
            var filteredData = filterCalendarData(state.dayData, state);
            document.getElementById('calendar-body').innerHTML = renderCalendarDayMarkup(filteredData);
          } else if (state.view === 'week' && state.weekData) {
            var filteredWeek = filterCalendarWeekData(state.weekData, state);
            document.getElementById('calendar-body').innerHTML = renderCalendarWeekMarkup(filteredWeek);
          } else if (state.view === 'month' && state.monthData) {
            var filteredMonth = filterCalendarMonthData(state.monthData, state);
            document.getElementById('calendar-body').innerHTML = renderCalendarMonthMarkup(filteredMonth);
          }
        }, 300);
      });
    }

    // Filter button handlers
    var filterBtns = root.querySelectorAll('.calendar-filter-icon');
    for (var k = 0; k < filterBtns.length; k++) {
      filterBtns[k].addEventListener('click', function (e) {
        var btn = e.currentTarget;
        var title = btn.getAttribute('title') || '';
        // Show filter dropdown based on button title
        if (title === 'Bác sĩ') {
          showCalendarDoctorFilter(btn, state);
        } else if (title === 'Thời gian') {
          showCalendarTimeFilter(btn, state);
        } else if (title === 'Dịch vụ') {
          showCalendarServiceFilter(btn, state);
        } else if (title === 'Danh sách') {
          showCalendarListFilter(btn, state);
        }
      });
    }
  }

  // Filter functions for calendar data
  function filterCalendarData(data, state) {
    if (!data || !data.items) return data;
    var query = state.searchQuery;
    var filters = state.filters;
    var filtered = data.items.filter(function (item) {
      // Search filter
      if (query) {
        var nameMatch = item.customerName && item.customerName.toLowerCase().indexOf(query) >= 0;
        var phoneMatch = item.customerPhone && item.customerPhone.toLowerCase().indexOf(query) >= 0;
        if (!nameMatch && !phoneMatch) return false;
      }
      // Doctor filter
      if (filters.doctor && item.doctorId !== filters.doctor) return false;
      // Time filter
      if (filters.time) {
        var hour = parseInt(item.startTime ? item.startTime.split(':')[0] : '0', 10);
        if (filters.time === 'morning' && (hour < 8 || hour >= 12)) return false;
        if (filters.time === 'afternoon' && (hour < 12 || hour >= 17)) return false;
        if (filters.time === 'evening' && (hour < 17 || hour >= 21)) return false;
      }
      // Service filter
      if (filters.service && item.serviceId !== filters.service) return false;
      return true;
    });
    return { items: filtered, doctors: data.doctors, services: data.services };
  }

  function filterCalendarWeekData(data, state) {
    if (!data || !data.days) return data;
    var query = state.searchQuery;
    var filters = state.filters;
    data.days.forEach(function (day) {
      if (day.items) {
        day.items = day.items.filter(function (item) {
          if (query) {
            var nameMatch = item.customerName && item.customerName.toLowerCase().indexOf(query) >= 0;
            var phoneMatch = item.customerPhone && item.customerPhone.toLowerCase().indexOf(query) >= 0;
            if (!nameMatch && !phoneMatch) return false;
          }
          if (filters.doctor && item.doctorId !== filters.doctor) return false;
          if (filters.time) {
            var hour = parseInt(item.startTime ? item.startTime.split(':')[0] : '0', 10);
            if (filters.time === 'morning' && (hour < 8 || hour >= 12)) return false;
            if (filters.time === 'afternoon' && (hour < 12 || hour >= 17)) return false;
            if (filters.time === 'evening' && (hour < 17 || hour >= 21)) return false;
          }
          if (filters.service && item.serviceId !== filters.service) return false;
          return true;
        });
      }
    });
    return data;
  }

  function filterCalendarMonthData(data, state) {
    if (!data || !data.days) return data;
    var query = state.searchQuery;
    var filters = state.filters;
    data.days.forEach(function (day) {
      if (day.items) {
        day.items = day.items.filter(function (item) {
          if (query) {
            var nameMatch = item.customerName && item.customerName.toLowerCase().indexOf(query) >= 0;
            var phoneMatch = item.customerPhone && item.customerPhone.toLowerCase().indexOf(query) >= 0;
            if (!nameMatch && !phoneMatch) return false;
          }
          if (filters.doctor && item.doctorId !== filters.doctor) return false;
          if (filters.time) {
            var hour = parseInt(item.startTime ? item.startTime.split(':')[0] : '0', 10);
            if (filters.time === 'morning' && (hour < 8 || hour >= 12)) return false;
            if (filters.time === 'afternoon' && (hour < 12 || hour >= 17)) return false;
            if (filters.time === 'evening' && (hour < 17 || hour >= 21)) return false;
          }
          if (filters.service && item.serviceId !== filters.service) return false;
          return true;
        });
      }
    });
    return data;
  }

  // Filter dropdown functions
  function showCalendarDoctorFilter(btn, state) {
    var menu = createFilterDropdown([
      { value: '', label: 'Tất cả bác sĩ' },
      { value: 'doctor_1', label: 'BS. Minh' },
      { value: 'doctor_2', label: 'BS. Lan' },
      { value: 'doctor_3', label: 'BS. Hùng' },
    ], state.filters.doctor, function (value) {
      state.filters.doctor = value || null;
      loadCalendarViewData();
    });
    showFilterMenu(btn, menu);
  }

  function showCalendarTimeFilter(btn, state) {
    var menu = createFilterDropdown([
      { value: '', label: 'Tất cả thời gian' },
      { value: 'morning', label: 'Sáng (8:00 - 12:00)' },
      { value: 'afternoon', label: 'Chiều (12:00 - 17:00)' },
      { value: 'evening', label: 'Tối (17:00 - 21:00)' },
    ], state.filters.time, function (value) {
      state.filters.time = value || null;
      loadCalendarViewData();
    });
    showFilterMenu(btn, menu);
  }

  function showCalendarServiceFilter(btn, state) {
    var menu = createFilterDropdown([
      { value: '', label: 'Tất cả dịch vụ' },
      { value: 'service_1', label: 'Niềng răng' },
      { value: 'service_2', label: 'Tẩy trắng' },
      { value: 'service_3', label: 'Cạo vôi' },
    ], state.filters.service, function (value) {
      state.filters.service = value || null;
      loadCalendarViewData();
    });
    showFilterMenu(btn, menu);
  }

  function showCalendarListFilter(btn, state) {
    // Toggle between views or show list view
    var menu = createFilterDropdown([
      { value: 'day', label: 'Ngày' },
      { value: 'week', label: 'Tuần' },
      { value: 'month', label: 'Tháng' },
    ], state.view, function (value) {
      if (value && value !== state.view) {
        state.view = value;
        renderCalendar();
      }
    });
    showFilterMenu(btn, menu);
  }

  function createFilterDropdown(options, selectedValue, onSelect) {
    var html = '<div class="calendar-filter-dropdown">';
    options.forEach(function (opt) {
      var isSelected = opt.value === selectedValue || (opt.value === '' && !selectedValue);
      html += '<div class="calendar-filter-option' + (isSelected ? ' active' : '') + '" data-value="' + escapeHtml(opt.value) + '">' + escapeHtml(opt.label) + '</div>';
    });
    html += '</div>';
    // Attach click handlers after rendering
    setTimeout(function () {
      var dropdown = document.querySelector('.calendar-filter-dropdown');
      if (dropdown) {
        dropdown.querySelectorAll('.calendar-filter-option').forEach(function (item) {
          item.addEventListener('click', function () {
            var val = this.getAttribute('data-value');
            onSelect(val);
            closeFilterMenus();
          });
        });
      }
    }, 0);
    return html;
  }

  function showFilterMenu(btn, menuHtml) {
    closeFilterMenus();
    var menuContainer = document.createElement('div');
    menuContainer.className = 'calendar-filter-menu-container';
    menuContainer.innerHTML = menuHtml;
    btn.parentNode.appendChild(menuContainer);
    // Close on outside click
    var closeHandler = function (e) {
      if (!menuContainer.contains(e.target)) {
        closeFilterMenus();
        document.removeEventListener('click', closeHandler);
      }
    };
    setTimeout(function () {
      document.addEventListener('click', closeHandler);
    }, 0);
  }

  function closeFilterMenus() {
    document.querySelectorAll('.calendar-filter-menu-container').forEach(function (el) {
      el.remove();
    });
  }

  async function loadCalendarViewData() {
    var state = getCalendarViewState();
    state.companyId = getSelectedBranchId();
    state.itemMap = {};
    updateCalendarDateLabel();

    var body = document.getElementById('calendar-body');
    if (!body) return;
    body.innerHTML = renderLoadingState('Đang tải lịch hẹn...');

    var requestSeq = ++state.requestSeq;
    try {
      if (state.view === 'day') {
        var dayData = await fetchCalendarDayData(state.date, state.companyId);
        if (requestSeq !== state.requestSeq) return;
        state.dayData = dayData;
        state.weekData = null;
        state.monthData = null;
        body.innerHTML = renderCalendarDayMarkup(dayData);
        return;
      }

      if (state.view === 'week') {
        var weekData = await fetchCalendarWeekData(state.date, state.companyId);
        if (requestSeq !== state.requestSeq) return;
        state.dayData = null;
        state.weekData = weekData;
        state.monthData = null;
        body.innerHTML = renderCalendarWeekMarkup(weekData);
        return;
      }

      var monthData = await fetchCalendarMonthData(state.date, state.companyId);
      if (requestSeq !== state.requestSeq) return;
      state.dayData = null;
      state.weekData = null;
      state.monthData = monthData;
      body.innerHTML = renderCalendarMonthMarkup(monthData);
    } catch (err) {
      if (requestSeq !== state.requestSeq) return;
      // Render an empty grid on error instead of a blank area
      if (state.view === 'day') {
        body.innerHTML = renderCalendarDayMarkup(null);
      } else if (state.view === 'week') {
        body.innerHTML = renderCalendarWeekMarkup(null);
      } else {
        body.innerHTML = renderCalendarMonthMarkup(null);
      }
      if (window.console && typeof window.console.error === 'function') {
        console.error('calendar-load-error', err);
      }
    }
  }

  async function fetchCalendarDayData(dateInput, companyId) {
    var params = { date: dateInput || TODAY_ISO };
    if (companyId) params.companyId = companyId;

    var payload = null;
    try {
      payload = await api('/api/appointments/calendar' + toQueryString(params));
    } catch (_err) {
      payload = null;
    }
    if (!payload) {
      return {
        date: params.date,
        startHour: 6,
        endHour: 23,
        doctors: [],
        unassigned: [],
      };
    }

    var doctors = await fetchCalendarDoctors(companyId);
    var sourceDoctors = Array.isArray(payload.doctors) ? payload.doctors : [];
    var sourceMap = {};
    for (var i = 0; i < sourceDoctors.length; i++) {
      var doctorId = String(sourceDoctors[i].doctorId || sourceDoctors[i].id || '');
      sourceMap[doctorId] = {
        doctorId: doctorId,
        doctorName: sourceDoctors[i].doctorName || sourceDoctors[i].name || 'Bác sĩ',
        appointments: normalizeAppointmentList(sourceDoctors[i].appointments),
      };
    }

    var merged = [];
    for (var j = 0; j < doctors.length; j++) {
      var id = String(doctors[j].id || '');
      if (sourceMap[id]) {
        merged.push(sourceMap[id]);
        delete sourceMap[id];
      } else {
        merged.push({
          doctorId: id,
          doctorName: doctors[j].name || 'Bác sĩ',
          appointments: [],
        });
      }
    }

    var leftoverKeys = Object.keys(sourceMap);
    for (var x = 0; x < leftoverKeys.length; x++) {
      merged.push(sourceMap[leftoverKeys[x]]);
    }

    merged.sort(function (a, b) {
      return String(a.doctorName || '').localeCompare(String(b.doctorName || ''), 'vi');
    });

    return {
      date: payload.date || params.date,
      startHour: Number(payload.startHour) || 6,
      endHour: Number(payload.endHour) || 23,
      doctors: merged,
      unassigned: normalizeAppointmentList(payload.unassigned),
    };
  }

  async function fetchCalendarDoctors(companyId) {
    var params = {
      isDoctor: true,
      limit: 0,
    };
    if (companyId) params.companyId = companyId;

    var payload = null;
    try {
      payload = await api('/api/employees' + toQueryString(params));
    } catch (_err) {
      payload = null;
    }
    if (!payload) return [];

    var items = safeItems(payload);
    var doctors = [];
    for (var i = 0; i < items.length; i++) {
      if (items[i].isDoctor === false) continue;
      doctors.push({
        id: String(items[i].id || items[i].employeeId || ''),
        name: String(items[i].name || items[i].doctorName || 'Bác sĩ'),
      });
    }
    doctors.sort(function (a, b) {
      return String(a.name || '').localeCompare(String(b.name || ''), 'vi');
    });
    return doctors;
  }

  async function fetchCalendarWeekData(dateInput, companyId) {
    var weekStart = weekStartInput(dateInput || TODAY_ISO);
    var dayValues = [];
    for (var i = 0; i < 7; i++) {
      dayValues.push(shiftDateInput(weekStart, i));
    }

    var dayRows = [];
    for (var j = 0; j < dayValues.length; j++) {
      var dayPayload = await fetchCalendarDayData(dayValues[j], companyId);
      var appointments = [];
      for (var d = 0; d < dayPayload.doctors.length; d++) {
        appointments = appointments.concat(dayPayload.doctors[d].appointments || []);
      }
      appointments = appointments.concat(dayPayload.unassigned || []);
      appointments.sort(sortAppointmentsByStart);
      dayRows.push({
        date: dayPayload.date || dayValues[j],
        appointments: appointments,
      });
    }

    return {
      startHour: 6,
      endHour: 23,
      weekStart: weekStart,
      days: dayRows,
    };
  }

  async function fetchCalendarMonthData(dateInput, companyId) {
    var monthStart = monthStartInput(dateInput || TODAY_ISO);
    var monthEnd = monthEndInput(dateInput || TODAY_ISO);
    var payload = null;
    try {
      payload = await api('/api/appointments' + toQueryString({
        dateFrom: monthStart,
        dateTo: monthEnd,
        limit: 0,
        companyId: companyId || '',
      }));
    } catch (_err) {
      payload = null;
    }

    var items = payload ? normalizeAppointmentList(safeItems(payload)) : [];
    var map = {};
    for (var i = 0; i < items.length; i++) {
      var key = String(items[i].appointmentDate || '').slice(0, 10);
      if (!map[key]) map[key] = [];
      map[key].push(items[i]);
    }

    var gridStart = weekStartInput(monthStart);
    var cells = [];
    for (var idx = 0; idx < 42; idx++) {
      var iso = shiftDateInput(gridStart, idx);
      var dayNum = Number(iso.split('-')[2] || 0);
      cells.push({
        date: iso,
        day: dayNum,
        inMonth: iso.slice(0, 7) === monthStart.slice(0, 7),
        appointments: map[iso] || [],
      });
    }

    return {
      month: monthStart.slice(0, 7),
      cells: cells,
    };
  }

  function renderCalendarDayMarkup(data) {
    var state = getCalendarViewState();
    var startHour = (data && Number(data.startHour)) || 6;
    var endHour = (data && Number(data.endHour)) || 21;
    var pxPerMinute = 1.05;
    var hourHeight = 60 * pxPerMinute;
    var timelineHeight = Math.max((endHour - startHour) * hourHeight, 380);

    var columns = [];
    if (data && data.doctors) {
      for (var i = 0; i < data.doctors.length; i++) {
        var docAppts = filterAppointmentsBySegment(data.doctors[i].appointments, state.segment);
        columns.push({
          name: data.doctors[i].doctorName || 'Bác sĩ',
          appointments: docAppts,
          count: docAppts.length,
        });
      }
      var unassigned = filterAppointmentsBySegment(data.unassigned || [], state.segment);
      if (unassigned.length) {
        columns.push({ name: 'Không xác định', appointments: unassigned, count: unassigned.length });
      }
    }

    // Always show at least one empty column so the time grid renders
    if (!columns.length) {
      columns.push({ name: 'Không xác định', appointments: [], count: 0 });
    }

    var gridTemplate = '72px repeat(' + columns.length + ', minmax(180px, 1fr))';
    var html = '<section class="calendar-grid cal-day">';
    html += '<div class="calendar-grid-head" style="grid-template-columns:' + gridTemplate + '">';
    html += '<div class="calendar-time-head"></div>';
    for (var h = 0; h < columns.length; h++) {
      html += '<div class="calendar-col-head"><strong>' + escapeHtml(columns[h].name) + '</strong>';
      if (columns[h].count > 0) html += '<span>' + formatNumber(columns[h].count) + ' lịch</span>';
      html += '</div>';
    }
    html += '</div>';
    html += '<div class="calendar-grid-body-wrap"><div class="calendar-grid-body" style="grid-template-columns:' + gridTemplate + '">';
    html += '<div class="calendar-time-column" style="height:' + timelineHeight + 'px">' + calendarTimeLabelsMarkup(startHour, endHour, hourHeight) + '</div>';
    for (var c = 0; c < columns.length; c++) {
      var positioned = calendarLayoutAppointments(columns[c].appointments, startHour, endHour, pxPerMinute);
      html += '<div class="calendar-lane-column" style="height:' + timelineHeight + 'px">';
      html += calendarHourLinesMarkup(startHour, endHour, hourHeight);
      html += calendarBlocksMarkup(positioned);
      html += '</div>';
    }
    html += '</div></div></section>';
    return html;
  }

  function renderCalendarWeekMarkup(data) {
    // Always render the week grid structure, even with no data
    if (!data || !Array.isArray(data.days)) {
      // Build a default empty week from current date so the grid is visible
      var _ws = weekStartInput(TODAY_ISO);
      var _emptyDays = [];
      for (var _di = 0; _di < 7; _di++) {
        _emptyDays.push({ date: shiftDateInput(_ws, _di), appointments: [] });
      }
      data = { startHour: 6, endHour: 21, weekStart: _ws, days: _emptyDays };
    }

    var state = getCalendarViewState();
    var weekdayFull = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN'];

    // Collect all unique doctors across the week
    var doctorMap = {};
    var doctorOrder = [];
    for (var di = 0; di < data.days.length; di++) {
      var dayAppts = filterAppointmentsBySegment(data.days[di].appointments, state.segment);
      for (var ai = 0; ai < dayAppts.length; ai++) {
        var docName = dayAppts[ai].doctorName || 'Không xác định';
        if (!doctorMap[docName]) {
          doctorMap[docName] = {};
          doctorOrder.push(docName);
        }
        if (!doctorMap[docName][data.days[di].date]) doctorMap[docName][data.days[di].date] = [];
        doctorMap[docName][data.days[di].date].push(dayAppts[ai]);
      }
    }

    if (!doctorOrder.length) {
      doctorOrder.push('Không xác định');
      doctorMap['Không xác định'] = {};
    }

    // Build week table with doctor rows
    var html = '<section class="cal-week-container">';
    // Header row with day columns
    html += '<div class="cal-week-head">';
    html += '<div class="cal-week-head-label"></div>';
    for (var hi = 0; hi < data.days.length; hi++) {
      var dayDate = parseDateInput(data.days[hi].date);
      var dayNum = String(dayDate.getDate()).padStart(2, '0') + '/' + String(dayDate.getMonth() + 1).padStart(2, '0');
      var dayAllAppts = filterAppointmentsBySegment(data.days[hi].appointments, state.segment);
      var isToday = data.days[hi].date === TODAY_ISO;
      html += '<div class="cal-week-head-day' + (isToday ? ' cal-week-today' : '') + '">';
      html += '<strong>' + weekdayFull[hi] + '</strong>';
      html += '<span>' + dayNum + '</span>';
      html += '<span class="cal-week-head-count">' + formatNumber(dayAllAppts.length) + '</span>';
      html += '</div>';
    }
    html += '</div>';

    // Doctor rows
    html += '<div class="cal-week-body">';
    for (var dri = 0; dri < doctorOrder.length; dri++) {
      var drName = doctorOrder[dri];
      var drTotalCount = 0;
      for (var dck = 0; dck < data.days.length; dck++) {
        drTotalCount += (doctorMap[drName][data.days[dck].date] || []).length;
      }
      html += '<div class="cal-week-row">';
      html += '<div class="cal-week-doctor-label"><span class="cal-week-doctor-name">' + escapeHtml(drName) + '</span>' +
        (drTotalCount > 0 ? '<span class="cal-week-doctor-count">' + formatNumber(drTotalCount) + '</span>' : '') +
        '</div>';
      for (var dj = 0; dj < data.days.length; dj++) {
        var cellAppts = doctorMap[drName][data.days[dj].date] || [];
        cellAppts.sort(sortAppointmentsByStart);
        html += '<div class="cal-week-cell">';
        for (var ci = 0; ci < cellAppts.length; ci++) {
          var appt = cellAppts[ci];
          state.itemMap[appt.id] = appt;
          var statusMeta = appointmentStatusMeta(appt.state);
          html += '<button class="cal-week-appt ' + statusMeta.className + '" data-calendar-appointment="' + escapeHtml(appt.id) + '">';
          html += '<span class="cal-week-appt-name">' + escapeHtml(appt.patientName || 'Không rõ') + '</span>';
          html += '<span class="cal-week-appt-time">' + escapeHtml(appt.startTime || '') + (appt.endTime ? ' - ' + escapeHtml(appt.endTime) : '');
          if (appt.patientPhone) html += '  ' + escapeHtml(appt.patientPhone);
          html += '</span>';
          if (appt.services && appt.services.length) {
            html += '<span class="cal-week-appt-svc">' + escapeHtml(appt.services[0]) + '</span>';
          }
          html += '</button>';
        }
        if (!cellAppts.length) {
          html += '<span class="cal-week-empty"></span>';
        }
        html += '</div>';
      }
      html += '</div>';
    }
    html += '</div></section>';
    return html;
  }

  function renderCalendarMonthMarkup(data) {
    // Always render the month grid structure, even with no data
    if (!data || !Array.isArray(data.cells)) {
      var _ms = monthStartInput(TODAY_ISO);
      var _gs = weekStartInput(_ms);
      var _emptyCells = [];
      for (var _ci = 0; _ci < 42; _ci++) {
        var _iso = shiftDateInput(_gs, _ci);
        _emptyCells.push({ date: _iso, day: Number(_iso.split('-')[2] || 0), inMonth: _iso.slice(0, 7) === _ms.slice(0, 7), appointments: [] });
      }
      data = { month: _ms.slice(0, 7), cells: _emptyCells };
    }
    var state = getCalendarViewState();
    var weekDays = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
    var html = '<section class="cal-month-container">';
    html += '<div class="cal-month-weekdays">';
    for (var i = 0; i < weekDays.length; i++) {
      html += '<div class="cal-month-weekday">' + weekDays[i] + '</div>';
    }
    html += '</div><div class="cal-month-grid">';

    // Count totals for summary
    var totalAppointments = 0;
    var totalDone = 0;
    var totalCancel = 0;

    for (var c = 0; c < data.cells.length; c++) {
      var cell = data.cells[c];
      var filtered = filterAppointmentsBySegment(cell.appointments, state.segment);
      var isToday = cell.date === TODAY_ISO;
      var cellClass = 'cal-month-cell';
      if (!cell.inMonth) cellClass += ' cal-month-out';
      if (isToday) cellClass += ' cal-month-today';

      // Count by status
      var countByStatus = { waiting: 0, in_progress: 0, done: 0, cancel: 0, confirmed: 0, arrived: 0 };
      for (var fi = 0; fi < filtered.length; fi++) {
        var st = normalizeAppointmentStatus(filtered[fi].state);
        if (countByStatus[st] !== undefined) countByStatus[st]++;
        else countByStatus.waiting++;
        if (cell.inMonth) {
          totalAppointments++;
          if (st === 'done') totalDone++;
          if (st === 'cancel') totalCancel++;
        }
      }

      html += '<button class="' + cellClass + '" data-calendar-day="' + escapeHtml(cell.date) + '">';
      html += '<div class="cal-month-day-num">' + formatNumber(cell.day) + '</div>';

      if (filtered.length > 0 && cell.inMonth) {
        var activeCount = countByStatus.waiting + countByStatus.in_progress + countByStatus.confirmed + countByStatus.arrived;
        if (activeCount > 0) {
          html += '<div class="cal-month-stat cal-month-stat-active"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg><span>Đang hẹn: <strong>(' + formatNumber(activeCount) + ')</strong></span></div>';
        }
        if (countByStatus.done > 0) {
          html += '<div class="cal-month-stat cal-month-stat-done"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg><span>Đã đến: <strong>(' + formatNumber(countByStatus.done) + ')</strong></span></div>';
        }
        if (countByStatus.cancel > 0) {
          html += '<div class="cal-month-stat cal-month-stat-cancel"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9l6 6M15 9l-6 6"/></svg><span>Hủy hẹn: <strong>(' + formatNumber(countByStatus.cancel) + ')</strong></span></div>';
        }
      }
      html += '</button>';
    }
    html += '</div>';

    // Summary stats below the grid
    html += '<div class="cal-month-summary">';
    html += '<div class="cal-month-summary-item"><span>Tổng lịch hẹn:</span><strong>' + formatNumber(totalAppointments) + '</strong></div>';
    html += '<div class="cal-month-summary-item"><span>Hoàn thành:</span><strong class="text-success">' + formatNumber(totalDone) + '</strong></div>';
    html += '<div class="cal-month-summary-item"><span>Đã hủy:</span><strong class="text-danger">' + formatNumber(totalCancel) + '</strong></div>';
    html += '</div>';

    html += '</section>';
    return html;
  }

  function calendarTimeLabelsMarkup(startHour, endHour, hourHeight) {
    var html = '';
    for (var hour = startHour; hour <= endHour; hour++) {
      var top = (hour - startHour) * hourHeight;
      html += '<div class="calendar-time-label" style="top:' + top + 'px">' + String(hour).padStart(2, '0') + ':00</div>';
    }
    return html;
  }

  function calendarHourLinesMarkup(startHour, endHour, hourHeight) {
    var html = '';
    for (var hour = startHour; hour <= endHour; hour++) {
      var top = (hour - startHour) * hourHeight;
      html += '<div class="calendar-hour-line" style="top:' + top + 'px"></div>';
    }
    return html;
  }

  function calendarBlocksMarkup(items) {
    var state = getCalendarViewState();
    var html = '';
    for (var i = 0; i < items.length; i++) {
      var row = items[i];
      state.itemMap[row.id] = row;
      var status = appointmentStatusMeta(row.state);
      var svcText = row.services && row.services.length ? row.services[0] : '';
      var isCompact = row._height < 40;
      html +=
        '<button class="calendar-appointment ' + status.className + (isCompact ? ' cal-day-compact' : '') + '" ' +
        'style="top:' + Math.round(row._top) + 'px; height:' + Math.round(row._height) + 'px; left:' + row._left + '%; width:' + row._width + '%;" ' +
        'data-calendar-appointment="' + escapeHtml(row.id) + '">' +
        '<span class="calendar-appointment-name">' + escapeHtml(row.patientName || 'Không rõ tên') + '</span>';
      if (!isCompact) {
        if (svcText) html += '<span class="calendar-appointment-svc">' + escapeHtml(svcText) + '</span>';
        html += '<span class="calendar-appointment-time">' + escapeHtml(row.startTime || '--:--') + (row.endTime ? (' - ' + escapeHtml(row.endTime)) : '') + '</span>';
        if (row.patientPhone) html += '<span class="calendar-appointment-phone">' + escapeHtml(row.patientPhone) + '</span>';
      } else {
        html += '<span class="calendar-appointment-time">' + escapeHtml(row.startTime || '--:--') + '</span>';
      }
      html += '<span class="cal-day-status-dot ' + status.className + '"></span>';
      html += '</button>';
    }
    return html;
  }

  function calendarLayoutAppointments(items, startHour, endHour, pxPerMinute) {
    var rows = normalizeAppointmentList(items);
    rows.sort(sortAppointmentsByStart);

    var laneEnd = [];
    for (var i = 0; i < rows.length; i++) {
      var lane = -1;
      for (var l = 0; l < laneEnd.length; l++) {
        if (laneEnd[l] <= rows[i].startMinute) {
          laneEnd[l] = rows[i].endMinute;
          lane = l;
          break;
        }
      }
      if (lane === -1) {
        laneEnd.push(rows[i].endMinute);
        lane = laneEnd.length - 1;
      }
      rows[i]._lane = lane;
    }

    var lanes = Math.max(laneEnd.length, 1);
    var dayStart = startHour * 60;
    var dayEnd = endHour * 60;
    for (var j = 0; j < rows.length; j++) {
      var start = Math.max(dayStart, rows[j].startMinute);
      var end = Math.min(dayEnd, rows[j].endMinute);
      if (end <= start) end = start + 20;
      rows[j]._top = (start - dayStart) * pxPerMinute;
      rows[j]._height = Math.max((end - start) * pxPerMinute, 24);
      rows[j]._width = 100 / lanes;
      rows[j]._left = rows[j]._lane * rows[j]._width;
    }
    return rows;
  }

  function normalizeAppointmentList(items) {
    if (!Array.isArray(items)) return [];
    var normalized = [];
    for (var i = 0; i < items.length; i++) {
      normalized.push(normalizeAppointmentItem(items[i]));
    }
    return normalized;
  }

  function normalizeAppointmentItem(item) {
    var row = item || {};
    var id = String(row.id || row.appointmentId || '');
    var appointmentDate = String(row.appointmentDate || row.date || TODAY_ISO).slice(0, 10);
    var startTime = String(row.startTime || row.time || '');
    var endTime = String(row.endTime || '');
    var state = normalizeAppointmentStatus(row.state || row.status || 'waiting');
    var services = row.services;
    if (!Array.isArray(services)) {
      services = services ? String(services).split(',') : [];
    }
    services = services.map(function (value) { return String(value || '').trim(); }).filter(Boolean);

    var startMinute = Number(row.startMinute);
    var endMinute = Number(row.endMinute);
    if (!isFinite(startMinute)) startMinute = parseTimeMinute(startTime);
    if (!isFinite(endMinute) || endMinute <= startMinute) endMinute = parseTimeMinute(endTime);
    if (!isFinite(endMinute) || endMinute <= startMinute) endMinute = startMinute + 30;

    return {
      id: id,
      appointmentDate: appointmentDate,
      patientName: String(row.patientName || row.name || ''),
      patientPhone: String(row.patientPhone || row.phone || row.partnerPhone || ''),
      doctorName: String(row.doctorName || row.doctor || ''),
      startTime: startTime,
      endTime: endTime,
      state: state,
      services: services,
      notes: String(row.notes || row.note || ''),
      startMinute: startMinute,
      endMinute: endMinute,
    };
  }

  function filterAppointmentsBySegment(items, segment) {
    if (!Array.isArray(items)) return [];
    if (!segment || segment === 'all') return items.slice();
    return items.filter(function (row) {
      if (segment === 'morning') return row.startMinute >= 360 && row.startMinute < 720;
      if (segment === 'afternoon') return row.startMinute >= 720 && row.startMinute < 1080;
      if (segment === 'evening') return row.startMinute >= 1080 && row.startMinute < 1440;
      return true;
    });
  }

  function sortAppointmentsByStart(a, b) {
    if (a.startMinute !== b.startMinute) return a.startMinute - b.startMinute;
    return String(a.id || '').localeCompare(String(b.id || ''));
  }

  function normalizeAppointmentStatus(value) {
    var state = String(value || '').trim().toLowerCase().replace(/\\s+/g, '_').replace(/-/g, '_');
    if (state === 'inprogress') state = 'in_progress';
    if (state === 'completed') state = 'done';
    if (state === 'cancelled' || state === 'canceled') state = 'cancel';
    return state || 'waiting';
  }

  function appointmentStatusMeta(value) {
    var key = normalizeAppointmentStatus(value);
    var map = {
      waiting: { label: 'Chờ khám', className: 'state-waiting', badgeClass: 'tds-status-waiting' },
      confirmed: { label: 'Đã xác nhận', className: 'state-confirmed', badgeClass: 'tds-status-confirmed' },
      arrived: { label: 'Đã đến', className: 'state-arrived', badgeClass: 'tds-badge-purple' },
      in_progress: { label: 'Đang khám', className: 'state-in-progress', badgeClass: 'tds-status-in-progress' },
      done: { label: 'Hoàn thành', className: 'state-done', badgeClass: 'tds-status-done' },
      cancel: { label: 'Đã hủy', className: 'state-cancel', badgeClass: 'tds-status-cancelled' },
    };
    return map[key] || map.waiting;
  }

  function parseTimeMinute(value) {
    var text = String(value || '').trim();
    if (!text) return 6 * 60;
    var parts = text.split(':');
    if (parts.length < 2) return 6 * 60;
    var hour = Number(parts[0]);
    var minute = Number(parts[1]);
    if (!isFinite(hour) || !isFinite(minute)) return 6 * 60;
    return (hour * 60) + minute;
  }

  function showAppointmentDetailModal(item) {
    var status = appointmentStatusMeta(item.state);
    var servicesHtml = item.services.length
      ? ('<ul class="appointment-detail-list">' + item.services.map(function (svc) {
        return '<li>' + escapeHtml(svc) + '</li>';
      }).join('') + '</ul>')
      : '<p class="text-muted">Chưa có dịch vụ</p>';

    var html =
      '<div class="appointment-detail">' +
      '<div class="appointment-detail-row"><span class="text-secondary">Bệnh nhân</span><strong>' + escapeHtml(item.patientName || 'Không rõ tên') + '</strong></div>' +
      '<div class="appointment-detail-row"><span class="text-secondary">Bác sĩ</span><strong>' + escapeHtml(item.doctorName || 'Chưa chỉ định') + '</strong></div>' +
      '<div class="appointment-detail-row"><span class="text-secondary">Ngày</span><strong>' + escapeHtml(item.appointmentDate || '') + '</strong></div>' +
      '<div class="appointment-detail-row"><span class="text-secondary">Thời gian</span><strong>' + escapeHtml(item.startTime || '--:--') + (item.endTime ? (' - ' + escapeHtml(item.endTime)) : '') + '</strong></div>' +
      '<div class="appointment-detail-row"><span class="text-secondary">Trạng thái</span><span class="tds-badge ' + status.badgeClass + '">' + escapeHtml(status.label) + '</span></div>' +
      '<div class="appointment-detail-services"><span class="text-secondary">Dịch vụ</span>' + servicesHtml + '</div>' +
      '<div class="appointment-detail-notes"><span class="text-secondary">Ghi chú</span><p>' + escapeHtml(item.notes || 'Không có ghi chú') + '</p></div>' +
      '</div>';

    showModal('Chi tiết lịch hẹn', html, { width: 560 });
  }

  // P5: Appointment Form Modal - Create/Edit
  var _appointmentFormCache = { customers: [], doctors: [], services: [], loaded: false };
  async function showAppointmentFormModal(editingItem) {
    var isEditing = !!editingItem;
    var state = getCalendarViewState();
    var selectedDate = state.date || TODAY_ISO;

    // Load customers, doctors, services if not cached
    if (!_appointmentFormCache.loaded) {
      _appointmentFormCache.loaded = true;
      var branchId = getSelectedBranchId();
      try {
        var customersResp = await api('/api/customers?limit=500&offset=0' + (branchId ? '&companyId=' + encodeURIComponent(branchId) : ''));
        _appointmentFormCache.customers = safeItems(customersResp).map(function(c) { return { id: String(c.id || c.customerId || ''), name: c.name || c.fullName || c.phone || '', phone: c.phone || '' }; });
        _appointmentFormCache.customers.sort(function(a, b) { return String(a.name || '').localeCompare(String(b.name || ''), 'vi'); });
      } catch(_e) { _appointmentFormCache.customers = []; }
      try {
        var employeesResp = await api('/api/employees?limit=500&offset=0' + (branchId ? '&companyId=' + encodeURIComponent(branchId) : ''));
        var empItems = safeItems(employeesResp);
        _appointmentFormCache.doctors = [];
        for (var i = 0; i < empItems.length; i++) {
          if (empItems[i].isDoctor === false) continue;
          _appointmentFormCache.doctors.push({ id: String(empItems[i].id || empItems[i].employeeId || ''), name: empItems[i].name || empItems[i].doctorName || 'Bác sĩ' });
        }
        _appointmentFormCache.doctors.sort(function(a, b) { return String(a.name || '').localeCompare(String(b.name || ''), 'vi'); });
      } catch(_e) { _appointmentFormCache.doctors = []; }
      try {
        var productsResp = await api('/api/products?limit=500&offset=0' + (branchId ? '&companyId=' + encodeURIComponent(branchId) : ''));
        _appointmentFormCache.services = safeItems(productsResp).map(function(p) { return { id: String(p.id || p.productId || ''), name: p.name || p.productName || '', price: p.price || 0 }; });
        _appointmentFormCache.services.sort(function(a, b) { return String(a.name || '').localeCompare(String(b.name || ''), 'vi'); });
      } catch(_e) { _appointmentFormCache.services = []; }
    }

    var customers = _appointmentFormCache.customers;
    var doctors = _appointmentFormCache.doctors;
    var services = _appointmentFormCache.services;

    // Generate time slots
    var timeSlots = [];
    for (var h = 7; h <= 20; h++) {
      timeSlots.push(String(h).padStart(2, '0') + ':00');
      if (h < 20) timeSlots.push(String(h).padStart(2, '0') + ':30');
    }

    // Status options
    var statusOptions = [
      { value: 'waiting', label: 'Mới' },
      { value: 'confirmed', label: 'Đã xác nhận' },
      { value: 'arrived', label: 'Đã đến' },
      { value: 'cancel', label: 'Hủy' },
    ];

    // Build form content
    var content = '<form id="appointment-form" class="appointment-form">';

    // Patient dropdown
    content += '<div class="tds-form-group"><label class="tds-label">Bệnh nhân <span class="text-danger">*</span></label>';
    content += '<div class="tds-select-wrapper"><select class="tds-select" id="apf-patient" required>';
    content += '<option value="">-- Chọn bệnh nhân --</option>';
    for (var ci = 0; ci < customers.length; ci++) {
      var c = customers[ci];
      var isSelected = isEditing && editingItem.partnerId === c.id;
      content += '<option value="' + escapeHtml(c.id) + '" data-name="' + escapeHtml(c.name) + '" data-phone="' + escapeHtml(c.phone || '') + '"' + (isSelected ? ' selected' : '') + '>' + escapeHtml(c.name) + (c.phone ? ' - ' + escapeHtml(c.phone) : '') + '</option>';
    }
    content += '</select></div></div>';

    // Doctor dropdown
    content += '<div class="tds-form-group"><label class="tds-label">Bác sĩ</label>';
    content += '<div class="tds-select-wrapper"><select class="tds-select" id="apf-doctor">';
    content += '<option value="">-- Chọn bác sĩ --</option>';
    for (var di = 0; di < doctors.length; di++) {
      var d = doctors[di];
      var docSelected = isEditing && editingItem.doctorId === d.id;
      content += '<option value="' + escapeHtml(d.id) + '" data-name="' + escapeHtml(d.name) + '"' + (docSelected ? ' selected' : '') + '>' + escapeHtml(d.name) + '</option>';
    }
    content += '</select></div></div>';

    // Services multi-select
    content += '<div class="tds-form-group"><label class="tds-label">Dịch vụ</label>';
    content += '<div class="tds-multi-select" id="apf-services">';
    content += '<div class="tds-multi-select-tags" id="apf-services-tags"></div>';
    content += '<div class="tds-multi-select-dropdown" id="apf-services-dropdown" style="display:none">';
    for (var si = 0; si < services.length; si++) {
      var s = services[si];
      var svcChecked = isEditing && editingItem.services && editingItem.services.indexOf(s.name) >= 0;
      content += '<label class="tds-multi-select-item"><input type="checkbox" value="' + escapeHtml(s.name) + '"' + (svcChecked ? ' checked' : '') + '> ' + escapeHtml(s.name) + '</label>';
    }
    content += '</div></div>';
    content += '<button type="button" class="tds-btn tds-btn-sm tds-btn-ghost" id="apf-services-toggle">Chọn dịch vụ</button></div>';

    // Date picker
    content += '<div class="tds-form-group"><label class="tds-label">Ngày <span class="text-danger">*</span></label>';
    content += '<input class="tds-input" type="date" id="apf-date" value="' + (isEditing ? editingItem.appointmentDate : selectedDate) + '" required></div>';

    // Time picker
    content += '<div class="tds-form-group"><label class="tds-label">Giờ hẹn <span class="text-danger">*</span></label>';
    content += '<div class="tds-select-wrapper"><select class="tds-select" id="apf-time" required>';
    content += '<option value="">-- Chọn giờ --</option>';
    for (var ti = 0; ti < timeSlots.length; ti++) {
      var t = timeSlots[ti];
      var timeSelected = isEditing && editingItem.startTime && editingItem.startTime.startsWith(t);
      content += '<option value="' + t + ':00"' + (timeSelected ? ' selected' : '') + '>' + t + '</option>';
    }
    content += '</select></div></div>';

    // Duration display (calculated)
    content += '<div class="tds-form-group"><label class="tds-label">Thời lượng (phút)</label>';
    content += '<input class="tds-input" type="number" id="apf-duration" value="30" min="15" max="480"></div>';

    // Status dropdown
    content += '<div class="tds-form-group"><label class="tds-label">Trạng thái</label>';
    content += '<div class="tds-select-wrapper"><select class="tds-select" id="apf-status">';
    for (var si = 0; si < statusOptions.length; si++) {
      var st = statusOptions[si];
      var statusSelected = isEditing && editingItem.state === st.value;
      content += '<option value="' + st.value + '"' + (statusSelected ? ' selected' : '') + '>' + st.label + '</option>';
    }
    content += '</select></div></div>';

    // Notes textarea
    content += '<div class="tds-form-group"><label class="tds-label">Ghi chú</label>';
    content += '<textarea class="tds-textarea" id="apf-notes" rows="3">' + (isEditing ? (editingItem.notes || '') : '') + '</textarea></div>';

    content += '</form>';

    var footer = '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeModal()">Hủy</button>' +
      '<button class="tds-btn tds-btn-primary" id="apf-save">' + (isEditing ? 'Cập nhật' : 'Tạo mới') + '</button>';

    showModal(isEditing ? 'Cập nhật lịch hẹn' : 'Thêm lịch hẹn', content, {
      width: 640,
      footer: footer,
      onOpen: function(container) {
        // Services multi-select toggle
        var servicesToggle = document.getElementById('apf-services-toggle');
        var servicesDropdown = document.getElementById('apf-services-dropdown');
        if (servicesToggle && servicesDropdown) {
          servicesToggle.addEventListener('click', function() {
            servicesDropdown.style.display = servicesDropdown.style.display === 'none' ? 'block' : 'none';
          });
        }
        // Update selected services tags
        var updateServicesTags = function() {
          var tagsContainer = document.getElementById('apf-services-tags');
          if (!tagsContainer) return;
          var checkboxes = document.querySelectorAll('#apf-services-dropdown input[type="checkbox"]:checked');
          var labels = [];
          for (var i = 0; i < checkboxes.length; i++) {
            labels.push('<span class="tds-tag">' + escapeHtml(checkboxes[i].value) + '</span>');
          }
          tagsContainer.innerHTML = labels.join('');
          // Update duration based on services
          var durationInput = document.getElementById('apf-duration');
          if (durationInput) {
            durationInput.value = Math.max(30, checkboxes.length * 30);
          }
        };
        var serviceCheckboxes = document.querySelectorAll('#apf-services-dropdown input[type="checkbox"]');
        for (var i = 0; i < serviceCheckboxes.length; i++) {
          serviceCheckboxes[i].addEventListener('change', updateServicesTags);
        }
        updateServicesTags();

        // Save button handler
        var saveBtn = document.getElementById('apf-save');
        if (saveBtn) {
          saveBtn.addEventListener('click', async function() {
            var form = document.getElementById('appointment-form');
            if (!form.checkValidity()) {
              form.reportValidity();
              return;
            }

            var patientSelect = document.getElementById('apf-patient');
            var selectedOption = patientSelect.options[patientSelect.selectedIndex];
            var patientName = selectedOption ? (selectedOption.getAttribute('data-name') || '') : '';
            var patientPhone = selectedOption ? (selectedOption.getAttribute('data-phone') || '') : '';

            var doctorSelect = document.getElementById('apf-doctor');
            var docSelectedOption = doctorSelect.options[doctorSelect.selectedIndex];
            var doctorName = docSelectedOption ? (docSelectedOption.getAttribute('data-name') || '') : '';

            var selectedServices = [];
            var svcCheckboxes = document.querySelectorAll('#apf-services-dropdown input[type="checkbox"]:checked');
            for (var i = 0; i < svcCheckboxes.length; i++) {
              selectedServices.push(svcCheckboxes[i].value);
            }

            var dateVal = document.getElementById('apf-date').value;
            var timeVal = document.getElementById('apf-time').value;
            var duration = parseInt(document.getElementById('apf-duration').value, 10) || 30;
            var statusVal = document.getElementById('apf-status').value;
            var notesVal = document.getElementById('apf-notes').value;

            // Calculate end time
            var startParts = timeVal.split(':');
            var startMinutes = parseInt(startParts[0], 10) * 60 + parseInt(startParts[1], 10);
            var endMinutes = startMinutes + duration;
            var endHours = Math.floor(endMinutes / 60);
            var endMins = endMinutes % 60;
            var endTime = String(endHours).padStart(2, '0') + ':' + String(endMins).padStart(2, '0');

            var payload = {
              companyId: getSelectedBranchId() || null,
              partnerId: patientSelect.value || null,
              patientName: patientName,
              patientPhone: patientPhone,
              doctorId: doctorSelect.value || null,
              doctorName: doctorName,
              appointmentDate: dateVal,
              startTime: timeVal + ':00',
              endTime: endTime + ':00',
              state: statusVal,
              services: selectedServices,
              notes: notesVal || null,
            };

            try {
              if (isEditing) {
                await api('/api/appointments/' + encodeURIComponent(editingItem.id), {
                  method: 'PUT',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Đã cập nhật lịch hẹn');
              } else {
                await api('/api/appointments', {
                  method: 'POST',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Đã tạo lịch hẹn mới');
              }
              closeModal();
              loadCalendarViewData();
            } catch (err) {
              showToast('error', (err && err.message) || 'Không thể lưu lịch hẹn');
            }
          });
        }
      },
    });
  }

  function updateCalendarDateLabel() {
    var state = getCalendarViewState();
    var label = document.getElementById('calendar-date-label');
    if (!label) return;

    if (state.view === 'day') {
      label.textContent = formatDateLongVN(state.date);
      return;
    }
    if (state.view === 'week') {
      var weekStart = weekStartInput(state.date);
      var weekEnd = shiftDateInput(weekStart, 6);
      var ws = parseDateInput(weekStart);
      var we = parseDateInput(weekEnd);
      var fmtFull = function(d) { return String(d.getDate()).padStart(2,'0') + '/' + String(d.getMonth()+1).padStart(2,'0') + '/' + d.getFullYear(); };
      label.textContent = fmtFull(ws) + ' - ' + fmtFull(we);
      return;
    }
    label.textContent = 'Tháng ' + Number(state.date.slice(5, 7)) + ' - ' + state.date.slice(0, 4);
  }

  function formatDateLongVN(value) {
    var date = parseDateInput(value);
    return date.toLocaleDateString('vi-VN', {
      weekday: 'long',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  }

  function weekdayShortLabel(value) {
    return parseDateInput(value).toLocaleDateString('vi-VN', { weekday: 'short' });
  }

  function dateShortLabel(value) {
    var dt = parseDateInput(value);
    return String(dt.getDate()).padStart(2, '0') + '/' + String(dt.getMonth() + 1).padStart(2, '0');
  }

  function shiftDateInput(value, days) {
    var dt = parseDateInput(value);
    dt.setDate(dt.getDate() + days);
    return formatDateInput(dt);
  }

  function shiftMonthInput(value, months) {
    var dt = parseDateInput(value);
    dt.setDate(1);
    dt.setMonth(dt.getMonth() + months);
    return formatDateInput(dt);
  }

  function weekStartInput(value) {
    var dt = parseDateInput(value);
    var day = dt.getDay();
    var diff = day === 0 ? -6 : (1 - day);
    dt.setDate(dt.getDate() + diff);
    return formatDateInput(dt);
  }

  function monthStartInput(value) {
    var dt = parseDateInput(value);
    dt.setDate(1);
    return formatDateInput(dt);
  }

  function monthEndInput(value) {
    var dt = parseDateInput(value);
    dt.setMonth(dt.getMonth() + 1);
    dt.setDate(0);
    return formatDateInput(dt);
  }

  function parseDateInput(value) {
    var text = String(value || '').slice(0, 10);
    var dt = text ? new Date(text + 'T00:00:00') : new Date();
    if (isNaN(dt.getTime())) dt = new Date();
    dt.setHours(0, 0, 0, 0);
    return dt;
  }

  function renderLabo() {
    var el = document.getElementById('page-labo');
    if (!el) return;

    el.innerHTML =
      '<div class="labo-page">' +
      '<div class="tds-page-title-row">' +
      '<h2 class="tds-page-title">Quản lý phiếu Labo</h2>' +
      '</div>' +
      '<div class="tds-card labo-shell">' +
      '<div class="tds-table-toolbar labo-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="labo-search" placeholder="Tìm mã phiếu, khách hàng, bác sĩ..." value="' + escapeHtml(APP.labo.search || '') + '">' +
      '<select class="tds-select" id="labo-status-filter">' +
      '<option value="">Tất cả trạng thái</option>' +
      '<option value="draft"' + (APP.labo.status === 'draft' ? ' selected' : '') + '>Nháp</option>' +
      '<option value="confirmed"' + (APP.labo.status === 'confirmed' ? ' selected' : '') + '>Đã xác nhận</option>' +
      '<option value="done"' + (APP.labo.status === 'done' ? ' selected' : '') + '>Hoàn tất</option>' +
      '<option value="cancel"' + (APP.labo.status === 'cancel' ? ' selected' : '') + '>Đã hủy</option>' +
      '</select>' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-secondary tds-btn-sm" id="labo-refresh-btn">Làm mới</button>' +
      '</div>' +
      '</div>' +
      '<div id="labo-table"></div>' +
      '<div id="labo-pagination" class="labo-pagination"></div>' +
      '</div>' +
      '</div>';

    var searchInput = document.getElementById('labo-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.labo.search = searchInput.value.trim();
        APP.labo.page = 1;
        loadLaboData();
      }, 250));
    }

    var statusFilter = document.getElementById('labo-status-filter');
    if (statusFilter) {
      statusFilter.addEventListener('change', function () {
        APP.labo.status = this.value;
        APP.labo.page = 1;
        loadLaboData();
      });
    }

    var refreshBtn = document.getElementById('labo-refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', function () { APP.labo.page = 1; loadLaboData(); });

    loadLaboData();
  }

  async function loadLaboData() {
    APP.labo.loading = true;
    APP.labo.requestId += 1;
    var requestId = APP.labo.requestId;
    renderLaboTable();

    try {
      var query = toQueryString({
        search: APP.labo.search,
        state: APP.labo.status,
        companyId: getSelectedBranchId(),
        limit: APP.labo.pageSize,
        offset: (APP.labo.page - 1) * APP.labo.pageSize,
      });
      var data = await api('/api/sale-orders' + query);
      if (requestId !== APP.labo.requestId) return;
      var items = safeItems(data);
      APP.labo.items = items;
      APP.labo.total = (data && data.total) ? data.total : items.length;
    } catch (_err) {
      if (requestId !== APP.labo.requestId) return;
      APP.labo.items = [];
      APP.labo.total = 0;
    } finally {
      if (requestId === APP.labo.requestId) {
        APP.labo.loading = false;
        renderLaboTable();
        renderLaboPagination();
      }
    }
  }

  function renderLaboTable() {
    var tableWrap = document.getElementById('labo-table');
    if (!tableWrap) return;

    if (APP.labo.loading) {
      tableWrap.innerHTML = renderLoadingState('Đang tải dữ liệu labo...');
      return;
    }

    var rows = APP.labo.items || [];
    if (!rows.length) {
      tableWrap.innerHTML = renderEmptyState('Chưa có dữ liệu phiếu Labo');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr>' +
      '<th>Khách hàng</th>' +
      '<th>Phiếu điều trị</th>' +
      '<th>Dịch vụ</th>' +
      '<th>Bác sĩ</th>' +
      '<th>Chỉ định</th>' +
      '<th>Labo</th>' +
      '<th>Ngày giao</th>' +
      '<th>Trạng thái</th>' +
      '<th>Ngày nhận</th>' +
      '</tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        var laboStatus = item.state || 'draft';
        return (
          '<tr class="labo-row-clickable" data-id="' + escapeHtml(item.id || '') + '">' +
          '<td class="labo-cell-customer">' + escapeHtml(item.partnerName || '\u2014') + '</td>' +
          '<td>' + escapeHtml(item.name || item.id || '\u2014') + '</td>' +
          '<td>' + escapeHtml(item.serviceName || item.productName || '\u2014') + '</td>' +
          '<td>' + escapeHtml(item.doctorName || '\u2014') + '</td>' +
          '<td>' + escapeHtml(item.instruction || item.note || '\u2014') + '</td>' +
          '<td>' + escapeHtml(item.laboName || item.supplierName || '\u2014') + '</td>' +
          '<td>' + escapeHtml(formatDate(item.date || item.dateOrder)) + '</td>' +
          '<td><span class="tds-badge ' + stateBadgeClass(laboStatus) + '">' + escapeHtml(translateState(laboStatus)) + '</span></td>' +
          '<td>' + escapeHtml(formatDate(item.dateReceive || item.dateDone || '')) + '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    // Add click handlers for labo rows
    var laboRows = tableWrap.querySelectorAll('.labo-row-clickable');
    for (var r = 0; r < laboRows.length; r++) {
      laboRows[r].addEventListener('click', function (e) {
        var rowId = this.getAttribute('data-id');
        if (!rowId) return;
        var laboItem = (APP.labo.items || []).find(function (it) { return it.id === rowId; });
        if (laboItem) {
          openLaboOrderDrawer(laboItem);
        }
      });
    }
  }

  function renderLaboPagination() {
    var paginationWrap = document.getElementById('labo-pagination');
    if (!paginationWrap) return;

    var total = APP.labo.total || 0;
    var pageSize = APP.labo.pageSize;
    var page = APP.labo.page;
    var totalPages = Math.max(1, Math.ceil(total / pageSize));
    var start = Math.min((page - 1) * pageSize + 1, total);
    var end = Math.min(page * pageSize, total);

    if (total === 0) { paginationWrap.innerHTML = ''; return; }

    var pageButtons = '';
    var maxVisible = 5;
    var startPage = Math.max(1, page - Math.floor(maxVisible / 2));
    var endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) startPage = Math.max(1, endPage - maxVisible + 1);

    pageButtons += '<button class="partners-page-btn' + (page <= 1 ? ' disabled' : '') + '" data-page="' + (page - 1) + '">&laquo;</button>';
    for (var i = startPage; i <= endPage; i++) {
      pageButtons += '<button class="partners-page-btn' + (i === page ? ' partners-page-active' : '') + '" data-page="' + i + '">' + i + '</button>';
    }
    pageButtons += '<button class="partners-page-btn' + (page >= totalPages ? ' disabled' : '') + '" data-page="' + (page + 1) + '">&raquo;</button>';

    paginationWrap.innerHTML =
      '<div class="partners-pagination-left">' +
      pageButtons +
      '<select class="partners-pagesize-select" id="labo-pagesize">' +
      '<option value="20"' + (pageSize === 20 ? ' selected' : '') + '>20</option>' +
      '<option value="50"' + (pageSize === 50 ? ' selected' : '') + '>50</option>' +
      '<option value="100"' + (pageSize === 100 ? ' selected' : '') + '>100</option>' +
      '</select>' +
      '<span class="partners-pagesize-label">hàng trên trang</span>' +
      '</div>' +
      '<div class="partners-pagination-right">' +
      '<span>' + start + '-' + end + ' của ' + total + ' dòng</span>' +
      '</div>';

    var pageBtns = paginationWrap.querySelectorAll('.partners-page-btn');
    for (var j = 0; j < pageBtns.length; j++) {
      pageBtns[j].addEventListener('click', function () {
        if (this.classList.contains('disabled')) return;
        var p = parseInt(this.getAttribute('data-page'), 10);
        if (p >= 1 && p <= totalPages) {
          APP.labo.page = p;
          loadLaboData();
        }
      });
    }

    var pageSizeSelect = document.getElementById('labo-pagesize');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', function () {
        APP.labo.pageSize = parseInt(this.value, 10) || 20;
        APP.labo.page = 1;
        loadLaboData();
      });
    }
  }

  function renderPurchase() {
    var el = document.getElementById('page-purchase');
    if (!el) return;

    el.innerHTML =
      '<div class="tds-card purchase-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Chứng từ nhập / xuất kho</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="purchase-refresh-btn">Làm mới</button>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<select class="tds-select" id="purchase-type-filter">' +
      '<option value="">Tất cả loại</option>' +
      '<option value="incoming"' + (APP.purchase.pickingType === 'incoming' ? ' selected' : '') + '>Nhập kho</option>' +
      '<option value="outgoing"' + (APP.purchase.pickingType === 'outgoing' ? ' selected' : '') + '>Xuất kho</option>' +
      '</select>' +
      '<select class="tds-select" id="purchase-state-filter">' +
      '<option value="">Tất cả trạng thái</option>' +
      '<option value="draft"' + (APP.purchase.state === 'draft' ? ' selected' : '') + '>Nháp</option>' +
      '<option value="assigned"' + (APP.purchase.state === 'assigned' ? ' selected' : '') + '>Đã xác nhận</option>' +
      '<option value="done"' + (APP.purchase.state === 'done' ? ' selected' : '') + '>Hoàn tất</option>' +
      '</select>' +
      '</div>' +
      '</div>' +
      '<div id="purchase-table"></div>' +
      '</div>';

    var typeFilter = document.getElementById('purchase-type-filter');
    if (typeFilter) {
      typeFilter.addEventListener('change', function () {
        APP.purchase.pickingType = this.value;
        loadPurchaseData();
      });
    }

    var stateFilter = document.getElementById('purchase-state-filter');
    if (stateFilter) {
      stateFilter.addEventListener('change', function () {
        APP.purchase.state = this.value;
        loadPurchaseData();
      });
    }

    var refreshBtn = document.getElementById('purchase-refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', loadPurchaseData);

    loadPurchaseData();
  }

  async function loadPurchaseData() {
    APP.purchase.loading = true;
    APP.purchase.requestId += 1;
    var requestId = APP.purchase.requestId;
    renderPurchaseTable();

    try {
      var query = toQueryString({
        companyId: getSelectedBranchId(),
        pickingType: APP.purchase.pickingType,
        state: APP.purchase.state,
        limit: 50,
        offset: 0,
      });
      var data = await api('/api/stock-pickings' + query);
      if (requestId !== APP.purchase.requestId) return;
      APP.purchase.items = safeItems(data);
    } catch (_err) {
      if (requestId !== APP.purchase.requestId) return;
      APP.purchase.items = [];
    } finally {
      if (requestId === APP.purchase.requestId) {
        APP.purchase.loading = false;
        renderPurchaseTable();
      }
    }
  }

  function renderPurchaseTable() {
    var tableWrap = document.getElementById('purchase-table');
    if (!tableWrap) return;

    if (APP.purchase.loading) {
      tableWrap.innerHTML = renderLoadingState('Đang tải chứng từ kho...');
      return;
    }

    var rows = APP.purchase.items || [];
    if (!rows.length) {
      tableWrap.innerHTML = renderEmptyState('Chưa có chứng từ kho');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr><th>Mã chứng từ</th><th>Ngày</th><th>Loại</th><th>Đối tác</th><th>Chi nhánh</th><th>Trạng thái</th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item, pIdx) {
        return (
          '<tr class="purchase-row-clickable" data-pidx="' + pIdx + '" style="cursor:pointer">' +
          '<td>' + escapeHtml(item.name || item.id || '—') + '</td>' +
          '<td>' + escapeHtml(formatDate(item.date)) + '</td>' +
          '<td>' + escapeHtml(normalizePickingTypeLabel(item.pickingType)) + '</td>' +
          '<td>' + escapeHtml(item.partnerName || '—') + '</td>' +
          '<td>' + escapeHtml(item.companyName || '—') + '</td>' +
          '<td><span class="tds-badge ' + stateBadgeClass(item.state) + '">' + escapeHtml(translateState(item.state)) + '</span></td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    // Wire row clicks to open purchase detail drawer
    var purchaseClickRows = tableWrap.querySelectorAll('.purchase-row-clickable');
    for (var pi = 0; pi < purchaseClickRows.length; pi++) {
      purchaseClickRows[pi].addEventListener('click', function () {
        var idx = parseInt(this.getAttribute('data-pidx'), 10);
        var pItem = rows[idx];
        if (pItem) openPurchaseDetailDrawer(pItem);
      });
    }
  }

  function openPurchaseDetailDrawer(item) {
    var content =
      '<div class="drawer-header">' +
      '<h3>Chi ti\u1ebft ch\u1ee9ng t\u1eeb kho</h3>' +
      '<button class="drawer-close" onclick="TDS.closeDrawer()">&times;</button>' +
      '</div>' +
      '<div class="drawer-content">' +
      '<div class="drawer-field"><label>M\u00e3 ch\u1ee9ng t\u1eeb</label><span>' + escapeHtml(item.name || item.id || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Ng\u00e0y</label><span>' + escapeHtml(formatDate(item.date)) + '</span></div>' +
      '<div class="drawer-field"><label>Lo\u1ea1i</label><span>' + escapeHtml(normalizePickingTypeLabel(item.pickingType)) + '</span></div>' +
      '<div class="drawer-field"><label>\u0110\u1ed1i t\u00e1c</label><span>' + escapeHtml(item.partnerName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Chi nh\u00e1nh</label><span>' + escapeHtml(item.companyName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Tr\u1ea1ng th\u00e1i</label><span class="tds-badge ' + stateBadgeClass(item.state || 'draft') + '">' + escapeHtml(translateState(item.state || 'draft')) + '</span></div>' +
      (item.origin ? '<div class="drawer-field"><label>Ngu\u1ed3n</label><span>' + escapeHtml(item.origin) + '</span></div>' : '') +
      '</div>';
    openDrawer(content, 420);
  }

  function renderWarehouse() {
    var el = document.getElementById('page-warehouse');
    if (!el) return;

    el.innerHTML =
      '<div class="tds-card warehouse-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Biến động tồn kho</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="warehouse-refresh-btn">Làm mới</button>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="warehouse-search" placeholder="Tìm theo sản phẩm hoặc tham chiếu" value="' + escapeHtml(APP.warehouse.search || '') + '">' +
      '</div>' +
      '</div>' +
      '<div id="warehouse-summary"></div>' +
      '<div id="warehouse-table"></div>' +
      '</div>';

    var searchInput = document.getElementById('warehouse-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.warehouse.search = searchInput.value.trim();
        loadWarehouseData();
      }, 250));
    }

    var refreshBtn = document.getElementById('warehouse-refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', loadWarehouseData);

    loadWarehouseData();
  }

  async function loadWarehouseData() {
    APP.warehouse.loading = true;
    APP.warehouse.requestId += 1;
    var requestId = APP.warehouse.requestId;
    renderWarehouseSummary();
    renderWarehouseTable();

    try {
      var query = toQueryString({
        search: APP.warehouse.search,
        companyId: getSelectedBranchId(),
        limit: 50,
        offset: 0,
      });
      var responses = await Promise.all([
        api('/api/stock-moves/summary' + query),
        api('/api/stock-moves' + query),
      ]);
      if (requestId !== APP.warehouse.requestId) return;
      APP.warehouse.summary = safeItems(responses[0]);
      APP.warehouse.items = safeItems(responses[1]);
    } catch (_err) {
      if (requestId !== APP.warehouse.requestId) return;
      APP.warehouse.summary = [];
      APP.warehouse.items = [];
    } finally {
      if (requestId === APP.warehouse.requestId) {
        APP.warehouse.loading = false;
        renderWarehouseSummary();
        renderWarehouseTable();
      }
    }
  }

  function renderWarehouseSummary() {
    var summaryWrap = document.getElementById('warehouse-summary');
    if (!summaryWrap) return;

    if (APP.warehouse.loading) {
      summaryWrap.innerHTML = renderLoadingState('Đang tính tổng tồn kho...');
      return;
    }

    var rows = APP.warehouse.summary || [];
    if (!rows.length) {
      summaryWrap.innerHTML = '';
      return;
    }

    var incoming = 0;
    var outgoing = 0;
    var balance = 0;
    for (var i = 0; i < rows.length; i++) {
      incoming += toNumber(rows[i].incomingQty);
      outgoing += toNumber(rows[i].outgoingQty);
      balance += toNumber(rows[i].balanceQty);
    }

    summaryWrap.innerHTML =
      '<div class="dashboard-grid mt-md">' +
      '<article class="kpi-card"><p class="kpi-label">Tổng nhập</p><h3 class="kpi-value">' + escapeHtml(formatNumber(incoming)) + '</h3></article>' +
      '<article class="kpi-card"><p class="kpi-label">Tổng xuất</p><h3 class="kpi-value">' + escapeHtml(formatNumber(outgoing)) + '</h3></article>' +
      '<article class="kpi-card"><p class="kpi-label">Tồn ròng</p><h3 class="kpi-value">' + escapeHtml(formatNumber(balance)) + '</h3></article>' +
      '</div>';
  }

  function renderWarehouseTable() {
    var tableWrap = document.getElementById('warehouse-table');
    if (!tableWrap) return;

    if (APP.warehouse.loading) {
      tableWrap.innerHTML = renderLoadingState('Đang tải chi tiết tồn kho...');
      return;
    }

    var rows = APP.warehouse.items || [];
    if (!rows.length) {
      tableWrap.innerHTML = renderEmptyState('Chưa có dữ liệu biến động kho');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper mt-md">' +
      '<table class="tds-table">' +
      '<thead><tr><th>Ngày</th><th>Sản phẩm</th><th>Loại</th><th>SL</th><th>Tham chiếu</th><th>Chi nhánh</th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item, wIdx) {
        return (
          '<tr class="warehouse-row-clickable" data-widx="' + wIdx + '" style="cursor:pointer">' +
          '<td>' + escapeHtml(formatDate(item.date)) + '</td>' +
          '<td>' + escapeHtml(item.productName || '—') + '</td>' +
          '<td>' + escapeHtml(normalizePickingTypeLabel(item.pickingType)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatNumber(item.quantity || 0)) + '</td>' +
          '<td>' + escapeHtml(item.reference || '—') + '</td>' +
          '<td>' + escapeHtml(item.companyName || '—') + '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    // Wire row clicks to open warehouse detail drawer
    var whClickRows = tableWrap.querySelectorAll('.warehouse-row-clickable');
    for (var wi = 0; wi < whClickRows.length; wi++) {
      whClickRows[wi].addEventListener('click', function () {
        var idx = parseInt(this.getAttribute('data-widx'), 10);
        var wItem = rows[idx];
        if (wItem) openWarehouseDetailDrawer(wItem);
      });
    }
  }

  function openWarehouseDetailDrawer(item) {
    var content =
      '<div class="drawer-header">' +
      '<h3>Chi ti\u1ebft bi\u1ebfn \u0111\u1ed9ng kho</h3>' +
      '<button class="drawer-close" onclick="TDS.closeDrawer()">&times;</button>' +
      '</div>' +
      '<div class="drawer-content">' +
      '<div class="drawer-field"><label>Ng\u00e0y</label><span>' + escapeHtml(formatDate(item.date)) + '</span></div>' +
      '<div class="drawer-field"><label>S\u1ea3n ph\u1ea9m</label><span>' + escapeHtml(item.productName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Lo\u1ea1i</label><span>' + escapeHtml(normalizePickingTypeLabel(item.pickingType)) + '</span></div>' +
      '<div class="drawer-field"><label>S\u1ed1 l\u01b0\u1ee3ng</label><span>' + escapeHtml(formatNumber(item.quantity || 0)) + '</span></div>' +
      '<div class="drawer-field"><label>Tham chi\u1ebfu</label><span>' + escapeHtml(item.reference || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Chi nh\u00e1nh</label><span>' + escapeHtml(item.companyName || '\u2014') + '</span></div>' +
      (item.locationName ? '<div class="drawer-field"><label>V\u1ecb tr\u00ed kho</label><span>' + escapeHtml(item.locationName) + '</span></div>' : '') +
      '</div>';
    openDrawer(content, 420);
  }

  function renderCashbook() {
    var el = document.getElementById('page-cashbook');
    if (!el) return;

    el.innerHTML =
      '<div class="tds-card cashbook-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Sổ quỹ thu chi</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="cashbook-export-btn">Xuất Excel</button>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-input" id="cashbook-date-from" type="date" value="' + escapeHtml(APP.cashbook.dateFrom || MONTH_START_ISO) + '">' +
      '<input class="tds-input" id="cashbook-date-to" type="date" value="' + escapeHtml(APP.cashbook.dateTo || TODAY_ISO) + '">' +
      '<select class="tds-select" id="cashbook-type-filter">' +
      '<option value="">Tất cả dòng tiền</option>' +
      '<option value="inbound"' + (APP.cashbook.paymentType === 'inbound' ? ' selected' : '') + '>Thu</option>' +
      '<option value="outbound"' + (APP.cashbook.paymentType === 'outbound' ? ' selected' : '') + '>Chi</option>' +
      '</select>' +
      '<button class="tds-btn tds-btn-primary" id="cashbook-apply-btn">Áp dụng</button>' +
      '</div>' +
      '</div>' +
      '<div id="cashbook-table"></div>' +
      '</div>';

    var applyBtn = document.getElementById('cashbook-apply-btn');
    if (applyBtn) {
      applyBtn.addEventListener('click', function () {
        APP.cashbook.dateFrom = getInputValue('cashbook-date-from') || APP.cashbook.dateFrom;
        APP.cashbook.dateTo = getInputValue('cashbook-date-to') || APP.cashbook.dateTo;
        APP.cashbook.paymentType = getInputValue('cashbook-type-filter') || '';
        loadCashbookData();
      });
    }

    var exportBtn = document.getElementById('cashbook-export-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        downloadExcel('payments', {
          companyId: getSelectedBranchId(),
          dateFrom: APP.cashbook.dateFrom,
          dateTo: APP.cashbook.dateTo,
          paymentType: APP.cashbook.paymentType,
          columns: ['date', 'name', 'paymentType', 'partnerName', 'companyName', 'state', 'amount'],
        });
      });
    }

    loadCashbookData();
  }

  async function loadCashbookData() {
    APP.cashbook.loading = true;
    APP.cashbook.requestId += 1;
    var requestId = APP.cashbook.requestId;
    renderCashbookTable();

    try {
      var query = toQueryString({
        companyId: getSelectedBranchId(),
        dateFrom: APP.cashbook.dateFrom,
        dateTo: APP.cashbook.dateTo,
        paymentType: APP.cashbook.paymentType,
        limit: 80,
        offset: 0,
      });
      var data = await api('/api/payments' + query);
      if (requestId !== APP.cashbook.requestId) return;
      APP.cashbook.items = safeItems(data);
    } catch (_err) {
      if (requestId !== APP.cashbook.requestId) return;
      APP.cashbook.items = [];
    } finally {
      if (requestId === APP.cashbook.requestId) {
        APP.cashbook.loading = false;
        renderCashbookTable();
      }
    }
  }

  function renderCashbookTable() {
    var tableWrap = document.getElementById('cashbook-table');
    if (!tableWrap) return;

    if (APP.cashbook.loading) {
      tableWrap.innerHTML = renderLoadingState('Đang tải sổ quỹ...');
      return;
    }

    var rows = APP.cashbook.items || [];
    if (!rows.length) {
      tableWrap.innerHTML = renderEmptyState('Không có dữ liệu thu chi');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr><th>Ngày</th><th>Chứng từ</th><th>Đối tượng</th><th>Loại</th><th>Trạng thái</th><th>Chi nhánh</th><th class="text-right">Số tiền</th><th>Thao tác</th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(formatDate(item.date)) + '</td>' +
          '<td>' + escapeHtml(item.name || '—') + '</td>' +
          '<td>' + escapeHtml(item.partnerName || '—') + '</td>' +
          '<td>' + escapeHtml(normalizePaymentTypeLabel(item.paymentType)) + '</td>' +
          '<td><span class="tds-badge ' + stateBadgeClass(item.state) + '">' + escapeHtml(translateState(item.state)) + '</span></td>' +
          '<td>' + escapeHtml(item.companyName || '—') + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.amount || 0)) + '</td>' +
          '<td><button class="tds-btn tds-btn-ghost tds-btn-sm cashbook-view-btn" data-id="' + escapeHtml(String(item.id)) + '">Xem</button></td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    // Add click handlers for view buttons
    var viewBtns = tableWrap.querySelectorAll('.cashbook-view-btn');
    for (var i = 0; i < viewBtns.length; i++) {
      viewBtns[i].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        var item = rows.find(function (r) { return String(r.id) === String(id); });
        if (item) openPaymentDetailDrawer(item);
      });
    }
  }

  function openPaymentDetailDrawer(item) {
    var isInbound = item.paymentType === 'inbound';
    var amountClass = isInbound ? '' : 'negative';

    var content =
      '<div class="payment-detail-drawer">' +
      '<div class="payment-detail-header">' +
      '<h3 class="payment-detail-title">' + (isInbound ? 'Phiếu thu' : 'Phiếu chi') + '</h3>' +
      '<div class="payment-detail-actions">' +
      '<button class="tds-btn tds-btn-secondary" onclick="window.TDS.closeDrawer()">Đóng</button>' +
      '<button class="tds-btn tds-btn-primary" id="payment-detail-print-btn">In</button>' +
      '</div>' +
      '</div>' +
      '<div class="payment-detail-body">' +
      '<div class="payment-detail-grid">' +
      '<div class="payment-detail-field">' +
      '<span class="payment-detail-label">Số chứng từ</span>' +
      '<span class="payment-detail-value">' + escapeHtml(item.name || '—') + '</span>' +
      '</div>' +
      '<div class="payment-detail-field">' +
      '<span class="payment-detail-label">Ngày</span>' +
      '<span class="payment-detail-value">' + escapeHtml(formatDate(item.date)) + '</span>' +
      '</div>' +
      '<div class="payment-detail-field">' +
      '<span class="payment-detail-label">Đối tượng</span>' +
      '<span class="payment-detail-value">' + escapeHtml(item.partnerName || '—') + '</span>' +
      '</div>' +
      '<div class="payment-detail-field">' +
      '<span class="payment-detail-label">Loại</span>' +
      '<span class="payment-detail-value">' + escapeHtml(normalizePaymentTypeLabel(item.paymentType)) + '</span>' +
      '</div>' +
      '<div class="payment-detail-field">' +
      '<span class="payment-detail-label">Phương thức</span>' +
      '<span class="payment-detail-value">' + escapeHtml(item.journalName || 'Tiền mặt') + '</span>' +
      '</div>' +
      '<div class="payment-detail-field">' +
      '<span class="payment-detail-label">Trạng thái</span>' +
      '<span class="payment-detail-value"><span class="tds-badge ' + stateBadgeClass(item.state) + '">' + escapeHtml(translateState(item.state)) + '</span></span>' +
      '</div>' +
      '<div class="payment-detail-field full-width">' +
      '<span class="payment-detail-label">Nội dung</span>' +
      '<span class="payment-detail-value">' + escapeHtml(item.description || '—') + '</span>' +
      '</div>' +
      '<div class="payment-detail-field full-width">' +
      '<span class="payment-detail-label">Chi nhánh</span>' +
      '<span class="payment-detail-value">' + escapeHtml(item.companyName || '—') + '</span>' +
      '</div>' +
      '</div>' +
      '<div class="payment-detail-divider"></div>' +
      '<div class="payment-detail-field full-width">' +
      '<span class="payment-detail-label">Số tiền</span>' +
      '<span class="payment-detail-value payment-detail-amount ' + amountClass + '">' + formatCurrency(item.amount || 0) + '</span>' +
      '</div>' +
      '</div>' +
      '</div>';

    openDrawer(content, 560);

    // Add print handler
    setTimeout(function () {
      var printBtn = document.getElementById('payment-detail-print-btn');
      if (printBtn) {
        printBtn.addEventListener('click', function () {
          var drawerBody = document.querySelector('.payment-detail-body');
          if (drawerBody) {
            var printWindow = window.open('', '_blank');
            printWindow.document.write('<html><head><title>In phiếu</title>');
            printWindow.document.write('<style>body{font-family:Inter,sans-serif;padding:20px;} .payment-detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;} .payment-detail-label{font-size:12px;color:#64748b;} .payment-detail-value{font-size:14px;} .payment-detail-amount{font-size:24px;font-weight:600;color:#1a6de3;} .payment-detail-amount.negative{color:#ef4444;} .payment-detail-divider{margin:20px 0;border-top:1px solid #e2e8f0;}</style>');
            printWindow.document.write('</head><body>');
            printWindow.document.write(drawerBody.innerHTML);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            printWindow.print();
          }
        });
      }
    }, 100);
  }

  function renderCommission() {
    var el = document.getElementById('page-commission');
    if (!el) return;

    var now = new Date();
    var firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    var lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    if (!APP.commission.dateFrom || APP.commission.dateFrom === RANGE_START_ISO) {
      APP.commission.dateFrom = formatDateInput(firstDay);
    }
    if (!APP.commission.dateTo || APP.commission.dateTo === TODAY_ISO) {
      APP.commission.dateTo = formatDateInput(lastDay);
    }

    var activeTab = APP.commission.tab || 'overview';

    el.innerHTML =
      '<div class="commission-page">' +
      '<div class="tds-page-title-row">' +
      '<h2 class="tds-page-title">Hoa hồng người giới thiệu</h2>' +
      '</div>' +
      '<div class="commission-tabs">' +
      '<button class="commission-tab' + (activeTab === 'overview' ? ' commission-tab-active' : '') + '" data-tab="overview">Tổng quan</button>' +
      '<button class="commission-tab' + (activeTab === 'detail' ? ' commission-tab-active' : '') + '" data-tab="detail">Chi tiết</button>' +
      '</div>' +
      '<div class="tds-card commission-shell">' +
      '<div class="tds-table-toolbar commission-toolbar">' +
      '<div class="toolbar-left">' +
      '<div class="commission-date-range">' +
      '<input class="tds-input commission-date" id="commission-date-from" type="date" value="' + escapeHtml(APP.commission.dateFrom) + '">' +
      '<span class="commission-date-sep">\u2013</span>' +
      '<input class="tds-input commission-date" id="commission-date-to" type="date" value="' + escapeHtml(APP.commission.dateTo) + '">' +
      '</div>' +
      '<select class="tds-select" id="commission-type-filter">' +
      '<option value="">Loại hoa hồng</option>' +
      '<option value="referral"' + (APP.commission.commissionType === 'referral' ? ' selected' : '') + '>Giới thiệu</option>' +
      '<option value="service"' + (APP.commission.commissionType === 'service' ? ' selected' : '') + '>Dịch vụ</option>' +
      '<option value="revenue"' + (APP.commission.commissionType === 'revenue' ? ' selected' : '') + '>Doanh thu</option>' +
      '</select>' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<div class="commission-search-wrap">' +
      '<svg class="commission-search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' +
      '<input class="tds-search-input" id="commission-search" placeholder="Tìm kiếm theo họ tên" value="' + escapeHtml(APP.commission.search || '') + '">' +
      '</div>' +
      '</div>' +
      '</div>' +
      '<div id="commission-table"></div>' +
      '</div>' +
      '</div>';

    // Tab click handlers
    var tabBtns = el.querySelectorAll('.commission-tab');
    for (var t = 0; t < tabBtns.length; t++) {
      tabBtns[t].addEventListener('click', function () {
        APP.commission.tab = this.getAttribute('data-tab');
        renderCommission();
      });
    }

    // Date filter handlers
    var dateFrom = document.getElementById('commission-date-from');
    var dateTo = document.getElementById('commission-date-to');
    if (dateFrom) dateFrom.addEventListener('change', function () { APP.commission.dateFrom = this.value; loadCommissionData(); });
    if (dateTo) dateTo.addEventListener('change', function () { APP.commission.dateTo = this.value; loadCommissionData(); });

    // Type filter
    var typeFilter = document.getElementById('commission-type-filter');
    if (typeFilter) typeFilter.addEventListener('change', function () { APP.commission.commissionType = this.value; loadCommissionData(); });

    // Search
    var searchInput = document.getElementById('commission-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.commission.search = searchInput.value.trim();
        loadCommissionData();
      }, 250));
    }

    loadCommissionData();
  }

  async function loadCommissionData() {
    APP.commission.loading = true;
    APP.commission.requestId += 1;
    var requestId = APP.commission.requestId;
    renderCommissionTable();

    try {
      var query = toQueryString({
        search: APP.commission.search,
        type: APP.commission.commissionType,
        dateFrom: APP.commission.dateFrom,
        dateTo: APP.commission.dateTo,
        companyId: getSelectedBranchId(),
        limit: 80,
        offset: 0,
      });
      var data = await api('/api/commissions' + query);
      if (requestId !== APP.commission.requestId) return;
      APP.commission.items = safeItems(data);
    } catch (_err) {
      if (requestId !== APP.commission.requestId) return;
      APP.commission.items = [];
    } finally {
      if (requestId === APP.commission.requestId) {
        APP.commission.loading = false;
        renderCommissionTable();
      }
    }
  }

  function renderCommissionTable() {
    var tableWrap = document.getElementById('commission-table');
    if (!tableWrap) return;

    if (APP.commission.loading) {
      tableWrap.innerHTML = renderLoadingState('Đang tải hoa hồng...');
      return;
    }

    var rows = APP.commission.items || [];
    if (!rows.length) {
      tableWrap.innerHTML =
        '<div class="commission-empty">' +
        '<div class="commission-empty-icon">' +
        '<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>' +
        '<svg class="commission-empty-alert" width="20" height="20" viewBox="0 0 24 24" fill="#f59e0b" stroke="#fff" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>' +
        '</div>' +
        '<p class="commission-empty-text">Không có dữ liệu</p>' +
        '</div>';
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr>' +
      '<th>Người giới thiệu</th>' +
      '<th>Phân loại</th>' +
      '<th class="text-right">Lợi nhuận tính hoa hồng</th>' +
      '<th class="text-right">Tiền hoa hồng</th>' +
      '</tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(item.name || item.partnerName || '\u2014') + '</td>' +
          '<td>' + escapeHtml(item.type || item.category || '\u2014') + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.profit || item.revenue || 0)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.commission || item.amount || 0)) + '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';
  }

  // Submenu Route Render Functions
  // ---------------------------------------------------------------------------

  function renderLaboOrders() {
    var el = document.getElementById('page-labo'); if (!el) return;
    el.innerHTML =
      '<div class="tds-card labo-shell"><div class="tds-card-header">' +
      '<h2>\u0110\u1eb7t h\u00e0ng Labo</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="lo-export">Xu\u1ea5t Excel</button></div>' +
      '<div class="tds-table-toolbar"><div class="toolbar-left">' +
      '<input class="tds-search-input" id="lo-search" placeholder="T\u00ecm theo m\u00e3 \u0111\u01a1n, kh\u00e1ch h\u00e0ng" value="">' +
      '</div><div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-secondary" id="lo-refresh">L\u00e0m m\u1edbi</button>' +
      '</div></div><div id="lo-table"></div></div>';
    var si = document.getElementById('lo-search');
    if (si) si.addEventListener('input', debounce(function () { _loLoad(si.value.trim()); }, 250));
    var rb = document.getElementById('lo-refresh');
    if (rb) rb.addEventListener('click', function () { _loLoad(''); });
    var eb = document.getElementById('lo-export');
    if (eb) eb.addEventListener('click', function () { downloadExcel('sale-orders', { companyId: getSelectedBranchId(), columns: ['name', 'date', 'state', 'amountTotal', 'partnerName', 'doctorName', 'companyName'] }); });
    _loLoad('');
  }
  async function _loLoad(search) {
    var tw = document.getElementById('lo-table'); if (!tw) return;
    tw.innerHTML = renderLoadingState('\u0110ang t\u1ea3i \u0111\u01a1n h\u00e0ng Labo...');
    try {
      var rows = safeItems(await api('/api/sale-orders' + toQueryString({ search: search, companyId: getSelectedBranchId(), limit: 50, offset: 0 })));
      if (!rows.length) { tw.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 \u0111\u01a1n h\u00e0ng Labo'); return; }
      tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>M\u00e3 \u0111\u01a1n</th><th>Ng\u00e0y</th><th>Kh\u00e1ch h\u00e0ng</th><th>B\u00e1c s\u0129</th><th>Tr\u1ea1ng th\u00e1i</th><th class="text-right">Gi\u00e1 tr\u1ecb</th></tr></thead><tbody>' + rows.map(function (r) { return '<tr><td>' + escapeHtml(r.name || r.id || '\u2014') + '</td><td>' + escapeHtml(formatDate(r.date)) + '</td><td>' + escapeHtml(r.partnerName || '\u2014') + '</td><td>' + escapeHtml(r.doctorName || '\u2014') + '</td><td><span class="tds-badge ' + stateBadgeClass(r.state) + '">' + escapeHtml(translateState(r.state)) + '</span></td><td class="text-right">' + escapeHtml(formatCurrency(r.amountTotal || 0)) + '</td></tr>'; }).join('') + '</tbody></table></div>';
      // Wire row clicks to open sale order detail drawer
      var loClickRows = tw.querySelectorAll('tbody tr');
      for (var li = 0; li < loClickRows.length; li++) {
        loClickRows[li].style.cursor = 'pointer';
        (function (idx) {
          loClickRows[idx].addEventListener('click', function () {
            var loItem = rows[idx];
            if (loItem) openSaleOrderDrawer(loItem);
          });
        })(li);
      }
    } catch (_e) { tw.innerHTML = renderEmptyState('Kh\u00f4ng th\u1ec3 t\u1ea3i'); }
  }

  // Sale order detail drawer (for labo-orders sub-route)
  function openSaleOrderDrawer(item) {
    var content =
      '<div class="drawer-header">' +
      '<h3>Chi ti\u1ebft \u0111\u01a1n h\u00e0ng</h3>' +
      '<button class="drawer-close" onclick="TDS.closeDrawer()">&times;</button>' +
      '</div>' +
      '<div class="drawer-content">' +
      '<div class="drawer-field"><label>M\u00e3 \u0111\u01a1n</label><span>' + escapeHtml(item.name || item.id || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Ng\u00e0y</label><span>' + escapeHtml(formatDate(item.date)) + '</span></div>' +
      '<div class="drawer-field"><label>Kh\u00e1ch h\u00e0ng</label><span>' + escapeHtml(item.partnerName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>B\u00e1c s\u0129</label><span>' + escapeHtml(item.doctorName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Gi\u00e1 tr\u1ecb</label><span>' + escapeHtml(formatCurrency(item.amountTotal || 0)) + '</span></div>' +
      '<div class="drawer-field"><label>Tr\u1ea1ng th\u00e1i</label><span class="tds-badge ' + stateBadgeClass(item.state || 'draft') + '">' + escapeHtml(translateState(item.state || 'draft')) + '</span></div>' +
      (item.companyName ? '<div class="drawer-field"><label>Chi nh\u00e1nh</label><span>' + escapeHtml(item.companyName) + '</span></div>' : '') +
      (item.notes || item.note ? '<div class="drawer-field"><label>Ghi ch\u00fa</label><span>' + escapeHtml(item.notes || item.note) + '</span></div>' : '') +
      '</div>';
    openDrawer(content, 420);
  }

  // Open labo order detail drawer
  function openLaboOrderDrawer(item) {
    var content =
      '<div class="drawer-header">' +
      '<h3>Chi tiết phiếu Labo</h3>' +
      '<button class="drawer-close" onclick="closeDrawer()">&times;</button>' +
      '</div>' +
      '<div class="drawer-content">' +
      '<div class="drawer-field"><label>Mã phiếu</label><span>' + escapeHtml(item.name || item.id || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Khách hàng</label><span>' + escapeHtml(item.partnerName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Dịch vụ</label><span>' + escapeHtml(item.serviceName || item.productName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Bác sĩ</label><span>' + escapeHtml(item.doctorName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Labo</label><span>' + escapeHtml(item.laboName || item.supplierName || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Chỉ định</label><span>' + escapeHtml(item.instruction || item.note || '\u2014') + '</span></div>' +
      '<div class="drawer-field"><label>Ngày giao</label><span>' + escapeHtml(formatDate(item.date || item.dateOrder)) + '</span></div>' +
      '<div class="drawer-field"><label>Ngày nhận</label><span>' + escapeHtml(formatDate(item.dateReceive || item.dateDone || '')) + '</span></div>' +
      '<div class="drawer-field"><label>Trạng thái</label><span class="tds-badge ' + stateBadgeClass(item.state || 'draft') + '">' + escapeHtml(translateState(item.state || 'draft')) + '</span></div>' +
      '</div>';
    openDrawer(content, 420);
  }

  function renderPurchaseRefund() {
    var el = document.getElementById('page-purchase'); if (!el) return;
    el.innerHTML =
      '<div class="tds-card purchase-shell"><div class="tds-card-header">' +
      '<h2>Tr\u1ea3 h\u00e0ng nh\u00e0 cung c\u1ea5p</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="pr-refresh">L\u00e0m m\u1edbi</button></div>' +
      '<div id="pr-table"></div></div>';
    var rb = document.getElementById('pr-refresh');
    if (rb) rb.addEventListener('click', _prLoad);
    _prLoad();
  }
  async function _prLoad() {
    var tw = document.getElementById('pr-table'); if (!tw) return;
    tw.innerHTML = renderLoadingState('\u0110ang t\u1ea3i phi\u1ebfu tr\u1ea3 h\u00e0ng...');
    try {
      var rows = safeItems(await api('/api/stock-pickings' + toQueryString({ companyId: getSelectedBranchId(), pickingType: 'outgoing', limit: 50, offset: 0 })));
      if (!rows.length) { tw.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 phi\u1ebfu tr\u1ea3 h\u00e0ng'); return; }
      tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>M\u00e3 ch\u1ee9ng t\u1eeb</th><th>Ng\u00e0y</th><th>\u0110\u1ed1i t\u00e1c</th><th>Chi nh\u00e1nh</th><th>Tr\u1ea1ng th\u00e1i</th></tr></thead><tbody>' + rows.map(function (r) { return '<tr><td>' + escapeHtml(r.name || r.id || '\u2014') + '</td><td>' + escapeHtml(formatDate(r.date)) + '</td><td>' + escapeHtml(r.partnerName || '\u2014') + '</td><td>' + escapeHtml(r.companyName || '\u2014') + '</td><td><span class="tds-badge ' + stateBadgeClass(r.state) + '">' + escapeHtml(translateState(r.state)) + '</span></td></tr>'; }).join('') + '</tbody></table></div>';
    } catch (_e) { tw.innerHTML = renderEmptyState('Kh\u00f4ng th\u1ec3 t\u1ea3i'); }
  }

  // ===========================================================================
  // Timekeeping (#/timekeeping) - Calendar-style attendance grid
  // ===========================================================================
  function renderTimekeeping() {
    var el = document.getElementById('page-salary'); if (!el) return;
    var now = new Date(), yr = now.getFullYear(), mo = now.getMonth(), dim = new Date(yr, mo + 1, 0).getDate();
    el.innerHTML =
      '<div class="tds-card"><div class="tds-card-header"><h2>Bảng chấm công - Tháng ' + (mo + 1) + '/' + yr + '</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="tk-export">Xuất Excel</button></div>' +
      '<div class="tds-table-toolbar"><div class="toolbar-left">' +
      '<select class="tds-select" id="tk-month">' + [1,2,3,4,5,6,7,8,9,10,11,12].map(function (m) { return '<option value="' + m + '"' + (m === mo + 1 ? ' selected' : '') + '>Tháng ' + m + '</option>'; }).join('') + '</select>' +
      '<select class="tds-select" id="tk-year">' + [yr - 1, yr, yr + 1].map(function (y) { return '<option value="' + y + '"' + (y === yr ? ' selected' : '') + '>' + y + '</option>'; }).join('') + '</select>' +
      '<button class="tds-btn tds-btn-primary" id="tk-apply">Áp dụng</button></div></div>' +
      '<div id="tk-table"></div></div>';
    var ab = document.getElementById('tk-apply');
    if (ab) ab.addEventListener('click', function () {
      var sm = parseInt(getInputValue('tk-month')) || (mo + 1);
      var sy = parseInt(getInputValue('tk-year')) || yr;
      _tkLoad(sy, sm - 1, new Date(sy, sm, 0).getDate());
    });
    var eb = document.getElementById('tk-export');
    if (eb) eb.addEventListener('click', function () { downloadExcel('employees', { companyId: getSelectedBranchId(), columns: ['name', 'hrJob', 'companyName'] }); });
    _tkLoad(yr, mo, dim);
  }
  async function _tkLoad(yr, mo, dim) {
    var tw = document.getElementById('tk-table'); if (!tw) return;
    tw.innerHTML = renderLoadingState('Đang tải chấm công...');
    try {
      var dateFrom = yr + '-' + String(mo + 1).padStart(2, '0') + '-01';
      var dateTo = yr + '-' + String(mo + 1).padStart(2, '0') + '-' + String(dim).padStart(2, '0');
      var data = await api('/api/hr/salary' + toQueryString({ companyId: getSelectedBranchId(), dateFrom: dateFrom, dateTo: dateTo }));
      var emps = (data && data.employees) ? data.employees : safeItems(data);
      var timekeeping = safeItems((data && data.timekeeping) || []);
      if (!emps.length) { tw.innerHTML = renderEmptyState('Chưa có dữ liệu nhân viên'); return; }
      var dh = ''; for (var d = 1; d <= dim; d++) dh += '<th class="text-center" style="min-width:28px;padding:3px">' + d + '</th>';
      var tkMap = {};
      timekeeping.forEach(function (tk) { var k = tk.employeeName || ''; if (!tkMap[k]) tkMap[k] = {}; var dt = new Date(tk.date); if (!isNaN(dt.getTime())) tkMap[k][dt.getDate()] = tk; });
      tw.innerHTML = '<div class="tds-table-wrapper" style="overflow-x:auto"><table class="tds-table" style="font-size:12px"><thead><tr><th style="min-width:140px;position:sticky;left:0;background:#fff;z-index:1">Nhân viên</th><th>Chức vụ</th>' + dh + '<th class="text-center">Tổng</th></tr></thead><tbody>' +
        emps.map(function (e) {
          var empName = e.name || '—'; var empTk = tkMap[empName] || {};
          var c = '', totalH = 0;
          for (var dd = 1; dd <= dim; dd++) {
            var dw = new Date(yr, mo, dd).getDay(), we = dw === 0 || dw === 6;
            var rec = empTk[dd];
            if (rec && rec.hours) { totalH += rec.hours; c += '<td class="text-center" style="padding:3px;background:#DCFCE7">' + escapeHtml(formatNumber(rec.hours)) + '</td>'; }
            else { c += '<td class="text-center" style="padding:3px;' + (we ? 'background:#f3f4f6;color:#9ca3af' : '') + '">' + (we ? '-' : 'x') + '</td>'; if (!we) totalH += 8; }
          }
          return '<tr><td style="position:sticky;left:0;background:#fff;z-index:1">' + escapeHtml(empName) + '</td><td>' + escapeHtml(e.hrJob || e.jobTitle || '—') + '</td>' + c + '<td class="text-center font-semibold">' + escapeHtml(formatNumber(totalH)) + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    } catch (_e) { tw.innerHTML = renderEmptyState('Không thể tải chấm công'); }
  }

  // ===========================================================================
  // Shared payment page builder (enhanced with create button support)
  // ===========================================================================
  function _paymentPage(elId, title, tableId, paymentType, loadFn, createBtnLabel) {
    var el = document.getElementById(elId); if (!el) return;
    var createHtml = createBtnLabel ? '<button class="tds-btn tds-btn-primary" id="' + tableId + '-create">' + createBtnLabel + '</button>' : '';
    el.innerHTML = '<div class="tds-card cashbook-shell"><div class="tds-card-header"><h2>' + title + '</h2><div>' +
      '<button class="tds-btn tds-btn-secondary" id="' + tableId + '-export" style="margin-right:8px">Xuất Excel</button>' + createHtml +
      '</div></div><div class="tds-table-toolbar"><div class="toolbar-left">' +
      '<input class="tds-input" id="' + tableId + '-df" type="date" value="' + escapeHtml(MONTH_START_ISO) + '">' +
      '<input class="tds-input" id="' + tableId + '-dt" type="date" value="' + escapeHtml(TODAY_ISO) + '">' +
      '<button class="tds-btn tds-btn-primary" id="' + tableId + '-apply">Áp dụng</button></div></div>' +
      '<div id="' + tableId + '"></div></div>';
    var ab = document.getElementById(tableId + '-apply'); if (ab) ab.addEventListener('click', loadFn);
    var eb = document.getElementById(tableId + '-export'); if (eb) eb.addEventListener('click', function () { downloadExcel('payments', { companyId: getSelectedBranchId(), dateFrom: getInputValue(tableId + '-df'), dateTo: getInputValue(tableId + '-dt'), paymentType: paymentType, columns: ['date', 'name', 'paymentType', 'partnerName', 'companyName', 'state', 'amount'] }); });
    loadFn();
    return el;
  }
  async function _paymentLoad(tableId, paymentType, emptyMsg, columns) {
    var tw = document.getElementById(tableId); if (!tw) return;
    tw.innerHTML = renderLoadingState('Đang tải...');
    try {
      var q = { companyId: getSelectedBranchId(), dateFrom: getInputValue(tableId + '-df') || MONTH_START_ISO, dateTo: getInputValue(tableId + '-dt') || TODAY_ISO, limit: 80, offset: 0 };
      if (paymentType) q.paymentType = paymentType;
      var rows = safeItems(await api('/api/payments' + toQueryString(q)));
      if (!rows.length) { tw.innerHTML = renderEmptyState(emptyMsg); return; }
      var cols = columns || [
        { key: 'date', label: 'Ngày', fmt: function (v) { return escapeHtml(formatDate(v)); } },
        { key: 'name', label: 'Số phiếu', fmt: function (v) { return escapeHtml(v || '—'); } },
        { key: 'paymentType', label: 'Loại', fmt: function (v) { return escapeHtml(normalizePaymentTypeLabel(v)); } },
        { key: 'partnerName', label: 'Đối tượng', fmt: function (v) { return escapeHtml(v || '—'); } },
        { key: 'amount', label: 'Số tiền', fmt: function (v) { return escapeHtml(formatCurrency(v || 0)); }, cls: 'text-right' },
        { key: 'state', label: 'Trạng thái', fmt: function (v) { return (v === 'posted' || v === 'done') ? '<span class="tds-badge tds-badge-success">Đã xác nhận</span>' : '<span class="tds-badge tds-badge-warning">Nháp</span>'; } },
      ];
      tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr>' +
        cols.map(function (c) { return '<th' + (c.cls ? ' class="' + c.cls + '"' : '') + '>' + c.label + '</th>'; }).join('') +
        '<th>Thao tác</th></tr></thead><tbody>' +
        rows.map(function (r, rIdx) {
          return '<tr>' + cols.map(function (c) { return '<td' + (c.cls ? ' class="' + c.cls + '"' : '') + '>' + c.fmt(r[c.key]) + '</td>'; }).join('') +
            '<td><button class="tds-btn tds-btn-sm tds-btn-secondary payment-sub-view-btn" data-row-idx="' + rIdx + '">Xem</button></td></tr>';
        }).join('') + '</tbody></table></div>';
      // Wire "Xem" buttons to open payment detail drawer
      var subViewBtns = tw.querySelectorAll('.payment-sub-view-btn');
      for (var vi = 0; vi < subViewBtns.length; vi++) {
        subViewBtns[vi].addEventListener('click', function () {
          var idx = parseInt(this.getAttribute('data-row-idx'), 10);
          var item = rows[idx];
          if (item) openPaymentDetailDrawer(item);
        });
      }
    } catch (_e) { tw.innerHTML = renderEmptyState(emptyMsg); }
  }

  // Voucher create form helper
  function _voucherCreateForm(typeLabel) {
    return '<form><div class="tds-form-group"><label class="tds-label">Ngày</label><input class="tds-input" id="vcf-date" type="date" value="' + TODAY_ISO + '"></div>' +
      '<div class="tds-form-row"><div class="tds-form-group"><label class="tds-label">Phương thức</label><select class="tds-select" id="vcf-method"><option value="cash">Tiền mặt</option><option value="bank">Chuyển khoản</option></select></div>' +
      '<div class="tds-form-group"><label class="tds-label">Loại ' + typeLabel + '</label><input class="tds-input" id="vcf-category"></div></div>' +
      '<div class="tds-form-group"><label class="tds-label">Đối tượng</label><input class="tds-input" id="vcf-partner"></div>' +
      '<div class="tds-form-group"><label class="tds-label">Số tiền</label><input class="tds-input" id="vcf-amount" type="number" min="0"></div>' +
      '<div class="tds-form-group"><label class="tds-label">Nội dung</label><input class="tds-input" id="vcf-note"></div></form>';
  }
  async function _voucherSave(paymentType, reloadFn) {
    try {
      await api('/api/payments', { method: 'POST', body: JSON.stringify({ date: getInputValue('vcf-date'), paymentType: paymentType, method: getInputValue('vcf-method'), category: getInputValue('vcf-category'), partnerName: getInputValue('vcf-partner'), amount: Number(getInputValue('vcf-amount')) || 0, note: getInputValue('vcf-note') }) });
      showToast('success', 'Đã tạo phiếu thành công'); closeModal(); if (typeof reloadFn === 'function') reloadFn();
    } catch (err) { showToast('error', (err && err.message) || 'Không thể tạo phiếu'); }
  }

  // ===========================================================================
  // Salary Payment (#/salary-payment) - Quản lý tạm ứng
  // Columns: Mã phiếu, Ngày, Người nhận, Loại phiếu, Phương thức, Số tiền, Trạng thái, Thao tác
  // ===========================================================================
  function renderSalaryPayment() {
    var loadFn = function () { _spLoad(); };
    _paymentPage('page-salary', 'Quản lý tạm ứng', 'sp-tbl', 'outbound', loadFn, 'Tạo phiếu tạm ứng');
    var cb = document.getElementById('sp-tbl-create');
    if (cb) cb.addEventListener('click', function () {
      showModal('Tạo phiếu tạm ứng',
        '<form><div class="tds-form-group"><label class="tds-label">Ngày</label><input class="tds-input" id="sp-f-date" type="date" value="' + TODAY_ISO + '"></div>' +
        '<div class="tds-form-group"><label class="tds-label">Người nhận</label><input class="tds-input" id="sp-f-name" placeholder="Tên nhân viên"></div>' +
        '<div class="tds-form-row"><div class="tds-form-group"><label class="tds-label">Loại phiếu</label><select class="tds-select" id="sp-f-type"><option value="advance">Tạm ứng</option><option value="salary">Lương</option><option value="bonus">Thưởng</option></select></div>' +
        '<div class="tds-form-group"><label class="tds-label">Phương thức</label><select class="tds-select" id="sp-f-method"><option value="cash">Tiền mặt</option><option value="bank">Chuyển khoản</option></select></div></div>' +
        '<div class="tds-form-group"><label class="tds-label">Số tiền</label><input class="tds-input" id="sp-f-amount" type="number" min="0"></div>' +
        '<div class="tds-form-group"><label class="tds-label">Lý do</label><input class="tds-input" id="sp-f-reason"></div></form>',
        { footer: '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeModal()">Hủy</button><button class="tds-btn tds-btn-primary" id="sp-save">Lưu</button>',
          onOpen: function () { var sv = document.getElementById('sp-save'); if (sv) sv.addEventListener('click', async function () {
            try { await api('/api/hr/advances', { method: 'POST', body: JSON.stringify({ date: getInputValue('sp-f-date'), employeeName: getInputValue('sp-f-name'), type: getInputValue('sp-f-type'), method: getInputValue('sp-f-method'), amount: Number(getInputValue('sp-f-amount')) || 0, reason: getInputValue('sp-f-reason') }) });
              showToast('success', 'Đã tạo phiếu tạm ứng'); closeModal(); _spLoad();
            } catch (err) { showToast('error', (err && err.message) || 'Không thể tạo phiếu'); } }); } });
    });
  }
  async function _spLoad() {
    var tw = document.getElementById('sp-tbl'); if (!tw) return;
    tw.innerHTML = renderLoadingState('Đang tải phiếu tạm ứng...');
    try {
      var q = toQueryString({ companyId: getSelectedBranchId(), dateFrom: getInputValue('sp-tbl-df') || MONTH_START_ISO, dateTo: getInputValue('sp-tbl-dt') || TODAY_ISO });
      var data = await api('/api/hr/salary' + q);
      var advances = safeItems((data && data.advances) || []);
      if (!advances.length) {
        // Fallback to payments API
        var rows = safeItems(await api('/api/payments' + toQueryString({ companyId: getSelectedBranchId(), dateFrom: getInputValue('sp-tbl-df') || MONTH_START_ISO, dateTo: getInputValue('sp-tbl-dt') || TODAY_ISO, paymentType: 'outbound', limit: 80, offset: 0 })));
        if (!rows.length) { tw.innerHTML = renderEmptyState('Chưa có phiếu tạm ứng trong kỳ'); return; }
        tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Mã phiếu</th><th>Ngày</th><th>Người nhận</th><th>Loại phiếu</th><th>Phương thức</th><th class="text-right">Số tiền</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>' +
          rows.map(function (r) { return '<tr><td>' + escapeHtml(r.name || '—') + '</td><td>' + escapeHtml(formatDate(r.date)) + '</td><td>' + escapeHtml(r.partnerName || '—') + '</td><td>' + escapeHtml(normalizePaymentTypeLabel(r.paymentType)) + '</td><td>' + escapeHtml(r.journalName || '—') + '</td><td class="text-right">' + escapeHtml(formatCurrency(r.amount || 0)) + '</td><td>' + (r.state === 'posted' || r.state === 'done' ? '<span class="tds-badge tds-badge-success">Đã duyệt</span>' : '<span class="tds-badge tds-badge-warning">Chờ duyệt</span>') + '</td><td><button class="tds-btn tds-btn-sm tds-btn-secondary">Xem</button></td></tr>'; }).join('') + '</tbody></table></div>';
        return;
      }
      tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Mã phiếu</th><th>Ngày</th><th>Người nhận</th><th>Loại phiếu</th><th>Phương thức</th><th class="text-right">Số tiền</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>' +
        advances.map(function (item, idx) { return '<tr><td>' + escapeHtml(item.id || ('TU-' + String(idx + 1).padStart(4, '0'))) + '</td><td>' + escapeHtml(formatDate(item.date)) + '</td><td>' + escapeHtml(item.employeeName || '—') + '</td><td>' + escapeHtml(item.type || 'Tạm ứng') + '</td><td>' + escapeHtml(item.method || 'Tiền mặt') + '</td><td class="text-right">' + escapeHtml(formatCurrency(item.amount || 0)) + '</td><td>' + (item.state === 'done' ? '<span class="tds-badge tds-badge-success">Đã duyệt</span>' : '<span class="tds-badge tds-badge-warning">Chờ duyệt</span>') + '</td><td><button class="tds-btn tds-btn-sm tds-btn-secondary">Xem</button></td></tr>'; }).join('') + '</tbody></table></div>';
    } catch (_e) { tw.innerHTML = renderEmptyState('Không thể tải phiếu tạm ứng'); }
  }

  // ===========================================================================
  // Salary Reports (#/salary-reports) - Báo cáo thanh toán lương
  // Columns: Nhân viên, Chức vụ, Đầu kỳ, Lương, Thanh toán, Cuối kỳ
  // ===========================================================================
  function renderSalaryReports() {
    var el = document.getElementById('page-salary'); if (!el) return;
    el.innerHTML = '<div class="tds-card"><div class="tds-card-header"><h2>Báo cáo thanh toán lương</h2><button class="tds-btn tds-btn-secondary" id="sr-export">Xuất Excel</button></div>' +
      '<div class="tds-table-toolbar"><div class="toolbar-left"><input class="tds-input" id="sr-df" type="date" value="' + escapeHtml(MONTH_START_ISO) + '"><input class="tds-input" id="sr-dt" type="date" value="' + escapeHtml(TODAY_ISO) + '"><button class="tds-btn tds-btn-primary" id="sr-apply">Áp dụng</button></div></div><div id="sr-table"></div></div>';
    var ab = document.getElementById('sr-apply'); if (ab) ab.addEventListener('click', _srLoad);
    var eb = document.getElementById('sr-export'); if (eb) eb.addEventListener('click', function () { downloadExcel('employees', { companyId: getSelectedBranchId(), dateFrom: getInputValue('sr-df'), dateTo: getInputValue('sr-dt'), columns: ['name', 'hrJob', 'companyName', 'monthlySalary', 'allowance', 'commission'] }); });
    _srLoad();
  }
  async function _srLoad() {
    var tw = document.getElementById('sr-table'); if (!tw) return;
    tw.innerHTML = renderLoadingState('Đang tải báo cáo lương...');
    try {
      var data = await api('/api/hr/salary' + toQueryString({ companyId: getSelectedBranchId(), dateFrom: getInputValue('sr-df') || MONTH_START_ISO, dateTo: getInputValue('sr-dt') || TODAY_ISO }));
      var emps = (data && data.employees) ? data.employees : safeItems(data);
      var advances = safeItems((data && data.advances) || []);
      if (!emps.length) { tw.innerHTML = renderEmptyState('Chưa có dữ liệu lương'); return; }
      var advMap = {};
      advances.forEach(function (a) { var k = a.employeeName || ''; advMap[k] = (advMap[k] || 0) + toNumber(a.amount); });
      tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Nhân viên</th><th>Chức vụ</th><th class="text-right">Đầu kỳ</th><th class="text-right">Lương</th><th class="text-right">Thanh toán</th><th class="text-right">Cuối kỳ</th></tr></thead><tbody>' +
        emps.map(function (e) {
          var salary = toNumber(e.monthlySalary) + toNumber(e.allowance) + toNumber(e.commission);
          var paid = advMap[e.name] || 0;
          var opening = 0, closing = opening + salary - paid;
          return '<tr><td>' + escapeHtml(e.name || '—') + '</td><td>' + escapeHtml(e.hrJob || e.jobTitle || '—') + '</td><td class="text-right">' + escapeHtml(formatCurrency(opening)) + '</td><td class="text-right">' + escapeHtml(formatCurrency(salary)) + '</td><td class="text-right">' + escapeHtml(formatCurrency(paid)) + '</td><td class="text-right font-semibold">' + escapeHtml(formatCurrency(closing)) + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    } catch (_e) { tw.innerHTML = renderEmptyState('Không thể tải báo cáo lương'); }
  }

  // ===========================================================================
  // Receipts (#/receipts) - Phiếu thu with "Tạo phiếu thu" button
  // ===========================================================================
  function renderReceipts() {
    var loadFn = function () { _paymentLoad('rc-tbl', 'inbound', 'Chưa có phiếu thu'); };
    _paymentPage('page-cashbook', 'Phiếu thu', 'rc-tbl', 'inbound', loadFn, 'Tạo phiếu thu');
    var cb = document.getElementById('rc-tbl-create');
    if (cb) cb.addEventListener('click', function () {
      showModal('Tạo phiếu thu', _voucherCreateForm('thu'), {
        footer: '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeModal()">Hủy</button><button class="tds-btn tds-btn-primary" id="vcf-save">Lưu</button>',
        onOpen: function () { var sv = document.getElementById('vcf-save'); if (sv) sv.addEventListener('click', function () { _voucherSave('inbound', loadFn); }); }
      });
    });
  }

  // ===========================================================================
  // Payments Voucher (#/payments) - Phiếu chi with "Tạo phiếu chi" button
  // ===========================================================================
  function renderPaymentsVoucher() {
    var loadFn = function () { _paymentLoad('pv-tbl', 'outbound', 'Chưa có phiếu chi'); };
    _paymentPage('page-cashbook', 'Phiếu chi', 'pv-tbl', 'outbound', loadFn, 'Tạo phiếu chi');
    var cb = document.getElementById('pv-tbl-create');
    if (cb) cb.addEventListener('click', function () {
      showModal('Tạo phiếu chi', _voucherCreateForm('chi'), {
        footer: '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeModal()">Hủy</button><button class="tds-btn tds-btn-primary" id="vcf-save">Lưu</button>',
        onOpen: function () { var sv = document.getElementById('vcf-save'); if (sv) sv.addEventListener('click', function () { _voucherSave('outbound', loadFn); }); }
      });
    });
  }

  // ===========================================================================
  // Account Payment (#/account-payment) - Phiếu chuyển nội bộ
  // Columns: Ngày, Số phiếu, Loại, Phương thức, Số tiền, Nội dung, Trạng thái
  // ===========================================================================
  function renderAccountPayment() {
    var loadFn = function () { _apLoad(); };
    _paymentPage('page-cashbook', 'Phiếu chuyển nội bộ', 'ap-tbl', '', loadFn, 'Tạo phiếu chuyển');
    var cb = document.getElementById('ap-tbl-create');
    if (cb) cb.addEventListener('click', function () {
      showModal('Tạo phiếu chuyển nội bộ',
        '<form><div class="tds-form-group"><label class="tds-label">Ngày</label><input class="tds-input" id="ap-f-date" type="date" value="' + TODAY_ISO + '"></div>' +
        '<div class="tds-form-row"><div class="tds-form-group"><label class="tds-label">Loại</label><select class="tds-select" id="ap-f-type"><option value="internal">Nội bộ</option><option value="transfer">Chuyển quỹ</option></select></div>' +
        '<div class="tds-form-group"><label class="tds-label">Phương thức</label><select class="tds-select" id="ap-f-method"><option value="cash">Tiền mặt</option><option value="bank">Ngân hàng</option></select></div></div>' +
        '<div class="tds-form-group"><label class="tds-label">Số tiền</label><input class="tds-input" id="ap-f-amount" type="number" min="0"></div>' +
        '<div class="tds-form-group"><label class="tds-label">Nội dung</label><input class="tds-input" id="ap-f-note"></div></form>',
        { footer: '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeModal()">Hủy</button><button class="tds-btn tds-btn-primary" id="ap-save">Lưu</button>',
          onOpen: function () { var sv = document.getElementById('ap-save'); if (sv) sv.addEventListener('click', async function () {
            try { await api('/api/payments', { method: 'POST', body: JSON.stringify({ date: getInputValue('ap-f-date'), paymentType: 'transfer', method: getInputValue('ap-f-method'), category: getInputValue('ap-f-type'), amount: Number(getInputValue('ap-f-amount')) || 0, note: getInputValue('ap-f-note') }) });
              showToast('success', 'Đã tạo phiếu chuyển'); closeModal(); _apLoad();
            } catch (err) { showToast('error', (err && err.message) || 'Không thể tạo phiếu'); } }); } });
    });
  }
  async function _apLoad() {
    var tw = document.getElementById('ap-tbl'); if (!tw) return;
    tw.innerHTML = renderLoadingState('Đang tải phiếu chuyển nội bộ...');
    try {
      var rows = safeItems(await api('/api/payments' + toQueryString({ companyId: getSelectedBranchId(), dateFrom: getInputValue('ap-tbl-df') || MONTH_START_ISO, dateTo: getInputValue('ap-tbl-dt') || TODAY_ISO, limit: 80, offset: 0 })));
      if (!rows.length) { tw.innerHTML = renderEmptyState('Chưa có phiếu chuyển nội bộ'); return; }
      tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ngày</th><th>Số phiếu</th><th>Loại</th><th>Phương thức</th><th class="text-right">Số tiền</th><th>Nội dung</th><th>Trạng thái</th></tr></thead><tbody>' +
        rows.map(function (r) { return '<tr><td>' + escapeHtml(formatDate(r.date)) + '</td><td>' + escapeHtml(r.name || '—') + '</td><td>' + escapeHtml(normalizePaymentTypeLabel(r.paymentType)) + '</td><td>' + escapeHtml(r.journalName || r.companyName || '—') + '</td><td class="text-right">' + escapeHtml(formatCurrency(r.amount || 0)) + '</td><td>' + escapeHtml(r.partnerName || r.note || '—') + '</td><td>' + (r.state === 'posted' || r.state === 'done' ? '<span class="tds-badge tds-badge-success">Đã xác nhận</span>' : '<span class="tds-badge tds-badge-warning">Nháp</span>') + '</td></tr>'; }).join('') + '</tbody></table></div>';
    } catch (_e) { tw.innerHTML = renderEmptyState('Không thể tải phiếu chuyển nội bộ'); }
  }

  function renderCallHistory() {
    var el = document.getElementById('page-callcenter'); if (!el) return;
    el.innerHTML = '<div class="tds-card"><div class="tds-card-header"><h2>L\u1ecbch s\u1eed cu\u1ed9c g\u1ecdi</h2></div><div id="ch-table"></div></div>';
    var tw = document.getElementById('ch-table'); if (!tw) return;
    tw.innerHTML = renderLoadingState('\u0110ang t\u1ea3i l\u1ecbch s\u1eed cu\u1ed9c g\u1ecdi...');

    // Try backend first, fall back to localStorage
    _loadCallHistory(tw);
  }

  async function _loadCallHistory(tw) {
    try {
      var data = await api('/api/callcenter/history' + toQueryString({ companyId: getSelectedBranchId(), limit: 50 }));
      var items = safeItems(data);
      if (items.length) {
        _renderCallHistoryTable(tw, items);
        return;
      }
    } catch (_err) {
      // API failed, fall back to localStorage
    }
    // Fallback: use localStorage recent calls
    var rc = APP.callcenter.recentCalls || [];
    if (!rc.length) { tw.innerHTML = renderEmptyState('Ch\u01b0a c\u00f3 l\u1ecbch s\u1eed cu\u1ed9c g\u1ecdi'); return; }
    _renderCallHistoryTable(tw, rc);
  }

  function _renderCallHistoryTable(tw, items) {
    tw.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Th\u1eddi gian</th><th>S\u1ed1 \u0111i\u1ec7n tho\u1ea1i</th><th>Kh\u00e1ch h\u00e0ng</th><th>Lo\u1ea1i</th></tr></thead><tbody>' + items.map(function (c) { return '<tr><td>' + escapeHtml(formatDateTime(c.time || c.date || c.callDate)) + '</td><td>' + escapeHtml(c.phone || c.phoneNumber || '\u2014') + '</td><td>' + escapeHtml(c.customerName || c.name || c.partnerName || '\u2014') + '</td><td>' + escapeHtml(c.type || c.callType || 'G\u1ecdi \u0111i') + '</td></tr>'; }).join('') + '</tbody></table></div>';
  }

  function renderCommissionEmployee() {
    var el = document.getElementById('page-commission');
    if (!el) return;

    var now = new Date();
    var firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    var lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);

    el.innerHTML =
      '<div class="commission-page">' +
      '<div class="tds-page-title-row">' +
      '<h2 class="tds-page-title">Hoa hồng nhân viên</h2>' +
      '</div>' +
      '<div class="tds-card commission-shell">' +
      '<div class="tds-table-toolbar commission-toolbar">' +
      '<div class="toolbar-left">' +
      '<div class="commission-date-range">' +
      '<input class="tds-input commission-date" id="ce-date-from" type="date" value="' + escapeHtml(formatDateInput(firstDay)) + '">' +
      '<span class="commission-date-sep">\u2013</span>' +
      '<input class="tds-input commission-date" id="ce-date-to" type="date" value="' + escapeHtml(formatDateInput(lastDay)) + '">' +
      '</div>' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<div class="commission-search-wrap">' +
      '<svg class="commission-search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' +
      '<input class="tds-search-input" id="ce-search" placeholder="Tìm kiếm theo tên nhân viên" value="">' +
      '</div>' +
      '</div>' +
      '</div>' +
      '<div id="ce-table"></div>' +
      '</div>' +
      '</div>';

    var si = document.getElementById('ce-search');
    if (si) si.addEventListener('input', debounce(function () { _ceLoad(si.value.trim()); }, 250));
    _ceLoad('');
  }

  async function _ceLoad(search) {
    var tw = document.getElementById('ce-table');
    if (!tw) return;
    tw.innerHTML = renderLoadingState('Đang tải hoa hồng nhân viên...');
    try {
      var data = await api('/api/hr/salary' + toQueryString({ companyId: getSelectedBranchId() }));
      var emps = (data && data.employees) ? data.employees : safeItems(data);
      if (search) {
        var s = search.toLowerCase();
        emps = emps.filter(function (e) { return (e.name || '').toLowerCase().indexOf(s) !== -1; });
      }
      if (!emps.length) {
        tw.innerHTML =
          '<div class="commission-empty">' +
          '<div class="commission-empty-icon">' +
          '<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>' +
          '<svg class="commission-empty-alert" width="20" height="20" viewBox="0 0 24 24" fill="#f59e0b" stroke="#fff" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>' +
          '</div>' +
          '<p class="commission-empty-text">Không có dữ liệu</p>' +
          '</div>';
        return;
      }
      tw.innerHTML =
        '<div class="tds-table-wrapper"><table class="tds-table">' +
        '<thead><tr>' +
        '<th>Nhân viên</th>' +
        '<th>Dịch vụ</th>' +
        '<th class="text-right">Doanh thu</th>' +
        '<th class="text-right">Tỷ lệ HH</th>' +
        '<th class="text-right">Tiền hoa hồng</th>' +
        '</tr></thead><tbody>' +
        emps.map(function (e) {
          return '<tr>' +
            '<td>' + escapeHtml(e.name || '\u2014') + '</td>' +
            '<td>' + escapeHtml(e.hrJob || e.jobTitle || '\u2014') + '</td>' +
            '<td class="text-right">' + escapeHtml(formatCurrency(e.revenue || e.monthlySalary || 0)) + '</td>' +
            '<td class="text-right">' + escapeHtml(e.commissionRate ? (e.commissionRate + '%') : '\u2014') + '</td>' +
            '<td class="text-right">' + escapeHtml(formatCurrency(e.commission || 0)) + '</td>' +
            '</tr>';
        }).join('') +
        '</tbody></table></div>';
    } catch (_e) {
      tw.innerHTML =
        '<div class="commission-empty">' +
        '<div class="commission-empty-icon">' +
        '<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="1.2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>' +
        '</div>' +
        '<p class="commission-empty-text">Không thể tải hoa hồng nhân viên</p>' +
        '</div>';
    }
  }

  function normalizePickingTypeLabel(value) {
    var text = String(value || '').trim().toLowerCase();
    if (!text) return '—';
    if (text.indexOf('incoming') !== -1 || text.indexOf('inbound') !== -1 || text === 'in') return 'Nhập kho';
    if (text.indexOf('outgoing') !== -1 || text.indexOf('outbound') !== -1 || text === 'out') return 'Xuất kho';
    return text;
  }

  function normalizePaymentTypeLabel(value) {
    var text = String(value || '').trim().toLowerCase();
    if (!text) return '—';
    if (text.indexOf('in') !== -1 || text.indexOf('receipt') !== -1 || text.indexOf('thu') !== -1) return 'Thu';
    if (text.indexOf('out') !== -1 || text.indexOf('payment') !== -1 || text.indexOf('chi') !== -1) return 'Chi';
    return text;
  }

  function renderSalary() {
    var el = document.getElementById('page-salary');
    if (!el) return;

    var monthVal = String(APP.salary.month).padStart(2, '0') + '/' + APP.salary.year;
    var monthInputVal = APP.salary.year + '-' + String(APP.salary.month).padStart(2, '0');

    el.innerHTML =
      '<div class="salary-page">' +
      '<div class="tds-page-title-row">' +
      '<h2 class="tds-page-title">Bảng lương nhân viên</h2>' +
      '<div class="salary-month-picker">' +
      '<input type="month" class="tds-input salary-month-input" id="salary-month" value="' + escapeHtml(monthInputVal) + '">' +
      '</div>' +
      '</div>' +
      '<div id="salary-content" class="salary-content-area"></div>' +
      '</div>';

    var monthInput = document.getElementById('salary-month');
    if (monthInput) {
      monthInput.addEventListener('change', function () {
        var parts = this.value.split('-');
        if (parts.length === 2) {
          APP.salary.year = parseInt(parts[0], 10);
          APP.salary.month = parseInt(parts[1], 10);
          loadSalaryData();
        }
      });
    }

    loadSalaryData();
  }

  async function loadSalaryData() {
    APP.salary.loading = true;
    APP.salary.requestId += 1;
    var requestId = APP.salary.requestId;

    renderSalaryContentLoading();

    var m = APP.salary.month;
    var y = APP.salary.year;
    var dateFrom = y + '-' + String(m).padStart(2, '0') + '-01';
    var lastDay = new Date(y, m, 0).getDate();
    var dateTo = y + '-' + String(m).padStart(2, '0') + '-' + String(lastDay).padStart(2, '0');

    var query = toQueryString({
      dateFrom: dateFrom,
      dateTo: dateTo,
      companyId: getSelectedBranchId(),
    });

    try {
      var data = await api('/api/hr/salary' + query);
      if (requestId !== APP.salary.requestId) return;
      APP.salary.data = data || {};
      APP.salary.loading = false;
      renderSalaryContent();
    } catch (err) {
      if (requestId !== APP.salary.requestId) return;
      APP.salary.loading = false;
      APP.salary.data = null;
      renderSalaryEmpty();
    }
  }

  function renderSalaryContentLoading() {
    var content = document.getElementById('salary-content');
    if (!content) return;
    content.innerHTML =
      '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải dữ liệu lương...</span></div>';
  }

  function renderSalaryEmpty() {
    var content = document.getElementById('salary-content');
    if (!content) return;
    var monthLabel = String(APP.salary.month).padStart(2, '0') + '/' + APP.salary.year;
    content.innerHTML =
      '<div class="tds-card salary-empty-card">' +
      '<div class="salary-empty-illustration">' +
      '<svg width="180" height="140" viewBox="0 0 180 140" fill="none">' +
      '<rect x="40" y="30" width="100" height="80" rx="8" fill="#DBEAFE" stroke="#3B82F6" stroke-width="1.5"/>' +
      '<rect x="55" y="45" width="30" height="20" rx="4" fill="#3B82F6"/>' +
      '<circle cx="120" cy="90" r="15" fill="#FCD34D"/>' +
      '<circle cx="110" cy="100" r="10" fill="#FCD34D" opacity="0.7"/>' +
      '<circle cx="130" cy="95" r="8" fill="#FCD34D" opacity="0.5"/>' +
      '<path d="M60 80h25" stroke="#3B82F6" stroke-width="2" stroke-linecap="round"/>' +
      '<path d="M60 88h15" stroke="#93C5FD" stroke-width="2" stroke-linecap="round"/>' +
      '<rect x="50" y="20" width="20" height="20" rx="4" fill="#EF4444" opacity="0.8"/>' +
      '<path d="M56 28l8 4-8 4z" fill="#fff"/>' +
      '<rect x="100" y="25" width="30" height="15" rx="3" fill="#3B82F6" opacity="0.6"/>' +
      '<path d="M110 30l5 5 5-5" stroke="#fff" stroke-width="1.5" fill="none"/>' +
      '</svg>' +
      '</div>' +
      '<h3 class="salary-empty-title">Bảng Lương</h3>' +
      '<p class="salary-empty-desc">Bảng lương tháng ' + escapeHtml(monthLabel) + ' chưa có. Vui lòng bấm nút "Tính Lương" bên dưới để khởi tạo.</p>' +
      '<button class="tds-btn tds-btn-primary" id="salary-calc-btn">Tính lương</button>' +
      '</div>';

    var calcBtn = document.getElementById('salary-calc-btn');
    if (calcBtn) {
      calcBtn.addEventListener('click', function () {
        showToast('info', 'Đang tính lương tháng ' + monthLabel + '...');
        loadSalaryData();
      });
    }
  }

  function renderSalaryContent() {
    var content = document.getElementById('salary-content');
    if (!content) return;

    var data = APP.salary.data || {};
    var employees = safeItems(data.employees || []);

    if (!data.hasData || !employees.length) {
      renderSalaryEmpty();
      return;
    }

    content.innerHTML =
      '<div class="tds-card">' +
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr>' +
      '<th>STT</th>' +
      '<th>Nhân viên</th>' +
      '<th>Chức vụ</th>' +
      '<th class="text-right">Ngày công</th>' +
      '<th class="text-right">Lương cơ bản</th>' +
      '<th class="text-right">Phụ cấp</th>' +
      '<th class="text-right">Khấu trừ</th>' +
      '<th class="text-right">Thực lĩnh</th>' +
      '</tr></thead>' +
      '<tbody>' +
      employees.map(function (item, idx) {
        var baseSalary = item.monthlySalary || 0;
        var allowance = item.allowance || 0;
        var deduction = item.deduction || 0;
        var netPay = baseSalary + allowance - deduction + (item.commission || 0);
        return (
          '<tr>' +
          '<td>' + (idx + 1) + '</td>' +
          '<td>' + escapeHtml(item.name || '\u2014') + '</td>' +
          '<td>' + escapeHtml(item.jobTitle || item.hrJob || '\u2014') + '</td>' +
          '<td class="text-right">' + escapeHtml(formatNumber(item.workDays || 0)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(baseSalary)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(allowance)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(deduction)) + '</td>' +
          '<td class="text-right font-semibold">' + escapeHtml(formatCurrency(netPay)) + '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>' +
      '</div>';
  }

  function renderCallCenter() {
    var el = document.getElementById('page-callcenter');
    if (!el) return;

    el.innerHTML =
      '<div class="tds-card callcenter-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Tổng đài chăm sóc khách hàng</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="callcenter-export-btn">Xuất Excel</button>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="callcenter-search" placeholder="Nhập số điện thoại khách hàng" value="' + escapeHtml(APP.callcenter.search || '') + '">' +
      '<button class="tds-btn tds-btn-primary" id="callcenter-search-btn">Tìm kiếm</button>' +
      '</div>' +
      '</div>' +
      '<div id="callcenter-results"></div>' +
      '<div class="callcenter-recent">' +
      '<h3>Lịch sử cuộc gọi gần đây</h3>' +
      '<div id="callcenter-recent-list"></div>' +
      '</div>' +
      '</div>';

    var searchInput = document.getElementById('callcenter-search');
    var searchBtn = document.getElementById('callcenter-search-btn');
    var exportBtn = document.getElementById('callcenter-export-btn');

    if (searchInput) {
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          executeCallcenterSearch();
        }
      });
    }

    if (searchBtn) {
      searchBtn.addEventListener('click', function () {
        executeCallcenterSearch();
      });
    }

    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        downloadExcel('customers', {
          search: APP.callcenter.search,
          companyId: getSelectedBranchId(),
          columns: ['ref', 'name', 'phone', 'dateOfBirth', 'companyName', 'totalDebit'],
        });
      });
    }

    renderCallcenterRecentCalls();
    renderCallcenterResults();
  }

  function executeCallcenterSearch() {
    var input = document.getElementById('callcenter-search');
    APP.callcenter.search = input ? input.value.trim() : '';
    loadCallcenterResults();
  }

  async function loadCallcenterResults() {
    APP.callcenter.loading = true;
    APP.callcenter.requestId += 1;
    var requestId = APP.callcenter.requestId;
    renderCallcenterResults();

    try {
      var query = toQueryString({
        search: APP.callcenter.search,
        limit: 30,
        offset: 0,
        companyId: getSelectedBranchId(),
      });
      var data = await api('/api/customers' + query);
      if (requestId !== APP.callcenter.requestId) return;
      APP.callcenter.items = safeItems(data);
    } catch (_e) {
      if (requestId !== APP.callcenter.requestId) return;
      APP.callcenter.items = [];
    } finally {
      if (requestId === APP.callcenter.requestId) {
        APP.callcenter.loading = false;
        renderCallcenterResults();
      }
    }
  }

  function renderCallcenterResults() {
    var container = document.getElementById('callcenter-results');
    if (!container) return;

    if (APP.callcenter.loading) {
      container.innerHTML = '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tìm kiếm khách hàng...</span></div>';
      return;
    }

    if (!APP.callcenter.items.length) {
      container.innerHTML = '<div class="tds-empty"><p>Nhập số điện thoại để tìm khách hàng.</p></div>';
      return;
    }

    container.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table callcenter-table">' +
      '<thead>' +
      '<tr>' +
      '<th>Mã KH</th>' +
      '<th>Khách hàng</th>' +
      '<th>Điện thoại</th>' +
      '<th>Chi nhánh</th>' +
      '<th></th>' +
      '</tr>' +
      '</thead>' +
      '<tbody>' +
      APP.callcenter.items.map(function (item) {
        return (
          '<tr class="callcenter-row" data-id="' + escapeHtml(item.id || '') + '">' +
          '<td>' + escapeHtml(item.ref || '—') + '</td>' +
          '<td>' + escapeHtml(item.name || item.displayName || 'N/A') + '</td>' +
          '<td>' + escapeHtml(item.phone || '—') + '</td>' +
          '<td>' + escapeHtml(item.companyName || '—') + '</td>' +
          '<td class="text-right"><button class="tds-btn tds-btn-sm tds-btn-secondary callcenter-open" data-id="' + escapeHtml(item.id || '') + '">Mở hồ sơ</button></td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    var rows = container.querySelectorAll('.callcenter-row, .callcenter-open');
    for (var i = 0; i < rows.length; i++) {
      rows[i].addEventListener('click', function (e) {
        var id = this.getAttribute('data-id');
        if (!id) return;
        e.preventDefault();
        openCustomerDetail(id);
      });
    }
  }

  function renderCallcenterRecentCalls() {
    var list = document.getElementById('callcenter-recent-list');
    if (!list) return;

    if (!APP.callcenter.recentCalls.length) {
      list.innerHTML = '<div class="tds-empty"><p>Chưa có lịch sử cuộc gọi</p></div>';
      return;
    }

    list.innerHTML = APP.callcenter.recentCalls.map(function (item) {
      return (
        '<div class="callcenter-log-item">' +
        '<div class="callcenter-log-name">' + escapeHtml(item.name || 'N/A') + '</div>' +
        '<div class="callcenter-log-meta">' +
        '<span>' + escapeHtml(item.phone || '—') + '</span>' +
        '<span>' + escapeHtml(formatDateTime(item.openedAt)) + '</span>' +
        '</div>' +
        '</div>'
      );
    }).join('');
  }

  async function openCustomerDetail(customerId) {
    if (!customerId) return;

    openDrawer(
      '<div class="drawer-header"><h3>Chi tiết khách hàng</h3><button class="modal-close-btn" onclick="window.TDS.closeDrawer()">&times;</button></div>' +
      '<div class="drawer-body"><div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải hồ sơ...</span></div></div>',
      760
    );

    try {
      var detailPromise = api('/api/customers/' + encodeURIComponent(customerId));
      var appointmentPromise = api('/api/customers/' + encodeURIComponent(customerId) + '/appointments?limit=10&offset=0').catch(function () { return { items: [] }; });
      var treatmentPromise = api('/api/customers/' + encodeURIComponent(customerId) + '/treatments?limit=10&offset=0').catch(function () { return { items: [] }; });
      var examPromise = api('/api/dot-khams' + toQueryString({
        partnerId: customerId,
        companyId: getSelectedBranchId(),
        limit: 10,
        offset: 0,
      })).catch(function () { return { items: [] }; });
      var paymentPromise = api('/api/payments' + toQueryString({
        partnerId: customerId,
        companyId: getSelectedBranchId(),
        limit: 10,
        offset: 0,
      })).catch(function () { return { items: [] }; });

      var result = await Promise.all([
        detailPromise,
        appointmentPromise,
        treatmentPromise,
        examPromise,
        paymentPromise,
      ]);
      var detail = result[0] || {};
      var appointmentRows = safeItems(result[1]);
      var treatmentRows = safeItems(result[2]);
      var examRows = safeItems(result[3]);
      var paymentRows = safeItems(result[4]);

      addRecentCall({
        id: detail.id || customerId,
        name: detail.name || detail.displayName || 'N/A',
        phone: detail.phone || '—',
      });
      renderCallcenterRecentCalls();

      var drawerContent =
        '<div class="drawer-header">' +
        '<h3>' + escapeHtml(detail.name || detail.displayName || 'Khách hàng') + '</h3>' +
        '<div class="drawer-header-actions">' +
        '<button class="tds-btn tds-btn-sm tds-btn-secondary" id="drawer-edit-customer">Sửa</button>' +
        '<button class="modal-close-btn" onclick="window.TDS.closeDrawer()">&times;</button>' +
        '</div>' +
        '</div>' +
        '<div class="drawer-body">' +
        '<div class="reports-tabs customer-detail-tabs">' +
        '<button class="report-tab-btn active" data-customer-tab="profile">Hồ sơ</button>' +
        '<button class="report-tab-btn" data-customer-tab="appointments">Lịch hẹn</button>' +
        '<button class="report-tab-btn" data-customer-tab="treatments">Điều trị</button>' +
        '<button class="report-tab-btn" data-customer-tab="quotations">Báo giá</button>' +
        '<button class="report-tab-btn" data-customer-tab="exams">Đợt khám</button>' +
        '<button class="report-tab-btn" data-customer-tab="payments">Thanh toán</button>' +
        '<button class="report-tab-btn" data-customer-tab="labo">Labo</button>' +
        '<button class="report-tab-btn" data-customer-tab="advance">Tạm ứng</button>' +
        '<button class="report-tab-btn" data-customer-tab="debt">Sổ công nợ</button>' +
        '<button class="report-tab-btn" data-customer-tab="images">Hình ảnh</button>' +
        '<button class="report-tab-btn" data-customer-tab="teeth">Sơ đồ răng</button>' +
        '</div>' +
        '<div class="customer-tab-panels">' +
        /* -- Profile Tab -- */
        '<div class="customer-tab-panel" data-customer-panel="profile">' +
        '<div class="customer-detail-grid">' +
        '<div><span class="text-muted">Mã KH</span><p>' + escapeHtml(detail.ref || '—') + '</p></div>' +
        '<div><span class="text-muted">Điện thoại</span><p>' + escapeHtml(detail.phone || '—') + '</p></div>' +
        '<div><span class="text-muted">Email</span><p>' + escapeHtml(detail.email || '—') + '</p></div>' +
        '<div><span class="text-muted">Chi nhánh</span><p>' + escapeHtml(detail.companyName || '—') + '</p></div>' +
        '<div><span class="text-muted">Ngày sinh</span><p>' + escapeHtml(formatDate(detail.dateOfBirth || detail.birthdate)) + '</p></div>' +
        '<div><span class="text-muted">Giới tính</span><p>' + escapeHtml(detail.gender || '—') + '</p></div>' +
        '<div><span class="text-muted">Địa chỉ</span><p>' + escapeHtml(detail.address || detail.street || '—') + '</p></div>' +
        '<div><span class="text-muted">Nguồn</span><p>' + escapeHtml(detail.source || '—') + '</p></div>' +
        '<div><span class="text-muted">Nhóm KH</span><p>' + escapeHtml(detail.categories || '—') + '</p></div>' +
        '<div><span class="text-muted">Loại thẻ</span><p>' + escapeHtml(detail.cardType || '—') + '</p></div>' +
        '<div><span class="text-muted">Công nợ</span><p class="text-danger">' + escapeHtml(formatCurrency(detail.totalDebit || 0)) + '</p></div>' +
        '<div><span class="text-muted">Doanh thu</span><p class="text-success">' + escapeHtml(formatCurrency(detail.amountRevenueTotal || 0)) + '</p></div>' +
        '<div><span class="text-muted">Điều trị</span><p>' + escapeHtml(formatCurrency(detail.amountTreatmentTotal || 0)) + '</p></div>' +
        '<div><span class="text-muted">Trạng thái ĐT</span><p>' + escapeHtml(detail.orderState || '—') + '</p></div>' +
        '</div>' +
        (detail.comment ? '<div class="customer-notes mt-md"><span class="text-muted">Ghi chú</span><p>' + escapeHtml(detail.comment) + '</p></div>' : '') +
        '</div>' +
        /* -- Appointments Tab -- */
        '<div class="customer-tab-panel" data-customer-panel="appointments" style="display:none">' +
        renderSimpleTable(
          ['Ngày', 'Bác sĩ', 'Trạng thái', 'Ghi chú'],
          appointmentRows.map(function (item) {
            return [
              escapeHtml(formatDate(item.appointmentDate || item.date)),
              escapeHtml(item.doctorName || '—'),
              '<span class="tds-badge ' + stateBadgeClass(item.state || item.status) + '">' + escapeHtml(translateState(item.state || item.status)) + '</span>',
              escapeHtml(item.notes || item.note || '—'),
            ];
          }),
          'Chưa có lịch hẹn'
        ) +
        '</div>' +
        /* -- Treatments Tab -- */
        '<div class="customer-tab-panel" data-customer-panel="treatments" style="display:none">' +
        renderSimpleTable(
          ['Mã phiếu', 'Ngày', 'Trạng thái', 'Tổng tiền', 'Số dòng'],
          treatmentRows.map(function (item) {
            var lines = safeItems(item.lines || item.lineItems || []);
            return [
              escapeHtml(item.name || item.ref || item.id || '—'),
              escapeHtml(formatDate(item.date || item.orderDate || item.createdAt)),
              '<span class="tds-badge ' + stateBadgeClass(item.state || item.status) + '">' + escapeHtml(translateState(item.state || item.status)) + '</span>',
              '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.totalAmount || item.amountTotal || 0)) + '</span>',
              '<span class="text-right d-block">' + escapeHtml(formatNumber(lines.length)) + '</span>',
            ];
          }),
          'Chưa có phiếu điều trị'
        ) +
        '</div>' +
        /* -- Quotations Tab -- */
        '<div class="customer-tab-panel" data-customer-panel="quotations" style="display:none">' +
        '<div class="tds-loading" id="drawer-quotation-loading"><div class="tds-spinner"></div><span>Đang tải...</span></div>' +
        '</div>' +
        /* -- Exams Tab -- */
        '<div class="customer-tab-panel" data-customer-panel="exams" style="display:none">' +
        renderSimpleTable(
          ['Ngày', 'Đợt khám', 'Bác sĩ', 'Trạng thái', 'Lý do'],
          examRows.map(function (item) {
            return [
              escapeHtml(formatDate(item.date)),
              escapeHtml(item.name || item.sessionName || item.id || '—'),
              escapeHtml(item.doctorName || '—'),
              '<span class="tds-badge ' + stateBadgeClass(item.state) + '">' + escapeHtml(translateState(item.state)) + '</span>',
              escapeHtml(item.reason || '—'),
            ];
          }),
          'Chưa có dữ liệu đợt khám'
        ) +
        '</div>' +
        /* -- Payments Tab -- */
        '<div class="customer-tab-panel" data-customer-panel="payments" style="display:none">' +
        renderSimpleTable(
          ['Ngày', 'Loại', 'Số tiền', 'Sổ quỹ', 'Trạng thái'],
          paymentRows.map(function (item) {
            return [
              escapeHtml(formatDate(item.date)),
              escapeHtml(normalizePaymentTypeLabel(item.paymentType)),
              '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.amount || 0)) + '</span>',
              escapeHtml(item.journalName || '—'),
              '<span class="tds-badge ' + stateBadgeClass(item.state) + '">' + escapeHtml(translateState(item.state)) + '</span>',
            ];
          }),
          'Chưa có lịch sử thanh toán'
        ) +
        '</div>' +
        /* -- Labo Tab (T-053) -- */
        '<div class="customer-tab-panel" data-customer-panel="labo" style="display:none">' +
        '<div class="tds-loading" id="drawer-labo-loading"><div class="tds-spinner"></div><span>Đang tải...</span></div>' +
        '</div>' +
        /* -- Advance Payments Tab (T-053) -- */
        '<div class="customer-tab-panel" data-customer-panel="advance" style="display:none">' +
        '<div class="tds-loading" id="drawer-advance-loading"><div class="tds-spinner"></div><span>Đang tải...</span></div>' +
        '</div>' +
        /* -- Debt Ledger Tab (T-053) -- */
        '<div class="customer-tab-panel" data-customer-panel="debt" style="display:none">' +
        buildCustomerDebtPanel(detail, paymentRows, treatmentRows) +
        '</div>' +
        /* -- Images Tab (T-053) -- */
        '<div class="customer-tab-panel" data-customer-panel="images" style="display:none">' +
        '<div class="tds-loading" id="drawer-images-loading"><div class="tds-spinner"></div><span>Đang tải...</span></div>' +
        '</div>' +
        /* -- Teeth Map Tab (T-054) -- */
        '<div class="customer-tab-panel" data-customer-panel="teeth" style="display:none">' +
        buildTeethChartPanel(detail, treatmentRows) +
        '</div>' +
        '</div>' +
        '</div>';

      openDrawer(drawerContent, 760);
      bindCustomerDetailTabs();
      bindDrawerEditButton(detail);
      loadDrawerQuotationData(customerId);
      loadDrawerLaboData(customerId);
      loadDrawerAdvanceData(customerId);
      loadDrawerImagesData(customerId);
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể tải chi tiết khách hàng');
      closeDrawer();
    }
  }

  function bindDrawerEditButton(customer) {
    var btn = document.getElementById('drawer-edit-customer');
    if (!btn) return;
    btn.addEventListener('click', function () {
      closeDrawer();
      openCustomerModal(customer);
    });
  }

  async function loadDrawerLaboData(customerId) {
    var panel = document.querySelector('[data-customer-panel="labo"]');
    if (!panel) return;
    try {
      var data = await api('/api/sale-orders' + toQueryString({
        partnerId: customerId,
        companyId: getSelectedBranchId(),
        limit: 20,
        offset: 0,
      }));
      var rows = safeItems(data);
      panel.innerHTML = renderSimpleTable(
        ['Mã phiếu', 'Ngày', 'Trạng thái', 'Tổng tiền'],
        rows.map(function (item) {
          return [
            escapeHtml(item.name || item.id || '—'),
            escapeHtml(formatDate(item.date || item.orderDate)),
            '<span class="tds-badge ' + stateBadgeClass(item.state) + '">' + escapeHtml(translateState(item.state)) + '</span>',
            '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.totalAmount || item.amountTotal || 0)) + '</span>',
          ];
        }),
        'Không có phiếu Labo'
      );
    } catch (_err) {
      panel.innerHTML = renderEmptyState('Không thể tải dữ liệu Labo');
    }
  }

  async function loadDrawerQuotationData(customerId) {
    var panel = document.querySelector('[data-customer-panel="quotations"]');
    if (!panel) return;
    try {
      var data = await api('/api/customers/' + encodeURIComponent(customerId) + '/quotations?limit=20&offset=0');
      var rows = safeItems(data);
      panel.innerHTML = renderSimpleTable(
        ['Mã báo giá', 'Ngày', 'Trạng thái', 'Tổng tiền'],
        rows.map(function (item) {
          return [
            escapeHtml(item.name || item.ref || item.code || item.id || '—'),
            escapeHtml(formatDate(item.date || item.quoteDate || item.createdAt || item.createDate)),
            escapeHtml(item.state || item.status || '—'),
            '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.totalAmount || item.amountTotal || item.amount || 0)) + '</span>',
          ];
        }),
        'Chưa có báo giá'
      );
    } catch (_err) {
      panel.innerHTML = renderEmptyState('Không thể tải dữ liệu báo giá');
    }
  }

  async function loadDrawerImagesData(customerId) {
    var panel = document.querySelector('[data-customer-panel="images"]');
    if (!panel) return;
    try {
      var data = await api('/api/customers/' + encodeURIComponent(customerId) + '/images?limit=100&offset=0');
      var rows = safeItems(data);
      if (!rows.length) {
        panel.innerHTML = '<div class="customer-images-empty"><p>Chưa có hình ảnh</p><p class="text-secondary">Không tìm thấy ảnh cho khách hàng này.</p></div>';
        return;
      }

      var cards = [];
      for (var i = 0; i < rows.length; i++) {
        var src = resolveCustomerImageSrc(rows[i]);
        if (!src) continue;
        cards.push(
          '<figure class="customer-image-card">' +
          '<a href="' + escapeHtml(src) + '" target="_blank" rel="noopener noreferrer">' +
          '<img src="' + escapeHtml(src) + '" alt="Ảnh khách hàng">' +
          '</a>' +
          '<figcaption>' + escapeHtml(rows[i].name || rows[i].title || rows[i].note || rows[i].id || 'Ảnh') + '</figcaption>' +
          '</figure>'
        );
      }

      if (!cards.length) {
        panel.innerHTML = '<div class="customer-images-empty"><p>Chưa có hình ảnh hiển thị được</p><p class="text-secondary">Dữ liệu ảnh tồn tại nhưng không có URL/base64 hợp lệ.</p></div>';
        return;
      }

      panel.innerHTML = '<div class="customer-images-grid">' + cards.join('') + '</div>';
    } catch (_err) {
      panel.innerHTML = renderEmptyState('Không thể tải hình ảnh khách hàng');
    }
  }

  function resolveCustomerImageSrc(item) {
    if (!item) return '';
    var urlFields = [
      'url',
      'imageUrl',
      'imageurl',
      'src',
      'path',
      'fileUrl',
      'fileurl',
      'thumbnailUrl',
      'thumbnailurl',
    ];
    for (var i = 0; i < urlFields.length; i++) {
      var raw = item[urlFields[i]];
      if (typeof raw !== 'string') continue;
      var value = raw.trim();
      if (!value) continue;
      var lower = value.toLowerCase();
      if (lower.indexOf('http://') === 0 || lower.indexOf('https://') === 0 || lower.indexOf('/') === 0 || lower.indexOf('data:image/') === 0) {
        return value;
      }
    }

    var base64Fields = ['base64', 'imageBase64', 'imagebase64', 'image', 'photo', 'data'];
    for (var j = 0; j < base64Fields.length; j++) {
      var base64 = item[base64Fields[j]];
      if (typeof base64 !== 'string') continue;
      var b64 = base64.trim();
      if (!b64) continue;
      if (b64.indexOf('data:image/') === 0) return b64;
      if (b64.length > 64 && b64.indexOf(' ') === -1) return 'data:image/jpeg;base64,' + b64;
    }
    return '';
  }

  async function loadDrawerAdvanceData(customerId) {
    var panel = document.querySelector('[data-customer-panel="advance"]');
    if (!panel) return;
    try {
      var data = await api('/api/payments' + toQueryString({
        partnerId: customerId,
        paymentType: 'inbound',
        companyId: getSelectedBranchId(),
        limit: 20,
        offset: 0,
      }));
      var rows = safeItems(data);
      panel.innerHTML = renderSimpleTable(
        ['Ngày', 'Chứng từ', 'Số tiền', 'Sổ quỹ', 'Trạng thái'],
        rows.map(function (item) {
          return [
            escapeHtml(formatDate(item.date)),
            escapeHtml(item.name || '—'),
            '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.amount || 0)) + '</span>',
            escapeHtml(item.journalName || '—'),
            '<span class="tds-badge ' + stateBadgeClass(item.state) + '">' + escapeHtml(translateState(item.state)) + '</span>',
          ];
        }),
        'Chưa có tạm ứng'
      );
    } catch (_err) {
      panel.innerHTML = renderEmptyState('Không thể tải dữ liệu tạm ứng');
    }
  }

  function buildCustomerDebtPanel(detail, paymentRows, treatmentRows) {
    var entries = [];
    for (var i = 0; i < treatmentRows.length; i++) {
      var t = treatmentRows[i];
      entries.push({
        date: t.date || t.orderDate || t.createdAt || '',
        description: 'Phiếu điều trị: ' + (t.name || t.ref || t.id || '—'),
        debit: toNumber(t.totalAmount || t.amountTotal),
        credit: 0,
      });
    }
    for (var j = 0; j < paymentRows.length; j++) {
      var p = paymentRows[j];
      entries.push({
        date: p.date || '',
        description: 'Thanh toán: ' + (p.name || '—'),
        debit: 0,
        credit: toNumber(p.amount),
      });
    }
    entries.sort(function (a, b) {
      return String(a.date || '').localeCompare(String(b.date || ''));
    });

    var balance = 0;
    var tableRows = entries.map(function (entry) {
      balance += entry.debit - entry.credit;
      return [
        escapeHtml(formatDate(entry.date)),
        escapeHtml(entry.description),
        entry.debit ? '<span class="text-right d-block text-danger">' + escapeHtml(formatCurrency(entry.debit)) + '</span>' : '<span class="text-right d-block">—</span>',
        entry.credit ? '<span class="text-right d-block text-success">' + escapeHtml(formatCurrency(entry.credit)) + '</span>' : '<span class="text-right d-block">—</span>',
        '<span class="text-right d-block">' + escapeHtml(formatCurrency(balance)) + '</span>',
      ];
    });

    return (
      '<div class="debt-summary mb-md">' +
      '<span class="text-muted">Tổng công nợ hiện tại: </span>' +
      '<strong class="text-danger">' + escapeHtml(formatCurrency(detail.totalDebit || 0)) + '</strong>' +
      '</div>' +
      renderSimpleTable(
        ['Ngày', 'Diễn giải', 'Nợ (Debit)', 'Có (Credit)', 'Số dư'],
        tableRows,
        'Chưa có dữ liệu công nợ'
      )
    );
  }

  // ---------------------------------------------------------------------------
  // Teeth Chart (T-054)
  // ---------------------------------------------------------------------------
  function buildTeethChartPanel(detail, treatmentRows) {
    var treatedTeeth = {};
    for (var i = 0; i < treatmentRows.length; i++) {
      var lines = safeItems(treatmentRows[i].lines || treatmentRows[i].lineItems || []);
      for (var j = 0; j < lines.length; j++) {
        var teeth = String(lines[j].teeth || lines[j].toothNumber || '').split(/[,;\s]+/).filter(Boolean);
        for (var k = 0; k < teeth.length; k++) {
          var num = parseInt(teeth[k], 10);
          if (num >= 11 && num <= 48) {
            treatedTeeth[num] = {
              product: lines[j].productName || lines[j].name || 'Dịch vụ',
              state: treatmentRows[i].state || 'done',
            };
          }
        }
      }
    }

    var ADULT_TEETH = [
      [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28],
      [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38],
    ];

    var html = '<div class="teeth-chart-container">';
    html += '<div class="teeth-chart-label">Trên</div>';
    html += '<div class="teeth-row">';
    for (var t = 0; t < ADULT_TEETH[0].length; t++) {
      var num1 = ADULT_TEETH[0][t];
      var treated1 = treatedTeeth[num1];
      html += '<button class="tooth-cell' + (treated1 ? ' tooth-treated' : '') + '" data-tooth="' + num1 + '" title="' + (treated1 ? escapeHtml(treated1.product) : 'Răng ' + num1) + '">' + num1 + '</button>';
    }
    html += '</div>';
    html += '<div class="teeth-chart-divider"></div>';
    html += '<div class="teeth-row">';
    for (var b = 0; b < ADULT_TEETH[1].length; b++) {
      var num2 = ADULT_TEETH[1][b];
      var treated2 = treatedTeeth[num2];
      html += '<button class="tooth-cell' + (treated2 ? ' tooth-treated' : '') + '" data-tooth="' + num2 + '" title="' + (treated2 ? escapeHtml(treated2.product) : 'Răng ' + num2) + '">' + num2 + '</button>';
    }
    html += '</div>';
    html += '<div class="teeth-chart-label">Dưới</div>';
    html += '</div>';

    html += '<div class="teeth-legend mt-md">';
    html += '<span class="teeth-legend-item"><span class="tooth-cell tooth-sample"></span> Bình thường</span>';
    html += '<span class="teeth-legend-item"><span class="tooth-cell tooth-treated tooth-sample"></span> Đã điều trị</span>';
    html += '</div>';

    var treatedKeys = Object.keys(treatedTeeth);
    if (treatedKeys.length) {
      html += '<div class="teeth-detail-list mt-md">';
      html += '<h4>Chi tiết điều trị theo răng</h4>';
      html += renderSimpleTable(
        ['Răng', 'Dịch vụ', 'Trạng thái'],
        treatedKeys.sort(function (a, b) { return Number(a) - Number(b); }).map(function (key) {
          var info = treatedTeeth[key];
          return [
            escapeHtml(key),
            escapeHtml(info.product),
            '<span class="tds-badge ' + stateBadgeClass(info.state) + '">' + escapeHtml(translateState(info.state)) + '</span>',
          ];
        }),
        ''
      );
      html += '</div>';
    }

    return html;
  }

  function bindCustomerDetailTabs() {
    var container = document.getElementById('drawer-container');
    if (!container) return;

    var tabButtons = container.querySelectorAll('[data-customer-tab]');
    if (!tabButtons.length) return;

    for (var i = 0; i < tabButtons.length; i++) {
      tabButtons[i].addEventListener('click', function () {
        var target = this.getAttribute('data-customer-tab');
        if (!target) return;

        for (var j = 0; j < tabButtons.length; j++) {
          tabButtons[j].classList.remove('active');
        }
        this.classList.add('active');

        var panels = container.querySelectorAll('[data-customer-panel]');
        for (var k = 0; k < panels.length; k++) {
          var panel = panels[k];
          if (panel.getAttribute('data-customer-panel') === target) {
            panel.style.display = '';
          } else {
            panel.style.display = 'none';
          }
        }
      });
    }

    // Bind tooth click handlers
    var toothCells = container.querySelectorAll('.tooth-cell[data-tooth]');
    for (var t = 0; t < toothCells.length; t++) {
      toothCells[t].addEventListener('click', function () {
        var tooth = this.getAttribute('data-tooth');
        var title = this.getAttribute('title') || 'Răng ' + tooth;
        showToast('info', title);
      });
    }
  }

  function addRecentCall(item) {
    if (!item || !item.id) return;
    APP.callcenter.recentCalls = APP.callcenter.recentCalls.filter(function (entry) {
      return entry.id !== item.id;
    });
    APP.callcenter.recentCalls.unshift({
      id: item.id,
      name: item.name || 'N/A',
      phone: item.phone || '—',
      openedAt: new Date().toISOString(),
    });
    APP.callcenter.recentCalls = APP.callcenter.recentCalls.slice(0, 15);
    saveRecentCalls(APP.callcenter.recentCalls);
  }

  function renderReports() {
    var el = document.getElementById('page-reports');
    if (!el) return;

    var rptMode = APP.reports.rptMode || 'day';
    APP.reports.rptMode = rptMode;

    el.innerHTML =
      '<div class="rpt-shell">' +
      '<div class="rpt-page-header">' +
      '<h2>Báo cáo tổng quan</h2>' +
      '</div>' +

      // Summary cards row (6 cards matching the reference screenshot)
      '<div class="rpt-summary-cards" id="rpt-summary-cards">' +
      rptSummaryCardHTML('cash', 'Quỹ tiền mặt', 0, '#3B82F6', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M8 10h8M8 14h8"/></svg>') +
      rptSummaryCardHTML('bank', 'Quỹ ngân hàng', 0, '#10B981', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 3H8l-2 4h12l-2-4z"/></svg>') +
      rptSummaryCardHTML('supplier_debt', 'Nợ phải trả NCC', 0, '#EF4444', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>') +
      rptSummaryCardHTML('customer_debt', 'Nợ phải thu KH', 0, '#F59E0B', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>') +
      rptSummaryCardHTML('insurance_debt', 'Nợ phải thu BH', 0, '#6366F1', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>') +
      rptSummaryCardHTML('expected', 'Dự kiến thu', 0, '#0EA5E9', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>') +
      '</div>' +

      // Date controls bar
      '<div class="rpt-date-bar">' +
      '<div class="rpt-mode-toggle">' +
      '<button class="tds-btn tds-btn-sm ' + (rptMode === 'day' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-rpt-mode="day">Ngày</button>' +
      '<button class="tds-btn tds-btn-sm ' + (rptMode === 'month' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-rpt-mode="month">Tháng</button>' +
      '</div>' +
      '<div class="rpt-date-range">' +
      '<input class="tds-input tds-input-sm" id="rpt-date-from" type="date" value="' + escapeHtml(APP.reports.dateFrom) + '">' +
      '<span class="rpt-date-sep">&ndash;</span>' +
      '<input class="tds-input tds-input-sm" id="rpt-date-to" type="date" value="' + escapeHtml(APP.reports.dateTo) + '">' +
      '<button class="tds-btn tds-btn-sm tds-btn-secondary" id="rpt-date-icon" title="Áp dụng"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg></button>' +
      '</div>' +
      '</div>' +

      // Charts section
      '<div class="rpt-charts-section">' +
      '<div class="rpt-chart-card">' +
      '<h3 class="rpt-chart-title">BIỂU ĐỒ <span class="rpt-chart-highlight">DOANH THU</span></h3>' +
      '<canvas id="rpt-revenue-chart" width="600" height="300"></canvas>' +
      '<div class="rpt-chart-legend"><span class="rpt-legend-item"><span class="rpt-legend-dot" style="background:#3B82F6"></span> Doanh thu</span></div>' +
      '</div>' +
      '<div class="rpt-chart-card">' +
      '<h3 class="rpt-chart-title">BIỂU ĐỒ THU - CHI</h3>' +
      '<canvas id="rpt-income-expense-chart" width="600" height="300"></canvas>' +
      '<div class="rpt-chart-legend"><span class="rpt-legend-item"><span class="rpt-legend-dot" style="background:#3B82F6"></span> Thu</span><span class="rpt-legend-item"><span class="rpt-legend-dot" style="background:#EF4444"></span> Chi</span></div>' +
      '</div>' +
      '</div>' +

      // Keep existing tabs for detail drill-down
      '<div class="rpt-detail-section">' +
      '<div class="reports-tabs">' +
      Object.keys(REPORT_TABS).map(function (key) {
        var tab = REPORT_TABS[key];
        var activeClass = key === APP.reports.tab ? 'active' : '';
        return '<button class="report-tab-btn ' + activeClass + '" data-report-tab="' + key + '">' + escapeHtml(tab.label) + '</button>';
      }).join('') +
      '</div>' +
      '<div id="reports-content"></div>' +
      '</div>' +
      '</div>';

    // Bind mode toggle
    var modeBtns = el.querySelectorAll('[data-rpt-mode]');
    for (var mi = 0; mi < modeBtns.length; mi++) {
      modeBtns[mi].addEventListener('click', function () {
        var mode = this.getAttribute('data-rpt-mode');
        if (mode === APP.reports.rptMode) return;
        APP.reports.rptMode = mode;
        renderReports();
      });
    }

    // Bind date apply
    var dateIcon = document.getElementById('rpt-date-icon');
    if (dateIcon) {
      dateIcon.addEventListener('click', function () {
        var fromInput = document.getElementById('rpt-date-from');
        var toInput = document.getElementById('rpt-date-to');
        APP.reports.dateFrom = fromInput && fromInput.value ? fromInput.value : APP.reports.dateFrom;
        APP.reports.dateTo = toInput && toInput.value ? toInput.value : APP.reports.dateTo;
        loadReportOverviewData();
        loadReportTabData();
      });
    }

    // Bind tab buttons
    var tabButtons = el.querySelectorAll('.report-tab-btn');
    for (var i = 0; i < tabButtons.length; i++) {
      tabButtons[i].addEventListener('click', function () {
        var tab = this.getAttribute('data-report-tab');
        if (!REPORT_TABS[tab] || tab === APP.reports.tab) return;
        APP.reports.tab = tab;
        // Update active state
        for (var t = 0; t < tabButtons.length; t++) tabButtons[t].classList.remove('active');
        this.classList.add('active');
        loadReportTabData();
      });
    }

    loadReportOverviewData();
    loadReportTabData();
  }

  function rptSummaryCardHTML(key, label, value, color, iconSvg) {
    return (
      '<div class="rpt-summary-card" data-rpt-card="' + key + '">' +
      '<div class="rpt-card-icon" style="background:' + color + '20;color:' + color + '">' + iconSvg + '</div>' +
      '<div class="rpt-card-body">' +
      '<span class="rpt-card-label">' + escapeHtml(label) + ' <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="' + color + '" stroke-width="2" style="vertical-align:-1px"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg></span>' +
      '<span class="rpt-card-value" data-rpt-value="' + key + '">' + rptFormatVND(value) + '</span>' +
      '</div>' +
      '</div>'
    );
  }

  function rptFormatVND(value) {
    if (!value && value !== 0) return '0';
    return new Intl.NumberFormat('vi-VN').format(Math.round(Number(value) || 0));
  }

  async function loadReportOverviewData() {
    APP.reports.overviewRequestId += 1;
    var requestId = APP.reports.overviewRequestId;

    try {
      var branchId = getSelectedBranchId();
      var query = toQueryString({
        dateFrom: APP.reports.dateFrom,
        dateTo: APP.reports.dateTo,
        companyId: branchId,
      });
      var summary = null;
      try {
        summary = await api('/api/reports/summary' + query);
      } catch (_e) { summary = null; }

      if (requestId !== APP.reports.overviewRequestId) return;

      if (summary) {
        rptUpdateCardValue('cash', summary.cashFund || summary.cashBalance || summary.cash || 0);
        rptUpdateCardValue('bank', summary.bankFund || summary.bankBalance || summary.bank || 0);
        rptUpdateCardValue('supplier_debt', summary.supplierDebt || 0);
        rptUpdateCardValue('customer_debt', summary.customerDebt || 0);
        rptUpdateCardValue('insurance_debt', summary.insuranceDebt || 0);
        rptUpdateCardValue('expected', summary.expectedRevenue || summary.revenue || 0);
      }

      var trend = null;
      try {
        var dayCount = rptDateRangeDays(APP.reports.dateFrom, APP.reports.dateTo);
        trend = await api('/api/reports/revenue-trend' + toQueryString({
          companyId: branchId,
          dateTo: APP.reports.dateTo,
          days: dayCount,
        }));
      } catch (_e) { trend = null; }

      if (requestId !== APP.reports.overviewRequestId) return;
      rptDrawRevenueChart(trend);
      rptDrawIncomeExpenseChart(trend);
    } catch (err) {
      if (window.console) console.error('report-overview-error', err);
    }
  }

  function rptDateRangeDays(fromValue, toValue) {
    var from = new Date(fromValue);
    var to = new Date(toValue);
    if (isNaN(from.getTime()) || isNaN(to.getTime())) return 30;
    var diff = Math.floor((startOfDay(to) - startOfDay(from)) / (24 * 60 * 60 * 1000)) + 1;
    if (diff < 1) return 1;
    if (diff > 90) return 90;
    return diff;
  }

  function rptUpdateCardValue(key, value) {
    var el = document.querySelector('[data-rpt-value="' + key + '"]');
    if (el) el.textContent = rptFormatVND(value);
  }

  function rptSetupCanvasSize(canvas) {
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.parentElement.getBoundingClientRect();
    var w = Math.floor(rect.width - 32) || 600;
    var h = 280;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);
    return { ctx: ctx, w: w, h: h, dpr: dpr };
  }

  function rptBindChartTooltip(canvas, barRects, fullLabels, seriesNames) {
    var tooltip = canvas.parentElement.querySelector('.rpt-chart-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.className = 'rpt-chart-tooltip';
      canvas.parentElement.style.position = 'relative';
      canvas.parentElement.appendChild(tooltip);
    }

    canvas.addEventListener('mousemove', function (e) {
      var cr = canvas.getBoundingClientRect();
      var mx = e.clientX - cr.left;
      var my = e.clientY - cr.top;
      var hit = null;
      for (var i = 0; i < barRects.length; i++) {
        var r = barRects[i];
        if (mx >= r.x && mx <= r.x + r.w && my >= r.y && my <= r.y + r.h) {
          hit = r;
          break;
        }
      }
      if (!hit) {
        tooltip.style.display = 'none';
        return;
      }
      var label = fullLabels[hit.idx] || '';
      var lines = '<div class="rpt-tooltip-label">Ngày ' + escapeHtml(label) + '</div>';
      for (var si = 0; si < seriesNames.length; si++) {
        var dotColor = hit.colors ? hit.colors[si] : '#3B82F6';
        var val = hit.values ? hit.values[si] : 0;
        lines += '<div class="rpt-tooltip-row"><span class="rpt-tooltip-dot" style="background:' + dotColor + '"></span> ' + escapeHtml(seriesNames[si]) + ': ' + rptFormatVND(val) + '</div>';
      }
      tooltip.innerHTML = lines;
      tooltip.style.display = 'block';
      var tx = Math.min(hit.x + hit.w + 8, canvas.offsetWidth - 160);
      var ty = Math.max(hit.y - 10, 0);
      tooltip.style.left = tx + 'px';
      tooltip.style.top = ty + 'px';
    });

    canvas.addEventListener('mouseleave', function () {
      tooltip.style.display = 'none';
    });
  }

  function rptDrawRevenueChart(trend) {
    var canvas = document.getElementById('rpt-revenue-chart');
    if (!canvas) return;
    var size = rptSetupCanvasSize(canvas);
    var ctx = size.ctx, w = size.w, h = size.h;

    var items = trend && Array.isArray(trend.items) ? trend.items : (trend && Array.isArray(trend) ? trend : []);
    if (!items.length) {
      ctx.fillStyle = '#94A3B8';
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Không có dữ liệu', w / 2, h / 2);
      return;
    }

    var values = items.map(function (r) { return Number(r.revenue || r.totalAmount || r.amount || 0); });
    var labels = items.map(function (r) { return String(r.date || r.label || r.reportDate || '').slice(5); });
    var fullLabels = items.map(function (r) { return String(r.date || r.label || r.reportDate || '').replace(/^(\d{4})-(\d{2})-(\d{2})$/, '$3-$2-$1'); });
    var barRects = rptDrawBarChart(ctx, w, h, labels, [{ values: values, color: '#3B82F6' }]);
    rptBindChartTooltip(canvas, barRects, fullLabels, ['Doanh thu']);
  }

  function rptDrawIncomeExpenseChart(trend) {
    var canvas = document.getElementById('rpt-income-expense-chart');
    if (!canvas) return;
    var size = rptSetupCanvasSize(canvas);
    var ctx = size.ctx, w = size.w, h = size.h;

    var items = trend && Array.isArray(trend.items) ? trend.items : (trend && Array.isArray(trend) ? trend : []);
    if (!items.length) {
      ctx.fillStyle = '#94A3B8';
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Không có dữ liệu', w / 2, h / 2);
      return;
    }

    var incomeVals = items.map(function (r) {
      var cash = Number(r.cash || 0);
      var bank = Number(r.bank || 0);
      return Number(r.income || (cash + bank) || r.revenue || r.totalAmount || 0);
    });
    var expenseVals = items.map(function (r) {
      var other = Number(r.other || 0);
      return Math.abs(Number(r.expense || r.totalExpense || other || 0));
    });
    var labels = items.map(function (r) { return String(r.date || r.label || r.reportDate || '').slice(5); });
    var fullLabels = items.map(function (r) { return String(r.date || r.label || r.reportDate || '').replace(/^(\d{4})-(\d{2})-(\d{2})$/, '$3-$2-$1'); });
    var barRects = rptDrawBarChart(ctx, w, h, labels, [
      { values: incomeVals, color: '#3B82F6' },
      { values: expenseVals, color: '#EF4444' },
    ]);
    rptBindChartTooltip(canvas, barRects, fullLabels, ['Thu', 'Chi']);
  }

  function rptDrawBarChart(ctx, w, h, labels, series) {
    var padLeft = 80;
    var padBottom = 40;
    var padTop = 20;
    var padRight = 20;
    var chartW = w - padLeft - padRight;
    var chartH = h - padTop - padBottom;

    // Find max value across all series
    var maxVal = 0;
    for (var si = 0; si < series.length; si++) {
      for (var vi = 0; vi < series[si].values.length; vi++) {
        if (series[si].values[vi] > maxVal) maxVal = series[si].values[vi];
      }
    }
    if (maxVal === 0) maxVal = 1000000;

    // Nice round max
    var niceMax = rptNiceMax(maxVal);
    var gridLines = 6;
    var step = niceMax / gridLines;

    // Draw grid lines and Y labels
    ctx.strokeStyle = '#E5EAF3';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#64748B';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (var g = 0; g <= gridLines; g++) {
      var yVal = step * g;
      var y = padTop + chartH - (yVal / niceMax) * chartH;
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(w - padRight, y);
      ctx.stroke();
      ctx.fillText(rptFormatVND(yVal), padLeft - 8, y);
    }

    // Draw axes
    ctx.strokeStyle = '#CBD5E1';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padLeft, padTop);
    ctx.lineTo(padLeft, padTop + chartH);
    ctx.lineTo(w - padRight, padTop + chartH);
    ctx.stroke();

    // Draw bars
    var n = labels.length;
    var groupWidth = chartW / n;
    var barCount = series.length;
    var barPad = Math.max(groupWidth * 0.15, 2);
    var singleBarW = Math.max((groupWidth - barPad * 2) / barCount, 4);
    var hitRects = [];

    for (var bi = 0; bi < n; bi++) {
      var groupVals = [];
      var groupColors = [];
      for (var bs = 0; bs < barCount; bs++) {
        var val = series[bs].values[bi] || 0;
        groupVals.push(val);
        groupColors.push(series[bs].color);
        var barH = (val / niceMax) * chartH;
        var bx = padLeft + bi * groupWidth + barPad + bs * singleBarW;
        var by = padTop + chartH - barH;
        ctx.fillStyle = series[bs].color;
        ctx.fillRect(bx, by, Math.max(singleBarW - 1, 2), barH);
      }
      // Store hit rect for the entire group column
      hitRects.push({
        x: padLeft + bi * groupWidth,
        y: padTop,
        w: groupWidth,
        h: chartH,
        idx: bi,
        values: groupVals,
        colors: groupColors,
      });

      // X label
      ctx.fillStyle = '#64748B';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      var labelX = padLeft + bi * groupWidth + groupWidth / 2;
      // Rotate labels if many
      if (n > 15) {
        ctx.save();
        ctx.translate(labelX, padTop + chartH + 4);
        ctx.rotate(-Math.PI / 4);
        ctx.fillText(labels[bi], 0, 0);
        ctx.restore();
      } else {
        ctx.fillText(labels[bi], labelX, padTop + chartH + 6);
      }
    }
    return hitRects;
  }

  function rptNiceMax(value) {
    if (value <= 0) return 1000000;
    var magnitude = Math.pow(10, Math.floor(Math.log10(value)));
    var normalized = value / magnitude;
    var nice;
    if (normalized <= 1) nice = 1;
    else if (normalized <= 2) nice = 2;
    else if (normalized <= 5) nice = 5;
    else nice = 10;
    return nice * magnitude;
  }

  async function loadReportTabData() {
    var container = document.getElementById('reports-content');
    if (!container) return;

    var tabMeta = REPORT_TABS[APP.reports.tab];
    if (!tabMeta) return;

    APP.reports.loading = true;
    var rId = ++APP.reports.tableRequestId;

    container.innerHTML = '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải dữ liệu báo cáo...</span></div>';

    try {
      var query = toQueryString({
        dateFrom: APP.reports.dateFrom,
        dateTo: APP.reports.dateTo,
        companyId: getSelectedBranchId(),
        limit: 100,
        offset: 0,
      });
      var data = await api(tabMeta.endpoint + query);
      if (rId !== APP.reports.tableRequestId) return;
      APP.reports.rowsByTab[APP.reports.tab] = safeItems(data);
      APP.reports.loading = false;
      renderReportTable();
    } catch (err) {
      if (rId !== APP.reports.tableRequestId) return;
      APP.reports.loading = false;
      container.innerHTML = '<div class="tds-empty"><p>Không có dữ liệu cho kỳ lọc đã chọn.</p></div>';
    }
  }

  function renderReportTable() {
    var container = document.getElementById('reports-content');
    if (!container) return;
    var tabMeta = REPORT_TABS[APP.reports.tab];
    if (!tabMeta) return;

    var rows = APP.reports.rowsByTab[APP.reports.tab] || [];
    if (!rows.length) {
      container.innerHTML = '<div class="tds-empty"><p>Không có dữ liệu cho kỳ lọc đã chọn.</p></div>';
      return;
    }

    var headerHtml = tabMeta.columns.map(function (column) {
      return '<th>' + escapeHtml(column.label) + '</th>';
    }).join('');

    var bodyHtml = rows.map(function (item) {
      var rowCells = tabMeta.columns.map(function (column) {
        return '<td>' + renderTypedValue(item[column.key], column.type) + '</td>';
      }).join('');
      return '<tr>' + rowCells + '</tr>';
    }).join('');

    container.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table reports-table">' +
      '<thead><tr>' + headerHtml + '</tr></thead>' +
      '<tbody>' + bodyHtml + '</tbody>' +
      '</table>' +
      '</div>';
  }

  // ---------------------------------------------------------------------------
  // Sub-Report Pages (9 dedicated report pages)
  // ---------------------------------------------------------------------------

  /**
   * Generic sub-report page builder. Creates a page with:
   * - Title bar with branch filter
   * - Date range filter
   * - Data table (fetched from API) or empty state
   */
  function renderSubReportPage(options) {
    var el = document.getElementById('page-reports');
    if (!el) return;

    var title = options.title || 'Báo cáo';
    var endpoint = options.endpoint || '';
    var columns = options.columns || [];
    var stateKey = options.stateKey || 'sub';
    var dateMode = options.dateMode || 'range'; // 'range' or 'month'

    // Initialise sub-report state if needed
    if (!APP.reports[stateKey]) {
      APP.reports[stateKey] = {
        dateFrom: APP.reports.dateFrom || RANGE_START_ISO,
        dateTo: APP.reports.dateTo || TODAY_ISO,
        items: [],
        loading: false,
        requestId: 0,
      };
    }
    var st = APP.reports[stateKey];

    el.innerHTML =
      '<div class="rpt-shell rpt-sub-page">' +
      '<div class="rpt-page-header">' +
      '<h2>' + escapeHtml(title) + '</h2>' +
      '</div>' +

      // Filters bar
      '<div class="rpt-date-bar">' +
      '<div class="rpt-date-range">' +
      '<input class="tds-input tds-input-sm" id="subrpt-date-from" type="date" value="' + escapeHtml(st.dateFrom) + '">' +
      '<span class="rpt-date-sep">&ndash;</span>' +
      '<input class="tds-input tds-input-sm" id="subrpt-date-to" type="date" value="' + escapeHtml(st.dateTo) + '">' +
      '<button class="tds-btn tds-btn-sm tds-btn-primary" id="subrpt-apply"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg> Lọc</button>' +
      '</div>' +
      '</div>' +

      // Table container
      '<div class="rpt-sub-content" id="subrpt-table">' +
      renderLoadingState('Đang tải dữ liệu...') +
      '</div>' +
      '</div>';

    // Bind filter
    var applyBtn = document.getElementById('subrpt-apply');
    if (applyBtn) {
      applyBtn.addEventListener('click', function () {
        var f = document.getElementById('subrpt-date-from');
        var t = document.getElementById('subrpt-date-to');
        if (f && f.value) st.dateFrom = f.value;
        if (t && t.value) st.dateTo = t.value;
        loadSubReportData(endpoint, columns, st);
      });
    }

    // Initial load
    loadSubReportData(endpoint, columns, st);
  }

  async function loadSubReportData(endpoint, columns, st) {
    var container = document.getElementById('subrpt-table');
    if (!container) return;

    st.loading = true;
    var rId = ++st.requestId;
    container.innerHTML = renderLoadingState('Đang tải dữ liệu báo cáo...');

    try {
      var query = toQueryString({
        dateFrom: st.dateFrom,
        dateTo: st.dateTo,
        companyId: getSelectedBranchId(),
        limit: 200,
        offset: 0,
      });
      var data = await api(endpoint + query);
      if (rId !== st.requestId) return;
      st.items = safeItems(data);
      st.loading = false;
      renderSubReportTable(container, columns, st.items);
    } catch (err) {
      if (rId !== st.requestId) return;
      st.loading = false;
      // Guard against HTML error responses (e.g. 404 pages) leaking into the DOM
      var errMsg = (err && err.message) || '';
      if (errMsg.indexOf('<') !== -1 || errMsg.indexOf('<!') !== -1 || errMsg.length > 200) {
        errMsg = 'Không có dữ liệu';
      }
      container.innerHTML = renderEmptyState(errMsg || 'Không thể tải báo cáo');
    }
  }

  function renderSubReportTable(container, columns, rows) {
    if (!rows || !rows.length) {
      container.innerHTML = renderEmptyState('Không có dữ liệu');
      return;
    }

    var headerHtml = '<tr>' + columns.map(function (col) {
      return '<th>' + escapeHtml(col.label) + '</th>';
    }).join('') + '</tr>';

    var bodyHtml = rows.map(function (row) {
      var cells = columns.map(function (col) {
        return '<td>' + renderTypedValue(row[col.key], col.type) + '</td>';
      }).join('');
      return '<tr>' + cells + '</tr>';
    }).join('');

    container.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table reports-table">' +
      '<thead>' + headerHtml + '</thead>' +
      '<tbody>' + bodyHtml + '</tbody>' +
      '</table>' +
      '</div>';
  }

  // --- 1. Báo cáo ngày ---
  function renderReportDaily() {
    renderSubReportPage({
      title: 'Báo cáo ngày',
      endpoint: '/api/reports/daily',
      stateKey: 'rptDaily',
      columns: [
        { key: 'reportDate', label: 'Ngày', type: 'date' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
        { key: 'income', label: 'Thu', type: 'currency' },
        { key: 'expense', label: 'Chi', type: 'currency' },
        { key: 'balance', label: 'Tồn quỹ', type: 'currency' },
      ],
    });
  }

  // --- 2. Báo cáo doanh thu ---
  function renderReportRevenue() {
    renderSubReportPage({
      title: 'Báo cáo doanh thu',
      endpoint: '/api/reports/revenue-trend', // Fixed: was /api/reports/services (same as services report)
      stateKey: 'rptRevenue',
      columns: [
        { key: 'reportDate', label: 'Ngày', type: 'date' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
        { key: 'income', label: 'Thu', type: 'currency' },
        { key: 'expense', label: 'Chi', type: 'currency' },
      ],
    });
  }

  // --- 3. Báo cáo dịch vụ ---
  function renderReportServices() {
    renderSubReportPage({
      title: 'Báo cáo dịch vụ',
      endpoint: '/api/reports/services',
      stateKey: 'rptServices',
      columns: [
        { key: 'serviceName', label: 'Dịch vụ', type: 'text' },
        { key: 'quantity', label: 'Số lượng', type: 'number' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
      ],
    });
  }

  // --- 4. Báo cáo khách hàng ---
  function renderReportCustomers() {
    renderSubReportPage({
      title: 'Báo cáo khách hàng',
      endpoint: '/api/reports/customers',
      stateKey: 'rptCustomers',
      columns: [
        { key: 'customerName', label: 'Khách hàng', type: 'text' },
        { key: 'paymentCount', label: 'Số lần khám', type: 'number' },
        { key: 'totalAmount', label: 'Tổng chi tiêu', type: 'currency' },
      ],
    });
  }

  // --- 5. Báo cáo tiếp nhận ---
  function renderReportReception() {
    renderSubReportPage({
      title: 'Báo cáo tiếp nhận',
      endpoint: '/api/reports/reception',
      stateKey: 'rptReception',
      columns: [
        { key: 'hour', label: 'Giờ', type: 'text' },
        { key: 'count', label: 'Tổng tiếp nhận', type: 'number' },
        { key: 'newCount', label: 'Mới', type: 'number' },
        { key: 'returnCount', label: 'Tái khám', type: 'number' },
      ],
    });
  }

  // --- 6. Công nợ NCC ---
  function renderReportSupplierDebt() {
    renderSubReportPage({
      title: 'Công nợ NCC',
      endpoint: '/api/reports/supplier-debt',
      stateKey: 'rptSupplierDebt',
      columns: [
        { key: 'supplierName', label: 'NCC', type: 'text' },
        { key: 'openingDebt', label: 'Nợ đầu kỳ', type: 'currency' },
        { key: 'incurred', label: 'Phát sinh', type: 'currency' },
        { key: 'paid', label: 'Đã trả', type: 'currency' },
        { key: 'closingDebt', label: 'Nợ cuối kỳ', type: 'currency' },
      ],
    });
  }

  // --- 7. Báo cáo lịch hẹn ---
  function renderReportAppointments() {
    renderSubReportPage({
      title: 'Báo cáo lịch hẹn',
      endpoint: '/api/reports/appointments',
      stateKey: 'rptAppointments',
      columns: [
        { key: 'state', label: 'Trạng thái', type: 'text' },
        { key: 'count', label: 'Tổng hẹn', type: 'number' },
      ],
    });
  }

  // --- 8. Báo cáo công việc ---
  function renderReportTasks() {
    renderSubReportPage({
      title: 'Báo cáo công việc',
      endpoint: '/api/reports/staff', // No /api/reports/tasks endpoint exists; using staff data grouped by employee
      stateKey: 'rptTasks',
      columns: [
        { key: 'staffName', label: 'Nhân viên', type: 'text' },
        { key: 'orderCount', label: 'Tổng CV', type: 'number' },
        { key: 'totalAmount', label: 'Doanh thu', type: 'currency' },
      ],
    });
  }

  // --- 9. Công nợ bảo hiểm ---
  function renderReportInsurance() {
    renderSubReportPage({
      title: 'Công nợ bảo hiểm',
      endpoint: '/api/reports/insurance-debt',
      stateKey: 'rptInsurance',
      columns: [
        { key: 'insuranceName', label: 'Bảo hiểm', type: 'text' },
        { key: 'openingDebt', label: 'Nợ đầu kỳ', type: 'currency' },
        { key: 'incurred', label: 'Phát sinh', type: 'currency' },
        { key: 'collected', label: 'Đã thu', type: 'currency' },
        { key: 'closingDebt', label: 'Nợ cuối kỳ', type: 'currency' },
      ],
    });
  }


  // ---------------------------------------------------------------------------
  // 12 Category Pages — Dedicated Render Functions
  // ---------------------------------------------------------------------------

  function catProductGroupKey(group) {
    if (!group) return '';
    return String(group.id || group.name || '');
  }

  function catProductGroupName(group) {
    if (!group) return '';
    return String(group.name || group.displayName || group.id || '');
  }

  function catProductMatchesTab(item, tab) {
    var type = String(item.type2 || item.type || '').toLowerCase();
    if (!type) return tab === 'services';
    if (tab === 'services') return type.indexOf('service') >= 0;
    if (tab === 'materials') {
      return type.indexOf('product') >= 0 || type.indexOf('consu') >= 0 || type.indexOf('stock') >= 0 || type.indexOf('material') >= 0;
    }
    if (tab === 'medicine') {
      return type.indexOf('medicine') >= 0 || type.indexOf('drug') >= 0 || type.indexOf('pharma') >= 0;
    }
    return true;
  }

  async function loadCatProductsData(forceReload) {
    var st = APP.catProducts;
    if (st.loading) return;
    if (!forceReload && st.loaded) return;

    st.loading = true;
    st.requestId += 1;
    var requestId = st.requestId;
    renderCatProducts();

    try {
      var branchId = getSelectedBranchId();
      var responses = await Promise.all([
        api('/api/products' + toQueryString({
          limit: 0,
          offset: 0,
          companyId: branchId,
        })),
        api('/api/categories/products'),
      ]);
      if (requestId !== st.requestId) return;

      st.items = safeItems(responses[0]);
      st.groups = safeItems(responses[1]);
      st.loaded = true;
      st.companyId = branchId || '';
      st.total = st.items.length;
      st.loading = false;
      renderCatProducts();
    } catch (err) {
      if (requestId !== st.requestId) return;
      st.loading = false;
      st.loaded = false;
      var el = document.getElementById('page-categories');
      if (el) {
        el.innerHTML = renderEmptyState((err && err.message) || 'Không thể tải dữ liệu danh mục sản phẩm');
      }
    }
  }

  // ---- Products page (#/products) — Split-panel layout ----
  function renderCatProducts() {
    var el = document.getElementById('page-categories');
    if (!el) return;

    var st = APP.catProducts;
    var currentCompanyId = getSelectedBranchId() || '';
    if (st.loaded && st.companyId !== currentCompanyId) {
      st.loaded = false;
    }
    if (st.loading) {
      el.innerHTML = '<div class="tds-card categories-shell">' + renderLoadingState('Đang tải thông tin sản phẩm...') + '</div>';
      return;
    }

    if (!st.loaded) {
      loadCatProductsData();
      el.innerHTML = '<div class="tds-card categories-shell">' + renderLoadingState('Đang tải thông tin sản phẩm...') + '</div>';
      return;
    }

    var allGroups = Array.isArray(st.groups) ? st.groups.slice() : [];
    var filteredGroups = allGroups.filter(function (g) {
      var groupName = catProductGroupName(g);
      if (!st.groupSearch) return true;
      return groupName.toLowerCase().indexOf(st.groupSearch.toLowerCase()) >= 0;
    });

    var selectedGroupObj = null;
    for (var gIdx = 0; gIdx < allGroups.length; gIdx++) {
      if (catProductGroupKey(allGroups[gIdx]) === st.selectedGroup) {
        selectedGroupObj = allGroups[gIdx];
        break;
      }
    }
    var selectedGroupName = catProductGroupName(selectedGroupObj);

    var filteredItems = (Array.isArray(st.items) ? st.items : []).filter(function (item) {
      if (!catProductMatchesTab(item, st.tab)) return false;
      if (st.selectedGroup) {
        var itemGroupId = String(item.categoryId || '');
        var itemGroupName = String(item.categoryName || '');
        if (itemGroupId !== st.selectedGroup && itemGroupName !== selectedGroupName) return false;
      }
      if (st.statusFilter === 'active' && !item.active) return false;
      if (st.statusFilter === 'inactive' && !!item.active) return false;
      if (st.rightSearch) {
        var q = st.rightSearch.toLowerCase();
        var name = String(item.name || '').toLowerCase();
        var code = String(item.defaultCode || '').toLowerCase();
        var display = String(item.displayName || '').toLowerCase();
        if (name.indexOf(q) < 0 && code.indexOf(q) < 0 && display.indexOf(q) < 0) return false;
      }
      return true;
    });

    var total = filteredItems.length;
    var startIdx = (st.page - 1) * st.pageSize;
    var pageItems = filteredItems.slice(startIdx, startIdx + st.pageSize);
    var totalPages = Math.max(1, Math.ceil(total / st.pageSize));

    el.innerHTML =
      '<div style="padding:16px 16px 0">' +
        '<h2 style="margin:0 0 12px;font-size:18px;font-weight:600">Thông tin sản phẩm</h2>' +
      '</div>' +
      '<div class="catalog-split">' +
        '<div class="catalog-left">' +
          '<div class="catalog-left-header">Nhóm dịch vụ</div>' +
          '<div class="catalog-left-search">' +
            '<input type="text" id="cat-group-search" placeholder="Tìm kiếm nhóm dịch vụ" value="' + escapeHtml(st.groupSearch) + '">' +
          '</div>' +
          '<div class="catalog-left-header" style="font-size:12px;color:#94a3b8;padding:10px 16px 6px;border-bottom:none">Tên nhóm dịch vụ</div>' +
          '<ul class="catalog-group-list">' +
            filteredGroups.map(function (group) {
              var key = catProductGroupKey(group);
              var name = catProductGroupName(group);
              var activeClass = st.selectedGroup === key ? ' active' : '';
              return '<li class="catalog-group-item' + activeClass + '" data-group="' + escapeHtml(key) + '">' + escapeHtml(name) + '</li>';
            }).join('') +
          '</ul>' +
        '</div>' +
        '<div class="catalog-right">' +
          '<div class="catalog-right-header">' +
            '<div class="catalog-right-tabs">' +
              '<button class="cat-tab' + (st.tab === 'services' ? ' active' : '') + '" data-tab="services">Dịch vụ</button>' +
              '<button class="cat-tab' + (st.tab === 'materials' ? ' active' : '') + '" data-tab="materials">Vật tư</button>' +
              '<button class="cat-tab' + (st.tab === 'medicine' ? ' active' : '') + '" data-tab="medicine">Thuốc</button>' +
            '</div>' +
            '<div class="catalog-right-toolbar">' +
              '<button class="tds-btn tds-btn-primary tds-btn-sm" id="cat-products-add"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Thêm mới</button>' +
              '<select class="catalog-filter-select" id="cat-products-filter">' +
                '<option value="active"' + (st.statusFilter === 'active' ? ' selected' : '') + '>Đang sử dụng</option>' +
                '<option value="inactive"' + (st.statusFilter === 'inactive' ? ' selected' : '') + '>Ngưng sử dụng</option>' +
                '<option value="all"' + (st.statusFilter === 'all' ? ' selected' : '') + '>Tất cả</option>' +
              '</select>' +
              '<input class="catalog-search-input" id="cat-products-search" placeholder="Tìm kiếm theo mã hoặc tên" value="' + escapeHtml(st.rightSearch) + '">' +
              '<button class="catalog-more-btn" title="Thêm thao tác">&#8943;</button>' +
            '</div>' +
          '</div>' +
          '<div class="catalog-right-content">' +
            '<table class="tds-table">' +
              '<thead><tr>' +
                '<th><input type="checkbox"></th>' +
                '<th>Tên dịch vụ</th>' +
                '<th>Thao tác</th>' +
              '</tr></thead>' +
              '<tbody>' +
                (pageItems.length ? pageItems.map(function (item) {
                  var itemName = item.name || item.displayName || 'N/A';
                  var itemCode = item.defaultCode || item.code || '—';
                  return '<tr>' +
                    '<td><input type="checkbox"></td>' +
                    '<td><div style="font-weight:500">' + escapeHtml(itemName) + '</div><div style="font-size:12px;color:#94a3b8">' + escapeHtml(itemCode) + '</div></td>' +
                    '<td><div class="catalog-action-icons">' +
                      '<button class="cat-action-edit" title="Sửa" data-product-id="' + escapeHtml(item.id || '') + '"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>' +
                      '<button class="cat-action-delete" title="Xóa" data-product-id="' + escapeHtml(item.id || '') + '"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>' +
                      '<button class="cat-action-view" title="Ẩn/Hiện" data-product-id="' + escapeHtml(item.id || '') + '"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.9 10.9 0 0 1 12 20C7 20 2.73 16.89 1 12c.74-2.07 2-3.88 3.6-5.27"/><path d="M10.58 10.58A2 2 0 0 0 12 14a2 2 0 0 0 1.42-.58"/><path d="M9.88 5.09A10.94 10.94 0 0 1 12 4c5 0 9.27 3.11 11 8a10.93 10.93 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg></button>' +
                    '</div></td>' +
                  '</tr>';
                }).join('') : '<tr><td colspan="3" style="text-align:center;padding:40px;color:#94a3b8">Chưa có dữ liệu</td></tr>') +
              '</tbody>' +
            '</table>' +
          '</div>' +
          '<div class="catalog-right-footer">' +
            '<div class="catalog-footer-left">' +
              '<div class="catalog-pagination">' +
                renderCatPagination(st.page, totalPages) +
              '</div>' +
              '<select class="catalog-filter-select" id="cat-products-pagesize">' +
                '<option value="20"' + (st.pageSize === 20 ? ' selected' : '') + '>20</option>' +
                '<option value="50"' + (st.pageSize === 50 ? ' selected' : '') + '>50</option>' +
                '<option value="100"' + (st.pageSize === 100 ? ' selected' : '') + '>100</option>' +
              '</select>' +
              '<span>hàng trên trang</span>' +
            '</div>' +
            '<div class="catalog-footer-right">' +
              (total > 0 ? ((startIdx + 1) + '-' + Math.min(startIdx + st.pageSize, total) + ' của ' + total + ' dòng') : '0 dòng') +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>';

    // Event: group search
    var groupSearchInput = document.getElementById('cat-group-search');
    if (groupSearchInput) {
      groupSearchInput.addEventListener('input', debounce(function () {
        APP.catProducts.groupSearch = groupSearchInput.value.trim();
        renderCatProducts();
      }, 200));
    }

    // Event: group click
    var groupItems = el.querySelectorAll('.catalog-group-item[data-group]');
    for (var i = 0; i < groupItems.length; i++) {
      groupItems[i].addEventListener('click', function () {
        var g = this.getAttribute('data-group');
        APP.catProducts.selectedGroup = (APP.catProducts.selectedGroup === g) ? null : g;
        APP.catProducts.page = 1;
        renderCatProducts();
      });
    }

    // Event: tabs
    var tabBtns = el.querySelectorAll('.cat-tab');
    for (var t = 0; t < tabBtns.length; t++) {
      tabBtns[t].addEventListener('click', function () {
        APP.catProducts.tab = this.getAttribute('data-tab');
        APP.catProducts.page = 1;
        renderCatProducts();
      });
    }

    // Event: right search
    var rightSearchInput = document.getElementById('cat-products-search');
    if (rightSearchInput) {
      rightSearchInput.addEventListener('input', debounce(function () {
        APP.catProducts.rightSearch = rightSearchInput.value.trim();
        APP.catProducts.page = 1;
        renderCatProducts();
      }, 200));
    }

    // Event: status filter
    var filterSelect = document.getElementById('cat-products-filter');
    if (filterSelect) {
      filterSelect.addEventListener('change', function () {
        APP.catProducts.statusFilter = filterSelect.value;
        APP.catProducts.page = 1;
        renderCatProducts();
      });
    }

    // Event: add button
    var addBtn = document.getElementById('cat-products-add');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        showToast('info', 'Sản phẩm/Dịch vụ được quản lý từ hệ thống TDental gốc');
      });
    }

    // Event: pagination
    var pagBtns = el.querySelectorAll('.catalog-pagination button[data-page]');
    for (var p = 0; p < pagBtns.length; p++) {
      pagBtns[p].addEventListener('click', function () {
        var pg = parseInt(this.getAttribute('data-page'), 10);
        if (pg >= 1 && pg <= totalPages) {
          APP.catProducts.page = pg;
          renderCatProducts();
        }
      });
    }

    var pageSizeSelect = document.getElementById('cat-products-pagesize');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', function () {
        APP.catProducts.pageSize = parseInt(this.value, 10) || 20;
        APP.catProducts.page = 1;
        renderCatProducts();
      });
    }

    var productActionBtns = el.querySelectorAll('.cat-action-edit, .cat-action-delete, .cat-action-view');
    for (var a = 0; a < productActionBtns.length; a++) {
      productActionBtns[a].addEventListener('click', function () {
        showToast('info', 'Sản phẩm/Dịch vụ được quản lý từ hệ thống TDental gốc');
      });
    }
  }

  function renderCatPagination(currentPage, totalPages) {
    if (totalPages <= 1) return '<button class="active" data-page="1">1</button>';
    var buttons = [];
    var start = Math.max(1, currentPage - 2);
    var end = Math.min(totalPages, currentPage + 2);
    if (currentPage > 1) {
      buttons.push('<button data-page="' + (currentPage - 1) + '">&lsaquo;</button>');
    }
    for (var i = start; i <= end; i++) {
      buttons.push('<button data-page="' + i + '"' + (i === currentPage ? ' class="active"' : '') + '>' + i + '</button>');
    }
    if (end < totalPages) {
      buttons.push('<span style="padding:0 4px">...</span>');
      buttons.push('<button data-page="' + totalPages + '">' + totalPages + '</button>');
    }
    if (currentPage < totalPages) {
      buttons.push('<button data-page="' + (currentPage + 1) + '">&rsaquo;</button>');
    }
    return buttons.join('');
  }

  // ---- Generic helper: render category pages with DB-backed data ----
  function initCatSimpleState(pageKey) {
    APP.catPage.search = '';
    APP.catPage.items = [];
    APP.catPage.loading = false;
    APP.catPage.requestId = 0;
    APP.catPage.page = 1;
    APP.catPage.pageSize = 20;
    APP.catPage.total = 0;
    APP.catPage.activeKey = pageKey || '';
  }

  function catSimpleActiveBadge(active) {
    return active
      ? '<span class="tds-badge tds-badge-success">Đang dùng</span>'
      : '<span class="tds-badge tds-badge-gray">Ẩn</span>';
  }

  function catSimpleUpdated(value) {
    return value ? formatDateTime(value) : '—';
  }

  function mapManageCategoryRow(item) {
    return [
      item.name || '—',
      item.code || '—',
      item.type || '—',
      catSimpleActiveBadge(!!item.active),
      catSimpleUpdated(item.updatedAt),
      '',
    ];
  }

  function openCatSimpleDataPage(opts) {
    initCatSimpleState(opts.key || opts.title || '');
    renderCatSimplePage(opts);
  }

  function renderCatSimplePage(opts) {
    var el = document.getElementById('page-categories');
    if (!el) return;

    var search = APP.catPage.search || '';

    el.innerHTML =
      '<div class="tds-card categories-shell">' +
        '<div class="cat-page-header">' +
          '<h2>' + escapeHtml(opts.title) + '</h2>' +
          '<div class="cat-page-toolbar">' +
            '<input class="tds-search-input" id="cat-simple-search" placeholder="Tìm kiếm..." value="' + escapeHtml(search) + '">' +
            '<button class="tds-btn tds-btn-primary" id="cat-simple-add"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-2px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Thêm mới</button>' +
          '</div>' +
        '</div>' +
        '<div id="cat-simple-content"><div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải dữ liệu...</span></div></div>' +
      '</div>';

    var searchInput = document.getElementById('cat-simple-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.catPage.search = searchInput.value.trim();
        APP.catPage.page = 1;
        loadCatSimpleData(opts);
      }, 250));
    }

    var addBtn = document.getElementById('cat-simple-add');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        if (opts && opts.manageKind) {
          openCatSimpleModal(opts, null);
        } else if (opts && typeof opts.onAdd === 'function') {
          opts.onAdd(opts);
        } else if (opts && (opts.endpoint || opts.loader)) {
          openCatSimpleGenericModal(opts, null);
        } else {
          showToast('info', 'Chức năng thêm mới cho trang này đang phát triển');
        }
      });
    }

    loadCatSimpleData(opts);
  }

  async function loadCatSimpleData(opts) {
    var content = document.getElementById('cat-simple-content');
    if (!content) return;

    APP.catPage.loading = true;
    APP.catPage.requestId += 1;
    var requestId = APP.catPage.requestId;
    var activeKey = APP.catPage.activeKey;
    content.innerHTML = '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải dữ liệu...</span></div>';

    var params = {
      search: APP.catPage.search || '',
      limit: APP.catPage.pageSize || 20,
      offset: Math.max(0, ((APP.catPage.page || 1) - 1) * (APP.catPage.pageSize || 20)),
      companyId: getSelectedBranchId(),
    };

    try {
      var data = await fetchCatSimpleRows(opts, params);
      if (requestId !== APP.catPage.requestId || activeKey !== APP.catPage.activeKey) return;

      APP.catPage.items = data.rows || [];
      APP.catPage._rawItems = data.rawItems || [];
      APP.catPage.total = typeof data.total === 'number' ? data.total : APP.catPage.items.length;

      var maxPage = Math.max(1, Math.ceil((APP.catPage.total || 0) / (APP.catPage.pageSize || 20)));
      if (APP.catPage.page > maxPage) {
        APP.catPage.page = maxPage;
        loadCatSimpleData(opts);
        return;
      }

      APP.catPage.loading = false;
      content.innerHTML = renderCatSimpleTableHtml(opts);
      bindCatSimpleEvents(elOrNull('page-categories'), opts);
    } catch (err) {
      if (requestId !== APP.catPage.requestId || activeKey !== APP.catPage.activeKey) return;
      APP.catPage.loading = false;
      content.innerHTML = '<div class="tds-empty"><p>' + escapeHtml((err && err.message) || 'Không thể tải dữ liệu') + '</p></div>';
    }
  }

  async function fetchCatSimpleRows(opts, params) {
    if (opts && typeof opts.loader === 'function') {
      var custom = await opts.loader(params);
      if (custom && Array.isArray(custom.rows)) {
        return { rows: custom.rows, total: typeof custom.total === 'number' ? custom.total : custom.rows.length };
      }
      if (Array.isArray(custom)) return { rows: custom, total: custom.length };
      return { rows: [], total: 0 };
    }

    var queryBase = {
      search: params.search,
      limit: params.limit,
      offset: params.offset,
    };

    if (opts && opts.useCompany) {
      queryBase.companyId = params.companyId;
    }
    if (opts && typeof opts.extraQuery === 'function') {
      var ext = opts.extraQuery(params) || {};
      Object.assign(queryBase, ext);
    } else if (opts && opts.extraQuery) {
      Object.assign(queryBase, opts.extraQuery);
    }

    var endpoint = '';
    if (opts && opts.manageKind) {
      endpoint = '/api/categories/manage/' + encodeURIComponent(opts.manageKind) + toQueryString(queryBase);
    } else if (opts && opts.endpoint) {
      endpoint = opts.endpoint + toQueryString(queryBase);
    } else {
      return { rows: [], total: 0 };
    }

    var data = await api(endpoint);
    var items = safeItems(data);
    var rowMapper = (opts && typeof opts.mapItem === 'function') ? opts.mapItem : mapManageCategoryRow;
    var rows = items.map(function (item) { return rowMapper(item || {}); });
    var total = (data && typeof data.totalItems === 'number') ? data.totalItems : rows.length;
    return { rows: rows, total: total, rawItems: items };
  }

  function renderCatSimpleTableHtml(opts) {
    var rows = APP.catPage.items || [];
    if (!rows.length) {
      return '<div class="tds-empty"><p>Chưa có dữ liệu trong cơ sở dữ liệu.</p></div>';
    }

    var total = APP.catPage.total || rows.length;
    var pageSize = APP.catPage.pageSize || 20;
    var currentPage = APP.catPage.page || 1;
    var totalPages = Math.max(1, Math.ceil(total / pageSize));
    var start = total ? ((currentPage - 1) * pageSize + 1) : 0;
    var end = total ? Math.min(currentPage * pageSize, total) : 0;

    return (
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr>' + opts.columns.map(function (col) { return '<th>' + escapeHtml(col) + '</th>'; }).join('') + '</tr></thead>' +
      '<tbody>' + rows.map(function (row, rowIdx) {
        return '<tr>' + row.map(function (cell, cellIdx) {
          if (cellIdx === row.length - 1 && opts.hasActions) {
            return '<td><div class="catalog-action-icons">' +
              '<button class="cat-action-edit" data-row="' + rowIdx + '" title="Sửa"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>' +
              '<button class="cat-action-delete" data-row="' + rowIdx + '" title="Xóa"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>' +
            '</div></td>';
          }
          if (typeof cell === 'string' && cell.indexOf('<') === 0) {
            return '<td>' + cell + '</td>';
          }
          return '<td>' + escapeHtml(String(cell == null ? '—' : cell)) + '</td>';
        }).join('') + '</tr>';
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>' +
      '<div class="catalog-right-footer">' +
        '<div class="catalog-footer-left">' +
          '<div class="catalog-pagination">' + renderCatPagination(currentPage, totalPages) + '</div>' +
          '<select class="catalog-filter-select" id="cat-simple-pagesize">' +
            '<option value="20"' + (pageSize === 20 ? ' selected' : '') + '>20</option>' +
            '<option value="50"' + (pageSize === 50 ? ' selected' : '') + '>50</option>' +
            '<option value="100"' + (pageSize === 100 ? ' selected' : '') + '>100</option>' +
          '</select>' +
          '<span>hàng trên trang</span>' +
        '</div>' +
        '<div class="catalog-footer-right">' + start + '-' + end + ' của ' + total + ' dòng</div>' +
      '</div>'
    );
  }

  function bindCatSimpleEvents(el, opts) {
    if (!el) return;

    var pagBtns = el.querySelectorAll('.catalog-pagination button[data-page]');
    for (var p = 0; p < pagBtns.length; p++) {
      pagBtns[p].addEventListener('click', function () {
        var pg = parseInt(this.getAttribute('data-page'), 10);
        var totalPages = Math.max(1, Math.ceil((APP.catPage.total || 0) / (APP.catPage.pageSize || 20)));
        if (pg >= 1 && pg <= totalPages) {
          APP.catPage.page = pg;
          loadCatSimpleData(opts);
        }
      });
    }

    var pageSizeSelect = document.getElementById('cat-simple-pagesize');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', function () {
        APP.catPage.pageSize = parseInt(this.value, 10) || 20;
        APP.catPage.page = 1;
        loadCatSimpleData(opts);
      });
    }

    var editBtns = el.querySelectorAll('.cat-action-edit');
    for (var i = 0; i < editBtns.length; i++) {
      editBtns[i].addEventListener('click', function () {
        var rowIdx = parseInt(this.getAttribute('data-row'), 10);
        var rawItems = APP.catPage._rawItems || [];
        var item = rawItems[rowIdx];
        if (opts && opts.manageKind && item) {
          openCatSimpleModal(opts, item);
        } else if (opts && typeof opts.onEdit === 'function' && item) {
          opts.onEdit(opts, item);
        } else if (item && (opts.endpoint || opts.loader)) {
          openCatSimpleGenericModal(opts, item);
        } else {
          showToast('info', 'Chức năng sửa cho trang này đang phát triển');
        }
      });
    }
    var delBtns = el.querySelectorAll('.cat-action-delete');
    for (var j = 0; j < delBtns.length; j++) {
      delBtns[j].addEventListener('click', function () {
        var rowIdx = parseInt(this.getAttribute('data-row'), 10);
        var rawItems = APP.catPage._rawItems || [];
        var item = rawItems[rowIdx];
        if (opts && opts.manageKind && item && item.id) {
          deleteCatSimpleItem(opts, item.id);
        } else if (opts && typeof opts.onDelete === 'function' && item) {
          opts.onDelete(opts, item);
        } else if (item && item.id && opts.endpoint) {
          deleteCatSimpleGenericItem(opts, item.id);
        } else {
          showToast('info', 'Chức năng xóa cho trang này đang phát triển');
        }
      });
    }
  }

  function openCatSimpleModal(opts, item) {
    var editing = !!item;
    var content =
      '<form id="cat-simple-form">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tên</label>' +
      '<input class="tds-input" id="cat-simple-modal-name" required value="' + escapeHtml((item && item.name) || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Mã</label>' +
      '<input class="tds-input" id="cat-simple-modal-code" value="' + escapeHtml((item && item.code) || '') + '">' +
      '</div>' +
      '<label class="tds-checkbox-label">' +
      '<input type="checkbox" id="cat-simple-modal-active" ' + ((item ? !!item.active : true) ? 'checked' : '') + '>' +
      '<span>Kích hoạt</span>' +
      '</label>' +
      '</form>';

    showModal(editing ? 'Cập nhật' : 'Thêm mới', content, {
      footer:
        '<button class="tds-btn tds-btn-ghost" id="cat-simple-modal-cancel">Hủy</button>' +
        '<button class="tds-btn tds-btn-primary" id="cat-simple-modal-save">' + (editing ? 'Cập nhật' : 'Thêm mới') + '</button>',
      onOpen: function () {
        var cancelBtn = document.getElementById('cat-simple-modal-cancel');
        var saveBtn = document.getElementById('cat-simple-modal-save');
        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
        if (saveBtn) {
          saveBtn.addEventListener('click', async function () {
            var payload = {
              name: getInputValue('cat-simple-modal-name'),
              code: getInputValue('cat-simple-modal-code') || null,
              active: !!(document.getElementById('cat-simple-modal-active') || {}).checked,
              companyId: (opts && opts.useCompany) ? (getSelectedBranchId() || null) : null,
            };
            if (!payload.name) {
              showToast('warning', 'Tên là bắt buộc');
              return;
            }
            try {
              var kind = opts.manageKind;
              if (editing && item && item.id) {
                await api('/api/categories/manage/' + encodeURIComponent(kind) + '/' + encodeURIComponent(item.id), {
                  method: 'PUT',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Cập nhật thành công');
              } else {
                await api('/api/categories/manage/' + encodeURIComponent(kind), {
                  method: 'POST',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Tạo mới thành công');
              }
              closeModal();
              loadCatSimpleData(opts);
            } catch (err) {
              showToast('error', (err && err.message) || 'Không thể lưu');
            }
          });
        }
      },
    });
  }

  async function deleteCatSimpleItem(opts, itemId) {
    var ok = await tdsConfirm('Xóa mục này?', { title: 'Xóa mục' });
    if (!ok) return;
    try {
      await api('/api/categories/manage/' + encodeURIComponent(opts.manageKind) + '/' + encodeURIComponent(itemId), {
        method: 'DELETE',
      });
      showToast('success', 'Đã xóa thành công');
      loadCatSimpleData(opts);
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể xóa');
    }
  }

  // Generic modal for catalog pages that use endpoint/loader instead of manageKind
  function openCatSimpleGenericModal(opts, item) {
    var editing = !!item;
    var content =
      '<form id="cat-generic-form">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tên</label>' +
      '<input class="tds-input" id="cat-generic-name" required value="' + escapeHtml((item && (item.name || item.displayName)) || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Mã</label>' +
      '<input class="tds-input" id="cat-generic-code" value="' + escapeHtml((item && (item.code || item.defaultCode)) || '') + '">' +
      '</div>' +
      '<label class="tds-checkbox-label">' +
      '<input type="checkbox" id="cat-generic-active" ' + ((item ? !!item.active : true) ? 'checked' : '') + '>' +
      '<span>Kích hoạt</span>' +
      '</label>' +
      '</form>';

    showModal(editing ? 'Cập nhật' : 'Thêm mới', content, {
      footer:
        '<button class="tds-btn tds-btn-ghost" id="cat-generic-cancel">Hủy</button>' +
        '<button class="tds-btn tds-btn-primary" id="cat-generic-save">' + (editing ? 'Cập nhật' : 'Thêm mới') + '</button>',
      onOpen: function () {
        var cancelBtn = document.getElementById('cat-generic-cancel');
        var saveBtn = document.getElementById('cat-generic-save');
        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
        if (saveBtn) {
          saveBtn.addEventListener('click', async function () {
            var payload = {
              name: getInputValue('cat-generic-name'),
              code: getInputValue('cat-generic-code') || null,
              active: !!(document.getElementById('cat-generic-active') || {}).checked,
              companyId: (opts && opts.useCompany) ? (getSelectedBranchId() || null) : null,
            };
            if (!payload.name) {
              showToast('warning', 'Tên là bắt buộc');
              return;
            }
            try {
              var endpoint = opts.endpoint;
              if (!endpoint) { showToast('info', 'Không có endpoint để lưu'); return; }
              if (editing && item && item.id) {
                await api(endpoint + '/' + encodeURIComponent(item.id), {
                  method: 'PUT',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Cập nhật thành công');
              } else {
                await api(endpoint, {
                  method: 'POST',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Tạo mới thành công');
              }
              closeModal();
              loadCatSimpleData(opts);
            } catch (err) {
              showToast('error', (err && err.message) || 'Không thể lưu');
            }
          });
        }
      },
    });
  }

  async function deleteCatSimpleGenericItem(opts, itemId) {
    var ok = await tdsConfirm('Xóa mục này?', { title: 'Xóa mục' });
    if (!ok) return;
    try {
      var endpoint = opts.endpoint;
      if (!endpoint) { showToast('info', 'Không có endpoint để xóa'); return; }
      await api(endpoint + '/' + encodeURIComponent(itemId), {
        method: 'DELETE',
      });
      showToast('success', 'Đã xóa thành công');
      loadCatSimpleData(opts);
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể xóa');
    }
  }

  function elOrNull(id) {
    return document.getElementById(id) || null;
  }

  // ---- #/categories — Thông tin KH ----
  function renderCatCustomerInfo() {
    openCatSimpleDataPage({
      key: 'cat-customer-info',
      title: 'Thông tin khách hàng',
      columns: ['Tên trường', 'Mã', 'Loại', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      manageKind: 'customer-labels',
      mapItem: mapManageCategoryRow,
      useCompany: true,
    });
  }

  // ---- #/customer-stage — Trạng thái KH ----
  function renderCatCustomerStage() {
    openCatSimpleDataPage({
      key: 'cat-customer-stage',
      title: 'Trạng thái khách hàng',
      columns: ['Tên trạng thái', 'Mã', 'Loại', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      manageKind: 'customer-stages',
      mapItem: mapManageCategoryRow,
      useCompany: true,
    });
  }

  // ---- #/partner-catalog — Đối tác ----
  function renderCatPartners() {
    openCatSimpleDataPage({
      key: 'cat-partners',
      title: 'Đối tác',
      columns: ['Tên', 'Mã', 'Loại', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      manageKind: 'suppliers',
      mapItem: mapManageCategoryRow,
      useCompany: true,
    });
  }

  // ---- #/prescriptions — Đơn thuốc mẫu ----
  function renderCatPrescriptions() {
    openCatSimpleDataPage({
      key: 'cat-prescriptions',
      title: 'Đơn thuốc mẫu',
      columns: ['Tên đơn', 'Mã', 'Loại', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      manageKind: 'prescriptions',
      mapItem: mapManageCategoryRow,
      useCompany: true,
    });
  }

  // ---- #/price-list — Bảng giá ----
  function renderCatPriceList() {
    openCatSimpleDataPage({
      key: 'cat-price-list',
      title: 'Bảng giá',
      columns: ['Dịch vụ/Vật tư', 'Mã', 'Giá niêm yết', 'Giá vốn', 'Trạng thái', 'Thao tác'],
      hasActions: true,
      endpoint: '/api/products',
      useCompany: false,
      mapItem: function (item) {
        return [
          item.name || item.displayName || '—',
          item.defaultCode || item.code || '—',
          formatCurrency(item.listPrice || 0),
          formatCurrency(item.standardPrice || 0),
          catSimpleActiveBadge(!!item.active),
          '',
        ];
      },
    });
  }

  // ---- #/commission-table — Bảng hoa hồng ----
  function renderCatCommissionTable() {
    openCatSimpleDataPage({
      key: 'cat-commission-table',
      title: 'Bảng hoa hồng',
      columns: ['Tên cấu hình', 'Loại', 'Chi nhánh', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      useCompany: false,
      loader: async function (params) {
        var query = toQueryString({
          search: params.search,
          limit: params.limit,
          offset: params.offset,
        });
        var commissionData = await api('/api/commissions' + query);
        var commissions = safeItems(commissionData);
        var total = (commissionData && typeof commissionData.totalItems === 'number')
          ? commissionData.totalItems
          : commissions.length;

        var companyMap = {};
        try {
          var companiesData = await api('/api/companies?limit=0&offset=0');
          var companies = safeItems(companiesData);
          for (var i = 0; i < companies.length; i++) {
            var company = companies[i] || {};
            if (company.id) companyMap[String(company.id)] = company.name || String(company.id);
          }
        } catch (_e) {
          companyMap = {};
        }

        return {
          rows: commissions.map(function (item) {
            var companyLabel = item.companyName || companyMap[String(item.companyId || '')] || item.companyId || '—';
            return [
              item.name || '—',
              item.type || '—',
              companyLabel,
              catSimpleActiveBadge(!!item.active),
              catSimpleUpdated(item.lastUpdated || item.dateCreated),
              '',
            ];
          }),
          total: total,
        };
      },
    });
  }

  // ---- #/employees — Nhân viên ----
  function renderCatEmployees() {
    openCatSimpleDataPage({
      key: 'cat-employees',
      title: 'Nhân viên',
      columns: ['Tên', 'Chức vụ', 'Chi nhánh', 'Là bác sĩ', 'Trạng thái', 'Thao tác'],
      hasActions: true,
      endpoint: '/api/employees',
      useCompany: true,
      mapItem: function (item) {
        return [
          item.name || '—',
          item.hrJob || item.jobTitle || '—',
          item.companyName || '—',
          item.isDoctor ? '<span class="tds-badge tds-badge-blue">Bác sĩ</span>' : '<span class="tds-badge tds-badge-default">Nhân sự</span>',
          catSimpleActiveBadge(!!item.active),
          '',
        ];
      },
    });
  }

  // ---- #/labo-params — Thông số Labo ----
  function renderCatLaboParams() {
    openCatSimpleDataPage({
      key: 'cat-labo-params',
      title: 'Thông số Labo',
      columns: ['Tên thông số', 'Mã', 'Loại', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      manageKind: 'labo-materials',
      mapItem: mapManageCategoryRow,
      useCompany: true,
    });
  }

  // ---- #/income-expense-types — Loại thu chi ----
  function renderCatIncomeExpense() {
    openCatSimpleDataPage({
      key: 'cat-income-expense',
      title: 'Loại thu chi',
      columns: ['Tên loại', 'Nhóm', 'Mã', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      useCompany: false,
      loader: async function (params) {
        var query = toQueryString({
          search: params.search,
          limit: 300,
          offset: 0,
        });
        var incomeData = null;
        var expenseData = null;
        try { incomeData = await api('/api/categories/manage/income-types' + query); } catch (_e1) { incomeData = null; }
        try { expenseData = await api('/api/categories/manage/expense-types' + query); } catch (_e2) { expenseData = null; }
        var incomeItems = safeItems(incomeData).map(function (item) { item._group = 'Thu'; return item; });
        var expenseItems = safeItems(expenseData).map(function (item) { item._group = 'Chi'; return item; });
        var merged = incomeItems.concat(expenseItems);
        var start = params.offset || 0;
        var end = start + (params.limit || 20);
        return {
          rows: merged.slice(start, end).map(function (item) {
            return [
              item.name || '—',
              item._group || '—',
              item.code || '—',
              catSimpleActiveBadge(!!item.active),
              catSimpleUpdated(item.updatedAt),
              '',
            ];
          }),
          total: merged.length,
        };
      },
    });
  }

  // ---- #/stock-criteria — Tiêu chí kiểm kho ----
  function renderCatStockCriteria() {
    openCatSimpleDataPage({
      key: 'cat-stock-criteria',
      title: 'Tiêu chí kiểm kho',
      columns: ['Tên tiêu chí', 'Mã', 'Loại', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      manageKind: 'stock-criteria',
      mapItem: mapManageCategoryRow,
      useCompany: true,
    });
  }

  // ---- #/tooth-diagnosis — Chẩn đoán răng ----
  function renderCatToothDiagnosis() {
    openCatSimpleDataPage({
      key: 'cat-tooth-diagnosis',
      title: 'Chẩn đoán răng',
      columns: ['Mã', 'Tên chẩn đoán', 'Nhóm', 'Trạng thái', 'Cập nhật', 'Thao tác'],
      hasActions: true,
      manageKind: 'tooth-diagnosis',
      useCompany: true,
      mapItem: function (item) {
        return [
          item.code || '—',
          item.name || '—',
          item.type || '—',
          catSimpleActiveBadge(!!item.active),
          catSimpleUpdated(item.updatedAt),
          '',
        ];
      },
    });
  }

  function renderCategories() {
    var el = document.getElementById('page-categories');
    if (!el) return;

    var kind = CATEGORY_TYPES.some(function (item) { return item.key === APP.categories.kind; })
      ? APP.categories.kind
      : 'services';
    APP.categories.kind = kind;

    el.innerHTML =
      '<div class="tds-card categories-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Danh mục hệ thống</h2>' +
      '</div>' +
      '<div class="categories-tabs">' +
      CATEGORY_TYPES.map(function (item) {
        var activeClass = item.key === APP.categories.kind ? 'active' : '';
        return '<button class="category-tab-btn ' + activeClass + '" data-kind="' + item.key + '">' + escapeHtml(item.label) + '</button>';
      }).join('') +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="categories-search" placeholder="Tìm theo tên" value="' + escapeHtml(APP.categories.search || '') + '">' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-primary" id="categories-add-btn">+ Thêm danh mục</button>' +
      '</div>' +
      '</div>' +
      '<div id="categories-content"></div>' +
      '</div>';

    var tabs = el.querySelectorAll('.category-tab-btn');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].addEventListener('click', function () {
        var nextKind = this.getAttribute('data-kind');
        if (nextKind === APP.categories.kind) return;
        APP.categories.kind = nextKind;
        APP.categories.search = '';
        renderCategories();
      });
    }

    var searchInput = document.getElementById('categories-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.categories.search = searchInput.value.trim();
        loadCategoriesData();
      }, 250));
    }

    var addBtn = document.getElementById('categories-add-btn');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        openCategoryModal(APP.categories.kind, null);
      });
    }

    loadCategoriesData();
  }

  async function loadCategoriesData() {
    var container = document.getElementById('categories-content');
    if (!container) return;

    APP.categories.loading = true;
    APP.categories.requestId += 1;
    var requestId = APP.categories.requestId;
    container.innerHTML = '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải danh mục...</span></div>';

    try {
      var query = toQueryString({
        search: APP.categories.search,
        limit: 100,
        offset: 0,
        companyId: getSelectedBranchId(),
      });
      var data = await api('/api/categories/manage/' + encodeURIComponent(APP.categories.kind) + query);
      if (requestId !== APP.categories.requestId) return;
      APP.categories.dataByKind[APP.categories.kind] = safeItems(data);
      APP.categories.loading = false;
      renderCategoriesTable();
    } catch (err) {
      if (requestId !== APP.categories.requestId) return;
      APP.categories.loading = false;
      container.innerHTML = '<div class="tds-empty"><p>' + escapeHtml((err && err.message) || 'Không thể tải danh mục') + '</p></div>';
    }
  }

  function renderCategoriesTable() {
    var container = document.getElementById('categories-content');
    if (!container) return;

    var rows = APP.categories.dataByKind[APP.categories.kind] || [];
    if (!rows.length) {
      container.innerHTML = '<div class="tds-empty"><p>Chưa có dữ liệu cho danh mục này.</p></div>';
      return;
    }

    container.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table categories-table">' +
      '<thead>' +
      '<tr>' +
      '<th>Tên</th>' +
      '<th>Mã</th>' +
      '<th>Loại</th>' +
      '<th>Trạng thái</th>' +
      '<th>Cập nhật</th>' +
      '<th></th>' +
      '</tr>' +
      '</thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(item.name || 'N/A') + '</td>' +
          '<td>' + escapeHtml(item.code || '—') + '</td>' +
          '<td>' + escapeHtml(item.type || item.jobTitle || '—') + '</td>' +
          '<td>' + (item.active ? '<span class="tds-badge tds-badge-success">Đang dùng</span>' : '<span class="tds-badge tds-badge-gray">Ẩn</span>') + '</td>' +
          '<td>' + escapeHtml(formatDateTime(item.updatedAt)) + '</td>' +
          '<td class="text-right">' +
          '<button class="tds-btn tds-btn-sm tds-btn-secondary category-edit" data-id="' + escapeHtml(item.id || '') + '">Sửa</button> ' +
          '<button class="tds-btn tds-btn-sm tds-btn-danger category-delete" data-id="' + escapeHtml(item.id || '') + '">Xóa</button>' +
          '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    var editButtons = container.querySelectorAll('.category-edit');
    for (var i = 0; i < editButtons.length; i++) {
      editButtons[i].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        var item = findItemById(APP.categories.dataByKind[APP.categories.kind] || [], id);
        if (!item) return;
        openCategoryModal(APP.categories.kind, item);
      });
    }

    var deleteButtons = container.querySelectorAll('.category-delete');
    for (var j = 0; j < deleteButtons.length; j++) {
      deleteButtons[j].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        if (!id) return;
        deleteCategoryItem(id);
      });
    }
  }

  function openCategoryModal(kind, item) {
    var editing = !!item;
    var typeVisible = kind === 'services' || kind === 'products' || kind === 'partner-sources';

    var content =
      '<form id="category-form">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tên</label>' +
      '<input class="tds-input" id="category-name" required value="' + escapeHtml((item && item.name) || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Mã</label>' +
      '<input class="tds-input" id="category-code" value="' + escapeHtml((item && item.code) || '') + '">' +
      '</div>' +
      (typeVisible
        ? (
          '<div class="tds-form-group">' +
          '<label class="tds-label">Loại</label>' +
          '<input class="tds-input" id="category-type" value="' + escapeHtml((item && item.type) || '') + '">' +
          '</div>'
        )
        : '') +
      '<label class="tds-checkbox-label">' +
      '<input type="checkbox" id="category-active" ' + ((item ? !!item.active : true) ? 'checked' : '') + '>' +
      '<span>Kích hoạt</span>' +
      '</label>' +
      '</form>';

    showModal(editing ? 'Cập nhật danh mục' : 'Thêm danh mục', content, {
      footer:
        '<button class="tds-btn tds-btn-ghost" id="category-cancel-btn">Hủy</button>' +
        '<button class="tds-btn tds-btn-primary" id="category-save-btn">' + (editing ? 'Cập nhật' : 'Thêm mới') + '</button>',
      onOpen: function () {
        var cancelBtn = document.getElementById('category-cancel-btn');
        var saveBtn = document.getElementById('category-save-btn');

        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
        if (saveBtn) {
          saveBtn.addEventListener('click', async function () {
            var payload = {
              name: getInputValue('category-name'),
              code: getInputValue('category-code') || null,
              active: !!(document.getElementById('category-active') || {}).checked,
              companyId: getSelectedBranchId() || null,
            };
            if (typeVisible) {
              payload.type = getInputValue('category-type') || null;
            }

            if (!payload.name) {
              showToast('warning', 'Tên danh mục là bắt buộc');
              return;
            }

            try {
              if (editing && item && item.id) {
                await api('/api/categories/manage/' + encodeURIComponent(kind) + '/' + encodeURIComponent(item.id), {
                  method: 'PUT',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Cập nhật danh mục thành công');
              } else {
                await api('/api/categories/manage/' + encodeURIComponent(kind), {
                  method: 'POST',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Tạo danh mục thành công');
              }
              closeModal();
              loadCategoriesData();
            } catch (err) {
              showToast('error', (err && err.message) || 'Không thể lưu danh mục');
            }
          });
        }
      },
    });
  }

  async function deleteCategoryItem(itemId) {
    var ok = await tdsConfirm('Xóa danh mục này?', { title: 'Xóa danh mục' });
    if (!ok) return;

    try {
      await api('/api/categories/manage/' + encodeURIComponent(APP.categories.kind) + '/' + encodeURIComponent(itemId), {
        method: 'DELETE',
      });
      showToast('success', 'Đã xóa danh mục');
      loadCategoriesData();
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể xóa danh mục');
    }
  }

  function renderSettings() {
    var el = document.getElementById('page-settings');
    if (!el) return;

    var validTabs = ['branches', 'config', 'team', 'other', 'logs'];
    var activeTab = validTabs.indexOf(APP.settings.tab) >= 0 ? APP.settings.tab : 'branches';
    APP.settings.tab = activeTab;

    var tabDefs = [
      { key: 'branches', label: 'Chi nhánh' },
      { key: 'config', label: 'Cấu hình chung' },
      { key: 'team', label: 'Cấu hình Team' },
      { key: 'other', label: 'Cấu hình khác' },
      { key: 'logs', label: 'Lịch sử hoạt động' },
    ];

    var titleMap = {
      branches: 'Chi nhánh',
      config: 'Cấu hình chung',
      team: 'Cấu hình Team',
      other: 'Cấu hình khác',
      logs: 'Lịch sử hoạt động',
    };

    var headerAction = '';
    if (activeTab === 'branches') {
      headerAction = '<button class="tds-btn tds-btn-primary" id="settings-branch-create">Tạo mới</button>';
    } else if (activeTab === 'config') {
      headerAction = '<button class="tds-btn tds-btn-primary" id="settings-config-apply-top">Áp dụng</button>';
    }

    el.innerHTML =
      '<div class="settings-shell">' +
      '<div class="settings-page-header">' +
      '<h2>' + escapeHtml(titleMap[activeTab] || 'Cài đặt') + '</h2>' +
      headerAction +
      '</div>' +
      '<div class="settings-tabs">' +
      tabDefs.map(function (t) {
        return '<button class="settings-tab-btn ' + (activeTab === t.key ? 'active' : '') + '" data-settings-tab="' + t.key + '">' + escapeHtml(t.label) + '</button>';
      }).join('') +
      '</div>' +
      '<div id="settings-content"></div>' +
      '</div>';

    var tabs = el.querySelectorAll('.settings-tab-btn');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].addEventListener('click', function () {
        var tab = this.getAttribute('data-settings-tab');
        if (!tab || tab === APP.settings.tab) return;
        APP.settings.tab = tab;
        renderSettings();
      });
    }

    var createBtn = document.getElementById('settings-branch-create');
    if (createBtn) {
      createBtn.addEventListener('click', function () {
        showToast('info', 'Chi nhánh được quản lý từ hệ thống TDental gốc');
      });
    }

    var applyTopBtn = document.getElementById('settings-config-apply-top');
    if (applyTopBtn) {
      applyTopBtn.addEventListener('click', saveSettingsConfig);
    }

    if (activeTab === 'branches') {
      renderSettingsBranchesLayout();
      loadSettingsBranchesData();
    } else if (activeTab === 'config') {
      renderSettingsConfigLayout();
      loadSettingsConfigData();
    } else if (activeTab === 'team') {
      _renderSettingsTeam();
    } else if (activeTab === 'other') {
      _renderSettingsOther();
    } else if (activeTab === 'logs') {
      _renderSettingsLogs();
    }
  }

  function renderSettingsBranchesLayout() {
    var container = document.getElementById('settings-content');
    if (!container) return;

    container.innerHTML =
      '<div class="settings-branch-shell">' +
      '<div class="settings-branch-warning">' +
      '<span class="settings-warning-icon">&#9888;</span>' +
      '<span>Việt Nam đã chuyển sang <strong>34 tỉnh/thành mới</strong>. Bạn hãy cập nhật theo đơn vị hành chính mới.</span>' +
      '</div>' +
      '<div class="settings-branch-toolbar">' +
      '<input class="tds-search-input" id="settings-branch-search" placeholder="Tìm kiếm theo tên chi nhánh" value="' + escapeHtml(APP.settings.search || '') + '">' +
      '<select class="tds-select" id="settings-branch-status">' +
      '<option value="active"' + (APP.settings.branchStatus === 'active' ? ' selected' : '') + '>Đang hoạt động</option>' +
      '<option value="inactive"' + (APP.settings.branchStatus === 'inactive' ? ' selected' : '') + '>Ngưng hoạt động</option>' +
      '<option value="all"' + (APP.settings.branchStatus === 'all' ? ' selected' : '') + '>Tất cả</option>' +
      '</select>' +
      '</div>' +
      '<div id="settings-branches-table"></div>' +
      '</div>';

    var searchInput = document.getElementById('settings-branch-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.settings.search = searchInput.value.trim();
        APP.settings.branchPage = 1;
        renderSettingsBranchesTable();
      }, 200));
    }

    var statusSelect = document.getElementById('settings-branch-status');
    if (statusSelect) {
      statusSelect.addEventListener('change', function () {
        APP.settings.branchStatus = statusSelect.value;
        APP.settings.branchPage = 1;
        renderSettingsBranchesTable();
      });
    }
  }

  async function loadSettingsBranchesData() {
    var tableWrap = document.getElementById('settings-branches-table');
    if (!tableWrap) return;

    APP.settings.loading = true;
    APP.settings.requestId += 1;
    var requestId = APP.settings.requestId;
    tableWrap.innerHTML = '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải danh sách chi nhánh...</span></div>';

    try {
      var data = await api('/api/companies' + toQueryString({ limit: 0, offset: 0 }));
      if (requestId !== APP.settings.requestId) return;
      APP.settings.branches = safeItems(data);
      APP.settings.loading = false;
      renderSettingsBranchesTable();
    } catch (err) {
      if (requestId !== APP.settings.requestId) return;
      APP.settings.loading = false;
      tableWrap.innerHTML = '<div class="tds-empty"><p>' + escapeHtml((err && err.message) || 'Không thể tải danh sách chi nhánh') + '</p></div>';
    }
  }

  function renderSettingsBranchesTable() {
    var tableWrap = document.getElementById('settings-branches-table');
    if (!tableWrap) return;

    var rows = Array.isArray(APP.settings.branches) ? APP.settings.branches.slice() : [];
    var search = (APP.settings.search || '').trim().toLowerCase();
    if (search) {
      rows = rows.filter(function (item) {
        var name = String(item.name || '').toLowerCase();
        var address = String(item.address || '').toLowerCase();
        return name.indexOf(search) >= 0 || address.indexOf(search) >= 0;
      });
    }

    if (APP.settings.branchStatus === 'active') {
      rows = rows.filter(function (item) { return !!item.active; });
    } else if (APP.settings.branchStatus === 'inactive') {
      rows = rows.filter(function (item) { return !item.active; });
    }

    var total = rows.length;
    var pageSize = APP.settings.branchPageSize || 20;
    var totalPages = Math.max(1, Math.ceil(total / pageSize));
    if (APP.settings.branchPage > totalPages) APP.settings.branchPage = totalPages;
    if (APP.settings.branchPage < 1) APP.settings.branchPage = 1;

    var start = (APP.settings.branchPage - 1) * pageSize;
    var pageRows = rows.slice(start, start + pageSize);

    if (!pageRows.length) {
      tableWrap.innerHTML = renderEmptyState('Chưa có dữ liệu chi nhánh');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table settings-branches-table">' +
      '<thead><tr><th>Chi nhánh</th><th>Địa chỉ</th><th>Thao tác</th></tr></thead>' +
      '<tbody>' +
      pageRows.map(function (item) {
        return (
          '<tr>' +
          '<td><span class="settings-branch-arrow">&#8250;</span> ' + escapeHtml(item.name || 'N/A') + '</td>' +
          '<td>' + escapeHtml(item.address || '—') + '</td>' +
          '<td><div class="catalog-action-icons">' +
          '<button class="cat-action-edit settings-branch-action" data-action="edit" data-id="' + escapeHtml(item.id || '') + '" title="Sửa"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>' +
          '<button class="cat-action-view settings-branch-action" data-action="more" data-id="' + escapeHtml(item.id || '') + '" title="Chi tiết"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg></button>' +
          '<button class="cat-action-delete settings-branch-action" data-action="delete" data-id="' + escapeHtml(item.id || '') + '" title="Xóa"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>' +
          '</div></td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>' +
      '<div class="catalog-right-footer">' +
      '<div class="catalog-footer-left">' +
      '<div class="catalog-pagination">' + renderCatPagination(APP.settings.branchPage, totalPages) + '</div>' +
      '<select class="catalog-filter-select" id="settings-branch-pagesize">' +
      '<option value="20"' + (pageSize === 20 ? ' selected' : '') + '>20</option>' +
      '<option value="50"' + (pageSize === 50 ? ' selected' : '') + '>50</option>' +
      '<option value="100"' + (pageSize === 100 ? ' selected' : '') + '>100</option>' +
      '</select>' +
      '<span>hàng trên trang</span>' +
      '</div>' +
      '<div class="catalog-footer-right">' + (total > 0 ? ((start + 1) + '-' + Math.min(start + pageSize, total) + ' của ' + total + ' dòng') : '0 dòng') + '</div>' +
      '</div>';

    var pagBtns = tableWrap.querySelectorAll('.catalog-pagination button[data-page]');
    for (var i = 0; i < pagBtns.length; i++) {
      pagBtns[i].addEventListener('click', function () {
        var pg = parseInt(this.getAttribute('data-page'), 10);
        if (pg >= 1 && pg <= totalPages) {
          APP.settings.branchPage = pg;
          renderSettingsBranchesTable();
        }
      });
    }

    var pageSizeSelect = document.getElementById('settings-branch-pagesize');
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener('change', function () {
        APP.settings.branchPageSize = parseInt(this.value, 10) || 20;
        APP.settings.branchPage = 1;
        renderSettingsBranchesTable();
      });
    }

    var actionBtns = tableWrap.querySelectorAll('.settings-branch-action');
    for (var j = 0; j < actionBtns.length; j++) {
      actionBtns[j].addEventListener('click', function () {
        showToast('info', 'Chi nhánh được quản lý từ hệ thống TDental gốc');
      });
    }
  }

  // Settings Team tab
  function _renderSettingsTeam() {
    var container = document.getElementById('settings-content'); if (!container) return;
    container.innerHTML =
      '<div class="tds-table-toolbar"><div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-primary" id="st-create-btn">Tạo Team</button></div></div>' +
      '<div style="display:flex;gap:16px"><div style="flex:1" id="st-list"></div><div style="flex:2" id="st-members"><div class="tds-empty"><p>Chọn team để xem thành viên</p></div></div></div>';
    var cb = document.getElementById('st-create-btn');
    if (cb) cb.addEventListener('click', function () {
      showModal('Tạo Team',
        '<form><div class="tds-form-group"><label class="tds-label">Tên Team</label><input class="tds-input" id="st-f-name"></div><div class="tds-form-group"><label class="tds-label">Mô tả</label><input class="tds-input" id="st-f-desc"></div></form>',
        { footer: '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeModal()">Hủy</button><button class="tds-btn tds-btn-primary" id="st-save">Lưu</button>',
          onOpen: function () { var sv = document.getElementById('st-save'); if (sv) sv.addEventListener('click', async function () {
            try { await api('/api/teams', { method: 'POST', body: JSON.stringify({ name: getInputValue('st-f-name'), description: getInputValue('st-f-desc') }) }); showToast('success', 'Đã tạo team'); closeModal(); _loadTeamList(); }
            catch (err) { showToast('error', (err && err.message) || 'Lỗi'); } }); } });
    });
    _loadTeamList();
  }
  async function _loadTeamList() {
    var c = document.getElementById('st-list'); if (!c) return;
    c.innerHTML = renderLoadingState('Đang tải...');
    try {
      var teams = safeItems(await api('/api/teams'));
      if (!teams.length) { c.innerHTML = renderEmptyState('Chưa có team nào'); return; }
      c.innerHTML = teams.map(function (t) {
        return '<div class="tds-card" style="padding:12px;margin-bottom:8px;cursor:pointer;border:1px solid #E2E8F0;border-radius:8px" data-tid="' + escapeHtml(t.id || '') + '" class="st-team-item"><strong>' + escapeHtml(t.name || 'N/A') + '</strong><p class="text-secondary text-sm" style="margin:4px 0 0">' + escapeHtml(t.description || '') + '</p></div>';
      }).join('');
      var items = c.querySelectorAll('[data-tid]');
      for (var i = 0; i < items.length; i++) items[i].addEventListener('click', function () { _loadTeamMembers(this.getAttribute('data-tid')); });
    } catch (_e) { c.innerHTML = renderEmptyState('Không thể tải danh sách team'); }
  }
  async function _loadTeamMembers(teamId) {
    var c = document.getElementById('st-members'); if (!c) return;
    c.innerHTML = renderLoadingState('Đang tải thành viên...');
    try {
      var members = safeItems(await api('/api/teams/' + encodeURIComponent(teamId) + '/members'));
      if (!members.length) { c.innerHTML = renderEmptyState('Chưa có thành viên trong team'); return; }
      c.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Tên</th><th>Email</th><th>Vai trò</th><th>Thao tác</th></tr></thead><tbody>' +
        members.map(function (m, idx) { return '<tr><td>' + escapeHtml(m.name || 'N/A') + '</td><td>' + escapeHtml(m.email || '—') + '</td><td>' + escapeHtml(m.role || '—') + '</td><td><button class="tds-btn tds-btn-sm tds-btn-danger st-member-delete" data-team-id="' + escapeHtml(teamId) + '" data-member-idx="' + idx + '">Xóa</button></td></tr>'; }).join('') +
        '</tbody></table></div>';
      // Add click handlers for delete buttons
      var deleteBtns = c.querySelectorAll('.st-member-delete');
      for (var i = 0; i < deleteBtns.length; i++) {
        deleteBtns[i].addEventListener('click', function() {
          var teamIdBtn = this.getAttribute('data-team-id');
          var idx = parseInt(this.getAttribute('data-member-idx'), 10);
          var member = members[idx];
          if (member) showTeamMemberDeleteConfirm(teamIdBtn, member, members, _loadTeamMembers);
        });
      }
    } catch (_e) { c.innerHTML = renderEmptyState('Không thể tải thành viên'); }
  }

  // P9: Team Member Delete Confirmation
  function showTeamMemberDeleteConfirm(teamId, member, allMembers, refreshCallback) {
    // Get list of other members for reassignment
    var otherMembers = allMembers.filter(function(m) { return m.id !== member.id; });
    var reassignOptions = '<option value="">— Không chuyển —</option>';
    for (var i = 0; i < otherMembers.length; i++) {
      reassignOptions += '<option value="' + escapeHtml(otherMembers[i].id) + '">' + escapeHtml(otherMembers[i].name || otherMembers[i].email) + '</option>';
    }

    var content =
      '<div class="team-delete-confirm">' +
      '<p>Bạn có chắc chắn muốn xóa thành viên <strong>' + escapeHtml(member.name || member.email) + '</strong> khỏi team không?</p>' +
      '<div class="team-delete-reassign">' +
      '<label>Chuyển công việc cho:</label>' +
      '<select class="tds-select" id="tm-reassign">' + reassignOptions + '</select>' +
      '</div>' +
      '</div>';

    var footer = '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeModal()">Hủy</button>' +
      '<button class="tds-btn tds-btn-danger" id="tm-confirm-delete">Xóa</button>';

    showModal('Xóa thành viên', content, {
      width: 420,
      footer: footer,
      onOpen: function() {
        var confirmBtn = document.getElementById('tm-confirm-delete');
        if (confirmBtn) {
          confirmBtn.addEventListener('click', async function() {
            var reassignTo = document.getElementById('tm-reassign') ? document.getElementById('tm-reassign').value : '';
            try {
              // Try to call delete API if available
              await api('/api/teams/' + encodeURIComponent(teamId) + '/members/' + encodeURIComponent(member.id), {
                method: 'DELETE',
                body: JSON.stringify({ reassignTo: reassignTo || null }),
              });
              showToast('success', 'Đã xóa thành viên');
            } catch (err) {
              showToast('error', (err && err.message) || 'Không thể xóa thành viên');
              return;
            }
            closeModal();
            if (refreshCallback) refreshCallback(teamId);
          });
        }
      },
    });
  }

  // Settings Other tab - Feature toggles
  function _renderSettingsOther() {
    var container = document.getElementById('settings-content'); if (!container) return;
    container.innerHTML = renderLoadingState('Đang tải cấu hình...');
    _loadSettingsOtherData(container);
  }
  async function _loadSettingsOtherData(container) {
    try {
      var data = await api('/api/settings');
      var map = (data && data.map) || {};
      var toggles = [
        { key: 'customer_care', label: 'Chăm sóc KH' },
        { key: 'zalo_zns', label: 'ZALO ZNS' },
        { key: 'appointment_reminder', label: 'Nhắc lịch hẹn' },
        { key: 'visit_payment', label: 'Thanh toán đợt khám' },
      ];
      container.innerHTML = '<div class="settings-toggles" style="max-width:480px">' +
        toggles.map(function (t) {
          var on = String(map[t.key] || 'false') === 'true';
          return '<div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid #E2E8F0"><span style="font-weight:500">' + escapeHtml(t.label) + '</span>' +
            '<label style="position:relative;display:inline-block;width:44px;height:24px"><input type="checkbox" class="so-toggle" data-key="' + t.key + '"' + (on ? ' checked' : '') + ' style="opacity:0;width:0;height:0"><span style="position:absolute;cursor:pointer;inset:0;background:' + (on ? '#3B82F6' : '#CBD5E1') + ';border-radius:12px;transition:.3s"></span></label></div>';
        }).join('') +
        '</div><div style="margin-top:16px"><button class="tds-btn tds-btn-primary" id="so-apply-btn">Áp dụng</button></div>';
      var ab = document.getElementById('so-apply-btn');
      if (ab) ab.addEventListener('click', async function () {
        var items = [];
        var inputs = container.querySelectorAll('.so-toggle');
        for (var i = 0; i < inputs.length; i++) items.push({ key: inputs[i].getAttribute('data-key'), value: inputs[i].checked ? 'true' : 'false' });
        try { await api('/api/settings', { method: 'POST', body: JSON.stringify({ items: items }) }); showToast('success', 'Đã lưu cấu hình'); }
        catch (err) { showToast('error', (err && err.message) || 'Không thể lưu'); }
      });
    } catch (err) { container.innerHTML = renderEmptyState('Không thể tải cấu hình'); }
  }

  // Settings Logs tab - Activity log
  function _renderSettingsLogs() {
    var container = document.getElementById('settings-content'); if (!container) return;
    container.innerHTML =
      '<div class="tds-table-toolbar"><div class="toolbar-left">' +
      '<input class="tds-input" id="sl-from" type="date" value="' + escapeHtml(MONTH_START_ISO) + '">' +
      '<input class="tds-input" id="sl-to" type="date" value="' + escapeHtml(TODAY_ISO) + '">' +
      '<input class="tds-search-input" id="sl-search" placeholder="Tìm theo tài khoản">' +
      '<button class="tds-btn tds-btn-primary" id="sl-apply">Áp dụng</button></div></div>' +
      '<div id="sl-content"></div>';
    var ab = document.getElementById('sl-apply'); if (ab) ab.addEventListener('click', _loadSettingsLogsData);
    _loadSettingsLogsData();
  }
  async function _loadSettingsLogsData() {
    var c = document.getElementById('sl-content'); if (!c) return;
    c.innerHTML = renderLoadingState('Đang tải lịch sử...');
    try {
      var q = toQueryString({ dateFrom: getInputValue('sl-from') || MONTH_START_ISO, dateTo: getInputValue('sl-to') || TODAY_ISO, search: getInputValue('sl-search'), limit: 100, offset: 0 });
      var rows = safeItems(await api('/api/settings/logs' + q));
      if (!rows.length) { c.innerHTML = renderEmptyState('Không có lịch sử hoạt động'); return; }
      c.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Thời gian</th><th>Tài khoản</th><th>Hành động</th><th>Loại đối tượng</th><th>Id</th><th>Tên</th><th>Thao tác</th></tr></thead><tbody>' +
        rows.map(function (r, idx) { return '<tr><td>' + escapeHtml(formatDateTime(r.createdAt || r.timestamp)) + '</td><td>' + escapeHtml(r.userName || r.userEmail || '—') + '</td><td>' + escapeHtml(r.action || '—') + '</td><td>' + escapeHtml(r.objectType || r.resourceType || '—') + '</td><td>' + escapeHtml(r.objectId || r.resourceId || '—') + '</td><td>' + escapeHtml(r.objectName || r.resourceName || '—') + '</td><td><button class="tds-btn tds-btn-sm tds-btn-secondary sl-detail-btn" data-log-idx="' + idx + '">Chi tiết</button></td></tr>'; }).join('') +
        '</tbody></table></div>';
      // Add click handlers for detail buttons
      var detailBtns = c.querySelectorAll('.sl-detail-btn');
      for (var i = 0; i < detailBtns.length; i++) {
        detailBtns[i].addEventListener('click', function() {
          var idx = parseInt(this.getAttribute('data-log-idx'), 10);
          var row = rows[idx];
          if (row) showAuditLogDetail(row);
        });
      }
    } catch (err) { c.innerHTML = renderEmptyState((err && err.message) || 'Không thể tải lịch sử'); }
  }

  // P8: Show Audit Log Detail in Drawer
  function showAuditLogDetail(row) {
    var timestamp = formatDateTime(row.createdAt || row.timestamp);
    var user = row.userName || row.userEmail || '—';
    var action = row.action || '—';
    var objectType = row.objectType || row.resourceType || '—';
    var objectId = row.objectId || row.resourceId || '—';
    var objectName = row.objectName || row.resourceName || '—';
    var beforeJson = row.before || row.previousData || null;
    var afterJson = row.after || row.newData || null;

    // Build diff display
    var diffHtml = '';
    if (beforeJson && afterJson) {
      try {
        var before = typeof beforeJson === 'string' ? JSON.parse(beforeJson) : beforeJson;
        var after = typeof afterJson === 'string' ? JSON.parse(afterJson) : afterJson;
        var allKeys = Object.keys(Object.assign({}, before, after));
        diffHtml = '<div class="audit-detail-diff">';
        for (var k = 0; k < allKeys.length; k++) {
          var key = allKeys[k];
          var beforeVal = before[key];
          var afterVal = after[key];
          if (beforeVal !== afterVal) {
            diffHtml += '<div class="audit-detail-row"><span class="audit-detail-label">' + escapeHtml(key) + '</span><span class="audit-detail-value">';
            if (beforeVal !== undefined) {
              diffHtml += '<span class="audit-diff-removed">' + escapeHtml(String(beforeVal)) + '</span>';
            }
            if (afterVal !== undefined) {
              diffHtml += ' <span class="audit-diff-added">' + escapeHtml(String(afterVal)) + '</span>';
            }
            diffHtml += '</span></div>';
          }
        }
        diffHtml += '</div>';
      } catch(e) {
        diffHtml = '<pre>' + escapeHtml(JSON.stringify({ before: beforeJson, after: afterJson }, null, 2)) + '</pre>';
      }
    } else if (beforeJson || afterJson) {
      diffHtml = '<pre>' + escapeHtml(JSON.stringify(beforeJson || afterJson, null, 2)) + '</pre>';
    } else {
      diffHtml = '<p class="text-muted">Không có dữ liệu chi tiết</p>';
    }

    var html =
      '<div class="audit-detail-drawer">' +
      '<div class="audit-detail-header">' +
      '<h3>Chi tiết hoạt động</h3>' +
      '<button class="tds-btn tds-btn-ghost" onclick="TDS.closeDrawer()">&times;</button>' +
      '</div>' +
      '<div class="audit-detail-section">' +
      '<h4>Thông tin chung</h4>' +
      '<div class="audit-detail-row"><span class="audit-detail-label">Thời gian</span><span class="audit-detail-value">' + escapeHtml(timestamp) + '</span></div>' +
      '<div class="audit-detail-row"><span class="audit-detail-label">Tài khoản</span><span class="audit-detail-value">' + escapeHtml(user) + '</span></div>' +
      '<div class="audit-detail-row"><span class="audit-detail-label">Hành động</span><span class="audit-detail-value">' + escapeHtml(action) + '</span></div>' +
      '<div class="audit-detail-row"><span class="audit-detail-label">Loại đối tượng</span><span class="audit-detail-value">' + escapeHtml(objectType) + '</span></div>' +
      '<div class="audit-detail-row"><span class="audit-detail-label">ID</span><span class="audit-detail-value">' + escapeHtml(objectId) + '</span></div>' +
      '<div class="audit-detail-row"><span class="audit-detail-label">Tên</span><span class="audit-detail-value">' + escapeHtml(objectName) + '</span></div>' +
      '</div>' +
      '<div class="audit-detail-section">' +
      '<h4>Thay đổi dữ liệu</h4>' +
      diffHtml +
      '</div>' +
      '</div>';

    openDrawer(html, 500);
  }

  function renderSettingsUsersLayout() {
    var container = document.getElementById('settings-content');
    if (!container) return;

    container.innerHTML =
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="settings-user-search" placeholder="Tìm tên hoặc email" value="' + escapeHtml(APP.settings.search || '') + '">' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-secondary" id="settings-users-export">Xuất Excel</button>' +
      '<button class="tds-btn tds-btn-primary" id="settings-user-add">Thêm tài khoản</button>' +
      '</div>' +
      '</div>' +
      '<div id="settings-users-table"></div>';

    var searchInput = document.getElementById('settings-user-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.settings.search = searchInput.value.trim();
        loadUsersData();
      }, 250));
    }

    var addBtn = document.getElementById('settings-user-add');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        openUserModal(null);
      });
    }

    var exportBtn = document.getElementById('settings-users-export');
    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        downloadExcel('users', {
          search: APP.settings.search,
          columns: ['name', 'email', 'role', 'active', 'createdAt'],
        });
      });
    }
  }

  async function loadUsersData() {
    var tableWrap = document.getElementById('settings-users-table');
    if (!tableWrap) return;

    APP.settings.loading = true;
    APP.settings.requestId += 1;
    var requestId = APP.settings.requestId;

    tableWrap.innerHTML = '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải tài khoản...</span></div>';

    try {
      var query = toQueryString({
        search: APP.settings.search,
        limit: 100,
        offset: 0,
      });
      var data = await api('/api/users' + query);
      if (requestId !== APP.settings.requestId) return;
      APP.settings.users = safeItems(data);
      APP.settings.loading = false;
      renderUsersTable();
    } catch (err) {
      if (requestId !== APP.settings.requestId) return;
      APP.settings.loading = false;
      tableWrap.innerHTML = '<div class="tds-empty"><p>' + escapeHtml((err && err.message) || 'Không thể tải tài khoản') + '</p></div>';
    }
  }

  function renderUsersTable() {
    var tableWrap = document.getElementById('settings-users-table');
    if (!tableWrap) return;

    var rows = APP.settings.users || [];
    if (!rows.length) {
      tableWrap.innerHTML = '<div class="tds-empty"><p>Chưa có tài khoản nào.</p></div>';
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table settings-users-table">' +
      '<thead><tr><th>Tên</th><th>Email</th><th>Vai trò</th><th>Trạng thái</th><th>Ngày tạo</th><th></th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(item.name || 'N/A') + '</td>' +
          '<td>' + escapeHtml(item.email || '—') + '</td>' +
          '<td>' + escapeHtml(item.role || 'viewer') + '</td>' +
          '<td>' + (item.active ? '<span class="tds-badge tds-badge-success">Hoạt động</span>' : '<span class="tds-badge tds-badge-gray">Tạm khóa</span>') + '</td>' +
          '<td>' + escapeHtml(formatDateTime(item.createdAt)) + '</td>' +
          '<td class="text-right">' +
          '<button class="tds-btn tds-btn-sm tds-btn-secondary user-edit" data-id="' + escapeHtml(item.id || '') + '">Sửa</button> ' +
          '<button class="tds-btn tds-btn-sm tds-btn-danger user-delete" data-id="' + escapeHtml(item.id || '') + '">Xóa</button>' +
          '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    var editBtns = tableWrap.querySelectorAll('.user-edit');
    for (var i = 0; i < editBtns.length; i++) {
      editBtns[i].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        var user = findItemById(APP.settings.users || [], id);
        if (!user) return;
        openUserModal(user);
      });
    }

    var deleteBtns = tableWrap.querySelectorAll('.user-delete');
    for (var j = 0; j < deleteBtns.length; j++) {
      deleteBtns[j].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        deleteUser(id);
      });
    }
  }

  function openUserModal(user) {
    var editing = !!user;

    var content =
      '<form id="user-form">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Họ tên</label>' +
      '<input class="tds-input" id="user-name-input" required value="' + escapeHtml((user && user.name) || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Email</label>' +
      '<input class="tds-input" id="user-email-input" required value="' + escapeHtml((user && user.email) || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Mật khẩu ' + (editing ? '(để trống nếu không đổi)' : '') + '</label>' +
      '<input class="tds-input" id="user-password-input" type="password" ' + (editing ? '' : 'required') + '>' +
      '</div>' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Vai trò</label>' +
      '<select class="tds-select" id="user-role-input">' +
      '<option value="viewer" ' + (((user && user.role) || 'viewer') === 'viewer' ? 'selected' : '') + '>viewer</option>' +
      '<option value="staff" ' + (((user && user.role) || '') === 'staff' ? 'selected' : '') + '>staff</option>' +
      '<option value="manager" ' + (((user && user.role) || '') === 'manager' ? 'selected' : '') + '>manager</option>' +
      '<option value="admin" ' + (((user && user.role) || '') === 'admin' ? 'selected' : '') + '>admin</option>' +
      '</select>' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Trạng thái</label>' +
      '<select class="tds-select" id="user-active-input">' +
      '<option value="true" ' + ((user ? !!user.active : true) ? 'selected' : '') + '>Hoạt động</option>' +
      '<option value="false" ' + ((user && !user.active) ? 'selected' : '') + '>Tạm khóa</option>' +
      '</select>' +
      '</div>' +
      '</div>' +
      '</form>';

    showModal(editing ? 'Cập nhật tài khoản' : 'Thêm tài khoản', content, {
      footer:
        '<button class="tds-btn tds-btn-ghost" id="user-modal-cancel">Hủy</button>' +
        '<button class="tds-btn tds-btn-primary" id="user-modal-save">' + (editing ? 'Cập nhật' : 'Tạo tài khoản') + '</button>',
      onOpen: function () {
        var cancelBtn = document.getElementById('user-modal-cancel');
        var saveBtn = document.getElementById('user-modal-save');
        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

        if (saveBtn) {
          saveBtn.addEventListener('click', async function () {
            var payload = {
              name: getInputValue('user-name-input'),
              email: getInputValue('user-email-input'),
              role: getInputValue('user-role-input') || 'viewer',
              active: getInputValue('user-active-input') === 'true',
            };
            var password = getInputValue('user-password-input');
            if (password) payload.password = password;

            if (!payload.name || !payload.email) {
              showToast('warning', 'Vui lòng nhập đủ họ tên và email');
              return;
            }
            if (!editing && !payload.password) {
              showToast('warning', 'Mật khẩu là bắt buộc khi tạo tài khoản');
              return;
            }

            try {
              if (editing && user && user.id) {
                await api('/api/users/' + encodeURIComponent(user.id), {
                  method: 'PUT',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Đã cập nhật tài khoản');
              } else {
                await api('/api/users', {
                  method: 'POST',
                  body: JSON.stringify(payload),
                });
                showToast('success', 'Đã tạo tài khoản');
              }

              closeModal();
              loadUsersData();
            } catch (err) {
              showToast('error', (err && err.message) || 'Không thể lưu tài khoản');
            }
          });
        }
      },
    });
  }

  async function deleteUser(userId) {
    if (!userId) return;
    var ok = await tdsConfirm('Xóa tài khoản này?', { title: 'Xóa tài khoản' });
    if (!ok) return;

    try {
      await api('/api/users/' + encodeURIComponent(userId), { method: 'DELETE' });
      showToast('success', 'Đã xóa tài khoản');
      loadUsersData();
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể xóa tài khoản');
    }
  }

  function renderSettingsConfigLayout() {
    var container = document.getElementById('settings-content');
    if (!container) return;
    container.innerHTML = '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải cấu hình...</span></div>';
  }

  async function loadSettingsConfigData() {
    var container = document.getElementById('settings-content');
    if (!container) return;

    APP.settings.loading = true;
    APP.settings.requestId += 1;
    var requestId = APP.settings.requestId;

    try {
      APP.settings.config = await api('/api/settings');
      if (requestId !== APP.settings.requestId) return;
      APP.settings.loading = false;
      renderSettingsConfigForm();
    } catch (err) {
      if (requestId !== APP.settings.requestId) return;
      APP.settings.loading = false;
      container.innerHTML = '<div class="tds-empty"><p>' + escapeHtml((err && err.message) || 'Không thể tải cấu hình') + '</p></div>';
    }
  }

  function renderSettingsConfigForm() {
    var container = document.getElementById('settings-content');
    if (!container) return;

    var map = (APP.settings.config && APP.settings.config.map) || {};
    var commonFlags = [
      { key: 'cfg_marketing', label: 'Marketing', desc: 'Quản lý chương trình khuyến mãi, thẻ ưu đãi' },
      { key: 'cfg_unit', label: 'Đơn vị tính', desc: 'Hàng hóa có thể nhập xuất nhiều đơn vị tính' },
      { key: 'cfg_sms_brandname', label: 'SMS Brandname CSKH', desc: 'Quản lý SMS Brandname CSKH' },
      { key: 'cfg_insurance', label: 'Bảo hiểm', desc: 'Quản lý và đối soát công nợ bảo hiểm' },
      { key: 'cfg_customer_survey', label: 'Khảo sát khách hàng', desc: 'Quản lý và đánh giá chất lượng dịch vụ NK' },
      { key: 'cfg_refund', label: 'Hoàn tiền điều trị', desc: 'Cho phép tạo thanh toán hoàn tiền dịch vụ điều trị' },
      { key: 'cfg_reminder', label: 'Nhắc lịch hẹn', desc: 'Hiện thông báo khi sắp tới lịch hẹn' },
      { key: 'cfg_pharmacy', label: 'Bán thuốc', desc: 'Quản lý đơn thuốc và hóa đơn thuốc' },
      { key: 'cfg_survey_module', label: 'Khảo sát đánh giá', desc: 'Quản lý và cấu hình khảo sát đánh giá' },
      { key: 'cfg_stock_limit', label: 'Xuất kho quá số lượng tồn', desc: 'Không cho phép xuất kho quá số lượng tồn' },
      { key: 'cfg_foreign_currency', label: 'Thanh toán ngoại tệ', desc: 'Thanh toán phiếu điều trị bằng ngoại tệ' },
      { key: 'cfg_head_office', label: 'Head Office', desc: 'Quản lý tính năng Head Office' },
    ];
    var multiBranchFlags = [
      { key: 'cfg_shared_partner', label: 'Dùng chung danh sách đối tác' },
      { key: 'cfg_shared_product', label: 'Dùng chung danh sách sản phẩm' },
    ];

    container.innerHTML =
      '<div class="settings-config-panel">' +
      '<h3 class="settings-config-title">CẤU HÌNH CHUNG</h3>' +
      '<div class="settings-config-grid">' +
      commonFlags.map(function (item) {
        var checked = String(map[item.key] || 'false') === 'true' ? ' checked' : '';
        return '<label class="settings-config-item">' +
        '<input type="checkbox" class="settings-config-check" data-cfg-key="' + escapeHtml(item.key) + '"' + checked + '>' +
        '<div class="settings-config-item-body">' +
        '<span class="settings-config-item-label">' + escapeHtml(item.label) + '</span>' +
        '<span class="settings-config-item-desc">' + escapeHtml(item.desc) + '</span>' +
        '</div>' +
        '</label>';
      }).join('') +
      '</div>' +
      '<h3 class="settings-config-title">ĐA CHI NHÁNH</h3>' +
      '<div class="settings-config-grid settings-config-grid-two">' +
      multiBranchFlags.map(function (item) {
        var checked = String(map[item.key] || 'false') === 'true' ? ' checked' : '';
        return '<label class="settings-config-item">' +
        '<input type="checkbox" class="settings-config-check" data-cfg-key="' + escapeHtml(item.key) + '"' + checked + '>' +
        '<div class="settings-config-item-body">' +
        '<span class="settings-config-item-label">' + escapeHtml(item.label) + '</span>' +
        '</div>' +
        '</label>';
      }).join('') +
      '</div>' +
      '<div class="settings-config-actions"><button type="button" class="tds-btn tds-btn-primary" id="settings-apply-btn">Áp dụng</button></div>' +
      '</div>';

    var inlineApplyBtn = document.getElementById('settings-apply-btn');
    if (inlineApplyBtn) inlineApplyBtn.addEventListener('click', saveSettingsConfig);
  }

  async function saveSettingsConfig() {
    var container = document.getElementById('settings-content');
    if (!container) return;

    var checks = container.querySelectorAll('.settings-config-check[data-cfg-key]');
    if (!checks.length) {
      showToast('warning', 'Cấu hình đang tải, vui lòng thử lại');
      return;
    }
    var items = [];
    for (var i = 0; i < checks.length; i++) {
      items.push({
        key: checks[i].getAttribute('data-cfg-key'),
        value: checks[i].checked ? 'true' : 'false',
      });
    }

    try {
      await api('/api/settings', {
        method: 'POST',
        body: JSON.stringify({ items: items }),
      });
      showToast('success', 'Đã lưu cài đặt');
      loadSettingsConfigData();
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể lưu cài đặt');
    }
  }

  // ---------------------------------------------------------------------------
  // Export Helpers
  // ---------------------------------------------------------------------------
  async function downloadExcel(resource, filters) {
    filters = filters || {};

    var params = new URLSearchParams();
    params.set('format', 'xlsx');

    Object.keys(filters).forEach(function (key) {
      var value = filters[key];
      if (value === null || value === undefined || value === '') return;
      if (Array.isArray(value)) {
        if (value.length) params.set(key, value.join(','));
        return;
      }
      params.set(key, String(value));
    });

    var url = '/api/export/' + encodeURIComponent(resource) + '?' + params.toString();

    try {
      var headers = {};
      var token = localStorage.getItem('token');
      if (token) headers.Authorization = 'Bearer ' + token;

      var response = await fetch(url, {
        method: 'GET',
        headers: headers,
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }

      if (!response.ok) {
        var errText = '';
        try {
          var errJson = await response.json();
          errText = errJson.detail || errJson.message || '';
        } catch (_e) {
          errText = await response.text();
        }
        throw new Error(errText || 'Không thể xuất file Excel');
      }

      var blob = await response.blob();
      var disposition = response.headers.get('content-disposition') || '';
      var filenameMatch = disposition.match(/filename="?([^\"]+)"?/i);
      var filename = filenameMatch && filenameMatch[1] ? filenameMatch[1] : resource + '-' + TODAY_ISO + '.xlsx';

      var blobUrl = window.URL.createObjectURL(blob);
      var link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);

      showToast('success', 'Đang tải file Excel');
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể xuất file Excel');
    }
  }

  // ---------------------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------------------
  function renderLoadingState(message) {
    return (
      '<div class="tds-loading">' +
      '<div class="tds-spinner"></div>' +
      '<span>' + escapeHtml(message || 'Đang tải dữ liệu...') + '</span>' +
      '</div>'
    );
  }

  function renderEmptyState(message) {
    return (
      '<div class="tds-empty">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"></circle><line x1="8" y1="15" x2="16" y2="15"></line><line x1="9" y1="10" x2="9.01" y2="10"></line><line x1="15" y1="10" x2="15.01" y2="10"></line></svg>' +
      '<p>' + escapeHtml(message || 'Không có dữ liệu') + '</p>' +
      '</div>'
    );
  }

  function renderErrorState(message) {
    return (
      '<div class="tds-empty tds-error-state">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>' +
      '<p>' + escapeHtml(message || 'Đã có lỗi xảy ra') + '</p>' +
      '</div>'
    );
  }

  function renderSimpleTable(headers, rows, emptyMessage) {
    rows = rows || [];
    if (!rows.length) {
      return '<div class="tds-empty"><p>' + escapeHtml(emptyMessage || 'Không có dữ liệu') + '</p></div>';
    }

    return (
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr>' + headers.map(function (label) { return '<th>' + escapeHtml(label) + '</th>'; }).join('') + '</tr></thead>' +
      '<tbody>' + rows.map(function (row) {
        return '<tr>' + row.map(function (cell) {
          return '<td>' + cell + '</td>';
        }).join('') + '</tr>';
      }).join('') + '</tbody>' +
      '</table>' +
      '</div>'
    );
  }

  function renderTypedValue(value, type) {
    if (type === 'currency') return '<span class="text-right d-block">' + escapeHtml(formatCurrency(value)) + '</span>';
    if (type === 'number') return '<span class="text-right d-block">' + escapeHtml(formatNumber(value)) + '</span>';
    if (type === 'date') return escapeHtml(formatDate(value));
    return escapeHtml(value == null ? '—' : String(value));
  }

  function safeItems(payload) {
    if (!payload) return [];
    if (Array.isArray(payload)) return payload;
    if (payload.items && Array.isArray(payload.items)) return payload.items;
    if (payload.data && Array.isArray(payload.data)) return payload.data;
    if (payload.results && Array.isArray(payload.results)) return payload.results;
    if (payload.rows && Array.isArray(payload.rows)) return payload.rows;
    if (payload.records && Array.isArray(payload.records)) return payload.records;
    return [];
  }

  function toQueryString(params) {
    var usp = new URLSearchParams();
    Object.keys(params || {}).forEach(function (key) {
      var value = params[key];
      if (value === null || value === undefined || value === '') return;
      usp.set(key, String(value));
    });
    var query = usp.toString();
    return query ? ('?' + query) : '';
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str == null ? '' : String(str)));
    return div.innerHTML;
  }

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === 'function') {
      return window.CSS.escape(value);
    }
    return String(value).replace(/"/g, '\\"');
  }

  function startOfDay(value) {
    var dt = value instanceof Date ? new Date(value.getTime()) : new Date(value);
    dt.setHours(0, 0, 0, 0);
    return dt;
  }

  function formatDateInput(value) {
    var dt = value instanceof Date ? value : new Date(value);
    if (!(dt instanceof Date) || isNaN(dt.getTime())) return '';
    var year = dt.getFullYear();
    var month = String(dt.getMonth() + 1).padStart(2, '0');
    var day = String(dt.getDate()).padStart(2, '0');
    return year + '-' + month + '-' + day;
  }

  function formatDate(value) {
    if (!value) return '—';
    var dt = value instanceof Date ? value : new Date(value);
    if (isNaN(dt.getTime())) return '—';
    return dt.toLocaleDateString('vi-VN');
  }

  function formatDateTime(value) {
    if (!value) return '—';
    var dt = value instanceof Date ? value : new Date(value);
    if (isNaN(dt.getTime())) return '—';
    return dt.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function toNumber(value) {
    if (value === null || value === undefined || value === '') return 0;
    var number = Number(value);
    if (!isFinite(number)) return 0;
    return number;
  }

  function formatCurrency(value) {
    var number = Number(value || 0);
    if (!isFinite(number)) number = 0;
    return number.toLocaleString('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 });
  }

  function formatNumber(value) {
    var number = Number(value || 0);
    if (!isFinite(number)) number = 0;
    return number.toLocaleString('vi-VN');
  }

  var STATE_VI = {
    draft: 'Nháp', confirmed: 'Đã xác nhận', done: 'Hoàn thành', cancel: 'Đã hủy',
    cancelled: 'Đã hủy', posted: 'Đã xác nhận', paid: 'Đã thanh toán',
    waiting: 'Chờ khám', arrived: 'Đã đến', examining: 'Đang khám',
    in_progress: 'Đang khám', open: 'Mở', closed: 'Đóng',
    sent: 'Đã gửi', received: 'Đã nhận', approved: 'Đã duyệt',
    refused: 'Từ chối', pending: 'Chờ xử lý'
  };

  function translateState(state) {
    if (!state) return '—';
    return STATE_VI[state.toLowerCase()] || state;
  }

  function stateBadgeClass(state) {
    if (!state) return 'tds-badge-default';
    var s = state.toLowerCase();
    if (s === 'done' || s === 'posted' || s === 'paid' || s === 'approved') return 'tds-badge-green';
    if (s === 'cancel' || s === 'cancelled' || s === 'refused') return 'tds-badge-red';
    if (s === 'draft' || s === 'pending') return 'tds-badge-default';
    if (s === 'confirmed' || s === 'sent' || s === 'open') return 'tds-badge-blue';
    return 'tds-badge-default';
  }

  function getUserInitials(value) {
    var text = String(value || '').trim();
    if (!text) return 'A';
    var words = text.split(/\s+/).filter(Boolean);
    if (words.length === 1) return words[0].slice(0, 1).toUpperCase();
    return (words[0].slice(0, 1) + words[words.length - 1].slice(0, 1)).toUpperCase();
  }

  function getSelectedBranchId() {
    var selector = document.getElementById('branch-selector');
    if (selector && selector.value) return selector.value;
    return localStorage.getItem('selected_branch') || '';
  }

  function getSelectedBranchName() {
    var selector = document.getElementById('branch-selector');
    if (selector && selector.selectedOptions && selector.selectedOptions[0]) {
      return selector.selectedOptions[0].textContent || 'Tất cả chi nhánh';
    }
    return 'Tất cả chi nhánh';
  }

  function getInputValue(id) {
    var el = document.getElementById(id);
    return el ? String(el.value || '').trim() : '';
  }

  function findItemById(items, id) {
    var list = items || [];
    for (var i = 0; i < list.length; i++) {
      if (String(list[i].id) === String(id)) return list[i];
    }
    return null;
  }

  function debounce(fn, waitMs) {
    var timer = null;
    return function () {
      var context = this;
      var args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () {
        fn.apply(context, args);
      }, waitMs || 200);
    };
  }

  function loadRecentCalls() {
    try {
      var raw = localStorage.getItem(RECENT_CALLS_STORAGE_KEY);
      if (!raw) return [];
      var parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (_e) {
      return [];
    }
  }

  function saveRecentCalls(items) {
    try {
      localStorage.setItem(RECENT_CALLS_STORAGE_KEY, JSON.stringify(items || []));
    } catch (_e) {
      // Ignore storage quota failures.
    }
  }

  // ---------------------------------------------------------------------------
  // Custom Confirm Dialog (replaces window.confirm)
  // ---------------------------------------------------------------------------
  function tdsConfirm(message, options) {
    options = options || {};
    var title = options.title || 'Xác nhận';
    return new Promise(function (resolve) {
      var overlay = document.createElement('div');
      overlay.className = 'tds-confirm-overlay';
      overlay.innerHTML =
        '<div class="tds-confirm-box">' +
        '<div class="tds-confirm-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>' +
        '<div class="tds-confirm-title">' + escapeHtml(title) + '</div>' +
        '<div class="tds-confirm-message">' + escapeHtml(message) + '</div>' +
        '<div class="tds-confirm-actions">' +
        '<button class="tds-btn tds-btn-ghost tds-confirm-cancel">Hủy</button>' +
        '<button class="tds-btn tds-btn-danger tds-confirm-ok">' + escapeHtml(options.okText || 'Xóa') + '</button>' +
        '</div></div>';
      document.body.appendChild(overlay);
      requestAnimationFrame(function () { overlay.classList.add('visible'); });

      function close(result) {
        overlay.classList.remove('visible');
        setTimeout(function () { overlay.remove(); }, 280);
        resolve(result);
      }
      overlay.querySelector('.tds-confirm-cancel').addEventListener('click', function () { close(false); });
      overlay.querySelector('.tds-confirm-ok').addEventListener('click', function () { close(true); });
      overlay.addEventListener('click', function (e) { if (e.target === overlay) close(false); });
      document.addEventListener('keydown', function handler(e) {
        if (e.key === 'Escape') { close(false); document.removeEventListener('keydown', handler); }
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Searchable Dropdown Component
  // ---------------------------------------------------------------------------
  function createSearchableDropdown(inputEl, fetchOptions, onSelect) {
    var dropdown = document.createElement('div');
    dropdown.className = 'tds-search-dropdown';
    inputEl.parentElement.style.position = 'relative';
    inputEl.parentElement.appendChild(dropdown);
    var debounceTimer = null;
    var allOptions = [];
    var highlightIdx = -1;

    inputEl.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        var query = inputEl.value.toLowerCase().trim();
        if (query.length < 1) { dropdown.classList.remove('open'); return; }
        if (typeof fetchOptions === 'function') {
          var result = fetchOptions(query);
          if (result && typeof result.then === 'function') {
            result.then(function (opts) { renderOptions(opts, query); });
          } else {
            renderOptions(result || [], query);
          }
        }
      }, 200);
    });

    function renderOptions(options, query) {
      allOptions = options;
      highlightIdx = options.length ? 0 : -1;
      dropdown.innerHTML = options.slice(0, 20).map(function (o, i) {
        return '<div class="tds-search-dropdown-item' + (i === 0 ? ' highlighted' : '') + '" data-idx="' + i + '">' +
          '<span>' + escapeHtml(o.label) + '</span>' +
          (o.meta ? '<span class="item-meta">' + escapeHtml(o.meta) + '</span>' : '') +
          '</div>';
      }).join('') || '<div style="padding:16px;text-align:center;color:#9ca3af;">Không tìm thấy</div>';
      dropdown.classList.add('open');

      dropdown.querySelectorAll('.tds-search-dropdown-item').forEach(function (el) {
        el.addEventListener('click', function () {
          var idx = parseInt(el.getAttribute('data-idx'));
          var selected = allOptions[idx];
          if (selected) {
            inputEl.value = selected.label;
            if (onSelect) onSelect(selected);
            dropdown.classList.remove('open');
          }
        });
      });
    }

    inputEl.addEventListener('keydown', function (e) {
      if (!dropdown.classList.contains('open')) return;
      var items = dropdown.querySelectorAll('.tds-search-dropdown-item');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (items[highlightIdx]) items[highlightIdx].classList.remove('highlighted');
        highlightIdx = (highlightIdx + 1) % items.length;
        if (items[highlightIdx]) { items[highlightIdx].classList.add('highlighted'); items[highlightIdx].scrollIntoView({ block: 'nearest' }); }
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (items[highlightIdx]) items[highlightIdx].classList.remove('highlighted');
        highlightIdx = (highlightIdx - 1 + items.length) % items.length;
        if (items[highlightIdx]) { items[highlightIdx].classList.add('highlighted'); items[highlightIdx].scrollIntoView({ block: 'nearest' }); }
      } else if (e.key === 'Enter') {
        e.preventDefault();
        var selected = allOptions[highlightIdx];
        if (selected) { inputEl.value = selected.label; if (onSelect) onSelect(selected); dropdown.classList.remove('open'); }
      } else if (e.key === 'Escape') {
        dropdown.classList.remove('open');
      }
    });

    document.addEventListener('click', function (e) {
      if (!inputEl.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
      }
    });

    return { close: function () { dropdown.classList.remove('open'); }, destroy: function () { dropdown.remove(); } };
  }

  // ---------------------------------------------------------------------------
  // Button Ripple Effect
  // ---------------------------------------------------------------------------
  function initRippleEffect() {
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('.tds-btn');
      if (!btn) return;
      var circle = document.createElement('span');
      circle.classList.add('ripple-circle');
      var rect = btn.getBoundingClientRect();
      var size = Math.max(rect.width, rect.height);
      circle.style.width = circle.style.height = size + 'px';
      circle.style.left = (e.clientX - rect.left - size / 2) + 'px';
      circle.style.top = (e.clientY - rect.top - size / 2) + 'px';
      btn.appendChild(circle);
      setTimeout(function () { circle.remove(); }, 500);
    });
  }

  // ---------------------------------------------------------------------------
  // Expose Global Functions
  // ---------------------------------------------------------------------------
  window.TDS = {
    api: api,
    showToast: showToast,
    showModal: showModal,
    closeModal: closeModal,
    openDrawer: openDrawer,
    closeDrawer: closeDrawer,
    navigateTo: navigateTo,
    downloadExcel: downloadExcel,
    get user() { return APP.user; },
    get token() { return APP.token; },
  };

  // ---------------------------------------------------------------------------
  // App Init
  // ---------------------------------------------------------------------------
  async function init() {
    var authed = await checkAuth();
    if (!authed) return;

    initSidebar();
    initTopbar();
    initRippleEffect();
    initGlobalSearch();

    window.addEventListener('hashchange', handleRoute);
    window.addEventListener('resize', dashboardHandleResize);

    if (!window.location.hash) {
      window.location.hash = '#/dashboard';
    } else {
      handleRoute();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
