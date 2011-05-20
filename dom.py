#!/usr/bin/python

# to do
# python style comments for classes/methods
# comment style s/b consistent

# bug
# throne roomed a remodel
# remodeled copper into estate
# tried to remodel the esate into gardens (said no estate in hand)
# this is b/c remodeled card uses buyCard() which just tosses
# all the card in the discards (need to know the card at least, or else
# have buyCard() return a card instead
# or maybe take a deck to put the card into... :)

# bug
# curse actually should be in buy menu (for evaluating remodel options)
# but it shouldn't be buy-able

# bug
# attacks are generally broken in 3-4 player games
# attacks/actions that manipulate other players
# decks should be immediately resolved to ensure proper
# deck state.  If player 1 plays a council room, which
# entitles player 2 & 3 to draw from their deck into
# their hand, then player 2 plays a spy, which peaks at
# the top card on each players deck, player 3 will not have
# drawn their council room card yet and so player 2 will
# actually get to potentially discard that card!
# This is all going to be fixed in a refactor.

# bug
# throne room. If you play throne room during a turn but then
# don't take anymore actions, the throne room is still active on
# the next turn!

# bug
# colorama escape codes shouldn't be used if colorama
# module isn't present

# refactor
# menu commands should be in a dict of command to functions

# refactor
# when a player is playing their action cards, all of their actions/
# attacks will be handled immediately, except in the case where the
# resolution depends on other players making choices.  Currently,
# this is only the militia card. The militia card will get a new
# attribute, like delayedResolution or something, such that it will
# be resolved by players on their turn.  Everything else will be
# resolved immediately.  Further, card will be dealt to players within
# the play() method, rather than after the play() method returns.
# this is necessary in cases like Spy.

# feature request
# change (c) count kingdom cards option to something like
# (s) show kingdom cards (name, price, # card remaining)

# feature request
# report first province bought might be cool
# also if someone's opening hand is 5 copper, making a snide comment
# (about shuffling perhaps?) might be cute.  Could dress up the
# actions/attacks messaging a bit in general.

# feature request
# what about coloring the attack card red? Even though this isn't
# the way the actual Dominion cards are colored. Might be worth
# trying.

# feature request
# create debug mode

# feature request
# game log files


import random


# if colorama isn't found, that's ok
# we should just set the colored text strings if the import
# succeeds and if it doesn't, I could print a message about
# how the game looks prettier if colorama is installed

try:
    import colorama
except ImportError:
    print "ImportError: Couldn't find the colorama module."
    colorama = None


class Error( Exception ):
    pass


class CanceledAction( Error ):
    pass


class IllegalAction( Error ):
    pass


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

    def peek( self ):
        if len( self.__cards ) == 0:
            raise ValueError
        
        return self.__cards[0]

    def push( self, card ):
        self.__cards.insert( 0, card )

    def extend( self, cards ):
        self.__cards.extend( cards )

    def shuffle( self ):
        random.shuffle( self.__cards )
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
            s += ( "%s " % card )

        return s

    def __len__( self ):

        return len( self.__cards )

    def empty( self ):

        return ( len( self.__cards ) < 1 )
    
    def remove( self, card ):
        self.__cards.remove( card )

    def contains( self, card ):
        for c in self.__cards:
            if c.name == card.name:
                return True

        return False

    def getVP( self ):
        vp = 0
        for card in self.__cards:
            if card.name == "gardens":
                vp += ( card.vp * ( self.__len__() / 10 ))
            else:
                vp += card.vp
        return vp

    def getNumProvinces( self ):
        p = 0
        for card in self.__cards:
            if card.name == "province":
                p += 1
        return p

    def __iter__( self ):
        self.__currentCard = 0
        return self

    def next( self ):
        try:
            card = self.__cards[ self.__currentCard ]
        # should this except be catching a KeyError?
        except:
            self.__currentCard = 0
            raise StopIteration
        self.__currentCard += 1

        return card


class Attack:
    def __init__( self, cardName, playerName ):
        self.attackName = cardName
        self.playerName = playerName


class Card:
    def __init__( self, name, displayName, shortcut,
                  cost, value, action, vp,
                  helpText = "" ):
        self.name = name
        self.displayName = displayName
        self.shortcut = shortcut
        self.cost = cost
        self.value = value
        self.action = action
        self.vp = vp
        self.helpText = helpText

    def __repr__( self ):

        return "%s" % self.displayName

    def __eq__( self, other ):

        return self.name == other.name

    def __ne__( self, other ):

        return self.name != other.name

    def play( self, player, players, turn, supply ):
        pass


class Woodcutter( Card ):
    def __init__( self ):
        Card.__init__( self, "woodcutter", "(wo)odcutter", "wo",
                       3, 0, True, 0,
                       "+1 buy. +2 spend." )

    def play( self, player, players, turn, supply ):
        print "Playing %s, +1 buy, +2 spend.\n" % self.name
        player.numBuys += 1
        player.spendBonus += 2


class Moat( Card ):
    def __init__( self ):
        Card.__init__( self, "moat", "\033[36m(mo)at\033[39m", "mo",
                       2, 0, True, 0,
                       "+2 cards. Defend against other player attacks." )

    def play( self, player, players, turn, supply ):
        print "Playing %s, +2 cards." % self.name
        player.drawCards( 2 )


class Cellar( Card ):
    def __init__( self ):
        Card.__init__( self, "cellar", "(ce)llar", "ce",
                       2, 0, True, 0,
                       "+1 action. Discard any number of cards. " \
                       "+1 card per card discarded." )

    def play( self, player, players, turn, supply ):
        print "Playing %s, +1 action." % self.name
        player.numActions += 1
        numCardsDiscarded = 0
        
        while True:
            print "\nhand: %s" % player.hand
            discardCard = raw_input("Card name to discard (q to quit)> ")

            if discardCard == "q":
                break

            try:
                cardToRemove = supply.cardShortcuts[discardCard]
            except KeyError:
                print "\nHuh?"
                continue
                
            if player.hand.contains( cardToRemove ):
                print "Discarded %s." % cardToRemove.displayName
                numCardsDiscarded += 1
                player.hand.remove( cardToRemove )
                player.discard.add( cardToRemove )

        if numCardsDiscarded:
            player.drawCards( numCardsDiscarded )
        else:
            raise CanceledAction()
        

class Village( Card ):
    def __init__( self ):
        Card.__init__( self, "village", "(v)illage", "v",
                       3, 0, True, 0,
                       "+1 card.  +2 actions.")

    def play( self, player, players, turn, supply ):
        print "Playing %s, +2 actions, +1 card.\n" % self.name
        player.drawCards( 1 )
        player.numActions += 2

    
class Workshop( Card ):
    def __init__( self ):
        Card.__init__( self, "workshop", "(w)orkshop", "w",
                       3, 0, True, 0,
                       "Gain a card costing up to 4." )

    def play( self, player, players, turn, supply ):
        print "Playing %s.\n" % self.name

        # gain any card costing up to 4
        # if player changes mind about buy, then don't use up this card
        # this creates a duplicate card, oooops
        if not buyCard( supply, player, 4, True ):
            raise CanceledAction()


class Militia( Card ):
    def __init__( self ):
        Card.__init__( self, "militia", "(m)ilitia", "m",
                       4, 0, True, 0,
                       "+2 spend. Each other player discards " \
                       "down to 3 cards." )

    def play( self, player, players, turn, supply ):
        print "Playing %s, +2 spend.\n" % self.name
        player.spendBonus += 2
        turn.attacksInPlay.append( Attack( self.name, player.name ))


class Smithy( Card ):
    def __init__( self ):
        Card.__init__( self, "smithy", "(sm)ithy", "sm",
                       4, 0, True, 0,
                       "+3 cards.")

    def play( self, player, players, turn, supply ):
        print "Playing %s, +3 cards.\n" % self.name
        player.drawCards( 3 )

        
class Remodel( Card ):
    def __init__( self ):
        Card.__init__( self, "remodel", "(r)emodel", "r",
                       4, 0, True, 0,
                       "Trash a card in hand. Gain a card worth up " \
                       "to 2 more coins." )

    def play( self, player, players, turn, supply ):
        print "Playing %s.\n" % self.name

        while True:
            choice = raw_input("Select a card to trash (q to quit)> ")

            if choice == "q":
                raise CanceledAction()

            try:
                trashedCard = supply.cardShortcuts[choice]
            except KeyError:
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
            success = buyCard( supply, player, gainValue, True )


class Market( Card ):
    def __init__( self ):
        Card.__init__( self, "market", "(ma)rket", "ma",
                       5, 0, True, 0,
                       "+1 card.  +1 action.  +1 buy.  +1 spend.")

    def play( self, player, players, turn, supply ):
        print "Playing %s, +1 card, +1 action, +1 buy, +1 spend.\n" % \
              (self.name)
        player.numActions += 1
        player.numBuys += 1
        player.spendBonus += 1
        player.drawCards( 1 )


class Mine( Card ):
    def __init__( self ):
        Card.__init__( self, "mine", "(mi)ne", "mi",
                       5, 0, True, 0,
                       "Trash a copper, gain a silver in hand. OR " \
                       "Trash a silver, gain a gold in hand." )

    def play( self, player, players, turn, supply ):
        print "Playing %s.\n" % self.name

        # dont get stuck in endless input loop if player has no valid
        # coins to trash
        trashList = ["copper", "silver"]

        validAction = False
        for cardName in trashList:
            if player.hand.contains( supply.cardShortcuts[cardName] ):
                validAction = True

        if not validAction:
            print "You have no copper or silver in hand."
            raise IllegalAction()
            
        while True:
            cardName = raw_input("Select a card to trash (q to quit)> ")

            # One probably loses this action if they quit, but
            # at least the game isn't dead in this case.
            if cardName is "q":
                raise CanceledAction()

            try:
                trashedCard = supply.cardShortcuts[cardName]
            except KeyError:
                print "Please choose either copper or silver." % cardName
                continue

            if (trashedCard.name in trashList and
                player.hand.contains( trashedCard )):

                player.hand.remove( trashedCard )

                if trashedCard.name == "copper":

                    # TO DO: deck could be empty
                    mineCard = supply.decks["silver"].deal()
                    player.hand.add( mineCard )
                    print "%s mined %s to %s and gains it in hand." % \
                          (player.name,
                           trashedCard.displayName,
                           mineCard.displayName)

                if trashedCard.name == "silver":

                    # TO DO: deck could be empty                    
                    mineCard = supply.decks["gold"].deal()
                    player.hand.add( mineCard )
                    print "%s mined %s to %s and gains it in hand." % \
                          (player.name,
                           trashedCard.displayName,
                           mineCard.displayName)
                break
            
            else:
                print "The mine only operates on copper or silver in hand."


class Moneylender( Card ):
    def __init__( self ):
        Card.__init__( self, "moneylender", "(mon)eylender", "mon",
                       4, 0, True, 0,
                       "Trash a copper in hand. If you do, +3 spend.")    

    def play( self, player, players, turn, supply ):
        print "Playing %s.\n" % self.name

        copperCard = supply.cardShortcuts["copper"]
        if not player.hand.contains( copperCard ):
            print "\nYou have no copper in hand."
            raise IllegalAction()

        print "%s trashed %s." % (player.name, copperCard)
        player.hand.remove( copperCard )
        player.spendBonus += 3


class Chancellor( Card ):
    def __init__( self ):
        Card.__init__( self, "chancellor", "(ch)ancellor", "ch",
                       3, 0, True, 0,
                       "+2 spend.  You may immediately put your " \
                       "deck into your discard pile.")

    def play( self, player, players, turn, supply ):
        print "Playing %s, +2 spend.\n" % self.name

        while True:
            if len( player.deck ) == 1:
                prompt = "Discard the remainder of your deck? \
                (%d card remains) (y/n) >" % len( player.deck )
            else:
                prompt = "Discard the remainder of your deck? \
                (%d cards remain) (y/n) >" % len( player.deck )
                
            choice = raw_input( prompt )
            if choice in ["y", "n"]:
                break

        if choice == "y":
            player.discard.extend( player.deck )
            player.deck = Deck()
            print "Deck discarded."
        else:
            print "Keeping your deck in play."

        player.spendBonus += 2


class Festival( Card ):
    def __init__( self ):
        Card.__init__( self, "festival", "(f)estival", "f",
                       5, 0, True, 0,
                       "+2 actions.  +1 buy.  +2 spend.")

    def play( self, player, players, turn, supply ):
        print "Playing %s, +2 actions, +1 buy, +2 spend.\n" % self.name
        player.numActions += 2      
        player.numBuys += 1
        player.spendBonus += 2


class Laboratory( Card ):
    def __init__( self ):
        Card.__init__( self, "laboratory", "(l)aboratory", "l",
                       5, 0, True, 0,
                       "+2 cards.  +1 action.")

    def play( self, player, players, turn, supply ):
        print "Playing %s, +1 action, +2 cards.\n" % self.name        
        player.numActions += 1
        player.drawCards( 2 )


class Feast( Card ):
    def __init__( self ):
        Card.__init__( self, "feast", "(fe)ast", "fe",
                       4, 0, True, 0,
                       "Trash this card. Gain a card costing up to 5 coins.")

    def play( self, player, players, turn, supply ):
        print "Playing %s.\n" % self.name        
        if not buyCard( supply, player, 5, True ):
            raise CanceledAction()


class Adventurer( Card ):
    def __init__( self ):
        Card.__init__( self, "adventurer", "(a)dventurer", "a",
                       6, 0, True, 0,
                       "Reveal cards from your deck until you reveal " \
                       "2 treasure cards. Put those treasure cards into " \
                       "your hand and discard the other revealed cards." )

    def play( self, player, players, turn, supply ):
        print "Playing %s.\n" % self.name

        # if the player somehow doesn't have 2 treasure cards
        # in their deck (unlikely), this is an endless loop, oops
        treasureCards = 0
        
        while treasureCards < 2:

            try:
                newCard = player.deck.deal()
            except ValueError:
                player.deck.extend( player.discard )
                player.deck.shuffle()
                print ">< %s shuffles %d cards." % \
                      (player.name, len( player.deck )) 
                player.discard = Deck()
                newCard = player.deck.deal()
            
            if newCard.value:
                print "%s draws % and takes it in hand." % \
                      (player.name, newCard.displayName )
                player.hand.add( newCard )
                treasureCards += 1
            else:
                print "%s draws % and discards it." % \
                      (player.name, newCard.displayName )
                player.discard.add( newCard )


class Bureaucrat( Card ):
    def __init__( self ):
        Card.__init__( self, "bureaucrat", "(b)ureaucrat", "b",
                       4, 0, True, 0,
                       "Gain a silver on top of your deck. Each other " \
                       "player reveals a victory card from their hand " \
                       "and puts it on top of their deck." )

    def play( self, player, players, turn, supply ):
        print "Playing %s. Gain a %s on top of your deck.\n" % \
              (self.name, supply.cardShortcuts[ "silver" ].displayName)
        player.deck.push( supply.cardShortcuts[ "silver" ] )
        turn.attacksInPlay.append( Attack( self.name, player.name ))


class Witch( Card ):
    def __init__( self ):
        Card.__init__( self, "witch", "(wi)tch", "wi",
                       5, 0, True, 0,
                       "+2 cards.  Each other player takes a curse card." )

    def play( self, player, players, turn, supply ):
        print "Playing witch,  +2 cards."
        player.drawCards( 2 )
        turn.attacksInPlay.append( Attack( self.name, player.name ))


class Spy( Card ):
    def __init__( self ):
        Card.__init__( self, "spy", "(sp)y", "sp",
                       4, 0, True, 0,
                       "+1 card. +1 action.  Each player (including you) " \
                       "reveals the top card from his deck and either " \
                       "discards it or puts it back, your choice." )

    def play( self, player, players, turn, supply ):
        print "Playing Spy, +1 card, +1 action."

        player.drawCards( 1 )
        player.numActions += 1

        # I hate to do this in the card itself, because now it requires
        # passing in all the other players.  However, it will be faster/
        # easier to resolve it right now.
        for other in players:
            
            isPlayer = False
            if other.name == player.name:
                isPlayer = True
        
            # first check to see if other has a moat in hand
            if not isPlayer:
                if other.hand.contains( supply.cardShortcuts["moat"] ):
                    print "\n%s deflects the attack with a moat." % \
                          (other.name)
                    continue
            
            try:
                topCard = other.deck.deal()
            except ValueError:
                other.deck.extend( other.discard )
                other.deck.shuffle()
                print ">< %s shuffles %d cards." % \
                      (other.name, len( other.deck ))                 
                other.discard = Deck()
                topCard = other.deck.deal()


            if isPlayer:
                print "\n%s, your next card is %s." % \
                      (other.name, topCard.displayName)
            else:
                print "\nThe top card on %s's deck is %s" % \
                      (other.name, topCard.displayName)

            while True:
                fate = raw_input( "(d)iscard it or (p)ut it back? >" )
                if fate in ["d", "p"]:
                    break

            if fate == "d":
                print "\nDiscarded %s's %s" % \
                      (other.name, topCard.displayName)
                other.discard.add( topCard )
            else:
                print "\n%s's %s goes back." % \
                      (other.name, topCard.displayName)
                other.deck.push( topCard )


class Thief( Card ):
    def __init__( self ):
        Card.__init__( self, "thief", "(t)hief", "t",
                       4, 0, True, 0,
                       "Each player reveals the top 2 cards from his " \
                       "deck. If they reveal any treasure cards, they " \
                       "trash 1 that you choose. You may gain any or all " \
                       "of these trashed cards. They discard the other " \
                       "revealed cards." )

    def play( self, player, players, turn, supply ):
        print "Playing %s." % self.name

        # this is a fucking nightmare
        localTrash = []
        for other in players:

            if other.name == player.name:
                continue

            # first check to see if other has a moat in hand
            if other.hand.contains( supply.cardShortcuts["moat"] ):
                print "\n%s deflects the attack with a moat." % other.name
                continue

            treasure = 0 # using len( reveal ) would be safer
            reveal = []
            for i in range(2):
                try:
                    topCard = other.deck.deal()
                except ValueError:
                    other.deck.extend( other.discard )
                    other.deck.shuffle()
                    print ">< %s shuffles %d cards." % \
                          (other.name, len( other.deck ))
                    other.discard = Deck()
                    topCard = other.deck.deal()

                if topCard.value:
                    treasure += 1
                reveal.append( topCard )

            print "\n%s reveals %s and %s." % \
                  (other.name,
                   reveal[0].displayName,
                   reveal[1].displayName)

            if treasure == 1:                
                if reveal[0].value:
                    treasureCard = reveal[0]
                    otherCard = reveal[1]
                else:
                    treasureCard = reveal[1]
                    otherCard = reveal[0]

                prompt = "%s, trash the %s? (y/n)> " % \
                         (player.name, treasureCard.displayName)
                while True:
                    trashIt = raw_input( prompt )
                    if trashIt in ["y", "n"]:
                        break
                    
                if trashIt == "y":
                    print "The %s is trashed." % treasureCard.displayName
                    localTrash.append( treasureCard )
                else:
                    print "The %s is discarded" % treasureCard.displayName
                    other.discard.add( treasureCard )
                print "The %s gets discarded." % otherCard.displayName
                other.discard.add( otherCard )
                    
            elif treasure == 2:
                while True:
                    prompt = "%s, choose one to trash " \
                             "(q trashes nothing)> " % player.name
                    whichOne = raw_input( prompt )

                    if whichOne == "q":
                        break

                    # trash nothing, discard both
                    if whichOne == "":
                        for card in reveal:
                            print "%s discarded." % \
                                  card.displayName
                            other.discard.add( card )
                        break

                    # else, argh, get the shortcut
                    try:
                        theCard = supply.cardShortcuts[whichOne]
                    except KeyError:
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
                    # now resolve the choice
                    # this code is dumb
                    if reveal[0] == theCard:
                        print "The %s is trashed." % \
                              reveal[0].displayName
                        print "The %s is discarded." % \
                              reveal[1].displayName
                        localTrash.append( reveal[0] )
                        other.discard.add( reveal[1] )
                    else:
                        print "The %s is trashed." % \
                              reveal[1].displayName
                        print "The %s is discarded." % \
                              reveal[0].displayName
                        localTrash.append( reveal[1] )
                        other.discard.add( reveal[0] )
                    break
                
            else:

                # In this case, the cards weren't actually revealed
                # and they just go back to the other player's hand
                for card in reveal:
                    other.hand.add( card )
                continue

        # now rifle through the trash you thief!
        if len( localTrash ):
            print "\n%s, you may steal any of the trashed cards.\n" % \
                  player.name
            
            for card in localTrash:
                prompt = "(t)ake or (l)eave a %s?> " % card.displayName
                while True:
                    stealIt = raw_input( prompt )
                    if stealIt in ["t", "l"]:
                        break
                if stealIt == "t":
                    print "%s gains a %s!" % \
                          (player.name, card.displayName)
                    player.discard.add( card )
                else:
                    print "%s tosses the %s." % \
                          (player.name, card.displayName)
        else:
            print "No one had treasure to steal."


class Library( Card ):
    def __init__( self ):
        Card.__init__( self, "library", "(li)brary", "li",
                       5, 0, True, 0,
                       "Draw until you have 7 cards in hand. You may " \
                       "discard any actions cards as you draw them." )

    def play( self, player, players, turn, supply ):
        print "Playing %s." % self.name
        
        while len( player.hand ) < 7:
            try:
                topCard = player.deck.deal()
            except ValueError:
                player.deck.extend( player.discard )
                player.deck.shuffle()
                print ">< %s shuffles %d cards." % \
                      (player.name, len( player.deck ))                 
                player.discard = Deck()
                topCard = player.deck.deal()

            if topCard.action:
                print "\n%s draws %s." % (player.name, topCard)                
                while True:
                    keepIt = raw_input( "(d)iscard or (k)eep?> " )
                    if keepIt in ["d", "k"]:
                        break

                if keepIt == "d":
                    print "%s discards the %s." % (player.name, topCard)
                    player.discard.add( topCard )
                else:
                    print "%s keeps the %s." % (player.name, topCard)
                    player.hand.add( topCard )

            else:
                print "\n%s draws %s and takes it in hand." % \
                      (player.name, topCard)
                player.hand.add( topCard )


class CouncilRoom( Card ):
    def __init__( self ):
        Card.__init__( self, "council room", "(co)uncil room",
                       "co", 5, 0, True, 0,
                       "+4 cards.  +1 buy.  Each other player draws a card." )

    def play( self, player, players, turn, supply ):
        print "Playing %s, +4 cards, +1 buy.\n" % self.name
        player.drawCards( 4 )
        player.numBuys += 1
        turn.attacksInPlay.append( Attack( self.name, player.name ))


class Chapel( Card ):
    def __init__( self ):
        Card.__init__( self, "chapel", "(cha)pel", "cha",
                       2, 0, True, 0,
                       "Trash up to 4 cards." )

    def play( self, player, players, turn, supply ):
        print "Playing %s.\n" % self.name
        cardsTrashed = 0

        while True:
            if cardsTrashed >= 4:
                break
            
            choice = raw_input("Select a card to trash (q to quit)> ")
            if choice == "q":
                break
            
            try:
                trashedCard = supply.cardShortcuts[choice]
            except KeyError:
                print "Huh?"
                continue
            
            if player.hand.contains( trashedCard ):
                print "Trashed %s" % trashedCard.displayName
                cardsTrashed += 1
                player.hand.remove( trashedCard )
            else:
                print "You don't have that card in hand."

        if not cardsTrashed:
            raise CanceledAction()


class ThroneRoom( Card ):
    def __init__( self ):
        Card.__init__( self, "throne room", "(th)rone room", "th",
                       4, 0, True, 0,
                       "Choose an action card in your hand.  Play it twice." )

    def play( self, player, players, turn, supply ):
        print "Throne Room, play your next action card twice.\n"
        turn.numThroneRooms += 1
        player.numActions += 1
        turn.chainingThroneRooms = True


class Curse( Card ):
    def __init__( self ):
        Card.__init__( self, "curse", "\033[35m(cu)rse\033[39m", "cu",
                       0, 0, False, -1,
                       "-1 victory point.")
        

class Estate( Card ):
    def __init__( self ):
        Card.__init__( self, "estate", "\033[32m(e)state\033[39m", "e",
                       2, 0, False, 1,
                       "+1 victory point.")


class Gardens( Card ):
    def __init__( self ):
        Card.__init__( self, "gardens", "\033[32m(ga)rdens\033[39m", "ga",
                       4, 0, False, 1,
                       "1 victory point per 10 cards in your deck.")    
    

class Duchy( Card ):
    def __init__( self ):
        Card.__init__( self, "duchy", "\033[32m(d)uchy\033[39m", "d",
                       5, 0, False, 3,
                       "3 victory points.")


class Province( Card ):
    def __init__( self ):
        Card.__init__( self, "province", "\033[32m(p)rovince\033[39m", "p",
                       8, 0, False, 6,
                       "6 victory points.")


class Copper( Card ):
    def __init__( self ):
        Card.__init__( self, "copper", "\033[33m(c)opper\033[39m", "c",
                       0, 1, False, 0,
                       "1 coin." )


class Silver( Card ):
    def __init__( self ):
        Card.__init__( self, "silver", "\033[33m(s)ilver\033[39m", "s",
                       3, 2, False, 0,
                       "2 coins." )


class Gold( Card ):
    def __init__( self ):
        Card.__init__( self, "gold", "\033[33m(g)old\033[39m", "g",
                       6, 3, False, 0,
                       "3 coins." )


class CardFactory():
    def __init__( self ):
        self.__cards = {"estate": Estate(),
                        "duchy": Duchy(),
                        "province": Province(),
                        "gardens": Gardens(),
                        "gold": Gold(),
                        "silver": Silver(),
                        "copper": Copper(),
                        "curse": Curse(),
                        "cellar": Cellar(),
                        "chapel": Chapel(),
                        "moat": Moat(),
                        "chancellor": Chancellor(),
                        "village": Village(),
                        "woodcutter": Woodcutter(),
                        "workshop": Workshop(),
                        "bureaucrat": Bureaucrat(),
                        "feast": Feast(),
                        "militia": Militia(),
                        "moneylender": Moneylender(),
                        "remodel": Remodel(),
                        "smithy": Smithy(),
                        "spy": Spy(),
                        "thief": Thief(),
                        "throne room": ThroneRoom(),
                        "gardens": Gardens(),
                        "council room": CouncilRoom(),
                        "festival": Festival(),
                        "laboratory": Laboratory(),
                        "library": Library(),
                        "market": Market(),
                        "mine": Mine(),
                        "witch": Witch(),
                        "adventurer": Adventurer() 
                        }

    def create( self, cardName ):
        card = None
        try:
            card = self.__cards[cardName]
        except KeyError:
            print "CardFactory.create( cardName ) got unknown card name."

        return card
        

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

    def drawCards( self, numCards, silent = False ):

        for i in range( numCards ):
            try:
                card = self.deck.deal()
            except ValueError:
                self.deck.extend( self.discard )
                self.deck.shuffle()
                print ">< %s shuffles %d cards." % \
                      (self.name, len( self.deck ))
                self.discard = Deck()
                card = self.deck.deal()
                
            self.hand.add( card )
            if not silent:
                print "%s draws %s" % (self.name, card.displayName)


class TurnState():
    def __init__( self, numPlayers ):
        self.attacksInPlay = []
        self.numPlayers = numPlayers
        self.numThroneRooms = 0  # num consecutive throne rooms in play
        self.chainingThroneRooms = False


class CardSupply():
    def __init__( self, numPlayers, cardFactory ):
        self.__numPlayers = numPlayers
        self.__factory = cardFactory

        # start with only the cards that appear in every game
        self.decks = {"estate": Deck(),
                      "duchy": Deck(),
                      "province": Deck(),
                      "copper": Deck(),
                      "silver": Deck(),
                      "gold": Deck()}

        self.cardShortcuts = {}
        self.__setup()

    def __setup( self ):

        if self.__numPlayers <= 2:
            numVpCards = 8
        else:
            numVpCards = 12

        # set up variable number of VP cards
        for i in range(numVpCards):
            self.decks["estate"].add( self.__factory.create("estate") )
            self.decks["duchy"].add( self.__factory.create("duchy") )
            self.decks["province"].add( self.__factory.create("province") )

        for i in range(60):
            self.decks["copper"].add( self.__factory.create("copper") )

        for i in range(40):
            self.decks["silver"].add( self.__factory.create("silver") )

        for i in range(30):
            self.decks["gold"].add( self.__factory.create("gold") )


    # if this method is not called independently at setup time
    # there will be no kingdom cards for the game to use!
    # cardList is just a list of card names (strings)
    def setKingdomCards( self, cardList ):

        if len(cardList) != 10:
            print "The chosen deck configuration must contain 10 cards."
            print "This is most likely a problem with " \
                  "the decks layout file."
            raise SystemExit()

        for cardName in cardList:
            try:
                card = self.__factory.create(cardName)
            except:
                print "Got unknown card name %s." % cardName
                print "This is most likely a problem with " \
                      "the decks layout file."
                raise SystemExit()

            # There are always 10 of each action card
            self.decks[cardName] = Deck()
            for i in range(10):
                self.decks[cardName].add( card )

        # Auto-magically add the Curse card if we require it.
        # (In the base set, only the Witch card requires Curse.)
        if "witch" in cardList:
            self.decks["curse"] = Deck()
            for i in range(30):
                self.decks["curse"].add( self.__factory.create("curse") )

        self.__setupCardShortcuts()

    # These will now be specific to the configured decks for the game
    # rather than contain all known cards/shortcuts
    def __setupCardShortcuts( self ):

        # Not sure I like these values as card instances.
        for deck in self.decks.values():
            card = deck.peek()
            self.cardShortcuts[card.name] = card
            self.cardShortcuts[card.shortcut] = card


# Useful debugging function
def dumpDecks( player ):
    print "\nDEBUG: %s's current deck state" % player.name
    print "In hand: ", player.hand
    print "In play: ", player.inPlay
    print "In deck: ", player.deck
    print "In discard: ", player.discard

# card help looks better now, but the code is major suck
def cardHelp( decks ):
    print

    for i in range( 9 ):
        vpCards = []
        for deck in decks.values():

            if deck.empty():
                continue

            card = deck.peek()

            if card.vp == i and card.vp:
                vpCards.append( card )
                
        # hack for gardens card
        for card in vpCards:
            if card.name != 'gardens':
                print "%s (%d VP) " % (card.displayName, card.vp),

    print

    # do all this again just to show gardens VP
    # correctly if it's in the game, ack!
    for deck in decks.values():
        if deck.empty():
            continue

        card = deck.peek()
        if card.name == 'gardens':
            print "%s (%d VP per 10 cards in deck)" % \
                  (card.displayName, card.vp)
        
    print

    for i in range( 9 ):

        cardChoices = []
        for deck in decks.values():
            if deck.empty():
                continue

            card = deck.peek()

            if card.cost == i and card.action:
                cardChoices.append( card )
                
        for thisCard in cardChoices:
            print "%s: %s" % (thisCard.displayName, thisCard.helpText)

# max spend is the upper limit of cards to display
# and determines which cards are available for purchase on this buy
# return whether or not someone bought a card
def buyCard( supply, player, maxSpend, freeCard = False ):
    print "\nLet's go shopping!\n"

    if not freeCard:
        if ( player.spendBonus + player.hand.getCoin() ) == 1:
            if player.numBuys == 1:
                print "You have %d coin and %d buy remaining.\n" % \
                      (player.spendBonus + player.hand.getCoin(),
                       player.numBuys )
            else:
                print "You have %d coin and %d buys remaining.\n" % \
                      (player.spendBonus + player.hand.getCoin(),
                       player.numBuys )
        else:
            if player.numBuys == 1:
                print "You have %d coins and %d buy remaining.\n" % \
                      (player.spendBonus + player.hand.getCoin(),
                       player.numBuys)
            else:
                print "You have %d coins and %d buys remaining.\n" % \
                      (player.spendBonus + player.hand.getCoin(),
                       player.numBuys)
    else:
        print "Choose any card shown below."
        
    for i in range( maxSpend + 1 ):

        cardChoices = []
        for deck in supply.decks.values():
            if deck.empty():
                continue

            card = deck.peek()

            if card.cost == i and card.name != "curse":
                cardChoices.append( card.displayName )
                
        if len( cardChoices ) > 0:
            if i == 1:
                print " %d coin : " % i,
            else:
                print " %d coins: " % i,
            for thisCard in cardChoices:
                print "%s " % thisCard,
            print

    while True:
        cardName = raw_input("\nName of card to buy (q to quit)> ")

        if cardName == "q":
            break
        try:
            card = supply.cardShortcuts[cardName]
            break
        except KeyError:
            print "\nThat card name is not valid."

    if cardName == "q":
        return False

    try:
        if supply.decks[card.name].empty():
            print "That deck is empty."
            return False
    except KeyError:
        print "That card is not available in this game."
        return False

    # get the card
    card = supply.decks[card.name].deal()

    # any maxSpend restriction for this "buy"
    if card.cost > maxSpend:
        print "That card is not available for this transaction."
        return False

    # enough coin or free card?
    if (( player.spendBonus + player.hand.getCoin() ) >= card.cost or
        freeCard ):
            
        player.discard.add( card )
        print "\n%s bought a %s.\n" % (player.name, card.displayName)

        # if they get this "buy" due to another card (ie. remodel)
        # then it doesn't cost them one of their buys or end
        # their actions this turn
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

        for moneyCard in player.hand:
            if (moneyCard.name in ["gold", "silver", "copper"] and
                moneyCard.value <= totalToDeduct):
                totalToDeduct -= moneyCard.value
                cardsToRemove.append( moneyCard )

        # discard coin
        for spentCard in cardsToRemove:
            player.hand.remove( spentCard )
            player.discard.add( spentCard )

        return True

    else:
        print "You don't have enough for that."        
        supply.decks[card.name].add( card )

    return False

def handleAttacks( turn, player, supply ):

        # get rid of finished attacks
        finishedAttacks = []
        for attack in turn.attacksInPlay:
            if attack.playerName == player.name:
                finishedAttacks.append( attack )

        for attack in finishedAttacks:
            turn.attacksInPlay.remove( attack )

        for attack in turn.attacksInPlay:
            if attack.attackName == "militia":
                print "\n%s's militia card is in play." % attack.playerName

                if player.hand.contains( supply.cardShortcuts["moat"] ):
                    print "You deflect the attack with the moat.\n"

                elif len( player.hand ) <= 3:
                    print "You have 3 or less cards in hand already."

                else:
                    print "You must discard down to 3 cards.\n"

                    while True:
                        numCardsInHand = len( player.hand )
                        print "\nHand: %s" % player.hand

                        if numCardsInHand == 3:
                            break

                        cardName = raw_input("Card name to discard> ")
                        
                        try:
                            discardCard = supply.cardShortcuts[cardName]
                        except KeyError:
                            print "Huh?"
                            continue

                        if player.hand.contains( discardCard ):
                            player.hand.remove( discardCard )
                            player.discard.add( discardCard )
                        else:
                            print "Try discarding something from your hand!"

            if attack.attackName == "bureaucrat":
                print "%s's bureaucrat card is in play." % attack.playerName

                if player.hand.contains( supply.cardShortcuts["moat"] ):
                    print "You deflect the attack with the moat.\n"
                else:
                    cardToRemove = None
                    for card in player.hand:
                        if card.vp:
                            cardToRemove = card
                            break

                    if cardToRemove:
                        print "Putting %s from your hand " \
                              "on top of your deck.\n" % \
                              cardToRemove.displayName
                        player.hand.remove( cardToRemove )
                        player.deck.push( cardToRemove )
                    else:
                        print "You have no VP cards in hand.\n"
                        
                    print "Hand: %s\n" % (player.hand)

            if attack.attackName == "witch":
                print "%s's witch is in play!" % attack.playerName
                if player.hand.contains( supply.cardShortcuts["moat"] ):
                    print "You deflect the attack with the moat.\n"
                else:
                    newCurse = None
                    try:
                        newCurse = supply.decks["curse"].deal()
                    except ValueError:
                        print "No curse cards remaining."
                    if newCurse:
                        print "You take a curse.\n"
                        player.discard.add( newCurse )

            if attack.attackName == "council room":
                print "%s's council room gives you another card." % \
                      attack.playerName
                player.drawCards( 1 )
                print "\nHand: %s" % player.hand


def selectKingdomCards():

    DECK_LAYOUTS_FILE = "layouts.txt"
    layoutNames = {}
    deckLayouts = {}

    try:
        with open(DECK_LAYOUTS_FILE, "r") as f:

            layout = f.readline()
            cards = f.readline()

            while layout and cards:
                ( shortcut, layout ) = layout.split(":")
                layoutNames[shortcut] = layout.strip()

                cards = cards.split(",")
                cards = [ name.strip() for name in cards ]
                deckLayouts[shortcut] = cards
                
                layout = f.readline()
                cards = f.readline()

    except IOError:
        # The deck layout file is trivial to construct
        # It is a text file with 2 lines per layout where the
        # format is as follows:
        # layout shortcut: layout name
        # card1, card2, card3, ..., card10
        # Each layout must contain 10 action cards and do not include
        # VP cards, coins, or curse cards
        print "The file containing the deck layouts (%s) " \
              "cannot be loaded." % DECK_LAYOUTS_FILE
        
    # Let's just force the random layouts for now
    # since this option cannot be configured in the decks.txt
    # file. This will clobber any set using the shortcut "r"
    layoutNames["r"] = "random cards, require moat"

    while True:
        print "\nChoose a deck layout to play."
        print "Create your own layouts by adding them to %s\n" % \
              DECK_LAYOUTS_FILE

        for ( shortcut, layoutName ) in layoutNames.items():
            print "(%s) %s" % ( shortcut, layoutName )

        # A bit of a hack, but generate a new random set
        # here each time.
        deckLayouts["r"] = ["moat"]
        deckLayouts["r"].extend( random.sample(
                [ "cellar", "woodcutter", "workshop", "smithy", 
                  "remodel", "market", "mine", "militia", 
                  "village", "moneylender", "chancellor", 
                  "thief", "witch", "festival", "laboratory", 
                  "feast", "adventurer", "bureaucrat", "spy", 
                  "library", "council room", "throne room",
                  "gardens", "chapel" ], 9 ))        

        while True:
            choice = raw_input( "\nCard set> " )
            if choice in layoutNames:
                break
            else:
                print "Please choose a valid card set."
        
        cardSet = deckLayouts[choice]

        # Display the card choices.
        # Too bad these can't currently use colorama :(
        cardNum = 0
        for card in cardSet:
            print "%s " % ( card ),
            cardNum += 1
            if cardNum == 5:
                print "\n",
                
        choice = raw_input( "\n\nUse this set? (y/n)>" )
        if choice == 'y':
            break

    return cardSet


def showTitleFromFile():

    title = ""
    try:
        with open("title.txt", "r") as f:
            title = f.read()
    except IOError:
        # if the title file is missing, who cares really?
        pass
    print title

                                    
def main():

    if colorama:
        colorama.init()

    showTitleFromFile()

    random.seed(None)

    # create the players
    while True:
        numPlayers = raw_input("\nNumber of players (1-4)> ")
        try:
            numPlayers = int(numPlayers)
        except ValueError:
            print "\nPlease enter a valid number."
            continue

        if numPlayers > 0 and numPlayers < 5:
            break

    # set up the game decks
    cardFactory = CardFactory()
    supply = CardSupply( numPlayers, cardFactory )

    # choose kingdom cards to use
    cardSet = selectKingdomCards() 
    
    supply.setKingdomCards( cardSet )

    players = []
    for i in range(numPlayers):
        print "\nPlayer ", i
        name = raw_input("Enter your name> ")
        players.append( Player( name ) )

    # set up the player's deck
    print "\n"
    for i in range(numPlayers):
        for j in range(7):
            players[i].deck.add( Copper() )
        for j in range(3):
            players[i].deck.add( Estate() )

        players[i].deck.shuffle()
        print ">< %s shuffles %d cards." % (players[i].name,
                                         len( players[i].deck))

        # deal me a new one partna
        players[i].drawCards( 5, silent = True )

    isNewHand = True
    currentPlayerNumber = 0

    # now that there are actual card instances with play() methods
    # I need a magical container to pass in to contain all the
    # turn state that needs to be acted upon
    turn = TurnState( numPlayers )

    while True:

        if currentPlayerNumber == turn.numPlayers:
            currentPlayerNumber = 0
        
        player = players[currentPlayerNumber]

        gameOver = False
        if supply.decks[ "province" ].empty():
            print "The province deck is empty."
            gameOver = True

        # look at kingdom card decks
        numEmptyDecks = 0
        emptyDeckNames = []
        for ( deckName, deck ) in supply.decks.items():
            if deckName in ["estate", "duchy", "province",
                            "copper", "silver", "gold", "curse"]:
                continue
            if deck.empty():
                numEmptyDecks += 1
                emptyDeckNames.append( deckName )

        if numEmptyDecks:
            print "These kingdom card decks are now empty: ", emptyDeckNames

        if numEmptyDecks >= 3:
            gameOver = True

        if gameOver:
            for i in range( turn.numPlayers ):
                # combine all the decks
                players[i].deck.extend( players[i].inPlay )
                players[i].deck.extend( players[i].hand )
                players[i].deck.extend( players[i].discard )
                
                # lets count all the cards in each players hand
                counts = {}
                for card in players[i].deck:
                    if counts.has_key( card.name ):
                        counts[ card.name ] += 1
                    else:
                        counts[ card.name ] = 1

                # for now, stop dumping out the final
                # decks
                #print "Player %s" % ( players[i].name)
                #for (cardName, count) in counts.items():
                #    print "     %s %d" % ( cardName, count )
                    
            print "********** GAME OVER **********"
            for i in range( turn.numPlayers ):            
                print "Player: %d *%s* VP: %d" % \
                      (i + 1, players[i].name, players[i].deck.getVP())
            print "*******************************"
            break

        taskList = ["+", "x", "h", "c"]

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

        # next action same hand (or new hand)
        # always message whose turn it is first
        print "\n%s, your turn.  (%d/%d)\n" % \
              (player.name, player.deck.getNumShuffles(), player.numHands)
        
        print "Hand: %s" % (player.hand)
        
        if player.spendBonus + player.hand.getCoin() == 1:
            print "Actions: %d  Buys: %d  Spend: %d coin\n" % \
                  (player.numActions,
                   player.numBuys,
                   player.spendBonus + player.hand.getCoin())
        else:
            print "Actions: %d  Buys: %d  Spend: %d coins\n" % \
                  (player.numActions,
                   player.numBuys,
                   player.spendBonus + player.hand.getCoin())            

        # deal with attack cards in play
        if isNewHand:
            isNewHand = False
            handleAttacks( turn, player, supply )
            
        # end of attacks section
                        
        # show available menu options to player
        if player.numActions > 0:
            for card in player.hand:
                if card.action:
                    taskList += "a"
                    break

        print
            
        if "a" in taskList:
            print "(a) action"

        if ((player.hand.getCoin() + player.spendBonus) > 0  and
            player.numBuys > 0):
            print "(b) buy card (into discard pile)"
            taskList += "b"

        print "(c) count cards"
        print "(h) card help"
        print "(x) done with turn"
                
        while True:
            task = raw_input("> ")
            if task in taskList:
                break
            else:
                print "Huh?"

        # buy cards        
        if task == "b":
            buyCard( supply, player, 8 )
        
        if task == "+":
            dumpDecks( player )

        # *******************************************************
        # play action
        
        if task == "a":
            while True:
                card = raw_input("\nCard to play> ")
                # first see if they entered a shortcut
                try:
                    card = supply.cardShortcuts[card]
                    break
                except KeyError:
                    print "Huh?"
                    continue
                 
            if not player.hand.contains( card ):
                print "You don't have that card in hand."
            else:

                # get the card from hand so it can't be used
                # again during this turn
                cardInPlay = card

                if not cardInPlay.action:
                    print "That is not an action card."

                else:

                    # toggle off the throne room chain
                    if cardInPlay != ThroneRoom():
                        turn.chainingThroneRooms = False

                    # take the card from the hand
                    player.hand.remove( cardInPlay )

                    # immediately put the card into the inPlay deck
                    player.inPlay.add( cardInPlay )

                    # resolve the card
                    try:
                        cardInPlay.play( player, players, turn, supply )
                        player.numActions -= 1
                    except Error:
                        pass
                        
                        # put everything back
                        player.inPlay.remove( cardInPlay )
                        player.hand.add( cardInPlay )

                    # remove this option from the menu
                    if player.numActions == 0:
                        if "a" in taskList:
                            taskList.remove( "a" )

                    # resolve double play for Throne Room
                    # we toggle the bool off when the chain of
                    # throne rooms is finished being played
                    if (not turn.chainingThroneRooms and
                        turn.numThroneRooms > 0):
                        turn.numThroneRooms -= 1

                        # do it again
                        # second play shouldn't decrement numActions
                        print "\nThrone Room active, re-playing %s" % \
                              cardInPlay.displayName

                        try:
                            cardInPlay.play( player, players, turn, supply )
                        except Error:
                            pass

        # *******************************************************
            
        if task == "x":
            # Feast gets trashed after succesfully played
            try:
                while player.inPlay.contains( supply.cardShortcuts["feast"] ):
                    player.inPlay.remove( supply.cardShortcuts["feast"] )
            except KeyError:
                pass
                
            player.discard.extend( player.inPlay )
            player.inPlay = Deck()
            turn.throneRoom = 0
            isNewHand = True


        if task == "h":
            cardHelp( supply.decks )

        if task == "c":
            for( deckName, deck ) in supply.decks.items():
                if deckName in ["copper", "silver", "gold"]:
                    continue
                print "%s %d" % (deckName, len( deck ))

        # put cards in hand into discard pile
        if isNewHand:
            player.discard.extend( player.hand )
            player.hand = Deck()

            # deal me another
            player.drawCards( 5, silent = True )

            # next players turn now
            currentPlayerNumber += 1


if __name__ == "__main__":
    main()
