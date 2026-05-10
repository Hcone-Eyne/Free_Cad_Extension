
''' the translator between ai and source code
it takes stage manager's memory and voice / text and gives to api (ai) to get a perfect result '''

# importing nessary modules
from voice_input import stage_manager
import os
import requests
from pathlib import Path
from dotenv import load_dotenv # type: ignore
from voice_input.Keys.config import ai_gen_script, output_location, ai_gen_folder


# transition to external api to hardware run
import ollama # type:ignore
from voice_input.stage_manager import get_memory

# saftey net import module
import re

# loading environment variables
load_dotenv()
api_key = os.getenv("api_key")

# create function to send prompt to ai i call it "The Translator"
def translator(user_request):
    # get memorry from stage manager
    previous_memory = stage_manager.get_memory()

    # create system instruction
    # changed from {} to () 
    # {} must have keys and values
    # we are grouping system rules in ()
    system_rule = (f"""You are a FreeCAD Python scripting expert.
Return ONLY raw executable Python code. No markdown. No backticks. No comments. No print(). One statement per line.
 
=== REQUIRED HEADER (always first 4 lines) ===
import FreeCAD as App
import Part
import math
doc = App.newDocument('Model')
 
=== REQUIRED FOOTER (always last 4 lines) ===
feature = doc.addObject('Part::Feature', 'Shape')
feature.Shape = final_shape
doc.recompute()
feature.Shape.exportStep('{ai_gen_folder}/model.step')
 
=== PRIMITIVES ===
Part.makeBox(L, W, H)                          # corner at origin
Part.makeCylinder(R, H)                        # along Z-axis by default
Part.makeSphere(R)
Part.makeCone(R1, R2, H)
Part.makeTorus(R_major, R_tube)
 
=== TRANSFORMS ===
shape.translate(App.Vector(x, y, z))
shape.rotate(App.Vector(0,0,0), App.Vector(ax,ay,az), angle_deg)
App.Placement(App.Vector(x,y,z), App.Rotation(App.Vector(ax,ay,az), angle_deg))
 
=== BOOLEANS ===
final_shape = a.fuse(b).fuse(c)                # always chain, never leave floating parts
final_shape = base.cut(h1).cut(h2)             # chain cuts the same way
common = a.common(b)
 
=== CENTERING FORMULAS ===
# Box center:            (L/2, W/2, H/2)
# Hole center in box:    translate hole to (L/2, W/2, 0) before cut
# Corner hole offsets:   offset = R_hole*2 + 2   ->  (offset, offset), (L-offset, offset), (offset, W-offset), (L-offset, W-offset)
# Fuselage (horizontal): makeCylinder then rotate 90° around Y-axis
 
=== ALIGNMENT RULES ===
- Fuse parts touch if bounding boxes overlap by >= 0.1 mm
- Default: align secondary part centers to main body center (Y=0)
- Use unique descriptive names per part (fuselage, left_wing, right_wing, etc.)
 
=== PATTERNS ===
 
# Hex prism (side length r, height h):
pts = [App.Vector(r*math.cos(math.pi/2 + 2*math.pi*i/6), r*math.sin(math.pi/2 + 2*math.pi*i/6), 0) for i in range(6)]
pts.append(pts[0])
wire = Part.Wire([Part.LineSegment(pts[i], pts[i+1]).toShape() for i in range(6)])
solid = Part.Face(wire).extrude(App.Vector(0, 0, h))
 
# Hollow hex tube (wall thickness t):
inner_r = r - t
# (repeat hex prism above for outer_solid and inner_solid, then:)
hollow_hex = outer_solid.cut(inner_solid)
 
# Polar array (n copies around Z):
copies = [shape.copy() for i in range(n)]
for i, c in enumerate(copies): c.rotate(App.Vector(0,0,0), App.Vector(0,0,1), i * 360/n)
result = Part.makeCompound(copies)
 
# Linear array (n copies along X, spacing s):
copies = [shape.copy() for i in range(n)]
for i, c in enumerate(copies): c.translate(App.Vector(i*s, 0, 0))
result = Part.makeCompound(copies)
 
# Sweep (circle profile, straight path, length L):
profile = Part.Wire(Part.makeCircle(R, App.Vector(0,0,0), App.Vector(0,0,1)))
path    = Part.Wire([Part.LineSegment(App.Vector(0,0,0), App.Vector(0,0,L)).toShape()])
result  = path.makePipeShell([profile], True, False)
 
# Loft (circle r1 at z=0, circle r2 at z=H):
w1 = Part.Wire(Part.makeCircle(r1, App.Vector(0,0,0), App.Vector(0,0,1)))
w2 = Part.Wire(Part.makeCircle(r2, App.Vector(0,0,H), App.Vector(0,0,1)))
result = Part.makeLoft([w1, w2], True)
 
# Fillet / Chamfer:
shape.makeFillet(radius, shape.Edges)
shape.makeChamfer(size, shape.Edges)
 
# Mirror:
shape.mirror(App.Vector(0,0,0), App.Vector(1,0,0))
 
=== HARD RULES ===
- NEVER skip doc = App.newDocument('Model')
- NEVER use math functions unless geometry explicitly requires it (e.g. hex angles)
- NEVER use Part.makeCompound for assemblies that must be one solid — use .fuse() chain
- NEVER call addObject() on a shape; only on doc
- NEVER use App.ActiveDocument.removeObject()
- COUNTING: generate EXACTLY N sides when asked. Hexagon = range(6). No substitutions.
- Re-create all previous context objects before adding new ones
- final_shape MUST be assigned before the footer
"""
    )

    # adding code validator / auto fixer
    def validator(code):
        # functional footer checks
        if "App.newDocument" not in code:
            code = code.replace("import math","import math\n\ndoc=App.newDocument('Model')")
        if "doc.addObject" not in code:
            code += "\nfeature = doc.addObject('Part::Feature', 'Shape')"
        if "feature.Shape = final_shape" not in code:
            code += "\nfeature.Shape = final_shape"
        if "doc.recompute" not in code:
            code += "\ndoc.recompute()"
        if "exportStep" not in code:
            code += f"\nfeature.Shape.exportStep('{ai_gen_folder}/model.step')"            
        # variable checker
        if "final_shape" not in code:
            raise Exception("Ai Forgots to define final_shape")

        return code

    
    # send prompt to ai via ollama (local LLM)
    # sending it to reasoning model currently "phi4-mini" is the model for reasoning

    # using qwen2.5 coder model to generate python script based on the plan 
    print("Builder Model Active...")
    print(f"[Qwen 2.5]: Generating Code...")
    response = ollama.chat(model="qwen2.5-coder:7b", messages=[
        {"role":"system", 
        "content":system_rule
        },
        {"role":"user",
        "content":f"Existing Geometry Plan:\n{previous_memory}\n\nUpdate to apply:{user_request}"
        }
    ])
    print("\n[Builder Model]: Code Generated.")
    
    
    # 1.extract content from ollama
    raw_code = response.message.content

    # 2.clean python code (removing fen fencess such as '''python and '')
    clean_code = raw_code.replace("```python", "").replace("```py", "").replace("```", "").strip()

    # 3.split safety net and join statement onto seperate lines
    clean_code = re.sub(r';\s*', '\n', clean_code)

    # 4. saftey net injection
    # injects header if only missing
    print("injecting header (force)")
    ai_lines = clean_code.splitlines()
    body_code = [
        l for l in ai_lines
        if not any(x in l for x in ["import FreeCAD", "import Part", "import math", "App.newDocument","setActiveDocument"])
    ]
    # adding header
    header = (
        "import FreeCAD as App\n"
        "import Part\n"
        "import math\n"
        "doc = App.newDocument('Model')\n\n"
        )

    final_code = header + "\n".join(body_code)

    # validation phase (valaditing all of the code fairness)
    try:
        final_executable_code = validator(final_code)
    except Exception as e:
        print(f"Validation Error: {e}")
        return None

    # start saving the file

    # 5.save generated python script from runner.py
    file_name = "ai_gen_script.py"
    with open(ai_gen_script, "w") as file:
        file.write(final_executable_code)
    print(f"Script of ai generated Saved\n Location:{ai_gen_script}")
    print("Qwen 2.5 successfully runned")

    # returning the script
    return file_name
