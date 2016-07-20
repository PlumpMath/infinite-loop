from direct.showbase.DirectObject import DirectObject

from direct.actor.Actor import Actor

from panda3d.core import BitMask32

from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import ZUp

class Enemy(DirectObject):
    def __init__(self):

        self.enemies = []

    # Create enemy
    def createEnemy(self, render, world, x, y, z):
        h = 1.5
        w = 0.4
        shape = BulletCapsuleShape(w + 0.3, h - 2 * w, ZUp)

        self.badCharacter = BulletCharacterControllerNode(shape, 0.4, 'Scientist')
        self.badCharacterNP = render.attachNewNode(self.badCharacter)
        self.badCharacterNP.setPos(x, y, z)

        # self.badCharacterNP.setH(45)
        self.badCharacterNP.setCollideMask(BitMask32.allOn())
        world.attachCharacter(self.badCharacter)

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

        # # Add fog to enemy location
        # colour = (0.2, 0.2, 0.2)
        # fog = Fog("enemy fog")
        # fog.setColor(*colour)
        # fog.setExpDensity(0.03)
        # self.badCharacterNP.setFog(fog)
        # base.setBackgroundColor(*colour)