import bpy 

mod = bpy.context.active_object.modifiers.active
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