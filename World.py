from direct.distributed.DistributedObject import DistributedObject

class World(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.name = ''
        self.population = 0

    def announceGenerate(self):
        self.cr.worlds.append(self)
        messenger.send('updateWorlds')

    def setName(self, name):
        self.name = name

    def setPopulation(self, pop):
        self.population = pop

    def requestJoin(self, name):
        self.sendUpdate('requestJoin', [name])

    def nameOccupied(self):
        messenger.send('nameOccupied')