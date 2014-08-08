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


from PyQt5.QtWidgets import QDialog, QWidget, QTableWidgetItem, QLabel, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSlot, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from ui_popularsearches import Ui_PopularSearches
from categoryinfodialog import CategoryInfoDialog

import ebaysdk
from ebaysdk.shopping import Connection as Shopping


def iterable(obj):
    if type(obj) != list:
        obj = [obj]
    return obj


class PopularSearches(QWidget):
    def __init__(self, parent=None):
        super(PopularSearches, self).__init__(parent)
        
        self.ui = Ui_PopularSearches()
        self.ui.setupUi(self)
        self.ui.categoryTreeWidget.setColumnCount(2)
        self.ui.tableWidget.setColumnCount(5)
        self.ui.tableWidget.setColumnWidth(0, 160)
        self.ui.tableWidget.setColumnWidth(1, 160)
        self.ui.tableWidget.setColumnWidth(2, 480)
        self.ui.tableWidget.setColumnWidth(3, 320)
        
    @pyqtSlot(bool)
    def on_selectPushButton_clicked(self, checked):
        if self.ui.categoryTreeWidget.topLevelItemCount() == 10:
            return
        dialog = CategoryInfoDialog.instance()
        res = dialog.exec()
        if res == QDialog.Accepted and dialog.categoryID() != '-1':
            items = self.ui.categoryTreeWidget.findItems(dialog.categoryID(), Qt.MatchFixedString, 0)
            if items == []:
                QTreeWidgetItem(self.ui.categoryTreeWidget, [dialog.categoryID(), dialog.categoryNamePath()])
                
    @pyqtSlot(bool)    
    def on_removePushButton_clicked(self, checked):
        item = self.ui.categoryTreeWidget.currentItem()
        if item:
            self.ui.categoryTreeWidget.takeTopLevelItem(self.ui.categoryTreeWidget.currentIndex().row())
    
    @pyqtSlot(bool)    
    def on_clearPushButton_clicked(self, checked):
        while self.ui.tableWidget.rowCount() > 0:
            self.ui.tableWidget.removeRow(0)
        
    @pyqtSlot(bool)    
    def on_wipePushButton_clicked(self, checked):
        self.ui.tableWidget.clear()
        
    @pyqtSlot(bool)
    def on_searchPushButton_clicked(self, checked):
        categoryCount = self.ui.categoryTreeWidget.topLevelItemCount()
        queryKeywords = self.ui.queryKeywordsLineEdit.text()
        if categoryCount == 0 and queryKeywords == '':
            return
        categoryID = None
        includeChild = self.ui.includeChildCheckBox.checkState() == Qt.Checked
        if categoryCount == 1:
            categoryID = self.ui.categoryTreeWidget.topLevelItem(0).text(0)
        elif categoryCount > 1:
            if includeChild:
                categoryID = self.ui.categoryTreeWidget.topLevelItem(0).text(0)
            else:
                categoryID = list()
                for i in range(0, categoryCount):
                    categoryID.append(self.ui.categoryTreeWidget.topLevelItem(i).text(0))
        shopping = Shopping(warnings = False, trackingpartnercode=2)
        data = {'MaxKeywords': self.ui.spinBox.value(),
                'MaxResultsPerPage': 200,
                'PageNumber': 1}
        if includeChild:
            data['IncludeChildCategories'] = True
        if categoryID != None:
            data['CategoryID'] = categoryID
        if queryKeywords != '':
            data['QueryKeywords'] = self.ui.queryKeywordsLineEdit.text()
        response = shopping.execute('FindPopularSearches', data)
        reply = response.reply
        popularSearchResult = iterable(reply.PopularSearchResult)
        row = self.ui.tableWidget.rowCount()
        for result in popularSearchResult:
            self.ui.tableWidget.insertRow(row)
            
            if result.has_key('CategoryParentName'):
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(result.CategoryParentName))
            if result.has_key('CategoryName'):
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(result.CategoryName))
            if result.has_key('RelatedSearches'):
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(result.RelatedSearches))
            if result.has_key('AlternativeSearches'):
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(result.AlternativeSearches))
            if result.has_key('QueryKeywords'):
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(result.QueryKeywords))
            row += 1
        
