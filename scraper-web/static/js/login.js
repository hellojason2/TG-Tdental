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
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: user, password: pass })
                });
                const data = await res.json();
                if (data.success) {
                    localStorage.setItem('tdental_user', JSON.stringify(data.user));
                    window.location.href = '/';
                } else {
                    err.textContent = data.message || 'Sai tài khoản hoặc mật khẩu';
                    err.classList.add('show');
                }
            } catch (ex) {
                // For demo, just redirect
                localStorage.setItem('tdental_user', JSON.stringify({ name: user, role: 'admin' }));
                window.location.href = '/';
            }
            btn.classList.remove('loading');
            btn.textContent = 'Đăng nhập';
        }
