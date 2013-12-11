#! /usr/bin/env python
import pygame
import os, sys
import subprocess
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
    self.rightLayout = QtGui.QVBoxLayout()
    self.addSongButton = QtGui.QPushButton("Add song")
    self.addSongButton.clicked.connect(self.addSong)
    self.findSongButton = QtGui.QPushButton("Find song")
    self.findSongButton.clicked.connect(self.findSong)
    self.findSongGroup = QtGui.QGroupBox("Find song:")
    self.songButtonLayout = QtGui.QHBoxLayout()
    self.songButtonLayout.addWidget(self.addSongButton)
    self.songButtonLayout.addWidget(self.findSongButton)
    self.rightLayout.addLayout(self.songButtonLayout)
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
    mainLayout.addLayout(self.rightLayout)
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
  #  This will act as a slot for the 'find song' button being clicked.
  def findSong(self):
    groupLayout = QtGui.QVBoxLayout(self.findSongGroup)
    urlLayout = QtGui.QHBoxLayout()
    urlLabel = QtGui.QLabel("URL:")
    self.urlLine = QtGui.QLineEdit()
    urlLayout.addWidget(urlLabel)
    urlLayout.addWidget(self.urlLine)
    nameLayout = QtGui.QHBoxLayout()
    nameLabel = QtGui.QLabel("Name of song:")
    self.nameLine = QtGui.QLineEdit()
    nameEnd = QtGui.QLabel(".wav")
    nameLayout.addWidget(nameLabel)
    nameLayout.addWidget(self.nameLine)
    nameLayout.addWidget(nameEnd)
    self.addButton = QtGui.QPushButton("Add")
    self.addButton.clicked.connect(self.onAddClicked)
    groupLayout.addLayout(urlLayout)
    groupLayout.addLayout(nameLayout)
    groupLayout.addWidget(self.addButton)
    self.rightLayout.addWidget(self.findSongGroup)
    
  ##
  #  This will be triggered when the addButton is clicked.
  def onAddClicked(self):
    subprocess.call(['youtube-dl', '-o', "{}.mp4".format(self.nameLine.text()), self.urlLine.text()])
    subprocess.call(['ffmpeg', '-i', "{}.mp4".format(self.nameLine.text()), "{}.wav".format(self.nameLine.text())])
    with open("songlist.txt", 'a') as f:
      f.write(os.getcwd()+ "/" + "{}.wav".format(self.nameLine.text()) + "\n")
    self.names["{}.wav".format(self.nameLine.text())] = os.getcwd() + "/{}.wav".format(self.nameLine.text())
    self.songList.addItem("{}.wav".format(self.nameLine.text()))

  ##
  #  This is triggered when an item in the list is double clicked. A song will play.
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
