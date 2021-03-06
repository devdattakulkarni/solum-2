# Copyright 2014 - Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import solum
from solum.common import context
from solum.common import trace_data
from solum.tests import base

solum.TLS.trace = trace_data.TraceData()

# Just putting highly recognizable values in context
CONTEXT = context.RequestContext(
    '_auth_token_', '_user_', '_tenant_', '_domain_', '_user_domain_',
    '_project_domain_', '_is_admin_', '_read_only_', '_request_id_',
    '_user_name_', '_roles_', '_auth_url_',
    auth_token_info='_auth_token_info_')


class TestTraceData(base.BaseTestCase):
    """Tests the TraceData class."""
    def test_auto_clear(self):
        """auto_clear success and then a failure case."""
        solum.TLS.trace.auto_clear = True
        solum.TLS.trace.auto_clear = False
        try:
            solum.TLS.trace.auto_clear = 'fail'
        except AssertionError:
            pass
        else:
            self.assertTrue(False)

    def test_import_context(self):
        """Test importing Oslo RequestContext."""
        solum.TLS.trace.clear()
        solum.TLS.trace.import_context(CONTEXT)
        self.assertEqual(
            solum.TLS.trace._user_data,
            {'user': '_user_', 'tenant': '_tenant_'})
        self.assertEqual(({
            'domain': '_domain_',
            'instance_uuid': None,
            'is_admin': '_is_admin_',
            'project_domain': '_project_domain_',
            'read_only': '_read_only_',
            'roles': '_roles_',
            'show_deleted': False,
            'user_domain': '_user_domain_',
            'user_identity': '_user_ _tenant_ _domain_ '
            '_user_domain_ _project_domain_',
            'user_name': '_user_name_',
            'auth_url': '_auth_url_',
            'auth_token_info': '_auth_token_info_'
        }), solum.TLS.trace._support_data)

    def test_info_commands(self):
        """Test trace setting functions."""
        solum.TLS.trace.clear()
        solum.TLS.trace.request_id = '98765'
        solum.TLS.trace.user_info(ip_addr="1.2.3.4", user_id=12345)
        solum.TLS.trace.support_info(confidential_data={"a": "b", "c": "d"})
        self.assertEqual(
            solum.TLS.trace._user_data,
            {'ip_addr': '1.2.3.4', 'user_id': 12345})
        self.assertEqual(
            solum.TLS.trace._support_data,
            {'confidential_data': {'a': 'b', 'c': 'd'}})
        self.assertEqual(
            solum.TLS.trace.request_id,
            '98765')
