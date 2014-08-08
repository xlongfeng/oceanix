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
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from ui_topsellingproducts import Ui_TopSellingProducts

import ebaysdk
from ebaysdk.merchandising import Connection as Merchandising


class TopSellingProducts(QWidget):
    def __init__(self, parent=None):
        super(TopSellingProducts, self).__init__(parent)
        
        self.ui = Ui_TopSellingProducts()
        self.ui.setupUi(self)
        self.ui.tableWidget.setColumnCount(5);
        self.ui.tableWidget.setColumnWidth(0, 120);
        self.ui.tableWidget.setColumnWidth(1, 480);
        
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.on_finished)
        self.manager.sslErrors.connect(self.on_sslErrors)
        
        self.replyMap = dict()
        
    @pyqtSlot(bool)    
    def on_wipePushButton_clicked(self, checked):
        while self.ui.tableWidget.rowCount() > 0:
            self.ui.tableWidget.removeRow(0)
        
    @pyqtSlot(bool)    
    def on_searchPushButton_clicked(self, checked):
        merchandising = Merchandising(warnings = False)
        response = merchandising.execute('getTopSellingProducts')
        reply = response.reply
        productRecommendations = reply.productRecommendations.product
        row = self.ui.tableWidget.rowCount()
        for product in productRecommendations:
            self.ui.tableWidget.insertRow(row)
            if product.has_key('imageURL'):
                imageUrl = product.imageURL
                reply = self.manager.get(QNetworkRequest(QUrl(imageUrl)))
                self.replyMap[reply] = row
            viewProductURL = QLabel()
            viewProductURL.setOpenExternalLinks(True)
            #viewProductURL.setTextInteractionFlags(Qt.TextBrowserInteraction)
            title = '<a href="%s">%s</a>' % (product.productURL, product.title)
            viewProductURL.setText(title)
            self.ui.tableWidget.setCellWidget(row, 1, viewProductURL)
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(product.catalogName))
            if product.has_key('priceRangeMin') and product.has_key('priceRangeMax'):
                self.ui.tableWidget.setItem(row, 3, QTableWidgetItem('%s - %s' % (product.priceRangeMin.value, product.priceRangeMax.value)))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(product.reviewCount))
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
            self.ui.tableWidget.setRowHeight(row, 120)
    
    @pyqtSlot(QNetworkReply, list)
    def on_sslErrors(self, reply, errors):
        if reply in self.replyMap:
            del self.replyMap[reply]
