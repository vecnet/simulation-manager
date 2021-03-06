# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls import include, patterns, url

from sim_manager.api import v1_api

urlpatterns = patterns('',
    url(r'^test-output-url/$', 'sim_manager.views.test_output_url', name='test-output-url'),
    url(r'', include(v1_api.urls)),
)
