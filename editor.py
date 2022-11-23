from PyQt5.QtWidgets import QWidget, QGroupBox, QLineEdit, QTextEdit, QLabel, QPushButton, QTableWidget, QComboBox, QTableWidgetItem
from PyQt5.Qt import QGridLayout, QHBoxLayout, QMessageBox, Qt, QColor, QTextCursor
import os
import json
import re

class Editor(QWidget):
    USER = 0
    SHARED = 1

    def __init__(self):
        super(Editor, self).__init__()

        self.permissions = None # {}

        self.currentUser = None # ""
        self.currentObjects = None # []

        self.teTextLen = 0

        self.setWindowTitle('МБКС ЛР2 | Лазарев Михайлин')
        self.setMinimumWidth(500)

        # +++++++++++++++++++++++++++ Folders +++++++++++++++++++++++++++

        self.gbPaths = QGroupBox('Пути')
        self.layoutPaths = QGridLayout()
        self.leSharedFolderPath = QLineEdit('Shared')
        self.lePermissionsFilePath = QLineEdit('permissions.json')

        self.layoutPaths.addWidget(QLabel('Папка сохранения: '), 0, 0)
        self.layoutPaths.addWidget(self.leSharedFolderPath, 0, 1)
        self.layoutPaths.addWidget(QLabel('Файл прав доступа: '), 1, 0)
        self.layoutPaths.addWidget(self.lePermissionsFilePath, 1, 1)

        self.gbPaths.setLayout(self.layoutPaths)

        # ++++++++++++++=++++++++++++++++++++++++++++++++++++++++++++++++

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^ Permissions ^^^^^^^^^^^^^^^^^^^^^^^^

        self.gbPermissionsView = QGroupBox('Права доступа:')
        self.lytPermissions = QGridLayout()
        self.twPermissions = QTableWidget()
        self.twPermissions.setAlternatingRowColors(True)
        self.leCommands = QLineEdit()
        self.leCommands.setToolTip('Grant (subj, priv, array[1..n])\n'
                                   'Revoke (subj, priv, array[1..n])\n'
                                   'Create (subj, array[1..n])\n'
                                   'Remove (subj, array[1..n])')
        self.btnExecuteCommand = QPushButton('Выполнить')

        self.lytPermissions.addWidget(self.twPermissions, 0, 0, 1, 3)
        self.lytPermissions.addWidget(QLabel('Команда:'), 1, 0)
        self.lytPermissions.addWidget(self.leCommands, 1, 1)
        self.lytPermissions.addWidget(self.btnExecuteCommand, 1, 2)

        self.gbPermissionsView.setLayout(self.lytPermissions)


        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        # &&&&&&&&&&&&&&&&&&&&&&&&& User select &&&&&&&&&&&&&&&&&&&&&&&&&

        self.gbUserSelection = QGroupBox('Выбор пользователя:')
        self.lytUserSelection = QGridLayout()
        self.cbUserSelect = QComboBox()
        self.lblAvailable = QLabel('Доступно:')

        self.lytUserSelection.addWidget(self.cbUserSelect, 0, 0)
        self.lytUserSelection.addWidget(self.lblAvailable, 1, 0)

        self.gbUserSelection.setLayout(self.lytUserSelection)

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

        # **************************** EDITOR ***************************

        self.gbEditor = QGroupBox('Редактор')
        self.layoutEditor = QGridLayout()
        self.leFileName = QLineEdit()
        self.teEditor = QTextEdit()
        self.layoutEditorSub = QHBoxLayout()

        self.btnOpen = QPushButton('Открыть')
        self.btnSaveFile = QPushButton('Сохранить')

        self.layoutEditorSub.setStretch(0, 1)
        self.layoutEditorSub.addWidget(self.btnSaveFile, 1)

        self.layoutEditor.addWidget(QLabel('Имя файла: '), 0, 0)
        self.layoutEditor.addWidget(self.leFileName, 0, 1)
        self.layoutEditor.addWidget(self.btnOpen, 0, 2)
        self.layoutEditor.addWidget(self.teEditor, 1, 0, 1, 3)
        self.layoutEditor.addLayout(self.layoutEditorSub, 2, 0, 1, 3)

        self.gbEditor.setLayout(self.layoutEditor)

        # ***************************************************************

        self.teEditor.textChanged.connect(self.teTextChanged)
        self.btnOpen.clicked.connect(self.btnOpenFileClicked)
        self.btnSaveFile.clicked.connect(self.btnSaveFileClicked)
        self.cbUserSelect.currentTextChanged.connect(self.cbUserSelectIndexChanged)
        self.lePermissionsFilePath.textChanged.connect(self.loadPermissions)
        self.btnExecuteCommand.clicked.connect(self.executeCommand)

        self.loadPermissions()

        self.layoutMain = QGridLayout()
        self.layoutMain.addWidget(self.gbPaths, 0, 0)
        self.layoutMain.addWidget(self.gbPermissionsView, 1, 0)
        self.layoutMain.addWidget(self.gbUserSelection, 2, 0)
        self.layoutMain.addWidget(self.gbEditor, 3, 0)

        self.setLayout(self.layoutMain)

    def loadPermissions(self):
        self.twPermissions.clear()
        self.twPermissions.setRowCount(0)
        self.twPermissions.setColumnCount(0)

        self.cbUserSelect.clear()

        self.permissions = None

        self.currentUser = None
        self.currentObjects = None

        try:
            with open(self.lePermissionsFilePath.text(), "r") as fs:
                permissions = json.loads(fs.read())

                self.permissions = permissions
                objects = list(permissions['objects'])
                users = list(permissions['users'].keys())

                # Filling permissions table
                self.twPermissions.setColumnCount(len(objects))
                self.twPermissions.setHorizontalHeaderLabels(objects)
                self.twPermissions.setRowCount(len(users))
                self.twPermissions.setVerticalHeaderLabels(users)
                self.twPermissions.resizeColumnsToContents()

                for oid, obj in enumerate(objects):
                    for uid, user in enumerate(users):
                        if obj in self.permissions['users'][user]:
                            self.twPermissions.setItem(uid, oid, QTableWidgetItem("+"))

                # Adding users to selector
                self.cbUserSelect.clear()
                self.cbUserSelect.addItems(users)

                self.currentUser = self.cbUserSelect.currentText()
                self.currentObjects = self.permissions['users'][self.currentUser]

                self.cbUserSelectIndexChanged(self.currentUser)

        except:
            pass

    def savePermissions(self):
        with open(self.lePermissionsFilePath.text(), "w") as fs:
            json.dump(self.permissions, fs)

    def cbUserSelectIndexChanged(self, user):
        self.lblAvailable.setText("Доступно: ")

        if self.cbUserSelect.count() == 0:
            return

        self.currentUser = user
        self.currentObjects = self.permissions['users'][user]
        self.teTextChanged()
        self.lblAvailable.setText("Доступно: " + self.permissions['users'][user])

    def teTextChanged(self):
        if (self.currentUser is None) or (self.currentObjects is None):
            return

        text = self.teEditor.toPlainText()

        if len(text) < self.teTextLen:
            self.teTextLen = len(text)
            return

        self.teEditor.textChanged.disconnect(self.teTextChanged)

        self.teEditor.clear()

        for letter in text:
            if letter not in self.currentObjects:
                self.teEditor.setTextColor(QColor('#FF0000'))
            else:
                self.teEditor.setTextColor(QColor('#000000'))

            self.teEditor.insertPlainText(letter)

        self.teTextLen = len(text)

        self.teEditor.textChanged.connect(self.teTextChanged)

    def btnSaveFileClicked(self):
        if (self.currentUser is None) or (self.currentObjects is None):
            return

        text = self.teEditor.toPlainText()
        fileName = self.leFileName.text()

        if len(fileName) <= 3:
            QMessageBox.warning(None, 'Некорректное название файла', 'Название файла должно содержать более 3 '
                                                                     'симоволов', QMessageBox.Ok)
            return

        if re.search(r'[^' + str(self.currentObjects) + r']', text):
            QMessageBox.warning(None, 'Некорректное содержимое файла', 'Текст содержит недоступные объекты',
                                QMessageBox.Ok)
            return

        try:
            with open(os.path.join(self.leSharedFolderPath.text(), fileName), 'w') as fs:
                fs.write(text)
        except:
            QMessageBox.warning(None, 'Ошибка записи', 'Ошибка записи', QMessageBox.Ok)
            return

        QMessageBox.information(None, 'Сохранено', 'Сохранение выполнено успешно', QMessageBox.Ok)

    def btnOpenFileClicked(self):
        fileName = self.leFileName.text()

        try:
            with open(os.path.join(self.leSharedFolderPath.text(), fileName), 'r') as fs:
                text = fs.read()
        except:
            QMessageBox.warning(None, 'Ошибка чтения', 'Ошибка чтения', QMessageBox.Ok)
            return

        self.teEditor.setText(text)
        self.teTextChanged()

    def executeCommand(self):
        if self.permissions is None:
            return

        command = self.leCommands.text()
        command = command.replace(' ', '')

        # Really bad regexps, but its only 2 hours to sleep left

        if not re.match('^Grant\(.+,.+\)$', command) is None:
            user = command[command.rindex('(')+1:command.rindex(',')]
            prev = list(command[command.rindex(',') + 1:command.rindex(')')])

            if user not in self.permissions['users']:
                QMessageBox.warning(None, 'Ошибка исполнения', 'Пользователь не найден', QMessageBox.Ok)
                return

            for letter in prev:
                if letter not in self.permissions['objects']:
                    self.permissions['objects'] = self.permissions['objects'] + letter

                if letter not in self.permissions['users'][user]:
                    self.permissions['users'][user] = self.permissions['users'][user] + letter

            self.savePermissions()
            self.loadPermissions()

        elif not re.match('^Revoke\(.+,.+\)$', command) is None:
            user = command[command.rindex('(') + 1:command.rindex(',')]
            prev = list(command[command.rindex(',') + 1:command.rindex(')')])

            if user not in self.permissions['users']:
                QMessageBox.warning(None, 'Ошибка исполнения', 'Пользователь не найден', QMessageBox.Ok)
                return

            for letter in prev:
                self.permissions['users'][user] = self.permissions['users'][user].replace(letter, '')

            for letter in prev:
                contains = False

                for ur, pm in self.permissions['users'].items():
                    if letter in pm:
                        contains = True
                        break

                if not contains:
                    self.permissions['objects'] = self.permissions['objects'].replace(letter, '')

        elif not re.match('^Create\(.+\)$', command) is None:
            user = command[command.rindex('(') + 1:command.rindex(')')]

            if user not in self.permissions['users']:
                self.permissions['users'][user] = ''
            else:
                QMessageBox.warning(None, 'Ошибка исполнения', 'Пользователь уже существует', QMessageBox.Ok)
                return

        elif not re.match('^Remove\(.+\)$', command) is None:
            user = command[command.rindex('(') + 1:command.rindex(')')]

            if user not in self.permissions['users']:
                QMessageBox.warning(None, 'Ошибка исполнения', 'Пользователь не существует', QMessageBox.Ok)
            else:
                self.permissions['users'].pop(user)

            for letter in self.permissions['objects']:
                contains = False

                for ur, pm in self.permissions['users'].items():
                    if letter in pm:
                        contains = True
                        break

                if not contains:
                    self.permissions['objects'] = self.permissions['objects'].replace(letter, '')

        else:
            QMessageBox.warning(None, 'Неверный формат команды', 'Неверный формат команды', QMessageBox.Ok)
            return

        self.savePermissions()
        self.loadPermissions()

        QMessageBox.information(None, 'Успех', 'Команда успешно выполнена', QMessageBox.Ok)

        self.loadPermissions()
