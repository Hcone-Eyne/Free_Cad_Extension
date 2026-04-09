''' this program is like short term memory for ai
with this it stores user before prompts / request and process that 
if future prompt request interaction with the past prompt object '''

# import all dependiences
import json
from pathlib import Path
from Keys.config import memory_path

# locating memory folder for ai
memory_path = memory_path

# script saver in json format
# this function stores the prompt which is used to make 3d object
def script_saver(script_name, script_content, parameters = None):
    # this stores current use script details so ai can modify it
    store_data = {
        "current_file":script_name,
        "code":script_content,
        "parameters":parameters or {}
    }

    # saving the memory
    with open(memory_path, "w") as file:
        json.dump(store_data, file , indent=4)
    print(f"Memory Saved \nMemory Saved Location:"[memory_path])    

# load the memory to ai
def load_memory():
    ''' this retrives the last known script from the memory '''
    # check if memory path exitts
    if not memory_path.exists():
        print("memory path isn't exists")
        # return stops code from being proceed futher
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
        return memory["code"]
    # if memory is empty return this message
    else:
        return "No Memory Found"