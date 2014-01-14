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
			
			if (!scope.data.description){
				scope.showDiagnosis();
			}
		};
		
		function detailController($scope){		
			$scope.showDiagnosis = function() {
				$scope.shouldShowDiagnosis = true;
				$scope.$parent.diagnosisShowed = true;					
			};
		};
		
		return {
			restrict: 'C',
			scope : {},
			templateUrl: '/templates/Consilia/singleDetail.html',
			link: link,
			controller: detailController
	   }
		
	});
	
	app.directive('singleConsilia', function($compile){
		function link (scope, iElement, iAttrs){
			scope.data = scope.$parent.item;
			scope.showDetail = false;			
		};
		
		function detailController($scope, $element, consiliaFactory){	
			var isDetailLoaded = false;
			var nextIndex = 0;
			
			$scope.showNext = false;
			
			$scope.next = function(){
				var template = '<div class="viewSingleConsilaDetail"></div>';
				isolateScope = $scope.$new();
				isolateScope.detail = $scope.data.details[nextIndex];
				isolateScope.diagnosisShowed = false;
				$scope.showNext = false;
				
				isolateScope.$watch('diagnosisShowed', function(){
					$scope.showNext = isolateScope.diagnosisShowed;
				});
				
				var itemDetailUI = $compile(template)( isolateScope );				
				var btnContainer = angular.element( document.querySelector('#btnContainer'+$scope.data.id) );
				
				var parent = btnContainer.parent();
				parent[0].insertBefore(itemDetailUI[0], btnContainer[0]);
				
				nextIndex += 1;
				if (nextIndex == $scope.data.details.length){
					btnContainer.remove();
				}
			};
			
		    $scope.toggleDetail = function(){
		    	$scope.showDetail = !$scope.showDetail;	
		    	
		    	if ($scope.showDetail && !isDetailLoaded){
		    		consiliaFactory.getConsiliaDetailAsync($scope.data.id, function(allInfo){
		    			$scope.data = allInfo;
		    			isDetailLoaded = true;
		    			$scope.next();
		    		});
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