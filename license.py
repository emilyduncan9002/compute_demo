import requests
import json
import os

url = "https://api4.prismacloud.io/login"

payload = {}
payload["username"] = os.environ.get("prismaUserName")
payload["password"] = os.environ.get("prismaSecretKey")
payload_json = json.dumps(payload)
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json; charset=UTF-8",
}

auth_token = requests.request("POST", url, headers=headers, data=payload_json)
auth_token_data = auth_token.json()
token = auth_token_data["token"]

# print(auth_token.text)


url = "https://api4.prismacloud.io/cloud/group"

group_payload = {}
group_payload["accountIds"] = []
headers = {"Accept": "application/json; charset=UTF-8", "x-redlock-auth": token}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

# url = "https://api4.prismacloud.io/license/api/v2/time_series"
url = "https://api4.prismacloud.io/license/api/v2/usage"

usage_payload = {}
usage_payload["accountIds"] = []
usage_payload["accountGroupIds"] = ["1a687eb3-6d92-4142-8e5e-544b7ebc2c09"]
usage_payload["cloudTypes"] = [
    "aws",
    "azure",
    "oci",
    "alibaba_cloud",
    "gcp",
    "others",
    "repositories",
]
usage_payload["timeRange"] = {
    "type": "relative",
    "value": {"amount": "3", "unit": "month"},
}
usage_payload_json = json.dumps(usage_payload)
# print(group_payload_json)

headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json; charset=UTF-8",
    "x-redlock-auth": token,
}

response = requests.request("POST", url, headers=headers, data=usage_payload_json)

# print(response.json())
