import base

class Frame(base.Base):

    def __init__(self, image, duration=None):
        super(Frame, self).__init__()
        self.image = image
        if duration is None:
            duration = 100
        self.duration = duration


