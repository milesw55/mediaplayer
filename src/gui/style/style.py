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

## COMBO BOX

COMBO_BOX = """#fileType {
  color: #000;
  background: #fff;
  border: 2px solid #444;
  border-radius: 3px;
  min-width: 55px;
  max-width: 55px;
}
"""

## GROUP BOX

GROUP_BOX = """#urlGroup {
  border: 0px solid black;
}"""

## LIST WIDGET

LIST_WIDGET = """#listWidget:item:selected {
  color: black;
  background-color: #00d0d4;
}
"""

## SLIDER

SLIDER = """QSlider::groove:horizontal {
     border: 1px solid #999999;
     height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
     background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
     margin: 2px 0;
 }

 QSlider::handle:horizontal {
     background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
     border: 1px solid #5c5c5c;
     width: 18px;
     margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
     border-radius: 3px;
 }"""

## SPLITTER

SPLITTER = """#splitter:handle {
  background-color: transparent;
}
"""

## MAIN WINDOW
MAIN_WINDOW = """#mainWindow { background: qlineargradient(x0: 1, y0: 1, x1: 0, y1: 1, stop: 1 #00d0d4, stop: 0.8 #FFF, stop: 0.2 #FFF, stop: 0 #000); }"""
