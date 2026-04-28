''' main part of the program
it stays in loop , takes input gives it to translator(ai_core) and then body(runner.py)
to execute result '''

# importing nessary modules
import threading
import traceback
import sys
import time

# getting required files location
from pathlib import Path
thank_me_later = Path(__file__).resolve().parent.parent
# appending path location
sys.path.append(str(thank_me_later)) # hehehehe a fix to run main withn the folder

# import required modules
from voice_input.command_bridge import process_command
from voice_input.cad_assist.ai_core import translator
from voice_input.cad_assist import runner
from voice_input import stage_manager
from ui.phil_overlay import Phil_Overlay



def process_command(user_input):
    ''' the main function for voice and text'''
    if not user_input:
        return None
        
    if user_input.lower() in ["exits", "quit", "q"]:
        print("Shuting down")
        return None

    # call the brain if input is received
    print(f"Thinking about:{user_input}....")
    generated_script = translator(user_input)

    if generated_script:
        print("Executing Script ...")
        runner.execute_cad_scripts(generated_script)
        print("Sucessfully generated")
    else:
        print("Failed to generate the Script")


# start the engine
def engine(app):
    # adding  timer / flag to let ui load before start
    while not getattr(app, "is_ready", False):
        time.sleep(0.5)

    print("Cad Assistant initialised:")
    print("Unifined Input Active...")

    # initializing loop 
    while True:
        try:
            # to prevent crash
            time.sleep(2)
            # get input from user
            user_input = input("Prompt:").strip()

            if not user_input:
                continue
        
            if user_input.lower() in ["exits", "quit", "q"]:
                print("Shuting down")
                app.quit() #closing the ui
                break

            # call the function to process command
            process_command(user_input)
            # to quit the application 
            
        except EOFError:    
            break 
        except KeyboardInterrupt:
            print("Shuting Down")
            app.quit()
            break
        except Exception as e:
            print(f"Loop Crashed Error:{e}")
            traceback.print_exc()

if __name__ == "__main__":
    # create the ui instance first
    app = Phil_Overlay()
    # 1. Start the Voice Thread (phil's ear)
    # voice_thread = threading.Thread(target=app.continuous_listen, daemon=True) [this is controlled in phil_overlay]
    # voice_thread.start() [this is controlled in phil_overlay]

    # 2. start the text loop (keyboard) its own thread or another words this monitors text based inputa
    text_thread = threading.Thread(target = engine, args = (app,), daemon=True) # target = means it runs engine function in thread , args = passes app / arguments instance to it , daemon
    text_thread.start()
    
    # 3, start the ui on the main thread
    app.mainloop()