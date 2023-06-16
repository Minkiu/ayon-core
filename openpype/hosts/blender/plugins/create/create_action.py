"""Create an animation asset."""

import bpy

from openpype.pipeline import get_current_task_name
import openpype.hosts.blender.api.plugin
from openpype.hosts.blender.api import lib


class CreateAction(openpype.hosts.blender.api.plugin.BlenderCreator):
    """Action output for character rigs"""

    identifier = "io.openpype.creators.blender.action"
    name = "actionMain"
    label = "Action"
    family = "action"
    icon = "male"

    def process(self):

        asset = self.data["asset"]
        subset = self.data["subset"]
        name = openpype.hosts.blender.api.plugin.asset_name(asset, subset)
        collection = bpy.data.collections.new(name=name)
        bpy.context.scene.collection.children.link(collection)
        self.data['task'] = get_current_task_name()
        lib.imprint(collection, self.data)

        if (self.options or {}).get("useSelection"):
            for obj in lib.get_selection():
                if (obj.animation_data is not None
                        and obj.animation_data.action is not None):

                    empty_obj = bpy.data.objects.new(name=name,
                                                     object_data=None)
                    empty_obj.animation_data_create()
                    empty_obj.animation_data.action = obj.animation_data.action
                    empty_obj.animation_data.action.name = name
                    collection.objects.link(empty_obj)

        return collection
