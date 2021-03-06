from direct.showbase.DirectObject import DirectObject

from direct.actor.Actor import Actor

from panda3d.core import BitMask32
from panda3d.core import Fog

from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import ZUp


class Enemy(DirectObject):
    def __init__(self, render, world, x, y, z, type):
        self.type = type
        h = 1.5
        w = 0.4
        shape = BulletCapsuleShape(w + 0.3, h - 2 * w, ZUp)

        self.badCharacter = BulletCharacterControllerNode(shape, 0.4, 'Lego')
        self.badCharacterNP = render.attachNewNode(self.badCharacter)
        self.badCharacterNP.setPos(x, y, z)

        self.startPositionX = self.badCharacterNP.getX()
        self.startPositionY = self.badCharacterNP.getY()
        self.startPositionZ = self.badCharacterNP.getZ()

        # self.badCharacterNP.setH(45)
        self.badCharacterNP.setCollideMask(BitMask32.allOn())
        world.attachCharacter(self.badCharacter)

        # self.world.attachRigidBody(self.badCharacter.node())
        self.badActorNP = Actor('../models/lego/' + self.type + '/' + self.type + '.egg', {
            'walk': '../models/lego/' + self.type + '/' + self.type + '-walk.egg',
            'attack': '../models/lego/' + self.type + '/' + self.type + '-attack.egg',})

        self.badActorNP.reparentTo(self.badCharacterNP)
        self.badActorNP.setScale(0.3)
        self.badActorNP.setH(180)
        self.badActorNP.setPos(0, 0, 0.5)

        # Associates badActorNP with badCharacterNP
        self.badCharacterNP.setPythonTag("badActorNP", self.badActorNP)

        # # Add fog to enemy location
        # colour = (0.2, 0.2, 0.2)
        # fog = Fog("enemy fog")
        # fog.setColor(*colour)
        # fog.setExpDensity(0.02)
        # self.badCharacterNP.setFog(fog)
        # base.setBackgroundColor(*colour)

    def backToStartPos(self):
        self.badCharacterNP.setPos(self.startPositionX, self.startPositionY, self.startPositionZ)