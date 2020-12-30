import json
import logging
import os
import secrets

from flask import Flask, render_template, request
from utils import success_json_response, get_ddb_items, summarise_dict, filter_dict, get_ddb_item, create_user

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
if ADMIN_SALT == None:
  logger.error("Missing ADMIN_SALT environment variable.  This might not be an issue if this is not the first time the tool has been run.")
else:
  if ADMIN_SALT not in ["yes", "no"]:
    logger.error("Invalid ADMIN_SALT value, setting to 'no'.")
    ADMIN_SALT = "no"

# need to create the admin account if this is the first time the tool has run
if ADMIN_REALM and ADMIN_USER and ADMIN_PASSWORD and ADMIN_SALT:
  # check if the user exists
  user = get_ddb_item(table = DDB_TABLE, p_realm = ADMIN_REALM, p_user = ADMIN_USER)
  if not user:
    # need to create the user
    logger.info("Creating admin user...")
    create_user(
      table=DDB_TABLE,
      realm=ADMIN_REALM,
      user=ADMIN_USER,
      password=ADMIN_PASSWORD,
      salt=ADMIN_SALT
    )
    logger.info("Created admin user.")
  else:
    logger.info("Admin user already exists, so not creating again")
else:
  logger.error("The details needed to set the admin user password are not present in the environment.")

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
    create_user(
      table=DDB_TABLE,
      realm=realm,
      user=user,
      password=request.json["password"],
      salt=request.json["salt"]
    )
    return get_user(realm, user)
  else:
    return success_json_response({
      "error": "Request must be JSON."
    })
