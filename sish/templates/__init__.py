try:
    from importlib.resources import read_text
except ImportError:
    from importlib_resources import read_text

from string import Template

def get_template(name):
    return Template(read_text('sish.templates', name))
