


class infraEnvCreateParams:
    def __init__(self, name, pullsecret, version=None, clusterid=None):
        self.params = {}
        self.params['name'] = name + "infra-env"
        self.params['pull_secret'] = pullsecret
        if version is not None:
            self.params['openshift_version'] = version
        if clusterid is not None:
            self.params['cluster_id'] = clusterid

    def getParams(self):
        return self.params