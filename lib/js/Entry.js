(function() {
	var app = angular.module('app', ['ngRoute']);
	app.config(function ($routeProvider){
		$routeProvider
			.when('/view1',
					{
						controller: 'consiliaController',
						templateUrl: '/templates/Partials/Consilia.html'
					})
			.otherwise({redirectTo: '/view1'});
	});
	
	var controllers = {};
	controllers.consiliaController = function($scope){
		
	};
	
	app.controller(controllers);
})();