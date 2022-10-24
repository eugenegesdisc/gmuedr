#!/bin/env python

import argparse
import os
import requests
from urllib.parse import urlparse
from .command_factory import CommandFactory

# overriding requests.Session.rebuild_auth to mantain headers when redirected


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():
    parser = argparse.ArgumentParser(
        description="Download data")
    parser.add_argument(
        'action', choices=['convert', 'combine', 'list'],
        help='action on processing data')
    parser.add_argument(
        '-l', '--list', required=False, type=str,
        help='files to process. support wildcards. E.g. /tdir/*.HDF5')
    parser.add_argument(
        '-d', '--directory', required=False, type=str,
        help='target directory or fullpath to the combined file')
    parser.add_argument(
        '-v', '--variables', required=False, type=str,
        help='variables as comma-separated list')
    parser.add_argument(
        '-p', '--password', required=False, type=str, help='password')
    parser.add_argument(
        '-s', '--suffix', required=False, default=".nc4",
        type=str, help='suffix of files to be downloaded')
    parser.add_argument(
         '--debug', required=False, type=str2bool, nargs='?',
         const=True, default=False, help='debug')
    args = parser.parse_args()

    print("args=", args)
    CommandFactory.create(args.action, args).execute()
