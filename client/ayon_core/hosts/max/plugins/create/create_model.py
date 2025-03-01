# -*- coding: utf-8 -*-
"""Creator plugin for model."""
from ayon_core.hosts.max.api import plugin


class CreateModel(plugin.MaxCreator):
    """Creator plugin for Model."""
    identifier = "io.openpype.creators.max.model"
    label = "Model"
    family = "model"
    icon = "gear"
