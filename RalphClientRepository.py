from direct.distributed.AstronClientRepository import AstronClientRepository
from direct.showbase.ShowBase import ShowBase
from RalphGlobals import *
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from direct.task import Task
from panda3d.core import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *

loadPrcFile('ralph.prc')

class RalphClientRepository(AstronClientRepository, FSM):
    def __init__(self):
        dcFileNames = ['direct.dc', 'ralph.dc']

        AstronClientRepository.__init__(self, dcFileNames)
        FSM.__init__(self, 'RalphClientRepository')

        self.GameGlobalsId = GAME_GLOBALS_ID
        # Generate the LoginManager staticly, so it'll be always available.
        self.loginManager = self.generateGlobalObject(LOGIN_MANAGER_DO_ID, 'LoginManager')

        self.worldsInterest = None
        self.managerInterest = None
        self.areaInterest = None

        self.worlds = []
        self.itemId2worldId = {}

        # Set the background color to black
        base.win.setClearColor((0, 0, 0, 1))

        # HACK: Handlers for object generation with OTHER fields is missing from AstronClientRepository
        # so we'll add one of them here until the PR which adds the functions to ACR has been merged.
        # https://github.com/Astron/panda3d/pull/17/
        self.message_handlers[CLIENT_ENTER_OBJECT_REQUIRED_OTHER] = self.handleEnterObjectRequiredOther

    def enterConnect(self):
        self.text = OnscreenText(text='Connecting...', fg=(1, 1, 1, 1), pos = (0, 0.00), scale = 0.07)
        url = URLSpec('g://127.0.0.1:4430')
        self.connect([url], successCallback=self.connectSuccess)

    def connectSuccess(self):
        """ We are connected, but we're not done yet.
        First, we send an CLIENT_HELLO message to make 
        sure our version and DC files are in sync... """

        self.sendHello('ralph')
        taskMgr.doMethodLater(10, self.connectFailed, 'HelloTimeout')
        base.acceptOnce('CLIENT_HELLO_RESP', lambda : self.request('Login'))

    def connectFailed(self, task = None):
        self.request('Failed')
        return Task.done

    def exitConnect(self):
        taskMgr.remove('HelloTimeout')
        self.text.destroy()

    def enterLogin(self):
        """ Now, we authenticate ourselves by sending a login request to
        the LoginManager.  After that, the UD server should then tell 
        Astron that we're good to go. """
        self.text = OnscreenText(text='Authenticating...', fg=(1, 1, 1, 1), pos = (0, 0.00), scale = 0.07)
        taskMgr.doMethodLater(10, self.connectFailed, 'LoginTimeout')
        self.loginManager.login()
        base.acceptOnce('loginResp', self.loginResp)

    def loginResp(self, success):
        taskMgr.remove('LoginTimeout')
        if success:
            self.request('Menu')
        else:
            print('Login failed!')

    def exitLogin(self):
        self.text.destroy()

    def enterMenu(self):
        
        self.text1 = OnscreenText(text='Enter a name:', fg=(1, 1, 1, 1), pos=(-0.05, 0.4), scale = 0.07)
        self.nameEntry = DirectEntry(text = "" ,scale=.07, pos=(-0.4, 0, 0.3))
        self.text2 = OnscreenText(text='Select a world:', fg=(1, 1, 1, 1), pos=(-0.05, 0.0), scale = 0.07)

        #self.menuFrame = DirectScrolledFrame(canvasSize = (-2,2,-2,2), frameSize = (-.5,.5,-.5,.5), autoHideScrollBars=True)

        self.list = DirectScrolledList(
            decButton_pos= (0.35, 0, 0.53),
            decButton_text = "Dec",
            decButton_text_scale = 0.04,
            decButton_borderWidth = (0.005, 0.005),
 
            incButton_pos= (0.35, 0, -0.02),
            incButton_text = "Inc",
            incButton_text_scale = 0.04,
            incButton_borderWidth = (0.005, 0.005),
 
            frameSize = (0.0, 0.7, -0.05, 0.59),
            #frameColor = (1,0,0,0.5),
            pos = (-0.4, 0, -0.65),
            items = [],
            numItemsVisible = 4,
            forceHeight = 0.11,
            itemFrame_frameSize = (-0.2, 0.2, -0.37, 0.11),
            itemFrame_pos = (0.35, 0, 0.4),
            )

        if not self.worldsInterest:
            # Get the 'World' objects so we can make a choice of which world to connect to.
            self.worldsInterest = self.addInterest(self.GameGlobalsId, ZONE_ID_WORLDS, 'worlds selection', 'WorldInterestFinished')

        base.acceptOnce('WorldInterestFinished', self.worldInterestFinished)

    def worldInterestFinished(self):
        for world in self.worlds:
            button = DirectButton(text=world.name, text_scale=0.1, borderWidth = (0.01, 0.01), relief=2,
                                  command=self.worldSelect, extraArgs=[world])
            self.list.addItem(button)

    def worldSelect(self, world):
        name = self.nameEntry.get()
        self.joinedWorld = world
        world.requestJoin(name)
        base.acceptOnce('nameOccupied', self.nameOccupied)
        base.acceptOnce('localAvatarGenerated', self.localAvatarGenerated)

    def nameOccupied(self):
        self.text1.setText('The name has been taken, try a different name.')

    def localAvatarGenerated(self):
        """ Before doing anything else, we must get our globalClock
        to be in sync with the server. """
        if not self.managerInterest:
            self.managerInterest = self.addInterest(self.joinedWorld.doId, ZONE_ID_MANAGERS, 'world managers')
        else:
            self.alterInterest(self.managerInterest, self.joinedWorld.doId, ZONE_ID_MANAGERS, 'world managers')
        base.acceptOnce('gotTimeSync', self.gotTimeSync)
        
    def gotTimeSync(self):
        self.request('World')

    def exitMenu(self):
        self.text1.destroy()
        self.nameEntry.destroy()
        self.text2.destroy()
        self.list.destroy()

    def enterWorld(self):
        self.environ = loader.loadModel("models/world")
        self.environ.reparentTo(render)

        base.floater = NodePath(PandaNode("floater"))
        base.floater.reparentTo(localAvatar)
        base.floater.setZ(2.0)

        localAvatar.setCollisions()
        localAvatar.allowControls()

        # Send a interest request to the world with the area zone so we can see other players. 
        if not self.areaInterest:
            self.areaInterest = self.addInterest(self.joinedWorld.doId, ZONE_ID_AREA, 'world area')
        else:
            self.alterInterest(self.areaInterest, self.joinedWorld.doId, ZONE_ID_AREA, 'world area')

        # Move our object to the area zone so other players can see it.
        localAvatar.b_setLocation(self.joinedWorld.doId, ZONE_ID_AREA)

        ralphStartPos = self.environ.find("**/start_point").getPos()
        localAvatar.setPos(ralphStartPos + (0, 0, 0.5))

        # Set up the camera
        base.disableMouse()
        base.camera.setPos(localAvatar.getX(), localAvatar.getY() + 10, 2)

        # Automaticly send our position every second or so.
        localAvatar.startPosHprBroadcast()

    def exitWorld(self):
        pass

    def sendSetLocation(self, doId, parentId, zoneId):
        """ Called by b_setLocation """
        dg = PyDatagram()
        dg.addUint16(CLIENT_OBJECT_LOCATION)
        dg.addUint32(doId)
        dg.addUint32(parentId)
        dg.addUint32(zoneId)
        self.send(dg)

    # Copied from my PR
    def handleEnterObjectRequiredOther(self, di):
        do_id = di.get_uint32()
        parent_id = di.get_uint32()
        zone_id = di.get_uint32()
        dclass_id = di.get_uint16()
        dclass = self.dclassesByNumber[dclass_id]
        self.generateWithRequiredOtherFields(dclass, do_id, di, parent_id, zone_id)


base = ShowBase()
base.cr = RalphClientRepository()
base.cr.request('Connect')
base.run()