'''
A port of the Explode Geometry .NET plug-in on the ADN-DevTech GitHub:
https://github.com/ADN-DevTech/3dsMax-Explode-Geometry
This example illustrates using PySide2 in Max, and working with TriObject and Mesh objects
'''

from PySide2 import QtWidgets
import MaxPlus

# Protect our Qt widgets from being garbage collected:
class _GCProtector(object):
    widgets = []
    
    

def convert_to_triangle_faces(node, addShell, shell_amount, addEditMesh, collapseNode,centerPivot):
    # convert to a mesh geometry, then use EvalWOrldState() to get an instance of the object
    node.Convert(MaxPlus.ClassIds.TriMeshGeometry)
    object_state = node.EvalWorldState()
    obj_original = object_state.Getobj()
    # print "o: %s" % obj_original
    
    # is this a TriObject already?
    if not obj_original.IsSubClassOf(MaxPlus.ClassIds.TriMeshGeometry):
        # find a way to convert it anyway?
        pass
       
    # save node settings to apply later:
    mat = node.GetLocalTM()
    offset_pos = node.GetObjOffsetPosition()
    offset_rot = node.GetObjOffsetRotation()
    offset_scale = node.GetObjOffsetScale() 
    
    # cast to TriObject object and get the mesh so we can work with it
    tri_obj = MaxPlus.TriObject._CastFrom(obj_original)    
    tri_mesh = tri_obj.GetMesh()
    
    # create a new TriObject for each new face, and set it up:
    for face in tri_mesh.Faces:
        
        new_face = MaxPlus.Factory.CreateNewTriObject()
        n = MaxPlus.Factory.CreateNode(new_face)
        mesh = new_face.GetMesh()
        mesh.SetNumFaces(1)
        mesh.SetNumVerts(3)
        mesh.GetFace(0).SetVerts(0,1,2)        
        mesh.GetFace(0).SetEdgeVisFlags(1,1,1)
        mesh.GetFace(0).SetSmGroup(2)

        # now for each vertex, get the old face's points and store into new
        for i in range (0,3):
            pt = tri_mesh.GetVertex(face.GetVert(i))
            mesh.SetVert(i,pt)
        
        # force re-draw
        mesh.InvalidateGeomCache()       
        
            # add shell modifier
        if addShell:
            mod = MaxPlus.Factory.CreateObjectModifier(MaxPlus.ClassIds.Shell)
            mod.ParameterBlock.outerAmount.Value = shell_amount
            n.AddModifier(mod)

            # add edit mesh modifier
        if addEditMesh:
            mod = MaxPlus.Factory.CreateObjectModifier(MaxPlus.ClassIds.Edit_Mesh)
            n.AddModifier(mod)

            # collapse the node
        if collapseNode:
            n.Collapse(True)

            # update node to match object being exploded:
            n.SetLocalTM(mat)
            n.SetObjOffsetPosition(offset_pos)
            n.SetObjOffsetRotation(offset_rot)
            n.SetObjOffsetScale(offset_scale)

            if centerPivot:
                t = MaxPlus.Core.GetCurrentTime()
                n.CenterPivot(t, False)
                n.AlignPivot(t, False)
    

app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication([])


''' Form class that allows the user to select options for the script
'''
class Form(QtWidgets.QDialog):
    def __init__(self, parent=MaxPlus.GetQMaxMainWindow()):
        super (Form,self).__init__(parent)        

        self.resize(250, 300)
        self.setWindowTitle('Window')
        _GCProtector.widgets.append(self)
        
    
        main_layout = QtWidgets.QVBoxLayout()
        # Explode operations
        # PolyObject not yet supported in Python:
        '''
        groupbox1 = QtWidgets.QGroupBox("Explode Operations")
        radio1 = QtWidgets.QRadioButton("&Explode to Polygons")
        radio2 = QtWidgets.QRadioButton("Explode to Triangles")
        radio2.setChecked(True)
        
        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(radio1)
        vbox1.addWidget(radio2)
        groupbox1.setLayout(vbox1)
        
        main_layout.addWidget(groupbox1)
        '''

        #Explode options
        groupbox2 = QtWidgets.QGroupBox("Explode Options")
        self.checkbox1 = QtWidgets.QCheckBox("Add Shell Modifier")
        self.checkbox2 = QtWidgets.QCheckBox("Add Edit Mesh Modifier")
        self.checkbox3 = QtWidgets.QCheckBox("Collapse Modifier Stack")
        self.checkbox4 = QtWidgets.QCheckBox("Center Pivot")
        self.checkbox5 = QtWidgets.QCheckBox("Delete Original")
        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(self.checkbox1)
        vbox2.addWidget(self.checkbox2)
        vbox2.addWidget(self.checkbox3)
        vbox2.addWidget(self.checkbox4)
        vbox2.addWidget(self.checkbox5)
        
        label1 = QtWidgets.QLabel("Shell Offset:")
        self.spin1 = QtWidgets.QDoubleSpinBox()
        self.spin1.setMinimum(0.1)
        self.spin1.setSingleStep(0.1)
        self.spin1.setValue(0.1)
        vbox2.addWidget(label1)
        vbox2.addWidget(self.spin1)
        
        groupbox2.setLayout(vbox2)    
        main_layout.addWidget(groupbox2)        
        
        label = QtWidgets.QLabel("Explode Selected Objects")
        main_layout.addWidget(label)
    
        btn = QtWidgets.QPushButton("Explode")
        main_layout.addWidget(btn)
        self.setLayout(main_layout)
    
        btn.clicked.connect(self.do_explode)
        
    # Gather the settings from the form, and call convert_to_triangle_faces
    def do_explode(self):   
        # get values from window
        addShell = self.checkbox1.isChecked()
        shell_amount = self.spin1.value
        addEditMesh = self.checkbox2.isChecked()        
        collapseNode = self.checkbox3.isChecked()
        centerPivot = self.checkbox4.isChecked()
        deleteOriginal = self.checkbox5.isChecked()
        
        # iterate through the selected nodes
        if MaxPlus.SelectionManager.GetCount() <=0:
            msg = "Nothing selected. Please select a node to explode."
            print msg
            self.show_alert(msg)
        else:
            for n in MaxPlus.SelectionManager.Nodes:
                print "node name: %s" % n.Name
                convert_to_triangle_faces(n, addShell, shell_amount,
                                          addEditMesh, collapseNode,
                                          centerPivot)
            
                if deleteOriginal:
                    n.Delete()
        
            # close the dialog
            self.close()
        
    # alert dialog 
    def show_alert(self, message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(message)
        msgBox.exec_()
        
    
def main():        
    #MaxPlus.FileManager.Reset(True)
    form = Form()
    #form.setParent(MaxPlus.GetQMaxWindow())
    #MaxPlus.MakeQWidgetDockable(form,4)
    form.show()   

    
    
if __name__ == '__main__':
    main()
