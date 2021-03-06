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

import sqlalchemy as sa

from solum.common import exception
from solum import objects
from solum.objects import assembly as abstract
from solum.objects.sqlalchemy import component
from solum.objects.sqlalchemy import models as sql


class Assembly(sql.Base, abstract.Assembly):
    """Represent an assembly in sqlalchemy."""

    __tablename__ = 'assembly'
    __resource__ = 'assemblies'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    trigger_id = sa.Column(sa.String(36))
    trust_id = sa.Column(sa.String(255))
    name = sa.Column(sa.String(100))
    description = sa.Column(sa.String(255))
    tags = sa.Column(sa.Text)
    plan_id = sa.Column(sa.Integer, sa.ForeignKey('plan.id'), nullable=False)
    status = sa.Column(sa.String(36))
    application_uri = sa.Column(sa.String(1024))
    username = sa.Column(sa.String(256))

    @classmethod
    def _raise_trigger_not_found(cls, item_id):
        """Raise a NotFound exception."""
        raise exception.ResourceNotFound(id=item_id, name='trigger')

    @classmethod
    def get_by_trigger_id(cls, context, trigger_id):
        try:
            session = sql.Base.get_session()
            return session.query(cls).filter_by(trigger_id=trigger_id).one()
        except sa.orm.exc.NoResultFound:
            cls._raise_trigger_not_found(trigger_id)

    def _non_updatable_fields(self):
        return set(('uuid', 'id', 'project_id'))

    @property
    def plan_uuid(self):
        return objects.registry.Plan.get_by_id(None, self.plan_id).uuid

    @plan_uuid.setter
    def plan_uuid(self, value):
        plan = objects.registry.Plan.get_by_uuid(None, value)
        self.plan_id = plan.id

    @property
    def _extra_keys(self):
        return ['plan_uuid']

    @property
    def components(self):
        session = sql.Base.get_session()
        return session.query(component.Component).filter_by(
            assembly_id=self.id).all()

    def destroy(self, context):
        session = sql.Base.get_session()
        with session.begin():
            session.query(component.Component).filter_by(
                assembly_id=self.id).delete()
            session.query(self.__class__).filter_by(
                id=self.id).delete()

    @property
    def heat_stack_component(self):
        session = sql.Base.get_session()
        return session.query(component.Component).filter_by(
            assembly_id=self.id, component_type='heat_stack').first()


class AssemblyList(abstract.AssemblyList):
    """Represent a list of assemblies in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return AssemblyList(sql.model_query(context, Assembly))
