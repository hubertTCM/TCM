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
			$http({'method' : 'get', 'url' : '/consiliaDetail','params': {'id': id} })
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
		$scope.title = "全部医案"

	    init();
	    function init() {
	    	consiliaFactory.getConsiliasAsync( function(data){
		       $scope.consilias = data;	    	
	    	} );
	    };
	
	    $scope.details = {};
	    $scope.toggleConsiliaDetail = function (id) { 
	    	var info = $scope.details[id];
	    	if (info){
	    		info.show = !info.show;
	    		return;
	    	}
	    	
	    	consiliaFactory.getConsiliaDetailAsync(id, function(data){
	    		$scope.details[id] = {'data' : data, 'show' : true};
	    	});
	    };
	    
	    $scope.shouldShow = function(id){
	    	var info = $scope.details[id];
	    	if (info){
	    		return info.show;
	    	}
	    	return false;
	    }
		
	};
	
	app.controller(controllers);
})();