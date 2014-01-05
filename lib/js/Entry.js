(function() {
	
	// put all the controllers here, which is not good practice.
	// Refactor later when I get more knowledge about AngularJS
	
	var app = angular.module('app', ['ngRoute']);
	app.config(function ($routeProvider){
		$routeProvider
			.when('/Consilia',
					{
						controller: 'consiliaController',
						templateUrl: '/templates/Partials/Consilia.html'
					})
			.otherwise({redirectTo: '/Consilia'});
	});
	
	app.factory('consiliaFactory', function () {
        var factory = {};
        var consilias = [
			{ name: 'Dave Jones', description: 'Phoenix' },
			{ name: 'Jamie Riley', description: 'Atlanta' },
			{ name: 'Heedy Wahlin', description: 'Chandler' },
			{ name: 'Thomas Winter', description: 'Seattle' }
        ];

        factory.getConsilias = function () {
            //Can use $http object to retrieve remote data
            //in a "real" app
            return consilias;
        };
        return factory;
    });
	
	var controllers = {};
	controllers.consiliaController = function($scope, consiliaFactory){        
		$scope.consilias = [];

	    init();
	    function init() {
	       $scope.consilias = consiliaFactory.getConsilias();
	    }
	
	    $scope.addConsilia = function () {
	        $scope.consilias.push(
			{
			    name: $scope.inputData.name,
			    city: $scope.inputData.description
			});
	    }
		
	};
	
	app.controller(controllers);
})();