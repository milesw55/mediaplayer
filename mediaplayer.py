#! /usr/bin/env python
import pygame
import os, sys
from PySide import QtGui, QtCore

##
#  This is the main widget that will parent
#  most of the GUI's features. 
class MusicWidget(QtGui.QWidget):
  ##
  #  Main initializer function.
  def __init__(self):
    super(MusicWidget, self).__init__()
    self.setWindowTitle("WAV Player")
    mainLayout = QtGui.QHBoxLayout(self)
    leftLayout = QtGui.QVBoxLayout()
    rightLayout = QtGui.QVBoxLayout()
    addSongButton = QtGui.QPushButton("Add song")
    addSongButton.clicked.connect(self.addSong)
    rightLayout.addWidget(addSongButton)
    groupbox = QtGui.QGroupBox("Your songs:")
    gboxLayout = QtGui.QVBoxLayout()
    self.songList = QtGui.QListWidget()
    self.songList.itemDoubleClicked.connect(self.onItemDoubleClicked)
    content = ""
    self.names = {}
    with open("songlist.txt", 'r') as f:
      content = f.read()
    for song in content.split('\n'):
      if song != "":
        self.names[os.path.basename(song)] = song
        self.songList.addItem(os.path.basename(song))
    gboxLayout.addWidget(self.songList)
    groupbox.setLayout(gboxLayout)
    leftLayout.addWidget(groupbox)
    buttonLayout = QtGui.QHBoxLayout()
    self.playButton = QtGui.QPushButton("Play")
    self.playButton.clicked.connect(self.playTriggered)
    buttonLayout.addWidget(self.playButton)
    pauseButton = QtGui.QPushButton("Pause")
    pauseButton.clicked.connect(self.pauseTriggered)
    buttonLayout.addWidget(pauseButton)
    leftLayout.addLayout(buttonLayout)
    mainLayout.addLayout(leftLayout)
    mainLayout.addLayout(rightLayout)
    self.started = False
    pygame.mixer.init()
    self.prevSong = None

  ##
  #  This function will act as a slot to the 'add song'
  #  button being triggered.
  def addSong(self):
    fileName, fileType = QtGui.QFileDialog.getOpenFileName(self, "Add song", os.getcwd(), "WAV Files (*.wav)")
    with open("songlist.txt", 'a') as f:
      f.write(fileName + '\n')
    self.names[os.path.basename(fileName)] = filename
    self.songList.addItem(os.path.basename(fileName))
  
  ##
  #
  def onItemDoubleClicked(self, item):
    song = self.names[item.text()]
    self.prevSong = song
    pygame.mixer.music.load(song)
    self.started = True
    pygame.mixer.music.play()

  ##
  #  This function will act as a slot to the 'play button'
  #  being triggered.
  def playTriggered(self):
    song = self.names[self.songList.currentItem().text()]
    if (self.prevSong is None) or (self.prevSong != song):
      self.prevSong = song
      pygame.mixer.music.load(song)
    if self.started == False:
      self.started = True
      pygame.mixer.music.play()
    elif pygame.mixer.music.get_busy():
      pygame.mixer.music.unpause()
    else:
      pygame.mixer.music.play()

  ##
  #  This function will act as a slot to the 'pause button'
  #  being triggered.
  def pauseTriggered(self):
    pygame.mixer.music.pause()


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  musicWidget = MusicWidget()
  musicWidget.show()
  app.exec_()
