#!/usr/bin/env python


from __future__ import division, print_function, absolute_import, unicode_literals

import os
import os.path
import shutil
import sys
import csv
import json
import logging

import ssl
from urllib.request import urlopen, Request, URLError, HTTPError
import subprocess


try:
    from StringIO import StringIO  # python2
except ImportError:
    from io import StringIO  # python3


def get_file_list(src, tok):
    """Get list of files in directory for given date"""
    try:
        files = [
            file
            for file in csv.DictReader(  # pylint: disable=R1721
                StringIO(geturl(src + ".csv", tok)), skipinitialspace=True
            )
        ]
    except ImportError:
        files = json.loads(geturl(src + ".json", tok))
    return files


def sync_files(src, dest, tok, file):
    # currently we use filesize of 0 to indicate directory
    filesize = int(file["size"])
    path = os.path.join(dest, file["name"])
    url = src + "/" + file["name"]
    if filesize == 0:
        try:
            logging.info("creating dir: %s", path)
            os.mkdir(path)
            sync_files(src + "/" + file["name"], path, tok, src + "/" + file["name"])
        except IOError as err:
            logging.info("mkdir `%s': %s", err.filename, err.strerror)
            sys.exit(-1)
    else:
        try:
            if not os.path.exists(path):
                logging.info("downloading: %s", path)
                with open(path, "w+b") as file_h:
                    geturl(url, tok, file_h)
            else:
                logging.info("skipping: %s", path)
        except IOError as err:
            logging.info("open `%s': %s", err.filename, err.strerror)
            sys.exit(-1)
    return 0


def geturl(url, token=None, out=None):
    user_agent = "tis/download.py_1.0--" + sys.version.replace("\n", "").replace(
        "\r", ""
    )
    headers = {"user-agent": user_agent}
    if not token is None:
        headers["Authorization"] = "Bearer " + token
    try:

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        try:
            file_h = urlopen(Request(url, headers=headers), context=ctx)
            if out is None:
                return file_h.read().decode("utf-8")
            else:
                shutil.copyfileobj(file_h, out)
        except HTTPError as err:
            # logging.info("HTTP GET error code: %(code)s", {"code": err.code()})
            logging.info("HTTP GET error message: %s", err.message)
        except URLError as err:
            logging.info("Failed to make request: %s", err.reason)
        return None

    except AttributeError:
        # OS X Python 2 and 3 don't support tlsv1.1+ therefore... curl

        try:
            args = ["curl", "--fail", "-sS", "-L", "--get", url]
            for (entry_1, entry_2) in headers.items():
                args.extend(["-H", ": ".join([entry_1, entry_2])])
            if out is None:
                # python3's subprocess.check_output returns stdout as a byte string
                result = subprocess.check_output(args)
                return result.decode("utf-8") if isinstance(result, bytes) else result
            else:
                subprocess.call(args, stdout=out)
        except subprocess.CalledProcessError as err:
            logging.info(
                "curl GET error message: %s",
                (err.message if hasattr(err, "message") else err.output),
            )
        return None


def main(src, tok):
    logging.basicConfig(
        filename="logs/cloud_locations.log",
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s: %(message)s",
    )
    return get_file_list(src, tok)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
