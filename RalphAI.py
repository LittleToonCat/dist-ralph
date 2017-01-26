from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI

class RalphAI(DistributedSmoothNodeAI):
    def __init__(self, air):
        DistributedSmoothNodeAI.__init__(self, air)
        self.air = air
        self.name = ''

    def delete(self):
        DistributedSmoothNodeAI.delete(self)
        base.air.avatars.remove(self)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name