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
#  @author milesw55
import os, sys
import shutil
import subprocess
import re
from src.gui.style import style
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

  def download(self, url, mp4, name, song, artist, album):
    if not re.match("\w+", name):
      self.error.emit("Invalid name for saving song.")
      return
    audioFile = "/downloads/{}".format(name)
    youtube = "youtube-dl"
    ffmpeg = "ffmpeg"
    if sys.platform.startswith("win"):
      youtube = '.\\src\\engine\\youtube-dl.exe'
      ffmpeg = '.\\src\\engine\\ffmpeg\\bin\\ffmpeg.exe'
    elif sys.platform.startswith("darwin"):
      ffmpeg = './src/engine/ffmpeg/bin/ffmpeg'
      # Add code for prompting installation of youtube-dl
    ret = subprocess.call([youtube, '-o', mp4, url], shell=True)
    if (ret != 0):
      self.error.emit("Error downloading. URL may be invalid or copyrighted.")
      return
    command = [ffmpeg, '-i', mp4]
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
    addSong = song is not None and song != ''
    addArtist = artist is not None and artist != ''
    addAlbum = album is not None and album != ''
    if addSong or addArtist or addAlbum:
      if addSong:
        command.append('-metadata')
        command.append('title={}'.format(song))
      if addArtist:
        command.append('-metadata')
        command.append('artist={}'.format(artist))
      if addAlbum:
        command.append('-metadata')
        command.append('album={}'.format(album))
    command.append(".{}".format(audioFile))
    ret = subprocess.call(command, shell=True)
    if (ret != 0):
      self.error.emit("Error ripping audio.")
      os.remove(mp4)
      return
    os.remove(mp4)
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
class URLDownloadingGroup(QtGui.QVBoxLayout):

  ##
  #  Signal of added song.
  songAdded = QtCore.Signal(str)

  ##
  #  Signal for download request.
  downloadRequest = QtCore.Signal(str, str, str, str, str, str)

  ##
  #  Main initializer function.
  def __init__(self, parent):
    super(URLDownloadingGroup, self).__init__()
    self._parent = parent
    # self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
    self.setContentsMargins(0,0,0,0)
    self.findSongGroup = QtGui.QGroupBox()
    self.findSongGroup.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
    self.findSongGroup.setObjectName("urlGroup")
    self.findSongGroup.setStyleSheet(style.GROUP_BOX)
    self.addWidget(self.findSongGroup)

    groupLayout = QtGui.QVBoxLayout(self.findSongGroup)
    groupLayout.setContentsMargins(0,0,0,0)

    urlLayout = QtGui.QHBoxLayout()
    urlLayout.setContentsMargins(0,0,0,0)
    self.urlLine = QtGui.QLineEdit()
    self.urlLine.setStyleSheet("QLineEdit { background-color: #FFF; }")
    self.urlLine.setFont(StandardFont())
    self.addButton = QtGui.QPushButton("Add URL")
    self.addButton.setObjectName("addButton")
    self.addButton.setStyleSheet(style.button("addButton"))
    self.addButton.setFont(StandardFont())
    self.addButton.clicked.connect(self.onAddClicked)
    urlLayout.addWidget(self.urlLine)
    urlLayout.addWidget(self.addButton)


    groupLayout.addLayout(urlLayout)

    self.songButtonLayout = QtGui.QHBoxLayout()
    self.songButtonLayout.setContentsMargins(0,0,0,0)
    
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
    # self.songButtonLayout.addWidget(self.addSongButton)
    self.thread = None

    self.addLayout(self.songButtonLayout)

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
    song = None
    artist = None
    album = None
    text, ok = QtGui.QInputDialog().getText(self._parent, "Download Information", "Song Title:", QtGui.QLineEdit.Normal)
    if ok and text:
      song = text
    text, ok = QtGui.QInputDialog().getText(self._parent, "Download Information", "Artist:", QtGui.QLineEdit.Normal)
    if ok and text:
      artist = text
    text, ok = QtGui.QInputDialog().getText(self._parent, "Download Information", "Album Title:", QtGui.QLineEdit.Normal)
    if ok and text:
      album = text
    mp4 = "{}.mp4".format(song)
    if not os.path.isdir(os.path.join(os.getcwd(), "downloads")):
      os.makedirs(os.path.join(os.getcwd(), "downloads"))
    audioName = "{}{}".format(song, ".mp3")
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
    self.downloadRequest.emit(url, mp4, audioName, song, artist, album)

  ##
  #  Updates.
  def onAudioFileAdded(self, audioFile):
    fileName = os.getcwd() + audioFile
    fileName = fileName.replace("\\", "/")
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
    self.itemToSong = {}
    self.items = []
    gboxLayout = QtGui.QVBoxLayout(self)
    self.songList = QtGui.QTableWidget()
    self.songList.setRowCount(0)
    self.songList.setColumnCount(4)
    self.songList.setHorizontalHeaderLabels(["Track", "Album", "Artist", "Time"])
    self.songList.setObjectName("listWidget")
    self.songList.setFont(StandardFont())
    self.songList.setStyleSheet(style.LIST_WIDGET)
    self.songList.itemDoubleClicked.connect(self.onItemDoubleClicked)
    self.songList.itemChanged.connect(self.onItemChanged)
    self.songList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.connect(
      self.songList,
      QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'),
      self.onContextMenuRequested
    )
    self.remove = QtGui.QAction("Remove", self)
    self.remove.triggered.connect(self.removeTriggered)
    content = ""
    self.names = {}
    with open("songlist.txt", 'a') as f:
      print("songlist.txt does exist\ncontinuing with initialization")
    with open("songlist.txt", 'r') as f:
      content = f.read()
    rows = 0
    for song in content.split('\n'):
      if song != "":
        self.names[os.path.basename(song)] = song
        rows += 1
        self.songList.setRowCount(rows)
        name = os.path.basename(song)
        ffmpeg = "ffmpeg"
        if sys.platform.startswith("win"):
          youtube = '.\\src\\engine\\youtube-dl.exe'
          ffmpeg = '.\\src\\engine\\ffmpeg\\bin\\ffmpeg.exe'
        elif sys.platform.startswith("darwin"):
          ffmpeg = './src/engine/ffmpeg/bin/ffmpeg'
        metaFile = 'metadata.txt'
        ret = subprocess.call([ffmpeg,"-i", song, "-f", "ffmetadata", metaFile], shell=True)
        album = ''
        artist = ''
        length = '0:00'
        lines = []
        with open(metaFile, 'r') as f:
          lines = f.readlines()
        for line in lines:
          if len(line.split("=")) == 2:
            key, value = line.split("=")
            if key == 'title':
              name = value.strip()
            elif key == 'album':
              album = value.strip()
            elif key == 'artist':
              artist = value.strip()
        os.remove(metaFile)
        infoFile = 'info.txt'
        ret = subprocess.call([ffmpeg,"-i", song, "2>{}".format(infoFile)], shell=True)
        with open(infoFile, 'r') as f:
          lines = f.readlines()
        for line in lines:
          if line.strip().startswith("Duration"):
            length = line.strip().split(",")[0].split(" ")[1]
            break
        os.remove(infoFile)
        if length.startswith("00"):
          length = length[3:]
        if length.startswith("0"):
          length = length[1:]
        rest, seconds = length.rsplit(":", 1)
        value = int(float(seconds))
        if float(seconds) - value > 0.5:
          seconds = str(value+1)
          if value+1 < 10:
            seconds = "0" + str(value+1)
        else:
          seconds = str(value)
          if value < 10:
            seconds = "0" + str(value)
        length = rest + ":" + seconds
        fields = [name, album, artist, length]
        items = []
        for idx, field in enumerate(fields):
          item = QtGui.QTableWidgetItem(field)
          print(item.icon().isNull())
          if idx == 3:
            item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
          else:
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable)
          items.append(item)
          self.songList.setItem(rows-1, idx, item)
        self.itemToSong[id(items)] = song
        self.items.append(items)
    self.songList.verticalHeader().hide()
    self.songList.horizontalHeader().setStretchLastSection(True)
    self.songList.setColumnWidth(0, 200)
    self.songList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    self.songList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    self.songList.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
    gboxLayout.addWidget(self.songList)
    self.setLayout(gboxLayout)

  ##
  #  Returns the current song.
  def getCurrentSong(self):
    # Find song name.
    item = self.songList.currentItem()
    __items = None
    song = None
    for _items in self.items:
      for _item in _items:
        if id(_item) == id(item):
          __items = _items
    for items, _song in self.itemToSong.items():
      if __items is not None and id(__items) == items:
        song = _song
    return song
  
  ##
  #  Context Menu Requested.
  def onContextMenuRequested(self, point):
    if self.songList.itemAt(point) is not None:
      self.rightClickMenu = QtGui.QMenu()
      self.rightClickMenu.addAction(self.remove)
      self.rightClickMenu.popup(self.songList.mapToGlobal(point))

  ##
  #  On Item Changed.
  def onItemChanged(self, item):
    columnName = self.songList.horizontalHeaderItem(item.column()).text()
    metaName = None
    metaValue = item.text()
    # Find song name.
    __items = None
    for _items in self.items:
      for _item in _items:
        if id(_item) == id(item):
          __items = _items
    song = None
    for items, _song in self.itemToSong.items():
      if __items is not None and id(__items) == items:
        song = _song
        break
    if columnName == "Track":
      metaName = "title"
    elif columnName == "Album":
      metaName = "album"
    elif columnName == "Artist":
      metaName = "artist"
    if metaName is not None and song is not None:
      ffmpeg = "ffmpeg"
      if sys.platform.startswith("win"):
        youtube = '.\\src\\engine\\youtube-dl.exe'
        ffmpeg = '.\\src\\engine\\ffmpeg\\bin\\ffmpeg.exe'
      elif sys.platform.startswith("darwin"):
        ffmpeg = './src/engine/ffmpeg/bin/ffmpeg'
      cmd = [ffmpeg, "-i", song, "-metadata"]
      out = 'out12341325.wav'
      none = False
      if metaName == "title":
        cmd.append('title={}'.format(metaValue))
        cmd.append(out)
        ret = subprocess.call(cmd, shell=True)
      elif metaName == "album":
        cmd.append('album={}'.format(metaValue))
        cmd.append(out)
        ret = subprocess.call(cmd, shell=True)
      elif metaName == "artist":
        cmd.append('artist={}'.format(metaValue))
        cmd.append(out)
        ret = subprocess.call(cmd, shell=True)
      else:
        none = True
      if not none:
        cmd = [ffmpeg, "-i", out, song, "-y"]
        ret = subprocess.call(cmd, shell=True)
        os.remove(out)
  
  ##
  #  This is triggered when an item in the list is double clicked. A song will play.
  def onItemDoubleClicked(self, item):
    # Find song name.
    __items = None
    song = None
    for _items in self.items:
      for _item in _items:
        if id(_item) == id(item):
          __items = _items
    for items, _song in self.itemToSong.items():
      if __items is not None and id(__items) == items:
        song = _song
        break
    self.playing.emit(song)

  ##
  #  On song added, update the dictionary and list widget.
  def onSongAdded(self, fileName):
    song = fileName
    rows = self.songList.rowCount()
    rows += 1
    self.songList.setRowCount(rows)
    name = os.path.basename(song)
    ffmpeg = "ffmpeg"
    if sys.platform.startswith("win"):
      youtube = '.\\src\\engine\\youtube-dl.exe'
      ffmpeg = '.\\src\\engine\\ffmpeg\\bin\\ffmpeg.exe'
    elif sys.platform.startswith("darwin"):
      ffmpeg = './src/engine/ffmpeg/bin/ffmpeg'
    metaFile = 'metadata.txt'
    ret = subprocess.call([ffmpeg,"-i", song, "-f", "ffmetadata", metaFile], shell=True)
    album = ''
    artist = ''
    length = '0:00'
    lines = []
    with open(metaFile, 'r') as f:
      lines = f.readlines()
    for line in lines:
      if len(line.split("=")) == 2:
        key, value = line.split("=")
        if key == 'title':
          name = value.strip()
        elif key == 'album':
          album = value.strip()
        elif key == 'artist':
          artist = value.strip()
    os.remove(metaFile)
    infoFile = 'info.txt'
    ret = subprocess.call([ffmpeg,"-i", song, "2>{}".format(infoFile)], shell=True)
    with open(infoFile, 'r') as f:
      lines = f.readlines()
    for line in lines:
      if line.strip().startswith("Duration"):
        length = line.strip().split(",")[0].split(" ")[1]
        break
    os.remove(infoFile)
    if length.startswith("00"):
      length = length[3:]
    if length.startswith("0"):
      length = length[1:]
    rest, seconds = length.rsplit(":", 1)
    value = int(float(seconds))
    if float(seconds) - value > 0.5:
      seconds = str(value+1)
      if value+1 < 10:
        seconds = "0" + str(value+1)
    else:
      seconds = str(value)
      if value < 10:
        seconds = "0" + str(value)
    length = rest + ":" + seconds
    fields = [name, album, artist, length]
    items = []
    for idx, field in enumerate(fields):
      item = QtGui.QTableWidgetItem(field)
      if idx == 3:
        item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
      items.append(item)
      self.songList.setItem(rows-1, idx, item)
    self.itemToSong[id(items)] = song
    self.items.append(items)

  ##
  #  Remove Triggered.
  def removeTriggered(self):
    songName = self.getCurrentSong()
    row = self.songList.currentRow()
    self.songList.removeRow(row)
    lines = None
    with open("songlist.txt", "r") as f:
      lines = f.readlines()
    with open("songlist.txt", "w") as f:
      for line in lines:
        if line.strip() != songName:
          f.write(line)

##
#  This is the main widget that will parent
#  most of the GUI's features. 
class MusicWidget(QtGui.QWidget):
  ##
  #  Main initializer function.
  def __init__(self):
    super(MusicWidget, self).__init__()
    self.songs = []
    self.mediaObject = Phonon.MediaObject(self)
    self.mediaObject.finished.connect(self.onFinished)
    self.mediaObject.tick.connect(self.onTick)
    self.mediaObject.totalTimeChanged.connect(self.onTotalTimeChanged)
    self.output = Phonon.AudioOutput(Phonon.MusicCategory, self)
    self.output.setVolume(50)
    self.path = Phonon.createPath(self.mediaObject, self.output)
    self.setWindowTitle("Media Player")
    self.setObjectName("musicWidget")
    self.setStyleSheet("#musicWidget { background-color: white; }")
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    self.started = False
    self.prevSong = None
    self.rightWidget = QtGui.QWidget()
    self.rightLayout = QtGui.QVBoxLayout(self)
    self.groupbox = SongPlayingGroup("Your Songs:")
    self.rightLayout.addWidget(self.groupbox)
    self.rightGroup = URLDownloadingGroup(self)
    self.rightGroup.songAdded.connect(self.groupbox.onSongAdded)
    self.groupbox.playing.connect(self.onPlaying)
    mediaLayout = QtGui.QVBoxLayout()
    self.slider = Phonon.SeekSlider()
    self.slider.setMediaObject(self.mediaObject)
    self.sliderPressed = False
    buttonLayout = QtGui.QHBoxLayout()
    self.backButton = QtGui.QPushButton()
    self.backButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "back.png")))
    self.backButton.setObjectName("backButton")
    self.backButton.setStyleSheet(style.multimediaButton("backButton"))
    self.backButton.setFont(StandardFont())
    self.backButton.clicked.connect(self.backTriggered)
    self.playing = False
    self.playButton = QtGui.QPushButton()
    self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "play.png")))
    self.playButton.setObjectName("playButton")
    self.playButton.setStyleSheet(style.multimediaButton("playButton"))
    self.playButton.setFont(StandardFont())
    self.playButton.clicked.connect(self.playTriggered)
    self.forwardButton = QtGui.QPushButton()
    self.forwardButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "forward.png")))
    self.forwardButton.setObjectName("forwardButton")
    self.forwardButton.setStyleSheet(style.multimediaButton("forwardButton"))
    self.forwardButton.setFont(StandardFont())
    self.forwardButton.clicked.connect(self.forwardTriggered)
    self.timeLabel = QtGui.QLabel("--:--/--:--")
    self.timeLabel.setFont(StandardFont())
    buttonLayout.addWidget(self.backButton)
    buttonLayout.addWidget(self.playButton)
    buttonLayout.addWidget(self.forwardButton)
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(self.timeLabel)
    mediaLayout.addWidget(self.slider)
    mediaLayout.addLayout(buttonLayout)
    self.rightLayout.addLayout(mediaLayout)
    self.rightLayout.addLayout(self.rightGroup)
    
  ##
  #  This function will act as a slot to the 'back button'
  #  being triggered.
  def backTriggered(self):
    song = self.groupbox.getCurrentSong()
    row = self.groupbox.songList.currentRow() - 1
    state = self.mediaObject.state()
    currentTime = self.mediaObject.totalTime() - self.mediaObject.remainingTime()
    if (self.prevSong is None) or row < 0 or currentTime > 3000:
      self.prevSong = song
      self.groupbox.songList.selectRow(row+1)
    else:
      self.groupbox.songList.selectRow(row)
      self.prevSong = self.groupbox.getCurrentSong()
    self.setCurrentSource(self.prevSong)
    if self.started == False:
      self.started = True
      self.mediaObject.play()
      self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "pause.png")))
    elif state == Phonon.PlayingState or row >= 0:
      self.playing = True
      self.mediaObject.play()
      self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "pause.png")))

  ##
  #  Close Event.
  def closeEvent(self, e):
    try:
      self.mediaObject.setCurrentSource(None)
      shutil.rmtree("cached")
    except Exception as ex:
      pass
    e.accept()

  ##
  #  This function will act as a slot to the 'forward button'
  #  being triggered.
  def forwardTriggered(self):
    if not self.started:
      self.started = True
    self.playing = True
    self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "pause.png")))
    self.onFinished()

  ##
  #  Play next song on finished.
  def onFinished(self):
    row = self.groupbox.songList.currentRow() + 1
    if row >= self.groupbox.songList.rowCount():
      self.playing = False
      self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "play.png")))
      return
    self.groupbox.songList.selectRow(row)
    self.prevSong = self.groupbox.getCurrentSong()
    self.setCurrentSource(self.prevSong)
    self.mediaObject.play()
  
  ##
  #  This function will act as a slot to the 'SongPlayingGroup.playing' signal
  #  being triggered.
  def onPlaying(self, song):
    self.prevSong = song
    self.setCurrentSource(song)
    self.mediaObject.play()
    self.playButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "pause.png")))
    self.playing = True
    self.started = True

  ##
  #  Play next song on finished.
  def onTick(self, time):
    seconds = time/1000
    if seconds - int(seconds) < 0.5:
      seconds = int(seconds)
    else:
      seconds = int(seconds) + 1
    _seconds = seconds
    minutes = 0
    while seconds >= 60:
      minutes += 1
      seconds -= 60
    text = self.timeLabel.text()
    index = text.split("/")[1]
    if seconds < 10:
      self.timeLabel.setText("{1}:0{2}/{0}".format(index, minutes, seconds))
    else:
      self.timeLabel.setText("{1}:{2}/{0}".format(index, minutes, seconds))

  ##
  #  Slot for totalTimeChanged.
  def onTotalTimeChanged(self, totalTime):
    seconds = totalTime/1000
    if seconds - int(seconds) < 0.5:
      seconds = int(seconds)
    else:
      seconds = int(seconds) + 1
    _seconds = seconds
    minutes = 0
    while seconds >= 60:
      minutes += 1
      seconds -= 60
    text = self.timeLabel.text()
    index = text.split("/")[0]
    if index == "--:--":
      index = "0:00"
    if seconds < 10:
      self.timeLabel.setText("{0}/{1}:0{2}".format(index, minutes, seconds))
    else:
      self.timeLabel.setText("{0}/{1}:{2}".format(index, minutes, seconds))

  ##
  #  This function will act as a slot to the 'play button'
  #  being triggered.
  def playTriggered(self):
    song = self.groupbox.getCurrentSong()
    if self.playing:
      self.playing = False
    else:
      self.playing = True
    if self.playing:
      if (self.prevSong is None) or (self.prevSong != song):
        self.prevSong = song
        self.setCurrentSource(song)
        row = self.groupbox.songList.currentRow()
        self.groupbox.songList.selectRow(row)
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
  #  Set the current source. Also perform some system dependent
  #  checks.
  def setCurrentSource(self, song):
    if sys.platform.startswith("win") and not song.endswith("wav"):
      songName = song.rsplit("/", 1)[1].rsplit(".", 1)[0]
      songName = "/cached/{}42348096709138027698504.wav".format(songName)
      wavHash = os.getcwd() + songName
      wavHash = wavHash.replace("\\", "/")
      _song = song
      song = wavHash
      if wavHash not in self.songs:
        print("{} not in self.songs".format(wavHash))
        print("Adding...")
        self.songs.append(wavHash)
        print("Complete!")
        self.mediaObject.setCurrentSource(None)
        ffmpeg = '.\\src\\engine\\ffmpeg\\bin\\ffmpeg.exe'
        dir = os.path.dirname(wavHash)
        try:
          os.stat(dir)
        except:
          os.mkdir(dir)
        command = [ffmpeg, '-i', _song, wavHash]
        print(command)
        ret = subprocess.call(command, shell=True)
    self.mediaObject.setCurrentSource(song)

##
#  This is the main window.
class mainwindow(QtGui.QMainWindow):

  ## Signal for letting the widget know that a song has been added.
  songAdded = QtCore.Signal(str)

  ##
  #  Main intializer.
  def __init__(self):
    super(mainwindow, self).__init__()
    self.setObjectName("mainWindow")
    self.setStyleSheet(style.MAIN_WINDOW)
    self.setWindowTitle("Cadence")
    self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), "setup", "images", "windowicon.ico")))
    self.resize(600, 800)
    addFileAction = QtGui.QAction("Add File", self)
    addFileAction.setShortcut('Ctrl+F')
    addFileAction.triggered.connect(self.addFile)
    exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(self.close)
    viewDownloadsAction = QtGui.QAction("Show in folder...", self)
    viewDownloadsAction.setShortcut('Ctrl+D')
    viewDownloadsAction.triggered.connect(self.openDownloadsFolder)
    
    self.statusBar()

    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(addFileAction)
    fileMenu.addAction(exitAction)
    downloadsMenu = menubar.addMenu("&Downloads")
    downloadsMenu.addAction(viewDownloadsAction)
    self.musicWidget = MusicWidget()
    self.songAdded.connect(self.musicWidget.groupbox.onSongAdded)
    self.setCentralWidget(self.musicWidget)

  ##
  #  Adds a local file to the songlist.
  def addFile(self):
    fileName, fileType = QtGui.QFileDialog.getOpenFileName(self, "Add song", os.getcwd(), "Audio Files (*.ogg *.mp3 *.wav)")
    with open("songlist.txt", 'a') as f:
      f.write(fileName + '\n')
    self.songAdded.emit(fileName)

  ##
  #  This function will open the downloads folder.
  def openDownloadsFolder(self):
    cmd = ''
    path = ''
    if sys.platform.startswith("win"):
      cmd = 'explorer'
      path = 'downloads'
    elif sys.platform.startswith("darwin"):
      cmd = 'open'
      path = './downloads'
    else:
      cmd = 'nautilus'
      path = './downloads'
    command = [cmd, path]
    if not sys.platform.startswith("darwin"):
      ret = subprocess.call(command, shell=True)
    else:
      ret = subprocess.call(cmd+' '+path, shell=True)

  ##
  #  Making sure to explicitly close the music widget.
  def closeEvent(self, e):
    self.musicWidget.close()
    e.accept()
