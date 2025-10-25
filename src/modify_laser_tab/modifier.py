# Updated on 12:03 PM CDT, Monday, September 01, 2025
import re
import logging
import tkinter as tk
import pyperclip

def process_command(gui, command):
    logging.debug(f"Processing command in Modify Laser tab: {command}")
    if not command.startswith('/'):
        command = '/' + command

    modified_command = command
    original_coords = None

    try:
        center_x = float(gui.centering_x.get()) if gui.centering_x.get() and gui.modify_centering.get() else 0.0
        center_y = float(gui.centering_y.get()) if gui.centering_y.get() and gui.modify_centering.get() else 0.0
        center_z = float(gui.centering_z.get()) if gui.centering_z.get() and gui.modify_centering.get() else 0.0
    except ValueError:
        center_x, center_y, center_z = 0.0, 0.0, 0.0
        logging.warning("Invalid centering modifier values, using defaults (0.0, 0.0, 0.0)")
        gui.print_to_text("Warning: Invalid centering values, using defaults (0.0, 0.0, 0.0)", "normal")

    if command == '/' or not command.strip('/'):
        try:
            x = float(gui.pos_x_set.get()) + center_x if gui.modify_coords.get() and gui.pos_x_set.get() else 0.0
            y = float(gui.pos_y_set.get()) + center_y if gui.modify_coords.get() and gui.pos_y_set.get() else 0.5
            z = float(gui.pos_z_set.get()) + center_z if gui.modify_coords.get() and gui.pos_z_set.get() else 0.999999
            trans_x = float(gui.trans_x.get()) if gui.modify_translation.get() and gui.trans_x.get() else 0.5
            trans_y = float(gui.trans_y.get()) if gui.modify_translation.get() and gui.trans_y.get() else 0.0
            trans_z = float(gui.trans_z.get()) if gui.modify_translation.get() and gui.trans_z.get() else 0.0
            beam_scale = float(gui.beam_scale.get()) if gui.modify_scale.get() and gui.beam_scale.get() else -150.0
            tag = gui.tag_text.get().strip() if gui.tag_text.get() else "beam1"
            block_type = gui.block_text.get().strip().replace("__", ":") if gui.block_text.get() else "minecraft:lime_concrete"

            modified_command = (
                f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f} '
                f'{{block_state:{{Name:"{block_type}"}},'
                f'transformation:{{translation:[{trans_x:.6f}f,{trans_y:.6f}f,{trans_z:.6f}f],'
                f'scale:[0.1f,0.1f,{beam_scale:.6f}f],'
                f'left_rotation:[0.0f,0.0f,0.0f,1.0f],'
                f'right_rotation:[0.0f,0.0f,0.0f,1.0f]}},'
                f'brightness:{{block:15,sky:15}},shadow:false,billboard:"fixed",Tags:["{tag}"]}}'
            )
            logging.debug(f"Generated new command: {modified_command}")
            gui.print_to_text(f"Generated Command: {modified_command}", "command")
        except ValueError as e:
            logging.error(f"Error generating command: {e}")
            gui.print_to_text("Error: Please enter valid numbers for coordinates, translation, and scale.", "normal")
            return command
    else:
        coord_match = re.match(r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', command)
        if coord_match:
            x, y, z = map(float, coord_match.groups())
            original_coords = [x, y, z]
            logging.debug(f"Extracted coordinates: {original_coords}")

        new_tag = gui.tag_text.get().strip() if gui.tag_text.get() else "beam1"
        if 'Tags:' in command:
            modified_command = re.sub(
                r'Tags:\s*\["([^"]*)"\]',
                f'Tags:["{new_tag}"]',
                modified_command,
                flags=re.DOTALL
            )
        elif command.startswith('/execute') or command.startswith('/tp'):
            modified_command = re.sub(
                r'tag=([^,\s\]]+)',
                f'tag={new_tag}',
                modified_command,
                flags=re.DOTALL
            )

        if gui.modify_coords.get() and original_coords:
            try:
                x = float(gui.pos_x_set.get()) + center_x if gui.pos_x_set.get() else original_coords[0] + center_x
                y = float(gui.pos_y_set.get()) + center_y if gui.pos_y_set.get() else original_coords[1] + center_y
                z = float(gui.pos_z_set.get()) + center_z if gui.pos_z_set.get() else original_coords[2] + center_z
                modified_command = re.sub(
                    r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)',
                    f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f}',
                    modified_command
                )
                gui.print_to_text(f"Original Coordinates: {original_coords}", "coord")
                gui.print_to_text(f"New Coordinates: [{x:.6f}, {y:.6f}, {z:.6f}]", "modified_coord")
            except ValueError:
                logging.warning("Invalid coordinate values, skipping coordinate modification")
                gui.print_to_text("Warning: Invalid coordinate values, skipping coordinate modification", "normal")

        if gui.modify_translation.get():
            try:
                trans_x = float(gui.trans_x.get()) if gui.trans_x.get() else 0.5
                trans_y = float(gui.trans_y.get()) if gui.trans_y.get() else 0.0
                trans_z = float(gui.trans_z.get()) if gui.trans_z.get() else 0.0
                modified_command = re.sub(
                    r'translation:\[\s*-?\d+\.?\d*f,\s*-?\d+\.?\d*f,\s*-?\d+\.?\d*f\s*\]',
                    f'translation:[{trans_x:.6f}f,{trans_y:.6f}f,{trans_z:.6f}f]',
                    modified_command
                )
            except ValueError:
                logging.warning("Invalid translation values, skipping translation modification")
                gui.print_to_text("Warning: Invalid translation values, skipping translation modification", "normal")

        if gui.modify_scale.get():
            try:
                beam_scale = float(gui.beam_scale.get()) if gui.beam_scale.get() else -150.0
                modified_command = re.sub(
                    r'scale:\[\s*-?\d+\.?\d*f,\s*-?\d+\.?\d*f,\s*-?\d+\.?\d*f\s*\]',
                    f'scale:[0.1f,0.1f,{beam_scale:.6f}f]',
                    modified_command
                )
            except ValueError:
                logging.warning("Invalid scale values, skipping scale modification")
                gui.print_to_text("Warning: Invalid scale values, skipping scale modification", "normal")

        if gui.block_text.get():
            block_type = gui.block_text.get().strip().replace("__", ":")
            modified_command = re.sub(
                r'block_state:\{Name:"[^"]*"\}',
                f'block_state:{{Name:"{block_type}"}}',
                modified_command
            )

    if hasattr(gui, 'cmd_text_set') and gui.cmd_text_set.winfo_exists():
        gui.cmd_text_set.delete("1.0", tk.END)
        gui.cmd_text_set.insert("1.0", modified_command)
    else:
        logging.warning("cmd_text_set not found or not initialized")
        gui.print_to_text("Warning: cmd_text_set not found or not initialized", "normal")

    pyperclip.copy(modified_command.encode('utf-8').decode('utf-8'))
    gui.print_to_text("Command copied to clipboard.", "normal")
    return modified_command

def set_laser_preset(gui):
    gui.modify_coords.set(True)
    gui.modify_translation.set(True)
    gui.modify_scale.set(True)
    gui.modify_centering.set(True)
    gui.pos_x_set.set("0.0")
    gui.pos_y_set.set("0.5")
    gui.pos_z_set.set("0.999999")
    gui.trans_x.set("0.5")
    gui.trans_y.set("0.0")
    gui.trans_z.set("0.0")
    gui.beam_scale.set("-150.0")
    gui.centering_x.set("0.0")
    gui.centering_y.set("0.0")
    gui.centering_z.set("0.0")
    gui.tag_text.set("beam1")
    gui.block_text.set("minecraft:lime_concrete")
    gui.laser_mode.set("laser")
    logging.debug("Set laser preset values")
    gui.print_to_text("Applied Laser preset", "normal")

def set_lightbeam_preset(gui):
    gui.modify_coords.set(True)
    gui.modify_translation.set(True)
    gui.modify_scale.set(True)
    gui.modify_centering.set(True)
    gui.pos_x_set.set("0.0")
    gui.pos_y_set.set("0.5")
    gui.pos_z_set.set("0.999999")
    gui.trans_x.set("0.0")
    gui.trans_y.set("0.0")
    gui.trans_z.set("0.0")
    gui.beam_scale.set("-75.0")
    gui.centering_x.set("0.0")
    gui.centering_y.set("0.0")
    gui.centering_z.set("0.0")
    gui.tag_text.set("lightbeam1")
    gui.block_text.set("minecraft:light_blue_concrete")
    gui.laser_mode.set("lightbeam")
    logging.debug("Set lightbeam preset values")
    gui.print_to_text("Applied Lightbeam preset", "normal")