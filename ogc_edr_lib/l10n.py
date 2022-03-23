from typing import Union
from babel import Locale
import locale
from translate import Translator
from copy import deepcopy

from ogc_edr_lib.ogc_api_config import OgcApiConfig

# Cache translated configurations
_cfg_cache = {}


class LocaleTranslator(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LocaleTranslator, cls).__new__(cls)
            cls.config = OgcApiConfig()
        return cls.instance

    def translate2(self, value, loc: Union[list, Locale, str]):
        """
        Translate the value into specific locale:

        Case 1: If `value` is an array of localized value struct (where locale code
        is in attribute 'locale' and actual value is in attribute 'value'), this
        function tries to find and return the translation for the given locale. If
        no match found, the value of the first object in the array is retrieved and
        translated using Babel. The translated value is returned.

        Case 2: If the given `value` is a string or an array of strings,
        translate.Translator is used to trnslate the string or phrase. If successful,
        the translated string is returned. Otherwise, an TranslationError is thrown.

        Default: Any other value type is returned without translation.

        A LocaleError is raised, if 'locale' is not a Locale or an invalid string
        representation of locale.

        :param value: A value to translate. To be qualified for translation,
                the value is either of the following: (1) a string, (2) an array
                of dict like {locale: en_US, value: "Hello world"}.
        :param language: A locale string (e.g. "en-US" or "en") or Python Locale.

        :returns: A translated string or the original value.

        :raises: LocaleError
        """
        the_ret_val = value
        thelocale = self.negotiate_loc_language(loc)

        the_case = self.determine_value_case(value)
        if the_case == 1:
            the_ret_val = self.find_loc_in_value_array(value, thelocale)
            if the_ret_val == None:
                the_ret_val = self.translate_value(
                    value[0].get('value'), thelocale)
        elif the_case == 2:
            the_ret_val = self.translate_value(value, thelocale)
        return the_ret_val

    def translate(self, value, loc: Union[list, Locale, str]):
        """
        Translate the value into specific locale:

        Case 1: If `value` is an array of localized value struct (where locale code
        is in attribute 'locale' and actual value is in attribute 'value'), this
        function tries to find and return the translation for the given locale. If
        no match found, the value of the first object in the array is retrieved,
        the first language value is returned.

        Case 2: If the given `value` is a string or an array of strings,
        just return without doing anything.

        Default: Any other value type is returned without translation.

        A LocaleError is raised, if 'locale' is not a Locale or an invalid string
        representation of locale.

        :param value: A value to translate. To be qualified for translation,
                the value is either of the following: (1) a string, (2) an array
                of dict like {locale: en_US, value: "Hello world"}.
        :param language: A locale string (e.g. "en-US" or "en") or Python Locale.

        :returns: A translated string or the original value.

        :raises: LocaleError
        """
        the_ret_val = value
        thelocale = self.negotiate_loc_language(loc)

        the_case = self.determine_value_case(value)
        if the_case == 1:
            the_ret_val = self.find_loc_in_value_array(value, thelocale)
            if the_ret_val == None:
                the_ret_val = value[0].get('value')
        elif the_case == 2:
            the_ret_val = value
        return the_ret_val

    def translate_with_case(self, value, loc: Union[list, Locale, str]):
        """
        Translate the value into specific locale:

        Case 1: If `value` is an array of localized value struct (where locale code
        is in attribute 'locale' and actual value is in attribute 'value'), this
        function tries to find and return the translation for the given locale. If
        no match found, the value of the first object in the array is retrieved,
        the first language value is returned.

        Case 2: If the given `value` is a string or an array of strings,
        just return without doing anything.

        Default: Any other value type is returned without translation.

        A LocaleError is raised, if 'locale' is not a Locale or an invalid string
        representation of locale.

        :param value: A value to translate. To be qualified for translation,
                the value is either of the following: (1) a string, (2) an array
                of dict like {locale: en_US, value: "Hello world"}.
        :param language: A locale string (e.g. "en-US" or "en") or Python Locale.

        :returns: A translated string or the original value.

        :raises: LocaleError
        """
        the_ret_val = value
        thelocale = self.negotiate_loc_language(loc)

        the_case = self.determine_value_case(value)
        if the_case == 1:
            the_ret_val = self.find_loc_in_value_array(value, thelocale)
            if the_ret_val == None:
                the_ret_val = value[0].get('value')
        elif the_case == 2:
            the_ret_val = value
        return the_ret_val, the_case

    def translate_struct(self, struct, locale_: Locale, is_config: bool = False):
        """
        Returns a copy of a given dict or list, where all language structs
        are filtered on the given locale, i.e. all language structs are replaced
        by translated values for the best matching locale.

        :param struct: A dict or list (of dicts) to filter/translate.
        :param locale_: The Babel Locale to filter on.
        :param is_config: If True, the struct is treated as a pygeoapi config.
                          This means that the first 2 levels won't be translated
                          and the translated struct is cached for speed.

        :returns: A translated dict or list
        """

        def _translate_dict(obj, level: int = 0):
            """ Recursive function to walk and translate a struct. """
            items = obj.items() if isinstance(obj, dict) else enumerate(obj)
            for k, v in items:
                if 0 <= level <= max_level and isinstance(v, (dict, list)):
                    # Skip first 2 levels (don't translate)
                    _translate_dict(v, level + 1)
                    continue
                if isinstance(v, list):
                    if self.determine_value_case(v) == 1:
                        tr = self.translate(v, locale_)
                        obj[k] = tr
                    else:
                        _translate_dict(v, level + 1)  # noqa
                    continue
                tr, caseno = self.translate_with_case(v, locale_)
                # caseno = self.determine_value_case(v)
                if caseno == 1:
                    obj[k] = tr
                elif isinstance(tr, dict):
                    # Look for language structs in next level
                    _translate_dict(tr, level + 1)
                else:
                    # Overwrite level with translated value
                    obj[k] = tr
        max_level = -1
#        max_level = 1 if is_config else -1
        result = {}
        if not struct:
            return result
        if not locale_:
            return struct

        # Check if we already translated the dict before
        result = _cfg_cache.get(locale_) if is_config else result
        if not result:
            # Create deep copy of config and translate/filter values
            result = deepcopy(struct)
            _translate_dict(result)

            # Cache translated pygeoapi configs for faster retrieval next time
            if is_config:
                _cfg_cache[locale_] = result

        return result

    def determine_value_case(self, value) -> int:
        """
        Determine the translation case based on the value:

        Case 1: If `value` is an array of localized value struct (where locale code
        is in attribute 'locale' and actual value is in attribute 'value')

        Case 2: If the given `value` is a string or an array of strings

        Default 0: Any other value.


        :param value: A value to translate. To be qualified for translation,
                the value is either of the following: (1) a string, (2) an array
                of dict like {locale: en_US, value: "Hello world"}.

        :returns: Case number. Default 0 - not qualified for translation.

        """
        if isinstance(value, str):
            return 2
        if isinstance(value, list):
            if all(isinstance(n, str) for n in value):
                return 2
            elif self._check_all_with_locale_value_pair(value):
                return 1
        return 0

    def _check_all_with_locale_value_pair(self, value):
        try:
            if all(all(key in n for key in ('locale', 'value')) for n in value):
                return True
        except:
            return False
        return False

    def find_loc_in_value_array(self, value: list, thelocale: str) -> Union[list, str]:
        """
        Retrieve the value of matching local language.

        :param value: An array of dict like {locale: en_US, value: "Hello world"}

        :returns: A string or an array of strings.
        """
        for x in value:
            if x.get('locale') == thelocale:
                return x.get('value')
        return None

    def translate_value(self, value: Union[list, str], thelocale: str) -> Union[list, str]:
        """
        Translate the value to the given local language.

        :param value: A string or An array of string.

        :param thelocale: A string of local language e.g. "en" or "en_US"

        :returns: A string or an array of strings.
        """
        the_translator = Translator(to_lang=thelocale)
        the_ret_val = value
        if isinstance(value, str):
            the_ret_val = the_translator.translate(value)
        elif isinstance(value, list):
            the_ret_val = []
            for x in value:
                the_ret_val.append(the_translator.translate(x))
        return the_ret_val

    def negotiate_loc_language(self, loc: Union[list, Locale, str]) -> str:
        if loc == None:
            return self.config.get_config()['server']['locales'][0]
        the_locales = loc
        if isinstance(loc, Locale):
            the_locales = [loc.language+"_"+loc.territory]
        elif isinstance(loc, str):
            the_locales = [loc.replace("-", "_")]
        the_locale = Locale.negotiate(
            the_locales, self.config.get_config()['server']['locales'])
        the_ret_str = the_locale.language+"_"+the_locale.territory
        return the_ret_str

    def get_config_translated(self, loc: Union[list, Locale, str]):
        thelocale = self.negotiate_loc_language(loc)
        tconfig = self.translate_struct(
            self.config.config, thelocale, is_config=True)
        return tconfig
