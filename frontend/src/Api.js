import axios from 'axios';

class ApiHandler {
    constructor() {
        
    }

    addUser(realm, user, password, salt, success_callback, failure_callback) {
        var self = this;
        axios({
            method: "post",
            url: "http://localhost:5000/api/realm/" + realm + "/user/" + user,
            responseType: "json",
            data: {
                password: password,
                salt: salt ? "yes" : "no"
            }
        }).then(function(response) {
            success_callback(response.data);
        }).catch(function(error) {
            failure_callback();
        })
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