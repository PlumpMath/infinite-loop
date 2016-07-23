from direct.showbase.DirectObject import DirectObject

from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletRigidBodyNode
from direct.interval.IntervalGlobal import *
from panda3d.core import Point3



class MovingPlatform(DirectObject):
    def __init__(self, render, world, x, y, z):

        self.movingPlatform = loader.loadModel('../models/square-flat/square.egg')
        geomnodes = self.movingPlatform.findAllMatches('**/+GeomNode')
        gn = geomnodes.getPath(0).node()
        geom = gn.getGeom(0)
        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)

        self.node = BulletRigidBodyNode('MovingPlatform')
        self.node.setMass(0)
        self.node.addShape(shape)
        self.movingPlatformnn = render.attachNewNode(self.node)
        self.movingPlatformnn.setPos(x, y, z)

        # # Store platform positions
        # self.startPositionX = self.movingPlatformnn.getX()
        # self.startPositionY = self.movingPlatformnn.getY()
        # self.startPositionZ = self.movingPlatformnn.getZ()

        self.movingPlatformnn.setScale(9, 7, 0.5)
        world.attachRigidBody(self.node)
        self.movingPlatform.reparentTo(self.movingPlatformnn)

        # Associates movingPlatformnn with movingPlatform
        self.movingPlatformnn.setPythonTag("movingPlatformNP", self.movingPlatform)

        # Create and play the sequence of intervals
        downInterval = self.movingPlatformnn.posInterval(3, Point3(x, y, z), startPos=Point3(x, y, z + 15))
        upInterval = self.movingPlatformnn.posInterval(3, Point3(x, y, z + 15), startPos=Point3(x, y, z))

        elevateParallel = Parallel()
        elevate = Sequence(downInterval, upInterval, name="elevate")
        elevateParallel.append(elevate)

        elevateParallel.loop()