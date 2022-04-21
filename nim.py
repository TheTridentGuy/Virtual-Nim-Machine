"""
Virtual Nim Machine:
A program that plays you in four different versions of
the math game nim.

Program does not import any other modules except for PyQt5
and some of python's built-in modules.

Copyright (c) 2022 Aiden Bohlander.

This file is part of the Virtual Nim Machine.

the Virtual Nim Machine is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

the Virtual Nim Machine is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with the Virtual Nim Machine. If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import os
import random
import time
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMessageBox


basedir = os.path.dirname(__file__)
form_class = uic.loadUiType(os.path.join(basedir, "start.ui"))[0]
game_form_class = uic.loadUiType(os.path.join(basedir, "game.ui"))[0]


class StartWindow(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.windows = []
        try:
            with open(os.path.join(basedir, "rules.txt")) as f:
                self.rules.setText(f.read())
        except FileNotFoundError:
            self.rules.setText("Unable To Find Rules.\n\nGoogle 'Nim Game' for more info.")
        self.options = ["1 Pile Last Gem Wins", "1 Pile Last Gem Loses", "2 Pile Last Gem Wins",
                        "2 Pile Last Gem Loses", "Nim Grand Master Style"]
        for opt in self.options:
            self.mode.addItem(opt)
        self.play.clicked.connect(self.startgame)

    def startgame(self):
        newgame = Game(self, self.mode.currentText())
        newgame.show()
        self.windows.append(newgame)


class Game(QtWidgets.QMainWindow, game_form_class):
    def __init__(self, parent=None, mode=""):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        modes = {"1 Pile Last Gem Wins": 0, "1 Pile Last Gem Loses": 1, "2 Pile Last Gem Wins": 2,
                 "2 Pile Last Gem Loses": 3, "Nim Grand Master Style": random.randint(0, 3)}
        modestrings = ["1 Pile Last Gem Wins", "1 Pile Last Gem Loses", "2 Pile Last Gem Wins",
                       "2 Pile Last Gem Loses", "Nim Grand Master Style"]
        self.mode = modes[mode]
        self.starttime = False
        self.go = False
        self.pileselect.currentIndexChanged.connect(self.updatemax)
        self.sendmove.clicked.connect(self.handlemove)
        self.gofirst.clicked.connect(self.makemove)
        if self.mode == 0 or self.mode == 1:
            self.pile = [random.randint(8, 40)]
            self.max = random.randint(3, (self.pile[0] // 4) + 2)
            maxstr = "Max You Can Take:\t" + str(self.max)
            self.pilea.setHidden(True)
            self.pileb.setHidden(True)
            self.pilec.setHidden(False)
            self.drawpile(self.pilec, self.pile[0], "Pile A")
            self.pileselect.addItem("Pile A:")
        else:
            maxstr = ""
            self.pile = [random.randint(6, 40), random.randint(6, 40)]
            self.pilea.setHidden(False)
            self.pileb.setHidden(False)
            self.pilec.setHidden(True)
            self.drawpile(self.pilea, self.pile[0], "Pile A")
            self.drawpile(self.pileb, self.pile[1], "Pile B")
            self.pileselect.addItem("Pile A:")
            self.pileselect.addItem("Pile B:")
        self.updatemax()
        self.type.setText(modestrings[self.mode] + ",  " + maxstr)
        self.timer = QtCore.QTimer(self)
        self.timer.start(2000)
        self.timer.timeout.connect(self.checkmove)

    def checkmove(self):
        if self.go:
            self.makemove()
        if self.starttime:
            self.go = True

    def handlemove(self):
        thoughts = ["Thinking...", "Let's see here...", "Hmmm...", " My turn here... Let's see..."]
        self.sendmove.setHidden(True)
        if not self.starttime or self.go:
            self.chat.setText(random.choice(thoughts))
            self.starttime = True
            if self.pileselect.currentText() == "Pile A:":
                self.pile[0] -= self.numgems.value()
                self.drawpile(self.pilea, self.pile[0], "Pile A")
                self.drawpile(self.pilec, self.pile[0], "Pile A")
            else:
                self.pile[1] -= self.numgems.value()
                self.drawpile(self.pileb, self.pile[1], "Pile B")

    def makemove(self):
        thoughts = ["Aha! Got it!", "Oh I see!", "Ooohhhhhh... I see now!", "Oh! Of course!"]
        self.chat.setText(random.choice(thoughts))
        won = False
        lost = False
        self.gofirst.setHidden(True)
        """
        modes : [0: "1 Pile Last Gem Wins", 1: "1 Pile Last Gem Loses", 2: "2 Pile Last Gem Wins",
                 3: "2 Pile Last Gem Loses"]
        """
        #  mode == 0 or mode == 1
        if self.mode == 0 or self.mode == 1:
            #  mode == 0
            if self.mode == 0:
                if self.pile[0] <= 0:
                    won = True
                    self.win()
                    self.close()
                elif self.pile[0] <= self.max:
                    self.pile[0] = 0
                elif self.pile[0] % (self.max + 1) != 0:
                    self.pile[0] -= self.pile[0] % (self.max + 1)
                else:
                    self.pile[0] -= random.randint(1, self.max)
                self.drawpile(self.pilec, self.pile[0], "Pile A")
                if self.pile[0] <= 0 and not won:
                    self.lose()
                    self.close()
            #  mode == 1
            else:
                if self.pile[0] <= 0:
                    self.lose()
                    self.close()
                    lost = True
                elif self.max + 1 >= self.pile[0] > 1:
                    self.pile[0] = 1
                elif self.pile[0] % (self.max + 1) == 0:
                    self.pile[0] -= self.max
                elif self.pile[0] % (self.max + 1) != 1:
                    self.pile[0] -= (self.pile[0] % (self.max + 1)) - 1
                else:
                    self.pile[0] -= random.randint(1, self.max)
                self.drawpile(self.pilec, self.pile[0], "Pile A")
                if self.pile[0] <= 0 and not lost:
                    self.win()
                    self.close()
        #  mode == 2 or mode == 3
        else:
            #  mode == 2
            if self.mode == 2:
                if self.pile[0] <= 0 and self.pile[1] <= 0:
                    won = True
                    self.win()
                    self.close()
                elif self.pile[0] > self.pile[1]:
                    self.pile[0] = self.pile[1]
                elif self.pile[1] > self.pile[0]:
                    self.pile[1] = self.pile[0]
                else:
                    self.pile[random.randint(0, 1)] -= random.randint(1, 8)
                self.drawpile(self.pilea, self.pile[0], "Pile A")
                self.drawpile(self.pileb, self.pile[1], "Pile B")
                if self.pile[0] <= 0 and self.pile[1] <= 0 and not won:
                    self.lose()
                    self.close()
            #  mode == 3
            else:
                if self.pile[0] <= 0 and self.pile[1] <= 0:
                    lost = True
                    self.lose()
                    self.close()
                if self.pile[0] == 0:
                    self.pile[1] = 1
                elif self.pile[1] == 0:
                    self.pile[0] = 1
                elif self.pile[0] == 1:
                    self.pile[1] = 0
                elif self.pile[0] == 1:
                    self.pile[0] = 0
                elif self.pile[0] > self.pile[1]:
                    self.pile[0] = self.pile[1]
                elif self.pile[1] > self.pile[0]:
                    self.pile[1] = self.pile[0]
                else:
                    self.pile[random.randint(0, 1)] -= random.randint(1, 8)
                self.drawpile(self.pilea, self.pile[0], "Pile A")
                self.drawpile(self.pileb, self.pile[1], "Pile B")
                if self.pile[0] <= 0 and self.pile[1] <= 0 and not lost:
                    self.win()
                    self.close()
        self.updatemax()
        self.sendmove.setHidden(False)
        self.starttime = False
        self.go = False

    def lose(self):
        self.chat.setText("Yay! I won!")
        msgbox = QMessageBox()
        msgbox.setText("You Lost!\nComputers still rule the world.")
        msgbox.setWindowTitle("You Win")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.buttonClicked.connect(msgbox.close)
        msgbox.exec()

    def win(self):
        self.chat.setText("Darn! I lost!")
        msgbox = QMessageBox()
        msgbox.setText("You Won!\nComputers don't rule the world.\nYet!")
        msgbox.setWindowTitle("You Win")
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.buttonClicked.connect(msgbox.close)
        msgbox.exec()

    def updatemax(self):
        self.numgems.setMinimum(1)
        if self.mode == 0 or self.mode == 1:
            self.numgems.setMaximum(self.max)
        else:
            if self.pileselect.currentText() == "Pile A:":
                self.numgems.setMaximum(self.pile[0])
            else:
                self.numgems.setMaximum(self.pile[1])

    def drawpile(self, pile, num=0, text=""):
        if num < 0:
            num = 0
        counter = 1
        newtext = [f"{text} ({num}):\n"]
        for i in range(10):
            for j in range(10):
                if counter <= num:
                    newtext.append("O")
                    counter += 1
            newtext.append("\n")
        pile.setText("".join(newtext))


app = QtWidgets.QApplication(sys.argv)
start = StartWindow()
start.show()
app.exec_()
