from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

class LoginManagerUD(DistributedObjectGlobalUD):
    """ A simple UberDOG object to verify 
    all new client connections """
    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)

    def login(self):
        """ This function gets called whenever the client
        sends the 'login' field update to us.

        Normally, if this were an real MMO, we would go 
        through the process of calling the online API's and
        verify the account's existance, but for demostration
        purposes, we'll just skip all that and assume all the
        info has been verified. """

        # First, get the ID of the sender...
        sender = self.air.getMsgSender()

        # Secondly, tell Astron to set this client
        # to the ESTABLISHED state, so that the client will 
        # have the full ability to send updates to all the non-anonymous
        # objects, and send interest messages.
        self.air.setClientState(sender, 2) # 2 = ESTABLISHED

        # And lastly, send the 'loginResp' update *directly*
        # to the client, and we're all done here!
        self.sendUpdateToChannel(sender, 'loginResp', [True])
