// 1. Inisialisasi Data Global
let assetData = [];

// Fungsi membaca data aman saat halaman dimuat
document.addEventListener("DOMContentLoaded", function() {
    try {
        const rawText = document.getElementById('safe-json-data').textContent;
        if(rawText && rawText.trim() !== "") {
            assetData = JSON.parse(rawText);
        }
    } catch (error) {
        console.error("Gagal membaca data JSON:", error);
    }

    // Render QR Code Kecil di Tabel
    const qrElements = document.querySelectorAll('.qr-render');
    qrElements.forEach(el => {
        const code = el.getAttribute('data-code');
        const data = assetData.find(a => a.barcode === code);
        const name = data ? data.product_name : '';

        if(code) {
            const qrPayloadText = `Barcode: ${code}\nNama Barang: ${name}`;
            new QRCode(el, {
                text: qrPayloadText,
                width: 75,
                height: 75,
                colorDark: "#1A1917",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.M
            });
        }
    });
});

/* --- FUNGSI MODAL VENDOR (YANG DIPERBAIKI) --- */

// Fungsi tutup modal (Global Scope agar bisa diakses HTML)
function closeSupplierModal() {
    const modal = document.getElementById('modal-supplier');
    if (modal) {
        modal.style.display = 'none';
    }
}

function openSupplierModal(barcode) {
    try {
        const data = assetData.find(a => a.barcode === barcode);
        if (!data) return;

        const modal = document.getElementById('modal-supplier');
        const modalBody = document.getElementById('modal-supplier-content');
        const modalFooter = document.getElementById('modal-supplier-footer');

        // 1. Persiapan Data
        const company = data.supplier_name || '-';
        const contact = data.supplier_contact || '-';
        let rawPhone = data.supplier_phone || '-';
        
        // Format WA (08xx -> 628xx)
        let waNumber = rawPhone.replace(/\D/g, '');
        if (waNumber.startsWith('0')) waNumber = '62' + waNumber.substring(1);
        const waLink = `https://wa.me/${waNumber}`;

        // 2. Render Body dengan Layout Grid (Professional & Rapi)
        // Menggunakan class CSS .vendor-info-row yang sudah didefinisikan di HTML
        modalBody.innerHTML = `
            <!-- Baris 1: Nama Perusahaan -->
            <div class="vendor-info-row">
                <div class="v-label">Perusahaan</div>
                <div class="v-value" style="color: var(--gp-green); font-size: 16px;">${company}</div>
            </div>

            <!-- Baris 2: Nama PIC -->
            <div class="vendor-info-row">
                <div class="v-label">Nama (PIC)</div>
                <div class="v-value">${contact}</div>
            </div>

            <!-- Baris 3: Nomor Telepon -->
            <div class="vendor-info-row">
                <div class="v-label">No. Telepon</div>
                <div class="v-value">
                    <span style="background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-family: monospace;">
                        ${rawPhone}
                    </span>
                </div>
            </div>
        `;

        // 3. Render Footer (Tombol)
        // Tombol Batal diberi type="button" agar aman
        let footerHtml = `
            <button type="button" class="btn-action" onclick="closeSupplierModal()" 
                style="background: transparent; border: 1px solid #cbd5e1; color: #475569;">
                Batal
            </button>
        `;

        // Jika ada nomor HP valid, tambahkan tombol WA
        if (rawPhone && rawPhone !== '-' && rawPhone.length > 5) {
            footerHtml += `
                <a href="${waLink}" target="_blank" style="
                    text-decoration: none;
                    background-color: #25D366; 
                    color: white; 
                    padding: 8px 16px; 
                    border-radius: 6px; 
                    font-weight: bold; 
                    font-size: 13px; 
                    display: flex; 
                    align-items: center; 
                    gap: 8px; 
                    box-shadow: 0 4px 6px rgba(37, 211, 102, 0.2);
                    transition: transform 0.1s;">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.6 2.326z"/></svg>
                    Hubungi via WhatsApp
                </a>
            `;
        }

        modalFooter.innerHTML = footerHtml;
        modal.style.display = 'flex';

    } catch (error) {
        console.error("Error membuka modal vendor:", error);
        alert("Gagal memuat data vendor.");
    }
}

/* --- FUNGSI MODAL DETAIL ASSET --- */

function openModal(barcode) {
    const data = assetData.find(a => a.barcode === barcode);
    if (!data) return;

    const modalContent = document.getElementById('modal-content-area');
    const formatter = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 });
    const harga = formatter.format(data.purchase_cost || 0);

    let specsHtml = '-';
    if (data.specs) {
        if (typeof data.specs === 'object') {
            specsHtml = Object.entries(data.specs)
                .map(([key, val]) => `<div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding:4px 0;"><span style="color:#666; font-size:12px;">${key}</span><span style="font-weight:600;">${val}</span></div>`)
                .join('');
        } else {
            specsHtml = data.specs;
        }
    }

    modalContent.innerHTML = `
        <div class="data-group"><span class="data-label">Nomor Barcode</span><span class="data-value">${data.barcode || '-'}</span></div>
        <div class="data-group"><span class="data-label">Serial Number</span><span class="data-value">${data.serial_number || '-'}</span></div>
        
        <div class="data-group"><span class="data-label">Nama Asset</span><span class="data-value" style="color:var(--gp-green);">${data.product_name}</span></div>
        <div class="data-group"><span class="data-label">Model</span><span class="data-value">${data.model || '-'}</span></div>
        
        <div class="data-group"><span class="data-label">Kategori</span><span class="data-value">${data.category_name || '-'}</span></div>
        <div class="data-group"><span class="data-label">Status</span><span class="data-value">${data.status_name || '-'}</span></div>
        
        <div class="data-group"><span class="data-label">Lokasi</span><span class="data-value">${data.lokasi_full || '-'}</span></div>
        <div class="data-group"><span class="data-label">Supplier</span><span class="data-value">${data.supplier_name || '-'}</span></div>
        
        <div class="data-group"><span class="data-label">Tanggal Beli</span><span class="data-value">${data.purchase_date || '-'}</span></div>
        <div class="data-group"><span class="data-label">Harga Beli</span><span class="data-value">${harga}</span></div>
        
        <div class="data-group" style="grid-column: span 2; background: #F8FAF9; padding: 15px; border-radius: 8px; border: 1px solid #eee;">
            <span class="data-label" style="display:block; margin-bottom:8px;">Spesifikasi Teknis</span>
            <div style="font-size: 13px;">${specsHtml}</div>
        </div>
    `;

    document.getElementById('modal-detail').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-detail').style.display = 'none';
}

/* --- FUNGSI QR CODE --- */

function toggleQR() {
    const table = document.getElementById('asset-table');
    const btn = document.getElementById('btn-toggle-qr');
    table.classList.toggle('show-qr-mode');
    
    if(table.classList.contains('show-qr-mode')) {
        btn.innerText = "Sembunyikan QR Code";
        btn.style.background = "var(--gp-orange)";
        btn.style.color = "var(--white)";
    } else {
        btn.innerText = "Tampilkan QR Code";
        btn.style.background = "transparent";
        btn.style.color = "var(--gp-black)";
    }
}

function zoomQR(barcode) {
    const data = assetData.find(a => a.barcode === barcode);
    const productName = data ? data.product_name : 'Tidak Diketahui';

    document.getElementById('large-qr-text').innerText = barcode;
    document.getElementById('large-qr-product').innerText = productName;
    
    const qrContainer = document.getElementById('large-qr-render');
    qrContainer.innerHTML = ''; 

    const qrPayloadText = `Barcode: ${barcode}\nNama Barang: ${productName}`;
    new QRCode(qrContainer, {
        text: qrPayloadText,
        width: 250,
        height: 250,
        colorDark: "#1A1917",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });

    document.getElementById('modal-qr').style.display = 'flex';
}

function closeQRModal() {
    document.getElementById('modal-qr').style.display = 'none';
}

function printOnlyQR() {
    document.body.classList.add('print-qr-only');
    window.print();
    setTimeout(() => {
        document.body.classList.remove('print-qr-only');
    }, 500);
}