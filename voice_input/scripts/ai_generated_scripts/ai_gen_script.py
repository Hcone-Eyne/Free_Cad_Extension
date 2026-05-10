import FreeCAD as App
import Part
import math
doc = App.newDocument('Model')



# Create the cylinder for the hex bolt shaft
shaft_radius = 4
shaft_height = 40
shaft = Part.makeCylinder(shaft_radius, shaft_height)

# Create the HEX WIRE pattern for the head of the hex bolt
head_radius = 8
head_height = 8
n_sides = 6
hex_points = [App.Vector(head_radius * math.cos(math.pi / 2 + 2 * math.pi * i / n_sides),
                         head_radius * math.sin(math.pi / 2 + 2 * math.pi * i / n_sides),
                         0) for i in range(n_sides)]
hex_points.append(hex_points[0])
hex_wire = Part.Wire([Part.LineSegment(hex_points[i], hex_points[i+1]).toShape() for i in range(n_sides)])
head_face = Part.Face(hex_wire).extrude(App.Vector(0, 0, head_height))

# Translate the head to the correct position
head_translation = App.Placement(App.Vector(0, 0, shaft_height), App.Rotation())
head_translated = head_face.copy()
head_translated.Placement *= head_translation

# Fuse the shaft and the translated head
final_shape = shaft.fuse(head_translated)

feature = doc.addObject('Part::Feature', 'Shape')
feature.Shape = final_shape
doc.recompute()
feature.Shape.exportStep('/Users/enoch/Desktop/Free_Cad_Extension/voice_input/scripts/ai_generated_scripts/model.step')