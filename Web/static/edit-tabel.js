document.addEventListener('DOMContentLoaded', function() {
            
    // 1. Ambil data dari DIV tersembunyi
    let assetsData = [];
    try {
        const jsonData = document.getElementById('safe-json-data').textContent;
        if (jsonData.trim() !== '') {
            assetsData = JSON.parse(jsonData);
        }
    } catch (e) {
        console.error("Gagal parsing JSON data asset:", e);
    }

    const deptSelect = document.getElementById('edit_department_id');
    const catSelect = document.getElementById('edit_category_id');
    const locSelect = document.getElementById('edit_location_id');
    const dateInput = document.getElementById('edit_purchase_date');
    const barcodeInput = document.getElementById('edit_barcode');
    const autoBarcodeToggle = document.getElementById('autoBarcodeToggle');
    const hotelCodeInput = document.getElementById('hotelCodeInput');
    const modelInput = document.getElementById('edit_model'); // Tambahan untuk Model
    
    const allCatOptions = Array.from(catSelect.options);

    // Filter Kategori (Subgroup) saat Departemen berubah
    deptSelect.addEventListener('change', function() {
        const selectedDeptId = this.value;
        catSelect.innerHTML = '<option value="" data-code="">-- Pilih --</option>';
        
        if (selectedDeptId) {
            catSelect.disabled = false;
            const filteredCats = allCatOptions.filter(opt => opt.getAttribute('data-dept') == selectedDeptId);
            filteredCats.forEach(opt => catSelect.appendChild(opt.cloneNode(true)));
        } else {
            catSelect.disabled = true;
            catSelect.innerHTML = '<option value="" data-code="">-- Pilih Dept Dahulu --</option>';
        }
        generateAutoBarcode(); 
    });

    // Logika Auto Barcode
    function generateAutoBarcode() {
        if (!autoBarcodeToggle || !autoBarcodeToggle.checked) return;

        // 1. Kode Departemen
        const deptOpt = deptSelect.options[deptSelect.selectedIndex];
        const deptCode = (deptOpt && deptOpt.getAttribute('data-code') && deptOpt.value !== "") 
                         ? deptOpt.getAttribute('data-code') : 'DEP';
        
        // 2. Kode Kategori & Model
        const catOpt = catSelect.options[catSelect.selectedIndex];
        const catCode = (catOpt && catOpt.getAttribute('data-code') && catOpt.value !== "") 
                         ? catOpt.getAttribute('data-code') : 'CAT';
        
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
                    
                    let nums = w.match(/\d+/g); // Sertakan angka jika gabung dengan huruf (Misal: X1 -> 1)
                    return nums ? firstChar + nums.join('') : firstChar;
                }).join('');
            }
        }
        
        // 3. Kode Lokasi
        const locOpt = locSelect.options[locSelect.selectedIndex];
        const locCode = (locOpt && locOpt.getAttribute('data-code') && locOpt.value !== "") 
                         ? locOpt.getAttribute('data-code') : 'LOC';

        // 4. Tahun 4 Digit - Bulan 2 Digit (YYYY-MM)
        let dateStr = 'YYYY-MM';
        if (dateInput && dateInput.value) {
            const d = new Date(dateInput.value);
            const year = d.getFullYear(); // 4 digit tahun
            const month = String(d.getMonth() + 1).padStart(2, '0'); // 2 digit bulan
            dateStr = `${year}-${month}`;
        }

        // 5. Kode Hotel
        const hotelCode = (hotelCodeInput && hotelCodeInput.value) ? hotelCodeInput.value : 'GPB';
        
        // Format Akhir: DEP/CAT-MOD/LOC/YYYY-MM/HOTEL
        const finalBarcode = `${deptCode}/${catCode}-${modelValue}/${locCode}/${dateStr}/${hotelCode}`.toUpperCase();
        
        if (barcodeInput) {
            barcodeInput.value = finalBarcode;
        }
    }

    autoBarcodeToggle.addEventListener('change', function() {
        if (this.checked) {
            barcodeInput.setAttribute('readonly', true);
            barcodeInput.style.backgroundColor = 'var(--surface-alt)';
            barcodeInput.style.color = 'var(--primary)';
            generateAutoBarcode();
        } else {
            barcodeInput.removeAttribute('readonly');
            barcodeInput.style.backgroundColor = '';
            barcodeInput.style.color = '';
        }
    });

    catSelect.addEventListener('change', generateAutoBarcode);
    locSelect.addEventListener('change', generateAutoBarcode);
    dateInput.addEventListener('change', generateAutoBarcode);
    if(hotelCodeInput) hotelCodeInput.addEventListener('input', generateAutoBarcode);
    if(modelInput) modelInput.addEventListener('input', generateAutoBarcode); // Trigger saat model diketik

    // FUNGSI UNTUK MEMBUKA MODAL
    window.openEditModal = function(assetId) {
        const asset = assetsData.find(a => String(a.asset_id) === String(assetId));
        if (!asset) {
            console.error('Asset ID:', assetId, 'Data:', assetsData);
            alert('Data tidak ditemukan di memory!');
            return;
        }

        // Isi form modal
        document.getElementById('edit_asset_id').value = asset.asset_id;
        document.getElementById('edit_product_name').value = asset.product_name || '';
        document.getElementById('edit_model').value = asset.model || '';
        document.getElementById('edit_manufacturer').value = asset.manufacturer || '';
        document.getElementById('edit_barcode').value = asset.barcode || '';
        document.getElementById('edit_serial_number').value = asset.serial_number || '';
        document.getElementById('edit_location_id').value = asset.location_id || '';
        document.getElementById('edit_status_id').value = asset.status_id || '';
        document.getElementById('edit_purchase_date').value = asset.purchase_date || '';
        document.getElementById('edit_supplier_id').value = asset.supplier_id || '';
        document.getElementById('edit_purchase_cost').value = asset.purchase_cost || 0;
        document.getElementById('edit_age_asset').value = asset.age_asset || 0;
        document.getElementById('edit_qty').value = asset.qty || 1;
        document.getElementById('edit_warranty_info').value = asset.warranty_info || '';
        document.getElementById('edit_keterangan').value = asset.keterangan || '';

        // Reset toggle barcode
        autoBarcodeToggle.checked = false;
        barcodeInput.removeAttribute('readonly');
        barcodeInput.style.backgroundColor = '';

        // Trigger filter kategori
        deptSelect.value = asset.department_id || '';
        deptSelect.dispatchEvent(new Event('change'));
        
        setTimeout(() => { 
            catSelect.value = asset.category_id || ''; 
        }, 50);

        document.getElementById('modal-edit').style.display = 'flex';
    };

    window.closeEditModal = function() {
        document.getElementById('modal-edit').style.display = 'none';
    };

    window.openBarcodeSettings = function() {
        document.getElementById('modal-barcode-settings').style.display = 'flex';
    };
    window.closeBarcodeSettings = function() {
        document.getElementById('modal-barcode-settings').style.display = 'none';
        generateAutoBarcode();
    };

    // Validasi Usia (Hanya Angka)
    const ageInput = document.getElementById('edit_age_asset');
    if(ageInput) {
        ageInput.addEventListener('input', function() { this.value = this.value.replace(/[^0-9]/g, ''); });
        ageInput.addEventListener('blur', function() { if (this.value < 0) this.value = 0; });
    }

    // Validasi Harga (Tidak boleh minus)
    const costInput = document.getElementById('edit_purchase_cost');
    if(costInput) {
        costInput.addEventListener('blur', function() { if (this.value < 0) this.value = 0; });
    }
});