import FreeCAD as App
import Part
import math
doc = App.newDocument('Model')
# Create a cube with sides of 50mm
cube = Part.makeBox(50, 50, 50)
# Define the center of the cube
center_x, center_y, center_z = 25, 25, 25
# Create a cylinder to serve as the hole
hole = Part.makeCylinder(10, 50)  # Radius is half the diameter
hole.translate(App.Vector(center_x, center_y, center_z))
# Subtract the hole from the cube
final_shape = cube.cut(hole)
feature = doc.addObject('Part::Feature', 'Shape')
feature.Shape = final_shape
doc.recompute()
feature.Shape.exportStep('/Users/enoch/Desktop/Free_Cad_Extension/voice_input/scripts/ai_generated_scripts/model.step')