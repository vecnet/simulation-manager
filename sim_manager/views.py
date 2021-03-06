# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt


# If this variable is None, then the view function below returns a HTTP NotFound response.
status_to_return = None

captured_request = dict()


@csrf_exempt
def test_output_url(request):
    if status_to_return is None:
        return HttpResponseNotFound()

    captured_request.clear()
    captured_request['method'] = request.method
    captured_request['body'] = request.body

    return HttpResponse(status=status_to_return)