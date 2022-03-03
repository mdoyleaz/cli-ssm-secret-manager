import argparse
import boto3


def get_cli_args():
    parser = argparse.ArgumentParser(
        description="Get, Search, or Create AWS SSM parameters"
    )

    # Parent Parser
    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument(
        "-p",
        "--profile",
        required=True,
        help="[REQUIRED] Selects the AWS profile to use",
    )

    # Subparsers
    subparsers = parser.add_subparsers(
        help="Manage AWS SSM paramater store values", required=True, dest="action"
    )

    # Get SSM Parameter Parser
    parser_get = subparsers.add_parser(
        "get", parents=[parent_parser], help="Get SSM secret"
    )
    parser_get.add_argument("name", help="[REQUIRED] SSM Name")

    # Search SSM Parameter Parser
    parser_search = subparsers.add_parser(
        "search", parents=[parent_parser], help="Search for an SSM secret"
    )
    parser_search.add_argument("query", help="Search for secrets")

    # Create SSM Parameter Parser
    parser_create = subparsers.add_parser(
        "create", parents=[parent_parser], help="Create a new SSM secret"
    )

    parser_create.add_argument(
        "-n", "--name", required=True, help="[REQUIRED] SSM secret name"
    )

    parser_create.add_argument(
        "-v",
        "--value",
        required=True,
        help="[REQUIRED] SSM Key Value",
    )

    parser_create.add_argument(
        "-t",
        "--type",
        choices=["String", "SecureString"],
        required=True,
        help="SSM parameter type",
    )

    args = vars(parser.parse_args())
    return args


def create_ssm_secret(client, secret_name, secret_value, secret_type="String"):
    operation_parameters = {
        "Name": secret_name,
        "Value": secret_value,
        "Type": secret_type,
        "DataType": "text",
    }

    try:
        client.put_parameter(**operation_parameters)

        print("{} has been created".format(secret_name))

    except client.exceptions.ParameterAlreadyExists:
        existing_value = get_secret(client, secret_name)["Parameter"]["Value"]

        print("\033[0;37;41mSecret already exists\033[0m")
        print("Name: {}".format(secret_name))
        print("Value: {}".format(existing_value))

        overwrite_input = input(
            "If you would like to overwrite this value enter 'OVERWRITE': "
        )

        if overwrite_input == "OVERWRITE":
            operation_parameters["Overwrite"] = True
            client.put_parameter(**operation_parameters)

            print("{} has been updated".format(secret_name))

        else:
            print("Value was not overwritten")

    except Exception as e:
        print("Unable to create parameter\n")
        print("ERROR: {}".format(e))


## Takes in a single SSM key name and returns the value
def get_secret(client, secret_name):
    operation_parameters = {"Name": secret_name, "WithDecryption": True}
    response = client.get_parameter(**operation_parameters)

    return response


## Takes a list of SSM key names, and returns a list of all values
def get_secrets(client, secret_names):
    # Split list into batch of 'n' due to AWS limiting get_parameters() call to a max of 18
    n = 10
    split_list = [
        secret_names[i * n : (i + 1) * n]
        for i in range((len(secret_names) + n - 1) // n)
    ]

    results = []
    for i in split_list:
        operation_parameters = {
            "Names": i,
            "WithDecryption": True,
        }
        response = client.get_parameters(**operation_parameters)
        results.extend([parameter for parameter in response["Parameters"]])

    return results


## Searches all SSM secrets by key name
def search_secrets(client, search_query):
    paginator = client.get_paginator("describe_parameters")
    operation_parameters = {
        "ParameterFilters": [
            {
                "Key": "Name",
                "Option": "Contains",
                "Values": [
                    search_query,
                ],
            },
        ],
        "MaxResults": 50,
    }

    page_iterator = paginator.paginate(**operation_parameters)

    # Flattens page_iterator list and extracts secret name
    results = [
        secret["Name"] for page in page_iterator for secret in page["Parameters"]
    ]

    return results


def print_secret(secret_name, secret_value):
    print("\033[1;32;40m{}\033[0m:  {}".format(secret_name, secret_value))


if __name__ == "__main__":
    args = get_cli_args()

    session = boto3.session.Session(profile_name=args["profile"])
    client = session.client("ssm")

    if args["action"] == "create":
        create_ssm_secret(client, args["name"], args["value"], args["type"])
    elif args["action"] == "get":
        secret = get_secret(client, args["name"])["Parameter"]
        print_secret(secret["Name"], secret["Value"])
    elif args["action"] == "search":
        secrets_key_list = search_secrets(client, args["query"])
        secret_values = get_secrets(client, secrets_key_list)

        for secret in secret_values:
            print_secret(secret["Name"], secret["Value"])
