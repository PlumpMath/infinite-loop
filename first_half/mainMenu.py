from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame


class MainMenu:
    def __init__(self, assetLoader):
        self.notebook = assetLoader.modelLoader("/GUI/notebook.egg")
        self.buttons = assetLoader.modelLoader("/GUI/buttons.egg")
        self.score = assetLoader.modelLoader("/GUI/score.egg")
        # loads the egg files for the different componants of the menu

        self.notebookFrame = DirectFrame(geom=self.notebook, pos=(0, 0, -.91), relief=None)
        # creates and positions the frame which supplies the notebook background for the menu and encapsulates the rest of the menu.

        self.menuButton = DirectButton(geom=self.buttons.find("**/menu_ready"), borderWidth=(0, 0),
                                       frameSize=(-.115, .1, -.05, .05), pos=(-.5, 0, .05), rolloverSound=None,
                                       clickSound=None, relief=None)
        self.upButton = DirectButton(geom=(
        self.buttons.find("**/up_ready"), self.buttons.find("**/up_ready"), self.buttons.find("**/up_ready"),
        self.buttons.find("**/up_disabled")), borderWidth=(0, 0), frameSize=(-.1, .1, -.05, .05), pos=(-.18, 0, .05),
                                     rolloverSound=None, clickSound=None, relief=None)
        self.downButton = DirectButton(geom=(
        self.buttons.find("**/down_ready"), self.buttons.find("**/down_ready"), self.buttons.find("**/down_ready"),
        self.buttons.find("**/down_disabled")), borderWidth=(0, 0), frameSize=(-.1, .1, -.05, .05), pos=(.07, 0, .05),
                                       rolloverSound=None, clickSound=None, relief=None)
        self.plusButton = DirectButton(geom=self.buttons.find("**/plus_ready"), borderWidth=(0, 0),
                                       frameSize=(-.055, .055, -.05, .05), pos=(.35, 0, .05), rolloverSound=None,
                                       clickSound=None, relief=None)
        self.arrowsButton = DirectButton(geom=self.buttons.find("**/arrows_ready"), borderWidth=(0, 0),
                                         frameSize=(-.055, .055, -.05, .05), pos=(.515, 0, .05), rolloverSound=None,
                                         clickSound=None, relief=None)
        self.minusButton = DirectButton(geom=self.buttons.find("**/minus_ready"), borderWidth=(0, 0),
                                        frameSize=(-.055, .055, -.05, .05), pos=(.67, 0, .05), rolloverSound=None,
                                        clickSound=None, relief=None)
        self.starButton = DirectButton(geom=(
        self.buttons.find("**/star_ready"), self.buttons.find("**/star_ready"), self.buttons.find("**/star_ready"),
        self.buttons.find("**/star_disabled")), borderWidth=(0, 0), frameSize=(-.1, .1, -.05, .05), pos=(.89, 0, .05),
                                       rolloverSound=None, clickSound=None, relief=None)
        # creates each of the buttons and sets their positions


        self.menuButton.reparentTo(self.notebookFrame)
        self.upButton.reparentTo(self.notebookFrame)
        self.downButton.reparentTo(self.notebookFrame)
        self.plusButton.reparentTo(self.notebookFrame)
        self.arrowsButton.reparentTo(self.notebookFrame)
        self.minusButton.reparentTo(self.notebookFrame)
        self.starButton.reparentTo(self.notebookFrame)
        # parents all the buttons to the notebook frame, so their positions are relative to it.

        self.notebookFrame.setScale(.75, 1, .75)