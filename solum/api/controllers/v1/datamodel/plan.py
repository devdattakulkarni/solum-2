# Copyright 2014 - Rackspace US, Inc.
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

import uuid

import six
import wsme
from wsme.rest import json as wjson
from wsme import types as wtypes

from solum.api.controllers.v1.datamodel import types as api_types


class Requirement(wtypes.Base):

    requirement_type = wtypes.text
    "Type of requirement."

    fulfillment = wtypes.text
    "The ID of the service."


class ServiceReference(wtypes.Base):

    name = wtypes.text
    "The name of the service to be used."

    id = wtypes.text
    "The ID of the service to be used."

    characteristics = [wtypes.text]
    "A list of characteristics required from the service."


class Artifact(wtypes.Base):
    """Artifact."""

    name = wtypes.text
    "Name of the artifact."

    artifact_type = wtypes.text
    "Type of artifact."

    content = {wtypes.text: api_types.MultiType(wtypes.text,
                                                six.types.BooleanType)}
    "Type specific content as a flat dict."

    language_pack = wtypes.text
    "The Language pack required for this artifact."

    requirements = [Requirement]
    "List of requirements for the artifact."

    unittest_cmd = wtypes.text
    "Optional unit test command for the artifact."

    repo_token = wtypes.text
    "The OAuth token to access repository"

    def __init__(self, **kwargs):
        if 'requirements' in kwargs:
            kwargs['requirements'] = [Requirement(**re)
                                      for re in kwargs.get('requirements', [])]
        super(Artifact, self).__init__(**kwargs)


class Plan(api_types.Base):
    """Representation of an Plan file.

    The Plan resource is a representation of a Plan file. Plans are used to
    create Assembly resources. A Plan resource may be used to create an
    arbitrary number of Assembly instances. They use artifacts and services
    to indicate what will be used to generate the plan, and what services
    Solum can use to satisfy them. Note: Plan files are YAML and Plan resources
    are the REST representation of the Plan file after services have been
    matched to ones offered by Solum.
    """

    artifacts = [Artifact]
    """List of artifacts defining the plan."""

    services = [ServiceReference]
    """List of services needed by the plan."""

    parameters = {wtypes.text: api_types.MultiType(wtypes.text,
                                                   six.integer_types,
                                                   six.types.BooleanType,
                                                   six.types.FloatType)}
    """User defined parameters"""

    def __init__(self, **kwargs):
        if 'artifacts' in kwargs:
            kwargs['artifacts'] = [Artifact(**art)
                                   for art in kwargs.get('artifacts', [])]
        if 'services' in kwargs:
            kwargs['services'] = [ServiceReference(**sr)
                                  for sr in kwargs.get('services', [])]
        super(Plan, self).__init__(**kwargs)

    @classmethod
    def sample(cls):
        return cls(uri='http://example.com/v1/plans/x1',
                   name='Example-plan',
                   type='plan',
                   tags=['small'],
                   artifacts=[{
                       'name': 'My-python-app',
                       'artifact_type': 'git_pull',
                       'content': {'href': 'git://example.com/project.git',
                                   'private': False},
                       'language_pack': str(uuid.uuid4()),
                       'requirements': [{
                           'requirement_type': 'git_pull',
                           'fulfillment': 'id:build'}]}],
                   services=[{
                       'name': 'Build-Service',
                       'id': 'build',
                       'characteristics': ['python_build_service']}],
                   project_id='1dae5a09ef2b4d8cbf3594b0eb4f6b94',
                   user_id='55f41cf46df74320b9486a35f5d28a11',
                   description='A plan with no services or artifacts shown')

    @classmethod
    def from_db_model(cls, m, host_url):
        return cls(**(m.raw_content))

    def as_dict(self, db_model):
        base = super(Plan, self).as_dict_from_keys(['name', 'description'])
        if self.artifacts is not wsme.Unset:
            base.update({'artifacts': [wjson.tojson(Artifact, art)
                                       for art in self.artifacts]})
        if self.services is not wsme.Unset:
            base.update({'services': [wjson.tojson(ServiceReference, ref)
                                      for ref in self.services]})
        if self.parameters is not wsme.Unset:
            base.update({'parameters': self.parameters})
        return base
