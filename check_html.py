import re

with open('comparativo_divisivo.html', 'r', encoding='utf-8') as f:
    text = f.read()

funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', text)
print('Defined functions in JS:', funcs)

ids_in_html = set(re.findall(r'id=["\']([a-zA-Z0-9_-]+)["\']', text))
ids_in_js = set(re.findall(r'getElementById\(["\']([a-zA-Z0-9_-]+)["\']\)', text))

# Also check dynamic ids generated with templates like `card-${method}`
methods = ['diana', 'bisecting', 'furthest', 'pca']
dynamic_ids = set()
for m in methods:
    dynamic_ids.add(f'card-{m}')
    dynamic_ids.add(f'canvas-{m}')
    dynamic_ids.add(f'svg-{m}')
    dynamic_ids.add(f'diam-{m}')
    dynamic_ids.add(f'sil-{m}')
    dynamic_ids.add(f'cpcc-{m}')

missing = (ids_in_js - ids_in_html) - dynamic_ids
print('Missing static IDs in HTML:', missing)

# Check all dynamic IDs are present in HTML
missing_dyn = dynamic_ids - ids_in_html
print('Missing dynamic IDs in HTML:', missing_dyn)
