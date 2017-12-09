(function () {

  'use strict';

  angular.module('ArticleSearchEngineApp', [])

  .controller('SearchEngineController', ['$scope', '$log', '$http', '$timeout',
    function($scope, $log, $http, $timeout) {
        $scope.getResults = function() {
          // get the URL from the input
          var query = $scope.query;
          var fromDate = $scope.fromDate;
          var toDate = $scope.toDate;

          // search method
          $http.post('/search', {"q": query, "from": fromDate, "to": toDate}).
            success(function(data, status, headers, config) {
              $scope.results = data;
              $log.log(data);
            }).
            error(function(error) {
              $log.log(error);
            });
        };
      }
  ]);

}());

