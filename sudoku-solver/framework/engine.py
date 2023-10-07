class Engine:
    """
    Run in tight loop calling a callable and giving it this engine object.
    """

    def __init__(self, start=None, update=None):
        self.running = False
        self.start = start
        self.update = update

    def run(self, update=None):
        if update is not None:
            self.switch(update)
        if self.start is not None:
            self.start()
        self.running = True
        while self.running:
            self.update()

    def stop(self):
        self.running = False

    def switch(self, update):
        """
        Switch callable, called every loop iteration.
        """
        self.update = update
