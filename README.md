Media Player

contributors: milesw55, ntreado
url: https://github.com/milesw55/mediaplayer.git 

This project will be a GUI based music player
that allows the user to add any number of songs
to the list. Once a player has selected a song
in the list, the user then can play that song
by clicking the play button. Alternatively, the
user can pause that song and continue it at a
later time.

This program will be coded in python and will
use the [PySide](http://pyside.org) and [pygame](http://pygame.org) modules to handle
GUI and media player functions respectively. The
UNIX aspects of the program will be the storing
of file paths for the list of songs. This will be
read from and written to on every startup of the
program and every time a song is added to the GUI's
list.

In addition to the music features, there will
be an option for downloading music from youtube.

Supported Music File types: `wav`, `mp3`, `ogg`

Required packages:

- Python 2.7

  ```
  sudo yum install python
  sudo apt-get install python
  ```    
- pyside

  ```
  sudo yum install pyside
  sudo apt-get install python-pyside
  ```

- pygame

  ```
  sudo yum install pygame
  sudo apt-get install python-pyside
  ```
  
- youtube-dl

  ```
  sudo yum install youtube-dl
  sudo apt-get install youtube-dl
  ```

- ffmpeg
   
  ```
  sudo yum install ffmpeg
  sudo apt-get install ffmpeg
  ```  
- restricted-extras (so ubuntu can play mp3)
  (Fedora + pygame + mp3 = fail), please use .wav when downloading songs from youtube.
  
  ```
  sudo apt-get install ubuntu-restricted-extras 
  ```
