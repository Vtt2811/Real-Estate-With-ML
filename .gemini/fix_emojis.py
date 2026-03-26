import os
import re

EMOJI_MAP = {
    '🏠': '<i data-lucide="home"></i>',
    '🏡': '<i data-lucide="home"></i>',
    '📊': '<i data-lucide="bar-chart-2"></i>',
    '👤': '<i data-lucide="user"></i>',
    '🚪': '<i data-lucide="log-out"></i>',
    '🔍': '<i data-lucide="search"></i>',
    '🏘️': '<i data-lucide="building"></i>',
    '🏗️': '<i data-lucide="hard-hat"></i>',
    '🌆': '<i data-lucide="map"></i>',
    '🛏️': '<i data-lucide="bed-double"></i>',
    '📐': '<i data-lucide="ruler"></i>',
    '⭐': '<i data-lucide="star"></i>',
    '📍': '<i data-lucide="map-pin"></i>',
    '📏': '<i data-lucide="navigation"></i>',
    '📅': '<i data-lucide="calendar"></i>',
    '🤖': '<i data-lucide="bot"></i>',
    '⚡': '<i data-lucide="zap"></i>',
    '✨': '<i data-lucide="sparkles"></i>',
    '💡': '<i data-lucide="lightbulb"></i>',
    '➕': '<i data-lucide="plus-circle"></i>',
    '👁️': '<i data-lucide="eye"></i>',
    '📬': '<i data-lucide="inbox"></i>',
    '⏱️': '<i data-lucide="clock"></i>',
    '📭': '<i data-lucide="package-open"></i>',
    '❤️': '<i data-lucide="heart"></i>',
    '🚿': '<i data-lucide="shower-head"></i>',
    '✓': '<i data-lucide="check"></i>'
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Remove inline style for root font-sizing
    pattern = re.compile(r'\s*<style>\s*html\s*\{\s*font-size:\s*77%;\s*\}\s*body\s*\{\s*font-size:\s*clamp\(12px,\s*calc\(9px\s*\+\s*0\.6vw\),\s*18px\)\s*!important;\s*\}\s*</style>\s*')
    content = pattern.sub('\n', content)

    for emoji, icon in EMOJI_MAP.items():
        content = content.replace(emoji, icon)

    # Inject lucide CSS or script if we used an icon
    if ('data-lucide="' in content):
        if '<script src="https://unpkg.com/lucide@latest"></script>' not in content:
            content = content.replace('</head>', '    <script src="https://unpkg.com/lucide@latest"></script>\n</head>')
        if 'lucide.createIcons();' not in content:
            content = content.replace('</body>', '    <script>\n        lucide.createIcons();\n    </script>\n</body>')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated HTML: {filepath}')

for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            process_file(os.path.join(root, file))

# Fix dashboard.css size explicitly
try:
    with open('static/css/dashboard.css', 'r', encoding='utf-8') as f:
        css = f.read()
    if 'html { font-size: 77%; }' not in css:
        css = css.replace(':root {', 'html { font-size: 77%; }\n\n:root {')
        css = css.replace('font-size: clamp(14px, calc(10px + 0.8vw), 24px);', 'font-size: clamp(12px, calc(9px + 0.6vw), 18px) !important;')
        # bust cache
        
        with open('static/css/dashboard.css', 'w', encoding='utf-8') as f:
            f.write(css)
        print('Updated dashboard.css scaling')
except Exception as e:
    print(e)
