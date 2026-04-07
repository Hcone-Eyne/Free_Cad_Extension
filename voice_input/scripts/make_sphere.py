''' this code is used to create sphere'''
# appending FreeCAD's terminal/tools / library
import sys
sys.path.append("/Applications/FreeCAD.app/Contents/Resources/lib")

#importing nessary modules
import FreeCAD # type: ignore
import Part # type: ignore

# 1. creating document
doc = FreeCAD.newDocument("Version 1")

# 2. create shape od sphere
sphere = Part.makeSphere(20)

# 3. add shape to the document
part = doc.addObject("Part::Feature","Version 1")
part.Shape = sphere

# 4. save it in .step extension
output_path = "/Users/enoch/Desktop/Free_Cad_Extension/voice_input/output/sphere.step"
part.Shape.exportStep(output_path)

print("Sucess!, Saved to",output_path)