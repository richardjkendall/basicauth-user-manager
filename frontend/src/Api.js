import axios from 'axios';

class ApiHandler {
    constructor() {
        
    }

    getRealms(success_callback, failure_callback) {
        var self = this;
        axios({
            method: "get",
            url: "http://localhost:5000/api/realm",
            responseType: "json",
        }).then(function(response) {
            success_callback(response.data);
        }).catch(function(error) {
            failure_callback();
        });
    }

    getUsers(realm, success_callback, failure_callback) {
        var self = this;
        axios({
            method: "get",
            url: "http://localhost:5000/api/realm/" + realm,
            responseType: "json",
        }).then(function(response) {
            success_callback(response.data);
        }).catch(function(error) {
            failure_callback();
        });
    }
}

export default ApiHandler;