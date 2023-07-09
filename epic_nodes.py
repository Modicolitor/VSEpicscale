import bpy 


class BE_OT_CorrectAttributes(bpy.types.Operator):
    """Starts  Simple Batch Render"""
    bl_idname = "vsepic.corrattr"
    bl_label = "Select False Data type"

    def execute(self, context):
        
        mod = context.active_object.modifiers.active
        nodes = mod.node_group.nodes
        
        for node in nodes:
            if node.select:
                selnode = node
                break 
        
        #if selnode.type == 'INPUT_ATTRIBUTE': 
        name = selnode.inputs['Name'].default_value
        data_type = selnode.data_type 

        selnode.select   = False
           
        for node in nodes:
            if node.type == 'INPUT_ATTRIBUTE' or node.type == 'STORE_NAMED_ATTRIBUTE':
                if node.inputs['Name'].default_value == name:
                    if node.data_type != data_type:
                        node.select = True
            
        
        return {'FINISHED'}
    
    
           
            
class BE_PT_NodeEditorUi(bpy.types.Panel):
    bl_label = 'EpicNodes'
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

        
        subcol.operator("vsepic.corrattr")
        
        