## Code to disable creating pycache dir after running
import sys, typer, requests
sys.dont_write_bytecode = True
###################################################


from lib import hashicorp, assistedinstaller, logging
from urllib3.exceptions import InsecureRequestWarning


# requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)



app = typer.Typer()

# create hcp instance
hcp = hashicorp.hashicorp()
# get assisted installer token value from hashicorp
token = hcp.getAppSecret("assisted-installer", "token")['secret']['version']['value']
# get assisted installer pull_secret value from hashicorp
pullSecret = hcp.getAppSecret("assisted-installer", "pull_secret")['secret']['version']['value']
# create assisted installer instance
installer = assistedinstaller.assistedinstaller(token, pullSecret)



@app.command()
def getinfraenv(cluster_id: str = None, owner: str = None):
    infraenvs = installer.getInfrastructureEnvironments(cluster_id=cluster_id, owner=owner)
    logging.prettyPrint(infraenvs)


@app.command()
def postinfraenv(name: str = "", pullsecret: str = pullSecret, version: str = "None"):
    logging.logMessage(installer.postInfrastructureEnvironment(name, pullSecret, version="4.15"))


if __name__ == '__main__':
    app()