''' the bridger, it connects main.py and ui.py -n'''

# initialising the bridger
from voice_input.cad_assist.ai_core import translator
from voice_input.cad_assist import runner

# create a function that will be used by ui / user_requests
def process_command(user_input):
    # checking conditions for user_input
    if not user_input:
        return None
    if user_input.lower() in ["exits", "quit", "q"]:
        print("Shutting down")
        return None
    
    print(f"Thinking about:{user_input}....")
    # translating user_input to code / ai gonna process this
    generated_script = translator(user_input)

    # conditions checks if the generated scripts os good quality and ok to run
    if generated_script:
        print("Executing Script")
        # runs the script which llm generated
        runner.execute_cad_scripts(generated_script)
        print("Successfully Generated")
    # if failed print this
    else:
        print("Failed To generate the script")
