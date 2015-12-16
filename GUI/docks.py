#!/usr/bin/python3
# -*- coding: utf8 -*-

import sys

try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    raise ImportError("Cannot load PyQt4")

from numpy import deg2rad

import astrodynamics
from parameteredit import ParameterEdit


class OrbitParameters(QtGui.QWidget):

    def __init__(self, parent, orbit=None):

        super(OrbitParameters, self).__init__(parent)

        self.orbit = orbit

        self.params = \
            [ParameterEdit(self, 'a', 7000, 'km', 0, None, False, 500.0),
             ParameterEdit(self, 'e', 0.0, '', 0, 0.95, False, 0.01),
             ParameterEdit(self, 'i', 45, u'°', -90, 90, False, 0.5),
             ParameterEdit(self, u'Ω', 0.0, u'°', 0, 360, True, 0.5),
             ParameterEdit(self, u'ω', 0.0, u'°', -180, 180, True, 0.5),
             ParameterEdit(self, u'ν', 0.0, u'°', 0, 360, True, 0.5)]

        vbox = QtGui.QVBoxLayout()
        for param in self.params:
            vbox.addWidget(param)
            param.textChanged.connect(self.update_visualization)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def update_visualization(self, text):

        self.orbit.orbit_parameters = \
            astrodynamics.OrbitalParameters(self.params[0].value,
                                            self.params[1].value,
                                            deg2rad(self.params[2].value),
                                            deg2rad(self.params[3].value),
                                            deg2rad(self.params[4].value),
                                            deg2rad(self.params[5].value))
        self.orbit.update_data()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    w = OrbitParameters(None)
    w.show()

    sys.exit(app.exec_())
