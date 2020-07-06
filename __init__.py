import bpy 
from .vsepicscale import BE_OT_AddTransformStrip
from .vsepicscale import BE_PT_pciscaleUI

bl_info = {  # für export als addon
    "name": "VSEPicScale",
    "author": "Modicolitor",
    "version": (0, 1),
    "blender": (2, 83, 0),
    "location": "SEQUENCE_EDITOR > Tools",
    "description": "Scales pictures automatically by adding and adjusting a transform strip",
    "category": "Object"}



classes = (
    BE_OT_AddTransformStrip,
    BE_PT_pciscaleUI,
    )

register, unregister = bpy.utils.register_classes_factory(classes)