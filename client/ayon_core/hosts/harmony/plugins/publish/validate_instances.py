import pyblish.api

import ayon_core.hosts.harmony.api as harmony
from ayon_core.pipeline import get_current_asset_name
from ayon_core.pipeline.publish import (
    ValidateContentsOrder,
    PublishXmlValidationError,
)


class ValidateInstanceRepair(pyblish.api.Action):
    """Repair the instance."""

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
                    and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:
            data = harmony.read(instance.data["setMembers"][0])
            data["asset"] = get_current_asset_name()
            harmony.imprint(instance.data["setMembers"][0], data)


class ValidateInstance(pyblish.api.InstancePlugin):
    """Validate the instance asset is the current asset."""

    label = "Validate Instance"
    hosts = ["harmony"]
    actions = [ValidateInstanceRepair]
    order = ValidateContentsOrder

    def process(self, instance):
        instance_asset = instance.data["asset"]
        current_asset = get_current_asset_name()
        msg = (
            "Instance asset is not the same as current asset:"
            f"\nInstance: {instance_asset}\nCurrent: {current_asset}"
        )

        formatting_data = {
            "found": instance_asset,
            "expected": current_asset
        }
        if instance_asset != current_asset:
            raise PublishXmlValidationError(self, msg,
                                            formatting_data=formatting_data)
