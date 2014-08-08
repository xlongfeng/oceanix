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

from ui_popularitems import Ui_PopularItems
from categoryinfodialog import CategoryInfoDialog

import ebaysdk
from ebaysdk.shopping import Connection as Shopping


class PopularItems(QWidget):
    def __init__(self, parent=None):
        super(PopularItems, self).__init__(parent)
        
        self.ui = Ui_PopularItems()
        self.ui.setupUi(self)
        self.ui.categoryTreeWidget.setColumnCount(2)
        self.ui.tableWidget.setColumnCount(5)
        self.ui.tableWidget.setColumnWidth(0, 160)
        self.ui.tableWidget.setColumnWidth(1, 480)
               
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.on_finished)
        self.manager.sslErrors.connect(self.on_sslErrors)
        
        self.replyMap = dict()
        
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
        self.ui.categoryTreeWidget.clear()
        
    @pyqtSlot(bool)    
    def on_wipePushButton_clicked(self, checked):
        while self.ui.tableWidget.rowCount() > 0:
            self.ui.tableWidget.removeRow(0)
        
    @pyqtSlot(bool)
    def on_searchPushButton_clicked(self, checked):
        categoryCount = self.ui.categoryTreeWidget.topLevelItemCount()
        queryKeywords = self.ui.queryKeywordsLineEdit.text()
        if categoryCount == 0 and queryKeywords == '':
            return
        categoryID = None
        if categoryCount == 1:
            categoryID = self.ui.categoryTreeWidget.topLevelItem(0).text(0)
        elif categoryCount > 1:
            categoryID = list()
            for i in range(0, categoryCount):
                categoryID.append(self.ui.categoryTreeWidget.topLevelItem(i).text(0))
        shopping = Shopping(warnings = False, trackingpartnercode=2)
        data = {'MaxEntries': self.ui.spinBox.value()}
        if categoryID != None:
            data['CategoryID'] = categoryID
        if queryKeywords != '':
            data['QueryKeywords'] = self.ui.queryKeywordsLineEdit.text()
        response = shopping.execute('FindPopularItems', data)
        reply = response.reply
        itemArray = reply.ItemArray.Item
        row = self.ui.tableWidget.rowCount()
        for item in itemArray:
            self.ui.tableWidget.insertRow(row)
            imageUrl = 'http://thumbs3.ebaystatic.com/pict/%s4040.jpg' % item.ItemID
            reply = self.manager.get(QNetworkRequest(QUrl(imageUrl)))
            self.replyMap[reply] = row
            viewItemURL = QLabel()
            viewItemURL.setOpenExternalLinks(True)
            #viewItemURL.setTextInteractionFlags(Qt.TextBrowserInteraction)
            title = '<a href="%s">%s</a>' % (item.ViewItemURLForNaturalSearch, item.Title)
            viewItemURL.setText(title)
            self.ui.tableWidget.setCellWidget(row, 1, viewItemURL)
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(item.PrimaryCategoryName))
            #self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(item.buyItNowPrice.value))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(item.WatchCount))
            row += 1
                
    @pyqtSlot(QNetworkReply)
    def on_finished(self, reply):
        if reply in self.replyMap:
            row = self.replyMap.get(reply)
            del self.replyMap[reply]
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            image = QLabel()
            image.setPixmap(pixmap)
            self.ui.tableWidget.setCellWidget(row, 0, image)
            self.ui.tableWidget.setRowHeight(row, 160)
    
    @pyqtSlot(QNetworkReply, list)
    def on_sslErrors(self, reply, errors):
        if reply in self.replyMap:
            del self.replyMap[reply]
