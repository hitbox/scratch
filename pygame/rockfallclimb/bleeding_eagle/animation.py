import base
import core

class Animation(base.Base):

    def __init__(self, frames, repeat=None):
        super(Animation, self).__init__()
        self.frames = frames
        self.index = 0
        self.elapsed = 0
        self.repeat = repeat
        # XXX: callbacks?
        self.done = False

    def reset(self):
        self.index = 0
        self.elapsed = 0
        self.done = False

    @property
    def frame(self):
        return self.frames[self.index]

    @property
    def image(self):
        return self.frame.image

    def update(self):
        self.elapsed += core.Core.elapsed
        if self.elapsed >= self.frame.duration:
            # time for next frame
            if self.repeat:
                self.index = (self.index + 1) % len(self.frames)
            elif self.index + 1 < len(self.frames):
                self.index += 1
            else:
                self.done = True
            self.elapsed -= self.frame.duration


