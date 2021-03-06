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

import mock

from solum.api.handlers import plan_handler
from solum.tests import base
from solum.tests import fakes
from solum.tests import utils


@mock.patch('solum.objects.registry')
class TestPlanHandler(base.BaseTestCase):
    def setUp(self):
        super(TestPlanHandler, self).setUp()
        self.ctx = utils.dummy_context()

    def test_plan_get(self, mock_registry):
        mock_registry.Plan.get_by_uuid.return_value = {}
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.get('test_id')
        self.assertIsNotNone(res)
        get_by_uuid = mock_registry.Plan.get_by_uuid
        get_by_uuid.assert_called_once_with(self.ctx, 'test_id')

    def test_plan_get_all(self, mock_registry):
        mock_registry.PlanList.get_all.return_value = {}
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.get_all()
        self.assertIsNotNone(res)
        mock_registry.PlanList.get_all.assert_called_once_with(self.ctx)

    def test_plan_update(self, mock_registry):
        data = {'user_id': 'new_user_id', 'name': 'new_name',
                'project_id': 'new_proj_id', 'uuid': 'new_uuid'}
        db_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_uuid.return_value = db_obj
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.update('test_id', data)
        self.assertEqual(db_obj.user_id, res.user_id)
        self.assertEqual(db_obj.name, res.name)
        self.assertEqual(db_obj.project_id, res.project_id)
        self.assertEqual(db_obj.uuid, res.uuid)
        db_obj.save.assert_called_once_with(self.ctx)
        mock_registry.Plan.get_by_uuid.assert_called_once_with(self.ctx,
                                                               'test_id')

    def test_plan_create(self, mock_registry):
        data = {'name': 'new_name',
                'uuid': 'input_uuid'}
        db_obj = fakes.FakePlan()
        mock_registry.Plan.return_value = db_obj
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.create(data)
        db_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)

    def test_plan_create_with_param(self, mock_registry):
        data = {'name': 'new_name',
                'uuid': 'input_uuid',
                'parameters': {'username': 'user_a'}}
        db_obj = fakes.FakePlan()
        param_obj = fakes.FakeParameter()
        mock_registry.Plan.return_value = db_obj
        mock_registry.Parameter.return_value = param_obj
        handler = plan_handler.PlanHandler(self.ctx)
        res = handler.create(data)
        db_obj.create.assert_called_once_with(self.ctx)
        param_obj.create.assert_called_once_with(self.ctx)
        self.assertEqual(db_obj, res)

    def test_plan_delete(self, mock_registry):
        db_obj = fakes.FakePlan()
        mock_registry.Plan.get_by_uuid.return_value = db_obj
        handler = plan_handler.PlanHandler(self.ctx)
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(self.ctx)
        mock_registry.Plan.get_by_uuid.assert_called_once_with(self.ctx,
                                                               'test_id')

    def test_plan_delete_with_param(self, mock_registry):
        db_obj = fakes.FakePlan()
        param_obj = fakes.FakeParameter()
        mock_registry.Plan.get_by_uuid.return_value = db_obj
        mock_registry.Parameter.get_by_plan_id.return_value = param_obj
        handler = plan_handler.PlanHandler(self.ctx)
        handler.delete('test_id')
        db_obj.destroy.assert_called_once_with(self.ctx)
        param_obj.destroy.assert_called_once_with(self.ctx)
        mock_registry.Plan.get_by_uuid.assert_called_once_with(self.ctx,
                                                               'test_id')
        mock_registry.Parameter.get_by_plan_id.assert_called_once_with(
            self.ctx, db_obj.id)
