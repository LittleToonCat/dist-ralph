import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--name', help='The name of the World this AI server will generate', 
                    default='World')
parser.add_argument('--base-channel', help='The base channel that the server may use.',
                    type=int, default=200000000)
parser.add_argument('--stateserver', help="The control channel of this AI's designated State Server.",
                    type=int, default=402000)
parser.add_argument('--astron-ip', help="The IP address of the Astron Message Director to connect to.",
                    default='127.0.0.1:7190')

args = parser.parse_args()

from panda3d.core import *
loadPrcFileData('', 'window-type none\naudio-library-name null')
from direct.showbase.ShowBase import ShowBase
from RalphGlobals import *
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.distributed.TimeManagerAI import TimeManagerAI
from WorldAI import WorldAI

class RalphAIRepository(AstronInternalRepository):
    def __init__(self, args):
        dcFileNames = ['direct.dc', 'ralph.dc']

        self.baseChannel = args.base_channel

        self.GameGlobalsId = GAME_GLOBALS_ID

        self.serverId = args.stateserver

        AstronInternalRepository.__init__(self, self.baseChannel, self.serverId, dcFileNames = dcFileNames,
                                  dcSuffix = 'UD', connectMethod = self.CM_NET,
                                  threadedNet = True)

        # This is needed so we can generate objects to our World object.
        self.districtId = self.allocateChannel()

        self.worldName = args.name

        # List of generated Ralph objects.
        self.avatars = []

        # Allow some time for other processes.
        base.setSleep(0.01)

        if ':' in args.astron_ip:
            hostname, tcpPort = args.astron_ip.split(':')
        else:
            hostname = args.astron_ip
            tcpPort = 7190
        self.acceptOnce('airConnected', self.connectSuccess)
        self.connect(hostname, int(tcpPort))

    def connectSuccess(self):
        """ Successfully connected to the Message Director.
            Now to generate our World! """
        print('Connected Successfully!')

        self.world = WorldAI(self)
        self.world.setName(self.worldName)
        self.world.generateWithRequiredAndId(self.districtId, self.GameGlobalsId, ZONE_ID_WORLDS)
        self.setAI(self.districtId, self.baseChannel)

        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(ZONE_ID_MANAGERS)

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF

base = ShowBase()
base.air = RalphAIRepository(args)
base.run()