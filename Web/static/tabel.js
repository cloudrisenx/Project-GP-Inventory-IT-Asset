/**
 * Logik Tampilan & Interaksi Tabel Asset
 * Dilengkapi dengan Filter Otomatis (Dropdown Inline)
 */

let assetData = [];

document.addEventListener("DOMContentLoaded", function() {
    // 1. Ekstrak Data
    try {
        const rawText = document.getElementById('safe-json-data').textContent;
        if(rawText && rawText.trim() !== "") {
            assetData = JSON.parse(rawText);
        }
    } catch (error) {
        console.error("Gagal membaca data JSON:", error);
    }

    // 2. Render QR Code di Tabel
    const qrElements = document.querySelectorAll('.qr-render');
    qrElements.forEach(el => {
        const code = el.getAttribute('data-code');
        const data = assetData.find(a => a.barcode === code);

        if(code && data) {
            el.innerHTML = ""; 
            new QRCode(el, {
                text: generateRichPayload(data),
                width: 90, height: 90, 
                colorDark: "#000000", colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.M 
            });
        }
    });

    // 3. Bangun Dropdown Filter secara Dinamis
    populateInlineFilters();

    // 4. Tutup modal jika diklik di luar area konten
    window.onclick = function(event) {
        if (event.target.classList.contains('modal-overlay')) {
            event.target.style.display = 'none';
        }
    }
});

/* --- GENERATE QR LINK --- */
function generateRichPayload(data) {
    if (!data) return "INVALID_DATA";
    return `${window.location.origin}/scan/${data.barcode}`;
}

/* --- LOGIKA INLINE FILTER BAR --- */
function populateInlineFilters() {
    const depts = new Set();
    const locs = new Set();
    const cats = new Set();
    const vendors = new Set();

    // Kumpulkan nilai unik dari data asset
    assetData.forEach(item => {
        if (item.department_full) depts.add(item.department_full);
        if (item.lokasi_full) locs.add(item.lokasi_full);
        if (item.category_name) cats.add(item.category_name);
        if (item.supplier_name) vendors.add(item.supplier_name);
    });

    // Fungsi pembantu untuk mengisi dropdown
    const fillDropdown = (selectId, dataSet) => {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        Array.from(dataSet).sort().forEach(val => {
            const opt = document.createElement('option');
            opt.value = val;
            opt.textContent = val;
            select.appendChild(opt);
        });
        
        // Tambahkan event listener saat user memilih sesuatu
        select.addEventListener('change', applyInlineFilters);
    };

    fillDropdown('filter-dept', depts);
    fillDropdown('filter-loc', locs);
    fillDropdown('filter-cat', cats);
    fillDropdown('filter-vendor', vendors);
}

function applyInlineFilters() {
    const filterDept = document.getElementById('filter-dept').value;
    const filterLoc = document.getElementById('filter-loc').value;
    const filterCat = document.getElementById('filter-cat').value;
    const filterVendor = document.getElementById('filter-vendor').value;

    const rows = document.querySelectorAll('#asset-table tbody .asset-row');

    rows.forEach(row => {
        // Ambil atribut data dari tiap baris HTML (Tabel)
        const rowDept = row.getAttribute('data-departemen') || '';
        const rowLoc = row.getAttribute('data-lokasi') || '';
        const rowCat = row.getAttribute('data-kategori') || '';
        const rowVendor = row.getAttribute('data-vendor') || '';

        // Cek kecocokan (jika dropdown kosong, berarti cocok semua)
        const matchDept = (filterDept === "" || rowDept === filterDept);
        const matchLoc = (filterLoc === "" || rowLoc === filterLoc);
        const matchCat = (filterCat === "" || rowCat === filterCat);
        const matchVendor = (filterVendor === "" || rowVendor === filterVendor);

        // Sembunyikan atau tampilkan baris
        if (matchDept && matchLoc && matchCat && matchVendor) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function resetAllFilters() {
    document.getElementById('filter-dept').value = '';
    document.getElementById('filter-loc').value = '';
    document.getElementById('filter-cat').value = '';
    document.getElementById('filter-vendor').value = '';
    applyInlineFilters(); // Kembalikan tabel ke kondisi semula
}

/* --- CETAK MASSAL --- */
function openBulkPrintModal() {
    const total = assetData.length;
    document.getElementById('print-end').value = total;
    document.getElementById('print-end').max = total;
    document.getElementById('modal-bulk-print').style.display = 'flex';
}
function closeBulkPrintModal() { document.getElementById('modal-bulk-print').style.display = 'none'; }

function executeBulkPrint() {
    const start = parseInt(document.getElementById('print-start').value);
    const end = parseInt(document.getElementById('print-end').value);
    const container = document.getElementById('bulk-print-container');
    
    if (isNaN(start) || isNaN(end) || start < 1 || end > assetData.length || start > end) {
        alert("Nomor urut tidak valid."); return;
    }

    container.innerHTML = '';
    for (let i = start - 1; i < end; i++) {
        const item = assetData[i];
        if (!item) continue;

        const wrapper = document.createElement('div');
        wrapper.className = 'bulk-qr-item';
        
        const qrDiv = document.createElement('div');
        qrDiv.className = 'bulk-qr-code';
        new QRCode(qrDiv, {
            text: generateRichPayload(item),
            width: 120, height: 120,
            colorDark: "#000000", colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.M
        });

        wrapper.innerHTML = `<div class="bulk-qr-text">${item.barcode}</div>`;
        wrapper.prepend(qrDiv);
        container.appendChild(wrapper);
    }
    closeBulkPrintModal();
    setTimeout(() => { window.print(); }, 500);
}

/* --- CEK GARANSI --- */
function calculateWarrantyStatus(purchaseDateStr, warrantyStr) {
    if (!purchaseDateStr || !warrantyStr) return { label: warrantyStr || '-', isValid: null, expiryDate: '-' };

    try {
        let purchaseDate;
        const dateParts = purchaseDateStr.match(/^(\d{2})[-/](\d{2})[-/](\d{4})$/);
        if (dateParts) {
            purchaseDate = new Date(parseInt(dateParts[3]), parseInt(dateParts[2]) - 1, parseInt(dateParts[1]));
        } else {
            purchaseDate = new Date(purchaseDateStr);
        }

        if (isNaN(purchaseDate.getTime())) return { label: warrantyStr, isValid: null, expiryDate: '-' };

        const now = new Date(); now.setHours(0, 0, 0, 0);
        let monthsToAdd = 0, daysToAdd = 0;
        const text = warrantyStr.toLowerCase();
        const match = text.match(/(\d+)/);
        const number = match ? parseInt(match[0]) : 0;

        if (number > 0) {
            if (text.includes('tahun') || text.includes('year')) monthsToAdd = number * 12;
            else if (text.includes('bulan') || text.includes('month')) monthsToAdd = number;
            else if (text.includes('minggu') || text.includes('week')) daysToAdd = number * 7;
            else if (text.includes('hari') || text.includes('day')) daysToAdd = number;
        }

        const expiryDate = new Date(purchaseDate.getTime());
        if (monthsToAdd > 0) expiryDate.setMonth(expiryDate.getMonth() + monthsToAdd);
        if (daysToAdd > 0) expiryDate.setDate(expiryDate.getDate() + daysToAdd);
        expiryDate.setHours(23, 59, 59, 999); 

        const isValid = expiryDate >= now;
        const options = { day: 'numeric', month: 'long', year: 'numeric' };
        const expiryFormatted = expiryDate.toLocaleDateString('id-ID', options);

        if (monthsToAdd === 0 && daysToAdd === 0 && !text.match(/\d/)) return { label: warrantyStr, isValid: true, expiryDate: '-' };

        return {
            label: isValid ? `BERLAKU (s.d ${expiryFormatted})` : `SUDAH HABIS (Exp: ${expiryFormatted})`,
            isValid: isValid, expiryDate: expiryFormatted
        };
    } catch (e) { return { label: warrantyStr, isValid: null, expiryDate: '-' }; }
}

/* --- MODAL DETAIL UTAMA --- */
function openModal(barcode) {
    const data = assetData.find(a => a.barcode === barcode);
    if (!data) return;

    const modalContent = document.getElementById('modal-content-area');
    const formatter = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 });
    
    const harga = data.purchase_cost ? formatter.format(data.purchase_cost) : '-';

    let penyusutanFormatted = '-';
    if (data.purchase_cost && data.age_asset && data.purchase_date) {
        const parts = data.purchase_date.split('-');
        if (parts.length === 3) {
            const pDateYear = parseInt(parts[2]);
            const pDateMonth = parseInt(parts[1]) - 1; 
            
            const today = new Date();
            let monthsPassed = (today.getFullYear() - pDateYear) * 12;
            monthsPassed -= pDateMonth;
            monthsPassed += today.getMonth();
            
            if (monthsPassed < 0) monthsPassed = 0; 

            let currentVal = data.purchase_cost - ((data.purchase_cost / data.age_asset) * monthsPassed);
            if (currentVal < 0) currentVal = 0;

            penyusutanFormatted = formatter.format(currentVal);
        }
    }

    let warrantyHtml = '';
    if (data.warranty_info) {
        const warrantyCheck = calculateWarrantyStatus(data.purchase_date, data.warranty_info);
        const statusColor = warrantyCheck.isValid === true ? '#10B981' : (warrantyCheck.isValid === false ? '#EF4444' : '#6B7280');
        const statusIcon = warrantyCheck.isValid === true ? '✅' : (warrantyCheck.isValid === false ? '⚠️' : 'ℹ️');

        warrantyHtml = `
            <div class="data-group full-width">
                <div class="warranty-box" style="border-left: 4px solid ${statusColor};">
                    <div class="warranty-text" style="color: ${statusColor};">
                        ${statusIcon} GARANSI: ${data.warranty_info} <br>
                        <span style="font-weight:400; font-size:12px; color: var(--text-main);">Status: ${warrantyCheck.label}</span>
                    </div>
                </div>
            </div>
        `;
    }

    modalContent.innerHTML = `
        <div class="detail-grid">
            <div class="data-group">
                <span class="data-label">Nama Produk</span>
                <span class="data-value highlight">${data.product_name}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Model / Tipe</span>
                <span class="data-value">${data.model || '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Barcode ID</span>
                <span class="data-value mono">${data.barcode || '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Serial Number</span>
                <span class="data-value mono">${data.serial_number || '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Kategori</span>
                <span class="data-value">${data.category_name || '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Status Kondisi</span>
                <span class="data-value">${data.status_name || '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Departemen</span>
                <span class="data-value">${data.department_full || '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Lokasi Penempatan</span>
                <span class="data-value">${data.lokasi_full || '-'}</span>
            </div>
            
            <hr style="grid-column: span 2; border: 0; border-top: 1px dashed var(--border); margin: 8px 0;">
            
            <div class="data-group">
                <span class="data-label">Tanggal Pembelian</span>
                <span class="data-value">${data.purchase_date || '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Supplier / Vendor</span>
                ${data.supplier_name 
                    ? `<a href="#" onclick="openSupplierModal('${data.barcode}'); return false;" class="link-vendor" style="font-size: 14px;">${data.supplier_name}</a>` 
                    : `<span class="data-value">-</span>`}
            </div>
            
            <div class="data-group">
                <span class="data-label">Harga Pembelian</span>
                <span class="data-value">${harga}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Harga Penyusutan (Sisa)</span>
                <span class="data-value highlight" style="font-size: 15px; color: var(--primary);">${penyusutanFormatted}</span>
            </div>
            
            <div class="data-group">
                <span class="data-label">Perkiraan Usia Asset</span>
                <span class="data-value">${data.age_asset ? data.age_asset + ' Bulan' : '-'}</span>
            </div>
            <div class="data-group">
                <span class="data-label">Quantity (Qty)</span>
                <span class="data-value highlight" style="font-size: 15px;">${data.qty || '0'} Unit</span>
            </div>
            
            <hr style="grid-column: span 2; border: 0; border-top: 1px solid var(--border); margin: 8px 0;">

            <div class="data-group full-width">
                <span class="data-label">Keterangan Tambahan</span>
                <span class="data-value">${data.keterangan || '-'}</span>
            </div>
            
            ${warrantyHtml}
        </div>
    `;
    document.getElementById('modal-detail').style.display = 'flex';
}
function closeModal() { document.getElementById('modal-detail').style.display = 'none'; }

/* --- MODAL VENDOR --- */
function openSupplierModal(barcode) {
    const data = assetData.find(a => a.barcode === barcode);
    if (!data) return;

    const modalBody = document.getElementById('modal-supplier-content');
    const modalFooter = document.getElementById('modal-supplier-footer');
    
    const company = data.supplier_name || '-';
    const pic = data.supplier_contact || '-';
    let phone = data.supplier_phone || '-';

    modalBody.innerHTML = `
        <div class="vendor-row">
            <span class="v-label">Perusahaan</span>
            <span class="v-value" style="color:var(--primary); font-size:15px;">${company}</span>
        </div>
        <div class="vendor-row">
            <span class="v-label">Kontak (PIC)</span>
            <span class="v-value">${pic}</span>
        </div>
        <div class="vendor-row">
            <span class="v-label">Telepon</span>
            <span class="v-value mono" style="background:var(--surface-hover); padding:2px 6px; border-radius:4px;">${phone}</span>
        </div>
    `;

    let footerHtml = '';
    if (phone && phone.length > 6) {
        let waNum = phone.replace(/\D/g, '');
        if(waNum.startsWith('0')) waNum = '62' + waNum.substring(1);
        footerHtml = `<a href="https://wa.me/${waNum}" target="_blank" class="btn-action" style="background:#10B981; color:#FFFFFF; border:none; text-decoration:none;">Chat WhatsApp</a>`;
    }
    modalFooter.innerHTML = footerHtml;
    document.getElementById('modal-supplier').style.display = 'flex';
}
function closeSupplierModal() { document.getElementById('modal-supplier').style.display = 'none'; }

/* --- TAMPILKAN QR DI TABEL --- */
function toggleQR() {
    const table = document.getElementById('asset-table');
    const menuText = document.querySelector('#menu-toggle-qr span');
    
    table.classList.toggle('show-qr-mode');
    
    if(table.classList.contains('show-qr-mode')) {
        if(menuText) menuText.innerText = "Sembunyikan QR";
    } else {
        if(menuText) menuText.innerText = "Tampilkan QR";
    }
}

/* --- ZOOM QR --- */
function zoomQR(barcode) {
    const data = assetData.find(a => a.barcode === barcode);
    if (!data) return;

    document.getElementById('large-qr-text').innerText = barcode;
    const qrContainer = document.getElementById('large-qr-render');
    qrContainer.innerHTML = ''; 

    new QRCode(qrContainer, {
        text: generateRichPayload(data),
        width: 250, height: 250,
        colorDark: "#000000", colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.M 
    });
    document.getElementById('modal-qr').style.display = 'flex';
}
function closeQRModal() { document.getElementById('modal-qr').style.display = 'none'; }

/* --- CETAK 1 QR --- */
function printOnlyQR() {
    const barcode = document.getElementById('large-qr-text').innerText;
    const data = assetData.find(a => a.barcode === barcode);
    if (!data) return;

    const container = document.getElementById('bulk-print-container');
    container.innerHTML = ''; 

    const wrapper = document.createElement('div');
    wrapper.className = 'bulk-qr-item';
    
    const qrDiv = document.createElement('div');
    qrDiv.className = 'bulk-qr-code';
    new QRCode(qrDiv, {
        text: generateRichPayload(data),
        width: 120, height: 120,
        colorDark: "#000000", colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.M 
    });

    wrapper.innerHTML = `<div class="bulk-qr-text">${data.barcode}</div>`;
    wrapper.prepend(qrDiv);
    container.appendChild(wrapper);

    closeQRModal();
    setTimeout(() => { window.print(); }, 500);
}