import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty, CollectionProperty, PointerProperty
from ..dependencies.BlenderTools.send2ue import unreal


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


class SelectObjectsOperator(bpy.types.Operator):
    bl_idname = "ue.select_objects"
    bl_label = "Select objects"
    bl_options = {'REGISTER', 'UNDO'}

    obj_type: EnumProperty(name="Type", default="MESH", items=(
        ('MESH', 'Mesh', ''),
        ('ARMATURE', 'Armature', ''),
        ('CURVE', 'Curve', ''),
        ('LIGHT', 'Light', ''),
        ('CAMERA', 'Camera', ''),
        ('EMPTY', 'Empty', ''),
        ('FONT', 'Text', ''),
        ('META', 'Metaball', ''),
        ('VOLUME', 'Volume', ''),
        ('GPENCIL', 'Grease Pencil', ''),
        ('LATTICE', 'Lattice', ''),
        ('SURFACE', 'Surface', ''),
        ('LIGHT_PROBE', 'Light Probe', ''),
    ))

    is_select_children: BoolProperty(
        name="Select Children", default=False, description="No matter what type the child is")

    def select_hierarchy(self, obj):
        obj.select_set(True)
        for child in obj.children:
            self.select_hierarchy(child)

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        for obj in context.scene.objects:
            if obj.type == self.obj_type:
                if not self.is_select_children:
                    obj.select_set(True)
                else:
                    self.select_hierarchy(obj)

        return {"FINISHED"}


class SyncListItem(bpy.types.PropertyGroup):
    obj: PointerProperty(
        name="Object",
        type=bpy.types.Object
    )

    is_ready_sync: BoolProperty(default=True)


class UE_UL_SyncList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item.obj, 'name', text='',
                     emboss=False, icon="OUTLINER_OB_MESH")
            row.prop(item, 'is_ready_sync', icon="UV_SYNC_SELECT",
                     icon_only=True, toggle=True)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class RefreshSyncList(bpy.types.Operator):
    bl_idname = "ue.refresh_sync_list"
    bl_label = "Refresh UE sync list"

    is_first: BoolProperty(default=False)

    def execute(self, context):
        context.scene.ue_sync_list.clear()

        for obj in context.scene.objects:
            if 'is_sync' in obj and obj['is_sync']:
                item = context.scene.ue_sync_list.add()
                item.obj = obj

        if (not self.is_first):
            context.scene.ue_sync_list_index = len(
                context.scene.ue_sync_list) - 1
        else:
            context.scene.ue_sync_list_index = 0

        return {"FINISHED"}


class MarkSync(bpy.types.Operator):
    bl_idname = "ue.mark_sync"
    bl_label = "Mark selected to sync or not"
    bl_options = {'REGISTER', 'UNDO'}

    is_remove: BoolProperty(default=False, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        for obj in context.selected_objects:
            if(obj.type == "MESH"):
                obj['is_sync'] = not self.is_remove

        bpy.ops.ue.refresh_sync_list(is_first=self.is_remove)
        bpy.ops.object.select_all(action='DESELECT')
        return {"FINISHED"}


def on_sync_list_index_changed(self, context):
    bpy.ops.object.select_all(action='DESELECT')
    if len(context.scene.ue_sync_list) > 0:
        context.scene.ue_sync_list[context.scene.ue_sync_list_index].obj.select_set(
            True)


class SyncToUEOperator(bpy.types.Operator):
    bl_idname = "ue.sync_to_ue"
    bl_label = "Sync to UE"

    def execute(self, context):
        #TODO
        objs = [item.obj for item in context.scene.ue_sync_list if item.is_ready_sync]
        print("Sync meshes to UE:", objs)
        return {"FINISHED"}

def register():
    bpy.types.Scene.ue_sync_list = CollectionProperty(type=SyncListItem)
    bpy.types.Scene.ue_sync_list_index = IntProperty(
        name='Sync', default=0, update=on_sync_list_index_changed)


def unregister():
    del bpy.types.Scene.ue_sync_list_index
    del bpy.types.Scene.ue_sync_list
