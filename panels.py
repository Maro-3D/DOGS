import bpy
from bpy.types import Panel

from . import utils


# DOGS main panel
class DOGS_PT_panel(Panel):
    bl_label = "DOGS"
    bl_idname = "DOGS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DOGS'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        #needs to be fixed up next relese
        # ----------------- Export Avatar -----------------
        row = layout.row(align=True)
        row.scale_y = 2.0
        # Use the correct operator
        row.operator('export.simple_export', text="Export Avatar Collection", icon='EXPORT',)

        # Add the dropdown menu for colelctions with exporters
        layout.separator()
        row = layout.row(align=True)
        
        row.alignment = 'CENTER'
        row.prop(scene, 'selected_collection', text="Collection to export", icon="OUTLINER_COLLECTION")
        layout.separator()



# Panel for Mesh Stats of the avatar
class STATS_PT_panel(Panel):
    bl_label = "Stats"
    bl_idname = "STATS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DOGS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        selected_armature = scene.selected_armature

        if selected_armature:
            selected_armature_name = selected_armature.name
        else:
            selected_armature_name = None

        device_mode = scene.device_mode
        rating_mode = scene.rating_mode

        stats = utils.get_performance_stats(selected_armature_name, rating_mode)



        # ----------------- Avatar Armature -----------------

        # Add the dropdown menu for 'selected_armature'
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.prop(scene, 'selected_armature', text="Avatar Armature", icon="ARMATURE_DATA")
        
        # Add toggle button for additional options
        row.prop(scene, "show_extra_armature_options", text="", icon='DOWNARROW_HLT' if scene.show_extra_armature_options else 'RIGHTARROW')
       
        if scene.show_extra_armature_options:
            box = layout.box()
            box.label(text="Add Armatures", icon='OUTLINER_OB_ARMATURE')
            box.operator('add_armature.operator', text="Basic Humanoid", icon='ADD').armature_type = 'Basic'
            box.operator('add_armature.operator', text="Extended Humanoid", icon='ADD').armature_type = 'Extended'
            box.operator('add_armature.operator', text="Digitigrade Humanoid", icon='ADD').armature_type = 'Digitigrade'
        layout.separator()

        # ----------------- Rating Modes -----------------

        box = layout.box()
        row = box.row(align=True)
        
        row.label(text=f"Rating mode: ")
        row.prop(scene, 'device_mode', expand=True)

        

        row = box.row(align=True)

        row.label(text=f"Rating for: ")
        row.prop(scene, 'rating_mode', expand=True)

        box = box.box()

        #----------------- If no Armature -----------------

        if not selected_armature and rating_mode == 'ARMATURE':
            box.label(text="No Avatar Armature Selected!", icon="ERROR")
            return
        
        thresholds = utils.RATING_THRESHOLDS[device_mode]

        tri_icon = utils.get_icon(stats["tri_count"], [thresholds["Good"]["tri_count"], thresholds["Medium"]["tri_count"]])
        mat_icon = utils.get_icon(stats["material_count"], [thresholds["Good"]["material_count"], thresholds["Medium"]["material_count"]])
        bone_icon = utils.get_icon(stats["bone_count"], [thresholds["Good"]["bone_count"], thresholds["Medium"]["bone_count"]])
        skin_icon = utils.get_icon(stats["skinned_meshes"], [thresholds["Good"]["skinned_meshes"], thresholds["Medium"]["skinned_meshes"]])

        box.label(text=f"Triangls: {stats['tri_count']}", icon=tri_icon)
        box.label(text=f"Materials: {stats['material_count']}", icon=mat_icon)
        box.label(text=f"Bones: {stats['bone_count']}", icon=bone_icon)
        box.label(text=f"Skinned Meshs: {stats['skinned_meshes']}", icon=skin_icon)


        box = layout.box()
        rating = utils.get_rating(stats, device_mode)
        box.label(text=f"Rating: {rating}")

# Panel for Mesh Editing
class MESH_EDIT_PT_panel(Panel):
    bl_label = "Object & Mesh Editing"
    bl_idname = "MESH_EDIT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DOGS'
    bl_options = {'DEFAULT_CLOSED'}

    # Define the panel UI layout
    def draw(self, context):
        layout = self.layout
        obj = context.object
        

        # ----------------- Object -----------------
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Object", icon="META_CUBE")
        box = layout.box()
        sub = box.row(align=True)

        sub.operator("object.distribute_along_axis_with_mirrors", text="Distribute Selected Objects", icon="GEOMETRY_NODES")    

        
        # ----------------- Mesh -----------------    
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Mesh", icon="MESH_DATA")

        box = layout.box()
        sub = box.row(align=True)
        
        sub.label(text="Join Mesh:")
        sub.operator("object.join", text="Selected")
        sub.operator("object.join_visible", text="Visible")

        sub = box.row(align=True)
        sub.label(text="Separate By:")

        sub.scale_x = 0.96
        sub.operator("mesh.separate_by_selection", text="Selection", icon="FACESEL")

        sub = box.row()
        sub.operator("mesh.separate_by_loose_parts", text="Loose Parts", icon="STICKY_UVS_DISABLE")
        sub.operator("mesh.separate_by_materials", text="Materials", icon="MATERIAL")
        
        box = layout.box()
        sub = box.row(align=True)
        sub.label(text="Find:", icon="BORDERMOVE")
        sub.operator("object.show_ngons", text="Ngons")
        sub.operator("object.show_triangles", text="Triangels")
        
        
        # ----------------- Normals -----------------
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.label(text="Normals", icon="NORMALS_FACE")
        box = layout.box()
        sub = box.row(align=True)

        sub.label(text="Normals:")
        sub.operator("mesh.normals_make_consistent", text="Recalculate").inside = False
        sub.operator("mesh.flip_normals", text="Flip")

        overlay = context.space_data.overlay
        face_orientation_icon = "HIDE_OFF" if overlay.show_face_orientation else "HIDE_ON"
        sub.prop(overlay, "show_face_orientation", text="", icon=face_orientation_icon)

        box = layout.box()
        sub = box.row(align=True)
        sub.label(text="Shade:")
        sub.operator("object.shade_smooth", text="Smooth")
        sub.operator("object.shade_auto_smooth", text="Auto")
        sub.operator("object.shade_flat", text="Flat")
        sub.operator("mesh.customdata_custom_splitnormals_clear", text="", icon="X")
            

class WEIGHTPAINT_BONE_MODES_PT(bpy.types.Panel):
    """Panel with toggles for quickly switching between Weight Paint and Bone Edit modes"""
    bl_label = "Mode Toggles"
    bl_idname = "WEIGHTPAINT_BONE_MODES_PT"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DOGS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        overlay = context.space_data.overlay
        scene = context.scene
        tool_settings = context.scene.tool_settings

        # Weight Paint Mode Toggle
        if context.mode == 'PAINT_WEIGHT':
            row.operator("object.toggle_weight_paint_mode", text="Weight Mode", icon='RADIOBUT_ON').trigger_from_ui = True
            
            self.draw_weight_paint_mode_on(layout, overlay, scene, tool_settings, context)
        else:
            row.operator("object.toggle_weight_paint_mode", text="Weight Mode", icon='RADIOBUT_OFF').trigger_from_ui = True
            

        # Bone Pose Mode Toggle
        if context.mode == 'POSE':
            row.operator("object.toggle_pose_mode", text="Bone Mode", icon='RADIOBUT_ON')
            self.draw_bone_pose_mode_on(layout,context)
        else:
            row.operator("object.toggle_pose_mode", text="Bone Mode", icon='RADIOBUT_OFF')
            

        # Additional information if neither mode is active
        if context.mode not in {'POSE', 'PAINT_WEIGHT'}:
            self.draw_both_mode_off(layout)

    def draw_weight_paint_mode_on(self, layout, overlay, scene, tool_settings, context):
        obj = context.object
        if not obj:
            layout.label(text="No active object found.", icon="ERROR")
            return

        # Check if the object has an armature modifier
        armature = None
        for modifier in obj.modifiers:
            if modifier.type == 'ARMATURE':
                armature = modifier.object

        # Weight Paint Options
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Weight Paint Options", icon="WPAINT_HLT")

        box = layout.box()
        box.prop(overlay, "show_paint_wire", text="Show Wireframe")
        box.prop(overlay, "show_wpaint_contours", text="Show Weight Paint Contours")
        

        
        box = layout.box()
        box.prop(tool_settings, "use_auto_normalize", text="Auto Normalize Weights")
        box.prop(scene, "paint_through_mesh", text="Paint Through Mesh")
        box.prop(tool_settings.weight_paint, "use_group_restrict", text="Paint Only on Vertices in Group")

        if armature:
            # Armature-related options
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Weight Paint Functions", icon="MOD_VERTEX_WEIGHT")

            box = layout.box()
            
            #brush_mode = bpy.data.brushes["Add"].blend

            brush_mode = context.tool_settings.weight_paint.brush.blend


            box.operator("object.toggle_weight_brush_mode", text="Brush Mode: " + brush_mode, icon="BRUSH_DATA")
            box_row = box.row(align=True)
            box_row.operator("object.toggle_weight_value", text="Swap Weight", icon="UV_SYNC_SELECT")
            box_row = box.row(align=True)
            box_row.label(text="Fill with:", icon="IMAGE")
            box_row.scale_x = 0.6
            box_row.operator("object.assign_vertices_to_active_group", text="0").weight_value = 0.0
            box_row.operator("object.assign_vertices_to_active_group", text="1").weight_value = 1.0

           
            box = layout.box()
            box_row = box.row(align=True)
            box_row.operator("object.vertex_group_clean", text="Clean Vertex", icon="TRASH")
            box_row.operator("object.weight_gradient_operator", text="Spherical Gradient", icon="SURFACE_NCURVE")

            # Bone Settings
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Bone Settings", icon="GROUP_BONE")

            row = layout.row()
            box_row = row.row(align=True)

            box_row.prop(armature.pose, "use_mirror_x", text="Mirror Bone Pose in X Axis", icon="OUTLINER_DATA_ARMATURE")
            box_row.operator('object.reset_pose', text="", icon='LOOP_BACK')
            pivot_icon = (
                'PIVOT_INDIVIDUAL' if scene.tool_settings.transform_pivot_point == 'INDIVIDUAL_ORIGINS'
                else 'PIVOT_MEDIAN'
            )
            box_row.operator('object.toggle_pivot_point', text="", icon=pivot_icon)

            row = layout.box()
            box_row = row.row(align=True)
            box_row.label(text="Bone Collections", icon="GROUP")
            box_row = row.row(align=True)
            #Get the bone collection in weightpaint mode
            with bpy.context.temp_override(armature=armature.data):
                box_row.template_bone_collection_tree()



            row = layout.row()
            active_tool = bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).idname

            #Check if correct setup is present
            is_bone_influence_mode = obj.data.use_paint_mask and active_tool == "builtin.select_box"
            icon = "RADIOBUT_ON" if is_bone_influence_mode else "RADIOBUT_OFF"

            #Toggles the correct setup
            layout.operator("object.toggle_paint_mask_and_tool", text="Check Bone Influence", icon=icon)
            
            if is_bone_influence_mode:
                row = layout.row()
                box_row = row.row(align=True)
                box_row = layout.box()
                box_row.operator("object.find_influencing_bones", text="Show Influencing Bones", icon="ZOOM_SELECTED")
                box_row.operator('object.show_all_bones', icon='LOOP_BACK')

        else:
            layout.label(text="No armature found.", icon="ERROR")

    def draw_bone_pose_mode_on(self, layout, context):
        obj = context.active_object
        active_bone = context.active_bone

        is_armature_selected = obj and obj.type == 'ARMATURE'
        is_in_pose_mode = is_armature_selected and obj.mode == 'POSE'

        # Disable the entire layout if no armature is selected
        layout.enabled = is_armature_selected or is_armature_selected is not None

        if is_in_pose_mode and is_armature_selected:
            # Posing section
            row = layout.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="Posing", icon="POSE_HLT")

            pose_box = layout.box()

            # Mirror Pose Option
            mirror_row = pose_box.row(align=True)
            mirror_row.prop(obj.pose, "use_mirror_x", text="Mirror Pose in X Axis", toggle=True, icon="MOD_MIRROR")
            mirror_row.operator('object.reset_pose', text="", icon='LOOP_BACK')
            pivot_icon = (
                'PIVOT_INDIVIDUAL'
                if context.scene.tool_settings.transform_pivot_point == 'INDIVIDUAL_ORIGINS'
                else 'PIVOT_MEDIAN'
            )
            mirror_row.operator('object.toggle_pivot_point', text="", icon=pivot_icon)

            # Bone Options
            row = layout.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="Bone Options", icon="BONE_DATA")

            bone_box = layout.box()
            bone_box.prop(obj, "show_in_front", text="Show In Front")
            bone_box.prop(obj.data, "show_axes", text="Show Axes")
            bone_box.prop(obj.data, "show_names", text="Show Names")
            bone_box.prop(obj.data, "display_type", text="Bone Type")
            bone_box.prop(obj, "display_type", text="Display As")

            # Bone Color
            row = layout.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="Bone Color", icon="BRUSHES_ALL")

            bone_color_box = layout.box()

            if active_bone:
                bone_color_box.prop(obj.data, "show_bone_colors", text="Enable Bone Colors")
                bone_color_box.prop(active_bone.color, "palette", text="Bone Color")
                props = bone_color_box.operator("armature.copy_bone_color_to_selected", text="Copy Active Color to Selected")
                props.bone_type = 'EDIT'
                bone_color_box.operator("armature.copy_bone_color_to_collection", text="Copy Active Color to Collection")
            else:
                bone_color_box.label(text="No Bone Selected!", icon="ERROR")

            # Bone Collection Management
            row = layout.row(align=True)
            row.alignment = 'CENTER'
            row.label(text="Bone Collections", icon="GROUP_BONE")

            collection_row = layout.row()
            collection_row.template_bone_collection_tree()

            col = collection_row.column(align=True)
            col.operator("armature.collection_add", icon='ADD', text="")
            col.operator("armature.collection_remove", icon='REMOVE', text="")

            col.separator()

            col.menu("ARMATURE_MT_collection_context_menu", icon='DOWNARROW_HLT', text="")

            # Ensure active_bcoll is defined
            active_bcoll = obj.data.collections.active
            if active_bcoll:
                col.separator()
                col.operator("armature.collection_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("armature.collection_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            # Collection Assignment and Selection
            collection_action_row = layout.row()
            sub = collection_action_row.row(align=True)
            sub.operator("armature.collection_assign", text="Assign")
            sub.operator("armature.collection_unassign", text="Remove")

            sub = collection_action_row.row(align=True)
            sub.operator("armature.collection_select", text="Select")
            sub.operator("armature.collection_deselect", text="Deselect")


    def draw_both_mode_off(self, layout):
        box = layout.box()
        box.label(text="Neither mode is active.", icon="ERROR")



# Collect all panel classes in a list
classes = [
    DOGS_PT_panel,
    STATS_PT_panel,
    MESH_EDIT_PT_panel,
    WEIGHTPAINT_BONE_MODES_PT,
]
