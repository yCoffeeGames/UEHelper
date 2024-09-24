# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from . operators import *
from . import auto_load
bl_info = {
    "name": "UE Helper",
    "author": "yCoffeeGames",
    "description": "https://space.bilibili.com/1782986697",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "location": "VIEW_3D / UE",
    "warning": "",
    "category": "Generic"
}


auto_load.init()

ue_dict = {
    'zh_HANS': {
        ('*', 'UE Helper'): '虚幻引擎助手',

        ('Operator', 'Rename for UE'): '为UE重命名',
        ('*', 'Object Name Prefix'): '物体名称前缀',
        ('*', 'Add prefix to object names'): '是否增加物体名称前缀',
        ('*', 'Material Name Prefix'): '材质名称前缀',
        ('*', 'Add prefix to material names'): '是否增加材质名称前缀',

        ('Operator', 'Mark as UE collisions'): '标记为UE碰撞体',
        ('*', 'Convex'): '不规则',
        ('*', 'Set Parent'): '设置父级',
        ('*', 'Wireframe Display'): '线框显示',

        ('Operator', 'Set origin corner'): '设定边角原点',
        ('*', 'Index'): '序号',
        ('*', 'Snap to ground'): '吸附到地面',

        ('Operator', 'Set origin center'): '设定中心原点',

        ('Operator', 'Plane*'): '平面*',
        ('Operator', 'Cube*'): '立方体*',
        ('Operator', 'Cylinder*'): '柱体*',
        ('Operator', 'Add extra objects'): '添加额外物体',

        ('Operator', 'Apply transform'): '应用置换',
        ('Operator', 'Reset transform'): '重置置换'
    }
}


class VIEW3D_PT_UEHelper(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "UE Helper"
    bl_category = 'UE'

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("ue.rename_game", text="Rename for UE", icon="FILE_FONT")
        col.operator("ue.mark_ue_collision", text="Mark as UE collisions", icon="OUTLINER_OB_POINTCLOUD")
        
        layout.separator()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("ue.set_origin_corner", text="Set origin corner", icon="OBJECT_ORIGIN")
        row.operator("ue.set_origin_center", text="Set origin center", icon="SNAP_FACE_CENTER")
        row = col.row(align=True)
        row.operator("ue.apply_transform", text="Apply transform", icon="EMPTY_AXIS")
        row.operator("ue.reset_transform", text="Reset transform", icon="LOOP_BACK")


def menu_func(self, context):
    self.layout.operator("ue.add_extra_objects",
                         text="Plane*", icon="MESH_PLANE").mesh = "Plane"
    self.layout.operator("ue.add_extra_objects",
                         text="Cube*", icon="MESH_CUBE").mesh = "Cube"
    self.layout.operator("ue.add_extra_objects",
                         text="Cylinder*", icon="MESH_CYLINDER").mesh = "Cylinder"
    self.layout.separator()


def register():
    auto_load.register()
    bpy.utils.register_class(VIEW3D_PT_UEHelper)
    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)
    bpy.app.translations.register(__name__, ue_dict)


def unregister():
    bpy.app.translations.unregister(__name__)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_class(VIEW3D_PT_UEHelper)
    auto_load.unregister()
