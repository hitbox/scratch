from collections import defaultdict

_styles = defaultdict(dict)

def set(module_name, style_name, style_value):
    if module_name not in _styles:
        _styles[module_name] = defaultdict(dict)
    _styles[module_name][style_name] = style_value

def get(module_name, style_name, default=None):
    return _styles.get(module_name).get(style_name, default)
