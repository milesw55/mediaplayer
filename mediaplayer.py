#! /usr/bin/env python
#  This is a unique media player that allows the user to
#  download youtube videos on the fly.
#
#  Requirements:
#    Python 2.7
#    PySide
#    pygame
#    youtube-dl (unix package)
#    ffmpeg (unix package)
#
#  @authors milesw55, ntreado
import pygame
import os, sys
import subprocess
from src.gui.style import style
from PySide import QtGui, QtCore

##
#  This is the main widget that will parent
#  most of the GUI's features. 
class MusicWidget(QtGui.QWidget):
  ##
  #  Main initializer function.
  def __init__(self):
    super(MusicWidget, self).__init__()
    self.addLayoutInitialized = False
    self.setWindowTitle("Media Player")
    self.setObjectName("musicWidget")
    self.setStyleSheet("#musicWidget { background-color: white; }")
    mainLayout = QtGui.QHBoxLayout(self)
    self.splitter = QtGui.QSplitter()
    self.splitter.setObjectName("splitter")
    self.splitter.setStyleSheet(style.SPLITTER)
    self.rightWidget = QtGui.QWidget()
    self.rightLayout = QtGui.QVBoxLayout(self.rightWidget)
    leftWidget = QtGui.QWidget()
    leftLayout = QtGui.QVBoxLayout(leftWidget)
    self.splitter.addWidget(leftWidget)
    self.splitter.addWidget(self.rightWidget)
    self.addSongButton = QtGui.QPushButton("Add song")
    self.addSongButton.setObjectName("addSong")
    self.addSongButton.setStyleSheet(style.button("addSong"))
    self.addSongButton.clicked.connect(self.addSong)
    self.findSongButton = QtGui.QPushButton("Get song")
    self.findSongButton.setObjectName("getSong")
    self.findSongButton.setStyleSheet(style.button("getSong"))
    self.findSongButton.clicked.connect(self.findSong)
    self.findSongGroup = QtGui.QGroupBox()
    self.findSongGroup.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
    self.findSongGroup.setObjectName("urlGroup")
    self.findSongGroup.setStyleSheet(style.GROUP_BOX)
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
    with open("songlist.txt", 'a') as f:
      print("songlist.txt does exist\ncontinuing with initialization")
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
    self.playButton.setObjectName("playButton")
    self.playButton.setStyleSheet(style.button("playButton"))
    self.playButton.clicked.connect(self.playTriggered)
    buttonLayout.addWidget(self.playButton)
    pauseButton = QtGui.QPushButton("Pause")
    pauseButton.setObjectName("pauseButton")
    pauseButton.setStyleSheet(style.button("pauseButton"))
    pauseButton.clicked.connect(self.pauseTriggered)
    buttonLayout.addWidget(pauseButton)
    leftLayout.addLayout(buttonLayout)
    mainLayout.addWidget(self.splitter)
    self.started = False
    pygame.mixer.init()
    self.prevSong = None

  ##
  #  This function will act as a slot to the 'add song'
  #  button being triggered.
  def addSong(self):
    fileName, fileType = QtGui.QFileDialog.getOpenFileName(self, "Add song", os.getcwd(), "Audio Files (*.mp3 *.wav)")
    with open("songlist.txt", 'a') as f:
      f.write(fileName + '\n')
    self.names[os.path.basename(fileName)] = fileName
    self.songList.addItem(os.path.basename(fileName))
  
  ##
  #  This will act as a slot for the 'find song' button being clicked.
  def findSong(self):
    if not self.addLayoutInitialized:
      groupLayout = QtGui.QVBoxLayout(self.findSongGroup)
      urlLayout = QtGui.QHBoxLayout()
      urlLabel = QtGui.QLabel("URL:")
      self.urlLine = QtGui.QLineEdit()
      self.urlLine.setStyleSheet("QLineEdit { background-color: #FFF; }")
      urlLayout.addSpacing(24)
      urlLayout.addWidget(urlLabel)
      urlLayout.addWidget(self.urlLine)
      urlLayout.addSpacing(63)
      nameLayout = QtGui.QHBoxLayout()
      nameLabel = QtGui.QLabel("Save As:")
      self.nameLine = QtGui.QLineEdit()
      self.nameLine.setStyleSheet("QLineEdit { background-color: #FFF; }")
      self.nameEnd = QtGui.QComboBox()
      self.nameEnd.addItem(".mp3")
      self.nameEnd.addItem(".wav")
      nameLayout.addWidget(nameLabel)
      nameLayout.addWidget(self.nameLine)
      nameLayout.addWidget(self.nameEnd)
      self.addButton = QtGui.QPushButton("Add")
      self.addButton.setObjectName("addButton")
      self.addButton.setStyleSheet(style.button("addButton"))
      self.addButton.clicked.connect(self.onAddClicked)
      groupLayout.addLayout(urlLayout)
      groupLayout.addLayout(nameLayout)
      groupLayout.addWidget(self.addButton)
      self.rightLayout.addWidget(self.findSongGroup)
      self.addLayoutInitialized = True
    else:
      if self.findSongGroup.isVisible():
        self.findSongGroup.hide()
      else:
        self.findSongGroup.show()
    
  ##
  #  This will be triggered when the addButton is clicked.
  def onAddClicked(self):
    mp4 = "{}.mp4".format(self.nameLine.text())
    if not os.path.isdir(os.path.join(os.getcwd(), "downloads")):
      os.makedirs(os.path.join(os.getcwd(), "downloads"))
    audioFile = "/downloads/{}{}".format(self.nameLine.text(), self.nameEnd.currentText())
    audioName = "{}{}".format(self.nameLine.text(), self.nameEnd.currentText())
    subprocess.call(['youtube-dl', '-o', mp4, self.urlLine.text()])
    subprocess.call(['ffmpeg', '-i', mp4, ".{}".format(audioFile)])
    subprocess.call(['rm', mp4])
    with open("songlist.txt", 'a') as f:
      f.write(os.getcwd()+ audioFile + "\n")
    self.names[audioName] = os.getcwd() + "{}".format(audioFile)
    self.songList.addItem(audioName)
    self.findSongGroup.hide()

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
