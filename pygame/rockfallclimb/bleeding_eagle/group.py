import base

class Group(base.Base):
    
    def __init__(self):
        super(Group, self).__init__()
        self.members = []

    def update(self):
        for member in self.members:
            member.update()


