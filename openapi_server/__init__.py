import os
import connexion

from aiohttp import web

# -----customize--------
from ogc_edr_lib.connexion_ext.validation_ext import (
   MyParameterValidator, MyRequestBodyValidator, MyResponseBodyValidator
 )
from ogc_edr_lib.connexion_ext.uri_parsers import (
    MyOpenAPIURIParser)


def main():
    # ---custom validator-----
    validator_map = {
        'body': MyRequestBodyValidator,
        'parameter': MyParameterValidator,
        'response': MyResponseBodyValidator
        }
    options = {
        'uri_parser_class': MyOpenAPIURIParser,
        "swagger_ui": True
        }
    specification_dir = os.path.join(os.path.dirname(__file__), 'openapi')
    app = connexion.AioHttpApp(
        __name__, specification_dir=specification_dir, options=options)
    app.add_api('openapi.yaml',
                arguments={'title': 'Environmental Data Retrieval API&#39;s'},
                pythonic_params=True,
                pass_context_arg_name='request',
                validator_map=validator_map,
                strict_validation=False)
    static_dir = os.path.join(os.path.dirname(__file__), '../static')
    app.app.add_routes(
        [web.static("/static", static_dir,
                    follow_symlinks=True, show_index=True)]
        )
    app.run(port=8080)
