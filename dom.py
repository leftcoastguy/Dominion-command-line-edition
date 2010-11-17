#!/usr/bin/python


# to do

# test what happens if you try to use a card name that is not actually in any
# of the decks (because it will be in the shortcut map )

# still quite a bit of ugliness with this design
# getting/putting back cards for the buyCard() is retarded

# create debug mode

# the decks also need to behave like a queue, since some cards are now going to be
# put on top of the deck.  So shuffling will actually have to randomize the list

# card help
# card help could also be used during play to display what is happening
# as a result of action cards being played

# dash of color
# multi-menu commands?
# dump out statistics at end?
# dump out history of entire game

import random

class Deck:
    def __init__( self ):
        self.__cards = []
        self.__currentCard = 0 # used for iterator only
        self.__numShuffles = 0

    def add( self, card ):
        
        if card is None:
            print "WARN: adding None card to Deck()"
        self.__cards.append( card )

    def deal( self ):

        if len( self.__cards ) == 0:
            raise ValueError

        return self.__cards.pop(0)

    def push( self, card ):
        self.__cards.insert( 0, card )

    def extend( self, cards ):
        self.__cards.extend( cards )

    def shuffle( self ):
        random.shuffle( self.__cards )
        print "...shuffling..."
        self.__numShuffles += 1

    def getNumShuffles( self ):
        return self.__numShuffles

    def getCoin( self ):
        coin = 0
        for card in self.__cards:
            coin += card.value
        return coin

    def __str__( self ):
        s = ""
        for card in self.__cards:
            s += ( card.shortcutName + " " )
        return s

    def __len__( self ):
        return len( self.__cards )

    def empty( self ):
        return ( len( self.__cards ) < 1 )
    
    def remove( self, card ):
        self.__cards.remove( card )

    # might be better to write an == operator for card classes
    def contains( self, card ):
        for c in self.__cards:
            if c.name == card.name:
                return True
        return False

    def getVP( self ):
        vp = 0
        for card in self.__cards:
            vp += card.vp
        return vp

    def getNumProvinces( self ):
        p = 0
        for card in self.__cards:
            if card.name == 'province':
                p += 1
        return p

    def __iter__( self ):
        self.__currentCard = 0
        return self

    def next( self ):
        try:
            card = self.__cards[ self.__currentCard ]
        except:
            self.__currentCard = 0
            raise StopIteration
        self.__currentCard += 1
        return card


class Card:
    def __init__( self, name, shortcutName, cost, value, action, vp, helpText = "" ):
        self.name = name
        self.shortcutName = shortcutName
        self.cost = cost
        self.value = value
        self.action = action
        self.vp = vp
        self.helpText = helpText

    def __repr__( self ):
        return self.shortcutName

    def __eq__( self, other ):
        return self.name == other.name

    def __ne__( self, other ):
        return self.name != other.name

    def play( self, player, players, turn, shortcutMap, deckMap ):
        pass


class Woodcutter( Card ):
    def __init__( self ):
        Card.__init__( self, 'woodcutter', '(wo)odcutter', 3, 0, True, 0, "+1 buy. +2 spend." )

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.numBuys += 1
        player.spendBonus += 2


class Moat( Card ):
    def __init__( self ):
        Card.__init__( self, 'moat', '(mo)at', 2, 0, True, 0, "+2 cards.  When another player plays an attack card, you reveal this from your hand.  If you do, you are unaffected by that attack." )        

    def play( self, player, players, turn, shortcutMap, deckMap ):
        turn.cardsToDeal = 2        

class Cellar( Card ):
    def __init__( self ):
        Card.__init__( self, 'cellar', '(ce)llar', 2, 0, True, 0, "+1 action.  Discard any number of cards.  +1 card per card discarded." )

    def play( self, player, players, turn, shortcutMap, deckMap ):

        while True:
            print "\nhand (%d): %s" % (player.numHands, player.hand)
            discardCard = raw_input("Card name to discard (q to quit)> ")

            if discardCard == 'q':
                break

            player.numActions += 1

            try:
                cardToRemove = shortcutMap[ discardCard ]
            except:
                print "\nHuh?"
                continue
                
            if player.hand.contains( cardToRemove ):
                turn.cardsToDeal += 1
                player.hand.remove( cardToRemove )
                player.discard.add( cardToRemove )
            

class Village( Card ):
    def __init__( self ):
        Card.__init__( self, 'village', '(v)illage', 3, 0, True, 0, "+1 card.  +2 actions.")

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.numActions += 2
        turn.cardsToDeal = 1
    
class Workshop( Card ):
    def __init__( self ):
        Card.__init__( self, 'workshop', '(w)orkshop', 3, 0, True, 0, "Gain a card costing up to 4." )

    def play( self, player, players, turn, shortcutMap, deckMap ):
        
        # gain any card costing up to 4
        # if player changes mind about buy, then don't use up this card
        if not buyCard( deckMap, shortcutMap, player, 4, True ):
            player.hand.add( Workshop() )
            player.numActions += 1


class Militia( Card ):
    def __init__( self ):
        Card.__init__( self, 'militia', '(m)ilitia', 4, 0, True, 0, "+2 spend | Each other player discards down to 3 cards in his hand." )

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.spendBonus += 2
        turn.attacksInPlay[ 'militia' ] = turn.numPlayers - 1

class Smithy( Card ):
    def __init__( self ):
        Card.__init__( self, 'smithy', '(sm)ithy', 4, 0, True, 0, "+3 cards.")

    def play( self, player, players, turn, shortcutMap, deckMap ):
        turn.cardsToDeal = 3

        
class Remodel( Card ):
    def __init__( self ):
        Card.__init__( self, 'remodel', '(r)emodel', 4, 0, True, 0, "Trash a card from your hand.  Gain a card costing up to 2 more than the trashed card." )

    def play( self, player, players, turn, shortcutMap, deckMap ):
        
        while True:
            choice = raw_input("Select a card to trash> ")

            try:
                trashedCard = shortcutMap[ choice ]
            except:
                print "Huh?"
                continue
            
            if player.hand.contains( trashedCard ):
                player.hand.remove( trashedCard )
                break
            else:
                print "You don't have that card in hand."

        # set max value of card to gain
        gainValue = trashedCard.cost + 2

        success = False
        while not success:
            success = buyCard( deckMap, shortcutMap, player, gainValue, True )


class Market( Card ):
    def __init__( self ):
        Card.__init__( self, 'market', '(ma)rket', 5, 0, True, 0, "+1 card  +1 action  +1 buy  +1 spend")

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.numActions += 1
        player.numBuys += 1
        player.spendBonus += 1
        turn.cardsToDeal = 1


class Mine( Card ):
    def __init__( self ):
        Card.__init__( self, 'mine', '(mi)ne', 5, 0, True, 0,"Trash a treasure card from your hand.  Gain a treasure card costing up to 3 more, put it in your hand.  (Basically, copper and silver upgrade to silver and gold, respectively." )

    def play( self, player, players, turn, shortcutMap, deckMap ):

        # dont get stuck in endless input loop if player has no valid
        # coins to trash
        trashList = [ "copper", "silver" ]

        validAction = False
        for cardName in trashList:
            if player.hand.contains( shortcutMap[ cardName ] ):
                validAction = True

        if not validAction:
            player.hand.add( Mine() )
            player.numActions += 1
            print "You have no copper or silver in hand."
            return
            
        while True:
            cardName = raw_input("Select a card to trash> ")
            try:
                trashedCard = shortcutMap[ cardName ]
            except:
                print "Error: %s not in shortcutMap!" % cardName
                break

            if trashedCard.name in trashList and player.hand.contains( trashedCard ):
                player.hand.remove( trashedCard )
                if trashedCard.name == 'copper':
                    # TO DO: deck could be empty
                    mineCard = deckMap['silver'].deal()
                    player.hand.add( mineCard )
                if trashedCard.name == 'silver':
                    # TO DO: deck could be empty                    
                    mineCard = deckMap['gold'].deal()
                    player.hand.add( mineCard )
            else:
                print "Huh?"
            break


class Moneylender( Card ):
    def __init__( self ):
        Card.__init__( self, 'moneylender', '(mon)eylender', 4, 0, True, 0, "Trash a copper from your hand. If you do, +3 spend.")    

    def play( self, player, players, turn, shortcutMap, deckMap ):

        copperCard = shortcutMap[ "copper" ]
        if not player.hand.contains( copperCard ):
            print "You have no copper in hand."
            player.hand.add( Moneylender() )
            player.numActions += 1            
            return

        player.hand.remove( copperCard )
        player.spendBonus += 3


class Chancellor( Card ):
    def __init__( self ):
        Card.__init__( self, 'chancellor', '(ch)ancellor', 3, 0, True, 0, "+2 spend.  You may immediately put your deck into your discard pile.")

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.spendBonus += 2
        player.discard.extend( player.deck )
        player.deck = Deck()

class Festival( Card ):
    def __init__( self ):
        Card.__init__( self, 'festival', '(f)estival', 5, 0, True, 0, "+2 actions.  +1 buy.  +2 spend.")

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.numActions += 2      
        player.numBuys += 1
        player.spendBonus += 2


class Laboratory( Card ):
    def __init__( self ):
        Card.__init__( self, 'laboratory', '(l)aboratory', 5, 0, True, 0, "+2 cards.  +1 action.")

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.numActions += 1
        turn.cardsToDeal = 2


class Feast( Card ):
    def __init__( self ):
        Card.__init__( self, 'feast', '(fe)ast', 4, 0, True, 0, "Trash this card.  Gain a card costing up to 5.")

    def play( self, player, players, turn, shortcutMap, deckMap ):

        if not buyCard( deckMap, shortcutMap, player, 5, True ):
            player.hand.add( Feast() )
            player.numActions += 1

class Adventurer( Card ):
    def __init__( self ):
        Card.__init__( self, 'adventurer', '(a)dventurer', 6, 0, True, 0, "Reveal cards from your deck until you reveal 2 treasure cards. Put those treasure cards into your hand and discard the other revealed cards." )

    def play( self, player, players, turn, shortcutMap, deckMap ):

        print "Playing Adventurer..."
        # if the player somehow doesn't have 2 treasure cards
        # in their deck (unlikely), prevent an endless loop?
        treasureCards = 0
        
        while treasureCards < 2:

            try:
                newCard = player.deck.deal()
            except ValueError:
                player.deck.extend( player.discard )
                player.deck.shuffle()
                player.discard = Deck()
                newCard = player.deck.deal()
            
            print "Dealt %s." % (newCard.shortcutName),
            
            if newCard.value:
                print " Added to hand."
                player.hand.add( newCard )
                treasureCards += 1
            else:
                print " Discarded."
                player.discard.add( newCard )

class Bureaucrat( Card ):
    def __init__( self ):
        Card.__init__( self, 'bureaucrat', '(b)ureaucrat', 4, 0, True, 0, "Gain a silver: put it on top of your deck.  Each other player reveals a victory card from their hand and puts it on top of their deck." )

    def play( self, player, players, turn, shortcutMap, deckMap ):
        player.deck.push( shortcutMap[ "silver" ] )
        turn.attacksInPlay[ "bureaucrat" ] = turn.numPlayers - 1

class Witch( Card ):
    def __init__( self ):
        Card.__init__( self, 'witch', '(wi)tch', 5, 0, True, 0, "+2 cards.  Each other player takes a curse card." )

    def play( self, player, players, turn, shortcutMap, deckMap ):
        turn.cardsToDeal = 2
        turn.attacksInPlay[ "witch" ] = turn.numPlayers - 1

class Spy( Card ):
    def __init__( self ):
        Card.__init__( self, 'spy', '(sp)y', 4, 0, True, 0, "+1 card. +1 action.  Each player (including you) reveals the top card from his deck and either discards it or puts it back, your choice." )

    def play( self, player, players, turn, shortcutMap, deckMap ):
        turn.cardsToDeal = 1
        player.numActions += 1

        # I hate to do this in the card itself, because now it requires
        # passing in all the other players.  However, it will be faster/
        # easier to resolve in right now.
        for other in players:
            if other.name == player.name:
                continue

            # first check to see if other has a moat in hand
            if other.hand.contains( shortcutMap["moat"] ):
                print "%s deflects the attack with a moat." % other.name
                continue
            
            try:
                topCard = other.deck.deal()
            except ValueError:
                other.deck.extend( other.discard )
                other.deck.shuffle()
                other.discard = Deck()
                topCard = other.deck.deal()
            
            print "\nThe top card on %s's deck is %s" % ( other.name, topCard.shortcutName )

            while True:
                fate = raw_input( "(d) discard it or (p) put it back? >" )
                if fate in [ 'd', 'p' ]:
                    break

            if fate == "d":
                print "Discarded %s's %s" % ( other.name, topCard.shortcutName )
                other.discard.add( topCard )
            else:
                print "Put %s's %s back on the deck." % ( other.name, topCard.shortcutName )
                other.deck.push( topCard )

class Thief( Card ):
    def __init__( self ):
        Card.__init__( self, 'thief', '(t)hief', 4, 0, True, 0, "Each player reveals the top 2 cards from his deck. If they reveal any Treasure cards, they trash 1 that you choose.  You may gain any or all of these trashed cards.  They discard the other revealed cards." )

    def play( self, player, players, turn, shortcutMap, deckMap ):

        # this is a fucking nightmare
        localTrash = []
        for other in players:

            if other.name == player.name:
                continue

            # first check to see if other has a moat in hand
            if other.hand.contains( shortcutMap["moat"] ):
                print "%s deflects the attack with a moat." % other.name
                continue

            treasure = 0 # using len( reveal ) would be safer
            reveal = []
            for i in range(2):
                try:
                    topCard = other.deck.deal()
                except ValueError:
                    other.deck.extend( other.discard )
                    other.deck.shuffle()
                    other.discard = Deck()
                    topCard = other.deck.deal()

                if topCard.value:
                    treasure += 1
                reveal.append( topCard )

            print "\nThe next 2 cards from %s's deck are %s, %s." % ( other.name, reveal[0].shortcutName, reveal[1].shortcutName )

            if treasure == 1:
                
                print "You may trash the treasure card if you choose."
                if reveal[0].value:
                    treasureCard = reveal[0]
                    otherCard = reveal[1]
                else:
                    treasureCard = reveal[1]
                    otherCard = reveal[0]
                    
                while True:
                    trashIt = raw_input( "Trash it (y/n) >" )
                    if trashIt in [ "y", "n" ]:
                        break
                    
                if trashIt == "y":
                    print "Trashed %s." % treasureCard
                    localTrash.append( treasureCard )
                else:
                    print "Discarded %s." % treasureCard
                    other.discard.add( treasureCard )
                print "Discarded %s." % otherCard
                other.discard.add( otherCard )
                    
            elif treasure == 2:

                print "You may trash one of the treasure cards."
                
                while True:
                    whichOne = raw_input( "Card name to trash, <enter> to trash nothing> " )

                    # trash nothing
                    if whichOne == "":
                        # discard both
                        for card in reveal:
                            print "Discarded: " % card.shortcutName
                            other.discard.add( card )
                        break

                    # else, argh, get the shortcut
                    try:
                        theCard = shortcutMap[ whichOne ]
                    except:
                        print "Huh?"
                        continue

                    # did we find the card they mean?
                    foundIt = False
                    for card in reveal:
                        if card == theCard:
                            foundIt = True
                    
                    if not foundIt:
                        print "That's not one of the choices."
                        continue

                    # we know there are 2 cards in reveal list, right?
                    # now resolve their choice
                    if reveal[0] == theCard:
                        print "Trashed %s." % reveal[0].shortcutName
                        print "Discarded %s." % reveal[1].shortcutName
                        localTrash.append( reveal[0] )
                        other.discard.add( reveal[1] )
                    else:
                        print "Trashed %s." % reveal[1].shortcutName
                        print "Discarded %s." % reveal[0].shortcutName                        
                        localTrash.append( reveal[1] )
                        other.discard.add( reveal[0] )
                    break
                
            else:
                print "No treasure here."
                # put 'em in the discard pile
                for card in reveal:
                    print "Discarded %s." % card.shortcutName                        
                    other.discard.add( card )
                continue


        # now go through the trash you thief!
        if len( localTrash ):
            print "\nSteal any trashed cards you wish..."
            for card in localTrash:
                print "\n%s: " % card.shortcutName,
                while True:
                    stealIt = raw_input("(t) trash it  or  (s) steal it >")
                    if stealIt in [ "t", "s" ]:
                        break
                if stealIt == "s":
                    print "%s stole a %s!" % ( player.name, card.shortcutName )
                    player.discard.add( card )
        else:
            print "There is nothing to steal!"

class Library( Card ):
    def __init__( self ):
        Card.__init__( self, 'library', '(li)brary', 5, 0, True, 0, "Draw until you have 7 cards in hand.  You may discard any actions cards as you draw them." )

    def play( self, player, players, turn, shortcutMap, deckMap ):

        while len( player.hand ) < 7:
            try:
                topCard = player.deck.deal()
            except ValueError:
                player.deck.extend( player.discard )
                player.deck.shuffle()
                player.discard = Deck()
                topCard = player.deck.deal()
            if topCard.action:
                while True:
                    print "Drew: %s." % topCard
                    keepIt = raw_input( "(d)iscard or (k)eep >" )
                    if keepIt in [ "d", "k" ]:
                        break
                if not keepIt:
                    print "Discarded %s." % topCard
                    player.discard.add( topCard )
                else:
                    print "Keeping %s." % topCard
                    player.hand.add( topCard )
            else:
                print "Keeping %s." % topCard
                player.hand.add( topCard )

            

class Curse( Card ):
    def __init__( self ):
        Card.__init__( self, 'curse', '(cu)rse', 0, 0, False, -1, "Worth -1 VP.")
        
class Estate( Card ):
    def __init__( self ):
        Card.__init__( self, 'estate', '(e)state', 2, 0, False, 1, "Worth 1 VP.")

class Duchy( Card ):
    def __init__( self ):
        Card.__init__( self, 'duchy', '(d)uchy', 5, 0, False, 3, "Worth 3 VP.")        

class Province( Card ):
    def __init__( self ):
        Card.__init__( self, 'province', '(p)rovince', 8, 0, False, 6, "Worth 6 VP.")

class Copper( Card ):
    def __init__( self ):
        Card.__init__( self, 'copper', '(c)opper', 0, 1, False, 0, "1 copper." )

class Silver( Card ):
    def __init__( self ):
        Card.__init__( self, 'silver', '(s)ilver', 3, 2, False, 0, "Worth 2 coppers." )

class Gold( Card ):
    def __init__( self ):
        Card.__init__( self, 'gold', '(g)old', 6, 3, False, 0, "Worth 3 coppers." )

class Player:
    def __init__( self, name ):
        self.name = name
        self.deck = Deck()
        self.hand = Deck()
        self.inPlay = Deck()
        self.discard = Deck()
        self.numHands = 0
        self.spendBonus = 0
        self.numActions = 0
        self.numBuys = 0
        self.AI = False


class TurnState():
    def __init__( self, numPlayers ):
        self.cardsToDeal = 0
        self.attacksInPlay = {}  # { 'card name' : turns }
        self.numPlayers = numPlayers


class Table():
    def __init__( self, numPlayers ):
        self.__numPlayers = numPlayers
        self.pile1 = Deck()
        self.pile2 = Deck()
        self.pile3 = Deck()
        self.pile4 = Deck()
        self.pile5 = Deck()
        self.pile6 = Deck()
        self.pile7 = Deck()
        self.pile8 = Deck()
        self.pile9 = Deck()
        self.pile0 = Deck()
        
        self.pileEstate = Deck()
        self.pileDuchy = Deck()
        self.pileProvince = Deck()
        self.pileCurse = Deck()
        
        self.pileCopper = Deck()
        self.pileSilver = Deck()
        self.pileGold = Deck()
        
        self.deckMap = {}

        # setup method
        self.__setupPiles()

    # decks is just a list of card instances  [ Moat(), Cellar(), Moneylender() ]
    def __setupPiles( self ):

        # the deckMap maps user-input strings (ie. card names)
        # to actual decks
        # also, a handle to all the deck piles
        self.deckMap = { "copper" : self.pileCopper,
                         "silver" : self.pileSilver,
                         "gold" : self.pileGold,
                         "estate" : self.pileEstate,
                         "duchy" : self.pileDuchy,
                         "province" : self.pileProvince,
                         "curse" : self.pileCurse }

        if self.__numPlayers <= 2:
            cardsInDeck = 8
        else:
            cardsInDeck = 12

        # set up variable number of vp cards
        for i in range(cardsInDeck):
            self.pileEstate.add( Estate() )
            self.pileDuchy.add( Duchy() )
            self.pileProvince.add( Province() )


        for i in range(60):    
            self.pileCopper.add( Copper() )

        for i in range(40):    
            self.pileSilver.add( Silver() )

        for i in range(30):
            self.pileCurse.add( Curse() )
            self.pileGold.add( Gold() )


    # if this method is not called independently at setup time
    # there will be no kingdom cards for the game to use!
    # The cardList is a list of kingdom card instances
    def setKingdomCards( self, cardList ):
        
        # Is this Python?
        self.deckMap[ cardList[1].name ] = self.pile1
        self.deckMap[ cardList[2].name ] = self.pile2
        self.deckMap[ cardList[3].name ] = self.pile3
        self.deckMap[ cardList[4].name ] = self.pile4
        self.deckMap[ cardList[5].name ] = self.pile5
        self.deckMap[ cardList[6].name ] = self.pile6
        self.deckMap[ cardList[7].name ] = self.pile7
        self.deckMap[ cardList[8].name ] = self.pile8
        self.deckMap[ cardList[9].name ] = self.pile9
        self.deckMap[ cardList[0].name ] = self.pile0

        for i in range(10):
            self.pile1.add( cardList[1] )
            self.pile2.add( cardList[2] )
            self.pile3.add( cardList[3] )
            self.pile4.add( cardList[4] )
            self.pile5.add( cardList[5] )
            self.pile6.add( cardList[6] )
            self.pile7.add( cardList[7] )
            self.pile8.add( cardList[8] )
            self.pile9.add( cardList[9] )
            self.pile0.add( cardList[0] )


def setUpShortcuts():

    shortcutMap = {
        'p': Province(),
        'province': Province(),
        'e': Estate(),
        'estate': Estate(),        
        'd': Duchy(),
        'duchy': Duchy(),        
        'mo': Moat(),
        'moat': Moat(),        
        'ce': Cellar(),
        'cellar': Cellar(),        
        'v': Village(),
        'village': Village(),        
        'wo': Woodcutter(),
        'woodcutter': Woodcutter(),        
        'w': Workshop(),
        'workshop': Workshop(),        
        'm': Militia(),
        'militia': Militia(),        
        'sm': Smithy(),
        'smithy': Smithy(),        
        'r': Remodel(),
        'remodel': Remodel(),        
        'ma': Market(),
        'market': Market(),        
        'mi': Mine(),
        'mine': Mine(),        
        'g': Gold(),
        'gold': Gold(),        
        's': Silver(),
        'silver': Silver(),        
        'c': Copper(),
        'copper': Copper(),        
        'mon': Moneylender(),
        'moneylender': Moneylender(),        
        'ch': Chancellor(),
        'chancellor': Chancellor(),        
        'f': Festival(),
        'festival': Festival(),        
        'l': Laboratory(),
        'laboratory': Laboratory(),        
        'fe': Feast(),
        'feast': Feast(),
        'a': Adventurer(),
        'adventurer': Adventurer(),
        'b': Bureaucrat(),
        'bureaucrat': Bureaucrat(),
        'cu': Curse(),
        'curse': Curse(),
        'wi': Witch(),
        'witch': Witch(),
        'sp': Spy(),
        'spy': Spy(),
        't': Thief(),
        'thief': Thief(),
        'li': Library(),
        'library': Library(),
        
        }

    return shortcutMap


# this route just peaks at all card piles for a player
def dumpDecks( player ):
    print "Deck dump (btw, this is cheating!):"
    print "cards in hand: ", player.hand
    print "cards in deck: ", player.deck
    print "cards in play: ", player.inPlay
    print "cards in discard: ", player.discard


# max spend is the upper limit of cards to display
# and determines which cards are available for purchase on this buy

# return whether or not someone bought a card
def buyCard( deckMap, shortcutMap, player, maxSpend, freeCard = False ):

    print "\nCard Costs\n"

    for i in range( maxSpend + 1 ):

        cardChoices = []
        # could add a shortcut instance to Card()
        # then print that as the shortcut option
        # still requires maintaining separate shortcutMap (for now)
        
        # OMG this is an awful hack!
        # makes doing a list comprehension nigh
        for deck in deckMap.values():
            if deck.empty():
                continue

            # TO DO: this really needs fixing
            # get the card
            card = deck.deal()

            if card.cost == i:
                cardChoices.append( card.shortcutName )
                
            # now put it back, cringe
            deck.add( card )

        if len( cardChoices ) > 0:
            print "%d: " % (i),
            for thisCard in cardChoices:
                print "%s " % ( thisCard ),
            print

    while True:
        cardName = raw_input("\nName of card to buy> ")
        try:
            card = shortcutMap[ cardName ]
            break
        except:
            print "\nThat card name is not valid."            
            
    if deckMap[ card.name ].empty():
        print "That deck is empty."
        return False


    # get the card
    card = deckMap[ card.name ].deal()

    # any maxSpend restriction for this "buy"
    if card.cost > maxSpend:
        print "That card is not available for this transaction."
        return False

    # enough coin or free card?
    if (( player.spendBonus + player.hand.getCoin() ) >= card.cost or freeCard ):
            
        player.discard.add( card )
        print "\n%s bought a %s.\n" % ( player.name, card.name )

        # if they get this "buy" due to another card (ie. remodel)
        # then it doesn't cost them one of their buys or end their actions this turn
        if freeCard:
            return True

        player.numBuys -= 1
        player.numActions = 0

        # remove money cards from hand
        totalToDeduct = card.cost

        # use up the spend bonus first
        if totalToDeduct >= player.spendBonus:
            totalToDeduct -= player.spendBonus
            player.spendBonus = 0
        else:
            player.spendBonus -= totalToDeduct
            totalToDeduct = 0

        # try to spend gold, then silver, then copper
        cardsToRemove = [] # coin to remove from hand        
        for coin in [ 'gold', 'silver', 'copper' ]:
            
            for moneyCard in player.hand:
                if moneyCard.name == coin and moneyCard.value <= totalToDeduct:
                    totalToDeduct -= moneyCard.value
                    cardsToRemove.append( moneyCard )

        # discard coin
        for spentCard in cardsToRemove:
            player.hand.remove( spentCard )
            player.discard.add( spentCard )

        return True

    else:
        print "You don't have enough for that."        
        deckMap[ card.name ].add( card )

    return False


def main():

    random.seed(None)

    while True:
        numPlayers = raw_input("\nNumber of Players (1-4) > ")
        try:
            numPlayers = int(numPlayers)
        except:
            print "\nPlease enter a valid number."
            continue
        if numPlayers > 0 and numPlayers < 5:
            break

    # set up the game decks
    gameTable = Table( numPlayers )

    # to change the cards in play, must manually edit this list
    # for now
    
    basicCards = [ Moat(), Cellar(), Village(), Woodcutter(), Workshop(),
                   Militia(), Smithy(), Remodel(), Market(), Mine() ]

    longSilver = [ Moat(), Cellar(), Village(), Woodcutter(), Feast(),
                   Bureaucrat(), Remodel(), Spy(), Market(), Adventurer() ]

    basicThief = [ Moat(), Cellar(), Village(), Woodcutter(), Moneylender(),
                   Thief(), Remodel(), Library(), Market(), Mine() ]
    
    startingCards = basicThief
    
    gameTable.setKingdomCards( startingCards )

    # set up shortcuts
    shortcutMap = setUpShortcuts()

    # create the players
    players = []
    for i in range(numPlayers):
        print "\nPlayer ", (i + 1)
        name = raw_input("Enter your name> ")
        players.append( Player( name ) )

    # deal the hand
    for i in range(numPlayers):
        for j in range(7):
            players[i].deck.add( Copper() )

        for j in range(3):
            players[i].deck.add( Estate() )

        players[i].deck.shuffle()

        # deal me a new one pardner
        for j in range(5):
            try:
                card = players[i].deck.deal()
            except ValueError:
                players[i].deck.extend( players[i].discard )
                players[i].deck.shuffle()
                players[i].discard = Deck()
                card = players[i].deck.deal()
            players[i].hand.add( card )

        
    isNewHand = True
    vp = 0

    p = 0  # start with first player

    # now that there are actual card instances with play() methods
    # I need a magical container to pass in to contain all the
    # turn state that needs to be acted upon
    turn = TurnState( numPlayers )

    while True:

        # numPlayers is actually the number of players entered at beginning
        # p is the current player number starting with player 0
        # when displaying p, increment by 1
        if p == turn.numPlayers:
            p = 0
        
        player = players[p]

        # check for end game???
        gameOver = False
        if gameTable.deckMap[ 'province' ].empty():
            print "The province deck is empty."
            gameOver = True

        # look at kingdom card decks now
        numEmptyDecks = 0
        emptyDeckNames = []
        for ( deckName, deck ) in gameTable.deckMap.items():
            if deckName in [ 'estate', 'duchy', 'province', 'copper', 'silver', 'gold' ]:
                continue
            if deck.empty():
                numEmptyDecks += 1
                emptyDeckNames.append( deckName )

        if numEmptyDecks:
            print "These kingdom card decks are now empty: ", emptyDeckNames

        if numEmptyDecks >= 3:
            gameOver = True

        if gameOver:
            print "*******************************"
            print "********** GAME OVER **********"
            
            for i in range( turn.numPlayers ):
                players[i].deck.extend( players[i].inPlay )
                players[i].deck.extend( players[i].hand )
                players[i].deck.extend( players[i].discard )                
                print "Player: %d *%s* VP: %d" % ( i + 1, players[i].name, players[i].deck.getVP())
            print "*******************************"
            print "*******************************"

            for i in range( turn.numPlayers ):
                # lets count all the cards in each players hand
                counts = {}
                for card in players[i].deck:
                    if counts.has_key( card.name ):
                        counts[ card.name ] += 1
                    else:
                        counts[ card.name ] = 1
                print "Player %s" % ( players[i].name)
                for (cardName, count) in counts.items():
                    print "     %s %d" % ( cardName, count )
            break

        taskList = [ '+', 'x', 'h', 'c' ]

        # if the game is not over, keep going
        # deal 5 cards, reset counters
        if isNewHand:
            print "\n+++++++++++++++++++++++++++++++++++++++++++++++++++"
            player.numHands += 1
            player.numBuys = 1
            player.numActions = 0
            player.spendBonus = 0

            # determine actions for this hand
            # do you have any single action card in hand?
            for card in player.hand:
                if card.action:
                    player.numActions += 1
                    break

            vp = 0
            provinces = 0
            for card in player.hand:
                vp += card.vp
                if card.name == 'province':
                    provinces += 1
            vp += player.deck.getVP()
            provinces += player.deck.getNumProvinces()

        # next action this hand (or new hand)
        print "\n%s, your turn.  (%d/%d)" % ( player.name, player.deck.getNumShuffles(), player.numHands )
        print "Hand: %s" % (player.hand)
        print "Actions: %d  Buys: %d  Spend: $%d\n" % ( player.numActions, player.numBuys, player.spendBonus + player.hand.getCoin() )

        # deal with attack cards in play
        if isNewHand:
            
            isNewHand = False
            
            # get rid of finished attacks
            finishedAttacks = []
            for ( cardName, turns ) in turn.attacksInPlay.items():
                if turns == 0:
                    finishedAttacks.append( cardName )

            for cardName in finishedAttacks:
                del turn.attacksInPlay[ cardName ]
                
            for ( cardName, turns ) in turn.attacksInPlay.items():
            
                if cardName == 'militia':

                    turn.attacksInPlay[ 'militia' ] -= 1                
                    print "A militia card is in play."
                    
                    if player.hand.contains( shortcutMap["moat"] ):
                        print "You deflect the attack with the moat.\n"
                        
                    else:
                        print "You must discard 2 cards now.\n"

                        numDiscarded = 0
                        while True:
                            print "\nhand (%d): %s" % (player.numHands, player.hand)

                            if numDiscarded >= 2: break

                            cardName = raw_input("Card name to discard> ")
                            try:
                                discardCard = shortcutMap[ cardName ]
                            except:
                                print "Huh?"
                                continue
                            
                            if player.hand.contains( discardCard ):
                                numDiscarded += 1
                                player.hand.remove( discardCard )
                                player.discard.add( discardCard )

                if cardName == "bureaucrat":

                    print "A bureaucrat card is in play."

                    turn.attacksInPlay[ "bureaucrat" ] -= 1

                    if player.hand.contains( shortcutMap["moat"] ):
                        print "You deflect the attack with the moat.\n"
                    else:
                        
                        cardToRemove = None
                        for card in player.hand:
                            if card.vp:
                                cardToRemove = card
                                break
                    
                        if cardToRemove:
                            print "Putting %s from your hand on top of your deck.\n" % cardToRemove.shortcutName
                            player.hand.remove( cardToRemove )
                            player.deck.push( cardToRemove )
                        else:
                            print "You have no VP cards in your hand.\n"

                if cardName == "witch":

                    print "A witch is in play!"

                    turn.attacksInPlay[ "witch" ] -= 1

                    if player.hand.contains( shortcutMap["moat"] ):
                        print "You deflect the attack with the moat.\n"
                    else:
                        newCurse = None
                        try:
                            newCurse = gameTable.deckMap[ "curse" ].deal()
                        except:
                            print "No curse cards remaining."

                        if newCurse:
                            print "You take a curse.\n"
                            player.discard.add( newCurse )
                        
        # show available menu options to player
        if player.numActions > 0:
            for card in player.hand:
                if card.action:
                    taskList += 'a'
                    break
            
        if 'a' in taskList:
            print "(a) action"

        if ( player.hand.getCoin() + player.spendBonus) > 0  and player.numBuys > 0:
            print "(b) buy card (into discard pile)"
            taskList += 'b'

        print "(c) count kingdom cards"
        print "(h) card help"
        print "(x) finished with turn"
                
        while True:
            task = raw_input("> ")
            if task in taskList:
                break
            else:
                print "Huh?"

        # buy cards        
        if task == 'b':
            buyCard( gameTable.deckMap, shortcutMap, player, 8 )
        
        if task == '+':
            dumpDecks( player )

        # *******************************************************
        # play action
        
        if task == 'a':

            while True:

                card = raw_input("\nCard to play> ")

                # first see if they entered a shortcut
                try:
                    card = shortcutMap[ card ]
                    break
                except:
                    print "Huh?"
                    continue

            if not player.hand.contains( card ):
                print "You don't have that card in hand."

            else:

                # reset turn.cardsToDeal every action
                turn.cardsToDeal = 0

                # get the card from hand so it can't be used
                # again during this turn
                cardInPlay = card

                if not cardInPlay.action:
                    print "That is not an action card."

                else:

                    # take the card from the hand
                    player.hand.remove( cardInPlay )

                    # immediately put the card into the inPlay deck
                    player.inPlay.add( cardInPlay )

                    # resolve the card
                    cardInPlay.play( player, players, turn, shortcutMap, gameTable.deckMap )

                    # decrement actions remaining
                    player.numActions -= 1

                    # remove this option from the menu
                    if player.numActions == 0:
                        if 'a' in taskList:
                            taskList.remove( 'a' )

                    # put new cards into hand
                    for i in range( turn.cardsToDeal ):
                        try:
                            newCard = player.deck.deal()
                        except ValueError:
                            player.deck.extend( player.discard )
                            player.deck.shuffle()
                            player.discard = Deck()
                            newCard = player.deck.deal()

                        player.hand.add( newCard )


        # *******************************************************
            
        if task == 'x':
            # if a feast was played, the card gets trashed
            # after it's played
            while player.inPlay.contains( shortcutMap[ "feast" ] ):
                player.inPlay.remove( shortcutMap[ "feast" ] )
                
            player.discard.extend( player.inPlay )
            player.inPlay = Deck()
            isNewHand = True


        if task == 'h':
            print "Sorry, I changed my mind."

        if task == 'c':
            for( deckName, deck ) in gameTable.deckMap.items():
                if deckName in [ 'copper', 'silver', 'gold' ]:
                    continue
                print "%s %d" % ( deckName, len( deck ))

        # put cards in hand into discard pile
        if isNewHand:
            player.discard.extend( player.hand )
            player.hand = Deck()

            # deal me another
            for i in range(5):
                try:
                    card = player.deck.deal()
                except ValueError:
                    player.deck.extend( player.discard )
                    player.deck.shuffle()
                    player.discard = Deck()
                    card = player.deck.deal()
                player.hand.add( card )

                    

            # next players turn now
            p += 1


if __name__ == '__main__':
    main()
