''' runner.py is like phone case if phone falls case protects phone , just like that if any error occurs
runner.py tries to fix if not it stores the cause of error for later fixex '''

# importing nessary modules
import subprocess
import subprocess
import os
from pathlib import Path
import sys

# 1. Setup Folder Paths
# import all folder path from config file
from Keys.config import output_location, script_location, logs_location, free_cad_cmd

# 2. the checker (make sure that output and logs folder exists)
mandatory_path = [output_location, logs_location]
for folder in mandatory_path:
    if not folder.exists():
        print(f"Creating Folder:", {folder})
        folder.mkdir(parents = True, exist_ok = True)


# 3. the executor (runns all the function)
def execute_cad_scripts(script_name):
    # mentioning script path
    script_path_use = script_location / script_name
    print(f"Running Script:",{script_name})
    # we define this so every part of code can access / see this
    log_report = logs_location / "error.report.txt"

    try:
        # we try to run and capture the outcome of this
        result = subprocess.run (
            [free_cad_cmd, str(script_path_use)],
            capture_output= True,
            text = True,
            timeout = 20
        )

        # if script finished without error it prints sucess 
        if result.returncode == 0 and not result.stderr.strip():
            print(f"Script Sucessfully Executed \n Script:",{script_name})
            print("Log:\n",result.stdout) # this prints what script printed
        else:
            # if failed we notify and store info in logs
            print(f"Failed \nCrash Script",{script_name})


            # we have to create (if not exists) and write error report
            with open (log_report,"a") as file:
                file.write(result.stderr)

            print(f"Error Details Are Stored in ", {log_report})
    except subprocess.TimeoutExpired:
        # this part gonna catch the time breaker even
        print(f"Time Exceeded! Script took too long to run Perphaps Long infinte loop? \nUsed Script:{script_name}")
        # entering error in log 
        with open(log_report,"a") as file:
            file.write("Error: Execution Time Exceeded")
        print(f"Time_Out Details Stored in:",{log_report})

    
# 4. test run of runner.py
if __name__ == "__main__":
    # test the script 
    execute_cad_scripts("hang.py")