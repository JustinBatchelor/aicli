import tempfile
import requests
import re
import validators

from lib import logging

# def fetchOpenshiftVersion():
#     # Initial URL that will redirect to a specific versioned URL
#     url = "https://docs.openshift.com/container-platform/latest/welcome/index.html"

#     # Make a request and allow redirection
#     response = requests.get(url, allow_redirects=True)
    
#     # Check if the request was successful
#     if response.status_code == 200:
#         # Extract the final URL after redirection
#         final_url = response.url

#         # Regular expression to extract the version number
#         version_pattern = re.compile(r'/(\d+\.\d+)/')
#         match = version_pattern.search(final_url)
        
#         if match:
#             version = match.group(1)
#             return version
#         else:
#             logging.errorMessage("Version number not found in the URL.")
#             return ""
#     else:
#         logging.errorMessage("Failed to retrieve the URL. Status code: {}".format(response.status_code))
#         return ""

def validateDomain(domain):
    # Validate the domain
    return validators.domain(domain)

def validateName(name):
    # Regular expression pattern to match the name criteria
    pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'
    # return Matching the name with the pattern
    return re.match(pattern, name)

def validateVersion(version):
    # Regular expression pattern to match the version criteria
    pattern = r'^[0-9]+\.[0-9]+$'
    # return Matching the name with the pattern
    return re.match(pattern, version)

def validateSize(size):
    return size == "sno" or size == "compact"
