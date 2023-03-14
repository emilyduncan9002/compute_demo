import requests
import json

url = "https://api4.prismacloud.io/login"

payload = {}
payload["username"] = "c95e8e1c-a5bc-448a-a45e-da055bc41a37"
payload["password"] = "hE4ACsLl1HuabMJDvYZb/RjScCA="
payload_json = json.dumps(payload)
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json; charset=UTF-8",
}

auth_token = requests.request("POST", url, headers=headers, data=payload_json)
auth_token_data = auth_token.json()
token = auth_token_data["token"]

# print(auth_token.text)

# url = "https://api4.prismacloud.io/license/api/v2/time_series"
url = "https://api4.prismacloud.io/license/api/v2/usage"

group_payload = {}
group_payload["accountIds"] = []
group_payload["accountGroupIds"] = ["1a687eb3-6d92-4142-8e5e-544b7ebc2c09"]
group_payload["cloudTypes"] = [
    "aws",
    "azure",
    "oci",
    "alibaba_cloud",
    "gcp",
    "others",
    "repositories",
]
group_payload["timeRange"] = {
    "type": "relative",
    "value": {"amount": "3", "unit": "month"},
}
group_payload_json = json.dumps(group_payload)
# print(group_payload_json)

headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json; charset=UTF-8",
    "x-redlock-auth": token,
}

response = requests.request("POST", url, headers=headers, data=group_payload_json)

print(response.json())
