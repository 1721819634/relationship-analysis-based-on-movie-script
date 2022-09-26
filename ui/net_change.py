# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'net_change.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os


class Ui_NetchForm(object):
    def setupUi(self, NetchForm, file_name):
        NetchForm.setObjectName("NetchForm")
        NetchForm.resize(945, 584)
        self.verticalLayoutWidget = QtWidgets.QWidget(NetchForm)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 921, 551))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.netHtml = QWebEngineView()
        path = os.path.join('D:/PyC/Projects/relationship_analysis/analysis_data',
                            file_name, 'social_network/scene_analysis.html').replace('\\', '/')
        self.netHtml.load(QUrl(f"file:{path}"))
        self.verticalLayout.addWidget(self.netHtml)

        self.retranslateUi(NetchForm)
        QtCore.QMetaObject.connectSlotsByName(NetchForm)

    def retranslateUi(self, NetchForm):
        _translate = QtCore.QCoreApplication.translate
        NetchForm.setWindowTitle(_translate("NetchForm", "电影剧本人物关系分析系统"))


class NetchWidget(QtWidgets.QWidget, Ui_NetchForm):
    def __init__(self, file_name):
        super(NetchWidget, self).__init__()
        self.setupUi(self, file_name=file_name)