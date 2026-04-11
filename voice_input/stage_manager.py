''' this program is like short term memory for ai
with this it stores user before prompts / request and process that 
if future prompt request interaction with the past prompt object '''

# import all dependiences
import json
from pathlib import Path
from voice_input.Keys.config import memory_path

# locating memory folder for ai
memory_path = memory_path

# script saver in json format
# this function stores the prompt which is used to make 3d object
def script_saver(script_name, script_content, parameters = {"key":"value"}):
    # 1st principle ensure that directory exists
    memory_path.parent.mkdir(parents=True, exist_ok= True)

    # 2nd principle type sheielding preveing loop crash "Not a string"
    # this condition is going to convert set {} into string()
    if isinstance(script_content, set):
        script_name = list(script_name)[0]

    clean_name = str(script_name)
    clean_parameters = parameters if isinstance(parameters,dict) else {}

    # check if file exixts, if not create a NEW ONE!
    if not memory_path.exists() or memory_path.stat().st_size == 0:
        memory_path.touch()
        print(f"Memory path created, \nLocation:{memory_path.name}")
    # this stores current use script details so ai can modify it
    store_data = {
        "current_file":script_name,
        "code":script_content,
        "parameters":parameters if isinstance(parameters, dict) else {}
    }

    # saving the memory
    with open(memory_path, "w") as file:
        json.dump(store_data, file , indent=4)
    print(f"Memory Saved \nMemory Saved Location:{memory_path}")    

# load the memory to ai
def load_memory():
    ''' this retrives the last known script from the memory '''

    try:
        # check if memory path exitts
        if not memory_path.exists():
            print("memory path isn't exists")
            # return stops code from being proceed futher
            return None
    except Exception as e:
        print("Memory is either corrupted or empty")
        return None
    
    # loads json (memory) to ai
    with open(memory_path, "r") as file:
        # return loads the memory from json
        return json.load(file)

# getting last memory for ai to read and process futher
def get_memory():
    ''' a quick helper to get last memory for ai to read '''
    memory = load_memory()
    # if memory isn't empty return it
    if memory is not None:
        return memory.get("code", "No Memory Found")
    # if memory is empty return this message
    else:
        return "No Memory Found"