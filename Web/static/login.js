document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.querySelector('#togglePassword');
    const passwordInput = document.querySelector('#password');
    const loginForm = document.querySelector('#loginForm');
    const loginBtn = document.querySelector('#loginBtn');
    const guestBtn = document.querySelector('#guestBtn');

    if (togglePassword) {
        togglePassword.addEventListener('click', function (e) {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('bx-show');
            this.classList.toggle('bx-hide');
        });
    }

    // Aksi untuk tombol Guest (auto submit form dengan data guest)
    if (guestBtn) {
        guestBtn.addEventListener('click', function() {
            // Mengisi input form secara otomatis
            document.querySelector('#username').value = 'guest';
            document.querySelector('#password').value = 'admin123';
            
            // Animasi loading pada tombol utama
            loginBtn.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Memproses...";
            
            // Nonaktifkan kedua tombol untuk menghindari double-click
            loginBtn.setAttribute('disabled', 'true');
            guestBtn.setAttribute('disabled', 'true');
            
            // Submit form
            loginForm.submit();
        });
    }

    // Aksi submit biasa
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            loginBtn.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Memproses...";
            loginBtn.setAttribute('disabled', 'true');
            if (guestBtn) guestBtn.setAttribute('disabled', 'true');
        });
    }

    // Autoclose Flash Messages
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 500);
            });
        }, 5000);
    }
});