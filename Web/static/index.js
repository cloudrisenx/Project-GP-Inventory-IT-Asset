/**
 * Logika interaktif untuk Dashboard Inventory IT Griya Persada
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. LOGIKA DATABASE CHECKING ---
    const dot = document.querySelector('.status-dot');
    const text = document.getElementById('db-status-text');

    async function updateDBStatus() {
        try {
            const response = await fetch('/api/db-check');
            const data = await response.json();
            
            if (data.status === 'online') {
                dot.style.backgroundColor = '#10b981'; // Hijau
                text.innerText = 'Online';
                text.style.color = '#10b981';
            } else {
                dot.style.backgroundColor = '#ef4444'; // Merah
                text.innerText = 'Offline';
                text.style.color = '#ef4444';
            }
        } catch (error) {
            dot.style.backgroundColor = '#ef4444';
            text.innerText = 'Error';
        }
    }

    // Jalankan saat pertama kali load
    updateDBStatus();
    // Cek setiap 15 detik
    setInterval(updateDBStatus, 15000);

    // --- 2. LOGIKA TOGGLE THEME ---
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    const htmlElement = document.documentElement;

    // Fungsi untuk memperbarui Ikon & Teks pada tombol
    function updateThemeUI() {
        if (htmlElement.getAttribute('data-theme') === 'dark') {
            themeIcon.innerText = '🌙';
            themeText.innerText = 'Gelap';
        } else {
            themeIcon.innerText = '☀️';
            themeText.innerText = 'Terang';
        }
    }

    // Panggil sekali untuk menyesuaikan tombol saat load
    updateThemeUI();

    // Export fungsi ke objek window agar bisa dipanggil lewat onclick di HTML
    window.toggleTheme = function() {
        const currentTheme = htmlElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            // Ubah ke mode terang
            htmlElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        } else {
            // Ubah ke mode gelap
            htmlElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        }
        updateThemeUI(); // Update teks tombol
    };
});