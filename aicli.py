## Code to disable creating pycache dir after running
import sys, typer, os, datetime, time
sys.dont_write_bytecode = True
###################################################

import redhat_assisted_installer.assistedinstaller as redhat_assisted_installer
import hcp_vault_secrets.vaultsecrets as vaultsecrets

from lib import proxmox, tools, logging

app = typer.Typer()

# create hcp instance
hcp = vaultsecrets.vaultsecrets()
# get assisted installer token value from hashicorp and set it as an evironment variable
os.environ['REDHAT_OFFLINE_TOKEN'] = hcp.getAppSecret("assisted-installer", "token")
# get assisted installer pull_secret value from hashicorp and set it as an evironment variable
os.environ['REDHAT_PULL_SECRET'] = hcp.getAppSecret("assisted-installer", "pull_secret")
# create assisted installer instance
installer = redhat_assisted_installer.assistedinstaller()

# create proxmox cluster instance
pve = proxmox.proxmoxcluster(hcp.getAppSecret("proxmox", "password"))


@app.command()
def createcluster(name: str, version: str, high_availability_mode: str = "None", cpu_architecture: str = "x86_64"):
    return installer.postCluster(name=name, version=version, hamode=high_availability_mode, cpuarchitecture=cpu_architecture)

@app.command()
def deletecluster(cluster_id: str):
    return installer.deleteCluster(cluster_id)

@app.command()
def getcluster(cluster_id: str = None, with_hosts: bool = False, owner: str = None):
    return installer.getClusters(cluster_id=cluster_id, with_hosts=with_hosts, owner=owner)

@app.command()
def getinfraenv(cluster_id: str = None, owner: str = None):
    return installer.getInfrastructureEnvironments(cluster_id=cluster_id, owner=owner)
    
@app.command()
def createinfraenv(name: str, version: str, cluster_id: str = None, cpuarchitecture: str = "x86_64"):
    return installer.postInfrastructureEnvironment(name=name, version=version, clusterid=cluster_id, cpuarchitecture=cpuarchitecture)

@app.command()
def deleteinfraenv(id: str):
    return installer.deleteInfrastructureEnvironment(id=id)

@app.command()
def deploycluster(name: str, version: str, basedomain: str, size: str = "sno", cpuarchitecture: str = 'x86_64'):
    if not tools.validateName(name):
        logging.quitMessage("name: {} - is not a valid name that can be used with the assisted-installer. Please ensure the name conforms to the following regular expression: {}".format(name, "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"))
    
    if not tools.validateDomain(basedomain):
        logging.quitMessage("basedomain: {} - is not a valid domain. Please double check your imput and try again".format(basedomain))
    
    if not tools.validateVersion(version):
        logging.quitMessage("version: {} - is not a valid version. The code will default to the lastest supported version of openshift. Please double check the version you passed and ensure it conforms to the following regualar expression (only x.xx versions supported right now)".format(version))
    
    if not tools.validateSize(size):
        logging.quitMessage("size: {} - is not a valid size. Please choose from one of the following options [sno, compact]. The code currently defaults to installing a single node openshift cluster".format(size))
    
    # create proxmox cluster instance
    pve = proxmox.proxmoxcluster(hcp.getAppSecret("proxmox", "password"))

    if size == 'sno':
        cluster = installer.postCluster(name=name, version=version, basedomain=basedomain)
        if cluster:
            infra = installer.postInfrastructureEnvironment(name=name, version=version, clusterid=cluster['id'])
            pve.uploadISO(infra['download_url'], name)
            # define vm in proxmox
            vmID = pve.defineVM(name)
            # start the vm we recently created
            pve.startVM(vmID)

            endtime = datetime.datetime.now() + datetime.timedelta(minutes=5)

            while installer.getClusters(cluster_id=cluster['id'])[0]['status'] != 'ready':
                if datetime.datetime.now() >= endtime:
                    logging.quitMessage("Cluster failed to move to ready state within 5 minutes. Please review your dashboard for manual intervention")

                logging.logMessage("Waiting for cluster status to be 'ready'")
                logging.prettyPrint(f"{installer.getClusters(name)}")
                logging.logMessage("Sleeping for 30 seconds before retrying")
                time.sleep(30)

            installer.installCluster(id=cluster['id'])

            while installer.getClusters(cluster_id=cluster['id'])[0]['status'] != 'installed':
                if 'total_percentage' in installer.getClusters(cluster_id=cluster['id'])[0]['progress']:
                    logging.logMessage(f"Installation is {installer.getClusters(cluster_id=cluster['id'])[0]['progress']['total_percentage']}% complete.")
                else: 
                    logging.logMessage(f"Installation is 0% complete.")
                time.sleep(30)  
        else:
            logging.quitMessage("Failed to create cluster")

@app.command()
def destroycluster(name: str):
    if not tools.validateName(name):
        logging.quitMessage("name: {} - is not a valid name that can be used with the assisted-installer. Please ensure the name conforms to the following regular expression: {}".format(name, "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"))

    deleteVMs = pve.getVMsWithTag(name)
    logging.logMessage(f"Found {len(deleteVMs)} VM's to delete from proxmox")
    for vm in deleteVMs:
        # delete vm
        pve.deleteVM(vm)
    # delete the iso file that was created and uploaded to pve
    pve.deleteISO(name)

    clusters = installer.getClusters()

    for cluster in clusters:
        if cluster['name'] == name:
            installer.deleteCluster(cluster['id'])
            infra = installer.getInfrastructureEnvironments(cluster_id=cluster['id'])
            if infra:
                installer.deleteInfrastructureEnvironment(infra[0]['id'])
            break

if __name__ == '__main__':
    app()