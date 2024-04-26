import proxmoxer, os, jmespath, time, paramiko

from lib import logging


class proxmoxcluster:
    def __init__(self, password):
        self.serviceIP = os.environ.get("proxmoxServiceIP")
        self.servicePort = os.environ.get("proxmoxServicePort")
        self.serviceFQDN = "{}:{}".format(self.serviceIP, self.servicePort)
        self.username = os.environ.get("proxmoxUser")
        self.node = os.environ.get("proxmoxNode")
        self.password = password
        self.proxmox = self.authenticate()

    def sshCommand(self, ip, port, username, password, command):
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        
        # Automatically add untrusted hosts (make sure okay for security policy in your environment)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Connect to the host
            ssh.connect(ip, port=port, username=username, password=password)
            
            # Execute the command
            stdin, stdout, stderr = ssh.exec_command(command)
            
            # Read output from the command
            output = stdout.read().decode()
            
            # Optionally, handle errors if any from stderr
            error = stderr.read().decode()
            if error:
                return error

            return output
            
        except Exception as e:
            print("Connection Failed")
            print(e)
        finally:
            # Close the connection
            ssh.close()


    def authenticate(self):
        url = "{}/api2/json".format(self.serviceFQDN)
        self.proxmox = proxmoxer.ProxmoxAPI(url, user=self.username, password=self.password, verify_ssl=False)
        return self.proxmox
        
    def isAuthenticated(self):
        try:
            # Attempt to get Proxmox version or other harmless data
            version = self.proxmox.version.get()
            logging.logMessage("Successfully authenticated. Proxmox version: {}".format(version))
            return True
        except proxmoxer.core.ResourceException as e:
            # Handle specific exceptions related to authentication issues
            logging.errorMessage("Authentication failed or session expired: {}".format(e))
            return False
        except Exception as e:
            # General exception handling if needed
            logging.quitMessage("Error during authentication check: {}".format(e))

    def getVMs(self):
        if self.isAuthenticated():
            # return api response
            return self.proxmox.nodes(self.node).qemu.get()
        else:
            logging.errorMessage("API call failed due to authentication")
            self.authenticate()
            self.getVMs()

    def uploadISO(self, url, name):
        command = f"pvesh create /nodes/{self.node}/storage/local/download-url --content=iso --filename={name}.iso --url={url}"
        logging.logMessage(command)
        return self.sshCommand(self.serviceIP, 22, "root", self.password, command)
    
    def deleteISO(self, name):
        command = f'pvesh get nodes/{self.node}/storage/local/content/iso/{name}.iso'
        commandresult = self.sshCommand(self.serviceIP, 22, "root", self.password, command)
        if f'failed to stat' in commandresult:
            logging.logMessage("ISO file is already removed")
            return True
        command = f'pvesh delete nodes/{self.node}/storage/local/content/iso/{name}.iso'
        self.sshCommand(self.serviceIP, 22, "root", self.password, command)
        return True


    def getVMWithID(self, id):
        if self.isAuthenticated():
            return self.proxmox.nodes(self.node).qemu(id)
        else:
            self.authenticate()
            self.getVMWithID(id)

    # given that a vm returned from the method getVMs() will contain a tags field
    # if the vm has a tag 
    def getVMsWithTag(self, tag):
        try:
            # Get list of VMs on the specified node
            vm_list = self.getVMs()
            # for loop to prepare the data
            # currently, vms returned contain a tags field 'if and only if' the vm has a tag specified in it's config
            # (tags field is a ';' seperated string that needs to be of type list before jmespath query will work)
            # if not, the tags field is omitted
            #
            # create a new array of 'query-able' vm's
            # BUG: if a vm does not have a tag, the jmespath expression will fail
            # 
            # Therefore, we need to create new array, and only append the vms with 
            # a 'tags' field
            search_list = []
            for vm in vm_list:
                # safe check to see if 'tags' is defined in the vm config
                if 'tags' in vm:
                    # split vm['tags'] by ';' and turn it into a list object
                    vm['tags'] = vm['tags'].split(';')
                    search_list.append(vm)

            # JMESPath expression to find VMs with a specific tag
            # Adjust the expression as needed based on the structure of your data.
            expression = f"[?tags && contains(tags, '{tag}')]"
            # Return an array of vms that contains the tag specified
            return jmespath.search(expression, search_list)

        except Exception as e:
            logging.quitMessage(f"Error retrieving VMs from node {self.node}: {e}")


    def shutDownVM(self, vm):
        sleeptime = 2
        try:
            # Get the current vm status
            vm_status = self.proxmox.nodes(self.node).qemu(vm['vmid']).status.current.get()
            
            # if the vm is not stopped 
            if vm_status['status'] != 'stopped':
                # Send shutdown command to the VM
                logging.logMessage(f"Initiating shutdown for VM ID {vm['vmid']}")
                # send api request to stop
                if self.isAuthenticated():
                    self.proxmox.nodes(self.node).qemu(vm['vmid']).status.stop.post()
                else:
                    self.authenticate()
                # get vm status
                vm_status = self.proxmox.nodes(self.node).qemu(vm['vmid']).status.current.get()
            
                # Wait for the VM to shutdown
                while vm_status['status'] != 'stopped':
                    logging.logMessage(f"VM {vm['vmid']} current status: {vm['status']}.")
                    # Delay for poll_interval seconds before checking again
                    time.sleep(2)  
                    logging.logMessage(f"Waiting for VMID: {vm['vmid']} to move to 'stopped' status. Sleeping for {sleeptime} seconds")
                    # update vm_status var
                    vm_status = self.proxmox.nodes(self.node).qemu(vm['vmid']).status.current.get()

            return True

        except proxmoxer.ResourceException as e:
            if e.status_code == 500 and 'VM is locked' in str(e):
                logging.logMessage("VM is currently locked (possibly already shutting down). Please wait.")
                return False
            else:
                logging.quitMessage(f"Error during shutdown operation: {e}")
        except Exception as e:
            logging.quitMessage(f"Error retrieving VM status: {e}")

    def deleteVM(self, vm):
        if self.shutDownVM(vm):
            self.proxmox.nodes(self.node).qemu(vm['vmid']).delete()
            return True
        else:
            return False
        
    def defineVM(self, name):
        # vmid is required param to create vm using api
        vmID = 100
        for vm in self.getVMs():
            if vm['vmid'] > vmID:
                vmID = vm['vmid']

        vmID += 1
        # Define the VM parameters
        vm_params = {
            'vmid': vmID,
            'name': name,
            'memory': 32500,
            'cores': 8,
            'cpu': "x86-64-v2-AES",
            'ostype': "l26",
            'boot': 'order=scsi0;ide2;net0',
            'bios': 'ovmf',
            'scsihw': "virtio-scsi-single",
            'ide2': f'local:iso/{name}.iso,media=cdrom',
            'scsi0': f"local-lvm:{300}",
            'net0': "virtio,bridge=vmbr0,firewall=1",
            'machine': "q35",
            'onboot': 1,
            'acpi': 1,
            'agent': 'enabled=1',
            'hotplug': 'disk,network,usb',
            'efidisk0': 'local-lvm:4,size=4M,format=raw,efitype=4m',
            'tags': f'{name}' 
        }
        
        if self.isAuthenticated():
            try: 
                vm = self.proxmox.nodes(self.node).qemu.create(**vm_params)
                logging.logMessage(f"Sucessfully created vm {vm}")
                return vmID
            except Exception as e:
                logging.quitMessage(f"failed to create vm with error:\n{e}")

        else:
            self.authenticate()
            self.defineVM(name)


    
    def startVM(self, vmid):
        if self.isAuthenticated():
            try: 
                vm = self.proxmox.nodes(self.node).qemu(vmid).status.post('start')
                logging.logMessage(vm)
                return vm

            except Exception as e:
                logging.quitMessage(f"failed to start vm with error:\n{e}")

        else:
            self.authenticate()
            self.startVM(vmid)