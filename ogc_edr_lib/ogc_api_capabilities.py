import json
from ogc_edr_lib.ogc_api import OgcApi
from openapi_server.models.landing_page import (
 LandingPage, LandingPageProvider, LandingPageContact
)
from openapi_server.models.link import (
 Link as collectionLink
)
from openapi_server.models.conf_classes import (
    ConfClasses
)

from openapi_server.models.collections import (
    Collections
)

from openapi_server.models.collection import (
    Collection
)
from openapi_server.models.extent import (
    Extent, ExtentSpatial, ExtentTemporal, ExtentVertical
)
from openapi_server.models.collection_data_queries import(
    CollectionDataQueries
)
from openapi_server.models.collection_data_queries_position import(
    CollectionDataQueriesPosition
)
from ogc_edr_lib.l10n import LocaleTranslator
from urllib.parse import urlparse, parse_qs

from aiohttp import web

from typing import Tuple, Union

from multidict import CIMultiDict

import datetime

import logging

Logger = logging.getLogger(__name__)


class OgcApiCapabilities(OgcApi):
    def _select_items_by_key_value(
            self, pdict: dict, key: str, value: str):
        """
        helper function to filter a dict by a dict key

        :param dict_: ``dict``
        :param key: dict key
        :param value: dict key value

        :returns: filtered ``dict``
        """
        return {k: v for (k, v) in pdict.items() if v[key] == value}

    def list_collections(
            self, request: web.Request, bbox=None, datetime=None, f=None):
        """
        List collections

        :param request: A request object
        :param bbox: bounding bbox
        :param datetime: datetime
        :param f: format. It can be either in json, html, etc. Or fully spelled
        out as application/json, text/html

        :returns: tuple of headers, status code, content
        """
        qstrs = parse_qs(request.query_string)
        the_locale = qstrs.get('locale')
        the_formats = qstrs.get('f')
        the_formats = self.get_full_media_type_from_f_param(the_formats)
        best_match = self._negotiate_content_best_match(request, the_formats)

        translator = LocaleTranslator()
        theresources = translator.get_config_translated(
            the_locale)["resources"]
        thecollections = self._select_items_by_key_value(
            theresources, 'type', "collection")
        ret_collections = list()
        for k, v in thecollections.items():
            thecollection = self._form_collection(k, v)
            ret_collections.append(thecollection)
        ret_links = list()

        ret_collection_list = Collections(
            links=ret_links, collections=ret_collections)

        retcontent = self._format_content_collections(
            ret_collection_list, best_match)
        headers = CIMultiDict()
        headers["Content-Type"] = best_match

        return headers, 200, retcontent

    def get_queries(self, request: web.Request, collection_id, f=None):
        """
        List collections

        :param request: A request object
        :param bbox: bounding bbox
        :param datetime: datetime
        :param f: format. It can be either in json, html, etc. Or fully spelled
        out as application/json, text/html

        :returns: tuple of headers, status code, content
        """
        qstrs = parse_qs(request.query_string)
        the_locale = qstrs.get('locale')
        the_formats = qstrs.get('f')
        the_formats = self.get_full_media_type_from_f_param(the_formats)
        best_match = self._negotiate_content_best_match(request, the_formats)

        translator = LocaleTranslator()
        thecollection_value = translator.get_config_translated(
            the_locale)["resources"][collection_id]
        thecollection_metadata = self._form_collection(
            collection_id, thecollection_value, best_match)

        retcontent = self._format_content_collection(
            thecollection_metadata, best_match)
        headers = CIMultiDict()
        headers["Content-Type"] = best_match

        return headers, 200, retcontent

    def _form_collection(
        self, key, value: dict
    ):
        """
        Form a collection record from key-value pair.

        :param key: A unique id for collection
        :param value: The collection metadata in config file.

        :returns: Collection
        """
        title = self._retrieve_collection_item(value, "title")
        id = key
        description = self._retrieve_collection_item(value, "description")
        keywords = self._retrieve_collection_item(value, "keywords")
        extent = self._parse_collection_extent(value)

        thelinks = self._form_collection_links(id, value)
        data_queries = self._parse_collection_data_queries(
            value=value)
        crs = self._retrieve_collection_item(value, "crs")
        output_formats = self._retrieve_collection_item(
            value, "output_formats")
        parameter_names = self._retrieve_collection_item(
            value, "parameter_names")
        thecollection = Collection(
            description=description, keywords=keywords,
            id=id, title=title, extent=extent,
            links=thelinks, data_queries=data_queries,
            crs=crs, output_formats=output_formats,
            parameter_names=parameter_names)
        return thecollection

    def _retrieve_collection_item(
            self, value, item: str) -> Union[str, list, None]:
        try:
            return value[item]
        except BaseException as error:
            Logger.warning(error)
            return None

    def _parse_collection_extent(self, value) -> Union[Extent, None]:
        try:
            extent = Extent.from_dict(value["extents"])
            return extent
        except BaseException as error:
            Logger.warning(error)
            return None

    def _parse_collection_data_queries(
            self, value: dict):
        try:
            dataqueries = CollectionDataQueries.from_dict(
                value["data_queries"])
            return dataqueries
        except BaseException as error:
            Logger.warning(error)
            return None

    def _form_collection_links(self, collection_id, value):
        thelinks = []
        for lk in value["links"]:
            thelink = collectionLink(
                rel=lk["rel"],
                type=lk["type"],
                title=lk["title"],
                href=lk["href"]
            )
            if "hreflang" in lk:
                thelink.hreflang = lk["hreflang"]
            thelinks.append(thelink)
        # json
        thelink = collectionLink(
            type="application/json",
            rel="collection",
            title='This document as JSON',
            href='{}/collections/{}?f={}'.format(
                self.config.config['server']['url'], collection_id, "json")
        )
        thelinks.append(thelink)
        # html
        thelink = collectionLink(
            type="text/html",
            rel="alternate",
            title='This document as HTML',
            href='{}/collections/{}?f={}'.format(
                self.config.config['server']['url'], collection_id, "html")
        )
        thelinks.append(thelink)
        return thelinks

    def _negotiate_content_best_match(self, request: web.Request,
                                      the_formats: Union[list, None]):
        # get the best_match
        response_formats = self.config.get_response_formats("/")
        header_accept = ",".join(request.headers.getall('ACCEPT', '*/*'))
        best_match = None
        Logger.debug("header_accept= {}".format(header_accept))
        Logger.debug("the_formats= {}".format(the_formats))

        if the_formats is not None:
            best_match = self.config.get_mimetype_best_match(
                response_formats, ",".join(the_formats))
        if best_match is None:
            best_match = self.config.get_mimetype_best_match(
                response_formats, header_accept)
        return best_match

    def get_full_media_type_from_f_param(self, f_formats: list):
        if f_formats is None:
            return None
        ret_formats = []
        for f in f_formats:
            the_f = self._get_full_media_type_from_f_param(f)
            ret_formats.append(the_f)
        return ret_formats

    def _get_full_media_type_from_f_param(self, f_format):
        ret_format = f_format
        if f_format.lower() == 'json':
            ret_format = 'application/json'
        elif f_format.lower() == 'html':
            ret_format = 'text/html'
        return ret_format

    def _format_content_collection(
            self, lp: Collections, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "collection", mediatype)
        print("theplugin-name=", theplugin.name)
        thewriter = theplugin.cls({})
        return thewriter.write(
            options={
                "config": self.config.get_config(),
                "openapi": self.config.load_openapi_file(),
                "locale": loc
            },
            data=lp.to_dict())

    def get_requirements_classes(
            self, request: web.Request) -> Tuple[dict, int, str]:
        """
        Provide conformance definition

        :param request: A request object

        :returns: tuple of headers, status code, content
        """

        qstrs = parse_qs(request.query_string)
        the_locale = qstrs.get('locale')
        the_formats = qstrs.get('f')
        the_formats = self.get_full_media_type_from_f_param(the_formats)

        conformlist = self.config.config['metadata']['conformto']
        conform = ConfClasses(conforms_to=conformlist)

        best_match = self._negotiate_content_best_match(request, the_formats)

        retcontent = self._format_content_conformance(conform, best_match)
        headers = CIMultiDict()
        headers["Content-Type"] = best_match

        return headers, 200, retcontent

    def landing_page(self, request: web.Request) -> Tuple[dict, int, str]:
        """
        OGC API landing landing_page

        :param request: A request object

        :returns: tuples of headers, status code, content
        """

        the_translator = LocaleTranslator()

        qstrs = parse_qs(request.query_string)
        the_locale = qstrs.get('locale')
        the_formats = qstrs.get('f')
        the_formats = self.get_full_media_type_from_f_param(the_formats)

        theconfig = the_translator.get_config_translated(the_locale)

        title = self._retrieve_server_metadata_id_item(theconfig, "title")

        description = self._retrieve_server_metadata_id_item(
            theconfig, "description")

        keywords = self._retrieve_server_metadata_id_item(
            theconfig, 'keywords')

        lpprovider = LandingPageProvider(
            name=self.config.get_config()['metadata']['provider']['name'],
            url=self.config.get_config()['metadata']['provider']['url']
            )
        lpcontact = self._form_landing_page_contact()
        thelinks = self._form_landing_page_links()

        lp = LandingPage(title=title,
                         description=description,
                         keywords=keywords,
                         provider=lpprovider,
                         contact=lpcontact,
                         links=thelinks)

        best_match = self._negotiate_content_best_match(request, the_formats)
        Logger.debug("best_match={}".format(best_match))

        retcontent = self._format_content(lp, best_match)
        headers = CIMultiDict()
        headers["Content-Type"] = best_match
        return headers, 200, retcontent

    def _retrieve_server_metadata_id_item(self, theconfig: dict, item: str):
        try:
            retobj = theconfig['metadata']['identification'][item]
            return retobj
        except BaseException as error:
            Logger.warning("Not find {} - {}".format_map(item, error))
            return "GMU EDR Service Implementation"

    def _format_content(
            self, lp: LandingPage, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "landingpage", mediatype)
        Logger.debug("theplugin-name={}".format(theplugin.name))
        thewriter = theplugin.cls({})
        return thewriter.write(
            options={
                "config": self.config.get_config(),
                "openapi": self.config.load_openapi_file(),
                "locale": loc
            },
            data=lp.to_dict())

    def _form_landing_page_contact(self):
        lpcontact = LandingPageContact(
            email=self.config.get_config()['metadata']['contact']['email'],
            phone=self.config.get_config()['metadata']['contact']['phone'],
            fax=self.config.get_config()['metadata']['contact']['fax'],
            hours=self.config.get_config()['metadata']['contact']['hours'],
            instructions=self.config.get_config()[
                'metadata']['contact']['instructions'],
            address=self.config.get_config()['metadata']['contact']['address'],
            city=self.config.get_config()['metadata']['contact']['city'],
            stateorprovince=self.config.get_config()[
                'metadata']['contact']['stateorprovince'],
            postal_code=self.config.get_config()[
                'metadata']['contact']['postalcode'],
            country=self.config.get_config()['metadata']['contact']['country']
        )
        return lpcontact

    def _form_landing_page_links(self):
        thelinks = []
        thelink = collectionLink(
            rel='self',
            type="application/json",
            title="This document as JSON",
            href='{}?f={}'.format(
                self.config.get_config()['server']['url'], "json")
        )
        thelinks.append(thelink)
        thelink = collectionLink(
            rel='service-desc',
            type="application/vnd.oai.openapi+json;version=3.0",
            title="The OpenAPI definition as JSON",
            href='{}/openapi.json'.format(
                self.config.get_config()['server']['url'])
        )
        thelinks.append(thelink)
        thelink = collectionLink(
            rel='service-desc',
            type="text/yaml",
            title="The OpenAPI definition as YAML",
            href='{}/openapi.yaml'.format(
                self.config.get_config()['server']['url'])
        )
        thelinks.append(thelink)
        thelink = collectionLink(
            rel='service-doc',
            type="text/html",
            title="The OpenAPI UI",
            href='{}/ui'.format(
                self.config.get_config()['server']['url'])
        )
        thelinks.append(thelink)
        thelink = collectionLink(
            rel='conformance',
            type="application/json",
            title="Confomance",
            href='{}/ui'.format(
                self.config.get_config()['server']['url'])
        )
        thelinks.append(thelink)
        thelink = collectionLink(
            rel='collections',
            type="application/json",
            title="Collections",
            href='{}/collections'.format(
                self.config.get_config()['server']['url'])
        )
        thelinks.append(thelink)
        thelink = collectionLink(
            rel='collections',
            type="application/json",
            title="Collections",
            href='{}/groups'.format(
                self.config.get_config()['server']['url'])
        )
        thelinks.append(thelink)
        return thelinks

    def get_full_media_type_from_f_param(self, f_formats: list):
        if f_formats is None:
            return None
        ret_formats = []
        for f in f_formats:
            the_f = self._get_full_media_type_from_f_param(f)
            ret_formats.append(the_f)
        return ret_formats

    def _get_full_media_type_from_f_param(self, f_format):
        ret_format = f_format
        if f_format.lower() == 'json':
            ret_format = 'application/json'
        elif f_format.lower() == 'html':
            ret_format = 'text/html'
        return ret_format

    def _format_content_conformance(
            self, lp: ConfClasses, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "conformance", mediatype)
        print("theplugin-name=", theplugin.name)
        thewriter = theplugin.cls({})
        return thewriter.write(
            options={
                "config": self.config.get_config(),
                "openapi": self.config.load_openapi_file(),
                "locale": loc
            },
            data=lp.to_dict())

    def _format_content_collections(
            self, lp: Collections, mediatype: str, loc="en_US"):
        theplugin = self.config.pluginmanager.get_plugin_by_category_media_type(
            "formatter", "collections", mediatype)
        print("theplugin-name=", theplugin.name)
        thewriter = theplugin.cls({})
        return thewriter.write(
            options={
                "config": self.config.get_config(),
                "openapi": self.config.load_openapi_file(),
                "locale": loc
            },
            data=lp.to_dict())
