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

bl_info = {
    "name" : "UE Helper",
    "author" : "yCoffeeGames",
    "description" : "https://space.bilibili.com/1782986697",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "VIEW_3D / UE",
    "warning" : "",
    "category" : "Generic"
}

from . import auto_load
from . operators import ops_dict, RenameGameOperator, MarkAsUECollisionOperator
import bpy

auto_load.init()

class VIEW3D_PT_UEHelper(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "UE Helper"
    bl_category = 'UE'

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator(RenameGameOperator.bl_idname, text=RenameGameOperator.bl_label)
        col.operator(MarkAsUECollisionOperator.bl_idname, text=MarkAsUECollisionOperator.bl_label)

def register():
    auto_load.register()
    bpy.utils.register_class(VIEW3D_PT_UEHelper)
    bpy.app.translations.register(__name__, ops_dict)

def unregister():
    bpy.app.translations.unregister(__name__)
    bpy.utils.unregister_class(VIEW3D_PT_UEHelper)
    auto_load.unregister()
