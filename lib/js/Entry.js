(function() {
	
	// put all the controllers here, which is not good practice.
	// Refactor later when I am more familiar with AngularJS	
	var app = angular.module('app', ['ngRoute']);
	app.config(function ($routeProvider){
		$routeProvider
			.when('/Consilia',
					{
						controller: 'consiliaController',
						templateUrl: '/templates/Consilia/consiliaList.html'
					})
			.otherwise({redirectTo: '/Consilia'});
	});
	
	app.directive('viewSingleConsilaDetail', function(){
		function link (scope, iElement, iAttrs){
			scope.data = scope.$parent.detail;
			scope.showContent = true;
			scope.showDiagnosis = true;			
		};
		return {
			restrict: 'C',
			scope : {},
			templateUrl: '/templates/Consilia/singleDetail.html',
			link: link		
	   }
		
	});
	
	app.directive('singleConsilia', function($compile){
		function link (scope, iElement, iAttrs){
			scope.data = scope.$parent.item;
			scope.showDetail = false;			
		};
		
		function detailController($scope, $element, consiliaFactory){	
			var isDetailLoaded = false;
			var nextItem = 0;
			
			function showNextItem(){
				var template = '<div class="viewSingleConsilaDetail"></div>';
				isolateScepe = $scope.$new();
				isolateScepe.detail = $scope.data.details[nextItem];
				
				var el = $compile(template)( isolateScepe );
				
				var btn = angular.element(document.querySelector('#btn'+$scope.data.id));
				
		        btn.after(el);
				
				nextItem = 1;
			};
			
		    $scope.toggleDetail = function(){
		    	$scope.showDetail = !$scope.showDetail;	
		    	
		    	if ($scope.showDetail && !isDetailLoaded){
		    		consiliaFactory.getConsiliaDetailAsync($scope.data.id, function(allInfo){
		    			$scope.data = allInfo;
		    			isDetailLoaded = true;
				    	showNextItem();
		    		});
		    	}
		    	else{
			    	showNextItem();
		    	}
		    	
		    	
		    };				
		};
		
		
		return {
			restrict: 'C',
			scope : {},
			templateUrl: '/templates/Consilia/detail.html',
			link: link,
			controller : detailController			
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
		       $scope.consilias = data;	    	
	    	} );
	    };	
	};
	
	app.controller(controllers);
})();