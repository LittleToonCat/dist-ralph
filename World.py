from direct.distributed.DistributedObject import DistributedObject

class World(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)