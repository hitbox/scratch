from framework.engine import Engine

from .app import SudokuApp

def run():
    """
    Run main Sudoku board GUI.
    """
    # XXX: each refering to each other
    engine = Engine()
    gui = SudokuApp(engine)
    engine.start = gui.start
    engine.update = gui.update
    engine.run()
