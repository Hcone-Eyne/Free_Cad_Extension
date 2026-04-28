import FreeCAD as App
import Part
import math
doc = App.newDocument('Model')
# Hexagon base points
r = 10  # radius of the hexagon
pts = [App.Vector(r*math.cos(math.pi/2+2*math.pi*i/6), r*math.sin(math.pi/2+2*math.pi*i/6), 0) for i in range(6)]
pts.append(pts[0])
# Create hexagon base wire and face
wire = Part.Wire([Part.LineSegment(pts[i], pts[i+1]).toShape() for i in range(6)])
face = Part.Face(wire)
# Extrude the hexagon to create a pyramid
base_face = face.extrude(App.Vector(0, 0, 55))
# Create a triangle top for the pyramid
top_triangle = Part.makePolygon([App.Vector(-10, -10, 55), App.Vector(10, -10, 55), App.Vector(0, 10, 55), App.Vector(-10, -10, 55)])
base_face_top = base_face.fuse(top_triangle)
# Assign final_shape
final_shape = base_face_top
feature = doc.addObject('Part::Feature', 'Shape')
feature.Shape = final_shape
doc.recompute()
feature.Shape.exportStep('/Users/enoch/Desktop/Free_Cad_Extension/voice_input/scripts/ai_generated_scripts/model.step')