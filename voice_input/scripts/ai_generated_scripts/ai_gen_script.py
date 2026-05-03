import FreeCAD as App
import Part
import math
doc = App.newDocument('Model')


# Create the base plate
plate = Part.makeBox(80, 40, 5)

# Calculate offset for the holes
offset = 3 * 2 + 2

# Create and cut out holes at each corner
hole1 = Part.makeCylinder(3, 5)
plate = plate.cut(hole1.translate(App.Vector(offset, offset, 0)))

hole2 = Part.makeCylinder(3, 5)
plate = plate.cut(hole2.translate(App.Vector(80 - offset, offset, 0)))

hole3 = Part.makeCylinder(3, 5)
plate = plate.cut(hole3.translate(App.Vector(offset, 40 - offset, 0)))

hole4 = Part.makeCylinder(3, 5)
plate = plate.cut(hole4.translate(App.Vector(80 - offset, 40 - offset, 0)))

final_shape = plate

feature = doc.addObject('Part::Feature', 'Shape')
feature.Shape = final_shape
doc.recompute()
feature.Shape.exportStep('/Users/enoch/Desktop/Free_Cad_Extension/voice_input/scripts/ai_generated_scripts/model.step')