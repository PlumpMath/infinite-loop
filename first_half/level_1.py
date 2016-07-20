import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase.InputStateGlobal import inputState
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from panda3d.core import Mat4
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import PandaNode,NodePath,TextNode
from panda3d.core import Fog

from enemy import Enemy
from player import Player

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape

from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import ZUp


# -------DISPLAY-------
# Display instructions for player, title of game, and number of items left to collect
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1), pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

def addNumObj(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),pos=(1.3, 0.95), align=TextNode.ARight, scale = .055)


class level_1(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Input
        self.accept('escape', self.doExit)
        # self.accept('space', self.doJump)

        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('turnLeft', 'a')
        inputState.watchWithModifiers('turnRight', 'd')

        # Post the instructions
        self.title = addTitle("Infinite Loop: A Robot's Nightmare")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[W]: Run Forward")
        self.inst3 = addInstructions(0.85, "[A]: Turn Left")
        self.inst4 = addInstructions(0.80, "[S]: Walk Backwards")
        self.inst5 = addInstructions(0.75, "[D]: Turn Right")
        self.inst6 = addInstructions(0.70, "[MOUSE]: Look")
        self.inst7 = addInstructions(0.65, "[SPACE]: Jump")

        # Game state variables
        self.lettersRemaining = 5
        self.letters = []
        self.health = 100

        # Number of collectibles
        self.numObjects = addNumObj(
            "Find letters B R E A K to escape\nLetters Remaining: " + str(self.lettersRemaining))

        # Health Bar
        self.bar = DirectWaitBar(text="H E A L T H",
                                 value=100,  # start with full health
                                 pos=(0, .4, 0.93),  # position healthbar to top center
                                 scale=(1.3, 2.5, 2.5),
                                 barColor=(0.97, 0, 0, 1),
                                 frameSize=(-0.3, 0.3, 0, 0.025),
                                 text_mayChange=1,
                                 text_shadow=(0, 0, 0, 0),
                                 text_fg=(0.9, 0.9, 0.9, 1),
                                 text_scale=0.030,
                                 text_pos=(0, 0.005, 0))
        self.bar.setBin("fixed", 0)  # health bar gets drawn in last scene
        self.bar.setDepthWrite(False)  # turns of depth writing so it doesn't interfere with itself
        self.bar.setLightOff()  # fixes the color on the bar itself

        # Camera follows mouse
        mat = Mat4(camera.getMat())
        mat.invertInPlace()
        base.mouseInterfaceNode.setMat(mat)
        base.enableMouse()

        # Go through gamesetup sequence
        self.setup()

        # Add update task to task manager
        taskMgr.add(self.update, 'updateWorld')

        # Create a floater object
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

    def doExit(self):
        self.cleanup()
        sys.exit(1)

    def doReset(self):
        self.cleanup()
        self.setup()

    def createPlatform(self, x, y, z):
        self.platform = loader.loadModel('../models/disk/disk.egg')
        geomnodes = self.platform.findAllMatches('**/+GeomNode')
        gn = geomnodes.getPath(0).node()
        geom = gn.getGeom(0)
        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        node = BulletRigidBodyNode('Platform')
        node.setMass(0)
        node.addShape(shape)
        platformnn = render.attachNewNode(node)
        platformnn.setPos(x, y, z)
        platformnn.setScale(3)

        self.world.attachRigidBody(node)
        self.platform.reparentTo(platformnn)

    def createLetter(self, loadFile, x, y, z):
        self.letter = loader.loadModel(loadFile)
        geomnodes = self.letter.findAllMatches('**/+GeomNode')
        gn = geomnodes.getPath(0).node()
        geom = gn.getGeom(0)
        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        node = BulletRigidBodyNode('Letter')
        node.setMass(0)
        node.addShape(shape)

        self.letters.append(node)
        letternn = render.attachNewNode(node)
        letternn.setPos(x, y, z)
        letternn.setScale(1)
        letternn.setP(90) # orients the mesh for the letters to be upright

        self.world.attachRigidBody(node)
        self.letter.reparentTo(letternn)

        self.letter.setP(-90) # orients the actual letter objects to be upright

    # Collect the letters
    def collectLetters(self):
        for letter in self.letters:
            contactResult = self.world.contactTestPair(self.player.character, letter)
            if len(contactResult.getContacts()) > 0:
                letter.removeAllChildren()
                self.world.remove(letter)
                self.letters.remove(letter)
                self.numObjects.setText("Find letters B R E A K to escape\nLetters Remaining: " + str(len(self.letters)))

    # When robot comes in contact with enemy, health is reduced
    def reduceHealth(self):
        self.bar["value"] -= 3

    def update(self, task):

        dt = globalClock.getDt()
        self.player.processInput(dt)
        self.world.doPhysics(dt, 4, 1./240.)

        self.player.cameraFollow(self.floater)

        # Identifying player collecting items
        self.collectLetters()

        # Menus for winning/losing conditions
        if self.bar["value"] < 1:
            mainmenuTitle = OnscreenImage(image='../models/sorry.png', pos=(0, 0, 0))
            mainmenuTitle.setTransparency(TransparencyAttrib.MAlpha)

            mainmenuLoadGame = DirectButton(image='../models/retry_button.png', scale=.08, relief=None)
            mainmenuLoadGame.setTransparency(1)
            mainmenuLoadGame.resetFrameSize()
            self.doReset()

        if len(self.letters) == 4:
            levelclear = OnscreenImage(image='../models/beat_level_1.png')
            levelclear.setTransparency(TransparencyAttrib.MAlpha)

            mainmenuLoadGame = DirectButton(image='../models/retry_button.png', scale=.08, relief=None)
            mainmenuLoadGame.setTransparency(1)
            mainmenuLoadGame.resetFrameSize()
            self.doReset()

        return task.cont

    def cleanup(self):
        render.getChildren().detach()
        self.world = None

    def setup(self):

        # Physics World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        # Main Character
        self.player = Player()
        self.player.createPlayer(render, self.world)

        # Music
        backgroundMusic = loader.loadSfx('../sounds/elfman-piano-solo.ogg')
        backgroundMusic.setLoop(True)
        backgroundMusic.play()
        # backgroundMusic.setVolume(4.0)  # will need to lower this when I add sound effects

        # Skybox
        self.skybox = loader.loadModel('../models/skybox.egg')
        self.skybox.setScale(900) # make big enough to cover whole terrain
        self.skybox.setBin('background', 1)
        self.skybox.setDepthWrite(0)
        self.skybox.setLightOff()
        self.skybox.reparentTo(render)

        # Lighting
        dLight = DirectionalLight("dLight")
        dLight.setColor(Vec4(0.8, 0.8, 0.5, 1))
        dLight.setDirection(Vec3(-5, -5, -5))
        dlnp = render.attachNewNode(dLight)
        dlnp.setHpr(0, 60, 0)
        render.setLight(dlnp)
        aLight = AmbientLight("aLight")
        aLight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alnp = render.attachNewNode(aLight)
        render.setLight(alnp)

        # Fog
        colour = (0.2, 0.2, 0.3)
        genfog = Fog("general fog")
        genfog.setColor(*colour)
        genfog.setExpDensity(0.0018)
        render.setFog(genfog)
        base.setBackgroundColor(*colour)

        # Platform to collect B
        self.createPlatform(72, 70.2927, -1)

        # Platforms to collect R
        self.createPlatform(211, 210, -1)
        self.createPlatform(231, 227.5, 1)

        # Platforms to collect E and A
        self.createPlatform(330, 462, -0.4)
        self.createPlatform(340, 471, 2.1)
        self.createPlatform(350, 480, 4)
        self.createPlatform(335, 483, 5)

        # Platforms to collect K
        self.createPlatform(10, 739, -1)
        self.createPlatform(10, 75, -1)
        self.createPlatform(27, 722, -1)
        self.createPlatform(-7, 722, -1)


        # Create letters for robot to collect
        self.letterB = '../models/letters/letter_b.egg'
        self.createLetter(self.letterB, 72, 70.2927, 0)

        self.letterR = '../models/letters/letter_r.egg'
        self.createLetter(self.letterR, 231, 227.5, 2)

        self.letterE = '../models/letters/letter_e.egg'
        self.createLetter(self.letterE, 340, 471, 3.1)

        self.letterA = '../models/letters/letter_a.egg'
        self.createLetter(self.letterA, 335, 483, 6)

        self.letterK = '../models/letters/letter_k.egg'
        self.createLetter(self.letterK, 10, 722, 0)



        # Create scientist enemy
        # enemy2 = Enemy(self.render, 16, 23, -1)


        # Create complex mesh for Track using BulletTriangleMeshShape
        mesh = BulletTriangleMesh()
        self.track = loader.loadModel("../models/mountain_valley_track.egg")
        self.track.flattenStrong()
        for geomNP in self.track.findAllMatches('**/+GeomNode'):
            geomNode = geomNP.node()
            ts = geomNP.getTransform(self.track)
            for geom in geomNode.getGeoms():
                mesh.addGeom(geom, ts)

        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        node = BulletRigidBodyNode('Track')
        node.setMass(0)
        node.addShape(shape)
        tracknn = render.attachNewNode(node)
        self.world.attachRigidBody(tracknn.node())
        tracknn.setPos(27, -5, -2)
        self.track.reparentTo(tracknn)
        debugNode = BulletDebugNode("Debug")
        debugNode.showWireframe(True)

game = level_1()
game.run()
