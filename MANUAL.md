# DOGS Blender Add-on Manual

## Overview

**DOGS** is a comprehensive suite of tools for managing and editing armatures and meshes in Blender. It includes predefined armature types, advanced mesh editing operations, and enhanced rigging controls. The add-on is optimized for both PC and Portable platforms, providing detailed scene and armature statistics to help maintain performance-friendly models.

- **Author:** Marek Hanzelka
- **Version:** 0.0.1
- **Blender Version:** 4.2.0
- **Location:** `View3D > Sidebar > DOGS`
- **Category:** Rigging

---

## Installation

1. Download the `DOGS.zip` file.
2. In Blender, go to `Edit > Preferences > Add-ons > Install`.
3. Select the `DOGS.zip` file and click `Install Add-on`.
4. Enable the add-on by checking the checkbox next to `DOGS`.

---

## Features

### Armature Management

DOGS provides three predefined armature types:

- **Basic Humanoid**
- **Extended Humanoid**
- **Digitigrade Humanoid**

Each type is designed for specific use cases and can be added to your scene with a single click.

### Mesh Editing

The mesh editing panel offers several tools for manipulating mesh data, including:

- **Join Mesh**: Combine selected or visible meshes into one.
- **Separate Mesh**: Split meshes based on selection, loose parts, or materials.
- **Explode Selected Objects**: Separates and moves pieces of the mesh for visual effects.
- **Normals Management**: Recalculate or flip normals, and adjust shading (smooth, flat, auto).

### Scene & Armature Statistics

DOGS provides real-time statistics for both scenes and individual armatures:

- **Triangle Count**
- **Material Count**
- **Bone Count**
- **Skinned Mesh Count**

Statistics are evaluated against thresholds to determine the overall performance rating (`Good`, `Medium`, or `Poor`) for either PC or Portable platforms.

---

## Panels and Operators

### Main Panel (DOGS)

- **Import Model**: Import a model into the scene.
- **Avatar Armature**: Select an armature for detailed editing.
- **Add Armatures**: Dropdown to add predefined armature types.
- **Export**: Manage collections and export models.

### Stats Panel

Displays detailed statistics about the selected armature or all visible objects. Ratings are provided based on platform (PC or Portable).

- **Device Mode**: Toggle between PC and Portable modes.
- **Rating for**: Displays the selected armature or all visible objects.
- **Triangls**: Number of triangles.
- **Materials**: Number of materials.
- **Bones**: Number of bones.
- **Skinned Meshs**: Number of skinned meshes.

### Mesh Editing Panel

Provides tools for editing meshes directly from the panel:

- **Join Mesh**: Combines selected or visible meshes.
- **Separate Mesh**: Separates by selection, loose parts, or materials.
- **Normals**: Manage normals, including recalculating and flipping.
- **Shade**: Set shading to smooth, flat, or auto.

### Armature Editing Panel

Tools specifically for armature manipulation:

- **Pose Mode Toggle**: Enter or exit pose mode.
- **Bone Options**: Show names, axes, or change bone display types.
- **Bone Color**: Manage bone color settings.
- **Bone Collections**: Manage and organize bone collections.

### Weight Paint Editing Panel

Facilitates weight painting with advanced options:

- **Weight Paint Mode Toggle**: Enter or exit weight paint mode.
- **Show Weight Paint Contours**: Toggle contour visibility.
- **Mirror Bone Pose**: Mirror pose across the X-axis.
- **Clean Vertex Groups**: Removes unnecessary vertex groups.
- **Bone Collections**: Manage bone collections while in weight paint mode.

---

## Ratings and Thresholds

The add-on assesses the model's performance based on different thresholds for PC and Portable platforms:

- **PC Good**: Tri count ≤ 35,000, Materials ≤ 2, Bones ≤ 150, Skinned Meshes ≤ 8
- **PC Medium**: Tri count ≤ 70,000, Materials ≤ 8, Bones ≤ 256, Skinned Meshes ≤ 16
- **Portable Good**: Tri count ≤ 10,000, Materials ≤ 1, Bones ≤ 90, Skinned Meshes ≤ 1
- **Portable Medium**: Tri count ≤ 15,000, Materials ≤ 2, Bones ≤ 150, Skinned Meshes ≤ 2

---

## Frequently Asked Questions

### How do I add a new armature?
Go to the DOGS panel in the 3D Viewport sidebar, expand the "Add Armatures" section, and click on the desired armature type.

### Can I rate the entire scene?
Yes, in the Stats panel, enable the "Rate All Visible Objects" option to rate the entire scene instead of just the selected armature.

### How can I use the mesh editing features?
Ensure the object is in Object or Edit mode. Use the options in the Mesh Editing panel to join, separate, or manipulate mesh normals.

---

## Troubleshooting

### The add-on is not showing in the sidebar.
Ensure that the add-on is correctly installed and enabled in the Blender preferences. If the problem persists, try restarting Blender.

### Statistics are incorrect or not updating.
Ensure that the armature or mesh is selected and visible. If in Edit mode, make sure to exit and re-enter the mode to refresh the data.

---

## License

This add-on is distributed under the MIT License. See the LICENSE file for more details.

---

## Contact

For support, feature requests, or bug reports, contact the author at [email@example.com](mailto:email@example.com).

