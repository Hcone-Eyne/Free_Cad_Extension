import customtkinter as ctk


class phil_theme:
    bg          = "#18181B"   # window bg
    pill_bg     = "#27272A"   # pill frame
    border_idle = "#3F3F46"
    text_main   = "#FAFAFA"
    text_dim    = "#A1A1AA"

    btn_voice   = "#6366F1"   # indigo
    btn_text    = "#0EA5E9"   # sky blue
    btn_hover_v = "#4F46E5"
    btn_hover_t = "#0284C7"

    safe        = "#22C55E"
    danger      = "#EF4444"
    thinking    = "#F59E0B"


class Visual_look_Phill(ctk.CTkFrame):
    """
    Phil's floating pill UI.
    Layout (top→bottom):
      1. Status label
      2. Button row  [🎙 Voice]  [✏ Text]
      3. Text entry  (hidden until Text-mode is active)
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=phil_theme.pill_bg,
            corner_radius=20,
            border_width=1,
            border_color=phil_theme.border_idle,
            **kwargs
        )

        # ── Status label ──────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(
            self,
            text="READY TO BUILD",
            text_color=phil_theme.text_main,
            font=("Inter", 12, "bold"),
            fg_color="transparent",
        )
        self.status_label.pack(pady=(12, 4), padx=20)

        # ── Button row ────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=(0, 8), padx=16)

        self.voice_btn = ctk.CTkButton(
            btn_row,
            text="🎙  Voice",
            width=120, height=32,
            corner_radius=10,
            fg_color=phil_theme.btn_voice,
            hover_color=phil_theme.btn_hover_v,
            text_color="#FFFFFF",
            font=("Inter", 12, "bold"),
            command=master.on_voice_click,
        )
        self.voice_btn.pack(side="left", padx=(0, 8))

        self.text_btn = ctk.CTkButton(
            btn_row,
            text="✏  Text",
            width=120, height=32,
            corner_radius=10,
            fg_color=phil_theme.btn_text,
            hover_color=phil_theme.btn_hover_t,
            text_color="#FFFFFF",
            font=("Inter", 12, "bold"),
            command=master.on_text_click,
        )
        self.text_btn.pack(side="left")

        # ── Text entry (hidden by default) ────────────────────────────
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        # not packed yet — shown only in text-mode

        self.entry = ctk.CTkEntry(
            self.entry_frame,
            placeholder_text="Type your command…",
            width=270, height=32,
            fg_color="#3F3F46",
            text_color=phil_theme.text_main,
            border_color=phil_theme.btn_text,
            font=("Inter", 12),
        )
        self.entry.pack(side="left", padx=(0, 6))
        self.entry.bind("<Return>", lambda e: master.on_text_submit(self.entry.get()))

        send_btn = ctk.CTkButton(
            self.entry_frame,
            text="→",
            width=32, height=32,
            corner_radius=8,
            fg_color=phil_theme.btn_text,
            hover_color=phil_theme.btn_hover_t,
            font=("Inter", 14, "bold"),
            command=lambda: master.on_text_submit(self.entry.get()),
        )
        send_btn.pack(side="left")

    # ── Public helpers ────────────────────────────────────────────────

    def set_status(self, message: str, state: str = "normal"):
        self.status_label.configure(text=message.upper())
        colors = {
            "safe":     phil_theme.safe,
            "danger":   phil_theme.danger,
            "thinking": phil_theme.thinking,
            "normal":   phil_theme.border_idle,
        }
        self.configure(border_color=colors.get(state, phil_theme.border_idle))

    def show_text_entry(self):
        self.entry_frame.pack(pady=(0, 10), padx=16)
        self.entry.delete(0, "end")
        self.entry.focus()

    def hide_text_entry(self):
        self.entry_frame.pack_forget()

    def set_voice_active(self, active: bool):
        color = phil_theme.danger if active else phil_theme.btn_voice
        self.voice_btn.configure(
            fg_color=color,
            text="⏹  Stop" if active else "🎙  Voice",
        )