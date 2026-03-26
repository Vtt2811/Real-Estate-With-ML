import os
for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8') as f: c = f.read()
            n = c.replace('dashboard.css\' %}?v=8"', 'dashboard.css\' %}?v=9"')
            if n != c:
                with open(fp, 'w', encoding='utf-8') as f: f.write(n)
                print(f'Bumped {fp}')
