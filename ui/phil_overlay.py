# importing dependcies
import customtkinter as ctk
from ui.phil_widget import Visual_look_Phill
from pathlib import Path
import sys
import threading
# importing voice and text functions
current_location = Path(__file__).resolve().parent.parent

if str(current_location) not in sys.path:
    sys.path.insert(0, str(current_location))

from speech_processor.voice_handler import The_listener
# the code starts here

# creating a class for overlay to work on top of FreeCAD

class Phil_Overlay(ctk.CTk):
    def __init__(self):
        # sending the flag signal to engine to start
        self.is_ready = False # the flag for keyboard thread
        self.withdraw()
        # super() means “I’m taking over, but I’ll still follow the plans and principles Steve Jobs set up first.”
        super().__init__()

        # hiding the window while loading / working on
        self.withdraw()

        # initialising phil listening
        self.listener = The_listener()


        # 1. removing borders, no tittle bar , no "x" close button
        self.overrideredirect(True)

        # loading the created phil widget 
        # the macos / forcing macos to hide borders
        # telling macos to not show the Window borders
        try:
            self.tk.call("tk","unsupported","MacWindowStyle","style",self._w,'borderless','none')
        except:
            pass

        # 2 making the window transparent
        # We set the internal color to "transparent" directly to avoid the ValueError
        self._fg_color = "transparent"

        # 2.1 Making the phil Float: Stay on all top windoes
        # transprent fix
        self.configure(background="systemTransparent") # make the window transparent\
        self.wm_attributes("-transparent",True) # wm_attributes is like decide how the phil should be shown to user
        self.attributes("-alpha",1.0) # alpha = controls opcaity of window (1.0 is visible, 0.0 not visible)
        self.attributes("-topmost",True) # tells to show the window on the top of others

        # 4. Positioning the phil
        # fecthing the info of display
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # forcing to hide the tittle bar and start the phil
        self.after(20000,self.safe_start)

        def safe_start(self):
            self.deiconify() # show the window
            activate_phil(self) # start the phil

            # now start the ears
            self.listen_thread = threading.Thread(target = self.continous_listen, daemon= True)
            self.listen_thread.start()

            # let keyborad thread to knew the its safe to start
            self.is_ready = True
            print("Phill Notifier Initialised")

        # building function to activate phil
        def activate_phil(self):
            # show the first window
            self.deiconify()
            # start the listen process
            self.listen_thread = threading.Thread(target = self.continous_listen, daemon=True)
            self.listen_thread.start()
            # let keyborad thread to knew the its safe to start
            self.is_ready = True
            

        # setting width of the phil
        width = 400
        height = 80
        x = (screen_width // 2) - (width // 2)
        y = screen_height - 150 # 150 pixel about the button

        # geometry told to set the position of windows
        # The result: a small rectangle centered horizontally and 150 pixels from the bottom.
        self.geometry(f"{width}x{height}+{x}+{y}")

        # 5. attach the phil inside of the window created above 
        self.phil = Visual_look_Phill(master=self,bg_color ="#000000") #Pass a concrete background color to stop the widget from searching for one and any hex color works here
        self.phil.pack(expand=True)

        # 5.1 adding controls for stering
        self.phil.bind("<Button-1>",self.start_move) # makes respond to mouse events like clicking and draging
        self.phil.bind("<B1-Motion>",self.move_logic) # moves the window while dragging

        # making it grab friendly (movable)
        self.phil.status_label.bind("<Button-1>",self.start_move)
        self.phil.status_label.bind("<B1-Motion>",self.move_logic)

        # 6. Reveal the phil
        self.deiconify() # deiconify = make the window visible from hidden state
        self.update() # update = force the window to update and show
        self.lift() # lift = bring the phil to the top

        # starting background thread so ui stays responseive
        self.listen_thread = threading.Thread(target=self.continuous_listen, daemon=True)
        self.listen_thread.start()
    # ====================== The Listener ======================
    def continuous_listen(self):
        # importing requied dependecies here
        from voice_input.command_bridge import process_command
        ''' Runs in background and waits for voice input'''
        while True:
            # blocking thread - for safety purpose not to clash with anoother thread
            voice_data = self.listener.listen()
            
            # developing condition to check voice data
            if voice_data:
                # update ui
                self.after(0, self.process_user_input ,voice_data)

                # cad processing - no ui involement (prevents crash)
                process_command(voice_data)
        


    # creating a function to move the phil
    #====================== Movement logic ======================
    def start_move(self,event):
        # record initial position
        self.x_position = event.x
        self.y_position = event.y

    def move_logic(self,event):
        # prediciting / calculate new position
        x = self.winfo_x() + event.x - self.x_position
        y = self.winfo_y() + event.y - self.y_position
        self.geometry(f"+{x}+{y}") # update window position

    def sender(self,user_input):
        print(f"Phil is Processing:{user_input}")

    def user_requests(self, text_data):
        # checking for data
        if not text_data: return 

        # update ui to show phil is thinking
        self.phil.set_status(f"Processing.....\n\n{text_data[:15]}.....",state = "Thinking")

        # calling the command_bridge 
        from voice_input.command_bridge import process_command
        process_command(text_data)

        # this part is critical
        # soon the text file will pass through installed llm
        # and llm converts them into python commands
        print(f"Implementing Changes...\n\n{text_data}\n")

        # clearing the box for next entry of command
        self.phil.entry.delete(0,"end")

    # ============================== Accuracy Testing ============================== 
    def process_user_input(self,text_data):
        # 1. normalising the text data by removing making it lowercase and removing unwanted spaces
        # important for accuracy 
        normalizer = text_data.strip().lower()

        # 2. prints exactly what phil hears
        print("Exact Input:",normalizer)

        # 3. Keyword Search (checker)
        # if voice is messy ,by looking for words it understands
        if "cube" in normalizer or "box" in normalizer:
            self.phil.set_status("Target:Cube Identified")
        if "sphere" in normalizer or "ball" in normalizer:
            self.phil.set_status("Target:Sphere Identified")
        else:
            # if it doesn't recognize anything
            self.phil.set_status(f"Heared: {normalizer[:10]}.....", state = "thinking" )

# the tester / preview of the code
if __name__ == "__main__":
    app = Phil_Overlay()
    app.sender("create a new sketch")
    print("Overlay is currently active, to close use control + c")
    app.mainloop()
    