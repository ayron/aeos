#!/usr/bin/python2
import subprocess

try:
    from PyQt4 import QtCore, QtGui, uic
except ImportError:
    raise ImportError("Cannot load PyQt4")

try:
    from pivy.gui import soqt
except ImportError:
    raise ImportError("Cannot load Pivy")

import docks
import visualization


class Config(object):
    """Default Config"""

    # datetime(year, month, day[, hour[, minute[, second]]])
    # start = datetime(2015, 9, 16, 17, 00, 0)
    # end   = datetime(2015, 9, 16, 18, 00, 0)
    x = -2703.790000
    y = 4554.880000
    z = 4220.740000
    vx = -3.680000
    vy = -5.620000
    vz = 6.690000


class MyMainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):

        QtGui.QMainWindow.__init__(self, parent)
        #uic.loadUi('qspace.ui', self)


        # self.run_btn.clicked.connect(self.simulate_clicked)

        # Load settings if available
        # self.readSettings()

        # self.config = Config()
        # self.ReadConfig('simulation.cfg')

        # Main widgets
        eci_view = visualization.EarthViewer(self)
        ecf_view = visualization.EarthViewer(self)

        # Docks
        self.setup_dock_widgets()

        # Layout
        splitter = QtGui.QSplitter(self)
        splitter.addWidget(eci_view)
        splitter.addWidget(ecf_view)

        self.setCentralWidget(splitter)

        self.show()

    def setup_dock_widgets(self):

        dock = QtGui.QDockWidget("Orbit Parameters", self)
        op_dock = docks.OrbitParameters(dock)
        dock.setWidget(op_dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

    def ReadConfig(self, filename):

        print('Reading config')

        with open(filename, 'r') as f:
            c = f.read().split()

        dt = QtCore.QDateTime()
        dt.setTime_t(int(c[0]))
        self.start_edit.setDateTime(dt)
        dt.setTime_t(int(c[1]))
        self.stop_edit.setDateTime(dt)

        self.x_edit.insert(c[2])
        self.y_edit.insert(c[3])
        self.z_edit.insert(c[4])
        self.vx_edit.insert(c[5])
        self.vy_edit.insert(c[6])
        self.vz_edit.insert(c[7])

    def SaveConfig(self, filename):

        with open(filename, 'w') as f:
            f.write('%d %d\n%f %f %f %f %f %f' % (
                self.start_edit.dateTime().toTime_t(),
                self.stop_edit.dateTime().toTime_t(),
                float(self.x_edit.text()),
                float(self.y_edit.text()),
                float(self.z_edit.text()),
                float(self.vx_edit.text()),
                float(self.vy_edit.text()),
                float(self.vz_edit.text())))

    def closeEvent(self, event):

        print('Saving config')
        # self.SaveConfig('simulation.cfg')

    def readSettings(self):

        settings = QtCore.QSettings("MyCompany", "MyApp")

        self.restoreGeometry(settings.value('geometry').toByteArray())
        self.restoreState(settings.value('windowState').toByteArray())

    def simulate_clicked(self):

        self.SaveConfig('simulation.cfg')

        self.run_btn.setEnabled(False)

        # Run simulator (this blocks until complete)
        print('Calling simulator')
        p = subprocess.Popen(['../Propogate/build/space',
                              'simulation.cfg',
                              'states.csv'],
                             stdout=subprocess.PIPE)

        while True:
            line = p.stdout.readline()
            # print(line)

            if line.startswith('p:'):
                progress = int(float(line[2:]))
                self.progressBar.setValue(progress)
            elif line == '' and p.poll() is not None:
                break

        # self.ReloadStates()

        self.run_btn.setEnabled(True)
        self.progressBar.setValue(0)

        print('Done')


if __name__ == '__main__':

    soqt.SoQt.init(None)
    window = MyMainWindow(None)
    soqt.SoQt.mainLoop()
