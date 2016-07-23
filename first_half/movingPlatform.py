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

        self.movingPlatformnn.setScale(9, 7, 0.5)
        world.attachRigidBody(self.node)
        self.movingPlatform.reparentTo(self.movingPlatformnn)

        # Associates movingPlatformnn with movingPlatform
        self.movingPlatformnn.setPythonTag("movingPlatformNP", self.movingPlatform)

        # Create a sequence of intervals and play them together using parallel
        downInterval = self.movingPlatformnn.posInterval(3, Point3(x, y, z), startPos=Point3(x, y, z + 15))
        upInterval = self.movingPlatformnn.posInterval(3, Point3(x, y, z + 15), startPos=Point3(x, y, z))

        # To randomize a little, take x position of platform. If it's even move downward. If it's odd, upward
        if x % 2 == 0:
            elevate = Sequence(downInterval, upInterval, name="elevate")
        else:
            elevate = Sequence(upInterval, downInterval, name="elevateOpposite")

        elevateParallel = Parallel()
        elevateParallel.append(elevate)
        elevateParallel.loop()