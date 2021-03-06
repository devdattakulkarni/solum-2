# Copyright 2014 - Rackspace Hosting
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

import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import execution
from solum.api.handlers import pipeline_handler
from solum.common import exception


class ExecutionsController(rest.RestController):
    """Manages operations on the executions collection."""

    @exception.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose([execution.Execution], wtypes.text)
    def get_all(self, pipeline_id):
        """Return all executions, based on the provided pipeline_id."""
        handler = pipeline_handler.PipelineHandler(
            pecan.request.security_context)
        return [execution.Execution.from_db_model(obj,
                                                  pecan.request.host_url)
                for obj in handler.get(pipeline_id).executions]
