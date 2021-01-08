# basicauth-user-manager

![build and push to public aws ecr](https://github.com/richardjkendall/basicauth-user-manager/workflows/build%20and%20push%20to%20public%20aws%20ecr/badge.svg)

This is a companion to my [pam-dynamo](https://github.com/richardjkendall/pam-dynamo) module and implementations which use it like:

* https://github.com/richardjkendall/basicauth-rproxy
* https://github.com/richardjkendall/basicauth-rproxy-perpath

This tool manages the user records in a DyanmoDB table per the requirements of the pam-dynamo module, including salting and hashing passwords.

## Running it

The application is packaged as a container and is available on my ECR public container registry here https://gallery.ecr.aws/z7f7v2i3/basicauth-user-manager

Running it is as simple as

```bash
docker run \
  -e DDB_TABLE="table name" \
  -p 5000:5000 \
  public.ecr.aws/z7f7v2i3/basicauth-user-manager:latest
```

You will need a method to pass in AWS credentials.  This can either be done as environment variables or by running the container in an AWS environment like ECS.

## Protecting it

The application expects to be deployed behind a authenticating reverse proxy.  It works well with [basicauth-rproxy](https://github.com/richardjkendall/basicauth-rproxy) and if it is invoked with the following environment variables it will create a default user to allow access:

|Variable|Purpose|
|---|---|
|ADMIN_REALM|The realm used by the proxy|
|ADMIN_USER|The username for the admin user to create|
|ADMIN_PASSWORD|The password to set for the admin user|
|ADMIN_SALT|Should we salt the password "yes" or "no"|

If the ``ADMIN_USER`` already exists in the ``ADMIN_REALM`` it will not be recreated and its password will not be changed.

## Deploying

To make this easy, I've pre-created a Terraform module which can deploy the user manager behind the authenticating reverse proxy, you can see it here: https://github.com/richardjkendall/tf-modules/tree/master/modules/basicauth-user-manager

This module will also create an appropriate DynamoDB table if needed.