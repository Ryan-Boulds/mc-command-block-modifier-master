import tkinter as tk
from tkinter import ttk
import logging
import pyperclip

from modify_laser_tab.modify_laser_gui import create_modify_laser_gui
from set_coordinates_tab.set_coordinates_gui import create_set_coordinates_gui
from change_block_tab.change_block_gui import create_change_block_gui
from generate_laser_tab.generate_laser_gui import create_generate_laser_gui
from generate_end_beam_tab.generate_end_beam_gui import create_generate_end_beam_gui
from rename_tag_group_tab.rename_tag_group_gui import create_rename_tag_group_gui
from settings_tab.settings_gui import create_settings_gui
from worldedit_tab.worldedit_gui import create_worldedit_schematic_gui
from clipboard_parser.ClipboardParser import ClipboardCoordinateParser
from command_processor import CommandProcessor
from settings import load_settings, save_settings
from utils import (
    setup_logging,
    toggle_always_on_top,
    start_record_keybind,
    record_keybind,
    process_clipboard,
    on_closing,
    copy_to_clipboard
)
from generate_end_beam_tab.modifier import generate_end_beam_commands, generate_kill_end_beam_command
from generate_laser_tab.modifier import generate_laser_commands, generate_kill_laser_command, parse_clipboard_coordinates
from change_block_tab.modifier import modify_clipboard_command, generate_kill_block_display_command

class CommandModifierGUI:
    def __init__(self, root):
        setup_logging()  # Use enhanced logging from utils.py
        self.root = root
        self.root.title("Minecraft Command Block Modifier")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # Initialize settings and variables
        self.settings = load_settings()
        self.always_on_top = tk.BooleanVar(value=self.settings.get("always_on_top", True))
        self.key_bind = tk.StringVar(value=self.settings.get("key_bind", ""))
        self.coord_format = tk.StringVar(value=self.settings.get("coord_format", "Decimal"))
        self.is_recording_key = False
        self.is_destroyed = False

        # Initialize command processor and clipboard parser
        self.command_processor = CommandProcessor()
        self.command_processor.set_gui(self)
        self.clipboard_parser = ClipboardCoordinateParser(self)

        # Initialize variables for all tabs
        self.pos_vars = [tk.StringVar(value="0") for _ in range(3)]  # Used by other tabs
        self.target_vars = [tk.StringVar(value="0") for _ in range(3)]
        self.pos_x_set = tk.StringVar(value="0.0")
        self.pos_y_set = tk.StringVar(value="0.5")
        self.pos_z_set = tk.StringVar(value="0.999999")
        self.trans_x = tk.StringVar(value="0.5")
        self.trans_y = tk.StringVar(value="0.0")
        self.trans_z = tk.StringVar(value="0.0")
        self.beam_scale = tk.StringVar(value="-150.0")
        self.centering_x = tk.StringVar(value="0.0")
        self.centering_y = tk.StringVar(value="0.0")
        self.centering_z = tk.StringVar(value="0.0")
        self.block_text = tk.StringVar(value="minecraft:lime_concrete")
        self.tag_text = tk.StringVar(value="beam1")
        self.laser_x = tk.StringVar(value="0")
        self.laser_y = tk.StringVar(value="0")
        self.laser_z = tk.StringVar(value="0")
        self.laser_block = tk.StringVar(value="minecraft:lime_concrete")
        self.laser_length = tk.StringVar(value="-150.0")
        self.laser_tag = tk.StringVar(value="beam1")
        self.end_beam_x = tk.StringVar(value="0")
        self.end_beam_y = tk.StringVar(value="0")
        self.end_beam_z = tk.StringVar(value="0")
        self.end_beam_target_x = tk.StringVar(value="0")
        self.end_beam_target_y = tk.StringVar(value="0")
        self.end_beam_target_z = tk.StringVar(value="0")
        self.end_beam_tag = tk.StringVar(value="laser")
        self.change_block_tag = tk.StringVar(value="beam1")  # Added for Change Block tab
        self.modify_coords = tk.BooleanVar(value=True)
        self.modify_translation = tk.BooleanVar(value=True)
        self.modify_scale = tk.BooleanVar(value=True)
        self.modify_centering = tk.BooleanVar(value=True)
        self.laser_mode = tk.StringVar(value="laser")
        self.schematic_block = tk.StringVar(value="minecraft:command_block")
        self.schematic_width = tk.StringVar(value="1")
        self.schematic_height = tk.StringVar(value="1")
        self.schematic_length = tk.StringVar(value="1")
        self.schematic_x = tk.StringVar(value="0")
        self.schematic_y = tk.StringVar(value="0")
        self.schematic_z = tk.StringVar(value="0")
        self.schematic_command = tk.StringVar(value="say Hello from command block")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Create frames for each tab
        self.modify_laser_frame = ttk.Frame(self.notebook)
        self.set_coordinates_frame = ttk.Frame(self.notebook)
        self.change_block_frame = ttk.Frame(self.notebook)
        self.generate_laser_frame = ttk.Frame(self.notebook)
        self.generate_end_beam_frame = ttk.Frame(self.notebook)
        self.rename_tag_group_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.worldedit_frame = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.modify_laser_frame, text="Modify Laser")
        self.notebook.add(self.set_coordinates_frame, text="Set Coordinates")
        self.notebook.add(self.change_block_frame, text="Change Block")
        self.notebook.add(self.generate_laser_frame, text="Generate Laser")
        self.notebook.add(self.generate_end_beam_frame, text="Generate End Beam")
        self.notebook.add(self.rename_tag_group_frame, text="Rename Tag/Group")
        self.notebook.add(self.settings_frame, text="Settings")
        self.notebook.add(self.worldedit_frame, text="WorldEdit Schematic")

        # Initialize tab GUIs
        create_modify_laser_gui(self.modify_laser_frame, self)
        create_set_coordinates_gui(self.set_coordinates_frame, self)
        create_change_block_gui(self.change_block_frame, self)
        create_generate_laser_gui(self.generate_laser_frame, self)
        create_generate_end_beam_gui(self.generate_end_beam_frame, self)
        create_rename_tag_group_gui(self.rename_tag_group_frame, self)
        create_settings_gui(self.settings_frame, self)
        create_worldedit_schematic_gui(self.worldedit_frame, self)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Apply initial settings
        if self.always_on_top.get():
            self.toggle_always_on_top()
        if self.key_bind.get():
            self.root.bind(self.key_bind.get(), lambda e: self.process_clipboard())

        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))

    def toggle_always_on_top(self):
        toggle_always_on_top(self)

    def start_record_keybind(self):
        start_record_keybind(self)

    def record_keybind(self, event):
        record_keybind(self, event)

    def copy_to_clipboard(self, text):
        copy_to_clipboard(self, text)

    def process_clipboard(self):
        process_clipboard(self)

    def generate_laser(self):
        from generate_laser_tab.modifier import generate_laser_commands
        generate_laser_commands(self)

    def generate_kill_laser(self):
        from generate_laser_tab.modifier import generate_kill_laser_command
        generate_kill_laser_command(self)

    def copy_from_clipboard(self):
        from generate_laser_tab.modifier import parse_clipboard_coordinates
        parse_clipboard_coordinates(self)

    def generate_end_beam(self):
        from generate_end_beam_tab.modifier import generate_end_beam_commands
        generate_end_beam_commands(self)

    def generate_kill_end_beam(self):
        from generate_end_beam_tab.modifier import generate_kill_end_beam_command
        generate_kill_end_beam_command(self)

    def modify_clipboard_command(self):
        from change_block_tab.modifier import modify_clipboard_command
        modify_clipboard_command(self)

    def generate_kill_block_display(self):
        from change_block_tab.modifier import generate_kill_block_display_command
        generate_kill_block_display_command(self)

    def process_command(self, command):
        current_tab = self.notebook.tab(self.notebook.select(), "text")

        if current_tab == "Modify Laser":
            from modify_laser_tab.modifier import process_command
            process_command(self, command)
        elif current_tab == "Set Coordinates":
            from set_coordinates_tab.modifier import process_command
            process_command(self, command)
        elif current_tab == "Change Block":
            from change_block_tab.modifier import modify_clipboard_command
            return modify_clipboard_command(self)
        elif current_tab == "Generate Laser":
            from generate_laser_tab.modifier import generate_laser_commands
            return generate_laser_commands(self)
        elif current_tab == "Generate End Beam":
            from generate_end_beam_tab.modifier import generate_end_beam_commands
            return generate_end_beam_commands(self)
        elif current_tab == "Rename Tag/Group":
            from rename_tag_group_tab.modifier import process_command
            process_command(self, command)
        elif current_tab == "WorldEdit Schematic":
            from worldedit_tab.modifier import process_command
            process_command(self, command)

if __name__ == "__main__":
    root = tk.Tk()
    app = CommandModifierGUI(root)
    root.mainloop()