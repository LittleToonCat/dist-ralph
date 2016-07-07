from direct.distributed.DistributedObject import DistributedObject

class LoginManager(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

    def login(self):
        pass