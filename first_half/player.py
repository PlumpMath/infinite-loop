from direct.showbase.InputStateGlobal import inputState
from direct.actor.Actor import Actor
from direct.gui.DirectGui import *

from random import randint, random, uniform

from panda3d.core import Mat4
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import BitMask32
from panda3d.core import PandaNode,NodePath,TextNode

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import ZUp
from direct.showbase.DirectObject import DirectObject


class Player(DirectObject):

    def __init__(self, render, world):

        # Input
        self.accept('space', self.doJump)

        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('turnLeft', 'a')
        inputState.watchWithModifiers('turnRight', 'd')

        self.world = world
        self.scene = []
        self.health = 100
        self.isMoving = False


        self.createPlayer(render, self.world)

    def createPlayer(self, render, world):
        # Main Character
        h = 3.38
        w = 0.4
        shape = BulletCapsuleShape(w + 0.3, h - 2 * w, ZUp)


        self.character = BulletCharacterControllerNode(shape, 0.4, 'Robot')
        # self.character.setMass(1.0)
        self.characterNP = render.attachNewNode(self.character)
        self.characterNP.setPos(2, 0, 18)

        self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        world.attachCharacter(self.character)

        self.actorNP = Actor('../models/robot/lack.egg', {
            'walk': '../models/robot/lack-run.egg',
            'idle': '../models/robot/lack-idle.egg',
            'jump': '../models/robot/lack-jump.egg',
            'land': '../models/robot/lack-land.egg',
            'damage': '../models/robot/lack-damage.egg'})

        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.15)
        self.actorNP.setH(180)
        self.actorNP.setPos(0, 0, 0)

    def processInput(self, dt):
        speed = Vec3(0, 0, 0)
        omega = 0.0

        # Change speed of robot
        if inputState.isSet('forward'): speed.setY(10.0)
        if inputState.isSet('reverse'): speed.setY(-4.0)
        if inputState.isSet('left'):    speed.setX(-3.0)
        if inputState.isSet('right'):   speed.setX(3.0)
        if inputState.isSet('turnLeft'):  omega = 120.0
        if inputState.isSet('turnRight'): omega = -120.0

        if inputState.isSet('forward') or inputState.isSet('reverse') or inputState.isSet('left') or inputState.isSet(
                'right'):
            if self.isMoving is False:
                self.actorNP.loop("walk")
                if inputState.isSet('space'):
                    print "space pressed while walking"
                self.isMoving = True
                # print self.characterNP.getZ()

        else:
            if self.isMoving:
                self.actorNP.stop()
                self.actorNP.loop("idle")
                self.isMoving = False

        self.character.setAngularMovement(omega)
        self.character.setLinearMovement(speed, True)

    def doJump(self):

        if self.isOnGround is False:
            print "IS ON GROUND IS FALSE"
            self.character.setMaxJumpHeight(10.0)
            self.character.setJumpSpeed(6.0)
            self.character.doJump()
            self.actorNP.play("jump")
            self.actorNP.setPlayRate(0.8, "jump")
            self.actorNP.play("land")
            self.actorNP.setPlayRate(0.8, "land")
            self.isOnGround = True
        else:
            if self.isOnGround:
                print "IS ON GROUND IS TRUE"
                self.actorNP.stop()
                self.actorNP.loop("walk")
                self.isOnGround = False

                # if self.isMoving is True and self.characterNP.getZ() < 2:
                #     print "ON THE GROUND"
                #     print self.characterNP.getZ()
                #     self.actorNP.play("walk")

    def backToStartPos(self):
        self.characterNP.setPos(2, 0, 17.9983)
