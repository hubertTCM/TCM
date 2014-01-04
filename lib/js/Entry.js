(function(){
	var defaultModule = angular.module('defaultModule', []);
	defaultModule.config(function ($routeProvider){
		$routeProvider
			.when('/',
					{
						controller: 'consiliaController',
						templateUrl: '/templates/Partials/Consilia.html'
					})
			.otherwise({redirectTo: '/'});
	});

	defaultModule.controller('consiliaController', function($scope){
		
	});

})();