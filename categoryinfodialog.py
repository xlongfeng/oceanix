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


from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QMessageBox, QWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, pyqtSlot

from ui_categoryinfo import Ui_CategoryInfo

import ebaysdk
from ebaysdk.shopping import Connection as Shopping

from sqlalchemy import create_engine, func, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    category_id = Column(String)
    category_parent_id = Column(String)
    leaf_category = Column(String)

engine = create_engine('sqlite:///./0.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

class CategoryInfoDialog(QDialog):
    pInstance = None
    
    def __init__(self, parent=None):
        super(CategoryInfoDialog, self).__init__(parent)
        
        self.ui = Ui_CategoryInfo()
        self.ui.setupUi(self)
        self.resize(800, 600)
        
        root = QTreeWidgetItem(self.ui.treeWidget, ['All Categories', '-1', 'Root', 'false'])
        root.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        
    @classmethod
    def instance(cls):
        if cls.pInstance is None:
            cls.pInstance = cls()
        return cls.pInstance
    
    @pyqtSlot(QTreeWidgetItem, int)
    def on_treeWidget_itemClicked(self, item, column):
        '''
        if item.text(3) == 'true':
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setDisabled(True)
        '''
    
    @pyqtSlot(QTreeWidgetItem)
    def on_treeWidget_itemExpanded(self, item):
        if item.checkState(1) != Qt.Checked:
            categoryParentID = item.text(1)
            session = Session()
            count = session.query(Category).filter(Category.category_parent_id == categoryParentID).count()
            if count == 0:
                shopping = Shopping(warnings = False)
                response = shopping.execute(
                    'GetCategoryInfo',
                    {
                        'CategoryID': categoryParentID,
                        'IncludeSelector': 'ChildCategories'
                    }
                )
                reply = response.reply
                categoryArray = reply.CategoryArray.Category
                for category in categoryArray:
                    if category.CategoryID == categoryParentID:
                        continue
                    session.add(Category(
                        name=category.CategoryName,
                        path=category.CategoryNamePath,
                        category_id=category.CategoryID,
                        category_parent_id=category.CategoryParentID,
                        leaf_category=category.LeafCategory)
                    )
                session.commit()
                
            for category in session.query(Category).filter(Category.category_parent_id == categoryParentID).order_by(Category.id).all():
                child = QTreeWidgetItem(item, [category.name, category.category_id, category.path, category.leaf_category])
                if category.leaf_category == 'false':
                    child.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            item.setCheckState(1, Qt.Checked)
    
    def categoryID(self):
        return self.ui.treeWidget.currentItem().text(1)
    
    def categoryNamePath(self):
        return self.ui.treeWidget.currentItem().text(2)
