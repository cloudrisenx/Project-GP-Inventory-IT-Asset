/**
 * Logika Interaksi Form Tambah Data Asset
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // INISIALISASI ELEMEN FORM
    const maingroupSelect = document.getElementById('deptSelect');
    const subgroupSelect = document.getElementById('catSelect');
    const locSelect = document.getElementById('locSelect'); 
    const dateInput = document.getElementById('purchaseDate');
    const barcodeInput = document.getElementById('barcodeInput');
    const autoBarcodeCheck = document.getElementById('autoBarcodeToggle'); // Perbaikan nama ID
    
    // Simpan semua opsi subgroup (kategori) asli ke dalam memory untuk proses filter
    const allSubgroupOptions = Array.from(subgroupSelect.options);

    // FILTER SUBGROUP BERDASARKAN MAINGROUP
    maingroupSelect.addEventListener('change', function() {
        const selectedMaingroupId = this.value;
        
        subgroupSelect.innerHTML = '<option value="" data-code="">-- Pilih Subgroup --</option>';
        
        if (selectedMaingroupId) {
            subgroupSelect.disabled = false;
            // Filter subgroup yang data-dept nya cocok dengan ID maingroup
            const filteredSubgroups = allSubgroupOptions.filter(opt => opt.getAttribute('data-dept') === selectedMaingroupId);
            
            filteredSubgroups.forEach(opt => {
                subgroupSelect.appendChild(opt.cloneNode(true));
            });
        } else {
            subgroupSelect.disabled = true;
            subgroupSelect.innerHTML = '<option value="" data-code="">-- Pilih Maingroup Dahulu --</option>';
        }
        
        generateCustomCode(); 
    });

    // GENERATE KODE BARCODE (TAG ID)
    function generateCustomCode() {
        if (!autoBarcodeCheck || !autoBarcodeCheck.checked) return;

        // Ambil data-code dari Maingroup
        const mainOpt = maingroupSelect.options[maingroupSelect.selectedIndex];
        const mainCode = (mainOpt && mainOpt.getAttribute('data-code') && mainOpt.value !== "") 
                         ? mainOpt.getAttribute('data-code') : 'DEP';
        
        // Ambil data-code Kategori
        const subOpt = subgroupSelect.options[subgroupSelect.selectedIndex];
        const subCode = (subOpt && subOpt.getAttribute('data-code') && subOpt.value !== "") 
                         ? subOpt.getAttribute('data-code') : 'CAT';
        
        // Logika Singkatan Input Model
        const modelInput = document.querySelector('input[name="model"]');
        let modelValue = 'MOD';
        if (modelInput && modelInput.value.trim() !== "") {
            let mText = modelInput.value.trim();
            
            // Cek apakah keseluruhan teks model hanya berisi angka murni
            if (/^\d+$/.test(mText.replace(/[\s-]/g, ''))) {
                modelValue = mText.replace(/[\s-]/g, '').substring(0, 2); // Ambil 2 digit depan
            } else {
                // Jika mengandung huruf, ambil inisial (huruf pertama) dari tiap kata
                modelValue = mText.split(/[\s-]+/).map(w => {
                    if (/^\d+$/.test(w)) return w.substring(0, 2); // Jika ada kata yg murni angka
                    
                    let firstChar = w.match(/[a-zA-Z]/); // Cari huruf pertama
                    firstChar = firstChar ? firstChar[0] : w.charAt(0);
                    
                    let nums = w.match(/\d+/g); // Sertakan angka jika gabung dengan huruf
                    return nums ? firstChar + nums.join('') : firstChar;
                }).join('');
            }
        }
        
        // Ambil data-code dari Lokasi
        const locOpt = locSelect.options[locSelect.selectedIndex];
        const locCode = (locOpt && locOpt.getAttribute('data-code') && locOpt.value !== "") 
                         ? locOpt.getAttribute('data-code') : 'LOC';

        // Format Tanggal (YYYY-MM)
        let dateStr = 'YYYY-MM';
        if (dateInput && dateInput.value) {
            const d = new Date(dateInput.value);
            const year = d.getFullYear(); // 4 Digit      
            const month = String(d.getMonth() + 1).padStart(2, '0'); // 2 Digit
            dateStr = `${year}-${month}`;
        }

        // Ambil Kode Hotel
        const hotelCodeInput = document.getElementById('hotelCodeInput');
        const hotelCode = (hotelCodeInput && hotelCodeInput.value) ? hotelCodeInput.value : 'GPB';

        // Gabungkan menjadi: DEP/CAT-MOD/LOC/YYYY-MM/HOTEL
        const finalBarcode = `${mainCode}/${subCode}-${modelValue}/${locCode}/${dateStr}/${hotelCode}`.toUpperCase();

        if (barcodeInput) {
            barcodeInput.value = finalBarcode;
        }
    }

    // Event listeners Trigger Model
    const modelInput = document.querySelector('input[name="model"]');
    if (modelInput) modelInput.addEventListener('input', generateCustomCode);
    
    // EVENT LISTENERS TRIGGER BARCODE
    if (autoBarcodeCheck) {
        autoBarcodeCheck.addEventListener('change', function() {
            if (this.checked) {
                barcodeInput.setAttribute('readonly', true);
                barcodeInput.style.backgroundColor = 'var(--surface-alt)';
                barcodeInput.style.borderColor = 'var(--primary)';
                barcodeInput.style.color = 'var(--primary)';
                barcodeInput.style.fontWeight = '600';
                generateCustomCode(); 
            } else {
                barcodeInput.removeAttribute('readonly');
                barcodeInput.style.backgroundColor = '';
                barcodeInput.style.borderColor = '';
                barcodeInput.style.color = '';
                barcodeInput.style.fontWeight = '';
                barcodeInput.focus(); 
            }
        });
    }

    if(subgroupSelect) subgroupSelect.addEventListener('change', generateCustomCode);
    if(locSelect) locSelect.addEventListener('change', generateCustomCode);
    if(dateInput) dateInput.addEventListener('change', generateCustomCode);
    
    // Tambahan Event Listener untuk input Kode Hotel
    const hotelCodeInput = document.getElementById('hotelCodeInput');
    if(hotelCodeInput) hotelCodeInput.addEventListener('input', generateCustomCode);

    // VALIDASI ANGKA (HARGA & PERKIRAAN USIA)
    
    // Validasi Harga Beli
    const costInput = document.querySelector('input[name="purchase_cost"]');
    if (costInput) {
        costInput.addEventListener('blur', function() {
            if (this.value && this.value < 0) {
                alert("Harga beli tidak boleh bernilai negatif.");
                this.value = 0;
            }
        });
    }

    // Validasi Perkiraan Usia (Bulan) - Menggunakan name="age_asset"
    const ageInput = document.querySelector('input[name="age_asset"]');
    if (ageInput) {
        // Mencegah input huruf atau karakter aneh (hanya angka)
        ageInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        // Memastikan tidak minus atau kosong saat user selesai mengetik
        ageInput.addEventListener('blur', function() {
            if (this.value === '' || this.value < 0) {
                this.value = 0; 
            }
        });
    }
});

// FUNGSI MODAL PENGATURAN BARCODE
function openBarcodeSettings() {
    const modal = document.getElementById('modal-barcode-settings');
    if(modal) modal.style.display = 'flex';
}
function closeBarcodeSettings() {
    const modal = document.getElementById('modal-barcode-settings');
    if(modal) modal.style.display = 'none';
    
    // Trigger update code saat tutup modal
    const autoBarcodeCheck = document.getElementById('autoBarcodeToggle');
    if(autoBarcodeCheck && autoBarcodeCheck.checked) {
       // dispatch event tidak bisa langsung panggil fungsi scope internal, cukup percayakan pd input listener 
       const modelInput = document.querySelector('input[name="model"]');
       if(modelInput) modelInput.dispatchEvent(new Event('input'));
    }
}