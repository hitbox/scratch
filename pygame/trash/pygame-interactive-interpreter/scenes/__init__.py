class SceneError(Exception):
    pass


class SceneManager:

    def __init__(self, initial=None):
        self.scene = initial
        self.nextscene = None

    def current(self):
        return self.scene

    def switch(self, nextscene):
        """
        Flag a scene to switch to on next update.
        """
        if self.nextscene is not None:
            raise SceneError('Scene switch already pending.')
        self.nextscene = nextscene

    def has_nextscene(self):
        return self.nextscene is not None

    def do_switch(self):
        """
        Actually do switch between scenes calling the appropriate `enter` and
        `exit` methods.
        """
        if self.scene is not None:
            self.scene.exit()
        self.scene = self.nextscene
        self.scene.enter()
        self.clear_sceneswitch()

    def clear_sceneswitch(self):
        self.nextscene = None

    def update(self):
        """
        Call every frame. If a scene is waiting to switch to, do the switch.
        """
        if self.has_nextscene():
            self.do_switch()
        return self.current()


_scenemanager = SceneManager()

def switch(nextscene):
    _scenemanager.switch(nextscene)

def update():
    return _scenemanager.update()

switch.__doc__ = _scenemanager.switch.__doc__
update.__doc__ = _scenemanager.update.__doc__
