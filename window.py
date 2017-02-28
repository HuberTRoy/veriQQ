import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import api


class Window(QWidget):
    setItem = pyqtSignal(int, str)

    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("QQ批量验证工具")
        self.setItem.connect(self.setTableItems)
        self.resize(600, 500)
        self.workThread = WorkerThread(self)
        self.workThread.setTarget(self.versQQ)
        self.fromToFile = QPushButton("导入")
        self.fromToFile.clicked.connect(self.fromToFiles)
        self.startVer = QPushButton("开始验证")
        self.startVer.clicked.connect(self.workThread.start)
        self.stopVer = QPushButton("停止验证")
        self.stopVer.clicked.connect(self.workThread.exit)


        self.versDialog = VersDialog(self)

        # self.vcodeLabel = QLabel("验证码: ")
        # self.vcodeImg = QLabel()
        # self.vcodeImg.setObjectName("vcodeImg")
        # self.vcodeImg.setMaximumSize(130, 53)
        # self.vcodeImg.setMinimumSize(130, 53)
        # self.vcodeLine = QLineEdit()

        self.showTables = QTableWidget()
        self.showTables.setColumnCount(3)
        self.showTables.setColumnWidth(0, self.width()/3)
        self.showTables.setColumnWidth(1, self.width()/3)
        self.showTables.setColumnWidth(2, self.width()/3)
        self.showTables.setHorizontalHeaderLabels(["账号", "密码", "状态"])
        self.showTables.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.mainLayout = QVBoxLayout(self)
        self.topLayout = QHBoxLayout()
        self.topLayout.addWidget(self.fromToFile)
        self.topLayout.addWidget(self.startVer)
        self.topLayout.addWidget(self.stopVer)
        # self.topLayout.addWidget(self.vcodeLabel)
        # self.topLayout.addWidget(self.vcodeImg)
        # self.topLayout.addWidget(self.vcodeLine)
        self.mainLayout.addLayout(self.topLayout)

        self.mainLayout.addWidget(self.showTables)

    def fromToFiles(self):
        file_dio = QFileDialog()
        filename = file_dio.getOpenFileName()[0]
        with open(filename, 'r', encoding='utf-8') as f:
            datas = f.readlines()
            self.showTables.setRowCount(len(datas))
            for i in enumerate(datas):
                data = i[1].split(' ')
                self.showTables.setItem(i[0], 0, QTableWidgetItem(data[0]))
                self.showTables.setItem(i[0], 1, QTableWidgetItem(data[1].strip()))
                self.showTables.setItem(i[0], 2, QTableWidgetItem())

    def versQQ(self):
        allRow = self.showTables.rowCount()
        for i in range(allRow):
            username = self.showTables.item(i, 0).text()
            password = self.showTables.item(i, 1).text()
            #获取需不需要验证码。
            getVers = api.getVer(username)
            if getVers[0] == 0:
                # 不需要验证码。
                result = api.login_qq(username, password, *getVers[1:])
                if result == 'OK':
                    self.setItem.emit(i, "密码正确")
                else:
                    self.setItem.emit(i, "密码错误或异常")
            else:
                # 需要验证码。
                self.versDialog.vcodeImg.setStyleSheet('QLabel{border-image:url(catch/verifycode.jpg)}')
                self.versDialog.exec_()
                verifycode = self.versDialog.vcodeLine.text()
                result = api.login_qq(username, password, verifycode, *getVers[1:])
                if result == 'OK':
                    self.setItem.emit(i, "密码正确")
                else:
                    self.setItem.emit(i, "密码错误或异常")
                self.versDialog.vcodeLine.setText('')

    def setTableItems(self, line, text):
        self.showTables.item(line, 2).setText(text)

class VersDialog(QDialog):
    def __init__(self, parent=None):
        super(VersDialog, self).__init__()
        self.parent = parent
        self.setWindowTitle('输入验证码: 输入完成后会自动填入')
        self.vcodeImg = QLabel()
        self.vcodeImg.setObjectName("vcodeImg")
        self.vcodeImg.setMaximumSize(130, 53)
        self.vcodeImg.setMinimumSize(130, 53)
        self.vcodeLine = QLineEdit()
        self.vcodeLine.textChanged.connect(self.vcodeEvent)
        self.setStyleSheet('QLabel#vcodeImg{border: 1px solid;}')

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.vcodeImg)
        self.mainLayout.addWidget(self.vcodeLine)

    def vcodeEvent(self):
        if len(self.vcodeLine.text()) == 4:
            self.accept()


class TipDialog(QDialog):
    """提示框功能，需要一个文本参数。"""
    def __init__(self, text=None):
        super(TipDialog, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('完成提示')

        self.resize(270, 160)
        self.setStyleSheet("""QFrame#top_frame{background: #222222;}QLabel{color: #55aaff; font-size: 20px; font-weight: bold;} QPushButton {color:#313131; border: 0px;border-style: solid; font-size: 20px; font-weight: bold;} QPushButton::hover{color: #888888;}""")
        self.top_frame = QFrame()
        self.top_frame.setObjectName('top_frame')

        self.icon_label = QLabel(self.top_frame)

        self.top_text_label = QLabel(self.top_frame)

        self.top_text_label.setText('完成提示')

        self.close_button = QPushButton('×')
        self.close_button.clicked.connect(self.close)
        self.close_button.setMinimumSize(24, 24)

        # 正文提示内容。
        self.content_label = QLabel()
        self.content_label.setText(text)
        self.content_label.setWordWrap(True)

        self.closeButton = QPushButton()
        self.closeButton.setText('关闭')
        self.closeButton.clicked.connect(self.close)

        self.main_layout = QVBoxLayout()

        self.top_layout = QHBoxLayout()

        self.bottom_layout = QHBoxLayout()

        self.main_layout.addWidget(self.top_frame)
        self.main_layout.addWidget(self.content_label)
        self.main_layout.addLayout(self.bottom_layout)
        self.main_layout.addSpacing(10)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 2)
        self.main_layout.setStretch(2, 1)

        self.top_layout.addWidget(self.icon_label)
        self.top_layout.addWidget(self.top_text_label)
        self.top_layout.addWidget(self.close_button)
        self.top_layout.setStretch(0, 1)
        self.top_layout.setStretch(1, 2)
        self.top_layout.setStretch(2, 1)

        self.bottom_layout.addStretch(1)
        self.bottom_layout.addWidget(self.closeButton)
        self.bottom_layout.addStretch(1)

        self.top_frame.setLayout(self.top_layout)

        self.setLayout(self.main_layout)


class WorkerThread(QThread):
    """异步请求，类似Pyhton封装的Thread形式，用QThread在简单封装一下。"""
    def __init__(self, parent=None, target=None, *args, **kwargs):
        super(WorkerThread, self).__init__()

        self.parent = parent
        self.args = args
        self.kwargs = kwargs
        self.target = target

    def run(self):
        self.target(*self.args, **self.kwargs)
        
    def setTarget(self, target=None):
        """方便多次调用。"""
        self.target = target

    def setArgs(self, *args, **kwargs):
        """方便多次调用。"""
        self.args = args
        self.kwargs = kwargs



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())