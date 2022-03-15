# cli-ssm-secret-manager

Small scripts to get, create and search AWS SSM secrets

## Install

All that is required is to install Boto3

```shell
pip install boto3
```

## How it works

There are 3 main functions in this script, `get, search and create`

### Get SSM value

This option will return a single SSM parameter

```shell
python ssm_secret_manager.py get --profile AWS_PROFILE_NAME SSM_PARAMETER_NAME
```

### Search for SSM parameters

Option will print out all SSM values that contain the search query

```shell
python ssm_secret_manager.py search --profile AWS_PROFILE_NAME SSM_SEARCH_QUERY
```

### Create SSM parameter

Option allows you to create a new SSM parameter

```shell
python ssm_secret_manager.py create --profile AWS_PROFILE_NAME --key SSM_PARAMETER_NAME --value SSM_PARAMETER_VALUE --type {String, SecureString}
```
