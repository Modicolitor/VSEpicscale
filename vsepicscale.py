bl_info = {  # für export als addon
    "name": "VSEPicScale",
    "author": "Modicolitor",
    "version": (0, 1),
    "blender": (2, 83, 0),
    "location": "SEQUENCE_EDITOR > Tools",
    "description": "Scales pictures automatically by adding and adjusting a transform strip",
    "category": "Object"}


import bpy 



class BE_OT_AddTransformStrip(bpy.types.Operator):
    bl_idname = "object.be_ot_addtransformstrip"
    bl_label = "BE_OT_AddTransformStrip"


    def execute(self, context):
        data = bpy.data

        seq = context.scene.sequence_editor.active_strip
        print("Doing")
        
        
        
        
        #### find start start and end frame 
        start_frame = seq.frame_start
        duration = seq.frame_final_duration
        end_frame = seq.frame_start + seq.frame_final_duration
        
        filepath = seq.directory + "\\" + seq.filename
        
        ###load pic in blender

        bpy.ops.image.open(filepath=filepath, directory=seq.directory, files=[{"name":seq.filename}], relative_path=True, show_multiview=False)
        
        pic_width = data.images[seq.filename].size[1]
        pic_height = data.images[seq.filename].size[1]



        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=start_frame, frame_end=end_frame)

        transformStrip = context.scene.sequence_editor.active_strip


        transformStrip.scale_start_x = 1 
        transformStrip.scale_start_y = pic_width/pic_height

        
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
       
        subcol.label(text="Adjust")
        subcol.operator("object.be_ot_addtransformstrip", text="Add Coupling", icon="PLUS")  # zeige button an
        


classes = (
    BE_OT_AddTransformStrip,
    BE_PT_pciscaleUI
    )
register, unregister = bpy.utils.register_classes_factory(classes)