import json
import logging
import os
import secrets

from flask import Flask, render_template, request
from utils import success_json_response, get_ddb_items, summarise_dict, filter_dict, get_ddb_item, hash_password, ddb_create

app = Flask(__name__,
            static_url_path="/static",
            static_folder="static")

# set logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s')
logger = logging.getLogger(__name__)

# get environment config
DDB_TABLE = os.getenv("DDB_TABLE")
ADMIN_REALM = os.getenv("ADMIN_REALM")
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_SALT = os.getenv("ADMIN_SALT")

# check the environment config
if DDB_TABLE == None:
  logger.error("Missing DDB_TABLE environment variable.")
if ADMIN_REALM == None:
  logger.error("Missing ADMIN_REALM environment variable.  This might not be an issue if this is not the first time the tool has been run.")
if ADMIN_USER == None:
  logger.error("Missing ADMIN_USER environment variable.  This might not be an issue if this is not the first time the tool has been run.")
if ADMIN_PASSWORD == None:
  logger.error("Missing ADMIN_PASSWORD environment variable.  This might not be an issue if this is not the first time the tool has been run.")

@app.route("/api")
def root():
  return success_json_response({
    "ping": "pong"
  })

@app.route("/api/realm")
def get_realms():
  items = get_ddb_items(table = DDB_TABLE)
  return success_json_response({
    "data": summarise_dict(items, "realm")
  })

@app.route("/api/realm/<string:realm>", methods=["GET"])
def get_realm(realm):
  items = get_ddb_items(table = DDB_TABLE, p_realm = realm)
  return success_json_response({
    "data": filter_dict(items, ["realm", "user"])
  })

@app.route("/api/realm/<string:realm>/user/<string:user>", methods=["GET"])
def get_user(realm, user):
  item = get_ddb_item(table = DDB_TABLE, p_realm = realm, p_user = user)
  return success_json_response({
    "data": item
  })

@app.route("/api/realm/<string:realm>/user/<string:user>", methods=["POST"])
def update_user(realm, user):
  item = get_ddb_item(table = DDB_TABLE, p_realm = realm, p_user = user)
  if request.json:
    if "password" not in request.json:
      return success_json_response({
        "error": "'password' field is mandatory"
      })
    if "salt" not in request.json:
      return success_json_response({
        "error": "'salt' field is mandatory"
      })
    if request.json["salt"] not in ["yes", "no"]:
      return success_json_response({
        "error": "'salt' field can only be 'yes' or 'no'"
      })
    params = {
      "p_realm": realm,
      "p_user": user,
      "p_scopes": ["admin"]
    }
    if request.json["salt"] == "yes":
      salt = secrets.token_hex(32)
      params.update({
        "p_salt": salt,
        "p_password": hash_password(request.json["password"], salt)
      })
    else:
      params.update({
        "p_password": hash_password(request.json["password"])
      })
    ddb_create(table = DDB_TABLE, **params)
    return get_user(realm, user)
  else:
    return success_json_response({
      "error": "Request must be JSON."
    })
