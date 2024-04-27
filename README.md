# aicli

## Description

A CLI written in python to configure, deploy, and manage Red Hat OpenShift clusters using the Red Hat Assisted Installer and your Red Hat account. The application will also interface with your choice of supported hypervisor to manage the virtual machine configurations backing the cluster. Effectivly, allowing us to automating the installation of (IPI) Installer-Provided-Infrastructrue OpenShift cluster for supported Hypervisors with a single command. 

Currently, there are two sizes supported

| Size | Control-Nodes | CPU (per-node) | Memory (per-node) | Storage (per-node) |
| ---  | ------------- | --- | ------ | ------- |
| sno (single node openshift) | 1 | 8 vcpu | 32000GiB | 200GiB | 
| compact - (##IN DEVELOPMENT##) | 3 | 4 | 16GiB | 200GiB| 

This CLI will use the [redhat-assisted-installer](https://pypi.org/project/redhat-assisted-installer/), and the [hcp-vault-secrets](https://pypi.org/project/hcp-vault-secrets/) python packages to configure the remaining environment variables `REDHAT_PULL_SECRET` and `REDHAT_OFFLINE_TOKEN` 
 

**Supported Hypervisors**

- Proxmox Virtual Environment 8


## Requirements

    pip install -r requirements.txt


### Environment Variables

#### hcp-vault-secrets

- `clientID`: This is the clientID that is associated with the service principal in HashiCorp Cloud Platform.

- `clientSecret`: This is the clientSecret that is associated with the service principal in HashiCorp Cloud Platform.

- `organizationID`: The HashiCorp Cloud Platform organization ID that owns the Vault Secrets application

- `projectID`: The HashiCorp Cloud Platform project ID where the Vault Secrets application is located


#### proxmoxCluster

- `proxmoxServiceIP`: The local IP of your proxmox virtual environment

- `proxmoxServicePort`: The port that your proxmox virtual environment is running on

- `proxmoxUser`: The username@pam used for authentication against the pve API

- `proxmoxNode`: The name of the proxmox node to connect to

## Commands

### deploycluster

    # using python interpreter
    $ python aicli.py deploycluster [OPTIONS] NAME VERSION BASEDOMAIN 

    # using binary
    $ aicli deploycluster [OPTIONS] NAME VERSION BASEDOMAIN 

**Options**

```
  name: name 
    required: true
    type: str
    description: name of the openshift cluster to create
    example: ocp

  name: version
    required: true
    type: str
    description: openshift version (major.minor)
    example: 4.15, 4.14

  name: basedomain
    required: true
    type: str
    description: base domain to build the openshift routes 
    example: "example.com"

  name: size
    required: false
    default: "sno"
    type: str
    description: the cluster size that you want to deploy
    example: "compact"
    choices: ["sno", "compact"]

  name: cpuarchitecture
    required: false
    default: "x86_64"
    type: str
    description: The cpu architecture of the baremetal hardware this cluster will run on 
    choices: ["x86_64", "aarch64", "arm64", "ppc64le", "s390x", "multi"]
```

### destroycluster

**python interpreter**

    $ python aicli.py destroycluster [OPTIONS] NAME 

**using binary**

    $ aicli destroycluster [OPTIONS] NAME 

**Options**

```
  name: name 
    required: true
    default: ""
    type: str
    description: name of the openshift cluster to delete
    example: ocp

```



## References

- [redhat-assisted-installer | pypi package documentation](https://pypi.org/project/redhat-assisted-installer/)

- [hcp-vault-secrets | pypi package documentation](https://pypi.org/project/hcp-vault-secrets/)