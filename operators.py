# operators.py

import bpy
from bpy.props import StringProperty

from . import utils
from mathutils import Vector
import bmesh
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

class SimpleExportOperator(bpy.types.Operator):
    """Finds the nearest collection with exporters from the active object's collection and exports it"""
    bl_idname = 'export.simple_export'
    bl_label = 'Simple Export Operator'

    def execute(self, context):
        selected_coll = context.scene.selected_collection

        if selected_coll:
            self.active_selected_collection = selected_coll
            if hasattr(bpy.ops.collection, 'export_all'):
                bpy.ops.collection.export_all()
                # Include the exporter names in the success message
                exporter_names_str = ", ".join(exporter_names)
                self.report({'INFO'}, f"Successfully exported collection: '{selected_coll.name}' using exporters: {exporter_names_str}")
            else:
                self.report({'ERROR'}, "No valid export operator found.")
            context.view_layer.active_selected_colllection = original_collection
        else:
            self.report({'WARNING'}, "Could not find the layer collection for exporting.")


class AddArmatureOperator(bpy.types.Operator):
    """Add a predefined armature into the scene"""
    bl_idname = "add_armature.operator"
    bl_label = "Add Armature"
    bl_options = {'UNDO'}
    armature_type: StringProperty() # type: ignore

    def execute(self, context):
        if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        armature_data = utils.ARMATURE_TYPES[self.armature_type]

        bpy.ops.object.add(type='ARMATURE')
        obj = bpy.context.object
        obj.name = armature_data['name']
        armature = obj.data
        armature.name = armature_data['name']

        obj.show_in_front = True
        obj.data.display_type = 'OCTAHEDRAL'
        obj.display_type = 'WIRE'

        bpy.ops.object.mode_set(mode='EDIT')

        bones = {}
        for bone_data in armature_data['bones']:
            bone = armature.edit_bones.new(bone_data['name'])
            bone.head = bone_data['head']
            bone.tail = bone_data['tail']
            bones[bone_data['name']] = bone

        for bone_data in armature_data['bones']:
            if bone_data['parent']:
                child_bone = bones[bone_data['name']]
                parent_bone = bones[bone_data['parent']]
                child_bone.parent = parent_bone
                # Only set use_connect if child_bone.head is at parent_bone.tail
                if (child_bone.head - parent_bone.tail).length < 1e-6:
                    child_bone.use_connect = True

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

class OBJECT_OT_DistributeAlongAxisWithMirrors(bpy.types.Operator):
    """Arrange selected objects along a specified axis without overlapping, preserving mirrored pairs"""
    bl_idname = "object.distribute_along_axis_with_mirrors"
    bl_label = "Distribute Objects Along Axis with Mirrors"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="Axis to distribute along",
        items=[('X', "X Axis", ""), 
               ('Y', "Y Axis", ""), 
               ('Z', "Z Axis", "")],
        default='Y'
    ) # type: ignore
    
    margin: bpy.props.FloatProperty(
        name="Margin",
        description="Distance between the objects",
        default=0.20,
        min=0.0,
        max=1000.0,
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("The current mode is not Object mode.")
            return False
        if len(context.selected_objects) == 0:
            cls.poll_message_set("No objects selected.")
            return False
        if len(context.selected_objects) < 2:
            cls.poll_message_set("Less then two objects selected.")
            return False
        return True

    def execute(self, context):
        selected_objects = context.selected_objects

        # Set the origin of each object to its bounding box center
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            obj.select_set(False)

        # Re-select all objects
        for obj in selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = selected_objects[0]

        # Axis indices for distribution and mirror checking
        axis_index = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]
        # Define mirror axis mapping according to your expectations
        mirror_axis_mapping = {'X': 'Y', 'Y': 'X', 'Z': 'X'}  # Modify if necessary
        mirror_axis = mirror_axis_mapping[self.axis]
        mirror_axis_index = {'X': 0, 'Y': 1, 'Z': 2}[mirror_axis]

        # Group objects with their mirrored counterparts
        grouped_objects = []
        processed_objects = set()

        for obj in selected_objects:
            if obj in processed_objects:
                continue
            
            # Find a mirrored counterpart, if any
            mirrored_obj = next(
                (other for other in selected_objects 
                 if other != obj and 
                 round(other.location[mirror_axis_index], 4) == -round(obj.location[mirror_axis_index], 4) and
                 round(other.location[axis_index], 4) == round(obj.location[axis_index], 4)),
                None
            )

            if mirrored_obj:
                # Add the pair as a group
                grouped_objects.append([obj, mirrored_obj])
                processed_objects.update({obj, mirrored_obj})
            else:
                # Add as a single object group
                grouped_objects.append([obj])
                processed_objects.add(obj)

        # **Sort the groups along the selected axis**
        def get_group_sort_key(group):
            # Use the minimum position along the axis of the group
            min_val = min((obj.location[axis_index] for obj in group))
            return min_val

        grouped_objects.sort(key=get_group_sort_key)

        # Arrange each group along the selected axis
        current_position = 0.0

        for group in grouped_objects:
            # Calculate bounding box size for the entire group along the selected axis
            min_val = min((obj.matrix_world @ Vector(corner))[axis_index] for obj in group for corner in obj.bound_box)
            max_val = max((obj.matrix_world @ Vector(corner))[axis_index] for obj in group for corner in obj.bound_box)
            group_size = max_val - min_val

            # Move each object in the group by the same amount to keep them aligned
            delta = current_position - min_val
            for obj in group:
                obj.location[axis_index] += delta

            # Update the position for the next group, including margin
            current_position += group_size + self.margin

        return {'FINISHED'}

class OBJECT_OT_show_ngons(bpy.types.Operator):
    """Select faces that have more than 4 edges in the mesh objects"""
    bl_idname = "object.show_ngons"
    bl_label = "Ngons"
    
    @classmethod
    def poll(cls, context):
        # Check if any objects are selected
        if not context.selected_objects:
            cls.poll_message_set("No objects selected.")
            return False
        
        # Check if all selected objects are meshes
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                cls.poll_message_set("All selected objects must be meshes.")
                return False
        
        # Check if we are in Edit Mode
        if context.object.mode != 'EDIT':
            cls.poll_message_set("To use this function, you need to be in Edit Mode.")
            return False
        
        # All conditions are met
        return True
    
    def execute(self, context):
        
        total_selected_faces = 0  # To store the total number of selected Ngons across all objects
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # Ensure the object is the active one
                context.view_layer.objects.active = obj

                # Get the mesh data in Edit Mode
                mesh = bmesh.from_edit_mesh(obj.data)

                # Deselect all faces first
                bpy.ops.mesh.select_all(action='DESELECT')

                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

                # Select faces with more than 4 sides (Ngons)
                bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')

                # Count selected faces
                num_selected_faces = len([f for f in mesh.faces if f.select])
                total_selected_faces += num_selected_faces

                # Update the mesh in edit mode
                bmesh.update_edit_mesh(obj.data)

        if total_selected_faces > 0:
            self.report({'INFO'}, f"Found Ngons: {total_selected_faces}")
        else:
            self.report({'INFO'}, "No Ngons found in selected objects!")

        return {'FINISHED'}

class OBJECT_OT_show_triangles(bpy.types.Operator):
    """Select faces that have exactly 3 edges in the mesh objects"""
    bl_idname = "object.show_triangles"
    bl_label = "Select Triangles"

    @classmethod
    def poll(cls, context):
        # Check if any objects are selected
        if not context.selected_objects:
            cls.poll_message_set("No objects selected.")
            return False
        
        # Check if all selected objects are meshes
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                cls.poll_message_set("All selected objects must be meshes.")
                return False
        
        # Check if we are in Edit Mode
        if context.object.mode != 'EDIT':
            cls.poll_message_set("To use this function, you need to be in Edit Mode.")
            return False
        
        # All conditions are met
        return True
    
    def execute(self, context):
        total_selected_faces = 0  # To store the total number of selected triangles across all objects
        
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # Ensure the object is the active one
                context.view_layer.objects.active = obj

                # Get the mesh data in Edit Mode
                mesh = bmesh.from_edit_mesh(obj.data)

                # Deselect all faces first
                bpy.ops.mesh.select_all(action='DESELECT')
                
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

                # Select faces with exactly 3 sides (triangles)
                bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')

                # Count selected faces
                num_selected_faces = len([f for f in mesh.faces if f.select])
                total_selected_faces += num_selected_faces

                # Update the mesh in edit mode
                bmesh.update_edit_mesh(obj.data)

        if total_selected_faces > 0:
            self.report({'INFO'}, f"Found triangles: {total_selected_faces}")
        else:
            self.report({'INFO'}, "No triangles found in selected objects!")

        return {'FINISHED'}

# Operator to join visible objects
class OBJECT_OT_JoinVisible(bpy.types.Operator):
    """Join only visible mesh objects"""
    bl_idname = "object.join_visible"
    bl_label = "Join Visible"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if there are any visible objects
        visible_objects = any(
            obj.visible_get() and obj.type == 'MESH' for obj in context.visible_objects
        )

        if not visible_objects:
            cls.poll_message_set("No visible mesh objects in the scene.")
            return False

        # Check if the current mode is Object mode
        if context.mode != 'OBJECT':
            cls.poll_message_set("The current mode is not Object mode.")
            return False

        # All conditions are met
        return True

    def execute(self, context):
        # Ensure we're in Object mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Find all visible mesh objects
        visible_mesh_objects = [
            obj for obj in context.visible_objects
            if obj.type == 'MESH' and obj.visible_get()
        ]

        # Check if there are any visible mesh objects
        if not visible_mesh_objects:
            self.report({'WARNING'}, "No visible mesh objects to join.")
            return {'CANCELLED'}

        # Select all visible mesh objects
        for obj in visible_mesh_objects:
            obj.select_set(True)

        # Set the active object to the first one in the list
        context.view_layer.objects.active = visible_mesh_objects[0]

        # Join all selected objects
        bpy.ops.object.join()

        self.report({'INFO'}, f"Joined {len(visible_mesh_objects)} mesh objects.")
        return {'FINISHED'}

# Operator for separating by selection
class MESH_OT_SeparateBySelection(bpy.types.Operator):
    """Separates a mesh based on the selected faces"""
    bl_idname = "mesh.separate_by_selection"
    bl_label = "Separate by Selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_object = context.object
        
        if active_object is None:
            cls.poll_message_set("No active object in the context.")
            return False

        if active_object.type != 'MESH':
            cls.poll_message_set("Active object is not a mesh.")
            return False

        if active_object.mode != 'EDIT':
            cls.poll_message_set("Active object is not in edit mode.")
            return False
        
        # Check if there are any selected faces
        bm = bmesh.from_edit_mesh(active_object.data)
        if not any(face.select for face in bm.faces):
            cls.poll_message_set("No faces selected.")
            return False

        return True

    def execute(self, context):
        bpy.ops.mesh.separate(type='SELECTED')
        return {'FINISHED'}

# Operator for separating by loose parts
class MESH_OT_SeparateByLooseParts(bpy.types.Operator):
    """Separates a mesh based on its loose, unconnected parts"""
    bl_idname = "mesh.separate_by_loose_parts"
    bl_label = "Separate by Loose Parts"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        
        #I would love to use just bpy.ops.mesh.separate(type='LOOSE') but currently it breaks normals when used this issue was 
        #reported 2022 not fixed to this day.
        
        # Check the current mode
        initial_mode = bpy.context.active_object.mode
        
        # Ensure there is an active object and it is a mesh
        active_object = bpy.context.active_object
        if active_object is None or active_object.type != 'MESH':
            print("No active mesh object selected.")
            return

        # If not already in Edit Mode, switch to Edit Mode
        if initial_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all geometry in Edit Mode
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Separate by loose parts
        bpy.ops.mesh.separate(type='LOOSE')
        
        # Deselect all geometry
        bpy.ops.mesh.select_all(action='DESELECT')
        
        # Switch back to Object Mode if it was the initial mode
        if initial_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}
    
# Operator for separating by materials
class MESH_OT_SeparateByMaterials(bpy.types.Operator):
    """Separates a mesh based on the materials assigned to its faces"""
    bl_idname = "mesh.separate_by_materials"
    bl_label = "Separate by Materials"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        bpy.ops.mesh.separate(type='MATERIAL')
        return {'FINISHED'}

class OBJECT_OT_toggle_pose_mode(bpy.types.Operator):
    """Toggle between Pose Mode and previous mode"""
    bl_idname = "object.toggle_pose_mode"
    bl_label = "Toggle Pose Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        current_mode = context.mode



        # If currently in Pose mode, switch back to Object mode
        if current_mode == 'POSE':
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}

        # From OBJECT or PAINT_WEIGHT mode to POSE mode
        if current_mode in {'OBJECT', 'PAINT_WEIGHT'}:
            if not obj or obj.type not in {'MESH', 'ARMATURE'}:
                self.report({'WARNING'}, "Active object must be a Mesh or Armature.")
                return {'CANCELLED'}

            # If the active object is an Armature
            if obj.type == 'ARMATURE':
                bpy.ops.object.mode_set(mode='POSE')
                return {'FINISHED'}

            # If the active object is a Mesh
            elif obj.type == 'MESH':
                # Check if the mesh has only one armature parent
                armature_parents = [mod.object for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object]
                if len(armature_parents) == 1:
                    armature = armature_parents[0]

                    armature.hide_viewport = False
                    armature.hide_set(False)
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    armature.select_set(True)
                    context.view_layer.objects.active = armature
                    bpy.ops.object.mode_set(mode='POSE')
                    return {'FINISHED'}
                else:
                    self.report({'WARNING'}, "Mesh must have exactly one active Armature modifier.")
                    return {'CANCELLED'}
        else:
            # Switching from other modes to Pose Mode
            bpy.ops.object.mode_set(mode='OBJECT')
            return self.execute(context)

class OBJECT_OT_toggle_weight_paint_mode(bpy.types.Operator):
    """Toggle between Weight Paint Mode and Object Mode"""
    bl_idname = "object.toggle_weight_paint_mode"
    bl_label = "Toggle Weight Paint Mode"
    bl_options = {'UNDO'}

    trigger_from_ui: bpy.props.BoolProperty(
        name="Trigger from UI",
        description="Determine if operator is triggered from UI or shortcut",
        default=False
    )

    parent_method: bpy.props.EnumProperty(
        name="Parenting Method",
        description="Choose how to parent the mesh to the armature",
        items=[
            ('ARMATURE_AUTO', "Automatic Weights", ""),
            ('ARMATURE_ENVELOPE', "Envelope Weights", ""),
            ('ARMATURE_NAME', "Empty Groups", ""),
        ],
        default='ARMATURE_AUTO'
    )

    def armature_items(self, context):
        items = [(obj.name, obj.name, "") for obj in bpy.data.objects if obj.type == 'ARMATURE']
        if not items:
            items = [('None', 'None', 'No armatures available')]
        return items

    armature_to_parent: bpy.props.EnumProperty(
        name="Armature",
        description="Select an armature to parent the mesh to",
        items=armature_items
    )

    def mesh_items(self, context):
        items = [(obj.name, obj.name, "") for obj in bpy.context.scene.objects if obj.type == 'MESH']
        if not items:
            items = [('None', 'None', 'No meshes available')]
        return items

    mesh_to_paint: bpy.props.EnumProperty(
        name="Mesh",
        description="Select a mesh to parent to the armature",
        items=mesh_items
    )
    

    def execute(self, context):
        obj = context.active_object
        current_mode = context.mode

        # If the active object is not valid
        if not obj or obj.type not in {'MESH', 'ARMATURE'}:
            self.report({'WARNING'}, "Active object must be a Mesh or an Armature.")
            return {'CANCELLED'}

        # Toggle modes based on the active object's type and current mode
        if current_mode == 'PAINT_WEIGHT':
            # If already in Weight Paint mode, decide based on the object type
            if obj.type == 'MESH':
                # Switch back to Object mode
                bpy.ops.object.mode_set(mode='OBJECT')
                armature = self.find_armature(obj)
                armature.select_set(False)
                print("vypnuto")
            elif obj.type == 'ARMATURE':
                # Look for a parented mesh and switch to Weight Paint mode
                meshes = [child for child in obj.children if child.type == 'MESH']
                if meshes:
                    self.switch_to_weight_paint(meshes[0], obj, context)

            
            return {'FINISHED'}

        # Ensure Object mode for setup
        if current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Handle the case when the active object is a Mesh
        if obj.type == 'MESH':
            armature = self.find_armature(obj)
            if armature:
                self.switch_to_weight_paint(obj, armature, context)
            else:
                if not self.armature_to_parent:
                    self.report({'WARNING'}, "Please select an armature.")
                    return {'CANCELLED'}
                else:
                    armature_name = self.armature_to_parent
                    armature = bpy.data.objects.get(armature_name)
                    if not armature or armature.type != 'ARMATURE':
                        self.report({'WARNING'}, "Please select a valid armature.")
                        return {'CANCELLED'}
                    self.parent_mesh_to_armature(obj, armature)
                    self.switch_to_weight_paint(obj, armature, context)
        elif obj.type == 'ARMATURE':
            # Handle the case when the active object is an Armature
            meshes = [child for child in obj.children if child.type == 'MESH']
            if meshes:
                self.switch_to_weight_paint(meshes[0], obj, context)
            else:
                self.report({'WARNING'}, "No mesh parented to the armature.")
                return {'CANCELLED'}

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj.type == 'MESH' and not self.find_armature(obj):
            layout.label(text="Mesh is not parented to an armature.")
            layout.prop(self, "armature_to_parent")
            layout.prop(self, "parent_method")
        elif obj.type == 'ARMATURE':
            meshes = [child for child in obj.children if child.type == 'MESH']
            if not meshes:
                layout.label(text="No meshes parented to the armature.")
                layout.prop(self, "mesh_to_paint")
                layout.prop(self, "parent_method")
            elif len(meshes) > 1:
                layout.label(text="Select a Mesh that you would like to switch to:")
                layout.prop(self, "mesh_to_paint")
            else:
                # Only one mesh parented, no need to draw anything
                pass

    def invoke(self, context, event):
        
        if not self.trigger_from_ui:
            # Perform ray casting only when NOT triggered from the UI
            obj = self.get_object_under_cursor(context,event)
            print("Raycast shot down: ", obj)
        else: 
            obj = context.active_object
            print("No Raycast shot down: ", obj)
        
        if not obj:
            self.report({'WARNING'}, "No mesh selected!")
            return {'CANCELLED'}
        
        if obj.type == 'MESH':
            armature = self.find_armature(obj)
            if armature:
                # No need to show dialog
                return self.execute(context)
            else:
                # Need to show dialog
                return context.window_manager.invoke_props_dialog(self)
        elif obj.type == 'ARMATURE':
            meshes = [child for child in obj.children if child.type == 'MESH']
            if not meshes:
                # No meshes parented, need to select one
                return context.window_manager.invoke_props_dialog(self)
            elif len(meshes) == 1:
                # Only one mesh, proceed
                return self.execute(context)
            else:
                # Multiple meshes, need to select one
                return context.window_manager.invoke_props_dialog(self)
        
        else:
            
            return {'CANCELLED'}

    def switch_to_weight_paint(self, mesh, armature, context):
        #Make sure mesh and armature are visible
        armature.hide_viewport = False
        armature.hide_set(False)
        mesh.hide_viewport = False
        mesh.hide_set(False)

        # Ensure both mesh and armature are selected, with mesh active
        #bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        armature.select_set(True)
        context.view_layer.objects.active = mesh


        # Switch to Edit mode to deselect all vertices, then switch to Weight Paint mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')

        # Set it as the active vertex group
        active_bone = bpy.context.active_pose_bone
        
        # Set the vertex group corresponding to the active bone as active
        if active_bone and active_bone.name in mesh.vertex_groups:
            vertex_group = mesh.vertex_groups[active_bone.name]  # Corrected this line
            mesh.vertex_groups.active = vertex_group  # Set the active vertex group

        # Adjust viewport and tool settings
        if context.space_data.type == 'VIEW_3D':
            context.space_data.overlay.weight_paint_mode_opacity = 1

        context.scene.tool_settings.vertex_group_user = 'ACTIVE'
        
        #Still considering if this should be on by default for now turned off
        #context.scene.tool_settings.use_auto_normalize = True

    def find_armature(self, mesh):
        # Check parent
        if mesh.parent and mesh.parent.type == 'ARMATURE':
            return mesh.parent
        # Check modifiers
        for mod in mesh.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                return mod.object
        return None

    def parent_mesh_to_armature(self, mesh, armature):
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(type=self.parent_method)

    def get_object_under_cursor(self, context, event):
        """Utility function to get the object under the cursor"""
        region = context.region
        rv3d = context.space_data.region_3d

        # Get the 2D mouse coordinates from the event
        coord = (event.mouse_region_x, event.mouse_region_y)

        # Convert 2D mouse coordinates to a 3D ray
        view_vector = region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

        # Perform a ray cast
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            context.evaluated_depsgraph_get(),
            ray_origin,
            view_vector
        )

        return obj if result else None

class WeightGradientOperator(bpy.types.Operator):
    """Apply a spherical weight gradient centered at the selected bone"""
    bl_idname = "object.weight_gradient_operator"
    bl_label = "Apply Spherical Weight Gradient"
    bl_options = {'REGISTER', 'UNDO'}

    gradient_strength: bpy.props.FloatProperty(
        name="Gradient Strength",
        description="Maximum weight at the center of the bone",
        default=1.0,
        min=0.01,
        
    )

    gradient_radius: bpy.props.FloatProperty(
        name="Gradient Radius",
        description="Radius of the gradient sphere",
        default=1.0,
        min=0.0
    )

    gradient_type: bpy.props.EnumProperty(
        name="Gradient Type",
        description="Type of gradient",
        items=[
            ('LINEAR', "Linear", ""),
            ('SMOOTH', "Smooth", ""),
            ('CONSTANT', "Constant", "")
        ],
        default='LINEAR'
    )

    center_pos_obj: bpy.props.FloatVectorProperty(name="Bone Center", subtype='TRANSLATION')

    def invoke(self, context, event):
        obj = context.active_object

        if context.mode != 'PAINT_WEIGHT':
            self.report({'ERROR'}, "You must be in Weight Paint mode to use this operator.")
            return {'CANCELLED'}

        # Get the active vertex group (assumed to correspond to the selected bone)
        vertex_group = obj.vertex_groups.active
        if vertex_group is None:
            self.report({'ERROR'}, "No active vertex group.")
            return {'CANCELLED'}

        bone_name = vertex_group.name

        # Get the armature modifier and armature object
        armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE'), None)
        if armature_mod is None or armature_mod.object is None:
            self.report({'ERROR'}, "Object has no valid Armature modifier.")
            return {'CANCELLED'}

        armature = armature_mod.object

        # Get the pose bone from the armature
        pose_bone = armature.pose.bones.get(bone_name)
        if pose_bone is None:
            self.report({'ERROR'}, f"Pose Bone '{bone_name}' not found in armature.")
            return {'CANCELLED'}

        # Calculate the bone center
        head_pos_world = armature.matrix_world @ pose_bone.head
        tail_pos_world = armature.matrix_world @ pose_bone.tail
        center_pos_world = (head_pos_world + tail_pos_world) / 2

        # Store the bone center in object space
        self.center_pos_obj = obj.matrix_world.inverted() @ center_pos_world

        # Place the 3D cursor at the bone center (for debugging)
        bpy.context.scene.cursor.location = center_pos_world

        # Call the execute method
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object

        if context.mode != 'PAINT_WEIGHT':
            self.report({'ERROR'}, "You must be in Weight Paint mode to use this operator.")
            return {'CANCELLED'}

        center_pos_obj = self.center_pos_obj

        mesh = obj.data

        # Apply the gradient to each vertex in the mesh
        for v in mesh.vertices:
            v_co = v.co
            distance = (v_co - center_pos_obj).length

            if distance > self.gradient_radius:
                weight = 0.0
            else:
                normalized_distance = distance / self.gradient_radius if self.gradient_radius > 0 else 0.0

                if self.gradient_type == 'LINEAR':
                    weight = self.gradient_strength * (1 - normalized_distance)
                elif self.gradient_type == 'SMOOTH':
                    weight = self.gradient_strength * ((math.cos(math.pi * normalized_distance) + 1) / 2)
                elif self.gradient_type == 'CONSTANT':
                    weight = self.gradient_strength
                else:
                    weight = 0.0

            weight = max(0.0, min(weight, 1.0))  # Clamp the weight between 0 and 1

            vertex_group = obj.vertex_groups.active

            if weight > 0.0:
                vertex_group.add([v.index], weight, 'REPLACE')
            else:
                vertex_group.remove([v.index])

        return {'FINISHED'}

class ToggleWeightValue(bpy.types.Operator):
    """Toggle the weight paint value between 0 and 1"""
    bl_idname = "object.toggle_weight_value"
    bl_label = "Toggle Weight Value"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object

        # Check if there is an active object
        if obj is None:
            cls.poll_message_set("No active object selected.")
            return False

        # All conditions are met
        return True

    def execute(self, context):
        # Get the current weight value
        current_weight = bpy.context.scene.tool_settings.unified_paint_settings.weight
        
        # Toggle the weight value to 1 if it is 0, otherwise set it to 0
        if current_weight == 0:
            bpy.context.scene.tool_settings.unified_paint_settings.weight = 1.0
        else:
            bpy.context.scene.tool_settings.unified_paint_settings.weight = 0.0

        return {'FINISHED'}


class ToggleWeightBrushMode(bpy.types.Operator):
    """Toggle the weight paint Brush between Add and Subtract modes"""
    bl_idname = "object.toggle_weight_brush_mode"
    bl_label = "Toggle Weight Brush Mode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object

        # Check if there is an active object
        if obj is None:
            cls.poll_message_set("No active object selected.")
            return False

        # Check if we're in Weight Paint mode
        if context.mode != 'PAINT_WEIGHT':
            cls.poll_message_set("Not in Weight Paint mode.")
            return False

        return True

    def execute(self, context):
        # Access the active weight paint brush
        brush = context.tool_settings.weight_paint.brush

        if not brush:
            self.report({'WARNING'}, "No active weight paint brush found.")
            return {'CANCELLED'}

        # Toggle the blend mode
        if brush.blend == 'ADD':
            brush.blend = 'SUB'

        else:
            brush.blend = 'ADD'


        return {'FINISHED'}

class OBJECT_OT_FindInfluencingBones(bpy.types.Operator):
    bl_idname = "object.find_influencing_bones"
    bl_label = "Find Influencing Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        # Check for mesh object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh.")
            return {'CANCELLED'}

        if context.mode == 'PAINT_WEIGHT':
            # Get selected vertices in weight paint mode with paint mask
            vertex_indices = [v.index for v in obj.data.vertices if v.select]
            if not vertex_indices:
                self.report({'ERROR'}, "No vertices selected with the paint mask.")
                return {'CANCELLED'}

        else:
            self.report({'ERROR'}, "Must be in Weight Paint mode.")
            return {'CANCELLED'}


        # Get influencing vertex groups
        vg_indices = set()
        for v_idx in vertex_indices:
            vg_indices.update(g.group for g in obj.data.vertices[v_idx].groups)

        if not vg_indices:
            self.report({'INFO'}, "No influencing bones found.")
            return {'FINISHED'}

        # Find the armature
        armature = next((mod.object for mod in obj.modifiers if mod.type == 'ARMATURE'), None)
        if armature is None:
            self.report({'ERROR'}, "No armature modifier found on the mesh.")
            return {'CANCELLED'}

        # Deselect all bones and hide them
        for bone in armature.pose.bones:
            bone.bone.select = False
            bone.bone.hide = True  # Hide all bones initially

        # Map vertex groups to bones
        bone_names = [obj.vertex_groups[vg_idx].name for vg_idx in vg_indices if obj.vertex_groups[vg_idx].name in armature.data.bones]

        if not bone_names:
            self.report({'INFO'}, "No influencing bones found.")
            return {'FINISHED'}

        # Select and unhide the bones influencing the selected vertices
        for bone_name in bone_names:
            bone = armature.pose.bones.get(bone_name)
            if bone:
                bone.bone.select = True
                bone.bone.hide = False  # Unhide influencing bones


        self.report({'INFO'}, f"This mesh is influanced by: {len(bone_names)} Bones")
        return {'FINISHED'}

class OBJECT_OT_TogglePaintMaskAndTool(bpy.types.Operator):
    bl_idname = "object.toggle_paint_mask_and_tool"
    bl_label = "Toggle Paint Mask and Tool"
    bl_options = {'REGISTER', 'UNDO'}

    _original_use_paint_mask = None
    _original_tool_idname = None

    def execute(self, context):
        obj = context.active_object

        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, "Active object is not a mesh.")
            return {'CANCELLED'}

        # Access the mesh data
        mesh_data = obj.data

        # Get the current active tool idname
        current_tool = "builtin.brush"
        desired_tool = "builtin.select_box"

        # Check if the operator has already saved the original states
        if not hasattr(bpy.types.Scene, "_original_use_paint_mask"):
            # Save the original states
            bpy.types.Scene._original_use_paint_mask = False
            bpy.types.Scene._original_tool_idname = "builtin.brush"

            # Set the desired states
            mesh_data.use_paint_mask = True
            if current_tool != desired_tool:
                bpy.ops.wm.tool_set_by_id(name=desired_tool)

            self.report({'INFO'}, "States set to desired values.")
        else:
            # Restore the original states
            mesh_data.use_paint_mask = bpy.types.Scene._original_use_paint_mask
            bpy.ops.wm.tool_set_by_id(name=bpy.types.Scene._original_tool_idname)

            # Clean up the stored states
            del bpy.types.Scene._original_use_paint_mask
            del bpy.types.Scene._original_tool_idname

            self.report({'INFO'}, "Original states restored.")

        return {'FINISHED'}


class AssignVerticesToActiveGroup(bpy.types.Operator):
    """Bucket fill vertecies with the selected weight"""
    bl_idname = "object.assign_vertices_to_active_group"
    bl_label = "Assign All Vertices to Active Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

        # Set minimum and maximum values for the weight
    weight_value: bpy.props.FloatProperty(
        name="Weight Value", 
        default=0.0, 
        min=0.0,     # Minimum weight value
        max=1.0      # Maximum weight value
    )

    @classmethod
    def poll(cls, context):
        obj = context.object

        # Check if there is an active object
        if obj is None:
            cls.poll_message_set("No active object selected.")
            return False

        # Check if the active object has an active vertex group
        if obj.vertex_groups.active is None:
            cls.poll_message_set("The active object does not have an active vertex group.")
            return False

        # All conditions are met
        return True

    def execute(self, context):
        
        original_paint_settings_weight = bpy.context.scene.tool_settings.unified_paint_settings.weight
        
        bpy.context.scene.tool_settings.unified_paint_settings.weight = self.weight_value

        bpy.ops.paint.weight_set()

        bpy.context.scene.tool_settings.unified_paint_settings.weight = original_paint_settings_weight
        
        return {'FINISHED'}

# Operator to toggle the pivot point between Individual Origins and Median Point
class OBJECT_OT_TogglePivotPoint(bpy.types.Operator):
    bl_idname = "object.toggle_pivot_point"
    bl_label = "Toggle Pivot Point"
    bl_description = "Toggle transform pivot point between Individual Origins and Median Point"

    @classmethod
    def poll(cls, context):
            # Check if the active area is the 3D Viewport
        if context.area.type != 'VIEW_3D':
            cls.poll_message_set("The current area is not the 3D Viewport.")
            return False
        
        return True
    
    def execute(self, context):
        current_pivot = context.scene.tool_settings.transform_pivot_point
        new_pivot = 'INDIVIDUAL_ORIGINS' if current_pivot == 'MEDIAN_POINT' else 'MEDIAN_POINT'
        context.scene.tool_settings.transform_pivot_point = new_pivot
        return {'FINISHED'}

# Operator to color bones in selected bone's collection
class ARMATURE_OT_CopyBoneColorToCollection(bpy.types.Operator):
    """Copy the active bone's color to all bones in the active bone's collection(s)"""
    bl_idname = "armature.copy_bone_color_to_collection"
    bl_label = "Copy Bone Color to Collection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        armature_obj = context.object

        if not context.active_pose_bone:
            cls.poll_message_set("No active bone selected.")
            return False

        armature_data = armature_obj.data
        if not hasattr(armature_data, "collections") or not armature_data.collections:
            cls.poll_message_set("The armature does not have any bone collections.")
            return False

        return True

    def get_bone_collections(self, bone):
        """
        Returns a list of bone collections that the given bone belongs to.
        """
        armature = bone.id_data  # Gets the Armature data block the bone belongs to
        bone_collections = []
        for collection in armature.collections:
            if bone.name in [b.name for b in collection.bones]:
                bone_collections.append(collection)
        return bone_collections

    def execute(self, context):
        armature_obj = context.object
        armature_data = armature_obj.data

        # Ensure we're in Pose Mode
        if armature_obj.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        # Get the active pose bone
        active_pose_bone = context.active_pose_bone

        if not active_pose_bone:
            self.report({'WARNING'}, "No active bone selected.")
            return {'CANCELLED'}

        # Get the bone collections the active bone is in
        bone_collections = self.get_bone_collections(active_pose_bone.bone)

        if not bone_collections:
            self.report({'WARNING'}, "Active bone is not in any collection.")
            return {'CANCELLED'}

        # Get all bones in these collections
        bones_in_collections = set()
        for collection in bone_collections:
            for bone in collection.bones:
                bones_in_collections.add(bone.name)

        # If there are no other bones in the collection(s), cancel
        if len(bones_in_collections) <= 1:
            self.report({'WARNING'}, "No other bones in the collection(s).")
            return {'CANCELLED'}

        # Select all bones in these collections
        for pose_bone in armature_obj.pose.bones:
            if pose_bone.name in bones_in_collections:
                pose_bone.bone.select = True
            else:
                pose_bone.bone.select = False

        # Copy bone color to selected bones using the operator
        try:
            # Make sure only the active bone is selected (the operator copies from active to selected)
            bpy.ops.armature.copy_bone_color_to_selected()
        except RuntimeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        # Deselect all bones
        for pose_bone in armature_obj.pose.bones:
            pose_bone.bone.select = False

        # Optionally, reselect the active bone
        active_pose_bone.bone.select = True

        self.report({'INFO'}, "Finished copying color to bones in the active bone's collection(s).")
        return {'FINISHED'}

# Custom Operator to reset pose and maintain original selection
class OBJECT_OT_ResetPose(bpy.types.Operator):
    """Reset the pose of all bones and restore the original selection"""
    bl_idname = "object.reset_pose"
    bl_label = "Reset Pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Get the selected armature name from the scene property
        active_object = context.object
        # Ensure the active object matches the selected armature and is in Pose Mode
        return (
            active_object is not None and
            active_object.type == 'ARMATURE' and
            active_object.mode == 'POSE' or 
            active_object.mode == 'WEIGHT_PAINT'
            
        )

    def execute(self, context):
        # Get the active object (armature)
        selected_armature_name = context.scene.selected_armature
        active_object = context.object
        
        if active_object.name != selected_armature_name:
            armature_name = context.scene.selected_armature
            armature = bpy.data.objects.get(armature_name)
        
        else:
            armature = context.object
        

        
        original_selection = [bone.name for bone in armature.data.bones if bone.select]

        # Select all bones
        bpy.ops.pose.select_all(action='SELECT')

        # Clear location, rotation, and scale for all selected bones
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()

        # Deselect all bones
        bpy.ops.pose.select_all(action='DESELECT')

        # Reselect originally selected bones
        for bone_name in original_selection:
            armature.data.bones[bone_name].select = True

        return {'FINISHED'}

class OBJECT_OT_ShowAllBones(bpy.types.Operator):
    bl_idname = "object.show_all_bones"
    bl_label = "Unhide All Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        # Find the armature
        armature = next((mod.object for mod in obj.modifiers if mod.type == 'ARMATURE'), None)
        if armature is None:
            self.report({'ERROR'}, "No armature modifier found on the mesh.")
            return {'CANCELLED'}

        # Deselect all bones and hide them
        for bone in armature.pose.bones:
            bone.bone.select = True
            bone.bone.hide = False  # UnHide all bones

        self.report({'INFO'}, f"All Bones Shown")
        return {'FINISHED'}


# Collect all operator classes in a list
classes = [
    SimpleExportOperator,
    AddArmatureOperator,
    OBJECT_OT_DistributeAlongAxisWithMirrors,
    OBJECT_OT_show_ngons,
    OBJECT_OT_show_triangles,
    OBJECT_OT_JoinVisible,
    MESH_OT_SeparateBySelection,
    MESH_OT_SeparateByLooseParts,
    MESH_OT_SeparateByMaterials,  
    OBJECT_OT_toggle_pose_mode,  
    OBJECT_OT_toggle_weight_paint_mode,
    WeightGradientOperator,
    ToggleWeightValue,
    OBJECT_OT_FindInfluencingBones,
    AssignVerticesToActiveGroup,
    OBJECT_OT_TogglePivotPoint,
    ARMATURE_OT_CopyBoneColorToCollection,
    ToggleWeightBrushMode,
    OBJECT_OT_ResetPose,
    OBJECT_OT_TogglePaintMaskAndTool,
    OBJECT_OT_ShowAllBones,


]