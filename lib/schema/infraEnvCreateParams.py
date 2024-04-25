


class infraEnvCreateParams:
    def __init__(self, name, pullsecret, version=None):
        self.params = {}
        self.params['name'] = name + "infra-env"
        self.params['pull_secret'] = pullsecret
        if version is not None:
            self.params['openshift_version'] = version

    def getParams(self):
        return self.params