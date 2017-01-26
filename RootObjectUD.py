from direct.distributed.DistributedObjectUD import DistributedObjectUD

class RootObjectUD(DistributedObjectUD):
    """ This 'dummy' object may not look like much, 
    but it *is* important internally.

    Almost *all* objects needs a parent, and this object
    will be the parent to the 'LoginManager' and all
    the 'World' objects. (But not the Ralph avatars, they'll be parented to the world itself)
    And without this object's existance, Astron wouldn't be able to 
    parent the objects correctly, and it wouldn't be able direct the client's 
    inital interest messages.  Therefore, the client wouldn't receive 
    the 'World' objects as a result.
    """
    def __init__(self, air):
        DistributedObjectUD.__init__(self, air)