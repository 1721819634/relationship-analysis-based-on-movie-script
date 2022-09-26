# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'net_show.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from visual_data import v_main
from deal_script_data import de_main
import os
from ui.net_change import NetchWidget
from ui.intimacy_show import ImWidget

data_dir = 'D:/PyC/Projects/relationship_analysis/analysis_data/'

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1257, 790)
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(120, 20, 821, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(10, 20, 93, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.choose_file)

        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(20, 70, 141, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.create_net)

        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(290, 70, 141, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.netCh_show)

        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setGeometry(QtCore.QRect(290, 120, 161, 28))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.intimacy_show)

        self.horizontalLayoutWidget = QtWidgets.QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(520, 50, 730, 730))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayoutWidget = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 160, 501, 621))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.cb = QtWidgets.QComboBox(self)
        self.cb.setGeometry(QtCore.QRect(120, 120, 111, 28))
        self.cb.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.cb.setObjectName("cb")

        self.pushButton_5 = QtWidgets.QPushButton(Form)
        self.pushButton_5.setGeometry(QtCore.QRect(20, 120, 93, 28))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.clicked.connect(self.select_scene)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.netHtml = QWebEngineView()
        self.horizontalLayout.addWidget(self.netHtml)
        self.taHtml = QWebEngineView()
        self.verticalLayout.addWidget(self.taHtml)

        self.file_name = None
        self.n_dict = None
        self.label_doc = None
        self.scene_ids = None

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "电影剧本人物关系分析系统"))
        self.pushButton.setText(_translate("Form", "导入剧本"))
        self.pushButton_2.setText(_translate("Form", "生成社会网络"))
        self.pushButton_3.setText(_translate("Form", "网络演化分析"))
        self.pushButton_4.setText(_translate("Form", "关系亲密度演化分析"))
        self.pushButton_5.setText(_translate("Form", "选择情节"))

    def show_msg(self, msg):
        QtWidgets.QMessageBox.information(self, "提示框", msg, QtWidgets.QMessageBox.Ok)

    def choose_file(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(None, "选取文件夹", "D:/PyC/Projects/relationship_analysis/scripts",
                                                          "Text Files (*.txt)")  # 起始路径
        path = directory[0]
        if path != '':
            self.lineEdit.setText(path)
            result = de_main(path)
            self.file_name = result['data']
            self.show_msg(result['msg'])

    def create_net(self):
        if self.file_name is None:
            self.show_msg('还未读入文件！')
        else:
            result = v_main(self.file_name)
            datas = result['data']
            self.label_doc = datas['label_doc']
            self.n_dict = datas['n_dict']
            self.scene_ids = datas['scene_ids']
            self.show_msg('社会网络生成完毕！')
            self.cb.addItem('整个剧本')
            for id in self.scene_ids:
                self.cb.addItem(f'情节 {id}')
            self.show_net('0')

    def select_scene(self):
        select = self.cb.currentText()
        if select == "整个剧本":
            scene_id = '0'
        else:
            scene_id = select.split(' ')[-1]
        self.show_net(scene_id)

    def show_net(self, scene_id):
        net_dir = os.path.join(data_dir, self.file_name, 'social_network').replace('\\', '/')
        path1 = os.path.join(net_dir, scene_id + '_net.html').replace('\\', '/')
        path2 = os.path.join(net_dir, scene_id + '_centrality.html').replace('\\', '/')

        if os.path.exists(path1):
            self.netHtml.load(QUrl(f"file:{path1}"))
        else:
            self.netHtml.setHtml('''<!DOCTYPE html>
                                <html lang="en">
                                <head>
                                    <meta charset="UTF-8">
                                    <title>Title</title>
                                </head>
                                <body>
                                <h1>无对应网络!</h1>
                                </body>
                                </html>''')

        if os.path.exists(path2):
            self.taHtml.load(QUrl(f"file:{path2}"))
        else:
            # self.textBrowser.setText('无对应数据！')
            self.taHtml.setHtml('''<!DOCTYPE html>
                                <html lang="en">
                                <head>
                                    <meta charset="UTF-8">
                                    <title>Title</title>
                                </head>
                                <body>
                                <h1>无对应数据!</h1>
                                </body>
                                </html>''')

    def netCh_show(self):
        self.netCh_window = NetchWidget(self.file_name)
        self.netCh_window.show()

    def intimacy_show(self):
        self.im_window = ImWidget(self.file_name, self.n_dict, self.label_doc)
        self.im_window.show()












