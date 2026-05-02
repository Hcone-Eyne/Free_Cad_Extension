import FreeCAD as App
import Part
import math
doc = App.newDocument('Model')
final_shape = None
feature = doc.addObject('Part::Feature', 'Shape')
feature.Shape = final_shape
doc.recompute()
feature.Shape.exportStep('/Users/enoch/Desktop/Free_Cad_Extension/voice_input/scripts/ai_generated_scripts/model.step')