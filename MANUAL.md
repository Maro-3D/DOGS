# **DOGS Add-On User Manual**

This manual provides a detailed explanation of each function available in the DOGS add-on interface.

## **1. Import Model**
- **Function:** Allows you to import models into the scene.
- **Usage:** Click this button to open the file dialog and select a model to import. (Supported file formats are .stl, .obj, .fbx, .glb, .gltf, .dae)

## **2. Avatar Armature**
- **Function:** Dropdown menu to select the armature you want the statistics for.
- **Usage:** Choose an armature from the list of available armatures in the scene.

## **3. Add Armatures**
This section allows you to add different types of pre-made armatures to your scene.
- **3.1 Basic Humanoid:** Adds a simple humanoid armature.
- **3.2 Extended Humanoid:** Adds an extended version of the humanoid armature, which includes additional bones.
- **3.3 Digitigrade Humanoid:** Adds a digitigrade humanoid armature, suitable for models with animal-like leg structures.

## **4. Export**
This section manages the export settings for your model.
- **4.1 Export Dropdown:** Select the collection to export.
- **4.2 List of Exporters:** Shows exporters assigned to the active collection.
- **4.3 Add Export Format:** Allows you to add new exporters.
- **4.4 Export All:** Exports all added exporters.
- **4.5 Export Settings:** Shows the exporters' settings.
- **4.6 Export:** Exports the active exporter.

---

## **Stats Panel**

### **5. Device Mode**
Switch between rating your model for PC or Portable platforms. (Rating is based on VRChat limits)
- **5.1 PC VR:** Shows stats for PC VR devices.
- **5.2 Portable VR:** Shows stats for portable VR devices.

### **6. Rating for:**
- **Function:** Displays the name of the avatar currently being rated and switches the rating between rating for the selected Armature or the whole scene.
- **Usage:** The avatar's name is displayed here for reference during optimization.

### **7. Statistics**
Shows important statistics about the model:
- **7.1 Triangles:** The number of triangles in the mesh.
- **7.2 Materials:** The number of materials used by the model.
- **7.3 Bones:** The number of bones in the armature.
- **7.4 Skinned Meshes:** The number of skinned meshes.
- **7.5 Rating:** Overall rating based on the above statistics, helping to assess performance (e.g., Good, Poor).

---

## **Mesh Editing Panel**

### **8. Join Mesh**
Options for joining different parts of the mesh.
- **8.1 Selected:** Joins only the selected meshes.
- **8.2 Visible:** Joins all visible meshes.

### **9. Separate By**
Options to separate parts of the mesh based on different criteria.
- **9.1 Selection:** Separates the mesh based on selected parts.
- **9.2 Loose Parts:** Separates by loose parts, splitting the mesh where there are no connecting edges.
- **9.3 Materials:** Separates the mesh based on the different materials applied.

### **10. Explode Selected Objects**
- **Function:** Spreads selected objects in the scene.
- **Usage:** Useful for setting up the model for Substance Painter.

### **11. Normals**
Options for viewing and adjusting the normals of the mesh.
- **11.1 Recalculate:** Recalculates the normals to ensure they face the correct direction.
- **11.2 Flip:** Flips the direction of the normals.
- **11.3 Show/Hide:** Shows the direction of the normals.

### **12. Shade**
Adjust the shading of the selected mesh.
- **12.1 Smooth:** Applies smooth shading to the whole mesh.
- **12.2 Auto:** Adds a Smooth By Angle Modifier to automatically set the sharpness of mesh edges based on the angle between the neighboring faces.
- **12.3 Flat:** Applies flat shading to the whole mesh, showing each face distinctly.

### **13. Remove Custom Split Normals**
- **Function:** Removes any custom split normals, reverting to default normals.
- **Usage:** Useful if custom normals were applied and need to be reset.

---

## **Armature Editing Panel**

### **14. Pose Mode Toggle**
- **Function:** Toggles between Object Mode and Pose Mode.
- **Usage:** Click to switch into Pose Mode to adjust the armature's pose.

---

## **Weight Paint Editing Panel**

### **15. Enter Weight Paint Mode**
- **Function:** Switches to Weight Paint mode for painting vertex weights.
- **Usage:** Click to enter Weight Paint Mode for detailed adjustments of bone influence on the mesh.
