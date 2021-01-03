import axios from 'axios';

const API_BASE = "";
//const API_BASE = "http://localhost:5000";

class ApiHandler {

    delUser(realm, user, success_callback, failure_callback) {
        axios({
            method: "delete",
            url: API_BASE + "/api/realm/" + realm + "/user/" + user,
        }).then(function(response) {
            success_callback(response.data);
        }).catch(function(error) {
            failure_callback();
        });
    }

    addUser(realm, user, password, salt, success_callback, failure_callback) {
        axios({
            method: "post",
            url: API_BASE + "/api/realm/" + realm + "/user/" + user,
            responseType: "json",
            data: {
                password: password,
                salt: salt ? "yes" : "no"
            }
        }).then(function(response) {
            success_callback(response.data);
        }).catch(function(error) {
            failure_callback();
        });
    }

    getRealms(success_callback, failure_callback) {
        axios({
            method: "get",
            url: API_BASE + "/api/realm",
            responseType: "json",
        }).then(function(response) {
            success_callback(response.data);
        }).catch(function(error) {
            failure_callback();
        });
    }

    getUsers(realm, success_callback, failure_callback) {
        axios({
            method: "get",
            url: API_BASE + "/api/realm/" + realm,
            responseType: "json",
        }).then(function(response) {
            success_callback(response.data);
        }).catch(function(error) {
            failure_callback();
        });
    }
}

export default ApiHandler;