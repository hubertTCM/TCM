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
	
	app.factory('consiliaFactory', function($http) {
		var factory = {};
        factory.getConsiliasAsync = function (successCallback) {
		  $http.get('/allConsilias/')
			 .success(function (response){		    		
				 	successCallback(response);
				 })
			 .error(function(err){});
		};
		
		factory.getConsiliaDetailAsync = function (id, successCallback) {
			$http({'method' : 'get', 'url' : '/consiliaDetail','data': {'id': id}})
			 .success(function (response){		    		
				 	successCallback(response);
				 })
			 .error(function(err){});
		};

        return factory;
	});
	
	var controllers = {};
	controllers.consiliaController = function($scope, consiliaFactory){        
		$scope.consilias = [];
		$scope.title = "ȫ��ҽ��"

	    init();
	    function init() {
	    	consiliaFactory.getConsiliasAsync( function(data){
		       $scope.consilias = data;	    	
	    	} );
	    };
	
	    $scope.details = {};
	    $scope.getConsiliaDetail = function (id) { 
	    	var cachedData = $scope.details[id];
	    	if (cachedData){
	    		$scope.activeDetail = cachedData;
	    		return;
	    	}
	    	
	    	consiliaFactory.getConsiliaDetailAsync(id, function(data){
	    		$scope.details[id] = data;
	    		$scope.activeDetail = data;
	    	});
	    };
		
	};
	
	app.controller(controllers);
})();