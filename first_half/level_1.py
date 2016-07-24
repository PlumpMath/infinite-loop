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
from panda3d.core import Point3
from panda3d.core import BitMask32
from direct.interval.IntervalGlobal import *



from enemy import Enemy
from player import Player
from movingPlatform import MovingPlatform

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import *
from panda3d.bullet import BulletDebugNode



# -------DISPLAY-------

# menu = MainMenu()
# menu.frame.show()


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
        self.accept('f3', self.toggleDebug)


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
        self.collectedLetters = []
        self.health = 100
        self.enemies = []
        self.movingPlatforms = []
        self.isTakingDamage = False
        self.start = True
        self.worldCondition = False
        self.onLevelTwo = False

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


        base.disableMouse()
        # Camera follows mouse
        # mat = Mat4(camera.getMat())
        # mat.invertInPlace()
        # base.mouseInterfaceNode.setMat(mat)
        # base.enableMouse()

        # Go through gamesetup sequence
        self.setup()

        # Add update task to task manager
        taskMgr.add(self.update, 'updateWorld')
        taskMgr.add(self.updateWinLose, 'winLose')
        taskMgr.add(self.startMenu, 'startMenu')

        # Create a floater object
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
        else:
            self.debugNP.hide()

    def doExit(self):
        render.getChildren().detach()
        sys.exit(1)

    def doRestart(self):

        self.worldCondition = True

        # Hide menu
        self.mainMenuBackground.hide()
        for b in self.buttons:
            b.hide()

        # Set player back to starting state for level 1
        self.player.startPosLevel1()
        self.bar["value"] = 100
        self.health = 100

        # Set enemies back to starting state
        for enemy in self.enemies:
            enemy.backToStartPos()

        # Set collectibles back to starting state
        for l in self.letters:
            l.removeAllChildren()
            self.world.remove(l)
        self.letters[:] = []
        self.collectedLetters[:] = []
        self.createSetOfLetters()

        self.numObjects.setText("Find letters B R E A K to escape\nLetters Remaining: " + str(len(self.letters)))

        # Set skybox to level 1 skybox
        self.skybox.removeNode()

        self.skybox = loader.loadModel('../models/skybox.egg')
        self.skybox.setScale(900) # make big enough to cover whole terrain
        self.skybox.setBin('background', 1)
        self.skybox.setDepthWrite(0)
        self.skybox.setLightOff()
        self.skybox.reparentTo(render)

        # Set music to level 1 music
        if self.backgroundMusic.play:
            self.backgroundMusic.stop()
        self.backgroundMusic = loader.loadSfx('../sounds/elfman-piano-solo.ogg')
        self.backgroundMusic.setLoop(True)
        self.backgroundMusic.play()


    def doRestartLevel2(self):
        self.onLevelTwo = True
        self.doRestart()

        # Set skybox to level 2 skybox
        self.skybox.removeNode()

        self.skybox = loader.loadModel('../models/skybox_galaxy.egg')
        self.skybox.setScale(2000)  # make big enough to cover whole terrain
        self.skybox.setBin('background', 1)
        self.skybox.setDepthWrite(0)
        self.skybox.setLightOff()
        self.skybox.reparentTo(render)

        # Set music to level 2 music
        if self.backgroundMusic.play:
            self.backgroundMusic.stop()
        self.backgroundMusic = loader.loadSfx('../sounds/irving-montage.m4a')
        self.backgroundMusic.setLoop(True)
        self.backgroundMusic.play()

        # Set player back to starting state for level 2
        self.player.startPosLevel2()


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

    def createWall(self, x, y, z, h):
        self.wall = loader.loadModel('../models/wall/wall.egg')
        geomnodes = self.wall.findAllMatches('**/+GeomNode')
        gn = geomnodes.getPath(0).node()
        geom = gn.getGeom(0)
        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        wallNode = BulletRigidBodyNode('Wall')
        wallNode.setMass(0)
        wallNode.addShape(shape)
        wallnn = render.attachNewNode(wallNode)
        wallnn.setPos(x, y, z)
        wallnn.setH(h)
        wallnn.setScale(0.5, 50.5, 19)

        self.world.attachRigidBody(wallNode)
        self.wall.reparentTo(wallnn)

    def createLetter(self, loadFile, name, x, y, z):
        self.name = name
        self.letter = loader.loadModel(loadFile)
        geomnodes = self.letter.findAllMatches('**/+GeomNode')
        gn = geomnodes.getPath(0).node()
        geom = gn.getGeom(0)
        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        self.letterNode = BulletRigidBodyNode('Letter')
        self.letterNode.setMass(0)
        self.letterNode.addShape(shape)

        self.letters.append(self.letterNode)
        letternn = render.attachNewNode(self.letterNode)
        letternn.setPos(x, y, z)
        letternn.setScale(1)
        letternn.setP(90) # orients the mesh for the letters to be upright

        self.world.attachRigidBody(self.letterNode)
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
                self.collectedLetters.append(letter)
                self.numObjects.setText("Find letters B R E A K to escape\nLetters Remaining: " + str(len(self.letters)))

    def clearRemainingLetters(self):
        letter.removeAllChildren()
        self.world.remove(letter)
        self.letters.remove(letter)

    def enemyAttackDecision(self):
        for enemy in self.enemies:
            enemyProximity = enemy.badCharacterNP.getDistance(self.player.characterNP)

            # Manually set enemy's z so it doesn't fly up to match player's z
            characterPos = self.player.characterNP.getPos()
            characterPos.setZ(enemy.badCharacterNP.getZ())

            # Create direct path from enemy to player
            enemyPos = enemy.badCharacterNP.getPos()
            vec = characterPos - enemyPos
            vec.normalize()
            enemymovement = vec * 0.15 + enemyPos

            # Make a list of all the enemies in the list except for current enemy
            self.otherEnemies = self.enemies[:]
            self.otherEnemies.remove(enemy)

            # If 2 enemies get too close to each other, send one back to their starting position
            for otherEnemy in self.otherEnemies:
                enemy2enemyProx = enemy.badCharacterNP.getDistance(otherEnemy.badCharacterNP)

                if enemy2enemyProx < 1:
                    otherEnemy.backToStartPos()

            if enemyProximity < 20 and enemyProximity > 2:
                enemy.badCharacterNP.lookAt(self.player.characterNP)
                enemy.badCharacterNP.setPos(enemymovement)

            if enemyProximity < 20 and enemyProximity > 2 and not enemy.badActorNP.getAnimControl("walk").isPlaying():
                enemy.badActorNP.loop("walk")

            if enemyProximity < 2 and not enemy.badActorNP.getAnimControl("attack").isPlaying():
                enemy.badActorNP.stop()
                enemy.badActorNP.loop("attack")

            if enemyProximity < 2 and not self.player.actorNP.getAnimControl("damage").isPlaying():
                self.player.actorNP.play("damage")
                self.isTakingDamage = True

            if self.player.character.isOnGround() and self.isTakingDamage:
                if self.player.isNotWalking and not self.player.actorNP.getAnimControl("walk").isPlaying():
                    self.player.actorNP.stop("damage")
                    self.player.actorNP.loop("walk")
                    self.player.isTakingDamage = False


            if enemyProximity < 2:
                self.reduceHealth()

    # When robot comes in contact with enemy, health is reduced
    def reduceHealth(self):
        self.bar["value"] -= 0.1

    # Menus for losing conditions
    def updateWinLose(self, task):
        if (self.bar["value"] < 1 or (len(self.letters) == 4 and len(self.collectedLetters) > 0))and self.worldCondition:
            # self.mainMenuTitle = OnscreenImage(image='../models/sorry.png', pos=(0, 0, 0))
            # self.mainMenuTitle.setTransparency(TransparencyAttrib.MAlpha)
            #
            # b = DirectButton(image='../models/retry_button.png', scale=.08, relief=None, command=self.doRestart)
            # b.setTransparency(1)
            # b.resetFrameSize()
            self.worldCondition = False
            self.backgroundMusic.stop()

            self.mainMenuBackground = OnscreenImage(image='../models/main-menu-background.png', pos=(0, 0, 0),
                                                    scale=(1.4, 1, 1))
            Button_level1 = DirectButton(text="LEVEL 1", scale=.1, pos=(-0.2, -0.2, -0.65), command=self.doRestart)
            Button_level2 = DirectButton(text="LEVEL 2", scale=.1, pos=(0.23, -0.2, -0.65), command=self.doRestartLevel2)
            Button_start = DirectButton(text="START", scale=.1, pos=(0.65, -0.2, -0.65), command=self.doRestart)
            Button_quit = DirectButton(text="QUIT", scale=.1, pos=(1, -0.2, -0.65), command=self.doExit)

            # Redetermine size or else buttons may not be clickable
            self.buttons = [Button_level1, Button_level2, Button_start, Button_quit]
            for b in self.buttons:
                b.setTransparency(1)
                b.resetFrameSize()

        return task.cont

    # Load main menu
    def startMenu(self, task):
        if self.start:
            self.mainMenuBackground = OnscreenImage(image='../models/main-menu-background.png', pos=(0, 0, 0), scale=(1.4, 1, 1))
            Button_level1 = DirectButton(text="LEVEL 1", scale=.1, pos=(-0.2, -0.2, -0.65), command=self.doRestart)
            Button_level2 = DirectButton(text="LEVEL 2", scale=.1, pos=(0.23, -0.2, -0.65), command=self.doRestartLevel2)
            Button_start = DirectButton(text="START", scale=.1, pos=(0.65, -0.2, -0.65), command=self.doRestart)
            Button_quit = DirectButton(text="QUIT", scale=.1, pos=(1, -0.2, -0.65), command=self.doExit)

            # Redetermine size or else buttons may not be clickable
            self.buttons = [Button_level1, Button_level2, Button_start, Button_quit]
            for b in self.buttons:
                b.setTransparency(1)
                b.resetFrameSize()

            return task.done
        return task.cont

    def createEnemies(self):
        # Level 1 Security guards
        self.enemies.append(Enemy(render, self.world, 65, 68, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 69, 64, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 78, 72, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 204.968, 212.61, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 209.655, 203.636, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 217.109, 212.297, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 223.065, 220.857, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 6235.36, 222.674, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 7236.321, 231.365, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 332.143, 455.849, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 323.669, 460.24, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 329.634, 468.654, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 200.354, 710.706, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 209.07, 704.83, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 7212.075, 715.181, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 212.038, 724.852, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 203.831, 724.983, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 202.971, 734.249, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 6211.922, 735.278, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 191.579, 727.393, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 190.676, 735.513, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 180.853, 735.058, -1, "SecurityGuard"))
        # self.enemies.append(Enemy(render, self.world, 6181.708, 726.1, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 187.881, 717.305, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 177.801, 714.21, -1, "SecurityGuard"))
        self.enemies.append(Enemy(render, self.world, 180.247, 706.548, -1, "SecurityGuard"))

        # Level 2 Enemies (Mixed bag)
        self.enemies.append(Enemy(render, self.world, -220.549, 427.425, -1, "Scientist"))
        # self.enemies.append(Enemy(render, self.world, -223.242, 415.591, -1, "Brawler"))
        # self.enemies.append(Enemy(render, self.world, -211.013, 417.047, -1, "Voltage"))
        self.enemies.append(Enemy(render, self.world, -244.055, 304.031, -1, "Cinder"))
        # self.enemies.append(Enemy(render, self.world, -250.473, 294.736, -1, "Shield"))
        # self.enemies.append(Enemy(render, self.world, -247.543, 285.703, -1, "Wraith"))
        self.enemies.append(Enemy(render, self.world, -234.8, 285.066, -1, "Scientist"))
        self.enemies.append(Enemy(render, self.world, -214.313, 77.9221, -1, "Brawler"))
        self.enemies.append(Enemy(render, self.world, -210.797, 63.8862, -1, "Voltage"))
        self.enemies.append(Enemy(render, self.world, -206.397, 68.8532, -1, "Cinder"))
        self.enemies.append(Enemy(render, self.world, -212.291, 19.0834, -1, "Bricker"))
        # self.enemies.append(Enemy(render, self.world, -237.824, -162.731, -1, "Wraith"))
        self.enemies.append(Enemy(render, self.world, -226.271, -170.715, -1, "Scientist"))
        self.enemies.append(Enemy(render, self.world, -231.582, -171.925, -1, "Brawler"))
        self.enemies.append(Enemy(render, self.world, -236.969, -178.02, -1, "Shield"))




    def createSetOfLetters(self):
        self.letterB = '../models/letters/letter_b.egg'
        self.letterR = '../models/letters/letter_r.egg'
        self.letterE = '../models/letters/letter_e.egg'
        self.letterA = '../models/letters/letter_a.egg'
        self.letterK = '../models/letters/letter_k.egg'

        if self.onLevelTwo:
            self.createLetter(self.letterB, "B", -220, 417, 16)
            self.createLetter(self.letterR, "R", -251, 288, 20)
            self.createLetter(self.letterE, "E", -201.7, 53, 33)
            self.createLetter(self.letterA, "A", -206, 41, 25)
            self.createLetter(self.letterK, "K", -232, -174, 16)

        else:
            self.createLetter(self.letterB, "B", 72, 70.2927, 0)
            self.createLetter(self.letterR, "R", 225, 223, 2)
            self.createLetter(self.letterE, "E", 340, 471, 3.1)
            self.createLetter(self.letterA, "A", 335, 483, 6)
            self.createLetter(self.letterK, "K", 197, 721, 0)

    def createMovingPlatforms(self):

        # Platforms to collect B
        self.movingPlatforms.append(MovingPlatform(render, self.world, -220, 417, -2.2))

        # Platforms to collect R
        self.movingPlatforms.append(MovingPlatform(render, self.world, -240, 288, -2.2))
        self.movingPlatforms.append(MovingPlatform(render, self.world, -251, 288, 3.2))

        # Platforms to collect E and A
        self.movingPlatforms.append(MovingPlatform(render, self.world, -214, 72, -2.2))
        self.movingPlatforms.append(MovingPlatform(render, self.world, -203, 72, 4.2))
        self.movingPlatforms.append(MovingPlatform(render, self.world, -202, 53, 16.2))
        self.movingPlatforms.append(MovingPlatform(render, self.world, -207, 40.5, 7.2))

        # Platform to collect K
        self.movingPlatforms.append(MovingPlatform(render, self.world, -232, -174, -2.2))

    def update(self, task):

        # if base.mouseWatcherNode.hasMouse():
        #     x = base.mouseWatcherNode.getMouseX()
        #     print ("mouse X: ", x)
        #     y = base.mouseWatcherNode.getMouseY()
        #     print ("mouse Y: ", y)

        print self.player.characterNP.getPos()

        dt = globalClock.getDt()
        self.player.processInput(dt)
        self.world.doPhysics(dt, 4, 1./240.)

        # Call camera function in player class
        self.player.cameraFollow(self.floater)


        # Identifying player collecting items
        self.collectLetters()

        # Start from beginning position if player falls off track
        if self.player.characterNP.getZ() < -10.0:
            if self.onLevelTwo:
                self.player.startPosLevel2()
            else:
                self.player.startPosLevel1()

        # If player gets too close to enemy, enemy attacks
        self.enemyAttackDecision()

        return task.cont

    def setup(self):

        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        # Physics World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        # Main Character
        self.player = Player()
        self.player.createPlayer(render, self.world)

        # Enemies
        if self.enemies > 0:
            del self.enemies[:]
        self.createEnemies()

        # Music
        self.backgroundMusic = loader.loadSfx('../sounds/elfman-piano-solo.ogg')
        self.backgroundMusic.setLoop(True)
        self.backgroundMusic.stop()
        # backgroundMusic.setVolume(4.0)  # will need to lower this when I add sound effects

        # Level 1 Skybox
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
        genfog.setExpDensity(0.003)
        render.setFog(genfog)
        base.setBackgroundColor(*colour)

        # Create wall (x, y, z, h)
        self.createWall(-30.2215, -6.2, -2, 45)
        self.createWall(-203, 555.8, -2, 70)

        # Create letters for robot to collect
        self.createSetOfLetters()

        #-----Level 1 Platforms-----
        # Platform to collect B
        self.createPlatform(72, 70.2927, -1)

        # Platforms to collect R
        self.createPlatform(211, 210, -1)
        self.createPlatform(225, 223, 1)

        # Platforms to collect E and A
        self.createPlatform(330, 462, -0.4)
        self.createPlatform(340, 471, 2.1)
        self.createPlatform(350, 480, 4)
        self.createPlatform(335, 483, 5)

        # Platforms to collect K
        self.createPlatform(184, 712, -1)
        self.createPlatform(208, 730, -1)
        self.createPlatform(207, 711, -1)
        self.createPlatform(186, 731, -1)

        #-----Level 2 Platforms-----
        # Moving platforms
        if self.movingPlatforms > 0:
            del self.movingPlatforms[:]
        self.createMovingPlatforms()

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

game = level_1()
game.run()