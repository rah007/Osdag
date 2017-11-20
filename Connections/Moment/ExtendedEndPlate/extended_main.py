"""
Created on 24-Aug-2017

@author: Reshma
"""

from ui_extendedendplate  import  Ui_MainWindow
from ui_design_preferences import Ui_Dialog
from drawing_2D import ExtendedEndPlate
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from PyQt5.Qt import QColor, QBrush, Qt
from model import *
import sys
import os

class DesignPreference(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.maincontroller = parent


class Maincontroller(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.resultobj = None
        self.ui.combo_connLoc.setCurrentIndex(0)
        self.ui.combo_connLoc.currentIndexChanged.connect(self.get_beamdata)
        self.ui.combo_beamSec.setCurrentIndex(0)
        self.get_beamdata()
        self.gradeType = {'Please select type': '', 'HSFG': [8.8, 10.9],
                          'Bearing Bolt': [3.6, 4.6, 4.8, 5.6, 5.8, 6.8, 8.8, 9.8, 10.9, 12.9]}
        self.ui.combo_type.addItems(self.gradeType.keys())
        self.ui.combo_type.currentIndexChanged[str].connect(self.combotype_current_index_changed)
        self.ui.combo_type.setCurrentIndex(0)
        # self.retrieve_prestate()

        self.ui.btnFront.clicked.connect(lambda : self.call_2D_drawing("Front"))
        self.ui.btnTop.clicked.connect(lambda : self.call_2D_drawing("Top"))
        self.ui.btnSide.clicked.connect(lambda : self.call_2D_drawing("Side"))

        self.ui.btn_Design.clicked.connect(self.design_btnclicked)
        self.ui.btn_Reset.clicked.connect(self.reset_btnclicked)
        self.ui.actionDesign_Preferences.triggered.connect(self.design_prefer)


        min_fu = 290
        max_fu = 590
        self.ui.txt_Fu.editingFinished.connect(lambda: self.check_range(self.ui.txt_Fu, min_fu, max_fu))

        min_fy = 165
        max_fy = 450
        self.ui.txt_Fy.editingFinished.connect(lambda: self.check_range(self.ui.txt_Fy, min_fy, max_fy))

    def get_user_inputs(self):
        uiObj = {}
        uiObj["Member"] = {}
        uiObj["Member"]["Connectivity"] = str(self.ui.combo_connLoc.currentText())
        uiObj["Member"]["BeamSection"] = str(self.ui.combo_beamSec.currentText())
        uiObj["Member"]["fu (MPa)"] = self.ui.txt_Fu.text()
        uiObj["Member"]["fy (MPa)"] = self.ui.txt_Fy.text()

        uiObj["Load"] = {}
        uiObj["Load"]["ShearForce (kN)"] = self.ui.txt_Shear.text()
        uiObj["Load"]["Moment (kNm)"] = self.ui.txt_Moment.text()
        uiObj["Load"]["AxialForce"] = self.ui.txt_Axial.text()

        uiObj["Bolt"] = {}
        uiObj["Bolt"]["Diameter (mm)"] = self.ui.combo_diameter.currentText()
        uiObj["Bolt"]["Grade"] = self.ui.combo_grade.currentText()
        uiObj["Bolt"]["Type"] = self.ui.combo_type.currentText()

        uiObj["Plate"] = {}
        uiObj["Plate"]["Thickness (mm)"] = self.ui.combo_plateThick.currentText()
        uiObj["Plate"]["Height (mm)"] = self.ui.txt_plateHeight.text()
        uiObj["Plate"]["Width (mm)"] = self.ui.txt_plateWidth.text()

        uiObj["Weld"] = {}
        uiObj["Weld"]["Flange (mm)"] = self.ui.combo_flangeSize.currentText()
        uiObj["Weld"]["Web (mm)"] = self.ui.combo_webSize.currentText()
        return uiObj

    def design_prefer(self):
        section = DesignPreference(self)
        section.show()

    def design_btnclicked(self):
        self.uiObj = self.get_user_inputs()
        # outputs = extendedendplate(self.uiObj)

    def reset_btnclicked(self):
        self.ui.combo_beamSec.setCurrentIndex(0)
        self.ui.combo_connLoc.setCurrentIndex(0)
        self.ui.txt_Fu.clear()
        self.ui.txt_Fy.clear()
        self.ui.txt_Axial.clear()
        self.ui.txt_Shear.clear()
        self.ui.txt_Moment.clear()
        self.ui.combo_diameter.setCurrentIndex(0)
        self.ui.combo_type.setCurrentIndex(0)
        self.ui.combo_grade.setCurrentIndex(0)
        self.ui.combo_plateThick.setCurrentIndex(0)
        self.ui.txt_plateHeight.clear()
        self.ui.txt_plateWidth.clear()
        self.ui.combo_flangeSize.setCurrentIndex(0)
        self.ui.combo_webSize.setCurrentIndex(0)

    def get_beamdata(self):
        loc = self.ui.combo_connLoc.currentText()
        if loc == 'Flush' or loc == 'Extended one way' or loc == 'Extended both ways':
            beamdata = get_beamcombolist()
            old_beamdata = get_oldbeamcombolist()
            self.ui.combo_beamSec.addItems(beamdata)
            self.color_oldDatabase_section(old_beamdata, beamdata, self.ui.combo_beamSec)

    def color_oldDatabase_section(self, old_section, intg_section, combo_section):
        """

        Args:
            old_section: Old database
            intg_section: Integrated database

        Returns: Differentiate the database by color code

        """
        for col in old_section:
            if col in intg_section:
                indx = intg_section.index(str(col))
                combo_section.setItemData(indx, QBrush(QColor("red")), Qt.TextColorRole)

        duplicate = [i for i, x in enumerate(intg_section) if intg_section.count(x) > 1]
        for i in duplicate:
            combo_section.setItemData(i, QBrush(QColor("red")), Qt.TextColorRole)

    def fetchBeamPara(self):
        beamdata_sec = self.ui.combo_beamSec.currentText()
        dictbeamdata = get_beamdata(beamdata_sec)
        return  dictbeamdata

    def combotype_current_index_changed(self, index):
        """

        Args:
            index: Number

        Returns: Types of Grade

        """
        items = self.gradeType[str(index)]
        if items != 0 :
            self.ui.combo_grade.clear()
            stritems = []
            for val in items:
                stritems.append(str(val))

            self.ui.combo_grade.addItems(stritems)
        else:
            pass

    def check_range(self, widget, min_val, max_val):
        """

        Args:
            widget: Fu , Fy lineedit
            min_val: min value
            max_val: max value

        Returns: Check for the value mentioned for the given range

        """
        text_str = widget.text()
        text_str = int(text_str)
        if (text_str < min_val or text_str > max_val or text_str == ''):
            QMessageBox.about(self, "Error", "Please enter a value between %s-%s"%(min_val, max_val))
            widget.clear()
            widget.setFocus()




    def call_2D_drawing(self, view):
        beam_beam = ExtendedEndPlate()
        if view == "Front":
            filename = "D:\PyCharmWorkspace\Osdag\Connections\Moment\ExtendedEndPlate\Front.svg"
            beam_beam.save_to_svg(filename, view)
        elif view == "Side":
            filename = "D:\PyCharmWorkspace\Osdag\Connections\Moment\ExtendedEndPlate\Side.svg"
            beam_beam.save_to_svg(filename, view)
        else:
            filename = "D:\PyCharmWorkspace\Osdag\Connections\Moment\ExtendedEndPlate\Top.svg"
            beam_beam.save_to_svg(filename, view)


def main():
    app = QApplication(sys.argv)
    window = Maincontroller()
    module_setup()
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()