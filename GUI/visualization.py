#!/usr/bin/python2
"""Classes for 3d visualization of the orbit.
"""

import sys

try:
    from PyQt4 import QtGui
except ImportError:
    raise ImportError("Cannot load PyQt4")

try:
    from pivy import coin
    from pivy.gui import soqt
except ImportError:
    raise ImportError("Cannot load Pivy")

try:
    import numpy as np
except ImportError:
    raise ImportError("Cannot load NumPY")


class EarthViewer(QtGui.QWidget):

    def __init__(self, parent=None):

        super(EarthViewer, self).__init__(parent)

        earth = self.load_file('Resources/myearth.iv')

        root = coin.SoSeparator()
        root.addChild(earth)

        self.viewer = soqt.SoQtExaminerViewer(self)
        self.viewer.setSceneGraph(root)
        self.viewer.setTitle("Earth Viewer")
        self.viewer.setDecoration(False)
        self.viewer.toggleCameraType()
        self.viewer.show()

    def load_file(self, filename):

        # Open the input file
        input = coin.SoInput()
        if not input.openFile(filename):
            print >> sys.stderr, "Cannot open file %s" % (filename)
            return None

        # Read the whole file into the database
        graph = coin.SoDB.readAll(input)
        if graph is None:
            print >> sys.stderr, "Problem reading file"
            return None

        input.closeFile()
        return graph


if __name__ == '__main__':
    # Example Usage

    soqt.SoQt.init(None)
    vp = EarthViewer()
    soqt.SoQt.mainLoop()
