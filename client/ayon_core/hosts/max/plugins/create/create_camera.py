# -*- coding: utf-8 -*-
"""Creator plugin for creating camera."""
from ayon_core.hosts.max.api import plugin


class CreateCamera(plugin.MaxCreator):
    """Creator plugin for Camera."""
    identifier = "io.openpype.creators.max.camera"
    label = "Camera"
    family = "camera"
    icon = "gear"
