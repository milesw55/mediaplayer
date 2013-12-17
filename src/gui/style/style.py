# This file holds important style sheets
# for the media player app.

## BUTTONS

def button(name):
  ret = "#" + name + """ {
  color: #00d0d4;
  border: 2px solid #444;
  background: #111;
  border-radius: 3px;
  min-width: 80px;
  max-width: 80px;
}

#""" + name + """:hover {
  color: #00d0d4;
  border: 2px solid #444;
  background: #333;
  border-radius: 3px;
  min-width: 80px;
  max-width: 80px;
}

#""" + name + """:pressed {
  color: #00d0d4;
  border: 2px solid #444;
  background: #000;
  border-radius: 3px;
  min-width: 80px;
  max-width: 80px;
}

#""" + name + """:disabled {
  color: #333;
  border: 2px solid #444;
  background: #666;
  border-radius: 3px;
  min-width: 80px;
  max-width: 80px;
}"""
  return ret

def multimediaButton(name):
  ret = "#" + name + """ {
  color: #00d0d4;
  border: 2px solid #444;
  background: #111;
  border-radius: 10px;
  min-width: 40px;
  max-width: 40px;
}

#""" + name + """:hover {
  color: #00d0d4;
  border: 2px solid #444;
  background: #333;
  border-radius: 10px;
  min-width: 40px;
  max-width: 40px;
}

#""" + name + """:pressed {
  color: #00d0d4;
  border: 2px solid #444;
  background: #000;
  border-radius: 10px;
  min-width: 40px;
  max-width: 40px;
}

#""" + name + """:disabled {
  color: #333;
  border: 2px solid #444;
  background: #666;
  border-radius: 10px;
  min-width: 40px;
  max-width: 40px;
}"""
  return ret

## GROUP BOX

GROUP_BOX = """#urlGroup {
  border: 4px solid black;
  border-radius: 5px;
  background-color: #AAA;
}"""

## LIST WIDGET

LIST_WIDGET = """#listWidget:item:selected {
  color: black;
  background-color: #00d0d4;
}
"""

## SPLITTER

SPLITTER = """#splitter:handle {
  background-color: transparent;
}
"""

## MAIN WINDOW
MAIN_WINDOW = """#mainWindow { background: qlineargradient(x0: 1, y0: 1, x1: 0, y1: 1, stop: 1 #00d0d4, stop: 0.8 #FFF, stop: 0.2 #FFF, stop: 0 #000); }"""
