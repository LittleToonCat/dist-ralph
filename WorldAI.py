from direct.distributed.DistributedObjectAI import DistributedObjectAI

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

    def requestEnter(name):
        pass