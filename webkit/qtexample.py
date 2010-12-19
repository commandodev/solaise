import sys
import time
import json

from PySide import QtGui, QtDeclarative
import ystockquote

def sendData(data):
    global rootObject
    json_str = json.dumps(data).replace('"', '\\"')
    rootObject.evaluateJavaScript('receiveJSON("%s")' % json_str)

def receiveData(json_str):
    global rootObject
    print json_str
    data = json.loads(json_str)
    print 'Received data:', data

    if len(data) == 2 and data[0] == 'setRotation':
        rootObject.setProperty('rotation', data[1])
    else:
        sendData(ystockquote.get_historical_prices('GOOG', '20100101', '20101201'))

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    view = QtDeclarative.QDeclarativeView()
    view.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
    view.setSource(__file__.replace('.py', '.qml'))
    rootObject = view.rootObject()
    rootObject.setProperty('url', 'http://localhost:6544/GOOG')
    rootObject.alert.connect(receiveData)
    view.show()



    app.exec_()
