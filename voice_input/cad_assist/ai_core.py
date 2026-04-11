''' the translator between ai and source code
it takes stage manager's memory and voice / text and gives to api (ai) to get a perfect result '''

# importing nessary modules
from voice_input import stage_manager
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from voice_input.Keys.config import ai_gen_script
from voice_input import stage_manager

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
    # has to be in string(tuple) instead of dict {} 
    system_rule = (
        "You are a FreeCAD assistant. Only return valid Python code."
        "Return ONLY raw Python code."
        "NO Explanation Required."
        "IMPORTANT: Do not put periods (.) at the end of lines unless it is a method call. "
        "CRITICAL: Always save the final shape using: part.Shape.exportStep('{str(output_location)}/model.step')."
        "Start with: import FreeCAD as App, import Part"
        "Use EXACT syntax: doc.addObject('Part::Feature', 'Name')."
        "Do NOT include trailing periods or markdown backticks. "
        "Export final shape to: 'voice_input/ai_generated_scripts."
    )

    # send prompt to ai
    prompt = f"Previous Context:{previous_memory}\n\n Current Request:{user_request}"

    # unknown / sending request to ai
    headers = {
        "Authorization" : f"Bearer {api_key}",
        # no "." use slash instead for better navigation through file/folders
        "Content-Type":"application/json"
    }

    data = {
        "model":"openrouter/free",
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
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers = headers , json = data)

    # analysis the response and give it to user
    ai_response = response.json()

    # error handiling
    if "choices" not in ai_response:
        print(f"Api Error:{ai_response}")
        return None
    # raw data of ai in json format
    raw_code = ai_response["choices"] [0] ["message"] ["content"]

    # a clean python code (json to py)
    clean_code = raw_code.replace("```python", "").replace("```py", "").replace("```", "").strip()

    # save generated python script
    file_name = "ai_gen_script.py"
    with open(ai_gen_script, "w") as file:
        file.write(clean_code)
    print(f"Script of ai generated Saved\n Location:{ai_gen_script}")

    # store the current prompt in memory
    stage_manager.script_saver(file_name, clean_code)

    # returning output
    return str(file_name)
