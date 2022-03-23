from openapi_server.models.edr_feature_collection_geo_json import (
    EdrFeatureCollectionGeoJSON
)
from multidict import CIMultiDict
from typing import Tuple, Union
from aiohttp import web
from urllib.parse import urlparse, parse_qs
from ogc_edr_lib.l10n import LocaleTranslator
from openapi_server.models.extent import (
    Extent, ExtentSpatial, ExtentTemporal, ExtentVertical
)
from openapi_server.models.collection import (
    Collection
)
from openapi_server.models.collections import (
    Collections
)
from openapi_server.models.link import (
    Link as collectionLink
)
from openapi_server.models.collection_data_queries import(
    CollectionDataQueries
)
from openapi_server.models.collection_data_queries_position import(
    CollectionDataQueriesPosition
)
from ogc_edr_lib.ogc_api import OgcApi
import json
from datetime import datetime
from ogc_edr_lib.l10n import LocaleTranslator
import logging

Logger = logging.getLogger(__name__)


class OgcApiCollectionMetadataGetQueries(OgcApi):

    def get_queries(self, request: web.Request, collection_id, f=None):
        """
        List query types supported by the collection

        This will provide information about the query types that are supported
         by the chosen collection Use content negotiation to request HTML or
         JSON.

        :param collection_id: Identifier (id) of a specific collection
        :type collection_id: str
        :param f: format to return the data response in
        :type f: str

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

    def _form_collection(
        self, key, value: dict, r_media_type
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

        thelinks = self._form_collection_links(id, value, r_media_type)
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

    def _form_collection_links(self, collection_id, value, r_media_type):
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
            rel="alternate",
            title='This document as JSON',
            href='{}/collections/{}?f={}'.format(
                self.config.config['server']['url'], collection_id, "json")
        )
        if (
            r_media_type is None
            or r_media_type == "application/json"
        ):
            thelink.rel = "self"
        thelinks.append(thelink)
        # html
        thelink = collectionLink(
            type="text/html",
            rel="alternate",
            title='This document as HTML',
            href='{}/collections/{}?f={}'.format(
                self.config.config['server']['url'], collection_id, "html")
        )
        if (
            r_media_type == "text/html"
        ):
            thelink.rel = "self"
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
        thewriter = theplugin.cls({})
        return thewriter.write(
            options={
                "config": self.config.get_config(),
                "openapi": self.config.load_openapi_file(),
                "locale": loc
            },
            data=lp.to_dict())

    def _form_collection_data_query(
        self, dataqueries: Union[dict, None],
        querytype: str,
        loc="en_US"
    ):
        dq = dataqueries.get(querytype, None)
        if dq is None:
            return dq
        dqp = CollectionDataQueriesPosition()
        dqlink = collectionLink.from_dict(dq.get("link"))
        dqp.link = dqlink
        return dq
