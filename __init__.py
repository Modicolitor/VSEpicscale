import bpy
from .vsepicscale import BE_OT_AddTransformStrip
from .vsepicscale import BE_OT_ScaleAdPicture
from .vsepic_ui import BE_PT_pciscaleUI
from .vsepicscale import BE_OT_SceneStripWStab

from .vsepic_ui import BE_PT_VSECompUI

from .vsepicscale import BE_OT_CompStabOperator
from .vsepicscale import BE_OT_CorrectFPSOperator
from .vsepicscale import BE_OT_VSEpicUpdateData

from .vsepic_ui import BE_PT_VSEStabUI
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
from .vsepicprops import VSEpicCommentElement
from .vsepicprops import VSEpicSegement
from .vsepicprops import VSEpicVISElement
from .vsepicscale import BE_OT_UpdateVisList
from .vsepicscale import BE_OT_ApplyVisList

from .vsepic_draw import BE_OT_MarkProblems

from .epic_nodes import BE_OT_CorrectAttributes
from .epic_nodes  import BE_PT_NodeEditorUi

bl_info = {
    "name": "VSEPicScale",
    "author": "Modicolitor",
    "version": (0, 5),
    "blender": (4, 0, 2),
    "location": "SEQUENCE_EDITOR > Tools",
    "description": "Scales pictures automatically by adding and adjusting a transform strip",
    "category": "Object"}


classes = (
    #BE_OT_AddTransformStrip,
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
    
    BE_PT_NodeEditorUi,
    BE_OT_Initialize,
    # VSEpicStabTrack,
    VSEpicTrackElement,
    VSEpicCommentElement,
    VSEpicSegement,
    VSEpicTrackCol,
    
    BE_OT_MarkProblems,
    VSEpicVISElement,
    BE_OT_UpdateVisList,
    BE_OT_ApplyVisList,
    VSEpicPropertyGroup,
    BE_OT_CorrectAttributes,
)

register, unregister = bpy.utils.register_classes_factory(classes)

# bpy.types.Scene.vsepicprops = bpy.props.PointerProperty(
#    type=VSEpicPropertyGroup)
