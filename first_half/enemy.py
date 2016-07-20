import sys

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from player import Player

from panda3d.core import BitMask32
from panda3d.core import Vec3

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import ZUp

class Enemy():
    def __init__(self, render, world, x, y, z):

        self.x = x
        self.y = y
        self.z = z
        self.enemies = []
        self.world = world

        self.enemyCreate(self.world, self.x, self.y, self.z)

    # Create enemy
    def enemyCreate(self, world, x, y, z):
        h = 1.5
        w = 0.4
        shape = BulletCapsuleShape(w + 0.3, h - 2 * w, ZUp)

        self.badCharacter = BulletCharacterControllerNode(shape, 0.4, 'Scientist') #typeOfBadGuy ex: Scientist
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

        return self.enemies



        # # Add fog to enemy location
        # colour = (0.2, 0.2, 0.2)
        # fog = Fog("enemy fog")
        # fog.setColor(*colour)
        # fog.setExpDensity(0.03)
        # self.badCharacterNP.setFog(fog)
        # base.setBackgroundColor(*colour)

    def enemyAttack(self, characterNP, actorNP, badActorNP):
        print characterNP.getPos()
        player = Player(render, world)


        for enemy in self.enemies:
            enemyProximity = enemy.getDistance(characterNP)

            characterPos = player.characterNP.getPos()
            characterPos.setZ(enemy.getZ())  # manually set the enemy's z so it doesn't fly up to match robot's z
            enemy.node().setLinearMovement(5, True)

            if enemyProximity < 20 and enemyProximity > 3:
                enemy.lookAt(player.characterNP)

            if enemyProximity < 20 and enemyProximity > 3 and not badActorNP.getAnimControl("walk").isPlaying():
                self.badActorNP.loop("walk")

            if enemyProximity < 3 and not badActorNP.getAnimControl(
                    "attack").isPlaying() and not player.actorNP.getAnimControl("damage").isPlaying():
                badActorNP.stop()
                badActorNP.loop("attack")
                player.actorNP.play("damage")
                # reduceHealth()
