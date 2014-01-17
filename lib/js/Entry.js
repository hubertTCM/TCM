(function() {
	
	// put all the controllers here, which is not good practice.
	// Refactor later when I am more familiar with AngularJS	
	var app = angular.module('app', ['ngRoute']);
	app.config(function ($routeProvider){
		$routeProvider
			.when('/Consilia',
					{
						controller: 'consiliaController',
						templateUrl: '/templates/summaryList.html'
					})
			.when('/MedicalNote',
					{
						controller: 'medicalController',
						templateUrl: '/templates/summaryList.html'
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
	

	app.directive('medicalNoteDetail', function($compile){
		function link (scope, iElement, iAttrs){
			scope.data = scope.$parent.item;
			scope.showDetail = false;			
		};
		
		function detailController($scope, $element, consiliaFactory){	
			var isDetailLoaded = false;
			
			$scope.showNext = false;
			
		    $scope.toggleDetail = function(){
		    	$scope.showDetail = !$scope.showDetail;	
		    	
		    	if ($scope.showDetail && !isDetailLoaded){
		    		consiliaFactory.getMedicalNoteDetailAsync($scope.data.id, function(allInfo){
		    			$scope.data = allInfo;
		    			isDetailLoaded = true;
		    		});
		    	}	    	
		    	
		    };				
		};
		
		
		return {
			restrict: 'C',
			scope : {},
			templateUrl: '/templates/MedicalNote/detail.html',
			link: link,
			controller : detailController			
	   }
	});
	
	app.directive('medicalRelatedDetail', function($compile){
		function link (scope, iElement, iAttrs){
			var category = scope.$parent.category;
			switch(category){
			case "consilia":
				var template = '<div class="singleConsilia"></div>';				
				var detailUI = $compile(template)( scope );	
				var parent = iElement.parent();
				parent.append(detailUI);
				break;
			case "medicalNote":
				var template = '<div class="medicalNoteDetail"></div>';				
				var detailUI = $compile(template)( scope );	
				var parent = iElement.parent();
				parent.append(detailUI);
				break;
			}
		};

		
		return {
			restrict: 'C',
			link: link		
	   }
	});
	
	app.factory('consiliaFactory', function($http) {
		var factory = {};
        factory.getConsiliasAsync = function (from, to, successCallback) {
        	$http({'method' : 'get', 'url' : '/allConsilias/','params': {'from': from, "to" : to} })
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
		
		// Medical note
        factory.getMedicalNotesAsync = function (from, to, successCallback) {
        	$http({'method' : 'get', 'url' : '/allMedicalNotes/','params': {'from': from, "to" : to} })
			 .success(function (response){		    		
				 	successCallback(response);
				 })
			 .error(function(err){});
		};
		
		factory.getMedicalNoteDetailAsync = function (id, successCallback) {
			$http({'method' : 'get', 'url' : '/medicalNoteDetail','params': {'id': id} })
			 .success(function (response){		    		
				 	successCallback(response);
				 })
			 .error(function(err){});
		};

        return factory;
	});
	
	var controllers = {};
	controllers.consiliaController = function($scope, consiliaFactory){  
		
		$scope.data = [];
		$scope.title = "全部医案";
		$scope.category = "consilia";

		var currentPage = -1;
		var pageSize = 20;
		
		var dataFetched = false;
		
		function isValidPageIndex(pageIndex){
			if (!dataFetched){
				return true;
			}
			return pageIndex >= 0 && pageIndex < $scope.pages.length;
		};

	    $scope.pages = [];
	    $scope.navigateToPage = function(pageIndex){
	    	if (!isValidPageIndex(pageIndex)){
	    		return;
	    	}
	    	
	    	currentPage = pageIndex;
	    	var from = currentPage * pageSize;
	    	var to = (currentPage + 1) * pageSize - 1
	    	consiliaFactory.getConsiliasAsync(from, to, function(data){	    			
		       $scope.data = data.summarys;	
		       var pageCount = data.totalCount / pageSize
		       
		       $scope.pages.length = 0;
		       for(i = 0; i < pageCount; i++){
		    	   $scope.pages.push(i + 1);
		       }
	    	} );	    	
	    };
	    
	    $scope.previous = function(){
	    	$scope.navigateToPage(currentPage - 1);	    	
	    };
	    
	    $scope.next = function(){
	    	$scope.navigateToPage(currentPage + 1);
	    };
	    	    
	    function init() {
	    	$scope.next();
	    	dataFetched = true;
	    };	
		
	    init();
	};
	
	controllers.medicalController = function ($scope, consiliaFactory){
		
		$scope.data = [];
		$scope.title = "全部医话";
		$scope.category = "medicalNote";

		var currentPage = -1;
		var pageSize = 20;
		
		var dataFetched = false;
		
		function isValidPageIndex(pageIndex){
			if (!dataFetched){
				return true;
			}
			return pageIndex >= 0 && pageIndex < $scope.pages.length;
		};

	    $scope.pages = [];
	    $scope.navigateToPage = function(pageIndex){
	    	if (!isValidPageIndex(pageIndex)){
	    		return;
	    	}
	    	
	    	currentPage = pageIndex;
	    	var from = currentPage * pageSize;
	    	var to = (currentPage + 1) * pageSize - 1
	    	consiliaFactory.getMedicalNotesAsync(from, to, function(data){	    			
		       $scope.data = data.summarys;	
		       var pageCount = data.totalCount / pageSize
		       
		       $scope.pages.length = 0;
		       for(i = 0; i < pageCount; i++){
		    	   $scope.pages.push(i + 1);
		       }
	    	} );	    	
	    };
	    
	    $scope.previous = function(){
	    	$scope.navigateToPage(currentPage - 1);	    	
	    };
	    
	    $scope.next = function(){
	    	$scope.navigateToPage(currentPage + 1);
	    };
	    	    
	    function init() {
	    	$scope.next();
	    	dataFetched = true;
	    };	
		
	    init();
	};
	
	app.controller(controllers);
})();