

import bpy


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
