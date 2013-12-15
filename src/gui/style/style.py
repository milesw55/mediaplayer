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
}"""
  return ret

## GROUP BOX

GROUP_BOX = """#urlGroup {
  border: 4px solid black;
  border-radius: 5px;
  background-color: #AAA;
}"""

## SPLITTER

SPLITTER = """#splitter:handle {
  background-color: transparent;
}
"""
