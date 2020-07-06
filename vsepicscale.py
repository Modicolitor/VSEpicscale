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
        return {'FINISHED'}


class BE_PT_pciscaleUI(Panel):
    bl_label = 'Attract'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Strip'

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