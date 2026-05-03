import FreeCAD as App
import Part
import math
doc = App.newDocument('Model')


# Define dimensions
side_length = 25
wall_thickness = 2
height = 80
sphere_radius = 10

# Create outer hexagon
outer_pts = [App.Vector(side_length*math.cos(math.pi/2+2*math.pi*i/6), side_length*math.sin(math.pi/2+2*math.pi*i/6), 0) for i in range(6)]
outer_pts.append(outer_pts[0])
outer_wire = Part.Wire([Part.LineSegment(outer_pts[i], outer_pts[i+1]).toShape() for i in range(6)])
outer_face = Part.Face(outer_wire)
outer_solid = outer_face.extrude(App.Vector(0, 0, height))

# Create inner hexagon
inner_r = side_length - wall_thickness
inner_pts = [App.Vector(inner_r*math.cos(math.pi/2+2*math.pi*i/6), inner_r*math.sin(math.pi/2+2*math.pi*i/6), 0) for i in range(6)]
inner_pts.append(inner_pts[0])
inner_wire = Part.Wire([Part.LineSegment(inner_pts[i], inner_pts[i+1]).toShape() for i in range(6)])
inner_face = Part.Face(inner_wire)
inner_solid = inner_face.extrude(App.Vector(0, 0, height))

# Subtract inner solid from outer solid
hollow_hex = outer_solid.cut(inner_solid)

# Create a sphere with radius 10mm
sphere = Part.makeSphere(sphere_radius)

# Position the sphere at the center of the tube
sphere_centered = sphere.translate(App.Vector(0, 0, height/2))

# Rotate the entire assembly 30 degrees around Y-axis and then 15 degrees around X-axis
final_shape = hollow_hex.fuse(sphere_centered).rotate(App.Vector(side_length/2, side_length/2, height/2), App.Vector(0, 1, 0), 30).rotate(App.Vector(side_length/2, side_length/2, height/2), App.Vector(1, 0, 0), 15)

feature = doc.addObject('Part::Feature', 'Shape')
feature.Shape = final_shape
doc.recompute()
feature.Shape.exportStep('/Users/enoch/Desktop/Free_Cad_Extension/voice_input/scripts/ai_generated_scripts/model.step')