# This file is part of the Simulation Manager project for VecNet.
# For copyright and licensing information about this project, see the
# NOTICE.txt and LICENSE.md files in its top-level directory; they are
# available at https://github.com/vecnet/simulation-manager
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from tastypie import fields
from tastypie.api import Api
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest, NotFound, ImmediateHttpResponse
from tastypie.http import HttpApplicationError
from tastypie.resources import ALL, ModelResource, Resource

from vecnet.simulation import DictConvertible, ExecutionRequest

from sim_manager.models import Simulation, SimulationGroup
from sim_manager.scripts import api_urls


class ModelResourceWithRestrictedUpdate(ModelResource):
    """
    Base class for resources based on data models where only certain fields can be updated via a PATCH.

    The fields that can be updated must be specified in the derived class' Meta.allowed_update_fields member.
    """

    def update_in_place(self, request, original_bundle, new_data):
        """
        Update the bundle with new data from the request.  The new data is checked to make sure it only has allowed
        fields (no restricted fields).
        """
        # Based on http://stackoverflow.com/q/13704344/1258514
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest(
                'Only these fields can be updated: %s' % ', '.join(
                    self._meta.allowed_update_fields
                )
            )
        return super(ModelResourceWithRestrictedUpdate, self).update_in_place(request, original_bundle, new_data)


class SimulationGroupResource(ModelResourceWithRestrictedUpdate):
    class Meta:
        queryset = SimulationGroup.objects.all()
        resource_name = 'sim-groups'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch']
        authentication = ApiKeyAuthentication()
        authorization = Authorization()

        # Metadata not used by Tastypie
        allowed_update_fields = ['script_status']  # Used by ModelResourceWithRestrictedUpdate.update_in_place method

    def obj_create(self, bundle, **kwargs):
        """
        Create a new resource object.
        """
        #  Validate the execution request by converting it from the data dictionary
        try:
            execution_request = ExecutionRequest.from_dict(bundle.data)
        except DictConvertible.Error as exc:
            error_info = {
                'error': exc.error,
                'error_details': exc.details,
            }
            raise ImmediateHttpResponse(self.error_response(bundle.request, error_info))

        kwargs['submitter'] = bundle.request.user
        bundle = super(SimulationGroupResource, self).obj_create(bundle, **kwargs)
        group = bundle.obj

        try:
            group.setup_working_dir(execution_request)
        except Exception as e:
            error_info = {
                'error': "problem occurred when setting up the group's working directory",
                'error_details': "%s" % e,
            }
            raise ImmediateHttpResponse(self.error_response(bundle.request, error_info,
                                                            response_class=HttpApplicationError))

        # Put the API URLs for the group and the simulations endpoint into a file in the working directory.
        group_url = bundle.request.build_absolute_uri(self.get_resource_uri(bundle))
        simulations_url = bundle.request.build_absolute_uri(SimulationResource().get_resource_uri())
        api_urls.write_for_group(group.working_dir, group_url, simulations_url)

        # Start the background process with the submit_group.py script
        if not group.start_submission_script():
            error_info = {
                'error': "problem occurred when starting the script to submit the group's simulations",
                'error_details': group.script_error,
            }
            raise ImmediateHttpResponse(self.error_response(bundle.request, error_info,
                                                            response_class=HttpApplicationError))

        return bundle


class SimulationResource(ModelResourceWithRestrictedUpdate):
    group = fields.ForeignKey(SimulationGroupResource, 'group')

    class Meta:
        queryset = Simulation.objects.all()
        resource_name = 'simulations'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch']
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'group': ALL,
        }

        # Metadata not used by Tastypie
        allowed_update_fields = ['batch_job_id', 'error_details', 'status']  # See the inherited update_in_place method

    def obj_create(self, bundle, **kwargs):
        """
        Create a new Simulation resource object.
        """
        bundle = super(SimulationResource, self).obj_create(bundle, **kwargs)
        simulation = bundle.obj

        simulation.setup_working_dir()
        bundle.data['working_dir'] = simulation.working_dir  # So it's included in the response

        # Put the API URL for the simulation into a file in the working directory.
        simulation_url = bundle.request.build_absolute_uri(self.get_resource_uri(bundle))
        api_urls.write_for_simulation(simulation.working_dir, simulation_url)

        return bundle


class Square:
    """
    The square of an integer.
    """
    def __init__(self, number):
        self.number = number
        self.square = number * number


class SquareResource(Resource):
    """
    Represents squares of integers.  Used to test API authentication.
    """
    class Meta:
        resource_name = 'squares'
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        authentication = ApiKeyAuthentication()

    MIN_NUMBER = -8
    MAX_NUMBER = 10

    number = fields.IntegerField(attribute='number', unique=True,
                                 help_text='integer between %d and %d' % (MIN_NUMBER, MAX_NUMBER))
    square = fields.IntegerField(attribute='square', help_text='square of number')

    def obj_get(self, bundle, **kwargs):
        pk = kwargs['pk']
        try:
            number = int(pk)
        except ValueError:
            raise BadRequest('"%s" is not a valid integer' % pk)
        if number < SquareResource.MIN_NUMBER or SquareResource.MAX_NUMBER < number:
            raise NotFound('number is not between %d and %d' % (SquareResource.MIN_NUMBER, SquareResource.MAX_NUMBER))
        return Square(number)

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = dict()
        if isinstance(bundle_or_obj, Bundle):
            obj = bundle_or_obj.obj
        else:
            obj = bundle_or_obj
        kwargs['pk'] = obj.number
        return kwargs

    def get_object_list(self, request):
        # The Resource.get_schema() method calls this method:
        #
        #   https://github.com/toastdriven/django-tastypie/blob/v0.11.1/tastypie/resources.py#L1664
        #
        # to check for authorization to a resource's details.  However, this method is not implemented in the Resource
        # base class, so we need to provide an implementation.  This resource uses default ReadOnly authorization so
        # this method is, in essence, authorized.  Since the object list is not needed, we just return an empty list.
        return []


RESOURCES = (SimulationGroupResource, SimulationResource, SquareResource)

v1_api = Api(api_name='v1')
for resourceClass in RESOURCES:
    v1_api.register(resourceClass())
