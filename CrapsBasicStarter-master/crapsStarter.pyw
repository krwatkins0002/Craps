#!/usr/bin/env python

from logging import basicConfig, getLogger, DEBUG, INFO, CRITICAL
from pickle import dump, load
from die import *
from os import path
import sys
from sys import argv, exit
import crapsResources_rc
import PyQtStarterResources_rc
from PyQt5 import QtGui, uic
from PyQt5.QtCore import pyqtSlot, QSettings, Qt, QTimer, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog

startingDummyVariableDefault = 100
textOutputDefault = " ---- "
logFilenameDefault = 'CrapsGame.log'
createLogFileDefault = False
pickleFilenameDefault = ".PyQtStarterSavedObjects.pl"
numberOfWinsDefault = 0
currentBetDefault = 1
currentBankDefault = 999


class Craps(QMainWindow):
    """A game of Craps."""
    die1 = die2 = None

    def __init__(self, parent=None):
        """Build a game with two dice."""

        super().__init__(parent)

        super().__init__(parent)
        self.logger = getLogger("Watkins.Craps")
        self.appSettings = QSettings()
        self.quitCounter = 0;       # used in a workaround for a QT5 bug.

        self.pickleFilename = pickleFilenameDefault

        self.restoreSettings()

        try:
            self.pickleFilename = self.restoreGame()
        except FileNotFoundError:
            self.restartGame()

        uic.loadUi("Craps.ui", self)

        self.die1 = Die()
        self.die2 = Die()
        self.numberOfWins = 0
        self.currentBet = 0
        self.rollValue = 0
        self.rollButton.clicked.connect(self.rollButtonClickedHandler)
        self.preferencesSelectButton.clicked.connect(self.preferencesSelectButtonClickedHandler)
        self.currentBank = 999

    def __str__(self):
        """String representation for Craps.
        """

        return "Die1: %s\nDie2: %s" % (self.die1, self.die2)



    def updateUI(self):
        self.die1View.setPixmap(QtGui.QPixmap(":/" + str(self.die1.getValue())))
        self.die2View.setPixmap(QtGui.QPixmap(":/" + str(self.die2.getValue())))
        self.winsCountValueUI.setText(str(self.numberOfWins))
        self.currentBankValueUI.setText(str(self.currentBank))

    def restoreGame(self):
        if self.appSettings.contains('pickleFilename'):
            self.appSettings.value('pickleFilename', type=str)
            with open(path.join(path.dirname(path.realpath(__file__)),
                                self.appSettings.value('pickleFilename', type=str)), 'rb') as pickleFile:
                return load(pickleFile)
        else:
            self.logger.critical("No pickle Filename")

    def restoreSettings(self):
        if appSettings.contains('createLogFile'):
            self.createLogFile = appSettings.value('createLogFile')
        else:
            self.createLogFile = createLogFileDefault
            appSettings.setValue('createLogFile', self.createLogFile)

        if self.createLogFile:
            self.logger.debug("Starting restoreSettings")
        # Restore settings values, write defaults to any that don't already exist.
        self.dummyVariable = True
        self.textOutput = ""
        if self.appSettings.contains('dummyVariable'):
            self.dummyVariable = self.appSettings.value('dummyVariable', type=int)
        else:
            self.dummyVariable = startingDummyVariableDefault
            self.appSettings.setValue('dummyVariable', self.dummyVariable)

        if self.appSettings.contains('textOutput'):
            self.textOutput = self.appSettings.value('textOutput', type=str)
        else:
            self.textOutput = textOutputDefault
            self.appSettings.setValue('textOutput', self.textOutput)

        if self.appSettings.contains('createLogFile'):
            self.createLogFile = self.appSettings.value('createLogFile')
        else:
            self.createLogFile = logFilenameDefault
            self.appSettings.setValue('createLogFile', self.createLogFile)

        if self.appSettings.contains('logFile'):
            self.logFilename = self.appSettings.value('logFile', type=str)
        else:
            self.logFilename = logFilenameDefault
            self.appSettings.setValue('logFile', self.logFilename)

        if self.appSettings.contains('pickleFilename'):
            self.pickleFilename = self.appSettings.value('pickleFilename', type=str)
        else:
            self.pickleFilename = pickleFilenameDefault
            self.appSettings.setValue('pickleFilename', self.pickleFilename)

    def closeEvent(self, event):
        if self.createLogFile:
            self.logger.debug("Closing app event")
            if self.quitCounter == 0:
                self.quitCounter += 1
                quitMessage = "Are you sure you want to quit?"
                reply = QMessageBox.question(self, 'message', quitMessage, QMessageBox.Yes,
                                             QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.saveGame()
                    event.accept()
                else:
                    self.quitCounter = 0
                    event.ignore()

    def restartGame(self):
        if self.createLogFile:
            self.logger.debug("Restarting program")

    def saveGame(self):
        if self.createLogFile:
            self.logger.debug("Saving program state")
            saveItems = (
                         self.numberOfWins,
                         self.currentBet,
                         self.currentBank)
            if self.appSettings.contains('pickleFilename'):
                with open(path.join(path.dirname(path.realpath(__file__)),
                                    self.appSettings.value('pickleFilename', type=str)), 'wb') as pickleFile:
                    dump(saveItems, pickleFile)
            elif self.createLogFile:
                self.logger.critical("No pickle Filename")

    # Player asked for another roll of the dice.
    def rollButtonClickedHandler(self):
        print("Roll button clicked")
        self.currentBet = self.spinBox.value()
        self.rollValue = self.die1.roll() + self.die2.roll()
        if self.rollValue in (2, 3, 12):
            print("You lost.")
            self.currentBank -= self.currentBet
        if self.rollValue in (7, 11):
            print("You won!")
            self.numberOfWins += 1
            self.currentBank += self.currentBet
        if self.rollValue in (4, 5, 6, 8, 9, 10):
            print("Re-roll")
        self.updateUI()

    @pyqtSlot()  # User is requesting preferences editing dialog box.
    def preferencesSelectButtonClickedHandler(self):
        if self.createLogFile:
            self.logger.info("Setting preferences")
        preferencesDialog = PreferencesDialog()
        preferencesDialog.show()
        preferencesDialog.exec_()
        self.restoreSettings()              # 'Restore' settings that were changed in the dialog window.
        self.updateUI()

    @pyqtSlot()  # Player asked to quit the game.
    def closeEvent(self, event):
        if self.createLogFile:
            self.logger.debug("Closing app event")
        if self.quitCounter == 0:
            self.quitCounter += 1
            quitMessage = "Are you sure you want to quit?"
            reply = QMessageBox.question(self, 'Message', quitMessage, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.saveGame()
                event.accept()
            else:
                self.quitCounter = 0
                event.ignore()

class PreferencesDialog(QDialog):
    def __init__(self, parent = Craps):
        super(PreferencesDialog, self).__init__()

        uic.loadUi('preferencesDialog.ui', self)
        self.logger = getLogger("Watkins.Craps")

        self.appSettings = QSettings()
        if self.appSettings.contains('firstVariable'):
            self.firstVariable = self.appSettings.value('firstVariable', type=int)
        else:
            self.firstVariable = numberOfWinsDefault
            self.appSettings.setValue('firstVariable', self.firstVariable)

        if self.appSettings.contains('secondVariable'):
            self.secondVariable = self.appSettings.value('secondVariable', type=int)
        else:
            self.secondVariable = currentBetDefault
            self.appSettings.setValue('secondVariable', self.secondVariable)

        if self.appSettings.contains('thirdVariable'):
            self.thirdVariable = self.appSettings.value('thirdVariable', type=int)
        else:
            self.thirdVariable = currentBankDefault
            self.appSettings.setValue('thirdVariable', self.thirdVariable)

        if self.appSettings.contains('logFile'):
            self.logFilename = self.appSettings.value('logFile', type=str)
        else:
            self.logFilename = logFilenameDefault
            self.appSettings.setValue('logFile', self.logFilename)

        if self.appSettings.contains('createLogFile'):
            self.createLogFile = self.appSettings.value('createLogFile')
        else:
            self.createLogFile = logFilenameDefault
            self.appSettings.setValue('createLogFile', self.createLogFile )

        self.buttonBox.rejected.connect(self.cancelClickedHandler)
        self.buttonBox.accepted.connect(self.okayClickedHandler)
        self.firstVariableValue.editingFinished.connect(self.firstVariableValueChanged)
        self.secondVariableValue.editingFinished.connect(self.secondVariableValueChanged)
        self.thirdVariableValue.editingFinished.connect(self.thirdVariableValueChanged)
        self.createLogfileCheckBox.stateChanged.connect(self.createLogFileChanged)

        self.updateUI()

    # @pyqtSlot()
    def firstVariableValueChanged(self):
        self.firstVariable = int(self.firstVariableValue.text())

    # @pyqtSlot()
    def secondVariableValueChanged(self):
        self.secondVariable = int(self.secondVariableValue.text())

    # @pyqtSlot()
    def thirdVariableValueChanged(self):
        self.thirdVariable = int(self.thirdVariableValue.text())

    # @pyqtSlot()
    def createLogFileChanged(self):
        self.createLogFile = self.createLogfileCheckBox.isChecked()

    def updateUI(self):
        self.firstVariableValue.setText(str(self.firstVariable))
        self.secondVariableValue.setText(str(self.secondVariable))
        self.thirdVariableValue.setText(str(self.thirdVariable))
        if self.createLogFile:
            self.createLogfileCheckBox.setCheckState(Qt.Checked)
        else:
            self.createLogfileCheckBox.setCheckState(Qt.Unchecked)

    # @pyqtSlot()
    def okayClickedHandler(self):
        # write out all settings
        preferencesGroup = (('firstVariable', self.firstVariable),
                            ('secondVariable', self.secondVariable),
                            ('thirdVariable', self.thirdVariable),
                            ('logFile', self.logFilename),
                            ('createLogFile', self.createLogFile),
                            )
        # Write settings values.
        for setting, variableName in preferencesGroup:
            # if self.appSettings.contains(setting):
            self.appSettings.setValue(setting, variableName)

        self.close()

    # @pyqtSlot()
    def cancelClickedHandler(self):
        self.close()

if __name__ == "__main__":
    QCoreApplication.setOrganizationName("Watkins Software");
    QCoreApplication.setOrganizationDomain("kylerobertwatkins.com");
    QCoreApplication.setApplicationName("Craps");
    appSettings = QSettings()
    if appSettings.contains('createLogFile'):
        createLogFile = appSettings.value('createLogFile')
    else:
        createLogFile = createLogFileDefault
        appSettings.setValue('createLogFile', createLogFile)

    if createLogFile:
        startingFolderName = path.dirname(path.realpath(__file__))
        if appSettings.contains('logFile'):
            logFilename = appSettings.value('logFile', type=str)
        else:
            logFilename = logFilenameDefault
            appSettings.setValue('logFile', logFilename)
        basicConfig(filename=path.join(startingFolderName, logFilename), level=INFO,
                    format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
    app = QApplication(argv)
    PyQtStarterApp = Craps()
    PyQtStarterApp.updateUI()
    PyQtStarterApp.show()
    exit(app.exec_())


