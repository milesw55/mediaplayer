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
import os, sys
from PySide import QtGui, QtCore
from src.gui import mediaplayerui



if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  musicWidget = mediaplayerui.MusicWidget()
  musicWidget.show()
  app.exec_()
