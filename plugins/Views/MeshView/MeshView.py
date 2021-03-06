# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.View.View import View
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Resources import Resources
from UM.Application import Application
from UM.Math.Color import Color
from UM.Preferences import Preferences

import math

## Standard view for mesh models. 
class MeshView(View):
    EnabledColor = Color(1.0, 0.79, 0.14, 1.0)
    DisabledColor = Color(0.68, 0.68, 0.68, 1.0)

    def __init__(self):
        super().__init__()

        Preferences.getInstance().addPreference("view/show_overhang", False)
        Preferences.getInstance().preferenceChanged.connect(self._onPreferenceChanged)

        self._enabled_material = None
        self._disabled_material = None

    def beginRendering(self):
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        if not self._enabled_material:
            if Preferences.getInstance().getValue("view/show_overhang"):
                self._enabled_material = renderer.createMaterial(Resources.getPath(Resources.ShadersLocation, "default.vert"), Resources.getPath(Resources.ShadersLocation, "overhang.frag"))
            else:
                self._enabled_material = renderer.createMaterial(Resources.getPath(Resources.ShadersLocation, "default.vert"), Resources.getPath(Resources.ShadersLocation, "default.frag"))

            self._enabled_material.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
            self._enabled_material.setUniformValue("u_diffuseColor", self.EnabledColor)
            self._enabled_material.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
            self._enabled_material.setUniformValue("u_overhangColor", Color(1.0, 0.0, 0.0, 1.0))
            self._enabled_material.setUniformValue("u_shininess", 50.0)

        if not self._disabled_material:
            self._disabled_material = renderer.createMaterial(Resources.getPath(Resources.ShadersLocation, "default.vert"), Resources.getPath(Resources.ShadersLocation, "default.frag"))
            self._disabled_material.setUniformValue("u_ambientColor", Color(0.3, 0.3, 0.3, 1.0))
            self._disabled_material.setUniformValue("u_diffuseColor", self.DisabledColor)
            self._disabled_material.setUniformValue("u_specularColor", Color(1.0, 1.0, 1.0, 1.0))
            self._disabled_material.setUniformValue("u_overhangColor", Color(1.0, 0.0, 0.0, 1.0))
            self._disabled_material.setUniformValue("u_shininess", 50.0)

        if Application.getInstance().getActiveMachine():
            machine = Application.getInstance().getActiveMachine()

            if machine.getSettingValueByKey("support_enable"):
                angle = machine.getSettingValueByKey("support_angle")
                if angle != None:
                    self._enabled_material.setUniformValue("u_overhangAngle", math.cos(math.radians(90 - angle)))
            else:
                self._enabled_material.setUniformValue("u_overhangAngle", math.cos(math.radians(0)))

        for node in DepthFirstIterator(scene.getRoot()):
            if not node.render(renderer):
                if node.getMeshData() and node.isVisible():
                    # TODO: Find a better way to handle this
                    if hasattr(node, "_outside_buildarea"):
                        if node._outside_buildarea:
                            renderer.queueNode(node, material = self._disabled_material)
                        else:
                            renderer.queueNode(node, material = self._enabled_material)
                    else:
                        renderer.queueNode(node, material = self._enabled_material)

    def endRendering(self):
        pass

    def _onPreferenceChanged(self, preference):
        if preference == "view/show_overhang": ## Todo: This a printer only setting. Should be removed from Uranium.
            self._enabled_material = None
