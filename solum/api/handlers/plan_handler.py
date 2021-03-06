# Copyright (c) 2014 Rackspace Hosting
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

import base64
import errno
import os
import shelve
import uuid

from Crypto.PublicKey import RSA
from oslo.config import cfg

from solum.api.handlers import handler
from solum.common import clients
from solum import objects

cfg.CONF.import_opt('git_secrets_file', 'solum.common.clients',
                    group='barbican_client')
cfg.CONF.import_opt('barbican_disabled', 'solum.common.clients',
                    group='barbican_client')
secrets_file = cfg.CONF.barbican_client.git_secrets_file
barbican_disabled = cfg.CONF.barbican_client.barbican_disabled


class PlanHandler(handler.Handler):
    """Fulfills a request on the plan resource."""

    def get(self, id):
        """Return a plan."""
        return objects.registry.Plan.get_by_uuid(self.context, id)

    def update(self, id, data):
        """Modify existing plan."""
        db_obj = objects.registry.Plan.get_by_uuid(self.context, id)
        if 'name' in data:
            db_obj.name = data['name']
        db_obj.raw_content.update(dict((k, v) for k, v in data.items()
                                       if k != 'parameters'))
        db_obj.save(self.context)
        return db_obj

    def delete(self, id):
        """Delete existing plan."""
        db_obj = objects.registry.Plan.get_by_uuid(self.context, id)
        self._delete_params(db_obj.id)
        if db_obj.deploy_keys_uri:
            if barbican_disabled:
                s = shelve.open(secrets_file)
                del s[db_obj.deploy_keys_uri.encode("utf-8")]
                s.close()
            else:
                client = clients.OpenStackClients(None).barbican().admin_client
                client.secrets.delete(db_obj.deploy_keys_uri)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new plan."""
        db_obj = objects.registry.Plan()
        if 'name' in data:
            db_obj.name = data['name']
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        deploy_keys = []
        for artifact in data.get('artifacts', []):
            if (('content' not in artifact) or
                    ('private' not in artifact['content']) or
                    (not artifact['content']['private'])):
                continue
            new_key = RSA.generate(2048)
            public_key = new_key.publickey().exportKey("OpenSSH")
            private_key = new_key.exportKey("PEM")
            artifact['content']['public_key'] = public_key
            deploy_keys.append({'source_url': artifact['content']['href'],
                                'private_key': private_key})
        if deploy_keys:
            encoded_payload = base64.b64encode(bytes(str(deploy_keys)))
            if barbican_disabled:
                try:
                    os.makedirs(os.path.dirname(secrets_file), 0o700)
                except OSError as ex:
                    if ex.errno != errno.EEXIST:
                        raise
                s = shelve.open(secrets_file)
                try:
                    s[db_obj.uuid] = encoded_payload
                    db_obj.deploy_keys_uri = db_obj.uuid
                finally:
                    s.close()
            else:
                client = clients.OpenStackClients(None).barbican().admin_client
                db_obj.deploy_keys_uri = client.secrets.create(
                    name=db_obj.uuid,
                    payload=encoded_payload,
                    payload_content_type='application/octet-stream',
                    payload_content_encoding='base64').store()
        db_obj.raw_content = dict((k, v) for k, v in data.items()
                                  if k != 'parameters')
        db_obj.create(self.context)

        if 'parameters' in data:
            self._create_params(db_obj.id, data['parameters'])
        return db_obj

    def get_all(self):
        """Return all plans."""
        return objects.registry.PlanList.get_all(self.context)

    def _create_params(self, plan_id, parameters):
        param_obj = objects.registry.Parameter()
        param_obj.plan_id = plan_id
        param_obj.user_defined_params = parameters
        param_obj.create(self.context)

    def _delete_params(self, plan_id):
        param_obj = objects.registry.Parameter.get_by_plan_id(self.context,
                                                              plan_id)
        if param_obj:
            param_obj.destroy(self.context)
