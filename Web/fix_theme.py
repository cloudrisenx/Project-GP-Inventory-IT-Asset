import glob, os

script = '''
    <script>
        if (localStorage.getItem('theme') === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    </script>
'''

files = glob.glob(r'c:\Users\X\OneDrive\Documents\PROJECT GP\3. Project-IT-Asset\Web\templates\*.html')
for f in files:
    if os.path.basename(f) == 'header_layout.html':
        continue # It doesn't have a <head>
        
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    if "localStorage.getItem('theme')" not in content and '</head>' in content:
        new_content = content.replace('</head>', f'{script}</head>')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Added theme script to {os.path.basename(f)}')
