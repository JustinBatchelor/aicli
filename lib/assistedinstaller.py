import requests, json, jmespath, time
from urllib.parse import urlencode
from lib import logging
from lib.schema import infraEnvCreateParams


class assistedinstaller:
    def __init__(self, offline_token, pull_secret):
        self.offlineToken = offline_token
        self.pullSecret = pull_secret
        self.apiBase = "https://api.openshift.com/api/assisted-install/v2/"

    def getAccessToken(self):
        # URL for the token request
        url = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"

        # Headers to be sent with the request
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Data to be sent in the request, explicitly encoding each variable
        data = urlencode({
            "grant_type": "refresh_token",
            "client_id": "cloud-services",
            "refresh_token": self.offlineToken
        })

        try:
            # Make the POST request
            response = requests.post(url, headers=headers, data=data)

            # Handle response
            if response.status_code == 200:
                # Extract access token from the response JSON
                access_token = response.json().get("access_token")
                return access_token
            else:
                # Print error message if something went wrong
                logging.quitMessage(f"Failed to retrieve access token. Messsage from API: {response.text}")
        except Exception as e:
            logging.logMessage("")

    
    # Method that will implement the /v2/infra-envs GET assisted installer endpoint
    def getInfrastructureEnvironments(self, cluster_id=None, owner=None):
        url = self.apiBase + "infra-envs"
        if cluster_id is not None and owner is not None:
            url += f'?cluster_id={cluster_id}&owner={owner}'
        else:
            if cluster_id is not None:
                url += f'?cluster_id={cluster_id}'
            if owner is not None:
                url += f'?owner={owner}'

        headers = {
            "Authorization": "Bearer {}".format(self.getAccessToken()),
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                logging.logMessage("Returned Infrastructure Environments")
                logging.prettyPrint(json.loads(response.text))
                return json.loads(response.text)
            else: 
                logging.errorMessage(f"getInfrastructureEnvironments() method did not recieve a 200 status code, recieved {response.status_code} instead")
                logging.quitMessage(f"{response.text}")       
        except Exception as e:
            logging.quitMessage(f"getInfrastructureEnvironments() method errored on request.get() with the following error: {e}")


    def postInfrastructureEnvironment(self, name, version=None):
        url = self.apiBase + "infra-envs"

        headers = {
            "Authorization": "Bearer {}".format(self.getAccessToken()),
            "Content-Type": "application/json"
        }

        infraparams = infraEnvCreateParams.infraEnvCreateParams(name, self.pullSecret, version=version)

        data = infraparams.getParams()

        try:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 201:
                logging.logMessage(f"Successfully created Infrastructure Environment:")
                logging.prettyPrint(json.loads(response.text))
                return json.loads(response.text)
            else:
                logging.errorMessage(f"postInfrastructureEnvironments() method did not recieve a 201 status code, recieved {response.status_code} instead")
                logging.quitMessage(f"{response.text}")  

        except Exception as e:
            logging.quitMessage(f"postInfrastructureEnvironments() method errored on request.post() with the following error: {e}")

    def deleteInfrastructureEnvironment(self, id):
        url = self.apiBase + f"infra-envs/{id}"

        headers = {
            "Authorization": "Bearer {}".format(self.getAccessToken()),
            "Content-Type": "application/json"
        }

        try:
            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                logging.logMessage(f"Successfully deleted Infrastructure Environment: {id}")
                return True
            else:
                logging.errorMessage(f"deleteInfrastructureEnvironments() method did not recieve a 204 status code, recieved {response.status_code} instead")
                return False 

        except Exception as e:
            logging.quitMessage(f"deleteInfrastructureEnvironments() method errored on request.delete() with the following error: {e}")
