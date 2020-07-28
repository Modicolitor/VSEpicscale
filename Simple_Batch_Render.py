# BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# END GPL LICENSE BLOCK #####


import os
import shutil
from mathutils import Vector, Matrix
import bmesh
import bpy
bl_info = {
    "name": "Simple Batch Render",
    "author": "Martin Olanders",
    "version": (1, 3, 00),
    "blender": (2, 80, 0),
    "location": "Render > Render > Simple Batch Render",
    "description": "Will make a .bat file for batch rendering in Blender, will ONLY wok in windows",
    "warning": "",
    "wiki_url": "www.olanders.se\products.html",
    "category": "Render",
}

"""
Addonid: 20170313 1 2 00 
Usage:

Launch from "Render > Render > Simple Batch render"

Make a .bat file for batch render that can be launched from inside Blender or as it separate .bat file

Note:   Will only work in windows
        There must be a valid path to wherer blender.exe is located
        Also the .bat file must have the extension .bat

Additional links:
    Author Site: www.olanders.se
    e-mail: support@olanders.se
"""


# HERE IS DEFS
#
#
#


print("start bat file")

# Definitions

newline = "\n"
control_value = ""
start = "rem Adapted from Simple batch Render by Martin Olanders www.olanders.se"

# General code

# Find the blender instalation path and useres desktop path
Blender_file_start = os.path.dirname(bpy.app.binary_path) + "\\"
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
Bat_file_start = desktop + "\Simple Batch Render.bat"

Blender_files = "\\"

# print(Blender_file_start)
# print(Bat_file_start)


# Open file for writing and add value
def write_newline(file, inputvalue):
    # Write a new line in the file
    f1 = open(file, 'a')      # open for 'a'dding
    f1.write(inputvalue)
    f1.close()

# Check if the file is empty or not


def is_non_zero_file(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 3

# Check if input empty or not


def check_not_empty(value):
    if value == "":
        value = "true"
        return (value)
    else:
        return()  # False

# Check if blender.exe file exists in Blender start path


def check_valid_blender_dir(filepath_dir):
    # get list of all files in directory
    file_list = sorted(os.listdir(filepath_dir))
    if 'blender.exe' in file_list:
        return filepath_dir
    else:
        return ()  # False Blender not exits


# Check if file exists in filepath
# input Filpath dir and filename
def check_file_exist_in_dir(filepath, name_bat_file):
    # get list of all files in directory
    file_list = sorted(os.listdir(filepath))
    if name_bat_file in file_list:
        return filepath
    else:
        return ()  # False bat file not saved


# Check if bat file include blank spaces
def check_file_spaces(filename):
    # get list of all files in directory
    filename_only = os.path.basename(filename)
    if ' ' in filename_only:
        return ()  # False

    else:
        return filename


# Check if the bat file and Blender dir is OK
def check_bat_file_type(fpath, bpath):
    #bat_file_name_only = os.path.basename(fpath)
    if fpath[-4:] == ".bat":
        if check_valid_blender_dir(bpath):
            return fpath
            # if check_file_spaces(fpath):
            # return fpath
            # else:
            # return ()
        else:
            return ()
    else:
        return ()

# Check if the bat file only is OK


def check_bat_file_type_only(fpath):

    if fpath[-4:] == ".bat":
        return fpath
        # if check_file_spaces(fpath):
        # return fpath
        # else:
        # return ()
    else:
        return ()

# Check if render frames is ok strat value needs to be a number and end valeu also.


def check_render_frames(value_start, value_end):
    if value_start.isdigit():
        if value_end.isdigit():
            if value_end >= value_start:
                return()
            else:
                return "End frame is to low"
        else:
            return "End frame is not a number"
    else:
        return "Start frame is not a number"

# END general code

# Write the files


def main_writes_bat_file(context):
    # Write bat file of current file
    filelocation = bpy.data.filepath
    filename = bpy.path.basename(bpy.context.blend_data.filepath)
    blender_file_path = context.scene.blender_path
    batfile_path = context.scene.bat_file_path

    Description = newline + "rem Filename:" + filename + "     Start render frame:" + \
        context.scene.my_string_prop_start + \
        "   End render frame:" + context.scene.my_string_prop_end

    remove_filename = len(filelocation) - len(filename)
    value_start = 'cd ' + filelocation[:remove_filename]  # blender_file_path

    #value = 'blender -b "' + filelocation + '" -s ' + context.scene.my_string_prop_start + ' -e ' + context.scene.my_string_prop_end + ' -a'
    value = 'bpsrender ' + str(filelocation) + \
        ' -w ' + str(context.scene.Cores)

    if check_bat_file_type(batfile_path, blender_file_path):
        if is_non_zero_file(batfile_path):
            # Open the file for writing description
            write_newline(batfile_path, Description)
            # Open the file for new line
            write_newline(batfile_path, newline)
            # Open the file for writing command
            write_newline(batfile_path, value)
            # Open the file for new line
            write_newline(batfile_path, newline)

        else:
            f1 = open(batfile_path, 'a')      # open for 'a'dding
            f1.write(start)
            f1.close()
            # Open the file for new line
            write_newline(batfile_path, newline)
            write_newline(batfile_path, value_start)
            # Open the file for new line
            write_newline(batfile_path, newline)
            # Open the file for writing description
            write_newline(batfile_path, Description)
            # Open the file for new line
            write_newline(batfile_path, newline)
            # Open the file for writing command
            write_newline(batfile_path, value)
            # Open the file for new line
            write_newline(batfile_path, newline)


# Erase content in the file
def main_erase_file_info(context):
    # Write bat file of current file
    filelocation = bpy.data.filepath
    filename = bpy.path.basename(bpy.context.blend_data.filepath)
    batfile_path = context.scene.bat_file_path
    blender_file_path = context.scene.blender_path

    remove_filename = len(filelocation) - len(filename)
    value = 'cd ' + filelocation[:remove_filename]  # blender_file_path

    if check_bat_file_type(batfile_path, blender_file_path):
        f1 = open(batfile_path, 'w')      # open for 'w'riting
        f1.write(start)
        f1.close()

        # Open the file for new line
        write_newline(batfile_path, newline)
        write_newline(batfile_path, value)
        # Open the file for new line
        write_newline(batfile_path, newline)


# Open file in Notepad
def main_open_file_in_notepad(context):
    batfile_path = context.scene.bat_file_path
    bat_file_pathdir = os.path.dirname(batfile_path)
    bat_file_pathname = os.path.basename(batfile_path)

    if is_non_zero_file(batfile_path):
        if check_file_exist_in_dir(bat_file_pathdir, bat_file_pathname):
            if check_bat_file_type_only(batfile_path):

                bat_file_pathname = os.path.basename(batfile_path)
                bat_file_pathdir = os.path.dirname(batfile_path)
                bat_file_pathdir = bat_file_pathdir.replace("\\", "\\\\")
                bat_file_pathdir = bat_file_pathdir + '\\\\'
                stop_cmd = "/exit"
                os.chdir(bat_file_pathdir)
                start_command_for_dos = 'start cmd /c  C:\\Windows\\notepad.exe ' + \
                    bat_file_pathdir + bat_file_pathname
                os.system(start_command_for_dos)

# Start bat file


def main_start_bat_file(context):
    # Start bat file in new dos window
    filename = bpy.path.basename(bpy.context.blend_data.filepath)
    batfile_path = context.scene.bat_file_path

    if is_non_zero_file(batfile_path):
        if check_bat_file_type_only(batfile_path):

            bat_file_pathname = os.path.basename(batfile_path)
            bat_file_pathdir = os.path.dirname(batfile_path)

            bat_file_pathdir = bat_file_pathdir.replace("\\", "\\\\")
            bat_file_pathdir = bat_file_pathdir + '\\\\'

            os.chdir(bat_file_pathdir)
            start_command_for_dos = 'start cmd /c ' + '"' + bat_file_pathname + '"'
            os.system(start_command_for_dos)


# Start bat file and shut down computer after 5 minutes
def main_start_bat_file_shutdown(context):
    # Start bat file in new dos window, run and the shutdown
    filename = bpy.path.basename(bpy.context.blend_data.filepath)
    batfile_path = context.scene.bat_file_path

    if is_non_zero_file(batfile_path):
        if check_bat_file_type_only(batfile_path):

            value = "TIMEOUT /T 300"
            value_shutdown = "shutdown -s"
            bat_file_pathname = os.path.basename(batfile_path)
            bat_file_pathdir = os.path.dirname(batfile_path)

            bat_file_pathdir = bat_file_pathdir.replace("\\", "\\\\")
            bat_file_pathdir = bat_file_pathdir + '\\\\'

            bat_shutdown_file = batfile_path.replace(".bat", "_shut_down.bat")
            bat_shutdown_file = bat_shutdown_file.replace("\\", "\\\\")

            batfile_path = batfile_path.replace("\\", "\\\\")

            # Make a copy of the file
            shutil.copy2(batfile_path, bat_shutdown_file)

            bat_shutdown_file = os.path.basename(bat_shutdown_file)

            # Open the file for new line
            write_newline(bat_shutdown_file, newline)
            write_newline(bat_shutdown_file, value)

            write_newline(bat_shutdown_file, newline)
            write_newline(bat_shutdown_file, value_shutdown)

            os.chdir(bat_file_pathdir)
            start_command_for_dos = 'start cmd /c ' + '"' + bat_shutdown_file + '"'
            os.system(start_command_for_dos)

# Add many files from teh selected folder and add them to the batch render files


def main_add_from_folder(context):
    # the folder whrer to find the files
    folder = context.scene.add_folder_path
    #print (folder)

    # get list of all files in directory
    file_list = sorted(os.listdir(folder))
    # get a list of files ending in 'blend'
    obj_list = [item for item in file_list if item.endswith('.blend')]
    # loop through the strings in obj_list and add the files to the scene
    for item in obj_list:
        path_to_file = os.path.join(folder, item)

        # print(path_to_file)
        # print("\n")

        filelocation = path_to_file
        filename = bpy.path.basename(path_to_file)
        blender_file_path = context.scene.blender_path
        batfile_path = context.scene.bat_file_path

        Description = newline + "rem Filename:" + filename + "     Start render frame:" + \
            context.scene.my_string_prop_start + \
            "   End render frame:" + context.scene.my_string_prop_end

        value_start = 'cd ' + blender_file_path

        value = 'blender -b "' + filelocation + '" -s ' + \
            context.scene.my_string_prop_start + ' -e ' + \
                context.scene.my_string_prop_end + ' -a'

        if check_bat_file_type(batfile_path, blender_file_path):
            if is_non_zero_file(batfile_path):
                # Open the file for writing description
                write_newline(batfile_path, Description)
                # Open the file for new line
                write_newline(batfile_path, newline)
                # Open the file for writing command
                write_newline(batfile_path, value)
                # Open the file for new line
                write_newline(batfile_path, newline)

            else:
                f1 = open(batfile_path, 'a')      # open for 'a'dding
                f1.write(start)
                f1.close()
                # Open the file for new line
                write_newline(batfile_path, newline)
                write_newline(batfile_path, value_start)
                # Open the file for new line
                write_newline(batfile_path, newline)
                # Open the file for writing description
                write_newline(batfile_path, Description)
                # Open the file for new line
                write_newline(batfile_path, newline)
                # Open the file for writing command
                write_newline(batfile_path, value)
                # Open the file for new line
                write_newline(batfile_path, newline)


# HERE ARE TEH Classes


class writes_bat_file(bpy.types.Operator):
    """Writes a BAT file for this blend file"""
    bl_idname = "vsepic.writes_bat_file"
    bl_label = "Add render to queue"

    def execute(self, context):
        main_writes_bat_file(context)
        return {'FINISHED'}


class erase_file_info(bpy.types.Operator):
    """Erase content in file"""
    bl_idname = "vsepic.erase_file_info"
    bl_label = "Remove all renders from queue"

    def execute(self, context):
        main_erase_file_info(context)
        return {'FINISHED'}


class open_file_in_notepad(bpy.types.Operator):
    """Open file in Notepad"""
    bl_idname = "vsepic.open_file_in_notepad"
    bl_label = "Open file in Notepad"

    def execute(self, context):
        main_open_file_in_notepad(context)
        return {'FINISHED'}


class start_bat_file(bpy.types.Operator):
    """Starts  Simple Batch Render """
    bl_idname = "vsepic.start_bat_file"
    bl_label = "Start Batch Render"

    def execute(self, context):
        main_start_bat_file(context)
        return {'FINISHED'}


class start_bat_file_shutdown(bpy.types.Operator):
    """Start Simple Batch Render file and shutdown the computer after 5 minutes"""
    bl_idname = "myops.start_bat_file_shutdown"
    bl_label = "Batch Render and shutdown"

    def execute(self, context):
        main_start_bat_file_shutdown(context)
        return {'FINISHED'}


class add_from_folder(bpy.types.Operator):
    """Add many blend files from the selected folder"""
    bl_idname = "myops.add_from_folder"
    bl_label = "Add all blend files from the selected folder"

    def execute(self, context):
        main_add_from_folder(context)
        return {'FINISHED'}


'''
class Make_Bat_Meny(bpy.types.Panel):
    """Creates custom panel in the Viewport toolbar"""
    bl_context = 'render'
    bl_label = "Simple Batch Render"
    bl_idname = "OBJECT_PT_Shortcut_meny"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    bl_category = "Make Bat file"

    def draw(self, context):
        layout = self.layout

        # Make BAT file
        row = layout.row()
        row.operator("myops.writes_bat_file")

        col = self.layout.column(align=True)
        col.prop(context.scene, "my_string_prop_start")

        col = self.layout.column(align=True)
        col.prop(context.scene, "my_string_prop_end")

        layout = self.layout
        col = layout.column()
        col.prop(context.scene, "blender_path")

        layout = self.layout
        col = layout.column()
        col.prop(context.scene, "bat_file_path")

        # Open file in Notepad
        row = layout.row()
        row.operator("myops.open_file_in_notepad")

        # StartBAT file
        row = layout.row()
        row.operator("myops.start_bat_file")

        # StartBAT file and shutdown
        row = layout.row()
        row.operator("myops.start_bat_file_shutdown")

        row = layout.row()

        # Check start and end frame is ok
        if check_not_empty(context.scene.my_string_prop_start):

            row.label(text="Set Start frame", icon='INFO')
            row = layout.row()
        if check_not_empty(context.scene.my_string_prop_end):

            row.label(text="Set Endframe", icon='INFO')
            row = layout.row()

        if check_render_frames(context.scene.my_string_prop_start, context.scene.my_string_prop_end):
            row.label(text=check_render_frames(
                context.scene.my_string_prop_start, context.scene.my_string_prop_end), icon='ERROR')
            row = layout.row()

        # Check the blender start path is ok
        if check_not_empty(context.scene.blender_path):

            row.label(text="Set Blender start path", icon='INFO')
            row = layout.row()

        else:
            if check_file_exist_in_dir(context.scene.blender_path, 'blender.exe'):
                row = layout.row()
            else:
                row.label(
                    text="Warning: No blender.exe found in start path", icon='ERROR')
                row = layout.row()

        # Check the bat file is right
        if check_not_empty(context.scene.bat_file_path):
            row.label(text="Set bat file path and name", icon='INFO')
        else:
            if check_bat_file_type_only(context.scene.bat_file_path):
                row.label()
            else:
                row.label(
                    text="Warning: File name for file not ending with .bat", icon='ERROR')
                row = layout.row()

        # add many files from the same folder
        row = layout.row()
        row.operator("myops.add_from_folder")

        layout = self.layout
        col = layout.column()
        col.prop(context.scene, "add_folder_path")

        # Erase bat file content
        row = layout.row()
        row = layout.row()
        row.operator("myops.erase_file_info")
'''


def register():
    # bpy.utils.register_class(writes_bat_file)

    # bpy.utils.register_class(start_bat_file)

    # bpy.utils.register_class(open_file_in_notepad)

    # bpy.utils.register_class(start_bat_file_shutdown)

    # bpy.utils.register_class(Make_Bat_Meny)

    # bpy.utils.register_class(erase_file_info)

    # bpy.utils.register_class(add_from_folder)
    '''
    bpy.types.Scene.blender_path = bpy.props.StringProperty(
        name="Blender start path",
        #default = "C:\\Blender\\blender-2.78c-windows64\\",
        default=Blender_file_start,
        description="Define the path where Blender.exe is located",
        subtype='DIR_PATH'

    )
    '''
    bpy.types.Scene.my_string_prop_start = bpy.props.StringProperty(
        name="Start frame",
        description="Set start frame to render",
        default="0001"
    )

    bpy.types.Scene.my_string_prop_end = bpy.props.StringProperty(
        name="End frame",
        description="Set last frame to render or equal to start to only render one frame",
        default="0001"
    )
    bpy.types.Scene.bat_file_path = bpy.props.StringProperty(
        name="Save bat file to",
        default=Bat_file_start,
        description="Define where to save the bat file",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.add_folder_path = bpy.props.StringProperty(
        name="Folder with blend files",
        default=Blender_files,
        description="Where the blend files is located",
        subtype='DIR_PATH'
    )


def unregister():
    bpy.utils.unregister_class(writes_bat_file)

    bpy.utils.unregister_class(start_bat_file)

    bpy.utils.unregister_class(open_file_in_notepad)

    bpy.utils.unregister_class(start_bat_file_shutdown)

    bpy.utils.unregister_class(Make_Bat_Meny)

    bpy.utils.unregister_class(erase_file_info)

    del bpy.types.Scene.my_string_prop_start
    del bpy.types.Scene.my_string_prop_end

    del bpy.types.Scene.blender_path

    del bpy.types.Scene.bat_file_path

    bpy.utils.unregister_class(add_from_folder)


if __name__ == "__main__":
    register()
