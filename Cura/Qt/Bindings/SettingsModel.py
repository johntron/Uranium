from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot

from Cura.Qt.ListModel import ListModel

class SettingsModel(ListModel):
    
    NameRole = Qt.UserRole + 1
    CategoryRole =Qt.UserRole + 2
    CollapsedRole = Qt.UserRole + 3
    TypeRole = Qt.UserRole + 4
    ValueRole = Qt.UserRole + 5
    ValidRole = Qt.UserRole + 6
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._machine_settings = QCoreApplication.instance().getMachineSettings()
        self._updateSettings()
        
    def roleNames(self):
        return {self.NameRole:'name', self.CategoryRole:"category", self.CollapsedRole:"collapsed",self.TypeRole:"type",self.ValueRole:"value",self.ValidRole:"valid"}
        
    def _updateSettings(self):
        self.clear()
        settings = self._machine_settings.getAllSettings()
        for setting in settings:
            self.appendItem({"name":setting.getLabel(),"category":setting.getCategory().getLabel(),"collapsed":True,"type":setting.getType(),"value":setting.getValue(),"valid":setting.validate()})
            
    @pyqtSlot(str)
    def toggleCollapsedByCategory(self, category_key):
        for index in range(0, len(self.items)):
            item = self.items[index]
            if item["category"] == category_key:
                self.setProperty(index, 'collapsed', not item['collapsed'])
    
    @pyqtSlot(int, str, str)
    def settingChanged(self, index, key, value):
        #index = self.items.index(key)
        if self._machine_settings.getSettingByKey(key) is not None:
            self._machine_settings.getSettingByKey(key).setValue(value)
        self.setProperty(index,'valid', self.isValid(key))
    
    @pyqtSlot(str,result=int)
    def isValid(self,key):
        if self._machine_settings.getSettingByKey(key) is not None:
            return self._machine_settings.getSettingByKey(key).validate()
        return 5
        
        
        