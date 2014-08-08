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


from PyQt5.QtWidgets import QDialog, QWidget, QTableWidgetItem, QLabel
from PyQt5.QtCore import pyqtSlot, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest, QNetworkReply

from ui_mostwatcheditems import Ui_MostWatchedItems
from categoryinfodialog import CategoryInfoDialog

import ebaysdk
from ebaysdk.merchandising import Connection as Merchandising


class MostWatchedItems(QWidget):
    def __init__(self, parent=None):
        super(MostWatchedItems, self).__init__(parent)
        
        self.ui = Ui_MostWatchedItems()
        self.ui.setupUi(self)
        self.ui.tableWidget.setColumnCount(5)
        self.ui.tableWidget.setColumnWidth(0, 160)
        self.ui.tableWidget.setColumnWidth(1, 480)
        
        self.categoryID = ''
        
        self.manager = QNetworkAccessManager(self)
        diskCache = QNetworkDiskCache(self)
        diskCache.setCacheDirectory("cache")
        self.manager.setCache(diskCache)
        self.manager.finished.connect(self.on_finished)
        self.manager.sslErrors.connect(self.on_sslErrors)
        
        self.replyMap = dict()
        
    @pyqtSlot(bool)
    def on_selectPushButton_clicked(self, checked):
        dialog = CategoryInfoDialog.instance()
        res = dialog.exec()
        if res == QDialog.Accepted:
            self.ui.categoryLineEdit.setText('%s -> %s' % (dialog.categoryID(), dialog.categoryNamePath()))
            self.categoryID = dialog.categoryID()
    
    @pyqtSlot(bool)    
    def on_clearPushButton_clicked(self, checked):
        self.ui.categoryLineEdit.setText('')
        self.categoryID = ''
        
    @pyqtSlot(bool)    
    def on_wipePushButton_clicked(self, checked):
        while self.ui.tableWidget.rowCount() > 0:
            self.ui.tableWidget.removeRow(0)
        
    @pyqtSlot(bool)    
    def on_searchPushButton_clicked(self, checked):
        if self.categoryID != '' and self.categoryID != '-1':
            merchandising = Merchandising(warnings = False)
            response = merchandising.execute(
                'getMostWatchedItems',
                {
                    'categoryId': self.categoryID,
                    'maxResults': self.ui.spinBox.value()
                }
            )
            reply = response.reply
            itemRecommendations = reply.itemRecommendations.item
            row = self.ui.tableWidget.rowCount()
            for item in itemRecommendations:
                self.ui.tableWidget.insertRow(row)
                imageUrl = 'http://thumbs3.ebaystatic.com/pict/%s4040.jpg' % item.itemId
                request = QNetworkRequest(QUrl(imageUrl))
                request.setAttribute(QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferCache)
                reply = self.manager.get(request)
                self.replyMap[reply] = row
                viewItemURL = QLabel()
                viewItemURL.setOpenExternalLinks(True)
                #viewItemURL.setTextInteractionFlags(Qt.TextBrowserInteraction)
                title = '<a href="%s">%s</a>' % (item.viewItemURL, item.title)
                viewItemURL.setText(title)
                self.ui.tableWidget.setCellWidget(row, 1, viewItemURL)
                self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(item.primaryCategoryName))
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(item.buyItNowPrice.value))
                self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(item.watchCount))
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
