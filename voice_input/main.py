''' main part of the program
it stays in loop , takes input gives it to translator(ai_core) and then body(runner.py)
to execute result '''

# importing nessary modules
import sys
from voice_input.cad_assist.ai_core import translator
from voice_input.cad_assist import runner
from voice_input import stage_manager

# start the engine
def engine():
    print("Cad Assistant initialised:")

    # initializing loop 
    while True:
        try:
            # get input from user
            user_input = input("Prompt:").strip()

            if not user_input:
                continue
        
            if user_input.lower() in ["exits", "quit", "q"]:
                print("Shuting down")
                break

            # call the brain if input is received
            print("Thinking...")
            generated_script = translator(user_input)

            if generated_script:
                # call the runner
                print("Executing the given input..")
                runner.execute_cad_scripts(generated_script)
                print("Sucessfully Generated!")
            else:
                print("Failed To Generate Given Model")

        except KeyboardInterrupt:
            print("Shuting Down")
            break
        except Exception as e:
            print(f"Loop Crashed Error:{e}")

if __name__ == "__main__":
    engine()