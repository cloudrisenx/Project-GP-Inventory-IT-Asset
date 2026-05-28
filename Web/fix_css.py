import glob, os, re

master_css = '''/* --- NAVBAR STANDARDIZATION --- */
.top-navbar {
    background-color: var(--surface, var(--bg-card, #ffffff));
    padding: 0 32px;
    height: 72px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border, var(--border-color, #e5e5ea));
    position: sticky;
    top: 0;
    z-index: 50;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    transition: background-color 0.3s ease, border-color 0.3s ease;
}
.nav-brand { display: flex; align-items: center; gap: 12px; }
.brand-logo { background: var(--primary, var(--gp-green, #10b981)); color: #ffffff; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; padding: 6px 12px; border-radius: 8px; font-size: 16px; transition: color 0.3s ease; }
[data-theme="dark"] .brand-logo { color: #111827; }

.brand-info { display: flex; flex-direction: column; }
.brand-title { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 15px; color: var(--text-main, #1d1d1f); }
.brand-subtitle { font-size: 11px; color: var(--text-muted, #86868b); font-family: 'Inter', sans-serif;}

.nav-actions { display: flex; align-items: center; gap: 12px; }

.btn-back {
    text-decoration: none; color: var(--text-main, #1d1d1f); font-weight: 600; font-size: 13px;          
    display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px;        
    background-color: var(--surface-hover, var(--bg-hover, #f3f4f6)); border: 1px solid var(--border, var(--border-color, #e5e5ea)); border-radius: 50px; transition: all 0.3s ease;     
}
.btn-back:hover { background-color: var(--primary, var(--gp-green, #10b981)); border-color: var(--primary, var(--gp-green, #10b981)); color: #FFFFFF; }
[data-theme="dark"] .btn-back:hover { color: #111827; }

.btn-back svg { width: 16px; height: 16px; color: var(--text-muted, #86868b); transition: transform 0.2s ease, color 0.2s ease; }
.btn-back:hover svg { color: #FFFFFF; transform: translateX(-2px); }
[data-theme="dark"] .btn-back:hover svg { color: #111827; }
/* --- END NAVBAR STANDARDIZATION --- */'''

css_files = glob.glob(r'c:\Users\X\OneDrive\Documents\PROJECT GP\3. Project-IT-Asset\Web\static\*.css')
for f in css_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove old navbar blocks (simple approach using regex)
    content = re.sub(r'\.top-navbar\s*{[^}]*}', '', content)
    content = re.sub(r'\.nav-brand\s*{[^}]*}', '', content)
    content = re.sub(r'\.brand-logo\s*{[^}]*}', '', content)
    content = re.sub(r'\[data-theme="dark"\] \.brand-logo\s*{[^}]*}', '', content)
    content = re.sub(r':root \.brand-logo\s*{[^}]*}', '', content)
    content = re.sub(r'\.brand-info\s*{[^}]*}', '', content)
    content = re.sub(r'\.brand-title\s*{[^}]*}', '', content)
    content = re.sub(r'\.brand-subtitle\s*{[^}]*}', '', content)
    content = re.sub(r'\.nav-actions\s*{[^}]*}', '', content)
    content = re.sub(r'\.btn-back\s*{[^}]*}', '', content)
    content = re.sub(r'\.btn-back:hover\s*{[^}]*}', '', content)
    content = re.sub(r'\[data-theme="dark"\] \.btn-back:hover\s*{[^}]*}', '', content)
    content = re.sub(r'\.btn-back svg\s*{[^}]*}', '', content)
    content = re.sub(r'\.btn-back:hover svg\s*{[^}]*}', '', content)
    content = re.sub(r'\[data-theme="dark"\] \.btn-back:hover svg\s*{[^}]*}', '', content)
    
    new_content = content + '\n\n' + master_css
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(new_content)
    print(f'Standardized header in {os.path.basename(f)}')
