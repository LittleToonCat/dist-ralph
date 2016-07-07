from direct.distributed.DistributedObjectUD import DistributedObjectUD

class LoginManagerUD(DistributedObjectUD):
    def __init__(self, air):
        DistributedObjectUD.__init__(self, air)

    def login(self):
        pass