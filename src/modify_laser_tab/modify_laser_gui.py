# Updated on 12:25 PM CDT, Monday, September 01, 2025
import tkinter as tk
from tkinter import ttk
from .modifier import set_laser_preset, set_lightbeam_preset
from utils import adjust_offset

def create_modify_laser_gui(frame, gui):
    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    tk.Label(scrollable_frame, text="Modify Laser", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=5, pady=5, sticky="w")

    tk.Checkbutton(scrollable_frame, text="Modify Coords", variable=gui.modify_coords, font=("Arial", 10), bg='#f0f0f0').grid(row=1, column=0, columnspan=2, pady=2, sticky="w")
    tk.Checkbutton(scrollable_frame, text="Modify Translation", variable=gui.modify_translation, font=("Arial", 10), bg='#f0f0f0').grid(row=1, column=2, columnspan=2, pady=2, sticky="w")
    tk.Checkbutton(scrollable_frame, text="Modify Scale", variable=gui.modify_scale, font=("Arial", 10), bg='#f0f0f0').grid(row=2, column=0, columnspan=2, pady=2, sticky="w")
    tk.Checkbutton(scrollable_frame, text="Modify Centering", variable=gui.modify_centering, font=("Arial", 10), bg='#f0f0f0').grid(row=2, column=2, columnspan=2, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="Position:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=3, column=0, columnspan=5, pady=2, sticky="w")
    for i, (label, var) in enumerate([("X:", gui.pos_x_set), ("Y:", gui.pos_y_set), ("Z:", gui.pos_z_set)]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+4, column=0, pady=2, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+4, column=1, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▲", command=lambda v=var, c=1: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+4, column=2, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▼", command=lambda v=var, c=-1: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+4, column=3, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▲10", command=lambda v=var, c=10: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+4, column=4, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▼10", command=lambda v=var, c=-10: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+4, column=5, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="Centering:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=7, column=0, columnspan=5, pady=2, sticky="w")
    for i, (label, var) in enumerate([("X:", gui.centering_x), ("Y:", gui.centering_y), ("Z:", gui.centering_z)]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+8, column=0, pady=2, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+8, column=1, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▲", command=lambda v=var, c=1: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+8, column=2, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▼", command=lambda v=var, c=-1: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+8, column=3, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▲10", command=lambda v=var, c=10: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+8, column=4, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▼10", command=lambda v=var, c=-10: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+8, column=5, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="Translation:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=11, column=0, columnspan=5, pady=2, sticky="w")
    for i, (label, var) in enumerate([("X:", gui.trans_x), ("Y:", gui.trans_y), ("Z:", gui.trans_z)]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+12, column=0, pady=2, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+12, column=1, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▲", command=lambda v=var, c=1: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+12, column=2, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▼", command=lambda v=var, c=-1: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+12, column=3, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▲10", command=lambda v=var, c=10: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+12, column=4, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="▼10", command=lambda v=var, c=-10: adjust_offset(v, c), font=("Arial", 8)).grid(row=i+12, column=5, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="Scale:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=15, column=0, columnspan=5, pady=2, sticky="w")
    tk.Label(scrollable_frame, text="Beam Scale:", font=("Arial", 10), bg='#f0f0f0').grid(row=16, column=0, pady=2, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.beam_scale, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=16, column=1, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="Block:", font=("Arial", 10), bg='#f0f0f0').grid(row=17, column=0, pady=2, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.block_text, width=20, bg='#ffffff', font=("Arial", 10)).grid(row=17, column=1, columnspan=2, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="Tag:", font=("Arial", 10), bg='#f0f0f0').grid(row=18, column=0, pady=2, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.tag_text, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=18, column=1, pady=2, sticky="w")

    tk.Button(scrollable_frame, text="Laser Preset", command=lambda: set_laser_preset(gui), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=19, column=0, columnspan=2, pady=5, sticky="w")
    tk.Button(scrollable_frame, text="Lightbeam Preset", command=lambda: set_lightbeam_preset(gui), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=19, column=2, columnspan=2, pady=5, sticky="w")

    tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: gui.clipboard_parser.autofill_coordinates([gui.pos_x_set, gui.pos_y_set, gui.pos_z_set, gui.centering_x, gui.centering_y, gui.centering_z, gui.trans_x, gui.trans_y, gui.trans_z]), font=("Arial", 8)).grid(row=20, column=0, columnspan=5, pady=2, sticky="w")

    gui.cmd_text_set = tk.Text(scrollable_frame, height=2, width=40)
    gui.cmd_text_set.grid(row=21, column=0, columnspan=2, pady=2, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.cmd_text_set.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=21, column=2, pady=2, sticky="w")