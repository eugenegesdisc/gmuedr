import os
import yaml
import importlib
import pkgutil

import ogc_edr_lib.providers
import ogc_edr_lib.formatters
import inspect
import sys
import logging

Logger = logging.getLogger(__name__)


class PlugIn(object):
    def __init__(self, name, cls):
        super().__init__()
        self.name = name
        self.cls = cls


class OGCEDRPluginManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OGCEDRPluginManager, cls).__new__(cls)
            cls.plugins = {}
            cls.plugins["provider"] = []
            cls.instance.load_plugins(
                type="provider", module=ogc_edr_lib.providers)
            cls.plugins["formatter"] = []
            cls.instance.load_plugins(
                type="formatter", module=ogc_edr_lib.formatters)
        return cls.instance

    def iter_namespace(self, ns_pkg):
        # Specifying the second argument (prefix) to iter_modules makes the
        # returned name an absolute name instead of a relative one. This allows
        # import_module to work without having to do additional modification to
        # the name.
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    def load_plugins(self, type, module):
        discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in self.iter_namespace(module)
        }

        # find certain formatter
        for p, v in discovered_plugins.items():
            clsmembers = inspect.getmembers(sys.modules[p], inspect.isclass)
            for cm in clsmembers:
                if (
                    hasattr(cm[1], "type")
                    and cm[1].type == type
                ):
                    pl = PlugIn(name=cm[0], cls=cm[1])
                    self.plugins[type].append(pl)

    def get_plugin_by_media_type(self, type, mediatype):
        for p in self.plugins[type]:
            if mediatype in p.cls.supported_media_types:
                return p
        return None

    def get_plugin_by_category_media_type(self, type, category, mediatype):
        for p in self.plugins[type]:
            if category != p.cls.category:
                continue
            if mediatype in p.cls.supported_media_types:
                return p
        return None

    @staticmethod
    def get_provider_by_type(providers, provider_type):
        """
        helper function to load a provider by a provider type

        :param providers: ``list`` of providers
        :param provider_type: type of provider

        :returns: provider based on type
        """
        try:
            p = (next(d for i, d in enumerate(providers)
                      if d['type'] == provider_type))
        except BaseException as error:
            Logger.error(error)
            return None
        return p
