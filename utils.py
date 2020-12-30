import urllib, json, requests, boto3
import logging
from flask import make_response, jsonify

logger = logging.getLogger(__name__)

def post_to_url(url, **kwargs):
  r = requests.post(url, data=kwargs)
  return r.content

def get_from_url(url, token, **kwargs):
  headers = {
    "Authorization": "Bearer {t}".format(t=token)
  }
  r = requests.get(url, params=kwargs, headers=headers)
  return r.content

def success_json_response(payload):
  """
  Turns payload into a JSON HTTP200 response
  """
  response = make_response(jsonify(payload), 200)
  response.headers["Content-type"] = "application/json"
  return response

def dh_wrap_field(field):
  """
  Wraps a field value for DynamoDB
  """
  if isinstance(field, str):
      return {"S": field}
  else:
      return {"N": str(field)}

def split_name(key):
  """
  Gets a field name from a key
  """
  key_bits = key.split("_")
  if len(key_bits) > 1:
    return key_bits[1]
  else:
    return key

def flatten(item):
  """
  Convert data returned from dynamodb to raw python objects
  """
  if "S" in item:
    return item["S"]
  if "N" in item:
    return int(item["N"])
  if "L" in item:
    flattened_list = []
    for i in item["L"]:
      flattened_list.append(flatten(i))
    return flattened_list

def summarise_dict(table, field):
  """
  Take an input dict (table) and reduce it to the list of unique values in field
  """
  unique_values = []
  for row in table:
    if field in row:
      if row[field] not in unique_values:
        unique_values.append(row[field])
  return unique_values

def filter_dict(table, allowed_fields):
  """
  Take an input dict (table) and filter the available fields to the allowed list
  """
  filtered_rows = []
  for row in table:
    filtered_rows.append({key: row[key] for key in allowed_fields})
  return filtered_rows

def get_ddb_item(table, **kwargs):
  """
  Get item from ddb table using keys (expected to be in kwargs)

  Uses a consistent read
  """
  ddb = boto3.client("dynamodb")
  keys_for_dynamo = {split_name(k): dh_wrap_field(v) for (k,v) in kwargs.items()}
  params = {
    "TableName": table,
    "Key": keys_for_dynamo
  }
  logger.info("Getting item using params {p}".format(p=params))
  response = ddb.get_item(**params)
  if "Item" in response:
    logger.info("Got an item")
    flattened_item = {}
    for key, value in response["Item"].items():
      flattened_item.update({
        key: flatten(value)
      })
    return flattened_item
  else:
    return None

def get_ddb_items(table, **kwargs):
  """
  Scan table to get items which match kwargs

  Can be an expensive method to call.
  """
  ddb = boto3.client("dynamodb")
  params = {
    "TableName": table,
    "Limit": 5,
    "ConsistentRead": False
  }
  # check if we need to filter
  expression_bits = []
  attributes = {}
  attributenames = {}
  chr_counter = 65
  if len(kwargs) > 0:
    # create filter expression
    for key in [key for key in list(kwargs.keys())]:
      logger.info("working on field {key}".format(key=key))
      expression_bits.append("#n{key} = :{val}".format(key=split_name(key), val=chr(chr_counter)))
      attributes.update({
        ":{key}".format(key=chr(chr_counter)): dh_wrap_field(kwargs[key])
      })
      attributenames.update({
        "#n{key}".format(key=split_name(key)): "{key}".format(key=split_name(key))
      })
      chr_counter = chr_counter +  1
    filter_expression = " AND ".join(expression_bits)
    params.update({
      "FilterExpression": filter_expression,
      "ExpressionAttributeValues": attributes,
      "ExpressionAttributeNames": attributenames
    })
  keep_scanning = True
  logger.info("Starting scan...")
  logger.info(params)
  items = []
  while keep_scanning:
    response = ddb.scan(**params)
    items = items + response["Items"]
    if "LastEvaluatedKey" in response:
      params.update({
          "ExclusiveStartKey": response["LastEvaluatedKey"]
      })
    else:
      keep_scanning = False
  logger.info("Finished scan, got {l} items".format(l=len(items)))
  flattened_items = []
  for item in items:
    flattened_item = {}
    for key, value in item.items():
      flattened_item.update({
        key: flatten(value)
      })

    flattened_items.append(flattened_item)
  return flattened_items

