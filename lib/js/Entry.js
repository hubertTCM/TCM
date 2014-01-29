(function() {
	
	// put all the controllers here, which is not good practice.
	// Refactor later when I am more familiar with AngularJS	
	var app = angular.module('app', ['ngRoute', 'ngSanitize', 'ngCookies']);
	app.config(function ($routeProvider){
		$routeProvider
			.when('/MedicalNote/edit/:id', {
				template: '<div class="medicalNoteEdit"></div>'
			})
			.when('/:category/pages/:pageIndex',
					{
						controller: 'summarysController',
						templateUrl: '/templates/Share/summaryList.html'
					})
			.when('/:category',
					{
						controller: 'summarysController',
						templateUrl: '/templates/Share/summaryList.html'
					})
			.otherwise({redirectTo: 'MedicalNote/edit/1'});   
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
	   };
		
	});
	
	app.directive('singleConsilia', function($compile){
		function link (scope, iElement, iAttrs){
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
			templateUrl: '/templates/Consilia/detail.html',
			link: link,
			controller : detailController			
	   }
	});
	
	app.directive('medicalNoteDetail', function($compile){
		function link (scope, iElement, iAttrs){
			scope.showDetail = false;	
		    
		    scope.remove = function(){ // TBD
		    	iElement.remove();
		    };
		};
		
		function detailController($scope, $rootScope, $location, medicalNoteFactory){	
			var isDetailLoaded = false;
			
			$scope.showNext = false;			
		    $scope.toggleDetail = function(){
		    	$scope.showDetail = !$scope.showDetail;	
		    	
		    	if ($scope.showDetail && !isDetailLoaded){
		    		medicalNoteFactory.getDetailAsync($scope.data.id, function(allInfo){
		    			$scope.data = allInfo;						
		    			isDetailLoaded = true;
		    		});
		    	}		    	
		    };
		    
		    $scope.edit = function(){
		    	$location.path("/MedicalNote/edit/"+ $scope.data.id);
		    	$rootScope.noteDetail = $scope.data;
		    };
		};
		
		
		return {
			restrict: 'C',
			templateUrl: '/templates/MedicalNote/detail.html',
			link: link,
			controller : detailController			
	   }
	});
	
	app.directive('medicalRelatedDetail', function($compile){
		function link (scope, iElement, iAttrs){
			var template = '<div class="' + scope.$parent.detailTemplateName + '"></div>';
			var detailUI = $compile(template)( scope );	
			var parent = iElement.parent();
			parent.append(detailUI);
		};

		
		return {
			restrict: 'C',
			templateUrl: '/templates/Share/medicalRelatedDetail.html',
			link: link		
	   }
	});
	
	app.directive('medicalNoteEdit', function(){
		var contentEditorId = "contentTextarea";
						
		function link (scope, iElement, iAttrs){
			scope.changed = false;			
            tinymce.init({
            	selector: '#' + contentEditorId,
                setup: function (editor) {
                    editor.on('init', function(args) {    
            			var isContentReady = scope.data;        			
                    	if (args.target.id != contentEditorId){
                    		return;
                    	}

            			if (!isContentReady){
	            			scope.$watch('data', function(){
	                    		editor.setContent(scope.data.content); 
	        				});
            			}
            			else{
            				editor.setContent(scope.data.content); 
            			}
                    });
			        editor.on('change', function(e) {
						scope.changed = true;
						console.log("scope.changed = " + scope.changed);
			        });
                }
        	});     		
		};
		
		function editController($scope, $routeParams, $rootScope, medicalNoteFactory){
			function init(){
				$scope.data = $rootScope.noteDetail;
				var id = $routeParams.id;
				delete $rootScope.noteDetail;
				
				if(!$scope.data){
					medicalNoteFactory.getDetailAsync(id, function(info){
						$scope.data = info;
					});
				}
			};
			init();
		
			$scope.save = function(){
				var editor = tinymce.get(contentEditorId);
				$scope.data.content = editor.getContent();
				medicalNoteFactory.save($scope.data);
			};
			$scope.cancel = function(){
				var editor = tinymce.get(contentEditorId);
				editor.setContent($scope.data.content);
				$scope.changed = false;
			};
		};
		return {
			restrict: 'C',
			templateUrl: '/templates/MedicalNote/detailEdit.html',
			link: link,
			controller : editController			
	   }
	});
	
	app.factory('medicalNoteFactory', function($http) {
		var factory = {};
		
        factory.getSummarysAsync = function (from, to, successCallback) {
        	$http({'method' : 'get', 'url' : '/allMedicalNotes/','params': {'from': from, "to" : to} })
			 .success(function (response){		    		
				 	successCallback(response);
				 })
			 .error(function(err){});
		};
		
		factory.getDetailAsync = function (id, successCallback) {
			$http({'method' : 'get', 'url' : '/medicalNoteDetail','params': {'id': id} })
			 .success(function (response){		    		
				 	successCallback(response);
				 })
			 .error(function(err){});
		};
		
		factory.save = function (data, successCallback){
        	$http({'method' : 'post', 'url' : '/saveMedicalNote/', 'data': data })
			 .success(function (response){		    		
				 	successCallback(response);
				 })
			 .error(function(err){});
		};
		return factory;
	});
	
	app.factory('consiliaFactory', function($http) {
		var factory = {};
        factory.getSummarysAsync = function (from, to, successCallback) {
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

        return factory;
	});
	
	var controllers = {};
	controllers.summarysController = function($scope, $routeParams, $location, consiliaFactory, medicalNoteFactory){  
		var sourceProvider = null;
		$scope.category = $routeParams.category;
		switch ($routeParams.category){
			case "Consilia":
				$scope.detailTemplateName = "singleConsilia";
				sourceProvider = consiliaFactory;
				$scope.title = "全部医案";
				break;
			case "MedicalNote":
				$scope.detailTemplateName = "medicalNoteDetail";
				sourceProvider = medicalNoteFactory;
				$scope.title = "全部医话";
				break;
		};

		var currentPage = 0;
		if ($routeParams.pageIndex){
			currentPage = parseInt($routeParams.pageIndex);
		}
		var pageSize = 20;
		
		var dataFetched = false;
		
		function isValidPageIndex(pageIndex){
			if (!dataFetched){
				return true;
			}
			return pageIndex >= 0 && pageIndex < $scope.pages.length;
		};
		
		function getPagePath(pageIndex){
	    	return '/' + $routeParams.category + '/pages/' + pageIndex;			
		};
	    
	    function changePathToPage(pageIndex){
	    	$location.path(getPagePath(pageIndex));	    	
	    };

	    $scope.pages = [];
	    $scope.navigateToPage = function(pageIndex){
	    	if (!isValidPageIndex(pageIndex)){
	    		return;
	    	}
	    	
	    	currentPage = pageIndex;
	    	var from = currentPage * pageSize;
	    	var to = (currentPage + 1) * pageSize - 1
	    	sourceProvider.getSummarysAsync(from, to, function(data){	    			
		       $scope.allSummarys = data.summarys;	
		       var pageCount = data.totalCount / pageSize
		       
		       $scope.pages.length = 0;
		       for(i = 0; i < pageCount; i++){
		    	   $scope.pages.push({'pageNumber' : i + 1, 'path' : '#' + getPagePath(i)});
		       }
	    	} );	    	
	    };
	    
	    $scope.previous = function(){
	    	changePathToPage(currentPage - 1);	
	    };
	    
	    $scope.next = function(){
	    	changePathToPage(currentPage + 1);
	    };
	    	    
	    function init() {
	    	$scope.navigateToPage(currentPage);
	    	dataFetched = true;
	    };	
		
	    init();
	};
	
	app.controller(controllers);
})();