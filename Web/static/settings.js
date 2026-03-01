// Fungsi untuk membuka Modal
function openModal(modalId) {
    document.getElementById(modalId).style.display = "block";
}

// Fungsi untuk menutup Modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// Menutup modal jika user klik di luar area konten modal
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = "none";
    }
}

// --- LOGIKA EDIT PER HALAMAN ---

// 1. EDIT LOKASI
function editLocation(id, name, code) {
    document.getElementById('modalTitle').innerText = "Edit Lokasi";
    document.getElementById('location_id').value = id;
    document.getElementById('name').value = name;
    document.getElementById('code').value = code || ''; // SET CODE
    openModal('formModal');
}

function addLocation() {
    document.getElementById('modalTitle').innerText = "Tambah Lokasi Baru";
    document.getElementById('formItem').reset(); 
    document.getElementById('location_id').value = ""; 
    document.getElementById('code').value = ""; // RESET CODE
    openModal('formModal');
}

// 2. EDIT KATEGORI (DIPERBARUI DENGAN DEPARTEMEN)
// Kategori menggunakan Form Inline, logikanya ada di halaman HTML-nya.

// 3. EDIT SUPPLIER
function editSupplier(id, company, contact, phone) {
    document.getElementById('modalTitle').innerText = "Edit Supplier";
    document.getElementById('supplier_id').value = id;
    document.getElementById('company_name').value = company;
    document.getElementById('contact_person').value = contact;
    document.getElementById('phone').value = phone;
    openModal('formModal');
}

function addSupplier() {
    document.getElementById('modalTitle').innerText = "Tambah Supplier Baru";
    document.getElementById('formItem').reset();
    document.getElementById('supplier_id').value = "";
    openModal('formModal');
}

// 4. EDIT STATUS
function editStatus(id, name) {
    document.getElementById('modalTitle').innerText = "Edit Status Asset";
    document.getElementById('status_id').value = id;
    document.getElementById('status_name').value = name;
    openModal('formModal');
}

function addStatus() {
    document.getElementById('modalTitle').innerText = "Tambah Status Baru";
    document.getElementById('formItem').reset();
    document.getElementById('status_id').value = "";
    openModal('formModal');
}

// 5. LOGIKA DEPARTEMEN
function editDepartment(id, name, code) {
    document.getElementById('modalTitle').innerText = "Edit Departemen";
    document.getElementById('department_id').value = id;
    document.getElementById('name').value = name;
    
    // Pastikan ID input code di departemen tertangkap dengan benar
    if(document.getElementById('code')) {
        document.getElementById('code').value = (code !== 'None' && code) ? code : '';
    }
    
    openModal('formModal');
}

function addDepartment() {
    document.getElementById('modalTitle').innerText = "Tambah Departemen Baru";
    document.getElementById('formItem').reset(); 
    document.getElementById('department_id').value = ""; 
    
    if(document.getElementById('code')) {
        document.getElementById('code').value = ""; // RESET CODE
    }
    
    openModal('formModal');
}

function addDepartment() {
    document.getElementById('modalTitle').innerText = "Tambah Departemen Baru";
    document.getElementById('formItem').reset(); 
    document.getElementById('department_id').value = ""; 
    document.getElementById('code').value = ""; // RESET CODE
    openModal('formModal');
}