var ProfilesViewModel = function () {
    var self = this;
    var url = "/contact/GetAllProfiles";
    var refresh = function () {
        $.getJSON(url, {}, function (data) {
            self.Profiles(data);
        });
    };
    

    // Public data properties
    self.Profiles = ko.observableArray([]);
    refresh();
};

ko.applyBindings(new ProfilesViewModel());