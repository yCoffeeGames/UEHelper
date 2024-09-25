import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty



class ToggleFaceOrientationOperator(bpy.types.Operator):
    bl_idname = "ue.toggle_face_orientation"
    bl_label = "Toggle face orientation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.space_data.overlay.show_face_orientation = not bpy.context.space_data.overlay.show_face_orientation
        self.report({'INFO'}, bpy.app.translations.pgettext('Face orientation: ' + ("On" if bpy.context.space_data.overlay.show_face_orientation else "Off")))

        return {"FINISHED"}

