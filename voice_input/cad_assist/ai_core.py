
''' the translator between ai and source code
it takes stage manager's memory and voice / text and gives to api (ai) to get a perfect result '''

# importing nessary modules
from voice_input import stage_manager
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from voice_input.Keys.config import ai_gen_script, output_location, ai_gen_folder


# transition to external api to hardware run
import ollama
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
    system_rule =( f"""You are a FreeCAD Python scripting expert.
        Return ONLY raw executable Python code. No markdown. No backticks. No comments. No print().
        One statement per line. Never two statements on one line.

        ALWAYS start every script with these exact four lines:
        import FreeCAD as App
        import Part
        import math
        doc = App.newDocument('Model')

        NEVER skip doc = App.newDocument('Model'). Without it the script crashes with: name 'doc' is not defined.

        ALWAYS end every script with these exact four lines:
        feature = doc.addObject('Part::Feature', 'Shape')
        feature.Shape = final_shape
        doc.recompute()
        feature.Shape.exportStep('{ai_gen_folder}/model.step')
        
        PRIMITIVES:
        Part.makeBox(length, width, height)
        Part.makeCylinder(radius, height)
        Part.makeSphere(radius)
        Part.makeCone(radius1, radius2, height)
        Part.makeTorus(major_radius, tube_radius)
        
        BOOLEAN:  shape1.fuse(shape2) | shape1.cut(shape2) | shape1.common(shape2)
        MOVE:     shape.translate(App.Vector(x, y, z))
        ROTATE:   shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_degrees)
        FILLET:   shape.makeFillet(radius, shape.Edges)
        CHAMFER:  shape.makeChamfer(size, shape.Edges)
        EXTRUDE:  face.extrude(App.Vector(0, 0, height))
        REVOLVE:  face.revolve(App.Vector(0,0,0), App.Vector(0,0,1), 360)
        MIRROR:   shape.mirror(App.Vector(0,0,0), App.Vector(1,0,0))
        COMPOUND: Part.makeCompound([shape1, shape2, shape3])
        
        HEX WIRE (bolts, nuts, hex prisms):
        pts = [App.Vector(r*math.cos(math.pi/2+2*math.pi*i/6), r*math.sin(math.pi/2+2*math.pi*i/6), 0) for i in range(6)]
        pts.append(pts[0])
        wire = Part.Wire([Part.LineSegment(pts[i], pts[i+1]).toShape() for i in range(6)])
        face = Part.Face(wire)
        solid = face.extrude(App.Vector(0, 0, height))
        
        POLAR ARRAY (n copies around Z):
        copies = [shape.copy() for i in range(n)]
        for i, c in enumerate(copies):
            c.rotate(App.Vector(0,0,0), App.Vector(0,0,1), i * 360/n)
        result = Part.makeCompound(copies)
        
        LINEAR ARRAY (n copies along X):
        copies = [shape.copy() for i in range(n)]
        for i, c in enumerate(copies):
            c.translate(App.Vector(i * spacing, 0, 0))
        result = Part.makeCompound(copies)
        
        SWEEP (pipe along path):
        profile_wire = Part.Wire(Part.makeCircle(radius, App.Vector(0,0,0), App.Vector(0,0,1)))
        path_wire = Part.Wire([Part.LineSegment(App.Vector(0,0,0), App.Vector(0,0,length)).toShape()])
        result = path_wire.makePipeShell([profile_wire], True, False)
        
        LOFT (blend between two profiles):
        wire1 = Part.Wire(Part.makeCircle(r1, App.Vector(0,0,0), App.Vector(0,0,1)))
        wire2 = Part.Wire(Part.makeCircle(r2, App.Vector(0,0,height), App.Vector(0,0,1)))
        result = Part.makeLoft([wire1, wire2], True)
        
        RULES:
        Only call doc.addObject(). Never addObject() on a shape.
        Never use App.ActiveDocument.removeObject().
        Re-create all previous context objects before adding new ones.
        If unclear, make a reasonable default shape.
        NEVER skip doc = App.newDocument('Model').

        NOTE:
        The final geometry resulting from all operations MUST be assigned to the variable final_shape before the closing lines.
        Review the 'Previous Context' provided. You must re-generate the Python code for all previous objects to maintain the model state, then apply the 'New Request' to those objects.
        Part.makeBox starts at (0,0,0). To center a hole in a box of size L,W,H, the center coordinate is (L/2,W/2,H/2)

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

    
    # send prompt to ai
    prompt = f"\n Current Request:{user_request}"
    print("qwen2.5 is thinking...")
    # unknown / sending request to ai
    headers = {
        "Authorization" : f"Bearer {api_key}",
        # no "." use slash instead for better navigation through file/folders
        "Content-Type":"application/json"
    }

    data = {
        "model":"qwen2.5-coder:7b",
        "messages":[
            {"role":"system", 
            "content":system_rule
            },
            {"role":"user",
            "content":prompt
            }
        ]
    }


    # sending response to the ai
    # headers is waht we builded
    response = ollama.chat(model="qwen2.5-coder:7b", messages=[
        {"role":"system", 
        "content":system_rule
        },
        {"role":"user",
        "content":f"Existing code base:\n{previous_memory}\n\nUpdate to apply:{prompt}"
        }
    ])
    
    
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

    # store the current prompt in memory
    stage_manager.script_saver("ai_gen_script.py", final_executable_code, user_request)

    # returning the script
    return file_name
