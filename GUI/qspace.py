#!/usr/bin/env python

import sys
import subprocess

try:
    from PyQt4 import QtCore, QtGui, uic
except ImportError:
    raise ImportError("Cannot load PyQt4")

try:
    import vtk
    from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
except ImportError:
    raise ImportError("Cannot load VTK")

try:
    import numpy as np
except ImportError:
    raise ImportError("Cannot load NumPY")


def OrbitActor(orbit):

    # create source
    points = vtk.vtkPoints()
    for line in orbit:
        points.InsertNextPoint(list(line[:3]))

    lines = vtk.vtkCellArray()
    for i in range(points.GetNumberOfPoints()-1):
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0,i)
        line.GetPointIds().SetId(1,i+1)
        lines.InsertNextCell(line)

    polygon = vtk.vtkPolyData()
    polygon.SetPoints(points)
    polygon.SetLines(lines)

    # The mapper is responsible for pushing the geometry into the graphics
    # library. It may also do color mapping, if scalars or other
    # attributes are defined.
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polygon)
    mapper.Update()

    # The actor is a grouping mechanism: besides the geometry (mapper), it
    # also has a property, transformation matrix, and/or texture map.
    # Here we set its color and rotate it -22.5 degrees.
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # color actor
    actor.GetProperty().SetColor(1,0,1)
    actor.GetProperty().SetLineWidth(4)

    return actor

class EarthActor():

    def __init__(self, ren, filename):

        #super( EarthActor, self ).__init__()

        self.ren = ren

        self.Background()
        self.Coastlines()
        self.Geographic_Lines()

    def Background(self):

        # Start with plain sphere
        # create source
        sphere = vtk.vtkSphereSource()
        sphere.SetThetaResolution(24)
        sphere.SetPhiResolution(24)
        sphere.SetCenter(0,0,0)
        sphere.SetRadius(6370)

        mapper = vtk.vtkPolyDataMapper()        
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0,0,0.5) # (R,G,B)

        self.ren.AddActor(actor)

    def Coastlines(self):

        earth = vtk.vtkAppendPolyData()

        # Add coastlines
        import shapefile
        sf = shapefile.Reader('Resources/ne_110m_coastline.shp')
 
        for shape in sf.shapes():

            points = vtk.vtkPoints()
            lines = vtk.vtkCellArray() 
            
            for p in shape.points:
                # Convert latlon to cartesian
                # Assuming earth is a sphere 
                # TODO: upgrade to WGS84 
                R = 6371
                p = np.deg2rad(p)
                x = R * np.cos(p[1]) * np.cos(p[0])
                y = R * np.cos(p[1]) * np.sin(p[0])
                z = R * np.sin(p[1])

                points.InsertNextPoint(x, y, z)

            for i in range(points.GetNumberOfPoints()-1):
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0,i)
                line.GetPointIds().SetId(1,i+1)
                lines.InsertNextCell(line)

            coast = vtk.vtkPolyData()
            coast.SetPoints(points)
            coast.SetLines(lines)

            if vtk.VTK_MAJOR_VERSION <= 5:
                earth.AddInputConnection(coast.GetProducerPort())
            else:
                earth.AddInputData(coast)

        earth.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(earth.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)

    def Geographic_Lines(self):

        earth = vtk.vtkAppendPolyData()

        # Add coastlines
        import shapefile
        sf = shapefile.Reader('Resources/ne_110m_geographic_lines.shp')
 
        for shape in sf.shapes():

            points = vtk.vtkPoints()
            lines = vtk.vtkCellArray() 
            
            for p in shape.points:
                # Convert latlon to cartesian
                # Assuming earth is a sphere 
                # TODO: upgrade to WGS84 
                R = 6371
                p = np.deg2rad(p)
                x = R * np.cos(p[1]) * np.cos(p[0])
                y = R * np.cos(p[1]) * np.sin(p[0])
                z = R * np.sin(p[1])

                points.InsertNextPoint(x, y, z)

            for i in range(points.GetNumberOfPoints()-1):
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0,i)
                line.GetPointIds().SetId(1,i+1)
                lines.InsertNextCell(line)

            coast = vtk.vtkPolyData()
            coast.SetPoints(points)
            coast.SetLines(lines)

            if vtk.VTK_MAJOR_VERSION <= 5:
                earth.AddInputConnection(coast.GetProducerPort())
            else:
                earth.AddInputData(coast)

        earth.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(earth.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)

      

class Config:
    ''' Default Config'''
    # datetime(year, month, day[, hour[, minute[, second]]])
    #start = datetime(2015, 9, 16, 17, 00, 0)
    #end   = datetime(2015, 9, 16, 18, 00, 0)
    x     = -2703.790000 
    y     =  4554.880000
    z     =  4220.740000
    vx    = -3.680000
    vy    = -5.620000
    vz    =  6.690000

class MyMainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):

        QtGui.QMainWindow.__init__(self, parent)
        uic.loadUi('qspace.ui', self)

        self.SetupVis()

        self.run_btn.clicked.connect(self.simulate_clicked)

        # Load settings if available
        #self.readSettings()

        self.config = Config()
        self.ReadConfig('simulation.cfg')
        
        # show() has to be called before vtk rendering
        self.show()

        self.iren.Initialize()
    
        print 'Lighting'
        light = vtk.vtkLight() 
        light.SetLightTypeToSceneLight();
        light.SetPositional(True)
        light.SetPosition(149600000, 0, 0)
        light.SetColor(1.0, 1.0, 0.9)
        light.SetConeAngle(180);
        light.SetFocalPoint(0, 0, 0);
        #light.SetDiffuseColor(1,0,0);
        #light.SetAmbientColor(0,1,0);
        #light.SetSpecularColor(0,0,1);

        self.ren.AddLight(light)



    def ReadConfig(self, filename):
       
        print 'Reading config'

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
                float(self.vz_edit.text()) 
                ))

    def closeEvent(self, event):

        print 'Saving config'
        self.SaveConfig('simulation.cfg')

    def closeEvent2(self, event):
        settings = QtCore.QSettings("MyCompany", "MyApp")

        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())

        print 'Good-bye'

        QtGui.QMainWindow.closeEvent(self, event)

    def readSettings(self):
        
        settings = QtCore.QSettings("MyCompany", "MyApp")

        print settings.allKeys()

        print settings.value('windowState').toByteArray()
        self.restoreGeometry(settings.value('geometry').toByteArray())
        self.restoreState(settings.value('windowState').toByteArray())

    def SetupVis(self):

        self.frame = QtGui.QFrame() 
        self.vl = QtGui.QVBoxLayout()
        
        #self.vtkWidget = MyQVTKWidget(self.frame)
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        vtk.vtkInteractorStyleTrackballActor

        self.vl.addWidget(self.vtkWidget)

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        #sat = SatelliteActor(1000)

        self.earth = EarthActor(self.ren, 'Resources/ne_110m_coastline.shp') 

        # Load the orbit
        # Load Orbit Data
        self.orbit = np.loadtxt('states.csv')
        self.orbitactor = OrbitActor(self.orbit)
        self.ren.AddActor(self.orbitactor)

        self.ren.SetBackground(0.2, 0.2, 0.2)

        # Sign up to receive TimerEvent
        #self.cb = vtkTimerCallback()
        #self.cb.actor = sat
        #self.cb.points = self.orbit[:,:3]
        #self.iren.AddObserver('TimerEvent', self.cb.execute)
        #self.timerId = self.iren.CreateRepeatingTimer(100);

        self.ren.ResetCamera()
        camera = self.ren.GetActiveCamera()
        camera.SetFocalPoint(0, 0, 0)

        # Lighting
        self.ren.AutomaticLightCreationOff()

        rwin = self.vtkWidget.GetRenderWindow()
        #rwin.LineSmoothingOn()
        #rwin.SetMultiSamples() 
        #rwin.SetAAFrames(3)
        print 'OpenglGL', rwin.SupportsOpenGL() 
        print rwin.GetMultiSamples()

        print rwin.GetAAFrames()
        print rwin.GetFDFrames()

    def simulate_clicked(self):

        self.SaveConfig('simulation.cfg')

        self.run_btn.setEnabled(False)

        # Run simulator (this blocks until complete)
        print 'Calling simulator'
        p = subprocess.Popen(['../Propogate/build/space', 'simulation.cfg', 'states.csv'], stdout=subprocess.PIPE)
        
        while True:
            line = p.stdout.readline()
            print line,

            if line.startswith('p:'):
                progress = int(float(line[2:]))
                self.progressBar.setValue(progress)
            elif line == '' and p.poll() != None:
                break
      
        self.ReloadStates()

        self.run_btn.setEnabled(True)
        self.progressBar.setValue(0)
        
        print 'Done'

    def ReloadStates(self):
        
        print('Reload States')
       
        self.orbit = np.loadtxt('states.csv')

        # create source
        points = vtk.vtkPoints()
        for line in self.orbit:
            points.InsertNextPoint(list(line[:3]))

        lines = vtk.vtkCellArray()
        for i in range(points.GetNumberOfPoints()-1):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0,i)
            line.GetPointIds().SetId(1,i+1)
            lines.InsertNextCell(line)

        polygon = self.orbitactor.GetMapper().GetInput()
        polygon.SetPoints(points)
        polygon.SetLines(lines)
        polygon.Modified()
        print 'mod'

        #self.orbitactor.GetMapper().Update()
        
        self.vtkWidget.Render()
    

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = MyMainWindow(None)

    sys.exit(app.exec_())



