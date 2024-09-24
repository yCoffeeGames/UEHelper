import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty
import mathutils


class SetOriginToCornerOperator(bpy.types.Operator):
    bl_idname = "ue.set_origin_corner"
    bl_label = "Set origin corner"
    bl_description = "Support setting origin for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name="Index", default=0, min=0, max=7)
    is_on_ground: BoolProperty(name="Snap to ground", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(area=area):
                    cursor_location = context.scene.cursor.location.copy()

                    # Since origin set requires single selection, deselect all others
                    objs = context.selected_objects
                    bpy.ops.object.select_all(action='DESELECT')

                    for obj in objs:
                        if (obj.type != 'MESH'):
                            continue

                        obj.select_set(True)

                        target_corner = mathutils.Vector(
                            obj.bound_box[self.index])
                        corner_location = obj.matrix_world @ target_corner

                        bpy.ops.view3d.snap_cursor_to_selected()
                        obj.location = obj.location * 2 - corner_location
                        bpy.ops.object.origin_set(
                            type='ORIGIN_CURSOR', center='MEDIAN')

                        if (self.is_on_ground):
                            obj.location[2] = 0

                        obj.select_set(False)

                    # Select them back
                    for obj in objs:
                        obj.select_set(True)

                    # Reset 3D cursor back
                    bpy.context.scene.cursor.location = cursor_location

                break

        return {"FINISHED"}


def get_vertices_center_location(world_matrix, vertices):
    center = [
        sum(v[0] for v in vertices) / 4,
        sum(v[1] for v in vertices) / 4,
        sum(v[2] for v in vertices) / 4,
    ]
    return world_matrix @ mathutils.Vector(center)


class SetOriginToCenterOperator(bpy.types.Operator):
    bl_idname = "ue.set_origin_center"
    bl_label = "Set origin center"
    bl_description = "Support setting origin for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name="Index", default=0, min=0, max=1)
    is_on_ground: BoolProperty(name="Snap to ground", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(area=area):
                    cursor_location = context.scene.cursor.location.copy()

                    # Since origin set requires single selection, deselect all others
                    objs = context.selected_objects
                    bpy.ops.object.select_all(action='DESELECT')

                    for obj in objs:
                        if (obj.type != 'MESH'):
                            continue

                        obj.select_set(True)

                        target_vertices = [mathutils.Vector(
                            obj.bound_box[v]) for v in [1, 2, 5, 6]]
                        origin_vertices = [mathutils.Vector(
                            obj.bound_box[v]) for v in [0, 3, 4, 7]]
                        target_location = get_vertices_center_location(
                            obj.matrix_world, target_vertices)
                        origin_location = get_vertices_center_location(
                            obj.matrix_world, origin_vertices)

                        bpy.ops.view3d.snap_cursor_to_selected()
                        offset = target_location if self.index == 1 else origin_location
                        obj.location = obj.location * 2 - offset
                        bpy.ops.object.origin_set(
                            type='ORIGIN_CURSOR', center='MEDIAN')

                        if (self.is_on_ground):
                            obj.location[2] = 0

                        obj.select_set(False)

                    # Select them back
                    for obj in objs:
                        obj.select_set(True)

                    # Reset 3D cursor back
                    bpy.context.scene.cursor.location = cursor_location

                break

        return {"FINISHED"}


class AddExtraObjectsOperator(bpy.types.Operator):
    bl_idname = "ue.add_extra_objects"
    bl_label = "Add extra objects"
    bl_description = "Simple mesh with new origin"
    bl_options = {'REGISTER', 'UNDO'}

    mesh: StringProperty(name="Mesh", default="", options={'HIDDEN'})

    index: IntProperty(name="Index", default=0, min=0, max=7)
    size: FloatProperty(name="Size", default=2.0, min=0,
                        unit="LENGTH", precision=4)
    align: EnumProperty(name="Align", default="WORLD", items=(
        ('WORLD', 'World', ''),
        ('VIEW', 'View', ''),
        ('CURSOR', '3D Cursor', '')
    ))
    location: FloatVectorProperty(name="Location", unit="LENGTH", precision=4)
    rotation: FloatVectorProperty(
        name="Rotation", unit="ROTATION", precision=4)

    def invoke(self, context, event):
        self.align = "WORLD"
        self.location = bpy.context.scene.cursor.location
        self.rotation = (0, 0, 0)
        return self.execute(context)

    def execute(self, context):
        # Set rotation based on align
        if (self.align == "VIEW"):
            self.rotation = context.region_data.view_matrix.copy().inverted().to_3x3().to_euler()
        elif (self.align == "CURSOR"):
            self.rotation = context.scene.cursor.rotation_euler

        if self.mesh == "Plane":
            bpy.ops.mesh.primitive_plane_add(
                size=self.size, location=self.location, rotation=self.rotation, align=self.align)
            bpy.ops.ue.set_origin_corner(index=self.index, is_on_ground=False)
        elif self.mesh == "Cube":
            bpy.ops.mesh.primitive_cube_add(
                size=self.size, location=self.location, rotation=self.rotation, align=self.align)
            bpy.ops.ue.set_origin_corner(index=self.index, is_on_ground=False)
        elif self.mesh == "Cylinder":
            if (self.index > 1):
                self.index = 1
            bpy.ops.mesh.primitive_cylinder_add(
                radius=self.size/2, depth=self.size, location=self.location, rotation=self.rotation, align=self.align)
            bpy.ops.ue.set_origin_center(index=self.index, is_on_ground=False)

        return {"FINISHED"}


class ApplyTransformOperator(bpy.types.Operator):
    bl_idname = "ue.apply_transform"
    bl_label = "Apply transform"
    bl_options = {'REGISTER', 'UNDO'}

    is_location: BoolProperty(name="Location", default=False)
    is_rotation: BoolProperty(name="Rotation", default=False)
    is_scale: BoolProperty(name="Scale", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        for obj in context.selectable_objects:
            bpy.ops.object.transform_apply(
                location=self.is_location, rotation=self.is_rotation, scale=self.is_scale)
        return {"FINISHED"}


class ResetTransformOperator(bpy.types.Operator):
    bl_idname = "ue.reset_transform"
    bl_label = "Reset transform"
    bl_options = {'REGISTER', 'UNDO'}

    is_location: BoolProperty(name="Location", default=True)
    is_rotation: BoolProperty(name="Rotation", default=False)
    is_scale: BoolProperty(name="Scale", default=False)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        for obj in context.selectable_objects:
            if self.is_location:
                bpy.ops.object.location_clear(clear_delta=False)
            if self.is_rotation:
                bpy.ops.object.rotation_clear(clear_delta=False)
            if self.is_scale:
                bpy.ops.object.rotation_clear(clear_delta=False)

        return {"FINISHED"}
