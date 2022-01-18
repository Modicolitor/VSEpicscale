import bpy
from .vsepicscale import BE_OT_AddTransformStrip
from .vsepicscale import BE_OT_ScaleAdPicture
from .vsepicscale import BE_PT_pciscaleUI
from .vsepicscale import BE_OT_SceneStripWStab

from .vsepicscale import BE_PT_VSECompUI
from .vsepicscale import BE_OT_CompStabOperator
from .vsepicscale import BE_OT_CorrectFPSOperator
from .vsepicscale import BE_OT_VSEpicUpdateData

from .vsepicscale import BE_PT_VSEStabUI
from .vsepicscale import BE_OT_Initialize

from .Simple_Batch_Render import writes_bat_file
from .Simple_Batch_Render import erase_file_info
from .Simple_Batch_Render import open_file_in_notepad
from .Simple_Batch_Render import start_bat_file

from .vse_stabilize import BE_OT_AnimateMultiPointStab

from .vsepicprops import VSEpicPropertyGroup
#from .vsepicprops import VSEpicStabTrack
from .vsepicprops import VSEpicTrackCol
from .vsepicprops import VSEpicTrackElement
from .vsepicprops import VSEpicSegement

bl_info = {  # für export als addon
    "name": "VSEPicScale",
    "author": "Modicolitor",
    "version": (0, 3),
    "blender": (2, 93, 0),
    "location": "SEQUENCE_EDITOR > Tools",
    "description": "Scales pictures automatically by adding and adjusting a transform strip",
    "category": "Object"}


classes = (
    BE_OT_AddTransformStrip,
    BE_PT_pciscaleUI,
    BE_OT_ScaleAdPicture,
    BE_OT_SceneStripWStab,
    writes_bat_file,
    erase_file_info,
    open_file_in_notepad,
    start_bat_file,
    BE_PT_VSECompUI,
    BE_OT_CompStabOperator,
    BE_OT_CorrectFPSOperator,
    BE_PT_VSEStabUI,
    BE_OT_AnimateMultiPointStab,
    BE_OT_VSEpicUpdateData,

    BE_OT_Initialize,
    # VSEpicStabTrack,
    VSEpicTrackElement,
    VSEpicSegement,
    VSEpicTrackCol,
    VSEpicPropertyGroup,

)

register, unregister = bpy.utils.register_classes_factory(classes)
