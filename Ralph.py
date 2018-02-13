from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.actor.Actor import Actor
from panda3d.core import TextNode

class Ralph(DistributedSmoothNode):
    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)

        self.actor = None
        self.isMoving = False
        self.name = ''
        self.chat = ''
        self.nameText = None
        self.nameTextNP = None
        self.chatText = None
        self.chatTextNP = None

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
        self.chatText = TextNode('%d-chatText' % self.doId)
        self.chatText.setText(self.chat)
        self.chatText.setAlign(self.chatText.A_center)
        self.chatText.setTextColor(0.5, 0.5, 1, 1)
        self.chatNP = self.attachNewNode(self.chatText)
        self.chatNP.setScale(.35)
        self.chatNP.setPos(0, 0, 1.6)
        self.chatNP.setBillboardPointEye()

    def setName(self, name):
        self.name = name

    def setChat(self, chat):
        self.chat = chat
        self.chatText.setText(self.chat)

    def getChat(self):
        return self.chat

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
            