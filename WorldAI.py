from direct.distributed.DistributedObjectAI import DistributedObjectAI
from RalphGlobals import *
from RalphAI import RalphAI
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *

class WorldAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.name = ''
        self.population = 0

    def setName(self, name):
        self.name = name

    def d_setName(self, name):
        self.sendUpdate('setName', [name])

    def b_setName(self, name):
        self.setName(name)
        self.d_setName(name)

    def getName(self):
        return self.name

    def setPopulation(self, pop):
        self.population = pop

    def d_setPopulation(self, pop):
        self.sendUpdate('setPopulation', [pop])

    def b_setPopulation(self, pop):
        self.setPopulation(pop)
        self.d_setPopulation(pop)

    def getPopulation(self):
        return self.population

    def requestJoin(self, name):
        sender = self.air.getMsgSender()
        for avatar in self.air.avatars:
            if avatar.name == name:
                # The name is taken, so let's tell
                # the client that.
                self.sendUpdateToChannel(sender, 'nameOccupied', [])
                return
        ralph = RalphAI(self.air)
        ralph.setName(name)
        ralph.generateWithRequired(0)
        self.air.setOwner(ralph.doId, sender)
        self.air.clientAddSessionObject(sender, ralph.doId)

        dg = PyDatagram()
        dg.addServerHeader(sender, self.air.ourChannel, CLIENTAGENT_SET_CLIENT_ID)
        dg.addChannel(self.GetPuppetConnectionChannel(ralph.doId))
        self.air.send(dg)

        self.air.avatars.append(ralph)