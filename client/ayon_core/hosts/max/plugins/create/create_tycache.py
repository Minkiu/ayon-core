# -*- coding: utf-8 -*-
"""Creator plugin for creating TyCache."""
from ayon_core.hosts.max.api import plugin


class CreateTyCache(plugin.MaxCreator):
    """Creator plugin for TyCache."""
    identifier = "io.openpype.creators.max.tycache"
    label = "TyCache"
    family = "tycache"
    icon = "gear"
