import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase.InputStateGlobal import inputState
from direct.actor.Actor import Actor
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib

from direct.interval.IntervalGlobal import *



from random import randint, random, uniform

from panda3d.core import Mat4
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import BitMask32
from panda3d.core import PandaNode,NodePath,TextNode
from panda3d.core import Fog

from enemy import Enemy
from player import Player

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import ZUp


# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

# Function to hold number of collectibles remaining
def addNumObj(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                          pos=(1.3, 0.95), align=TextNode.ARight, scale = .055)

class level_1(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Input
        self.accept('escape', self.doExit)
        self.accept('space', self.doJump)

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

        self.scene = []

        # Game state variables
        self.isNotWalking = False
        self.jumpingHappened = False
        self.letters = []
        self.lettersRemaining = 5
        self.health = 100
        self.enemies = []

        # Number of collectibles
        self.numObjects = addNumObj("Find letters B R E A K to escape\nLetters Remaining: " + str(self.lettersRemaining))

        # Task
        taskMgr.add(self.update, 'updateWorld')

        self.setup()
        base.disableMouse()

        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Health Bar
        self.bar = DirectWaitBar(text="H E A L T H",
                            value=100, # start with full health
                            pos=(0, .4, 0.93), # position healthbar to top center
                            scale=(1.3, 2.5, 2.5),
                            barColor = (0.97, 0, 0, 1),
                            frameSize=(-0.3, 0.3, 0, 0.025),
                            text_mayChange=1,
                            text_shadow=(0, 0, 0, 0),
                            text_fg=(0.9, 0.9, 0.9, 1),
                            text_scale=0.030,
                            text_pos=(0, 0.005, 0))
        self.bar.setBin("fixed", 0) # health bar drawn last in scene
        self.bar.setDepthWrite(False) # turns of depth writing so it doesn't interfere with itself
        self.bar.setLightOff() # fixes the color on the bar itself

    def processInput(self, dt):
        speed = Vec3(0, 0, 0)
        omega = 0.0

        # Change speed of robot
        if inputState.isSet('forward'): speed.setY( 10.0)
        if inputState.isSet('reverse'): speed.setY(-4.0)
        if inputState.isSet('left'):    speed.setX(-3.0)
        if inputState.isSet('right'):   speed.setX( 3.0)
        if inputState.isSet('turnLeft'):  omega = 120.0
        if inputState.isSet('turnRight'): omega = -120.0

        if inputState.isSet('forward') or inputState.isSet('reverse') or inputState.isSet('left') or inputState.isSet('right'):
            if self.isNotWalking is False:
                self.actorNP.loop("walk")
                self.isNotWalking = True
                # print self.characterNP.getZ()

        # if self.jumpingHappened and not self.character.isOnGround():
        #     self.jumpingHappened = False
        #     self.actorNP.loop("walk")


        else:
            if self.isNotWalking:
                self.actorNP.stop()
                self.actorNP.loop("idle")
                self.isNotWalking = False


        # if not self.character.isOnGround():
        #     print "not on ground"
        #     self.jumping = True
        #
        # if self.jumping and self.character.isOnGround():
        #     print "is on groudn and is jumping"
        #     self.jumping = False
        #     if self.isMoving:
        #         print "is on ground, is jimping, and is Moving"
        #         self.actorNP.stop()
        #         self.actorNP.loop("walk")



        self.character.setAngularMovement(omega)
        self.character.setLinearMovement(speed, True)

    def doExit(self):
        self.cleanup()
        sys.exit(1)

    def doReset(self):
        self.cleanup()
        self.setup()

    def doJump(self):
        # self.jumpingHappened = True
        self.character.setMaxJumpHeight(10.0)
        self.character.setJumpSpeed(6.0)
        self.character.doJump()
        self.actorNP.play("jump")
        self.actorNP.setPlayRate(0.8, "jump")
        self.actorNP.play("land")
        self.actorNP.setPlayRate(0.8, "land")


        # self.actorNP.enableBlend()
        # self.actorNP.setControlEffect('jump', 0.2)
        # self.actorNP.setControlEffect('land', 0.8)
        # self.actorNP.loop('jump')
        # self.actorNP.loop('land')

        # if self.isMoving is True:
        #     myActorInterval1 = self.actorNP.actorInterval("jump", loop=0)
        #     myActorInterval2 = self.actorNP.actorInterval("walk", loop=1)
        #     myActorSequence = Sequence(myActorInterval1, myActorInterval2)
        #     myActorSequence.start()

        # if self.isMoving is True:
        #     print "moving is true"
        #     self.character.setMaxJumpHeight(10.0)
        #     self.character.setJumpSpeed(6.0)
        #     self.character.doJump()
        #     self.actorNP.play("jump")
        #     self.actorNP.setPlayRate(0.8, "jump")
        #     self.actorNP.play("land")
        #     self.actorNP.setPlayRate(0.8, "land")
        #     self.actorNP.stop()
        #     self.actorNP.loop("walk")


        # else:
        #     print "moving is false"
        #     self.actorNP.stop()
        #     self.actorNP.loop("idle")


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

    # Collecting the letters
    def collectLetters(self):
        for letter in self.letters:
            contactResult = self.world.contactTestPair(self.character, letter)
            if len(contactResult.getContacts()) > 0:
                letter.removeAllChildren()
                self.world.remove(letter)
                self.letters.remove(letter)
                self.numObjects.setText("Find letters B R E A K to escape\nLetters Remaining: " + str(len(self.letters)))

    # Create enemy
    def createEnemy(self, x, y, z):
        h = 1.5
        w = 0.4
        shape = BulletCapsuleShape(w + 0.3, h - 2 * w, ZUp)

        self.badCharacter = BulletCharacterControllerNode(shape, 0.4, 'Scientist')
        self.badCharacterNP = self.render.attachNewNode(self.badCharacter)
        self.badCharacterNP.setPos(x, y, z)

        # self.badCharacterNP.setH(45)
        self.badCharacterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.badCharacter)

        # self.world.attachRigidBody(self.badCharacter.node())
        self.badActorNP = Actor('../models/lego/Scientist/Scientist.egg', {
            'walk': '../models/lego/Scientist/Scientist-walk.egg',
            'attack': '../models/lego/Scientist/Scientist-taser.egg',
            'runaway': '../models/lego/Scientist/Scientist-runaway.egg',})

        self.badActorNP.reparentTo(self.badCharacterNP)
        self.enemies.append(self.badCharacterNP)
        self.badActorNP.setScale(0.3)
        self.badActorNP.setH(180)
        self.badActorNP.setPos(0, 0, 0.5)

        #badCharacterNP.setPythonTag("actorNp", badActorNP)
        #
        #for enemies in self.enemies:
        #   badActorNp = enemy.getPythonTag("actorNp")

        # Fog
        colour = (0.2, 0.2, 0.2)
        fog = Fog("enemy fog")
        fog.setColor(*colour)
        fog.setExpDensity(0.03)
        self.badCharacterNP.setFog(fog)
        base.setBackgroundColor(*colour)

    # Enemy Logic
    def enemyAttack(self):

        for enemy in self.enemies:
            enemyProximity = enemy.getDistance(self.characterNP)

            enemyPos = self.badCharacterNP.getPos()
            characterPos = self.characterNP.getPos()
            characterPos.setZ(enemy.getZ())  # manually set the enemy's z so it doesn't fly up to match robot's z

            # vec = characterPos - enemyPos
            # vec.normalize()
            #
            # enemymovement = vec * 0.1 + enemyPos
            # self.badCharacterNP.setPos(enemymovement)

            if enemyProximity < 20 and enemyProximity > 3:
                enemy.lookAt(self.characterNP)
                # enemy.setH(60)
                enemy.node().setLinearMovement(5, True)

            if enemyProximity < 20 and enemyProximity > 3 and not self.badActorNP.getAnimControl("walk").isPlaying():
                self.badActorNP.loop("walk")

            if enemyProximity < 3 and not self.badActorNP.getAnimControl("attack").isPlaying() and not self.actorNP.getAnimControl("damage").isPlaying():
                self.badActorNP.stop()
                enemy.node().setLinearMovement(5, False)
                self.badActorNP.loop("attack")
                self.actorNP.play("damage")
                self.reduceHealth()

    # When robot comes in contact with enemy, health is reduced
    def reduceHealth(self):
        self.bar["value"] -= 3

    def update(self, task):
        dt = globalClock.getDt()
        self.processInput(dt)
        self.world.doPhysics(dt, 4, 1./240.)

        # Restart robot's position to beginning if he falls off into space
        if self.characterNP.getZ() < -10.0:
            self.characterNP.setPos(2, 0, 17.9983)

        self.collectLetters()


        # If the camera is too far from robot, move it closer.
        # If the camera is too close to robot, move it farther.
        camvec = self.characterNP.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 20.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-20))
            camdist = 20.0
        if (camdist < 10.0):
            base.camera.setPos(base.camera.getPos() - camvec*(10-camdist))
            camdist = 10.0

        self.floater.setPos(self.characterNP.getPos())
        self.floater.setZ(self.characterNP.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        # camera zooming
        base.accept('wheel_up', lambda: base.camera.setY(base.cam.getY() + 200 * globalClock.getDt()))
        base.accept('wheel_down', lambda: base.camera.setY(base.cam.getY() - 200 * globalClock.getDt()))

        mat = Mat4(camera.getMat())
        mat.invertInPlace()
        base.mouseInterfaceNode.setMat(mat)
        base.enableMouse()


        self.enemyAttack()


        if self.bar["value"] < 1:
            mainmenuTitle = OnscreenImage(image='../models/sorry.png', pos=(0, 0, 0))
            mainmenuTitle.setTransparency(TransparencyAttrib.MAlpha)

            mainmenuLoadGame = DirectButton(image='../models/retry_button.png', scale=.08, relief=None)
            mainmenuLoadGame.setTransparency(1)
            mainmenuLoadGame.resetFrameSize()
            self.doReset()

        if len(self.letters) == 0:
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

        # World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))


        # Music
        backgroundMusic = loader.loadSfx('../sounds/elfman-piano-solo.ogg')
        backgroundMusic.setLoop(True)
        backgroundMusic.play()
        # backgroundMusic.setVolume(4.0)  # will need to lower this when I add sound effects

        # Skybox
        self.skybox = loader.loadModel('../models/skybox.egg')
        # make big enough to cover whole terrain, else there'll be problems with the water reflections
        self.skybox.setScale(900)
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


        # Main Character
        h = 3.38
        w = 0.4
        shape = BulletCapsuleShape(w + 0.3, h - 2 * w, ZUp)

        self.character = BulletCharacterControllerNode(shape, 0.4, 'Robot')
        # self.character.setMass(1.0)
        self.characterNP = self.render.attachNewNode(self.character)
        self.characterNP.setPos(2, 0, 18)

        self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character)

        self.actorNP = Actor('../models/robot/lack.egg', {
                         'walk' : '../models/robot/lack-run.egg',
                         'idle' : '../models/robot/lack-idle.egg',
                         'jump' : '../models/robot/lack-jump.egg',
                         'land' : '../models/robot/lack-land.egg',
                         'damage' : '../models/robot/lack-damage.egg'})

        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.15)
        self.actorNP.setH(180)
        self.actorNP.setPos(0, 0, 0)

        # Create scientist enemy
        # enemy2 = Enemy(self.render, 16, 23, -1)

        self.createEnemy(16, 23, -1)
        self.createEnemy(10, 19, -1)

        #
        # self.createEnemy(234, 217, -1)
        # self.createEnemy(2232, 220, -1)
        # self.createEnemy(218, 221, -1)
        # self.createEnemy(220, 210, -1)
        # self.createEnemy(221, 215, -1)
        # self.createEnemy(230, 230, -1)
        #
        # self.createEnemy(4, 725, -1)
        # self.createEnemy(5, 720, -1)
        # self.createEnemy(4, 722, -1)
        # self.createEnemy(8, 680, -1)
        # self.createEnemy(20, 690, -1)
        # self.createEnemy(20, 700, -1)
        # self.createEnemy(16, 710, -1)
        # self.createEnemy(5, 730, -1)
        # self.createEnemy(5, 715, -1)
        #
        # self.createEnemy(3, 725, -1)
        # self.createEnemy(4, 720, -1)
        # self.createEnemy(8, 710, -1)
        # self.createEnemy(8, 700, -1)
        # self.createEnemy(10, 722, 0)
        # self.createEnemy(20, 700, -1)
        # self.createEnemy(16, 710, -1)
        # self.createEnemy(2, 730, -1)
        # self.createEnemy(9, 715, -1)


        # create complex shape to encompass track using BulletTriangleMeshShape
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
