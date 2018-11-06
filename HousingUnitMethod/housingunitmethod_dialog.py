# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HousingUnitMethodDialog
                                 A QGIS plugin
 Estimate populatiion using HUT and addresses opendata
                             -------------------
        begin                : 2018-04-07
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Nelson Mileu
        email                : nmileu@campus.ul.pt
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from qgiscombomanager import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'housingunitmethod_dialog_base.ui'))


class HousingUnitMethodDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(HousingUnitMethodDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
	self.layerComboManager1 = VectorLayerCombo(self.comboBox_LayerA,"",{"hasGeometry": True})
	self.fieldComboManager1 = FieldCombo(self.comboBox_FieldPop, self.layerComboManager1)
	self.fieldComboManager2 = FieldCombo(self.comboBox_FieldHousing, self.layerComboManager1)
	self.layerComboManager2 = VectorLayerCombo(self.comboBox_LayerB,"",{"hasGeometry": True})
		
	self.browseButton.clicked.connect(self.browse)

    def browse(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self, self.trUtf8(u"Base directory"))
        if directory:
            self.baseDirectory.setText(directory)