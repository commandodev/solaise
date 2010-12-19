#!/usr/bin/env python
from random import randrange
from PySide import QtCore, QtGui

import solaise_cards.rc

# Geometry constants
ROWS = 4
COLS = 13

CARD_H = 107
PAD_H = 10
CARD_W = 75
PAD_W = 5

WINDOW_H = CARD_H*ROWS + PAD_H*(ROWS-1)
WINDOW_W = CARD_W*COLS + PAD_W*(COLS-1)

BTNS_H = 50

class Card(QtCore.QObject):
    """Wrapper around a QGraphicsPixmapItem representing a playing card"""

    SUITE_LOOKUP = dict(d='diamonds', s='spades', c='clubs', h='hearts')
    SUITES = ['s', 'd', 'h', 'c']
    FACES = range(2,11) + list('jqka')

    def __init__(self, face, suite):
        super(Card, self).__init__()
        self.face = face
        self.suite = suite
        # Fetch the correct image for the suite and face
        image_path = ":/img/img/%s-%s-75.png" % (self.SUITE_LOOKUP[suite], face)
        self.pixmap_item = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(image_path))
        self.pixmap_item.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)

    def __str__(self):
        return "%s%s" % (str(self.face).upper(), self.suite)

    def __cmp__(self, other):
        """Custom sorting, first comparing the suite and then the face"""
        suite_cmp = cmp(self.suite_idx, other.suite_idx)
        if suite_cmp == 0:
            return cmp(self.face_idx, other.face_idx)
        else:
            return suite_cmp

    # A property wrapping the position of proxied pixmap
    def set_pos(self, pos):
        self.pixmap_item.setPos(pos)

    def get_pos(self):
        return self.pixmap_item.pos()

    pos = QtCore.Property(QtCore.QPointF, get_pos, set_pos)

    @property
    def suite_idx(self):
        return self.SUITES.index(self.suite)

    @property
    def face_idx(self):
        return self.FACES.index(self.face)


class Hand(list):
    """Subclass of list to hold Card objects"""

    COLS = 13

    def __str__(self):
        return '\n'.join(self)

    def shuffled(self):
        """Return a shuffled copy of self"""
        cpy = self[:]
        shuffled_hand = Hand()
        while cpy:
            shuffled_hand.append(cpy.pop(randrange(0, len(cpy))))
        return shuffled_hand

    def coords_of(self, card):
        """Give column, row coordinates for card"""
        idx = self.index(card)
        return (idx % self.COLS, idx/self.COLS)


    def matrix(self):
        """Break into a matrix, handy for printing and debugging"""
        break_len = self.COLS
        return [self[s:e+1] for s,e in zip(range(0, len(self)-1, break_len),
                                           range(break_len-1, len(self), break_len))]

class CardHolder(QtGui.QGraphicsView):

    def position_for_coords(self, coords):
        """Translate column, row to pixel coords"""
        x, y = coords
        return QtCore.QPointF(x*(CARD_W + PAD_W), y*(CARD_H + PAD_H))

    def resizeEvent(self, event):
        super(CardHolder, self).resizeEvent(event)
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)




def pprint(hand):
    """Convenience debugging function to print a hand of cards"""
    return '\n'.join([' '.join(str(c) for c in row) for row in hand.matrix()])

if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    scene = QtGui.QGraphicsScene(0, 0, WINDOW_W, WINDOW_H+BTNS_H)
    view = CardHolder(scene)

    items = Hand(Card(face, suite) for suite in  Card.SUITES
                                   for face in Card.FACES)

    for i, card in enumerate(items):
        card.pixmap_item.setZValue(i)
        scene.addItem(card.pixmap_item)

    # Buttons.
    buttonFrame = QtGui.QFrame()
    layout = QtGui.QHBoxLayout()
    btn_labels =  [
            (QtGui.QPushButton(), "Shuffle"),
            (QtGui.QPushButton(), "Sort"),
            (QtGui.QPushButton(), "Close")
                ]
    for button, text in btn_labels:
        button.setText(text)
        layout.addWidget(button)
    shuffleButton, sortButton, closeButton = [b for b,l in btn_labels]
    buttonFrame.setLayout(layout)

    proxy = QtGui.QGraphicsProxyWidget()
    proxy.setWidget(buttonFrame)
    proxy.setFlags(QtGui.QGraphicsItem.ItemIgnoresTransformations)
    scene.addItem(proxy)
    proxy.setPos(WINDOW_W-500, WINDOW_H)
    proxy.scale(1.5, 1.5)
    proxy.setZValue(65)

    # View.
    view = CardHolder(scene)
    view.setWindowTitle("Solaise Cards")
    view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
    view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
    view.setRenderHints((QtGui.QPainter.Antialiasing |
                         QtGui.QPainter.SmoothPixmapTransform))

    # States.
    rootState = QtCore.QState()
    sortedState = QtCore.QState(rootState)
    shuffledState = QtCore.QState(rootState)
    centeredState = QtCore.QState(rootState)
    rootState.setInitialState(centeredState)

    def shuffle():
        shuffled = items.shuffled()
        for card in shuffled:
            shuffledState.assignProperty(card, 'pos',
                view.position_for_coords(shuffled.coords_of(card)))

    group = QtCore.QParallelAnimationGroup()
    for i, card in enumerate(items):

        # Animation.
        anim = QtCore.QPropertyAnimation(card, 'pos')
        anim.setDuration(500 + i * 15)
        anim.setEasingCurve(QtCore.QEasingCurve.InOutBack)
        group.addAnimation(anim)

        # Sorted state.
        sortedState.assignProperty(card, 'pos',
                view.position_for_coords(items.coords_of(card)))

        # Initial State.
        posn = view.position_for_coords(items.coords_of(items[32]))
        centeredState.assignProperty(card, 'pos', posn)

    # Transitions.
    states = QtCore.QStateMachine()
    states.addState(rootState)
    states.setInitialState(rootState)

    trans = rootState.addTransition(shuffleButton, "clicked()", shuffledState)
    trans.addAnimation(group)

    trans = rootState.addTransition(sortButton, "clicked()", sortedState)
    trans.addAnimation(group)

    # Timer and eventloop.
    timer = QtCore.QTimer()
    timer.start(125)
    timer.setSingleShot(True)
    trans = rootState.addTransition(timer.timeout, sortedState)
    trans.addAnimation(group)
    states.start()

    view.show()

    # Signals
    QtCore.QObject.connect(shuffleButton, QtCore.SIGNAL("clicked()"), shuffle)
    QtCore.QObject.connect(closeButton, QtCore.SIGNAL("clicked()"), view.close)

    sys.exit(app.exec_())
