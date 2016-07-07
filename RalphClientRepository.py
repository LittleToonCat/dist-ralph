from direct.distributed.AstronClientRepository import AstronClientRepository
from direct.showbase.ShowBase import ShowBase

class RalphClientRepository(AstronClientRepository):
	def __init__(self):
		dcFileNames = ['direct.dc', 'ralph.dc']

		AstronClientRepository.__init__(self, dcFileNames)

		self.loginManager = self.generateGlobalObject(1001, 'LoginManager')

base = ShowBase()
base.cr = RalphClientRepository()
base.run()