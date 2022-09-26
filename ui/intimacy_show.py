# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'intimacy_show.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from relate_analysis import nameDict
from relation_extraction import re_main
import json

social_re = ['father', 'mother', 'sibling', 'spouse', 'child']

class Ui_IntimacyForm(object):
    def setupUi(self, IntimacyForm, file_name, n_dict: nameDict, label_doc):
        IntimacyForm.setObjectName("IntimacyForm")
        IntimacyForm.resize(838, 580)
        self.file_name = file_name
        self.pushButton = QtWidgets.QPushButton(IntimacyForm)
        self.pushButton.setGeometry(QtCore.QRect(20, 20, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.data_show)

        self.verticalLayoutWidget = QtWidgets.QWidget(IntimacyForm)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 190, 821, 381))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout_2")

        self.myHtml = QWebEngineView()
        self.verticalLayout.addWidget(self.myHtml)

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(IntimacyForm)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 70, 811, 111))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout")

        self.textBrowser = QtWidgets.QTextBrowser(self.verticalLayoutWidget_2)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)

        self.comboBox = QtWidgets.QComboBox(IntimacyForm)
        self.comboBox.setGeometry(QtCore.QRect(140, 20, 93, 28))
        self.comboBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.comboBox.setObjectName("comboBox")

        self.comboBox_2 = QtWidgets.QComboBox(IntimacyForm)
        self.comboBox_2.setGeometry(QtCore.QRect(260, 20, 93, 28))
        self.comboBox_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.comboBox_2.setObjectName("comboBox_2")

        self.re_extraction(n_dict, label_doc)
        self.load_roles(n_dict)

        self.retranslateUi(IntimacyForm)
        QtCore.QMetaObject.connectSlotsByName(IntimacyForm)

    def re_extraction(self, n_dict, label_doc):
        re_path = os.path.join('analysis_data', self.file_name, 'relation_dict.json')
        if os.path.exists(re_path):
            with open(re_path, 'r') as f:
                self.relate_dict = json.load(f)
        else:
            self.relate_dict = re_main(n_dict, label_doc, self.file_name)

    def load_roles(self, n_dict: nameDict):
        roles = []
        for names in n_dict.name2id:
            roles.append(names[0])
        self.comboBox.addItems(roles)
        self.comboBox_2.addItems(roles)

    def data_show(self):
        role1 = self.comboBox.currentText()
        role2 = self.comboBox_2.currentText()
        if role1 == role2:
            self.textBrowser.setText('该角色对为同一人')
            self.myHtml.setHtml('''<!DOCTYPE html>
                                            <html lang="en">
                                            <head>
                                                <meta charset="UTF-8">
                                                <title>Title</title>
                                            </head>
                                            <body>
                                            <h1>无对应数据!</h1>
                                            </body>
                                            </html>''')
        else:
            file = role1 + '-' + role2 + '.html'
            path = os.path.join('D:/PyC/Projects/relationship_analysis/analysis_data',
                                self.file_name + '/role_related_data', file).replace('\\', '/')
            if not os.path.exists(path):
                file = role2 + '-' + role1 + '.html'
                path = os.path.join('D:/PyC/Projects/relationship_analysis/analysis_data',
                                    self.file_name + '/role_related_data', file).replace('\\', '/')
            self.myHtml.load(QUrl(f"file:{path}"))

            id1 = str(self.comboBox.currentIndex())
            id2 = str(self.comboBox_2.currentIndex())
            relate = self.relate_dict[id1][id2][0]
            if relate not in social_re:
                relate = 'unknown'
            self.textBrowser.setText(f'{role1} 与 {role2} 可能的关系为：{relate}')

    def retranslateUi(self, IntimacyForm):
        _translate = QtCore.QCoreApplication.translate
        IntimacyForm.setWindowTitle(_translate("IntimacyForm", "电影剧本人物关系分析系统"))
        self.pushButton.setText(_translate("IntimacyForm", "选择人物"))


class ImWidget(QtWidgets.QWidget, Ui_IntimacyForm):
    def __init__(self, file_name, n_dict: nameDict, label_doc):
        super(ImWidget, self).__init__()
        self.setupUi(self, file_name=file_name, n_dict=n_dict, label_doc=label_doc)
