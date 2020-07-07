

import bpy
from operator import attrgetter
import ntpath


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


class BE_OT_ScaleAdPicture(bpy.types.Operator):
    bl_idname = "object.be_ot_scaleadpicture"
    bl_label = "BE_OT_ScaleAdPicture"

    @classmethod
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


class BE_OT_SceneStripWStab(bpy.types.Operator):
    bl_idname = "object.be_ot_scenestripwstab"
    bl_label = "BE_OT_SceneStripWStab"

    move_to_first_frame: bpy.props.BoolProperty(
        name="Move to First Frame",
        description="The strips will start at frame 1 on the new scene",
        default=True,
    )

    @classmethod
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
            bpy.ops.power_sequencer.delete_direct()
            frame_offset = selection_start_frame - 1
            for s in context.sequences:
                try:
                    s.frame_start -= frame_offset
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
        print("stab should start")
        bpy.context.window.scene = bpy.data.scenes[new_scene_name]

        # parsing filename
        filepath, filename = ntpath.split(filepath)
        moviefile = filepath + filename
        print(f"file {filepath} filename {filename} moviefile {moviefile}")
        bpy.ops.clip.open(directory=filepath, files=[
                          {"name": filename}], relative_path=True)

        moviefile = filepath + filename
        print(moviefile)

        bpy.context.scene.use_nodes = True
        # compoistor node create node tree
        # C.scene.node_tree.nodes.new(

        active = context.scene.node_tree.nodes.active
        #mat = bpy.data.materials['AdvOceanMat']
        # macht einen Diffuseshader
        # mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        node_tree = context.scene.node_tree
        nodes = node_tree.nodes

        links = node_tree.links

        for node in nodes:
            nodes.remove(node)

        data = bpy.data
        # Ocean
        nodemov = nodes.new('CompositorNodeMovieClip')  # glossyshader machen
        nodemov.location = (-1200, 000)
        nodemov.clip = data.movieclips[filename]

        nodescale = nodes.new('CompositorNodeScale')  # glossyshader machen
        nodescale.location = (-900, 000)

        nodestab = nodes.new('CompositorNodeStabilize')  # glossyshader machen
        nodestab.location = (-600, 000)
        nodestab.clip = data.movieclips[filename]

        nodecomp = nodes.new('CompositorNodeComposite')  # glossyshader machen
        nodecomp.location = (-000, 000)

        # link basic OceanMaterial zum ersen Mix shader
        links.new(nodemov.outputs[0],
                  nodescale.inputs[0])
        links.new(nodescale.outputs[0],
                  nodestab.inputs[0])
        links.new(nodestab.outputs[0],
                  nodecomp.inputs[0])

        bpy.ops.workspace.append_activate(idname='MotionTracking')

        context.space_data.clip = data.movieclips[filename]


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

        subcol = col.column()
        subcol.operator("object.be_ot_scenestripwstab",
                        text="SceneStrip", icon="PLUS")
        subcol.prop(context.scene, "StabBool", text="Stabilizer")
