/* ==========================================================================
   TDental SPA - Main Application
   ========================================================================== */

(function () {
  'use strict';

  var TODAY_ISO = formatDateInput(new Date());
  var MONTH_START_ISO = formatDateInput(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
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
      dateFrom: MONTH_START_ISO,
      dateTo: TODAY_ISO,
      rowsByTab: {},
      requestId: 0,
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
      activeTab: 'overview',
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
      items: [],
      loading: false,
      requestId: 0,
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
      dateFrom: MONTH_START_ISO,
      dateTo: TODAY_ISO,
      paymentType: '',
      items: [],
      loading: false,
      requestId: 0,
    },
    commission: {
      search: '',
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
      dateFrom: MONTH_START_ISO,
      dateTo: TODAY_ISO,
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
    settings: {
      tab: 'users',
      search: '',
      users: null,
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
    '#/categories': { title: 'Danh mục', page: 'categories', render: renderCategories },
    '#/settings': { title: 'Cài đặt', page: 'settings', render: renderSettings },
  };

  // ---------------------------------------------------------------------------
  // API Helper
  // ---------------------------------------------------------------------------
  async function api(endpoint, options) {
    options = options || {};
    var headers = Object.assign({ 'Content-Type': 'application/json' }, options.headers || {});
    var token = localStorage.getItem('token');
    if (token) {
      headers.Authorization = 'Bearer ' + token;
    }
    var fetchOpts = Object.assign({}, options, { headers: headers });
    delete fetchOpts.raw;

    try {
      var res = await fetch(endpoint, fetchOpts);
      if (res.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
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
      '<button class="toast-close" title="Đóng">&times;</button>';

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
  function initSidebar() {
    var sidebar = document.getElementById('sidebar');
    var toggleBtn = document.getElementById('sidebar-toggle');
    var backdrop = document.getElementById('sidebar-backdrop');

    // Mobile toggle
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        var isOpen = sidebar.classList.contains('mobile-open');
        sidebar.classList.toggle('mobile-open', !isOpen);
        backdrop.style.display = isOpen ? 'none' : 'block';
      });
    }

    if (backdrop) {
      backdrop.addEventListener('click', function () {
        sidebar.classList.remove('mobile-open');
        backdrop.style.display = 'none';
      });
    }

    // Nav item click handlers (direct links only, not sub-menu items)
    var navItems = document.querySelectorAll('.sidebar-nav-item');
    for (var i = 0; i < navItems.length; i++) {
      (function (item) {
        // For items WITHOUT sub-menus, click navigates directly
        if (!item.classList.contains('has-submenu')) {
          item.addEventListener('click', function (e) {
            e.preventDefault();
            var route = this.getAttribute('data-route');
            if (route) navigateTo(route);
          });
        }

        // For items WITH sub-menus, hover shows the popup with a delay
        if (item.classList.contains('has-submenu')) {
          var showTimer = null;
          var hideTimer = null;

          function showSubmenu() {
            clearTimeout(hideTimer);
            showTimer = setTimeout(function () {
              item.classList.add('submenu-open');
            }, 50);
          }

          function hideSubmenu() {
            clearTimeout(showTimer);
            hideTimer = setTimeout(function () {
              item.classList.remove('submenu-open');
            }, 150);
          }

          item.addEventListener('mouseenter', showSubmenu);
          item.addEventListener('mouseleave', hideSubmenu);

          // Also clicking the icon navigates to default route
          item.querySelector('.nav-icon').addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            var route = item.getAttribute('data-route');
            if (route) navigateTo(route);
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
        // Close submenu
        var parent = this.closest('.has-submenu');
        if (parent) parent.classList.remove('submenu-open');
      });
    }
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

    // Branch button opens hidden selector
    var branchBtn = document.getElementById('branch-btn');
    var branchSelector = document.getElementById('branch-selector');
    if (branchBtn && branchSelector) {
      branchBtn.addEventListener('click', function () {
        // Toggle a dropdown or show the selector
        branchSelector.style.display = branchSelector.style.display === 'none' ? 'block' : 'none';
        branchSelector.style.position = 'absolute';
        branchSelector.style.top = '40px';
        branchSelector.style.right = '0';
        branchSelector.style.width = '200px';
        branchSelector.style.opacity = '1';
        branchSelector.style.pointerEvents = 'auto';
        branchSelector.style.zIndex = '200';
        branchSelector.style.height = 'auto';
        if (branchSelector.style.display === 'block') {
          branchSelector.focus();
        }
      });
      branchSelector.addEventListener('change', function () {
        var label = document.getElementById('branch-label');
        if (label) {
          var selected = branchSelector.options[branchSelector.selectedIndex];
          label.textContent = selected && selected.value ? selected.textContent : 'Chi nhánh';
        }
        branchSelector.style.display = 'none';
      });
      branchSelector.addEventListener('blur', function () {
        setTimeout(function () { branchSelector.style.display = 'none'; }, 150);
      });
    }

    // F2 shortcut for search focus
    document.addEventListener('keydown', function (e) {
      if (e.key === 'F2') {
        e.preventDefault();
        var searchInput = document.getElementById('topbar-search-input');
        if (searchInput) searchInput.focus();
      }
    });

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
    if (!selector) return;

    var savedBranch = localStorage.getItem('selected_branch') || '';
    selector.innerHTML = '<option value="">Tất cả chi nhánh</option>';

    try {
      var data = await api('/api/companies?limit=0');
      var branches = Array.isArray(data) ? data : safeItems(data);
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

    if (!selector._boundChange) {
      selector.addEventListener('change', function () {
        localStorage.setItem('selected_branch', this.value);
        loadNotificationCount();
        var route = routes[APP.currentRoute];
        if (route && typeof route.render === 'function') route.render();
      });
      selector._boundChange = true;
    }
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

    listEl.innerHTML = APP.notifications.items.map(function (item) {
      var title = escapeHtml(item.title || item.subject || 'Thông báo');
      var preview = escapeHtml(item.preview || item.content || '');
      var dateText = formatDateTime(item.createdAt || item.date);
      var stateClass = item.isRead ? 'read' : 'unread';
      return (
        '<div class="notif-item ' + stateClass + '">' +
        '<div class="notif-item-title">' + title + '</div>' +
        '<div class="notif-item-preview">' + preview + '</div>' +
        '<div class="notif-item-meta">' + escapeHtml(dateText) + '</div>' +
        '</div>'
      );
    }).join('');
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
      } else if (!APP.user) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        return false;
      }
    } catch (_e) {
      if (!APP.user) {
        localStorage.removeItem('token');
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
      '<div class="db-grid">' +
      '<div class="db-left"><div class="db-panel" style="padding:32px;text-align:center">' +
      '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải dữ liệu cho ' + escapeHtml(branchName) + '...</span></div>' +
      '</div></div>' +
      '<div class="db-right"></div>' +
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

    var result = await Promise.all([summaryPromise, receptionPromise, servicesPromise]);
    var summary = result[0];
    var reception = result[1];
    var services = result[2];

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

    return {
      branchId: branchId || '',
      branchName: branchName || 'Tất cả chi nhánh',
      fetchedAt: new Date(),
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
    user: '<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    doctor: '<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    clock: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    phone: '<svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    edit: '<svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
    trash: '<svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
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

    return (
      '<div class="db-grid">' +

      /* ===== LEFT COLUMN ===== */
      '<div class="db-left">' +

      /* -- Reception panel -- */
      '<div class="db-panel db-reception-panel">' +
      '<div class="db-panel-head">' +
      '<span class="db-panel-title">Tiếp nhận khách hàng</span>' +
      '<div class="db-panel-actions">' +
      '<button class="db-icon-btn" id="db-rec-add" title="Thêm">' + DB_SVG.plus + '</button>' +
      '<div class="db-search-wrap">' + DB_SVG.search +
      '<input id="db-rec-search" placeholder="Tìm kiếm theo họ tên, sđt">' +
      '</div>' +
      '<button class="db-icon-btn" id="db-rec-refresh" title="Làm mới">' + DB_SVG.refresh + '</button>' +
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
      '<button class="db-icon-btn" id="db-appt-refresh" title="Làm mới">' + DB_SVG.refresh + '</button>' +
      '</div>' +
      '</div>' +
      '<div class="db-panel-head" style="padding-top:4px">' +
      '<div class="db-search-wrap" style="flex:1">' + DB_SVG.search +
      '<input id="db-appt-search" placeholder="Tìm kiếm theo bác sĩ, họ tên, sđt">' +
      '</div>' +
      '</div>' +
      '<div class="db-tabs" id="db-appt-tabs">' +
      dbBuildApptTabs(allCards) +
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

      '</div>' /* end .db-grid */
    );
  }

  function dbBuildReceptionCards(items) {
    if (!items || !items.length) return '<div class="db-empty">Không có bệnh nhân trong ngày</div>';
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
    if (!items || !items.length) return '<div class="db-empty">Không có lịch hẹn trong ngày</div>';
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
      '<div class="db-acard" data-appt-state="' + escapeHtml(stateClass) + '" data-name="' + escapeHtml(name.toLowerCase()) + '" data-doctor="' + escapeHtml(doctor.toLowerCase()) + '" data-phone="' + escapeHtml(phone.toLowerCase()) + '">' +
      '<div class="db-acard-top">' +
      '<div class="db-acard-patient">' +
      '<img class="db-acard-avatar" src="data:image/svg+xml,' + encodeURIComponent('<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'%2394A3B8\'><circle cx=\'12\' cy=\'8\' r=\'4\'/><path d=\'M20 21a8 8 0 1 0-16 0\'/></svg>') + '">' +
      '<a href="#/partners/customers/' + escapeHtml(patientId) + '/overview">' + escapeHtml(name) + '</a>' +
      '</div>' +
      '<div class="db-acard-actions">' +
      '<button class="db-icon-btn" title="Chỉnh sửa">' + DB_SVG.edit + '</button>' +
      '<button class="db-icon-btn" title="Xóa">' + DB_SVG.trash + '</button>' +
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
      html += '<tr><td colspan="6" style="text-align:center;padding:24px;color:var(--tds-text-muted)">Chưa có dịch vụ trong ngày</td></tr>';
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
    if (tab === 'all') return all;
    return all.filter(function (item) {
      return getPartnerStatus(item) === tab;
    });
  }

  function getPartnerTabCounts() {
    var all = APP.partners.items || [];
    var counts = { all: all.length, treating: 0, new: 0, inactive: 0 };
    for (var i = 0; i < all.length; i++) {
      var s = getPartnerStatus(all[i]);
      counts[s] = (counts[s] || 0) + 1;
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
      { key: 'new', label: 'Mới', count: counts.new },
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
    if (!filtered.length) {
      tableWrap.innerHTML = renderEmptyState('Chưa có dữ liệu khách hàng');
      return;
    }

    var pageSize = APP.partners.pageSize;
    var page = APP.partners.page;
    var start = (page - 1) * pageSize;
    var end = Math.min(start + pageSize, filtered.length);
    var rows = filtered.slice(start, end);

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table partners-table">' +
      '<thead><tr>' +
      '<th>Mã số KH</th><th>Họ tên</th><th>Điện thoại</th><th>Ngày sinh</th>' +
      '<th>Ngày hẹn gần nhất</th><th>Ngày hẹn sắp tới</th>' +
      '<th>Ngày điều trị gần nhất</th><th>Tổng điều trị</th>' +
      '<th>Quỹ tích lũy</th><th class="text-right">Công nợ</th>' +
      '<th class="text-right">Tổng yêu cầu điều trị</th><th class="text-right">Thanh toán</th>' +
      '</tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        var status = getPartnerStatus(item);
        var statusLabel = getPartnerStatusLabel(status);
        var statusClass = getPartnerStatusClass(status);
        var nameDisplay = item.name || item.displayName || 'N/A';
        var initials = getUserInitials(nameDisplay);
        var avatarColor = status === 'treating' ? '#1A6DE3' : status === 'new' ? '#10B981' : '#94A3B8';
        return (
          '<tr class="partners-row" data-id="' + escapeHtml(item.id || '') + '">' +
          '<td class="partners-cell-ref">' + escapeHtml(item.ref || '—') + '</td>' +
          '<td><div class="partners-name-cell"><span class="partners-avatar-sm" style="background:' + avatarColor + '">' + escapeHtml(initials) + '</span><a href="#/partners/customers/' + encodeURIComponent(item.id || '') + '" class="partners-name-link">' + escapeHtml(nameDisplay) + '</a></div></td>' +
          '<td>' + escapeHtml(item.phone || '—') + '</td>' +
          '<td>' + escapeHtml(formatDate(item.dateOfBirth)) + '</td>' +
          '<td>' + escapeHtml(formatDate(item.lastAppointmentDate || item.lastVisitDate || item.lastExamDate)) + '</td>' +
          '<td>' + escapeHtml(formatDate(item.nextAppointmentDate)) + '</td>' +
          '<td>' + escapeHtml(formatDate(item.lastTreatmentDate || item.lastOrderDate)) + '</td>' +
          '<td><span class="partners-badge ' + statusClass + '">' + escapeHtml(statusLabel) + '</span></td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.loyaltyPoints || 0)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.totalDebit || 0)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.amountTreatmentTotal || 0)) + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.amountRevenueTotal || item.amountPaidTotal || 0)) + '</td>' +
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
        var id = this.getAttribute('data-id');
        if (id) navigateTo('#/partners/customers/' + encodeURIComponent(id));
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
      paginationWrap.innerHTML = '';
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
      '<span>' + start + '-' + end + ' của ' + total + ' dòng</span>' +
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
    APP.customerDetail.activeTab = 'overview';
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
    h += '</div>';
    h += '<div class="cdetail-main"><div class="cdetail-content">';
    h += '<div class="cdetail-tabs" id="cdetail-tabs">';
    var tabList = [['overview','Hồ sơ'],['appointments','Lịch hẹn'],['teeth','Tình trạng răng'],['quotation','Báo giá'],['treatments','Phiếu điều trị'],['exams','Đợt khám'],['labo','Labo'],['images','Hình ảnh'],['advance','Tạm ứng'],['debt','Sổ công nợ']];
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
    if (addTreatmentBtn) addTreatmentBtn.addEventListener('click', function () { showToast('info', 'Chức năng tạo phiếu điều trị đang được phát triển'); });
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
    if (tab === 'overview') {
      var toolbarHtml = '<div class="cdetail-overview-toolbar">' +
        '<h3 class="cdetail-section-title">Lịch sử điều trị</h3>' +
        '<div class="cdetail-toolbar-actions">' +
        '<button class="cdetail-toolbar-btn cdetail-toolbar-btn-active" title="Danh sách"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg></button>' +
        '<button class="cdetail-toolbar-btn" title="Lưới"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg></button>' +
        '<button class="cdetail-toolbar-btn" title="Xuất"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>' +
        '<span class="cdetail-toolbar-sep"></span>' +
        '<span class="cdetail-toolbar-link">In hồ sơ điều trị</span>' +
        '</div></div>';
      if (treatments.length) {
        panel.innerHTML = toolbarHtml + '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ngày</th><th>Dịch vụ</th><th>Số lượng</th><th>Thành tiền</th><th>Thanh toán</th><th>Còn lại</th><th>Răng & chẩn đoán</th><th>Bác sĩ</th><th>Trạng thái</th></tr></thead><tbody>' + treatments.map(function (t) { var lines = safeItems(t.lines || t.lineItems || []); var sn = lines.length ? (lines[0].name || lines[0].productName || '—') : '—'; var qtyDisplay = lines.length ? ((lines[0].quantity || 0) + (lines[0].teethCount ? ' Răng' : '')) : '—'; var teethInfo = (t.teeth || t.toothDiagnosis || '---'); var soRef = t.name || t.ref || ''; return '<tr><td><div>' + escapeHtml(formatDate(t.date || t.orderDate || t.createdAt)) + '</div>' + (soRef ? '<div class="cdetail-so-link">' + escapeHtml(soRef) + '</div>' : '') + '</td><td>' + escapeHtml(sn) + '</td><td>' + escapeHtml(qtyDisplay) + '</td><td class="text-right">' + escapeHtml(formatCurrency(t.totalAmount || t.amountTotal || 0)) + '</td><td class="text-right">' + escapeHtml(formatCurrency(t.paidAmount || t.amountPaid || 0)) + '</td><td class="text-right">' + escapeHtml(formatCurrency((t.totalAmount || t.amountTotal || 0) - (t.paidAmount || t.amountPaid || 0))) + '</td><td>' + escapeHtml(teethInfo) + '</td><td>' + escapeHtml(t.doctorName || '—') + '</td><td><span class="partners-badge partners-badge-blue">' + escapeHtml(t.state || t.status || '—') + '</span></td></tr>'; }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = toolbarHtml + renderEmptyState('Chưa có phiếu điều trị'); }
    } else if (tab === 'treatments') {
      if (treatments.length) {
        panel.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Mã phiếu</th><th>Ngày</th><th>Trạng thái</th><th class="text-right">Tổng tiền</th><th class="text-right">Đã TT</th></tr></thead><tbody>' + treatments.map(function (t) { return '<tr><td>' + escapeHtml(t.name || t.ref || '—') + '</td><td>' + escapeHtml(formatDate(t.date || t.orderDate || t.createdAt)) + '</td><td>' + escapeHtml(t.state || '—') + '</td><td class="text-right">' + escapeHtml(formatCurrency(t.totalAmount || t.amountTotal || 0)) + '</td><td class="text-right">' + escapeHtml(formatCurrency(t.paidAmount || t.amountPaid || 0)) + '</td></tr>'; }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = renderEmptyState('Chưa có phiếu điều trị'); }
    } else if (tab === 'appointments') {
      if (appointments.length) {
        panel.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ngày hẹn</th><th>Bác sĩ</th><th>Trạng thái</th><th>Ghi chú</th></tr></thead><tbody>' + appointments.map(function (a) { return '<tr><td>' + escapeHtml(formatDate(a.appointmentDate || a.date)) + '</td><td>' + escapeHtml(a.doctorName || '—') + '</td><td>' + escapeHtml(a.state || a.status || '—') + '</td><td>' + escapeHtml(a.notes || a.note || '—') + '</td></tr>'; }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = renderEmptyState('Chưa có lịch hẹn'); }
    } else if (tab === 'payments') {
      if (payments.length) {
        panel.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ngày</th><th>Loại</th><th class="text-right">Số tiền</th><th>Sổ quỹ</th><th>Trạng thái</th></tr></thead><tbody>' + payments.map(function (p) { return '<tr><td>' + escapeHtml(formatDate(p.date)) + '</td><td>' + escapeHtml(normalizePaymentTypeLabel(p.paymentType)) + '</td><td class="text-right">' + escapeHtml(formatCurrency(p.amount || 0)) + '</td><td>' + escapeHtml(p.journalName || '—') + '</td><td>' + escapeHtml(p.state || '—') + '</td></tr>'; }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = renderEmptyState('Chưa có lịch sử thanh toán'); }
    } else if (tab === 'exams') {
      var exams = APP.customerDetail.exams || [];
      if (exams.length) {
        panel.innerHTML = '<div class="tds-table-wrapper"><table class="tds-table"><thead><tr><th>Ngày khám</th><th>Bác sĩ</th><th>Chẩn đoán</th><th>Ghi chú</th><th>Trạng thái</th></tr></thead><tbody>' + exams.map(function (e) { return '<tr><td>' + escapeHtml(formatDate(e.date || e.examDate || e.createdAt)) + '</td><td>' + escapeHtml(e.doctorName || '—') + '</td><td>' + escapeHtml(e.diagnosis || e.reason || '—') + '</td><td>' + escapeHtml(e.notes || e.note || '—') + '</td><td>' + escapeHtml(e.state || e.status || '—') + '</td></tr>'; }).join('') + '</tbody></table></div>';
      } else { panel.innerHTML = renderEmptyState('Chưa có đợt khám'); }
    } else {
      var labels = { images: 'Hình ảnh', debt: 'Sổ công nợ', teeth: 'Tình trạng răng', quotation: 'Báo giá', labo: 'Labo', advance: 'Tạm ứng' };
      panel.innerHTML = renderEmptyState('Chức năng "' + (labels[tab] || tab) + '" đang được phát triển');
    }
  }

  function renderCDTimeline() {
    var timeline = document.getElementById('cdetail-timeline');
    if (!timeline) return;
    var events = [];
    (APP.customerDetail.treatments || []).forEach(function (t) { events.push({ date: t.date || t.orderDate || t.createdAt || '', type: 'treatment', title: 'Phiếu điều trị', desc: (t.name || t.ref || '') + ' - ' + formatCurrency(t.totalAmount || t.amountTotal || 0), author: t.createdBy || t.doctorName || '' }); });
    (APP.customerDetail.payments || []).forEach(function (p) { events.push({ date: p.date || p.createdAt || '', type: 'payment', title: 'Thanh toán', desc: formatCurrency(p.amount || 0), author: p.createdBy || '' }); });
    (APP.customerDetail.appointments || []).forEach(function (a) { events.push({ date: a.appointmentDate || a.date || a.createdAt || '', type: 'appointment', title: 'Lịch hẹn', desc: (a.doctorName ? 'BS: ' + a.doctorName : '') + (a.notes || a.note ? ' - ' + (a.notes || a.note) : ''), author: a.createdBy || '' }); });
    events.sort(function (a, b) { return (b.date || '').localeCompare(a.date || ''); });
    if (!events.length) { timeline.innerHTML = '<div class="cdetail-timeline-empty">Chưa có hoạt động</div>'; return; }
    var grouped = {};
    events.forEach(function (ev) { var dk = (ev.date || '').slice(0, 10) || 'unknown'; if (!grouped[dk]) grouped[dk] = []; grouped[dk].push(ev); });
    var html = '';
    Object.keys(grouped).sort(function (a, b) { return b.localeCompare(a); }).forEach(function (dk) {
      var dayLabel = dk === new Date().toISOString().slice(0, 10) ? 'Hôm nay' : formatDate(dk);
      html += '<div class="cdetail-timeline-group"><div class="cdetail-timeline-date">' + escapeHtml(dayLabel) + '</div>';
      grouped[dk].forEach(function (ev) {
        var ic = ev.type === 'payment' ? '#8B5CF6' : ev.type === 'treatment' ? '#1A6DE3' : '#F59E0B';
        html += '<div class="cdetail-timeline-item"><div class="cdetail-timeline-dot" style="background:' + ic + '"></div><div class="cdetail-timeline-content"><div class="cdetail-timeline-time">' + escapeHtml((ev.date || '').slice(11, 16) || '') + '</div><div class="cdetail-timeline-title">' + escapeHtml(ev.title) + '</div><div class="cdetail-timeline-desc">' + escapeHtml(ev.desc) + '</div>' + (ev.author ? '<div class="cdetail-timeline-author">Người tạo: ' + escapeHtml(ev.author) + '</div>' : '') + '</div></div>';
      });
      html += '</div>';
    });
    timeline.innerHTML = html;
  }

  // ---------------------------------------------------------------------------
  // Customer Create / Edit Modal (T-021)
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
    if (!window.confirm('Xóa tác vụ này?')) return;

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
    var state = getReceptionViewState();
    state.companyId = getSelectedBranchId();

    el.innerHTML =
      '<section class="tds-card reception-page">' +
      '<div class="reception-toolbar">' +
      '<div class="reception-toolbar-main">' +
      '<h2>Tiếp nhận trong ngày</h2>' +
      '<p class="text-secondary">Luồng điều phối: Chờ khám → Đang khám → Hoàn thành</p>' +
      '</div>' +
      '<div class="reception-toolbar-actions">' +
      '<button class="tds-btn tds-btn-secondary tds-btn-icon" data-reception-nav="prev" title="Ngày trước">&lsaquo;</button>' +
      '<button class="tds-btn tds-btn-secondary" data-reception-nav="today">Hôm nay</button>' +
      '<button class="tds-btn tds-btn-secondary tds-btn-icon" data-reception-nav="next" title="Ngày sau">&rsaquo;</button>' +
      '<span class="reception-date-label" id="reception-date-label"></span>' +
      '</div>' +
      '</div>' +
      '<div class="reception-summary" id="reception-summary"></div>' +
      '<div id="reception-board">' + renderLoadingState('Đang tải lịch tiếp nhận...') + '</div>' +
      '</section>';

    bindReceptionInteractions(el);
    loadReceptionBoardData();
  }

  function renderCalendar() {
    var el = document.getElementById('page-calendar');
    if (!el) return;
    var state = getCalendarViewState();
    state.companyId = getSelectedBranchId();

    el.innerHTML =
      '<section class="tds-card calendar-page">' +
      '<div class="calendar-toolbar">' +
      '<div class="calendar-toolbar-left">' +
      '<div class="calendar-view-switch">' +
      '<button class="tds-btn tds-btn-sm ' + (state.view === 'day' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-view="day">Ngày</button>' +
      '<button class="tds-btn tds-btn-sm ' + (state.view === 'week' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-view="week">Tuần</button>' +
      '<button class="tds-btn tds-btn-sm ' + (state.view === 'month' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-view="month">Tháng</button>' +
      '</div>' +
      '<div class="calendar-segment-switch">' +
      '<button class="tds-btn tds-btn-sm ' + (state.segment === 'all' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-segment="all">Tất cả</button>' +
      '<button class="tds-btn tds-btn-sm ' + (state.segment === 'morning' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-segment="morning">Sáng</button>' +
      '<button class="tds-btn tds-btn-sm ' + (state.segment === 'afternoon' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-segment="afternoon">Chiều</button>' +
      '<button class="tds-btn tds-btn-sm ' + (state.segment === 'evening' ? 'tds-btn-primary' : 'tds-btn-secondary') + '" data-calendar-segment="evening">Tối</button>' +
      '</div>' +
      '</div>' +
      '<div class="calendar-toolbar-actions">' +
      '<button class="tds-btn tds-btn-secondary tds-btn-icon" data-calendar-nav="prev" title="Trước">&lsaquo;</button>' +
      '<button class="tds-btn tds-btn-secondary" data-calendar-nav="today">Hôm nay</button>' +
      '<button class="tds-btn tds-btn-secondary tds-btn-icon" data-calendar-nav="next" title="Sau">&rsaquo;</button>' +
      '<span class="calendar-date-label" id="calendar-date-label"></span>' +
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
      body.innerHTML = renderErrorState('Không tải được dữ liệu lịch hẹn.');
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
    if (!data) return renderErrorState('Không có dữ liệu lịch hẹn.');
    var state = getCalendarViewState();
    var startHour = Number(data.startHour) || 7;
    var endHour = Number(data.endHour) || 21;
    var pxPerMinute = 1.05;
    var hourHeight = 60 * pxPerMinute;
    var timelineHeight = Math.max((endHour - startHour) * hourHeight, 380);

    var columns = [];
    for (var i = 0; i < data.doctors.length; i++) {
      var docAppts = filterAppointmentsBySegment(data.doctors[i].appointments, state.segment);
      columns.push({
        name: data.doctors[i].doctorName || 'Bác sĩ',
        appointments: docAppts,
        count: docAppts.length,
      });
    }
    var unassigned = filterAppointmentsBySegment(data.unassigned, state.segment);
    if (unassigned.length) {
      columns.push({ name: 'Không xác định', appointments: unassigned, count: unassigned.length });
    }

    if (!columns.length) {
      return renderEmptyState('Không có lịch hẹn trong ngày đã chọn.');
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
    if (!data || !Array.isArray(data.days)) {
      return renderErrorState('Không có dữ liệu lịch tuần.');
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
      return renderEmptyState('Không có lịch hẹn trong tuần đã chọn.');
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
    if (!data || !Array.isArray(data.cells)) {
      return renderErrorState('Không có dữ liệu lịch tháng.');
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
      '<div class="tds-card labo-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Danh sách phiếu điều trị / Labo</h2>' +
      '<button class="tds-btn tds-btn-secondary" id="labo-export-btn">Xuất Excel</button>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="labo-search" placeholder="Tìm theo mã phiếu, khách hàng, bác sĩ" value="' + escapeHtml(APP.labo.search || '') + '">' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-secondary" id="labo-refresh-btn">Làm mới</button>' +
      '</div>' +
      '</div>' +
      '<div id="labo-table"></div>' +
      '</div>';

    var searchInput = document.getElementById('labo-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.labo.search = searchInput.value.trim();
        loadLaboData();
      }, 250));
    }

    var refreshBtn = document.getElementById('labo-refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', loadLaboData);

    var exportBtn = document.getElementById('labo-export-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        downloadExcel('sale-orders', {
          search: APP.labo.search,
          companyId: getSelectedBranchId(),
          columns: ['name', 'date', 'state', 'amountTotal', 'partnerName', 'doctorName', 'companyName'],
        });
      });
    }

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
        companyId: getSelectedBranchId(),
        limit: 50,
        offset: 0,
      });
      var data = await api('/api/sale-orders' + query);
      if (requestId !== APP.labo.requestId) return;
      APP.labo.items = safeItems(data);
    } catch (_err) {
      if (requestId !== APP.labo.requestId) return;
      APP.labo.items = [];
    } finally {
      if (requestId === APP.labo.requestId) {
        APP.labo.loading = false;
        renderLaboTable();
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
      tableWrap.innerHTML = renderEmptyState('Chưa có dữ liệu phiếu điều trị');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr><th>Mã phiếu</th><th>Ngày</th><th>Khách hàng</th><th>Bác sĩ</th><th>Trạng thái</th><th class="text-right">Giá trị</th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(item.name || item.id || '—') + '</td>' +
          '<td>' + escapeHtml(formatDate(item.date)) + '</td>' +
          '<td>' + escapeHtml(item.partnerName || '—') + '</td>' +
          '<td>' + escapeHtml(item.doctorName || '—') + '</td>' +
          '<td>' + escapeHtml(item.state || '—') + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.amountTotal || 0)) + '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';
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
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(item.name || item.id || '—') + '</td>' +
          '<td>' + escapeHtml(formatDate(item.date)) + '</td>' +
          '<td>' + escapeHtml(normalizePickingTypeLabel(item.pickingType)) + '</td>' +
          '<td>' + escapeHtml(item.partnerName || '—') + '</td>' +
          '<td>' + escapeHtml(item.companyName || '—') + '</td>' +
          '<td>' + escapeHtml(item.state || '—') + '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';
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
      rows.map(function (item) {
        return (
          '<tr>' +
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
      '<thead><tr><th>Ngày</th><th>Chứng từ</th><th>Đối tượng</th><th>Loại</th><th>Trạng thái</th><th>Chi nhánh</th><th class="text-right">Số tiền</th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(formatDate(item.date)) + '</td>' +
          '<td>' + escapeHtml(item.name || '—') + '</td>' +
          '<td>' + escapeHtml(item.partnerName || '—') + '</td>' +
          '<td>' + escapeHtml(normalizePaymentTypeLabel(item.paymentType)) + '</td>' +
          '<td>' + escapeHtml(item.state || '—') + '</td>' +
          '<td>' + escapeHtml(item.companyName || '—') + '</td>' +
          '<td class="text-right">' + escapeHtml(formatCurrency(item.amount || 0)) + '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';
  }

  function renderCommission() {
    var el = document.getElementById('page-commission');
    if (!el) return;

    el.innerHTML =
      '<div class="tds-card commission-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Quản lý hoa hồng</h2>' +
      '<button class="tds-btn tds-btn-primary" id="commission-add-btn">Thêm quy tắc</button>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-search-input" id="commission-search" placeholder="Tìm theo tên quy tắc" value="' + escapeHtml(APP.commission.search || '') + '">' +
      '</div>' +
      '<div class="toolbar-right">' +
      '<button class="tds-btn tds-btn-secondary" id="commission-refresh-btn">Làm mới</button>' +
      '</div>' +
      '</div>' +
      '<div id="commission-table"></div>' +
      '</div>';

    var searchInput = document.getElementById('commission-search');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        APP.commission.search = searchInput.value.trim();
        loadCommissionData();
      }, 250));
    }

    var refreshBtn = document.getElementById('commission-refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', loadCommissionData);

    var addBtn = document.getElementById('commission-add-btn');
    if (addBtn) {
      addBtn.addEventListener('click', function () {
        openCommissionModal(null);
      });
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
      tableWrap.innerHTML = renderLoadingState('Đang tải quy tắc hoa hồng...');
      return;
    }

    var rows = APP.commission.items || [];
    if (!rows.length) {
      tableWrap.innerHTML = renderEmptyState('Chưa có quy tắc hoa hồng');
      return;
    }

    tableWrap.innerHTML =
      '<div class="tds-table-wrapper">' +
      '<table class="tds-table">' +
      '<thead><tr><th>Tên quy tắc</th><th>Loại</th><th>Trạng thái</th><th>Mô tả</th><th>Cập nhật</th><th></th></tr></thead>' +
      '<tbody>' +
      rows.map(function (item) {
        return (
          '<tr>' +
          '<td>' + escapeHtml(item.name || 'N/A') + '</td>' +
          '<td>' + escapeHtml(item.type || '—') + '</td>' +
          '<td>' + (item.active ? '<span class="tds-badge tds-badge-success">Hoạt động</span>' : '<span class="tds-badge tds-badge-gray">Tạm khóa</span>') + '</td>' +
          '<td>' + escapeHtml(item.description || '—') + '</td>' +
          '<td>' + escapeHtml(formatDateTime(item.lastUpdated || item.dateCreated)) + '</td>' +
          '<td class="text-right">' +
          '<button class="tds-btn tds-btn-sm tds-btn-secondary commission-edit" data-id="' + escapeHtml(item.id || '') + '">Sửa</button> ' +
          '<button class="tds-btn tds-btn-sm tds-btn-danger commission-delete" data-id="' + escapeHtml(item.id || '') + '">Xóa</button>' +
          '</td>' +
          '</tr>'
        );
      }).join('') +
      '</tbody>' +
      '</table>' +
      '</div>';

    var editBtns = tableWrap.querySelectorAll('.commission-edit');
    for (var i = 0; i < editBtns.length; i++) {
      editBtns[i].addEventListener('click', function () {
        var id = this.getAttribute('data-id');
        var row = findItemById(APP.commission.items || [], id);
        if (!row) return;
        openCommissionModal(row);
      });
    }

    var deleteBtns = tableWrap.querySelectorAll('.commission-delete');
    for (var j = 0; j < deleteBtns.length; j++) {
      deleteBtns[j].addEventListener('click', function () {
        deleteCommissionRule(this.getAttribute('data-id'));
      });
    }
  }

  function openCommissionModal(item) {
    var editing = !!item;
    var content =
      '<form id="commission-form">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tên quy tắc</label>' +
      '<input class="tds-input" id="commission-name-input" required value="' + escapeHtml((item && item.name) || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Loại</label>' +
      '<input class="tds-input" id="commission-type-input" value="' + escapeHtml((item && item.type) || '') + '" placeholder="Ví dụ: doanh_thu / gioi_thieu">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Mô tả</label>' +
      '<textarea class="tds-input" id="commission-description-input" rows="3">' + escapeHtml((item && item.description) || '') + '</textarea>' +
      '</div>' +
      '<label class="tds-checkbox-label"><input type="checkbox" id="commission-active-input" ' + (((item ? item.active : true) !== false) ? 'checked' : '') + '> Kích hoạt</label>' +
      '</form>';

    showModal(editing ? 'Cập nhật hoa hồng' : 'Thêm quy tắc hoa hồng', content, {
      footer:
        '<button class="tds-btn tds-btn-ghost" id="commission-modal-cancel">Hủy</button>' +
        '<button class="tds-btn tds-btn-primary" id="commission-modal-save">' + (editing ? 'Cập nhật' : 'Thêm mới') + '</button>',
      onOpen: function () {
        var cancelBtn = document.getElementById('commission-modal-cancel');
        var saveBtn = document.getElementById('commission-modal-save');
        if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
        if (!saveBtn) return;

        saveBtn.addEventListener('click', async function () {
          var name = getInputValue('commission-name-input');
          if (!name) {
            showToast('warning', 'Tên quy tắc là bắt buộc');
            return;
          }

          var payload = {
            name: name,
            type: getInputValue('commission-type-input') || null,
            description: getInputValue('commission-description-input') || null,
            active: !!(document.getElementById('commission-active-input') || {}).checked,
            companyId: getSelectedBranchId() || null,
          };

          try {
            if (editing && item && item.id) {
              await api('/api/commissions/' + encodeURIComponent(item.id), {
                method: 'PUT',
                body: JSON.stringify(payload),
              });
              showToast('success', 'Đã cập nhật quy tắc hoa hồng');
            } else {
              await api('/api/commissions', {
                method: 'POST',
                body: JSON.stringify(payload),
              });
              showToast('success', 'Đã tạo quy tắc hoa hồng');
            }

            closeModal();
            loadCommissionData();
          } catch (err) {
            showToast('error', (err && err.message) || 'Không thể lưu quy tắc hoa hồng');
          }
        });
      },
    });
  }

  async function deleteCommissionRule(commissionId) {
    if (!commissionId) return;
    if (!window.confirm('Xóa quy tắc hoa hồng này?')) return;

    try {
      await api('/api/commissions/' + encodeURIComponent(commissionId), { method: 'DELETE' });
      showToast('success', 'Đã xóa quy tắc hoa hồng');
      loadCommissionData();
    } catch (err) {
      showToast('error', (err && err.message) || 'Không thể xóa quy tắc hoa hồng');
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

    el.innerHTML =
      '<div class="tds-card salary-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Quản lý lương & nhân sự</h2>' +
      '<div class="salary-actions">' +
      '<button class="tds-btn tds-btn-secondary" id="salary-export-btn">Xuất Excel</button>' +
      '</div>' +
      '</div>' +
      '<div class="tds-table-toolbar">' +
      '<div class="toolbar-left">' +
      '<input class="tds-input salary-date" id="salary-date-from" type="date" value="' + escapeHtml(APP.salary.dateFrom) + '">' +
      '<input class="tds-input salary-date" id="salary-date-to" type="date" value="' + escapeHtml(APP.salary.dateTo) + '">' +
      '<button class="tds-btn tds-btn-primary" id="salary-apply-btn">Áp dụng</button>' +
      '</div>' +
      '</div>' +
      '<div id="salary-content"></div>' +
      '</div>';

    var applyBtn = document.getElementById('salary-apply-btn');
    var exportBtn = document.getElementById('salary-export-btn');

    if (applyBtn) {
      applyBtn.addEventListener('click', function () {
        var fromInput = document.getElementById('salary-date-from');
        var toInput = document.getElementById('salary-date-to');
        APP.salary.dateFrom = fromInput && fromInput.value ? fromInput.value : APP.salary.dateFrom;
        APP.salary.dateTo = toInput && toInput.value ? toInput.value : APP.salary.dateTo;
        loadSalaryData();
      });
    }

    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        downloadExcel('employees', {
          dateFrom: APP.salary.dateFrom,
          dateTo: APP.salary.dateTo,
          companyId: getSelectedBranchId(),
          columns: ['name', 'hrJob', 'companyName', 'monthlySalary', 'allowance', 'commission'],
        });
      });
    }

    loadSalaryData();
  }

  async function loadSalaryData() {
    APP.salary.loading = true;
    APP.salary.requestId += 1;
    var requestId = APP.salary.requestId;

    renderSalaryContentLoading();

    var query = toQueryString({
      dateFrom: APP.salary.dateFrom,
      dateTo: APP.salary.dateTo,
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
      renderSalaryError(err);
    }
  }

  function renderSalaryContentLoading() {
    var content = document.getElementById('salary-content');
    if (!content) return;
    content.innerHTML =
      '<div class="tds-loading"><div class="tds-spinner"></div><span>Đang tải dữ liệu lương...</span></div>';
  }

  function renderSalaryError(err) {
    var content = document.getElementById('salary-content');
    if (!content) return;
    content.innerHTML =
      '<div class="tds-empty">' +
      '<p>' + escapeHtml((err && err.message) || 'Không thể tải dữ liệu lương') + '</p>' +
      '</div>';
  }

  function renderSalaryContent() {
    var content = document.getElementById('salary-content');
    if (!content) return;

    var data = APP.salary.data || {};
    var employees = safeItems(data.employees || []);
    var timekeeping = safeItems(data.timekeeping || []);
    var advances = safeItems(data.advances || []);

    if (!data.hasData) {
      content.innerHTML =
        '<div class="tds-empty salary-empty">' +
        '<p>Chưa có dữ liệu</p>' +
        '<p class="text-secondary mt-sm">Dữ liệu HR trong bản dump hiện chưa khả dụng.</p>' +
        '</div>';
      return;
    }

    content.innerHTML =
      '<div class="salary-block">' +
      '<h3>Nhân sự</h3>' +
      renderSimpleTable(
        ['Tên', 'Chức danh', 'Chi nhánh', 'Lương cơ bản', 'Phụ cấp', 'Hoa hồng'],
        employees.map(function (item) {
          return [
            escapeHtml(item.name || 'N/A'),
            escapeHtml(item.jobTitle || item.hrJob || '—'),
            escapeHtml(item.companyName || '—'),
            '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.monthlySalary)) + '</span>',
            '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.allowance)) + '</span>',
            '<span class="text-right d-block">' + escapeHtml(formatNumber(item.commission || 0)) + '</span>',
          ];
        }),
        'Chưa có nhân sự'
      ) +
      '</div>' +
      '<div class="salary-block">' +
      '<h3>Chấm công</h3>' +
      renderSimpleTable(
        ['Ngày', 'Nhân viên', 'Giờ làm', 'Tăng ca', 'Trạng thái'],
        timekeeping.map(function (item) {
          return [
            escapeHtml(formatDate(item.date)),
            escapeHtml(item.employeeName || 'N/A'),
            '<span class="text-right d-block">' + escapeHtml(formatNumber(item.hours || 0)) + '</span>',
            '<span class="text-right d-block">' + escapeHtml(formatNumber(item.overtime || 0)) + '</span>',
            escapeHtml(item.state || '—'),
          ];
        }),
        'Không có dữ liệu chấm công trong kỳ lọc'
      ) +
      '</div>' +
      '<div class="salary-block">' +
      '<h3>Tạm ứng</h3>' +
      renderSimpleTable(
        ['Ngày', 'Nhân viên', 'Số tiền', 'Lý do', 'Trạng thái'],
        advances.map(function (item) {
          return [
            escapeHtml(formatDate(item.date)),
            escapeHtml(item.employeeName || 'N/A'),
            '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.amount || 0)) + '</span>',
            escapeHtml(item.reason || '—'),
            escapeHtml(item.state || '—'),
          ];
        }),
        'Không có dữ liệu tạm ứng trong kỳ lọc'
      ) +
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
              escapeHtml(item.state || item.status || '—'),
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
              escapeHtml(item.state || item.status || '—'),
              '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.totalAmount || item.amountTotal || 0)) + '</span>',
              '<span class="text-right d-block">' + escapeHtml(formatNumber(lines.length)) + '</span>',
            ];
          }),
          'Chưa có phiếu điều trị'
        ) +
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
              escapeHtml(item.state || '—'),
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
              escapeHtml(item.state || '—'),
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
        '<div class="customer-images-empty">' +
        '<p>Chưa có hình ảnh</p>' +
        '<p class="text-secondary">Tính năng tải ảnh sẽ được bổ sung sau.</p>' +
        '</div>' +
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
      loadDrawerLaboData(customerId);
      loadDrawerAdvanceData(customerId);
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
            escapeHtml(item.state || '—'),
            '<span class="text-right d-block">' + escapeHtml(formatCurrency(item.totalAmount || item.amountTotal || 0)) + '</span>',
          ];
        }),
        'Không có phiếu Labo'
      );
    } catch (_err) {
      panel.innerHTML = renderEmptyState('Không thể tải dữ liệu Labo');
    }
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
            escapeHtml(item.state || '—'),
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
            escapeHtml(info.state),
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
    APP.reports.requestId += 1;
    var requestId = APP.reports.requestId;

    try {
      var query = toQueryString({
        dateFrom: APP.reports.dateFrom,
        dateTo: APP.reports.dateTo,
        companyId: getSelectedBranchId(),
      });
      var summary = null;
      try {
        summary = await api('/api/reports/summary' + query);
      } catch (_e) { summary = null; }

      if (requestId !== APP.reports.requestId) return;

      if (summary) {
        rptUpdateCardValue('cash', summary.cashBalance || summary.cash || 0);
        rptUpdateCardValue('bank', summary.bankBalance || summary.bank || 0);
        rptUpdateCardValue('supplier_debt', summary.supplierDebt || 0);
        rptUpdateCardValue('customer_debt', summary.customerDebt || 0);
        rptUpdateCardValue('insurance_debt', summary.insuranceDebt || 0);
        rptUpdateCardValue('expected', summary.expectedRevenue || summary.revenue || 0);
      }

      var trend = null;
      try {
        trend = await api('/api/reports/revenue-trend' + query);
      } catch (_e) { trend = null; }

      if (requestId !== APP.reports.requestId) return;
      rptDrawRevenueChart(trend);
      rptDrawIncomeExpenseChart(trend);
    } catch (err) {
      if (window.console) console.error('report-overview-error', err);
    }
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

    var incomeVals = items.map(function (r) { return Number(r.income || r.revenue || r.totalAmount || 0); });
    var expenseVals = items.map(function (r) { return Number(r.expense || r.totalExpense || 0); });
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
    var rId = ++APP.reports.requestId;

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
      if (rId !== APP.reports.requestId) return;
      APP.reports.rowsByTab[APP.reports.tab] = safeItems(data);
      APP.reports.loading = false;
      renderReportTable();
    } catch (err) {
      if (rId !== APP.reports.requestId) return;
      APP.reports.loading = false;
      container.innerHTML = '<div class="tds-empty"><p>' + escapeHtml((err && err.message) || 'Không thể tải báo cáo') + '</p></div>';
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
    if (!window.confirm('Xóa danh mục này?')) return;

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

    var activeTab = APP.settings.tab === 'config' ? 'config' : 'users';
    APP.settings.tab = activeTab;

    el.innerHTML =
      '<div class="tds-card settings-shell">' +
      '<div class="tds-card-header">' +
      '<h2>Cài đặt hệ thống</h2>' +
      '</div>' +
      '<div class="settings-tabs">' +
      '<button class="settings-tab-btn ' + (activeTab === 'users' ? 'active' : '') + '" data-settings-tab="users">Tài khoản</button>' +
      '<button class="settings-tab-btn ' + (activeTab === 'config' ? 'active' : '') + '" data-settings-tab="config">Cấu hình</button>' +
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

    if (APP.settings.tab === 'users') {
      renderSettingsUsersLayout();
      loadUsersData();
    } else {
      renderSettingsConfigLayout();
      loadSettingsConfigData();
    }
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
    if (!window.confirm('Xóa tài khoản này?')) return;

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
      var settingsPromise = api('/api/settings');
      var companyPromise = api('/api/companies?limit=0');
      var response = await Promise.all([settingsPromise, companyPromise]);
      if (requestId !== APP.settings.requestId) return;

      APP.settings.config = response[0] || { items: [], map: {} };
      APP.settings.companies = safeItems(response[1]);
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

    container.innerHTML =
      '<form id="settings-config-form" class="settings-config-form">' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tên phòng khám</label>' +
      '<input class="tds-input" id="cfg-clinic-name" value="' + escapeHtml(map.clinic_name || '') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Chi nhánh mặc định</label>' +
      '<select class="tds-select" id="cfg-default-branch">' +
      '<option value="">Không chọn</option>' +
      APP.settings.companies.map(function (company) {
        var value = company.id || '';
        var selected = String(map.default_branch_id || '') === String(value) ? 'selected' : '';
        return '<option value="' + escapeHtml(value) + '" ' + selected + '>' + escapeHtml(company.name || 'N/A') + '</option>';
      }).join('') +
      '</select>' +
      '</div>' +
      '</div>' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Múi giờ</label>' +
      '<input class="tds-input" id="cfg-timezone" value="' + escapeHtml(map.default_timezone || 'Asia/Ho_Chi_Minh') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Tiền tệ</label>' +
      '<input class="tds-input" id="cfg-currency" value="' + escapeHtml(map.default_currency || 'VND') + '">' +
      '</div>' +
      '</div>' +
      '<div class="tds-form-row">' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Khung lịch hẹn (phút)</label>' +
      '<input class="tds-input" id="cfg-slot-minutes" type="number" min="5" value="' + escapeHtml(map.appointment_slot_minutes || '30') + '">' +
      '</div>' +
      '<div class="tds-form-group">' +
      '<label class="tds-label">Bật SMS tự động</label>' +
      '<select class="tds-select" id="cfg-auto-sms">' +
      '<option value="true" ' + ((String(map.auto_sms || 'false') === 'true') ? 'selected' : '') + '>Bật</option>' +
      '<option value="false" ' + ((String(map.auto_sms || 'false') === 'false') ? 'selected' : '') + '>Tắt</option>' +
      '</select>' +
      '</div>' +
      '</div>' +
      '<div class="settings-config-actions">' +
      '<button type="button" class="tds-btn tds-btn-primary" id="settings-apply-btn">Áp dụng</button>' +
      '</div>' +
      '</form>';

    var applyBtn = document.getElementById('settings-apply-btn');
    if (applyBtn) {
      applyBtn.addEventListener('click', saveSettingsConfig);
    }
  }

  async function saveSettingsConfig() {
    var payload = {
      items: [
        { key: 'clinic_name', value: getInputValue('cfg-clinic-name') || '' },
        { key: 'default_branch_id', value: getInputValue('cfg-default-branch') || '' },
        { key: 'default_timezone', value: getInputValue('cfg-timezone') || 'Asia/Ho_Chi_Minh' },
        { key: 'default_currency', value: getInputValue('cfg-currency') || 'VND' },
        { key: 'appointment_slot_minutes', value: getInputValue('cfg-slot-minutes') || '30' },
        { key: 'auto_sms', value: getInputValue('cfg-auto-sms') || 'false' },
      ],
    };

    try {
      await api('/api/settings', {
        method: 'POST',
        body: JSON.stringify(payload),
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
