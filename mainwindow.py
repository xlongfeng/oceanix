#############################################################################
##
## Copyright (C) 2014 xlongfeng <xlongfeng@126.com>.
## All rights reserved.
##
## This file is part of source code of OceaniX.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial Usage
## Licensees holding valid Qt Commercial licenses may use this file in
## accordance with the Qt Commercial License Agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and Nokia.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 2.1 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL included in the
## packaging of this file.  Please review the following information to
## ensure the GNU Lesser General Public License version 2.1 requirements
## will be met: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
##
## In addition, as a special exception, Nokia gives you certain additional
## rights.  These rights are described in the Nokia Qt LGPL Exception
## version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3.0 as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL included in the
## packaging of this file.  Please review the following information to
## ensure the GNU General Public License version 3.0 requirements will be
## met: http://www.gnu.org/copyleft/gpl.html.
##
## If you have questions regarding the use of this file, please contact
## Nokia at qt-info@nokia.com.
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget)

from ui_mainwindow import Ui_MainWindow
from mostwatcheditems import MostWatchedItems
from topsellingproducts import TopSellingProducts
from popularitems import PopularItems
from popularsearches import PopularSearches


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(1024, 768)
        
        self.mostWatchedItems = MostWatchedItems()
        self.ui.tabWidget.addTab(self.mostWatchedItems, 'Most Watched Items')
        
        self.topSellingProducts = TopSellingProducts()
        self.ui.tabWidget.addTab(self.topSellingProducts, 'Top Selling Products')
        
        self.popularItems = PopularItems()
        self.ui.tabWidget.addTab(self.popularItems, 'Popular Items')
        
        self.popularSearches = PopularSearches()
        self.ui.tabWidget.addTab(self.popularSearches, 'Popular Searches')
