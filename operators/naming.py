import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
class RenameGameOperator(bpy.types.Operator):
    bl_idname = "ue.rename_game"
    bl_label = "Rename for UE"
    bl_description = "Support naming materials and meshes for selected objects"
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
    bl_label = "Mark as UE collisions"
    bl_description = "Support setting selected objects as collisions and link them to the active object (lastly selected)"
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
                if obj == context.active_object or obj.type != 'MESH':
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
            if (context.active_object.type == 'MESH'):
                self.target_name = context.active_object.name.replace('UCX_', '').replace(
                    'UBX_', '').replace('UCP_', '').replace('USP_', '').replace('.', '_')
                context.active_object.name = str(
                    self.shape) + '_' + self.target_name

        return {'FINISHED'}
