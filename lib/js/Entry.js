(function() {
	
	// put all the controllers here, which is not good practice.
	// Refactor later when I am more familiar with AngularJS	
	var app = angular.module('app', ['ngRoute']);
	app.config(function ($routeProvider){
		$routeProvider
			.when('/Consilia',
					{
						controller: 'consiliaController',
						templateUrl: '/templates/Consilia/allSummary.html'
					})
			.otherwise({redirectTo: '/Consilia'});
	});
	
	app.directive('singleConsilia', function(){
		function link (scope, iElement, iAttrs){
			scope.data = scope.$parent.item;
//		    scope.id = parseInt(attrs.id);
//		    scope.showDetail = attrs.showDetail;
//		    
//		    attrs.$observe('showDetail', function(){
//		    	console.log(attrs.showDetail);  // TBD	
//		    });
		};
		
		
		return {
			restrict: 'C',
			scope : {},
			templateUrl: '/templates/Consilia/detail.html',
			link: link			
	   }
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
	    		for(var i=0; i<data.length;i++)
	    			data[i].showDetail = false;
	    			
		       $scope.consilias = data;	    	
	    	} );
	    };
	    
	    $scope.toggleShowDetail = function(item){
	    	item.showDetail = !item.showDetail;	 
	    };		
	};
	
	app.controller(controllers);
})();