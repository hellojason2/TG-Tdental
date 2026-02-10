function togglePassword() {
    const pw = document.getElementById('password');
    pw.type = pw.type === 'password' ? 'text' : 'password';
}

async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('loginBtn');
    const err = document.getElementById('loginError');
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('password').value;

    if (!user || !pass) {
        err.textContent = 'Vui lòng nhập tài khoản và mật khẩu';
        err.classList.add('show');
        return;
    }

    btn.classList.add('loading');
    btn.textContent = 'Đang đăng nhập...';
    err.classList.remove('show');

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: user, password: pass })
        });
        const data = await res.json();

        if (res.ok && data.token) {
            // Set session cookie (30 days, same as server token expiry)
            const d = new Date();
            d.setTime(d.getTime() + 30 * 24 * 60 * 60 * 1000);
            document.cookie = 'tdental_session=' + data.token + ';expires=' + d.toUTCString() + ';path=/;SameSite=Lax';

            // Also store in localStorage for API calls
            localStorage.setItem('tdental_token', data.token);
            localStorage.setItem('tdental_current_user', JSON.stringify(data.user));

            window.location.href = '/';
        } else {
            err.textContent = data.message || 'Sai tài khoản hoặc mật khẩu';
            err.classList.add('show');
        }
    } catch (ex) {
        err.textContent = 'Lỗi kết nối server';
        err.classList.add('show');
    }
    btn.classList.remove('loading');
    btn.textContent = 'Đăng nhập';
}
