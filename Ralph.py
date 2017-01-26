from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.actor.Actor import Actor
from panda3d.core import TextNode

class Ralph(DistributedSmoothNode):
    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)

        self.actor = None
        self.isMoving = False
        self.name = ''
        self.nameText = None
        self.nameTextNP = None

    def announceGenerate(self):
        DistributedSmoothNode.announceGenerate(self)
        self.activateSmoothing(True, False)
        self.startSmooth()

        self.loadActor()
        self.reparentTo(render)

    def disable(self):
        # Take it out of the scene graph.
        self.detachNode()

        DistributedSmoothNode.disable(self)

    def delete(self):
        # Stop the smooth task.
        self.stopSmooth()
        
        # Clean out self.model, so we don't have a circular reference.
        self.model = None

        DistributedSmoothNode.delete(self)

    def loadActor(self):
        if self.actor:
            self.actor.cleanup()
            
        self.actor = Actor('models/ralph',
                           {'walk' : 'models/ralph-walk',
                            'run' : 'models/ralph-run'})
        self.actor.reparentTo(self)
        self.actor.setScale(.2)

        # Setup a really simple nametag so we can know it's name.
        self.nameText = TextNode('%d-nameText' % self.doId)
        self.nameText.setText(self.name)
        self.nameText.setAlign(self.nameText.A_center)
        self.nameNP = self.attachNewNode(self.nameText)
        self.nameNP.setScale(.25)
        self.nameNP.setPos(0, 0, 1.2)
        self.nameNP.setBillboardPointEye()

    def setName(self, name):
        self.name = name

    def isLocal(self):
        return False

    def smoothPosition(self):
        """ This gets called when the position update
        has been received.  It determines whether
        to animate the object or not. """
        DistributedSmoothNode.smoothPosition(self)
        if not self.isLocal():
            if self.smoother.getSmoothForwardVelocity() or self.smoother.getSmoothRotationalVelocity():
                if self.isMoving == False:
                    self.actor.loop("run")
                    self.isMoving = True
            else:
                if self.isMoving == True:
                    self.actor.stop()
                    self.actor.pose("walk", 5)
                    self.isMoving = False
            