import builtins
import sys
from panda3d.core import *
from direct.gui import *
from Ralph import Ralph
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

class RalphOV(Ralph):
    """
    The 'Owner View' implementation of the "Ralph" object.

    An "Owner View" of the object gets generated when a client receives 
    "full" ownership of the object, and it's always available even 
    when it's not visible on the client's visibility view. 

    Think of this as a "local" implementation of the object,
    so you can add stuff like movement, changing clothes,
    wear accessories, pretty much anything that no one 
    else can do except the owner of this object. 

    (Getting ownership also means it can send fields marked 'ownsend' 
    and it'll receive fields that are marked 'ownrecv'.)
    """
    def __init__(self, cr):
        Ralph.__init__(self, cr)
        self.chatEntry = None
        # This is used to store which keys are currently pressed.
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "cam-left": 0, "cam-right": 0}

    def announceGenerate(self):
        Ralph.announceGenerate(self)
        builtins.localAvatar = self
        messenger.send('localAvatarGenerated')
        self.chatEntry = DirectEntry.DirectEntry(text = "" ,scale=.07, pos=(-0.4, 0, -0.85), relief = DirectGuiGlobals.RIDGE, command = self.b_setChat)

    def isLocal(self):
        return True

    def b_setChat(self, chat):
        self.d_setChat(chat)
        self.setChat(chat)

    def d_setChat(self, chat):
        self.sendUpdate('setChat', [chat])

    def setCollisions(self):
        self.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0, 0, 9)
        self.ralphGroundRay.setDirection(0, 0, -1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.ralphGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.ralphGroundColNp = self.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0, 0, 9)
        self.camGroundRay.setDirection(0, 0, -1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
        self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

    def allowControls(self):
        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_up", self.setKey, ["forward", True])
        self.accept("a", self.setKey, ["cam-left", True])
        self.accept("s", self.setKey, ["cam-right", True])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("arrow_up-up", self.setKey, ["forward", False])
        self.accept("a-up", self.setKey, ["cam-left", False])
        self.accept("s-up", self.setKey, ["cam-right", False])

        taskMgr.add(self.move, "moveTask")

    # Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # Get the time that elapsed since last frame.  We multiply this with
        # the desired speed in order to find out with which distance to move
        # in order to achieve that desired speed.
        dt = globalClock.getDt()

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        if self.keyMap["cam-left"]:
            base.camera.setX(base.camera, -20 * dt)
        if self.keyMap["cam-right"]:
            base.camera.setX(base.camera, +20 * dt)

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.getPos()
        #print startpos

        # If a move-key is pressed, move ralph in the specified direction.

        if self.keyMap["left"]:
            self.setH(self.getH() + 300 * dt)
        if self.keyMap["right"]:
            self.setH(self.getH() - 300 * dt)
        if self.keyMap["forward"]:
            self.setY(self, -25 * 0.005)

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if self.keyMap["forward"] or self.keyMap["left"] or self.keyMap["right"]:
            if self.isMoving is False:
                self.actor.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.actor.stop()
                self.actor.pose("walk", 5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            base.camera.setPos(base.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            base.camera.setPos(base.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0

        # Check for collisions...
        self.cTrav.traverse(render)

        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = list(self.ralphGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            self.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.

        entries = list(self.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == "terrain":
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ() + 1.0)
        if base.camera.getZ() < self.getZ() + 2.0:
            base.camera.setZ(self.getZ() + 2.0)

        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        base.camera.lookAt(base.floater)

        #if self.getPos() == (0, 0, 0):
        #    ralphStartPos = base.cr.environ.find("**/start_point").getPos()
        #    self.setPos(ralphStartPos + (0, 0, 0.5))

        return task.cont