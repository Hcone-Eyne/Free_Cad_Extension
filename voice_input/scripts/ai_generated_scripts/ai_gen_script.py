import FreeCAD as App
from pathlib import Path

doc = App.newDocument()

box = doc.addObject("Part::Box", "Box")
box.Length = 50
box.Width = 20
box.Height = 10

cyl = doc.addObject("Part::Cylinder", "Hole")
cyl.Radius = 2.5
cyl.Height = 15
cyl.Placement = App.Placement(App.Vector(25, 10, 5), App.Rotation())

cut = doc.addObject("Part::Cut", "Cut")
cut.Base = box
cut.Tool = cyl

doc.recompute()

step_path = "voice_input/ai_generated_scripts.step"
dir_path = "voice_input/ai_generated_scripts"
import os
os.makedirs(dir_path, exist_ok=True)
cut.Shape.exportStep(step_path)