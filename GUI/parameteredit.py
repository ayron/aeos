#!/usr/bin/python3
"""A modified QLineEdit for dealing with numbers."""

import sys

try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    raise ImportError("Cannot load PyQt4")


class ParameterEdit(QtGui.QLineEdit):
    """This is a special widget for numerical parameters.

    This widgets allows the user to adjust the values by
    dragging the mouse along it, as well as using the wheel.
    It is implemented using the OO state pattern.
    """

    class State(object):

        def __init__(self, parent):

            self.parent = parent

        def mouseMoveEvent(self, e):
            super(ParameterEdit, self.parent).mouseMoveEvent(e)

        def mousePressEvent(self, e):
            super(ParameterEdit, self.parent).mousePressEvent(e)

        def mouseReleaseEvent(self, e):
            super(ParameterEdit, self.parent).mouseReleaseEvent(e)

    class Normal(State):
        """THe Normal State.

        Used when the widget is not in focus.
        """

        def __init__(self, parent):

            super(parent.Normal, self).__init__(parent)

            self.parent.deselect()
            self.parent.clearFocus()

            self.parent.setReadOnly(True)
            # self.parent.selectionChanged.connect(self.parent.deselect)
            self.parent.update()

        def mousePressEvent(self, e):

            self.parent.state = self.parent.Pressed(self.parent)
            self.parent.start = e.x()
            e.accept()

    class Edit(State):

        def __init__(self, parent):

            super(parent.Edit, self).__init__(parent)
            self.parent.setReadOnly(False)
            # self.parent.selectionChanged.disconnect()
            self.parent.selectAll()
            self.parent.update()

    class Pressed(State):

        def __init__(self, parent):

            super(parent.Pressed, self).__init__(parent)

        def mouseReleaseEvent(self, e):

            self.parent.state = self.parent.Edit(self.parent)

        def mouseMoveEvent(self, e):

            self.parent.state = self.parent.Sliding(self.parent)
            self.parent.mouseMoveEvent(e)

    class Sliding(State):

        def __init__(self, parent):

            super(parent.Sliding, self).__init__(parent)

        def mouseReleaseEvent(self, e):

            self.parent.state = self.parent.Normal(self.parent)

        def mouseMoveEvent(self, e):

            scale = self.parent.increment * (e.x() - self.parent.start)
            self.parent.value = scale + self.parent.value
            self.parent.start = e.x()
            self.parent.update()

    def __init__(self, parent=None, label='label', value=0.0, units='units', min=0.0, max=1.0, cyclical=True, increment=0.05):

        super(ParameterEdit, self).__init__(parent)

        self.setValidator(QtGui.QDoubleValidator(-1e10, 1e10, 2))
        self.setAlignment(QtCore.Qt.AlignRight)

        self.setTextMargins(20, 0, 22, 0)

        self.label = label
        self.units = units
        self.min = min
        self.max = max
        self.cyclical = cyclical
        self.increment = increment
        self.value = value

        self.state = self.Normal(self)

    @property
    def value(self):
        return float(self.text())

    @value.setter
    def value(self, value):

        if self.cyclical:
            value = (value - self.min) % (self.max - self.min) + self.min
        else:
            if self.max is not None and value > self.max:
                value = self.max
            elif self.min is not None and value < self.min:
                value = self.min

        self.setText('%.2f' % value)

    def mousePressEvent(self, e):

        self.state.mousePressEvent(e)

    def mouseReleaseEvent(self, e):

        self.state.mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):

        self.state.mouseMoveEvent(e)

    def focusOutEvent(self, e):

        self.state = self.Normal(self)

    def wheelEvent(self, e):

        # Does not depend on the state
        scale = self.increment * e.delta() / 120.0
        self.value = scale + self.value
        e.accept()

    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter:
            self.state = self.Normal(self)
        else:
            super(ParameterEdit, self).keyPressEvent(e)

    def paintEvent(self, e):
        super(ParameterEdit, self).paintEvent(e)

        qp = QtGui.QPainter(self)

        qp.setPen(QtCore.Qt.white)

        bgRect = self.contentsRect()
        bgRect.adjust(5, 0, -5, 0)

        qp.drawText(bgRect,
                    QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                    self.label + ':')
        qp.drawText(bgRect,
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
                    self.units)


class Window(QtGui.QDialog):
    """Example usage of a Parameter Edit."""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        w1 = QtGui.QLineEdit()
        w2 = ParameterEdit()

        # Set UI
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(w1)
        hbox.addWidget(w2)
        hbox.addStretch(1)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    w = Window()
    w.show()

    sys.exit(app.exec_())
