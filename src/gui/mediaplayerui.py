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
import re
from style import style
from PySide import QtGui, QtCore
from PySide.phonon import Phonon



##
#  Download widget to be put in seperate thread.
class DownloadWidget(QtCore.QObject):

  ##
  #  Signal of added song.
  songAdded = QtCore.Signal(str)

  ##
  #  Error occurred.
  error = QtCore.Signal(str)

  ##
  #  Main initializer funciton.
  def __init__(self):
    super(DownloadWidget, self).__init__()

  def download(self, url, mp4, name):
    if not re.match("\w+", name):
      self.error.emit("Invalid name for saving song.")
      return
    audioFile = "/downloads/{}".format(name)
    ret = subprocess.call(['youtube-dl', '-o', mp4, url])
    if (ret != 0):
      self.error.emit("Error downloading. URL may be invalid or copyrighted.")
      return
    command = ['ffmpeg', '-i', mp4]
    if audioFile.endswith("ogg"):
      command.append('-acodec')
      command.append('vorbis')
      command.append('-aq')
      command.append('60')
      command.append('-vn')
      command.append('-ac')
      command.append('2')
      command.append('-strict')
      command.append('-2')
    command.append(".{}".format(audioFile))
    ret = subprocess.call(command)
    if (ret != 0):
      self.error.emit("Error ripping audio.")
      subprocess.call(['rm', mp4])
      return
    subprocess.call(['rm', mp4])
    self.songAdded.emit(audioFile)


##
#  Standard Font.
class StandardFont(QtGui.QFont):
  ##
  #  Main initializer function.
  def __init__(self):
    super(StandardFont, self).__init__()
    self.setFamily("SansSerif")
    self.setPointSize(10)

##
#  This class will hold the essential UI elements of the
#  song adding features. This includes adding local songs
#  and getting songs from URLs.
class URLDownloadingGroup(QtGui.QGroupBox):

  ##
  #  Signal of added song.
  songAdded = QtCore.Signal(str)

  ##
  #  Signal for download request.
  downloadRequest = QtCore.Signal(str, str, str)

  ##
  #  Main initializer function.
  def __init__(self):
    super(URLDownloadingGroup, self).__init__()
    self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)

    rightGroupLayout = QtGui.QVBoxLayout(self)

    directionLabel = QtGui.QLabel("You can add songs locally by clicking 'Add Local'." +
" Alternatively, you can enter a video URL such as one from YouTube and click 'Add URL' to save the audio from that video to your library." +
" Please note that copyrighted videos will not work. Enjoy.")
    directionLabel.setFont(StandardFont())
    directionLabel.setWordWrap(True)
    rightGroupLayout.addWidget(directionLabel)

    self.findSongGroup = QtGui.QGroupBox()
    self.findSongGroup.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
    self.findSongGroup.setObjectName("urlGroup")
    self.findSongGroup.setStyleSheet(style.GROUP_BOX)
    rightGroupLayout.addWidget(self.findSongGroup)

    groupLayout = QtGui.QVBoxLayout(self.findSongGroup)

    urlLayout = QtGui.QHBoxLayout()
    urlLabel = QtGui.QLabel("URL:")
    urlLabel.setFont(StandardFont())
    self.urlLine = QtGui.QLineEdit()
    self.urlLine.setStyleSheet("QLineEdit { background-color: #FFF; }")
    self.urlLine.setFont(StandardFont())
    urlLayout.addSpacing(27)
    urlLayout.addWidget(urlLabel)
    urlLayout.addWidget(self.urlLine)
    urlLayout.addSpacing(65)

    nameLayout = QtGui.QHBoxLayout()
    nameLabel = QtGui.QLabel("Save As:")
    nameLabel.setFont(StandardFont())
    self.nameLine = QtGui.QLineEdit()
    self.nameLine.setStyleSheet("QLineEdit { background-color: #FFF; }")
    self.nameLine.setFont(StandardFont())
    self.nameEnd = QtGui.QComboBox()
    self.nameEnd.setFont(StandardFont())
    self.nameEnd.setObjectName("fileType")
    self.nameEnd.setStyleSheet(style.COMBO_BOX)
    self.nameEnd.addItem(".ogg")
    self.nameEnd.addItem(".mp3")
    self.nameEnd.addItem(".wav")
    nameLayout.addWidget(nameLabel)
    nameLayout.addWidget(self.nameLine)
    nameLayout.addWidget(self.nameEnd)

    groupLayout.addLayout(urlLayout)
    groupLayout.addLayout(nameLayout)

    self.songButtonLayout = QtGui.QHBoxLayout()
    
    self.statusLabel = QtGui.QLabel()
    self.statusLabel.setObjectName("status")
    self.statusLabel.setFont(StandardFont())
    self.songButtonLayout.addWidget(self.statusLabel)

    self.addSongButton = QtGui.QPushButton("Add Local")
    self.addSongButton.setObjectName("addSong")
    self.addSongButton.setStyleSheet(style.button("addSong"))
    self.addSongButton.setFont(StandardFont())
    self.addSongButton.clicked.connect(self.addSong)
    self.songButtonLayout.addStretch(0)
    self.songButtonLayout.addWidget(self.addSongButton)

    self.addButton = QtGui.QPushButton("Add URL")
    self.addButton.setObjectName("addButton")
    self.addButton.setStyleSheet(style.button("addButton"))
    self.addButton.setFont(StandardFont())
    self.addButton.clicked.connect(self.onAddClicked)
    self.songButtonLayout.addWidget(self.addButton)
    self.thread = None

    rightGroupLayout.addLayout(self.songButtonLayout)

  ##
  #  This function will act as a slot to the 'add song'
  #  button being triggered.
  def addSong(self):
    fileName, fileType = QtGui.QFileDialog.getOpenFileName(self, "Add song", os.getcwd(), "Audio Files (*.ogg *.mp3 *.wav)")
    with open("songlist.txt", 'a') as f:
      f.write(fileName + '\n')
    self.songAdded.emit(fileName)

  ##
  #  Handles the close aciton.
  def close(self):
    self.thread.quit()
    
  ##
  #  This will be triggered when the addButton is clicked.
  def onAddClicked(self):
    mp4 = "{}.mp4".format(self.nameLine.text())
    if not os.path.isdir(os.path.join(os.getcwd(), "downloads")):
      os.makedirs(os.path.join(os.getcwd(), "downloads"))
    audioName = "{}{}".format(self.nameLine.text(), self.nameEnd.currentText())
    url = self.urlLine.text()
    if self.thread is not None:
      self.thread.quit()
    self.worker = DownloadWidget()
    self.worker.songAdded.connect(self.onAudioFileAdded)
    self.worker.error.connect(self.onError)
    self.thread = QtCore.QThread()
    self.worker.moveToThread(self.thread)
    self.downloadRequest.connect(self.worker.download)
    self.thread.start()
    self.addButton.setEnabled(False)
    self.statusLabel.setStyleSheet("#status { color: black; }")
    self.statusLabel.setText("Downloading...")
    self.downloadRequest.emit(url, mp4, audioName)

  ##
  #  Updates.
  def onAudioFileAdded(self, audioFile):
    fileName = os.getcwd()+ audioFile
    with open("songlist.txt", 'a') as f:
      f.write(fileName + "\n")
    self.addButton.setEnabled(True)
    self.statusLabel.setText("Download complete.")
    self.songAdded.emit(fileName)

  ##
  #  Display error.
  def onError(self, error):
    self.statusLabel.setStyleSheet("#status { color: red; }")
    self.statusLabel.setText(error)
    self.addButton.setEnabled(True)

##
#  The song playing group.
class SongPlayingGroup(QtGui.QGroupBox):

  ##
  #  Signal from saying a song started.
  playing = QtCore.Signal(str)
  
  ##
  #  Main initializer function.
  def __init__(self, name):
    super(SongPlayingGroup, self).__init__(name)
    self.setFont(StandardFont())
    gboxLayout = QtGui.QVBoxLayout(self)

    self.songList = QtGui.QListWidget()
    self.songList.setObjectName("listWidget")
    self.songList.setFont(StandardFont())
    self.songList.setStyleSheet(style.LIST_WIDGET)
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
    self.setLayout(gboxLayout)

  ##
  #  This is triggered when an item in the list is double clicked. A song will play.
  def onItemDoubleClicked(self, item):
    song = self.names[item.text()]
    self.playing.emit(song)

  ##
  #  On song added, update the dictionary and list widget.
  def onSongAdded(self, fileName):
    self.names[os.path.basename(fileName)] = fileName
    self.songList.addItem(os.path.basename(fileName))


##
#  This is the main widget that will parent
#  most of the GUI's features. 
class MusicWidget(QtGui.QWidget):
  ##
  #  Main initializer function.
  def __init__(self):
    super(MusicWidget, self).__init__()
    self.mediaObject = Phonon.MediaObject(self)
    self.mediaObject.finished.connect(self.onFinished)
    self.output = Phonon.AudioOutput(Phonon.MusicCategory, self)
    self.output.setVolume(50)
    self.path = Phonon.createPath(self.mediaObject, self.output)
    self.setWindowTitle("Media Player")
    self.setObjectName("musicWidget")
    self.setStyleSheet("#musicWidget { background-color: white; }")
    self.started = False
    self.prevSong = None

    mainLayout = QtGui.QHBoxLayout(self)

    self.splitter = QtGui.QSplitter()
    self.splitter.setObjectName("splitter")
    self.splitter.setStyleSheet(style.SPLITTER)

    leftWidget = QtGui.QWidget()
    leftLayout = QtGui.QVBoxLayout(leftWidget)

    self.rightWidget = QtGui.QWidget()
    self.rightLayout = QtGui.QVBoxLayout(self.rightWidget)
    self.groupbox = SongPlayingGroup("Your Songs:")
    self.rightLayout.addWidget(self.groupbox)
    self.rightGroup = URLDownloadingGroup()
    self.rightGroup.songAdded.connect(self.groupbox.onSongAdded)
    self.groupbox.playing.connect(self.onPlaying)
    self.rightLayout.addWidget(self.rightGroup)

    self.splitter.addWidget(leftWidget)
    self.splitter.addWidget(self.rightWidget)

    mainLayout.addWidget(self.splitter)

    buttonLayout = QtGui.QHBoxLayout()
    self.playing = False
    self.playButton = QtGui.QPushButton()
    self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "play.png")))
    self.playButton.setObjectName("playButton")
    self.playButton.setStyleSheet(style.multimediaButton("playButton"))
    self.playButton.setFont(StandardFont())
    self.playButton.clicked.connect(self.playTriggered)
    buttonLayout.addWidget(self.playButton)

    leftLayout.addLayout(buttonLayout)

  ##
  #  This function will act as a slot to the 'play button'
  #  being triggered.
  def onPlaying(self, song):
    self.mediaObject.setCurrentSource(song)
    self.mediaObject.play()
    self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "pause.png")))
    self.prevSong = self.groupbox.names[self.groupbox.songList.currentItem().text()]
    self.playing = True
    self.started = True
    
  ##
  #  Play next song on finished.
  def onFinished(self):
    self.prevSong = self.groupbox.songList.itemFromIndex(self.groupbox.songList.currentRow()+1).text()
    self.groupbox.songList.setCurrentItem(self.prevSong)
    self.prevSong = self.groupbox.names[self.prevSong]
    self.mediaObject.setCurrentSource(self.prevSong)
    self.mediaObject.play()

  ##
  #  This function will act as a slot to the 'play button'
  #  being triggered.
  def playTriggered(self):
    song = self.groupbox.names[self.groupbox.songList.currentItem().text()]
    if self.playing:
      self.playing = False
    else:
      self.playing = True
    if self.playing:
      if (self.prevSong is None) or (self.prevSong != song):
        self.prevSong = song
        self.mediaObject.setCurrentSource(song)
      if self.started == False:
        self.started = True
        self.mediaObject.play()
      elif self.mediaObject.state() == Phonon.PlayingState:
        self.mediaObject.pause()
      else:
        self.mediaObject.play()
      self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "pause.png")))
    else:
      self.mediaObject.pause()
      self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "play.png")))

##
#  This is the main window.
class mainwindow(QtGui.QMainWindow):
  ##
  #  Main intializer.
  def __init__(self):
    super(mainwindow, self).__init__()
    self.setObjectName("mainWindow")
    self.setStyleSheet(style.MAIN_WINDOW)
    self.setGeometry(200, 200, 800, 800)
    exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(self.close)

    self.statusBar()

    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(exitAction)
    self.musicWidget = MusicWidget()
    self.setCentralWidget(self.musicWidget)

