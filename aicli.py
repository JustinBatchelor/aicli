## Code to disable creating pycache dir after running
import sys, typer, requests
sys.dont_write_bytecode = True
###################################################


from lib import hashicorp, assistedinstaller, logging


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
    return installer.getInfrastructureEnvironments(cluster_id=cluster_id, owner=owner)
    

@app.command()
def createinfraenv(name: str = None, version: str = None):
    return installer.postInfrastructureEnvironment(name, version=version)


@app.command()
def deleteinfraenv(id: str = None):
    return installer.deleteInfrastructureEnvironment(id=id)

if __name__ == '__main__':
    app()