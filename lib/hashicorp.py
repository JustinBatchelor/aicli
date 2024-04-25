import requests
import os


from lib import logging

# A list of all required environment variable names to create an HCP instance
ENVIRONMENT_VARIABLE_KEYS = ["clientID", "clientSecret", "organizationID", "projectID"]

class hashicorp:
    def __init__(self):
        # Set var apiVersion used for HCP API
        self.apiVersion = "2023-06-13"
        # Set var token enpoint used for getting oauth token from HCP endpoint
        self.hcpTokenURL = "https://auth.hashicorp.com/oauth/token"
        # Set dict to hold all required env vars specified in `ENVIRONMENT_VARIABLE_KEYS`
        self.environmentVariables = {}
        # update memeber `environmentVariables`
        self.__populateEnvironmentVariables()


    # Method to loop through var `ENVIRONMENT_VARIABLE_KEYS` and store the value(s) in the 
    # class's memeber `environmentVariables` dict
    def __populateEnvironmentVariables(self):
        for key in ENVIRONMENT_VARIABLE_KEYS:
            if os.environ.get("{}".format(key)):
                self.environmentVariables[key] = os.environ.get("{}".format(key))
            else:
                logging.quitMessage("There was an error when creating the hcp instance. Please ensure that the clientID, clientSecret, organizationID, and projectID are set as environment variables")

    # Method to get the OAuthToken required for API authentication
    def getOAuthToken(self):
        grantType = "client_credentials"
        audience = "https://api.hashicorp.cloud"

        # Payload with grant type, client credentials, and audience
        payload = {
            'grant_type': grantType,
            'client_id': self.environmentVariables["clientID"],
            'client_secret': self.environmentVariables["clientSecret"],
            'audience': audience,
        }

        contentType = "application/x-www-form-urlencoded"
        # Headers
        headers = {
            'Content-Type': contentType,
        }
        
        response = requests.post(self.hcpTokenURL, data=payload, headers=headers)
        

        if response.status_code == 200:
            # Parse the token from the response
            token = response.json().get('access_token')
            return token
        else:
            logging.quitMessage("Failed to retrieve token, Response: {}".format(response.text))


    # Method to get the secret object 
    def getAppSecret(self, appName, secretName):   
        # format the API endpoint
        apiendpoint = "https://api.cloud.hashicorp.com/secrets/{}/organizations/{}/projects/{}/apps/{}/open/{}".format(self.apiVersion , self.environmentVariables["organizationID"], self.environmentVariables["projectID"], appName, secretName)
        

        # set the headers for the request using the accessToken provided by getOAuthToken()
        headers = {
            'Authorization': 'Bearer {}'.format(self.getOAuthToken())
        }

        response = requests.get(apiendpoint, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.quitMessage("Failed to get secret. Hitting the url api endpoint: {}".format(apiendpoint))