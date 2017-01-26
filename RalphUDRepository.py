import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--base-channel', help='The base channel that the server may use.',
                    type=int, default=100000000)
parser.add_argument('--stateserver', help="The control channel of this UD's designated State Server.",
                    type=int, default=402000)
parser.add_argument('--astron-ip', help="The IP address of the Astron Message Director to connect to.",
                    default='127.0.0.1:7190')

args = parser.parse_args()

from panda3d.core import *
loadPrcFileData('', 'window-type none\naudio-library-name null')
from direct.showbase.ShowBase import ShowBase
from direct.distributed.AstronInternalRepository import AstronInternalRepository
from RalphGlobals import *
from RootObjectUD import RootObjectUD
from LoginManagerUD import LoginManagerUD

class RalphUDRepostiory(AstronInternalRepository):
    """ This 'UberDOG' server will host all 'static' objects 
     with pre-defined ID's.  Such objects should handle complicated tasks
     like account verifiation, real money transactions, and what not. """

    def __init__(self, args):
        dcFileNames = ['direct.dc', 'ralph.dc']

        self.baseChannel = args.base_channel

        self.GameGlobalsId = GAME_GLOBALS_ID

        self.serverId = args.stateserver

        AstronInternalRepository.__init__(self, self.baseChannel, self.serverId, dcFileNames = dcFileNames,
                                  dcSuffix = 'UD', connectMethod = self.CM_NET,
                                  threadedNet = True)

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
            Now to generate the LoginManager """
        print 'Connected Successfully!'

        # Generate our 'dummy' object...
        rootObj = RootObjectUD(self)
        rootObj.generateWithRequiredAndId(self.GameGlobalsId, 0, 0)

        # Claim this object's ownership...
        self.setAI(self.GameGlobalsId, self.baseChannel)
        
        # And then generate the LoginManager itself. 
        # (It's ownership is defined automaticly internally)
        loginManager = LoginManagerUD(self)
        loginManager.generateWithRequiredAndId(LOGIN_MANAGER_DO_ID, self.GameGlobalsId, 0)

base = ShowBase()
base.air = RalphUDRepostiory(args)
base.run()