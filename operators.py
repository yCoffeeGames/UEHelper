import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty
import mathutils

class RenameGameOperator(bpy.types.Operator):
    bl_idname = "ue.rename_game"
    bl_label = "Rename For UE"
    bl_options = {'REGISTER', 'UNDO'}

    obj_prefix: StringProperty(name="Object Name Prefix", default="SM_")
    is_add_prefix_obj: BoolProperty(
        name="Add prefix to object names", default=True)

    mat_prefix: StringProperty(name="Material Name Prefix", default="M_")
    is_add_prefix_mat: BoolProperty(
        name="Add prefix to material names", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        for obj in context.selected_objects:
            if (obj and obj.type == 'MESH' and obj.name != '' and not obj.name.startswith(self.obj_prefix)):
                obj.name = (
                    self.obj_prefix if self.is_add_prefix_obj else '') + obj.name
                obj.name = obj.name.replace('.', '_')

            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if (mat and mat.name != '' and not mat.name.startswith(self.mat_prefix)):
                    mat.name = (
                        self.mat_prefix if self.is_add_prefix_mat else '') + mat.name
                    mat.name = mat.name.replace('.', '_')

        return {'FINISHED'}


class MarkAsUECollisionOperator(bpy.types.Operator):
    bl_idname = "ue.mark_ue_collision"
    bl_label = "Mark As UE Collisions"
    bl_options = {'REGISTER', 'UNDO'}

    target_name: StringProperty(name="Target Name", default="")
    shape: EnumProperty(name='Shape', items=(
        ('UCX', 'Convex', ''),
        ('UBX', 'Box', ''),
        ('UCP', 'Capsule', ''),
        ('USP', 'Sphere', '')
    ))
    is_set_parent: BoolProperty(name="Set Parent", default=True)
    is_set_wireframe: BoolProperty(name="Wireframe Display", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        # If more than 1 selected, let active object be the target. Otherwise the active object is used
        if (len(context.selected_objects) > 1):
            self.target_name = context.active_object.name
            count = 0
            new_objs = []
            for obj in context.selected_objects:
                if obj == context.active_object:
                    continue

                obj.name = str(self.shape) + '_' + \
                    self.target_name + '_' + str(count) + "_tmp"
                obj.name = obj.name.replace('.', '_')

                if self.is_set_parent:
                    matrix = context.active_object.matrix_world.copy()

                    obj.parent = context.active_object
                    obj.matrix_parent_inverse = matrix.inverted()

                if self.is_set_wireframe:
                    obj.display_type = 'WIRE'

                new_objs.append(obj)
                count += 1
            for obj in new_objs:
                obj.name = obj.name.rsplit('_tmp', 1)[0]
        else:
            self.target_name = context.active_object.name.replace('UCX_', '').replace(
                'UBX_', '').replace('UCP_', '').replace('USP_', '').replace('.', '_')
            context.active_object.name = str(
                self.shape) + '_' + self.target_name

        return {'FINISHED'}


class SetOriginToCornerOperator(bpy.types.Operator):
    bl_idname = "ue.set_origin_corner"
    bl_label = "Set Origin Corner"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name="Index", default=0, min=0, max=7)
    is_on_ground: BoolProperty(name="Snap to ground", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object

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
    bl_label = "Set Origin Center"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name="Index", default=0, min=0, max=1)
    is_on_ground: BoolProperty(name="Snap to ground", default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object

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
    bl_label = "Add Extra Objects"
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
    rotation: FloatVectorProperty(name="Rotation", unit="ROTATION", precision=4)

    def invoke(self, context, event):
        self.align = "WORLD"
        self.location = bpy.context.scene.cursor.location
        self.rotation = (0,0,0)
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
