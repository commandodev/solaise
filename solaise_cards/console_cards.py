#!/usr/bin/env python
from random import randrange
    
class Card(object):

    SUITES = ['Spades', 'Diamonds', 'Hearts', 'Clubs']
    FACES = range(2,11) + list('JQKA')

    def __init__(self, face, suite):
        self.face = face
        self.suite = suite

    def __str__(self):
        return "%s of %s" % (self.face, [s for s in self.SUITES
                                         if s[0] == self.suite][0])

    def __repr__(self):
        return "%s%s" % (self.face, self.suite)

    @property
    def suite_idx(self):
        """Get sort order for suite

        >>> c = Card(2, 'S')
        >>> c.suite_idx
        0
        >>> c = Card(10, 'C')
        >>> c.suite_idx
        3
        """
        return [s[0] for s in self.SUITES].index(self.suite)

    @property
    def face_idx(self):
        """Get sort order for face

        >>> c = Card(2, 'S')
        >>> c.face_idx
        0
        >>> c = Card('K', 'H')
        >>> c.face_idx
        11
        """
        return self.FACES.index(self.face)

    def __cmp__(self, other):
        suite_cmp = cmp(self.suite_idx, other.suite_idx)
        if suite_cmp == 0:
            return cmp(self.face_idx, other.face_idx)
        else:
            return suite_cmp

class Hand(list):

    def __str__(self):
        return '\n'.join(self)

    def shuffled(self):
        cpy = self[:]
        shuffled_hand = Hand()
        while cpy:
            shuffled_hand.append(cpy.pop(randrange(0, len(cpy))))
        return shuffled_hand

def hand_to_matrix(hand):
    break_len = len(Card.FACES)
    return [hand[s:e+1] for s,e in zip(range(0, len(hand)-1, break_len),
                                       range(break_len-1, len(hand), break_len))]


hand = Hand(Card(face, suite) for suite in [s[0] for s in Card.SUITES]
                              for face in Card.FACES)

if __name__ == "__main__":
    from pprint import pprint
    print '== SORTED'
    print '\n'.join([' '.join(repr(c) for c in row) for row in hand_to_matrix(hand)])
    print '== SHUFFLED'
    pprint(hand_to_matrix(hand.shuffled()))
    print '== SORTED'
    pprint(hand_to_matrix(sorted(hand.shuffled())))




def test_card_cmp():
    cards = [Card(2, 'S'), Card(3, 'D'), Card(4, 'D'), Card('K', 'S')]
    print sorted(cards)
    c = Card(3, 'S')
    ok_(c < Card(10, 'D'))
    ok_(c > Card(2, 'S'))
    ok_(c == Card(3, 'S'))
