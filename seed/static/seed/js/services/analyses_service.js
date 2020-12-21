angular.module('BE.seed.service.analyses', [])
  .factory('analyses_service', [
    '$http',
    '$log',
    'user_service',
    function (
      $http,
      $log,
      user_service
    ) {

      let get_analyses_for_org = function (org_id) {
        return $http.get('/api/v3/analyses/?organization_id=' + org_id).then(function (response) {
          return response.data;
        });
      };

      let get_analyses_for_canonical_property = function (property_id) {
        let org = user_service.get_organization().id;
        return $http.get('/api/v3/analyses/?organization_id=' + org + '&property_id=' + property_id).then(function (response) {
          return response.data;
        });
      };

      let create_analysis = function(name, service, configuration, property_view_ids) {
        let organization_id = user_service.get_organization().id;
        return $http({
          url: '/api/v3/analyses/',
          method: 'POST',
          params: { organization_id: organization_id },
          data: {
            name: name,
            service: service,
            configuration: configuration,
            property_view_ids: property_view_ids,
          }
        }).then(function (response) {
          return response.data
        })
      }

      let start_analysis = function(analysis_id) {
        let organization_id = user_service.get_organization().id;
        return $http({
          url: '/api/v3/analyses/' + analysis_id + '/start/',
          method: 'POST',
          params: { organization_id: organization_id },
        }).then(function (response) {
          return response.data
        }).catch(function (response) {
          return response.data
        })
      }

      let analyses_factory = {
        get_analyses_for_org: get_analyses_for_org,
        get_analyses_for_canonical_property: get_analyses_for_canonical_property,
        create_analysis: create_analysis,
        start_analysis: start_analysis,
      };

      return analyses_factory;
    }]);
