# customtkinter is like import all fancy ui 
import customtkinter as ctk

# setting up theme
class phil_theme:
    primary_color = "#FFFFFF"
    secondary_color = "#00BFFF"
    text_color = "#1A1A1A"
    tertary_color = "#A9A9A9"

    # indicators
    safe_color = "#34C759"        # Green
    danger_color = "#FF3B30"      # Red
    thinking_color = "#007AFF"    # Blue

# initialising components for the phil
class Visual_look_Phill(ctk.CTkFrame):
    def __init__(self,master,**kwargs):
        super().__init__(
            master,
            fg_color = phil_theme.primary_color,
            corner_radius = 15,
            border_width = 1,
            border_color = phil_theme.tertary_color,
            **kwargs
        )
        
        # creating layout outside of the phil
        # we gonna use grid layout
        self.grid_columnconfigure(0,weight= 2)

        # creating a status label to let user know what's happening
        self.status_label = ctk.CTkLabel(
            self,
            text = "Ready To Build",
            text_color = phil_theme.text_color,
            font = ("Inter",14,"bold")
        )
        self.status_label.pack(pady = 10, padx = 20)
        
    # the upgraded version (inferface) of update_state
    def set_status(self, message, state = "normal"):
        # remote control of phil apperance
        # changes the ui text and border based on phil
        self.status_label.configure(text = message.upper())

        if state == "safe":
            self.configure(border_color = phil_theme.safe_color)
        elif state == "danger":
            self.configure(border_color = phil_theme.danger_color)
        elif state == "thinking":
            self.configure(border_color = phil_theme.thinking_color)
        else:
            self.configure(border_color = phil_theme.tertary_color)


# --- TESTING BLOCK ---
# This part only runs if you play THIS file directly
if __name__ == "__main__":
    # 1. Create the main "hidden" window
    root = ctk.CTk()
    root.title("Phil Widget Test")
    root.geometry("400x200")

    # 2. "Instantiate" your class (This is building the car from the blueprint)
    test_pill = Visual_look_Phill(master=root)
    
    # 3. Put it on the screen
    test_pill.pack(pady=50)

    # 4. Start the app
    print("Phil is alive! Closing this window will stop the script.")
    root.mainloop()