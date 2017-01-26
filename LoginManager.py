from direct.distributed.DistributedObject import DistributedObject

class LoginManager(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

    def login(self):
        """ This function sends an field update called 'login' 
        to Astron, and assuming the field is marked 'airecv', 
        it should send the message to whoever hosting 
        the object. (Most likely the UberDOG server.) """
        self.sendUpdate('login', [])

    def loginResp(self, success):
        """ When the server sends the 'loginResp'
        update to us, the engine *should* unserialize
        the sent message, and calls this function with
        the sent arguments. """
        messenger.send('loginResp', [success])