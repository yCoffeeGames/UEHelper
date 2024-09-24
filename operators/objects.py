import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty


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

    is_select_children: BoolProperty(name="Select Children", default=False, description="No matter what type the child is")

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
