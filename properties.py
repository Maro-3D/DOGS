import bpy
from bpy.props import EnumProperty, BoolProperty, PointerProperty
from . import utils

def register():
    bpy.types.Scene.selected_armature = PointerProperty(
        name="Selected Armature",
        description="Armature of the avatar you want the performance statistics for",
        type=bpy.types.Armature,
        poll=utils.armature_items,
    )

    bpy.types.Scene.selected_collection = PointerProperty(
        name="Selected Export Collection",
        type=bpy.types.Collection,  # This defines the type of object we are selecting (Collection)
        poll=utils.collection_items
    )

    bpy.types.Scene.show_extra_armature_options = BoolProperty(
        name="Add Armature Menu",
        description="Toggle to show or hide extra armature creation options",
        default=False
    )

    bpy.types.Scene.device_mode = EnumProperty(
        name="Device Mode",
        description="Select Device Mode",
        items=[
            ('PC', "PC", "Displays the performance rating for VR running on a PC"),
            ('STANDALONE', "Standalone", "Displays the performance rating for VR running on a Standalone Headset"),
        ],
        default='PC'
    )


    bpy.types.Scene.rating_mode = EnumProperty(
        name="Rating Mode",
        description="Rating for",
        items=[
            ('SCENE', "Scene", "While rating the performance takes in to accout all visible objects in the current scene", 'SCENE_DATA',1),
            ('ARMATURE', "Armature", "While rating the performance takes in to accout only objects paranted to the selected avatar armature", 'ARMATURE_DATA',2)
        ],
        default='SCENE'
    )

    bpy.types.Scene.paint_through_mesh = bpy.props.BoolProperty(
        name="Paint Through Mesh",
        description="Enable or disable paint through mesh",
        default=False,
        update=lambda self, context: utils.update_brush_settings(context)
    )
    
def unregister():
    del bpy.types.Scene.selected_armature
    del bpy.types.Scene.show_extra_armature_options
    del bpy.types.Scene.device_mode
    del bpy.types.Scene.rating_mode
    del bpy.types.Scene.paint_through_mesh
    del bpy.types.Scene.selected_collection

    


