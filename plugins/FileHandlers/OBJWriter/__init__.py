# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from . import OBJWriter

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

#TODO: We can't quite finish this as we have no real faces to save yet. This writer should work, but is not tested.
def getMetaData():
    return {
        "type": "mesh_writer",
        "plugin": {
            "name": "Wavefront OBJ Writer",
            "author": "Ultimaker",
            "version": "1.0",
            "description": i18n_catalog.i18nc("OBJ Writer plugin description", "Makes it possbile to write Wavefront OBJ files.")
        },
        "mesh_writer": {
            "extension": "obj",
            "description": i18n_catalog.i18nc("OBJ Writer file format", "Wavefront OBJ File")
        }
    }

def register(app):
    return { "mesh_writer": OBJWriter.OBJWriter() }
