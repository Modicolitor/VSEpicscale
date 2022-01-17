import bpy
from operator import attrgetter
import ntpath
from .Simple_Batch_Render import *
from .vsepicprops import VSEpicPropertyGroup
# from .vsepicprops import VSEpicStabTrack
from .vsepicprops import VSEpicTrackCol, TrackElement


from bpy.types import Scene, MovieClip
import sys


class BE_OT_AddTransformStrip(bpy.types.Operator):
    bl_idname = "object.be_ot_addtransformstrip"
    bl_label = "BE_OT_AddTransformStrip"

    @classmethod
    def poll(cls, context):
        seq = context.scene.sequence_editor.active_strip
        if seq != None:
            if seq.type == 'IMAGE':
                return True
        return False

    def execute(self, context):
        data = bpy.data

        seq = context.scene.sequence_editor.active_strip

        # find start start and end frame
        start_frame = seq.frame_start
        duration = seq.frame_final_duration
        end_frame = seq.frame_start + seq.frame_final_duration
        filename = seq.strip_elem_from_frame(
            context.scene.frame_current).filename

        filepath = seq.directory + "\\" + filename

        # load pic in blender

        bpy.ops.image.open(filepath=filepath, directory=seq.directory, files=[
                           {"name": filename}], relative_path=True, show_multiview=False)

        pic_width = data.images[filename].size[0]
        pic_height = data.images[filename].size[1]

        bpy.ops.sequencer.effect_strip_add(
            type='TRANSFORM', frame_start=start_frame, frame_end=end_frame)

        transformStrip = context.scene.sequence_editor.active_strip

        r_height = context.scene.render.resolution_y
        r_width = context.scene.render.resolution_x
        # if pic_height >= pic_width:
        transformStrip.scale_start_x = pic_width/r_width
        transformStrip.scale_start_y = pic_height/r_height
        # else:
        #    transformStrip.scale_start_x = pic_width/r_width
        #    transformStrip.scale_start_y = pic_height/r_height
        return {'FINISHED'}


bpy.types.Scene.PicScalefactor = bpy.props.FloatProperty(default=1)
bpy.types.Scene.StabBool = bpy.props.BoolProperty(default=True)
bpy.types.Scene.Cores = bpy.props.IntProperty(default=4)
bpy.types.Scene.blender_path = bpy.props.StringProperty(
    name="Blender start path",
    # default = "C:\\Blender\\blender-2.78c-windows64\\",
    default=Blender_file_start,
    description="Define the path where Blender.exe is located",
    subtype='DIR_PATH')
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


class BE_OT_ScaleAdPicture(bpy.types.Operator):
    bl_idname = "object.be_ot_scaleadpicture"
    bl_label = "BE_OT_ScaleAdPicture"

    @ classmethod
    def poll(cls, context):
        seq = context.scene.sequence_editor.active_strip
        if seq != None:
            if seq.type == 'TRANSFORM':
                return True
        return False

    def execute(self, context):

        seq = context.scene.sequence_editor.active_strip

        seq.scale_start_x *= context.scene.PicScalefactor
        seq.scale_start_y *= context.scene.PicScalefactor

        return {'FINISHED'}


def delete_strips(context):
    selection = context.selected_sequences
    # if self.is_removing_transitions and bpy.ops.power_sequencer.transitions_remove.poll():
    #    bpy.ops.power_sequencer.transitions_remove()
    bpy.ops.sequencer.delete()

    # report_message = "Deleted " + str(len(selection)) + " sequence"
    # report_message += "s" if len(selection) > 1 else ""
    # self.report({"INFO"}, report_message)
    return {"FINISHED"}


class BE_OT_SceneStripWStab(bpy.types.Operator):
    bl_idname = "object.be_ot_scenestripwstab"
    bl_label = "BE_OT_SceneStripWStab"

    move_to_first_frame: bpy.props.BoolProperty(
        name="Move to First Frame",
        description="The strips will start at frame 1 on the new scene",
        default=True,
    )

    @ classmethod
    def poll(cls, context):
        return context.selected_sequences

    def execute(self, context):
        start_scene_name = context.scene.name

        if len(context.selected_sequences) != 0:
            selection = context.selected_sequences[:]
            selection_start_frame = min(
                selection, key=attrgetter("frame_final_start")
            ).frame_final_start
            selection_start_channel = min(
                selection, key=attrgetter("channel")).channel

            # information about movie file

            filepath = context.selected_sequences[0].filepath
            # Create new scene for the scene strip
            bpy.ops.scene.new(type="FULL_COPY")

            context.window.scene.name = context.selected_sequences[0].name
            new_scene_name = context.window.scene.name

            # after full copy also unselected strips are in the sequencer... Delete those strips
            bpy.ops.sequencer.select_all(action="INVERT")
            # bpy.ops.power_sequencer.delete_direct()
            print('alive')
            bpy.ops.sequencer.delete()
            print('alive')

            # um sequence_editor.sequences_all["DSC_1923_OpenMaryPan.MP4"].frame_offset_start nach hinten
            # oder
            # sequence_editor.sequences_all["DSC_1923_OpenMaryPan.MP4"].frame_start = 0

            frame_offset = selection_start_frame - 1
            for s in context.sequences:
                try:
                    s.frame_start = 0  # frame_offset
                    context.scene.frame_current = s.frame_offset_start
                except Exception:
                    continue
            bpy.ops.sequencer.select_all()
            bpy.ops.power_sequencer.preview_to_selection()

            # Back to start scene
            bpy.context.window.scene = bpy.data.scenes[start_scene_name]

            bpy.ops.power_sequencer.delete_direct()
            bpy.ops.sequencer.scene_strip_add(
                frame_start=selection_start_frame, channel=selection_start_channel, scene=new_scene_name
            )
            scene_strip = context.selected_sequences[0]

        # scene_strip.use_sequence = True
            if context.scene.StabBool:
                self.StabOption(context, start_scene_name,
                                new_scene_name, filepath)
        return {"FINISHED"}

    def StabOption(self, context, start_scene_name, new_scene_name, filepath):
        movieFilePath = filepath

        print("stab should start")
        bpy.context.window.scene = bpy.data.scenes[new_scene_name]

        # parsing filename
        filepath, filename = ntpath.split(filepath)
        moviefile = filepath + filename
        print(
            f"file {filepath} filename {filename} moviefile {moviefile} movieFilePath {movieFilePath} ")
        # bpy.ops.clip.open(directory=filepath, files=[
        #                  {"name": filename}], relative_path=True)

        # moviefile = filepath + filename

        S = bpy.context.scene
        mc = bpy.data.movieclips.load(movieFilePath)
        context.scene.epicmovieclip = mc
        print(moviefile)
        compstabnodes(context, mc)


def compstabnodes(context, movieclip):

    context.scene.use_nodes = True
    active = context.scene.node_tree.nodes.active

    node_tree = context.scene.node_tree
    nodes = node_tree.nodes

    links = node_tree.links

    for node in nodes:
        nodes.remove(node)

    data = bpy.data

    nodemov = nodes.new('CompositorNodeMovieClip')  # glossyshader machen
    nodemov.location = (-1200, 000)

    nodescale = nodes.new('CompositorNodeScale')  # glossyshader machen
    nodescale.location = (-900, 000)
    nodescale.space = 'RENDER_SIZE'

    nodestab = nodes.new('CompositorNodeStabilize')  # glossyshader machen
    nodestab.location = (-600, 000)

    nodecomp = nodes.new('CompositorNodeComposite')  # glossyshader machen
    nodecomp.location = (-000, 000)

    if movieclip != None:
        nodestab.clip = movieclip  # data.movieclips[filename]
        nodemov.clip = movieclip  # data.movieclips[filename]

    # link basic OceanMaterial zum ersen Mix shader
    links.new(nodemov.outputs[0],
              nodescale.inputs[0])
    links.new(nodescale.outputs[0],
              nodestab.inputs[0])
    links.new(nodestab.outputs[0],
              nodecomp.inputs[0])

    if movieclip != None:
        bpy.ops.workspace.append_activate(idname='MotionTracking')
        bpy.context.area.ui_type = 'CLIP_EDITOR'

        context.space_data.clip = movieclip  # data.movieclips[filename]


class BE_OT_CorrectFPSOperator(bpy.types.Operator):
    '''Takes a selected audio and an active Video and corrects the time difference with a speed control'''
    bl_idname = "object.correctfps"
    bl_label = "BE_OT_CorrectFPS"

    @ classmethod
    def poll(cls, context):

        return len(context.selected_sequences) == 2 and context.scene.sequence_editor.active_strip.type == 'MOVIE'

    def execute(self, context):

        acseq = context.scene.sequence_editor.active_strip

        selected_sequences = context.selected_sequences[:]
        for se in selected_sequences:
            if se != acseq:
                selseq = se
            se.select = False

        frameend = selseq.frame_final_duration

        acseq.select = True
        bpy.ops.sequencer.effect_strip_add(
            type='SPEED', frame_start=1, frame_end=26)

        acseq.frame_final_duration = frameend

        return {'FINISHED'}


class BE_PT_pciscaleUI(bpy.types.Panel):
    bl_label = 'MuseumsLove'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'VSEPicScale'

    def draw(self, context):

        data = bpy.data

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()
        row = layout.row()

        subcol = col.column()
        seq = context.scene.sequence_editor.active_strip

        subcol.label(text="Make Adjusted Transform strip")
        subcol.operator("object.be_ot_addtransformstrip",
                        text="Add Transform Strip", icon="PLUS")  # zeige button an

        subcol = col.column()
        subcol.label(text="Adjust pic scale (factor of transform)")
        subcol.operator("object.be_ot_scaleadpicture",
                        text="Adjust Transform Strip", icon="PLUS")
        subcol.prop(context.scene, "PicScalefactor")

        if seq != None:
            if seq.type == 'TRANSFORM':
                subcol.label(text="Position")
                subcol.prop(seq, "translate_start_x")
                subcol.prop(seq, "translate_start_y")

        subcol.operator("object.correctfps", text="Correct FPS")
        subcol = col.column()
        subcol.operator("object.be_ot_scenestripwstab",
                        text="SceneStrip", icon="PLUS")

        subcol = col.column()
        subcol.label(text="Quick Render")
        subcol.prop(context.scene, "bat_file_path", text="Save bat file to: ")
        subcol.prop(context.scene, "Cores", text="Number of Corse")
        subcol.operator("vsepic.writes_bat_file")
        subcol.operator("vsepic.erase_file_info")
        subcol.operator("vsepic.open_file_in_notepad")
        subcol.operator("vsepic.start_bat_file")


bpy.types.Scene.epicmovieclip = bpy.props.PointerProperty(
    name="Movie", type=MovieClip)


def initialize_addon(context):

    # bpy.types.Scene.vsepic_trackscol = bpy.props.PointerProperty(
    #    type=VSEpicTrackCol)
    bpy.types.Scene.vsepicprops = bpy.props.PointerProperty(
        type=VSEpicPropertyGroup)

    clip = get_clip(context)
    # generate TrackCol object auf dem Pointer
    # print(context.scene.trackscollection.tracks)

    context.scene.vsepicprops.trackscol.update(context, clip.tracking.tracks)

    # bpy.types.MovieClip.vsetsstab = bpy.props.PointerProperty(
    #    type=VSEpicStabTrack)

    # bpy.props.PointerProperty(
    #    type=VSEpicStabTrack)


def get_clip(context):
    # if context.scene.epicmovieclip != None: ##!!!!!!!!!!!!!!!!!!!hier muss das besser werden

    clip = context.scene.epicmovieclip
    return clip


class BE_OT_Initialize(bpy.types.Operator):
    bl_idname = "scene.initializeaddon"
    bl_label = "BE_OT_initializeaddon"

    def execute(self, context):

        initialize_addon(context)
        return {'FINISHED'}


class BE_OT_CompStabOperator(bpy.types.Operator):
    bl_idname = "object.compstaboperator"
    bl_label = "BE_OT_CompStabOperator"

    def execute(self, context):

        if context.scene.epicmovieclip == None:
            compstabnodes(context, None)
        else:
            compstabnodes(context, context.scene.epicmovieclip)

        bpy.context.area.ui_type = 'CompositorNodeTree'
        return {'FINISHED'}


class BE_PT_VSECompUI(bpy.types.Panel):
    bl_label = 'MuseumsLove'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'VSEPicScale'

    def draw(self, context):

        data = bpy.data

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()
        row = layout.row()

        subcol = col.column()

        subcol.template_ID(context.scene, "epicmovieclip", open="clip.open")
        subcol.operator("object.compstaboperator",
                        text="Generate Stabilizing Setup")


class BE_PT_VSEStabUI(bpy.types.Panel):
    bl_label = 'MuseumsLove'
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'VSEPicScale'

    def draw(self, context):

        data = bpy.data

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0,
                                even_columns=False, even_rows=False, align=True)
        col = flow.column()
        row = layout.row()

        subcol = col.column()

        if hasattr(context.scene, "vsepicprops"):
            vsepicprops = context.scene.vsepicprops
            subcol.template_ID(
                context.scene, "epicmovieclip", open="clip.open")

            subcol.operator("object.multipointstab",
                            text="Animate Stabilization")
            subcol.prop(vsepicprops, "target_scale")
            subcol.prop(vsepicprops, "offset_x")
            subcol.prop(vsepicprops, "offset_y")
            subcol.prop(vsepicprops, "mikrocorrect_x")
            subcol.prop(vsepicprops, "mikrocorrect_y")
            subcol.prop(vsepicprops, "const_x")
            subcol.prop(vsepicprops, "const_y")
            subcol.prop(vsepicprops, "const_slope_x")
            subcol.prop(vsepicprops, "const_slope_y")
            subcol.prop(vsepicprops, "sel_slope")
            subcol.prop(vsepicprops, "slope_factor")
            if hasattr(vsepicprops.trackscol, "ui_track_list"):
                subcol.prop(vsepicprops.trackscol, "ui_track_list")
                trackindex = int(vsepicprops.trackscol.ui_track_list)
                subcol.prop(
                    vsepicprops.trackscol.tracks[trackindex], 'posstab')
                subcol.prop(
                    vsepicprops.trackscol.tracks[trackindex], 'rotstab')

        else:
            subcol.operator("scene.initializeaddon",
                            text="Initialize")
