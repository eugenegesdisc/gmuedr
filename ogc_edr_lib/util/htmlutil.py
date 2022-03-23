import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape

Logger = logging.getLogger(__name__)


def render_j2_template(config, template, data, locale_=None):
    """
    render Jinja2 template

    :param config: dict of configuration
    :param template: template (relative path)
    :param data: dict of data
    :param locale_: the requested output Locale

    :returns: string of rendered template
    """

    custom_templates = False
    try:
        templates_path = config.get_config()['server']['templates']['path']
        env = Environment(loader=FileSystemLoader(templates_path),
                          extensions=['jinja2.ext.i18n',
                                      'jinja2.ext.autoescape'],
                          autoescape=select_autoescape(['html', 'xml']))
        custom_templates = True
        Logger.debug('using custom templates: {}'.format(templates_path))
    except (KeyError, TypeError):
        env = Environment(loader=FileSystemLoader(config.get_template_path()),
                          extensions=['jinja2.ext.i18n',
                                      'jinja2.ext.autoescape'],
                          autoescape=select_autoescape(['html', 'xml']))
        Logger.debug('using default templates: {}'.format(
            config.get_template_path()))

    env.filters['to_json'] = to_json
    env.filters['format_datetime'] = format_datetime
    env.filters['format_duration'] = format_duration
    env.filters['human_size'] = human_size
    env.globals.update(to_json=to_json)

    env.filters['get_path_basename'] = get_path_basename
    env.globals.update(get_path_basename=get_path_basename)

    env.filters['get_breadcrumbs'] = get_breadcrumbs
    env.globals.update(get_breadcrumbs=get_breadcrumbs)

    env.filters['filter_dict_by_key_value'] = filter_dict_by_key_value
    env.globals.update(filter_dict_by_key_value=filter_dict_by_key_value)

    translations = Translations.load('locale', [locale_])
    env.install_gettext_translations(translations)

    try:
        template = env.get_template(template)
    except TemplateNotFound as err:
        if custom_templates:
            Logger.debug(err)
            Logger.debug('Custom template not found; using default')
            env = Environment(loader=FileSystemLoader(config.get_template_path),
                              extensions=['jinja2.ext.i18n'])
            template = env.get_template(template)
        else:
            raise

    return template.render(config=l10n.translate_struct(config, locale_, True),
                           data=data, version=__version__)
