import group
import view

class Scene(group.Group):

    def __init__(self):
        super(Scene, self).__init__()
        self.views = [view.View()]

    def draw(self):
        for view in self.views:
            view.clear()
        return [member.draw() for member in self.members]

    def update(self):
        for view in self.views:
            view.update()
        super(Scene, self).update()


