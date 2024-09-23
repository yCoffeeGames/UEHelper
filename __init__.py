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


class VIEW3D_PT_UEHelper(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "UE Helper"
    bl_category = 'UE'

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(RenameGameOperator.bl_idname,
                     text=RenameGameOperator.bl_label)
        col.operator(MarkAsUECollisionOperator.bl_idname,
                     text=MarkAsUECollisionOperator.bl_label)
        row = col.row(align=True)
        row.operator(SetOriginToCornerOperator.bl_idname,
                     text=SetOriginToCornerOperator.bl_label)
        row.operator(SetOriginToCenterOperator.bl_idname,
                     text=SetOriginToCenterOperator.bl_label)

def menu_func(self, context):
    self.layout.operator(AddExtraObjectsOperator.bl_idname, text="Plane*", icon="MESH_PLANE").mesh = "Plane"
    self.layout.operator(AddExtraObjectsOperator.bl_idname, text="Cube*", icon="MESH_CUBE").mesh = "Cube"
    self.layout.operator(AddExtraObjectsOperator.bl_idname, text="Cylinder*", icon="MESH_CYLINDER").mesh = "Cylinder"
    self.layout.separator()

def register():
    auto_load.register()
    bpy.utils.register_class(VIEW3D_PT_UEHelper)
    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)
    bpy.app.translations.register(__name__, ops_dict)


def unregister():
    bpy.app.translations.unregister(__name__)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_class(VIEW3D_PT_UEHelper)
    auto_load.unregister()
