#!/usr/bin/env python

from logging import basicConfig, getLogger, DEBUG, INFO, CRITICAL
from pickle import dump, load
from die import *
from os import path
import sys
from sys import path, argv, exit
import crapsResources_rc
import PyQtStarterResources_rc
from PyQt5 import QtGui, uic
from PyQt5.QtCore import pyqtSlot, QSettings, Qt, QTimer, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog

logFileNameDefault = 'pyQtStarter.log'
createLogFileDefault = False
pickleFilenameDefault = ".PyQtStarterSavedObjects.pl"


class Craps(QMainWindow):
    """A game of Craps."""
    die1 = die2 = None

    def __init__(self, parent=None):
        """Build a game with two dice."""

        super().__init__(parent)
        uic.loadUi("Craps.ui", self)

        self.die1 = Die()
        self.die2 = Die()
        self.numberOfWins = 0
        self.currentBet = 0
        self.rollValue = 0
        self.rollButton.clicked.connect(self.rollButtonClickedHandler)
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

    def saveGame(self):
        if self.createLogFile:
            self.logger.debug("Saving program state")
            saveItems = (self.die1,
                         self.die2,
                         self.numberOfWins,
                         self.currentBet,
                         self.rollValue,
                         self.rollButtonClickedHandler,
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
            logFilename = logFileNameDefault
            appSettings.setValue('logFile', logFilename)
        basicConfig(filename=path.join(startingFolderName, logFilename), level=INFO,
                    format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
    app = QApplication(argv)
    PyQtStarterApp = Craps()
    PyQtStarterApp.updateUI()
    PyQtStarterApp.show()
    exit(app.exec_())


