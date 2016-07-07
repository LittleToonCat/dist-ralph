from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

class Ralph(DistributedSmoothNode):
    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)