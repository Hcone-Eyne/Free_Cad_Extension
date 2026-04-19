# customtkinter is like import all fancy ui 
import customtkinter as ctk

# setting up theme
class phil_theme:
    primary_color = "#FFFFFF"
    secondary_color = "#00BFFF"
    text_color = "#1A1A1A"
    tertary_color = "#A9A9A9"

# initialising components for the phil
class Visual_look_Phill(ctk.CtkFrame):
    def __init__(self,master,**kwargs):
        super().__init__(
            master,
            fg_colour = phil_theme.primary_colour,
            corner_radius = 15,
            border_width = 1,
            border_color = phil_theme.tertary_colour,
            **kwargs
        )
        
        # creating layout outside of the phil
        # we gonna use grid layout
        self.grid_columnconfigire(0,weight= 2)

        # creating a status label to let user know what's happening
        self.status_label = ckt.CTKLabel(
            self,
            text = "Ready To Build",
            text_colour = phil_theme.text_color,
            font = ("Inter",14,"bold")
        )
        self.status_label.pack(pady = 10, padx = 20)
        
    # the interface
    def update_state(self, new_text, color = None):
        self.status_label.configure(text= new_text)
        if color:
            self.configure(border_color = color)