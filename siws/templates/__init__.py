try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from string import Template

def get_template(name):
    template_folder = files('siws.templates')
    template_path = template_folder.joinpath(name)
    return Template(template_path.read_text())
