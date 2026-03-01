document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('tambahUserForm');
    const submitBtn = document.getElementById('submitBtn');

    form.addEventListener('submit', function() {
        submitBtn.innerHTML = "Menyimpan...";
        submitBtn.setAttribute('disabled', 'true');
    });

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