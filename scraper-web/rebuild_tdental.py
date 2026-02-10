import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_HTML = os.path.join(BASE_DIR, 'static', 'tdental.html')
STATIC_CSS = os.path.join(BASE_DIR, 'static', 'css', 'style.css')
STATIC_JS = os.path.join(BASE_DIR, 'static', 'js', 'app.js')
OUTPUT_HTML = os.path.join(BASE_DIR, 'tdental.html')

def rebuild():
    print(f"Reading {STATIC_HTML}...")
    with open(STATIC_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    print(f"Reading {STATIC_CSS}...")
    with open(STATIC_CSS, 'r', encoding='utf-8') as f:
        css = f.read()

    print(f"Reading {STATIC_JS}...")
    with open(STATIC_JS, 'r', encoding='utf-8') as f:
        js = f.read()

    # Replace CSS link
    print("Injecting CSS...")
    html = html.replace('<link rel="stylesheet" href="/static/css/style.css">', f'<style>\n{css}\n</style>')

    # Replace JS script
    print("Injecting JS...")
    html = html.replace('<script src="/static/js/app.js"></script>', f'<script>\n{js}\n</script>')

    print(f"Writing to {OUTPUT_HTML}...")
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Done!")

if __name__ == '__main__':
    rebuild()
