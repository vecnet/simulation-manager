# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from path import path
import requests


def download_file(url, local_path):
    """
    Download a file from a URL.
    """
    r = requests.get(url, stream=True)
    with open(local_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


def get_file_contents(filenames, callback, dir_path=None):
    """
    Get the contents for a set of text files.

    :param list filenames: Names of the files.
    :param callback: A callable object that's called with the name of each file before its contents are read.
    :param str dir_path: Where the files are located (default: current working directory

    :return dict : A dictionary where key = filename and value = list of strings (one per line in the file)
    """
    if dir_path is None:
        dir_path = path.getcwd().abspath()
    file_contents = dict()
    for filename in filenames:
        callback(filename)
        file_path = dir_path / filename
        if file_path.exists():
            with file_path.open('r') as f:
                file_contents[filename] = f.readlines()
        else:
            # File not found
            # This can be perfectly valid case for OpenMalaria model, if survey or
            # continuous output is disabled.
            # Skip this file
            pass
    return file_contents
