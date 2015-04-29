from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices

from UM.Application import Application
from UM.Logger import Logger
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.SceneNode import SceneNode
from UM.Scene.PointCloudNode import PointCloudNode
from UM.Mesh.MeshData import MeshType
from UM.Mesh.ReadMeshJob import ReadMeshJob
from UM.Mesh.WriteMeshJob import WriteMeshJob
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Message import Message

import os.path

class MeshFileHandlerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._mesh_handler = Application.getInstance().getMeshFileHandler()
        self._scene = Application.getInstance().getController().getScene()

    @pyqtProperty("QStringList", constant=True)
    def supportedReadFileTypes(self):
        file_types = []
        all_types = []

        for ext, desc in self._mesh_handler.getSupportedFileTypesRead().items():
            file_types.append("{0} (*.{1})(*.{1})".format(desc, ext))
            all_types.append("*.{0}".format(ext))

        file_types.sort()
        file_types.insert(0, "All Supported Types ({0})({0})".format(" ".join(all_types)))
        file_types.append("All Files (*.*)(*)")

        return file_types

    @pyqtProperty("QStringList", constant=True)
    def supportedWriteFileTypes(self):
        file_types = []

        for ext, desc in self._mesh_handler.getSupportedFileTypesWrite().items():
            file_types.append("{0} (*.{1})(*.{1})".format(desc, ext))

        file_types.sort()

        return file_types

    @pyqtSlot(QUrl)
    def readLocalFile(self, file):
        if not file.isValid():
            return

        job = ReadMeshJob(file.toLocalFile())
        job.finished.connect(self._readMeshFinished)
        job.start()


    @pyqtSlot(QUrl)
    def writeLocalFile(self, file):
        if not file.isValid():
            return
        app = Application.getInstance()
        for node in DepthFirstIterator(self._scene.getRoot()):
            if (type(node) is not SceneNode and type(node) is not PointCloudNode) or not node.getMeshData():
                continue

            job = WriteMeshJob(file.toLocalFile(), node.getMeshData())
            job.start()
            job.finished.connect(self._onWriteJobFinished)

    def _readMeshFinished(self, job):
        mesh = job.getResult()
        if mesh != None:
            if mesh.getType() is MeshType.pointcloud:  #Depending on the type we need a different node (as pointclouds are rendered differently)
                node = PointCloudNode()
            else:
                node = SceneNode()

            node.setSelectable(True)
            node.setMeshData(mesh)
            node.setName(os.path.basename(job.getFileName()))

            op = AddSceneNodeOperation(node, self._scene.getRoot())
            op.push()

            self._scene.sceneChanged.emit(node)
        else:
            print("No mesh :(")

    def _onWriteJobFinished(self, job):
        message = Message("Saved to {0}".format(job.getFileName()))
        message.addAction("Open Folder", "open", "Open the folder containing the saved file")
        message._file = job.getFileName()
        message.actionTriggered.connect(self._onMessageActionTriggered)
        message.show()

    def _onMessageActionTriggered(self, message, action):
        if action == "Open Folder":
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(message._file)))

def createMeshFileHandlerProxy(engine, script_engine):
    return MeshFileHandlerProxy()
