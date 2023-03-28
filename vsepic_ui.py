import bpy


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

        if hasattr(context.scene, "vsepicprops"):

            subcol = col.column()
            seq = context.scene.sequence_editor.active_strip

            #subcol.label(text="Make Adjusted Transform strip")
            # subcol.operator("object.be_ot_addtransformstrip",
            #                text="Add Transform Strip", icon="PLUS")  # zeige button an

            #subcol = col.column()
            #subcol.label(text="Adjust pic scale (factor of transform)")
            # subcol.operator("object.be_ot_scaleadpicture",
            #                text="Adjust Transform Strip", icon="PLUS")
            #subcol.prop(context.scene, "PicScalefactor")

            if seq != None:
                if seq.type == 'TRANSFORM':
                    subcol.label(text="Position")
                    subcol.prop(seq, "translate_start_x")
                    subcol.prop(seq, "translate_start_y")

            subcol.operator("object.correctfps", text="Correct FPS")
            subcol = col.column()
            subcol.operator("object.be_ot_scenestripwstab",
                            text="SceneStrip", icon="PLUS")
            subcol = col.box()
            subcol.operator("vsepic.markproblems",
                            text="Mark Problems", icon='BORDERMOVE')
            subcol.prop(context.scene.vsepicprops,
                        "show_error_marks", text='Toggle Marks')
            subcol.prop(context.scene.vsepicprops,
                        "check_coverage", text='Check Coverage')
            subcol.prop(context.scene.vsepicprops,
                        "check_blend_type", text='Check Blend Type')

            subcol = col.column()
            subcol.label(text="Quick Render")
            subcol.prop(context.scene, "bat_file_path",
                        text="Save bat file to: ")
            subcol.prop(context.scene, "Cores", text="Number of Corse")
            subcol.operator("vsepic.writes_bat_file")
            subcol.operator("vsepic.erase_file_info")
            subcol.operator("vsepic.open_file_in_notepad")
            subcol.operator("vsepic.start_bat_file")
            
            subcol = col.column()
            subcol.label(text="Save Visibility State")
            subcol.operator("sequencer.savevislist")
            subcol.operator("sequencer.applyvislist")
            
            
            
        else:
            subcol = col.column()
            subcol.operator("scene.initializeaddon",
                            text="Initialize")


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
            subcol.operator("vsepic.updatedata",
                            text="Update Data")
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

            if hasattr(vsepicprops.trackscol, "ui_comments"):
                for com in vsepicprops.trackscol.ui_comments:
                    subcol.label(text=com.comment)

            if hasattr(vsepicprops.trackscol, "ui_track_list"):
                if len(vsepicprops.trackscol.ui_track_list) != 0:
                    subcol.prop(vsepicprops.trackscol, "ui_track_list")
                    trackindex = int(vsepicprops.trackscol.ui_track_list)
                    subcol.prop(
                        vsepicprops.trackscol.tracks[trackindex], 'posstab')
                    subcol.prop(
                        vsepicprops.trackscol.tracks[trackindex], 'rotstab')

        else:
            subcol.operator("scene.initializeaddon",
                            text="Initialize")
