import random

def main():
    endScore = 101
    numPlayers = 3

    players = []
    for num in range(numPlayers):
        players.append(Simpleton())
        
    deck = Deck()

    end = False
    rounds = 0
    while not end:
        print("Round start")
        rounds += 1
        ccRound = CCRound(deck, players)
        ccRound.dealHands()

        cut = False
        while not cut:
            cut = ccRound.executeTurn()
        end = ccRound.resolution()

        player = players[0]
        players.remove(player)
        players.append(player)

        scoreMessage = "Round end; Scores: "
        numPlayer = 0
        for player in players:
            numPlayer += 1
            scoreMessage += "P" + str(numPlayer) + " " + str(player.sendScore()) + ", "
        print(scoreMessage)


    
class CCRound:
    def __init__(self, deck, players):
        self.handSize = 7
        self.deck = deck
        self.deck.setup()
        self.players = players
        self.numPlayers = len(self.players)
        self.turn = 0
        self.memories = []
        for player in players:
            self.memories.append(0)

    def dealHands(self):
        #alternately deals out seven cards to each player
        #also lays out one card for the game to begin
        toBeDealt = []
        for j in range(self.numPlayers):
            toBeDealt.append([])

        for i in range(self.handSize):
            for j in range(self.numPlayers):
                card = self.deck.dealCard()[0]
                toBeDealt[j].append(card)   

        j = 0
        for player in self.players:
            player.receiveHand(toBeDealt[j])
            j += 1

        card, useless = self.deck.dealCard()
        self.deck.discardCard(card)
        self.deck.checkTotalSize(self.numPlayers)

    def executeTurn(self):
        #decides whos turn it is
        #give players memories from other players
        #ask player whether they want to draw a new card or a discarded one
        #give player that card
        #ask player to discard a card
        #discard that card
        #ask player if they want to cut
        #update that player's memory
        #update turn

        self.deck.checkTotalSize(self.numPlayers)

        numPlayer = self.turn % self.numPlayers                 #decides whos turn it is
        currentPlayer = self.players[numPlayer]
        assembledMemories = self.assembleMemories(numPlayer)
        currentPlayer.receiveMemories(assembledMemories)        #gives player memories of other players

        deckOrDiscard = currentPlayer.sendDeckOrDiscard()       #aks player which card to draw
        if deckOrDiscard:
            card, wasReset = self.deck.dealCard()
            hidden = True
        else:
            card = self.dealDiscardCard()
            hidden = card
            wasReset = False
        currentPlayer.receiveCard(card)                         #give player the card they drew

        discardedCard, cut = currentPlayer.decide()             #ask player to discard a card, and cut
        self.deck.discardCard(discardedCard)                    #discard that dark

        self.deck.checkTotalSize(self.numPlayers)

        if cut:
            assert(currentPlayer.canCut()),"You cut illegaly noob"

        #create a memory of which card they drew (if visible)
        #which card they discarded, their score, and if they reset the deck
        memory = Memory(hidden, discardedCard, currentPlayer.sendScore(), wasReset)
        self.memories[numPlayer] = memory

        self.turn += 1                                          #update turn

        return cut

    #sends memories of the players in a list in the order that would go next
    #ex: if there are 4 players are player 3 wants to receive memories
    #then sendMemories will send a list containing, in order, 
    #the memories of the 4th player, then the 1st player, then the 2nd player
    def assembleMemories(self, numPlayer):
        memories = []
        for i in range(0,self.numPlayers-1):
            memories.append(self.memories[(numPlayer+1) % self.numPlayers])

        return memories

    #gets each player's hand
    #asks players how they will layed down their hand
    #calculate and accumulate their scores
    def resolution(self):
        hands = []
        for player in self.players:
            hands.append(player.sendHand())

        end = False
        scores = []
        for hand in hands:
            order = player.sendOrientedHand()
            score = hand.getValue(order)
            player.addScore(score)
            if player.sendScore() > 100:
                end = True
        
        return end

        

class Memory:
    #drew is either False or the card they picked up from the discard pile
    #discarded is the card they picked up
    def __init__(self, drew, discarded, score, wasReset):
        self.drew = drew
        self.discarded = discarded
        self.score = score
        self.wasReset = wasReset

    def getDrew(self):
        return self.drew

    def getDiscarded(self):
        return self.discarded

    def getScore(self):
        return self.score

    def wasReset(self):
        return wasReset



class Deck:
    def __init__(self):
        self.numSuits = 4
        self.numRanks = 13
        self.trueSize = 54
        self.deck = self.createDeck()
        self.size = len(self.deck)
        self.discard = []
        self.discardSize = len(self.discard)

    #sets deck up for another game
    def setup(self):
        for card in self.discard:
            self.deck.append(card)
        self.size = len(self.deck)
        self.shuffle()
        self.discard = []
        self.discardSize = len(self.discard)
        
    
    def createDeck(self):
        deck = []
        for i in range(self.numRanks):
            for j in range(self.numSuits):
                card = Card(i,j)
                deck.append(card)
        for i in range(2):
            deck.append(Card(13,4))

        return deck

    def shuffle(self):
        random.shuffle(self.deck)
    
    #returns the top card and a boolean informing player if
    #the deck had to be reset in order to have another card
    def dealCard(self):
        wasReset = False
        if self.isEmpty():
            self.setup()
            wasReset = True

        card = self.deck.pop()
        self.size -= 1

        return card, wasReset

    #puts card in discard
    def discardCard(self, card):
        self.discard.append(card)
        self.discardSize += 1

    #returns top of discard pile and removes it from discard
    def dealDiscardCard(self):
        self.discardSize -= 1
        return self.discard.pop()

    #shows top of discard pile
    def viewDiscardCard(self):
        return self.discard[len(self.discard)-1]

    def isEmpty(self):
        return self.size <= 0

    def checkTotalSize(self,numPlayers):
        cardsInPlay = numPlayers*7
        assert(self.trueSize == cardsInPlay+ self.size + self.discardSize),"Failure with size"
              
              

class Player:
    def __init__(self):
        self.score = 0
    #the game will give you a hand
    def receiveHand(self,cards):
        self.hand = Hand(cards)

    #the game requesting to see your hand
    def sendHand(self):
        return self.hand

    #send a list containing three lists such that
    #they describe how you want to lay down your cards
    #the first list contains the list of your groups
    #the second list contains list of your runs
    #the third list contains the cards that you weren't
    #able to fit into a group or a run
    def sendOrientedHand(self):
        return [[],[],[]]

    #receives memories of the players in a list in the order that would go next
    #ex: if there are 4 players and player 3 wants to receive memories
    #then they will receive a list containing, in order, 
    #the memories of the 4th player, then the 1st player, then the 2nd player
    def receiveMemories(self,memories):
        self.memories = memories

    #true for drawing card from deck and 
    #false for drawing deck from discard
    def sendDeckOrDiscard(self):
        return True

    #the game will send you a card
    def receiveCard(self, card):
        self.extraCard = card

    #decide which card to discard and decide whether to cut or not.
    #cut is a boolean
    def decide(self):
        return self.extraCard, cut

    #returns true if player is legally allowed to cut right now
    def canCut(self):
        bestValue = self.hand.bestOrder()[0].getValue()
        return bestValue <= 7

    def addScore(self, score):
        self.score += score

    def sendScore(self):
        return self.score

class Simpleton:
    def __init__(self):
        self.score = 0
    #the game will give you a hand
    def receiveHand(self,cards):
        self.hand = Hand(cards)

    #the game requesting to see your hand
    def sendHand(self):
        return self.hand

    #just lays it down in the self point minimizing way
    def sendOrientedHand(self):
        return self.hand.bestOrder()[0].getOrder()

    #receives memories of the players in a list in the order that would go next
    #ex: if there are 4 players and player 3 wants to receive memories
    #then they will receive a list containing, in order, 
    #the memories of the 4th player, then the 1st player, then the 2nd player
    def receiveMemories(self,memories):
        self.memories = memories

    #always draws a new card
    def sendDeckOrDiscard(self):
        return True

    #the game will send you a card
    def receiveCard(self, card):
        self.extraCard = card

    #looks at current hand and finds highest ranked card
    #that does not belong to any games. For testing it replaces that card
    #with drawn card and then again finds the highest ranked card
    #that does not belong to any games. If this card is the added card, then 
    #then discard higher of the two cards
    #otherwise keep it
    #cuts if it can

    #note that there will always exists such a card that does not belong
    #to a game since if there wouldn't be, it would've cut last round

    def decide(self):
        #gets the unused list
        bestCurrent = self.hand.bestOrder()[0]
        unused = bestCurrent.getUnused()
        #picks out the highest one
        unused.sort()
        unused.reverse()
        highestUnused = unused[0]
        #now replace new card with this card
        self.hand.replace(highestUnused,self.extraCard)
        #repeats same steps as earlier to get new highestUnused
        newBestCurrent = self.hand.bestOrder()[0]
        newUnused = newBestCurrent.getUnused()
        newUnused.sort()
        newUnused.reverse()
        newHighestUnused = newUnused[0]

        #if the worst card in this new order is the added extra card
        if newHighestUnused == self.extraCard:
            #and it's even worse than the previous worst card
            if newHighestUnused.getRank() >= highestUnused.getRank():
                #then we should replace it back
                self.hand.replace(self.extraCard, highestUnused)
            else:
                #otherwise then our old highestUnused is now our extra card
                self.extraCard = highestUnused

        cut = self.canCut()

        return self.extraCard, cut

    def canCut(self):
        bestValue = self.hand.bestOrder()[0].getValue()
        return bestValue <= 7

    def addScore(self, score):
        self.score += score

    def sendScore(self):
        return self.score



class Hand:
    def __init__(self, cards):
        self.trueSize = 7
        self.cards = cards
    
    def replace(self, oldCard, newCard):
        oldCardActuallyThere = False
        for card in self.cards:
            if card.cmpIdentity(oldCard):
                oldCardActuallyThere = True

        assert(oldCardActuallyThere),"Tried to replace a card that is not in hand"

        self.cards.remove(oldCard)
        self.cards.append(newCard)

    #returns a list of all possible ways to lay down the cards
    #sorted in order from least point gain to most point gain
    def bestOrder(self):
        master = []
        groups = self.findAllGroups()
        runs = self.findAllRuns()
        sortedGroups = [[]]
        sortedRuns = [[]]
        groupIndeces = [0]
        runIndeces = [0]
        for i in range(self.trueSize):
            sortedGroups.append([])
            sortedRuns.append([])

        #sorts groups by size
        #and makes a list of the sizes of groups we have
        for group in groups:
            length = len(group)
            sortedGroups[length].append(group)
            if length not in groupIndeces:
                groupIndeces.append(length)
        #sorts runs by size
        #and makes a list of the sizes of runs we have
        for run in runs:
            length = len(run)
            sortedRuns[length].append(run)
            if length not in runIndeces:
                runIndeces.append(length)

        #sends addToMaster all groups of size numGroups,
        #and all runs of numRuns. Does this for every
        #valid numGroups and numRuns
        for gIndex in groupIndeces:
            numGroups = gIndex
            for rIndex in runIndeces:
                numRuns = rIndex - numGroups
                master = self.processSectioning(master,
                                                numGroups,
                                                numRuns,
                                                sortedGroups,
                                                sortedRuns)

        master.sort()

        #deletes the orderings that are pretty much the same
        #(keeps one of the copies of course)
        toDelete = []
        for i in range(len(master)):
            for j in range(len(master)):
                if i != j:
                    if master[i].cmpIdentity(master[j]):
                        toDelete.append(master[i])

        for ordering in toDelete:
            master.remove(ordering)

        return master

    def processSectioning(self, master, numGroups, numRuns, sortedGroups, sortedRuns):
        #note that groups contains all potential groups of size numGroups
        #also that runs contains all potential runs of size numRuns


        if numGroups == 0:
            if numRuns == 0:
                master = self.addToMaster(master,[],[])

            #note that numRuns will never be 1 or 2

            #there's a maximum of one run here for
            #numRuns = 3,4,5, but 6 and 7 have more but still
            #have these ones
            elif numRuns in [3,4,5,6,7]:
                runs = sortedRuns[numRuns]
                for run in runs:
                    master = self.addToMaster(master,[],[run])
            #for remaining numRuns = 6
            #must have two runs of length 3
            if numRuns == 6:
                runs = sortedRuns[3]
                for run1 in runs:
                    for run2 in runs:
                        #make sure that the two runs are not colliding
                        #because that would just be a six run or some
                        #displacement of a joker
                        collision = False
                        for card1 in run1:
                            for card2 in run2:
                                if card1.cmpIdentity(card2):
                                    #now we know it's the same card
                                    #but we need to make sure that we don't have
                                    #two jokers and that's whats being compared
                                    joker = Card(13,4)
                                    numJokers = 0
                                    for card in self.cards:
                                        if card is joker:
                                            numJokers += 1

                                    collision = True
                                    if card1 is joker and numJokers == 2:
                                        collision = False
                                        numJokers = 1
                        if not collision:
                            master = self.addToMaster(master,[],[run1,run2])
            #for remining numRuns = 7
            #must have one run of length 4 and
            #one run of length 3
            elif numRuns == 7:
                runs3 = sortedRuns[3]
                runs4 = sortedRuns[4]

                for run1 in runs4:
                    for run2 in runs3:
                        master = self.addToMaster(master,[],[run1,run2])

        #note that numGroupss will ever be 1 or 2

        elif numGroups in [3,4]:
            #if this then we only have one game, so add it
            if numRuns == 0:
                groups = sortedGroups[numGroups]
                for group in groups:
                    master = self.addToMaster(master,[group],[])

            #numRuns cannot be 1 or 2 because that would be invalid

            #if numGroups is 3 or 4 and numRuns is 3 or 4
            #then we know we have at most one of each
            #so make an ordering with both of them
            #if they collide then making an ordering for each
            if numRuns in [3,4]:
                groups = sortedGroups[numGroups]
                runs = sortedRuns[numRuns]
                for group in groups:
                    for run in runs:

                        joker = Card(13,4)
                        numJokers = 0
                        for card in self.cards:
                            if card is joker:
                                numJokers += 1

                        collision = False
                        for card1 in group:
                            for card2 in run:
                                if card1.cmpIdentity(card2):
                                    #now we know it's the same card
                                    #but we need to make sure that we don't have
                                    #two jokers and that's what being compared
                                    collision = True
                                    if card1 is joker and numJokers == 2:
                                        collision = False
                                        numJokers = 1
                                              
                        if collision:
                            #make an ordering with just the group
                            master = self.addToMaster(master,[group],[])
                            #now with just the run
                            master = self.addToMaster(master,[],[run])
                        else:
                            #if there is no collision we can do both
                            master = self.addToMaster(master,[group],[run])

            #numRuns cannot be more than 4 because then numGroups
            #has to be less than 3

        #there can be no runs, and we must have two groups of size 3
        elif numGroups == 6:
            groups = sortedGroups[numGroups]
            for group1 in groups:
                for group2 in groups:
                    if not group1[2].cmpIdentity(group2[2]):
                            master = self.addToMaster(master,[group1,group2],[])

        #finally numGroups must be 7 and there must be
        #a group of 3 and a group of 4
        else:
            groups4 = sortedGroups[4]
            groups3 = sortedGroups[3]
            for group1 in groups4:
                for group2 in groups3:
                    master = self.addToMaster(master,[group1,group2],[])

        return master

    def addToMaster(self, master, groups, runs):
        unusedCards = []
        try:
            for card in self.cards:
                unusedCards.append(card)
            for group in groups:
                for card in group:
                    unusedCards.remove(card)
            for run in runs:
                for card in run:
                    unusedCards.remove(card)
        except:
            assert(False),"Sent colliding games"

        order = [groups,runs,unusedCards]
        master.append(Ordering(order))
        return master       

    #give it a list with index 0 : "groups", 1 : "runs", and 2 : "unused"
    #where each of these is a list containing the groups, runs, and unused cards
    #this method will tell you if it's a valid setup and how many points it's worth
    def getValue(self, order):
        unused = order[2]

        value = 0
        for card in unused:
            rank = card.getRank()
            if rank == 13:
                rank = 15
            value += rank+1

        return value

     #returns true if it's legal to order the cards this way
    
    #returns true if the order is legal
    def validateOrder(self, order):
        groups = order[0]
        runs = order[1]
        unused = order[2]

        for group in groups:
            if not self.validateGroup(group):
                return False
        
        for run in runs:
            if not self.validateRun(run):
                return False

        return True

    #tells if a group is valid
    def validateGroup(self, group):
        rank = -1
        for card in group:
            if card.getRank() != 13:    #gets the rank of the first non-joker card
                rank = card.getRank()
                break

        numCards = 0
        for card in group:     
            numCards+=1                 
            rankOfCard = card.getRank()
            if rankOfCard != rank and rankOfCard != 13: #checks if non-joker card has the right rank
                return False

        if numCards < 3:
            return False
        
        #we know they're all same rank, wondering if we have any duplicates
        suits = [0,0,0,0,0]
        for card in group:      #marks the suits we have
            suit = card.getSuit()
            suits[suit] += 1
        for num in range(len(suits)):       #checks if we have more than two non-joker suits
            if num is not 4 and suits[num] >= 2:
                return False            #there are two or more of the same suit thus not a group

        return True

    #tells if a run is valid
    def validateRun(self, run):
        suit = -1
        for card in run:
            if card.getSuit() != 4:         #gets the suit of the first non-joker card
                suit = card.getSuit()
                rankPrev = card.getRank()   #gets the rank of the first non-joker card
                break

        if suit == -1:
            return False

        numCards = 0
        for card in run:  
            numCards +=1                
            suitOfCard = card.getSuit()
            if suitOfCard != suit and suitOfCard != 4: #checks if a non-joker card has the right suit
                return False
        
        if numCards < 3:           #fails if run has less than 3 cards
            return False

        if run[0].getRank() == 13:
            start = 2
            if run[1].getRank() == 0:   #means we're putting a joker before an ace
                return False
        else:
            start = 1

        for index in range(start, len(run)):   #checks if the cards are consecutive
            rankCurrent = run[index].getRank()
            if rankCurrent == rankPrev+1 or rankCurrent == 13:
                rankPrev += 1
                if rankCurrent == 13 and index < len(run)-1 and run[index+1].getRank() == 13:   #two jokers in a row
                    return False
            else:
                return False
        if rankCurrent == 13:
            if rankPrev-1 == 12:    #means we're putting a joker after a king
                return False

        return True

    #finds all groups, including those completed by possible jokers
    #and sorts them into two sections: one which is completed on its own
    #and another which is completed with a joker. Note that groups to be completed
    #by jokers will be returned with a joker in them
    #also note that if you have two jokers, you cannot both put in the same
    #group so it doesn't matter      
    def findGroups(self):
        self.sortByRank()   #sorts cards by rank (perfect for groupings)
        cmpltdGroups = []
        cmpltablGroups = []
        groups = []
        group = []
        joker = Card(13,4)
        isJoker = False
        for card in self.cards:
            if card is joker:
                isJoker = True

        #find all groups if one ignores a possible joker
        for index in range(self.trueSize):
            if self.cards[index] is not joker:
                group.append(self.cards[index])
                if index < self.trueSize-1:
                    if self.cards[index].getRank() != self.cards[index+1].getRank():
                        groups.append(group)
                        group = []
                else:                   #else this is the last card
                    groups.append(group)

        for group in groups:
            length = len(group)
            if length >= 3:
                cmpltdGroups.append(group)
            elif length == 2 and isJoker:
                group.append(joker)
                cmpltablGroups.append(group)
            
        return cmpltdGroups, cmpltablGroups

    #return every group someone could come up with
    #adds cmpltablGroups and compltdGroups
    #if there exists a joker then
    #add a joker to each compltdGroup and add that as
    #well
    def findAllGroups(self):
        cmpltdGroups, cmpltablGroups = self.findGroups()
        allGroups = []
        for group in cmpltablGroups:
            allGroups.append(group)
        for group in cmpltdGroups:
            allGroups.append(group)
        
        joker = Card(13,4)
        isJoker = False
        for card in self.cards:
            if card is joker:
                isJoker = True

        if isJoker:
            for group in cmpltdGroups:
                if len(group) <= 3:
                    temp = []
                    for card in group:
                        temp.append(card)
                    temp.append(joker)
                    allGroups.append(temp)

        return allGroups

    #finds all runs and sorts them into four sections. First section is completed runs
    #Second section is runs that would be mergeable by one joker
    #Third section is runs that would be completed by one joker
    #NOTE THAT THE JOKER IS INSERTED IN RUNS FROM S. 1 AND 2 SO
    #THAT YOU KNOW WHICH CARDS YOU NEED
    #also note that if you have a 1S, 3S, 5S mrglRuns will notice
    #that 1S and 3S can be merged and that 3S and 5S can be merged
    #but will NOT concatenate the two mergings
    #Fourth section is all possible runs
    def findRuns(self):
        self.sortBySuitThenRank()
        cmpltdRuns = []
        cmpltablRuns = []
        mrgblRuns = []
        finishedRuns = []
        runs = []
        run = []
        joker = Card(13,4)
        numJokers = 0
        isJoker = False
        for card in self.cards:
            if card == joker:
                isJoker = True
                numJokers += 1
        
        #find all runs if one ignores a possible joker
        for index in range(self.trueSize):
            if self.cards[index] != joker:
                run.append(self.cards[index])
                if index < self.trueSize-1:
                    if ((self.cards[index].getRank()+1 != self.cards[index+1].getRank()) or 
                    (self.cards[index].getSuit() != self.cards[index+1].getSuit())):
                        runs.append(run)
                        run = []
                else:                   #else this is the last card
                    runs.append(run)

        for run in runs:
            temp = []
            for card in run:
                temp.append(card)
            length = len(temp)
            if length == 2:
                temp1 = []
                temp2 = []
                if run[0].getRank() != 0:
                    temp1.append(joker)
                for card in run:
                    temp1.append(card)
                    temp2.append(card)
                if run[1].getRank() != 12:
                    temp2.append(joker)
                cmpltablRuns.append(temp1)
                cmpltablRuns.append(temp2)
            elif length >= 3:
                cmpltdRuns.append(temp)

        #note that if you have multiple jokers then you cannot
        #have a run with consecutive jokers
        for card in self.cards:
            for index in range(len(runs)-1):
                lastCardInRun = runs[index][len(runs[index])-1]
                firstCardInNextRun = runs[index+1][0]
                if ((lastCardInRun.getRank()+2==firstCardInNextRun.getRank()) and 
                (lastCardInRun.getSuit() == firstCardInNextRun.getSuit())):
                    #means these two runs can be joined by a joker
                    runs[index].append(joker)
                    for addedCard in runs[index+1]: #now add the rest
                        runs[index].append(addedCard)

        for run in runs:
            if len(run) >= 3:
                for card in run:
                    if card == joker:   #means we inserted a joker, so it's one of our merged runs
                        mrgblRuns.append(run)
                        break

        return cmpltdRuns, mrgblRuns, cmpltablRuns

    #gets absolutely every run someone could possibly come up with
    #gets cmpltdRuns
    #if we have at least one joker it:
    #   adds joker to either end of cmpltdRuns and adds those
    #   adds cmpltbl runs
    #   adds mrgbl runs
    #   concatenates runs in mrgbl runs and adds those
    #if we have a second joker:
    #   adds jokers to both ends of cmpltdRuns and adds those
    #   adds joker to other end of cmpltbl runs
    #   adds joker to either end of mrgbl runs
    #   merges mrgbl runs again and adds those
    def findAllRuns(self):
        allRuns = []
        cmpltdRuns, mrgblRuns, cmpltablRuns = self.findRuns()
        joker = Card(13,4)

        #obviously add all cmpltdRuns
        for run in cmpltdRuns:
            allRuns.append(run)

        #finds number of jokers
        numJokers = 0
        for card in self.cards:
            if card == joker:
                numJokers += 1

        if numJokers >= 1:
            #if we have a joker we can add all cmpltabl runs of course
            for run in cmpltablRuns:
                allRuns.append(run)
                #if we have a second joker we can add it to either side
                #but we have to check which side the joker is already one
                #and we need to make sure we're not putting the joker
                #after a King or a before an Ace
                if numJokers == 2: 
                    add = False
                    temp = []
                    for card in run:
                        temp.append(card)
                    if run[0] == joker:
                        if run[1].getRank() != 12:
                            add = True
                            temp.append(joker)
                    else:
                        if run[0].getRank() != 0:
                            add = True
                            temp.insert(0,joker)
                    if add:
                        allRuns.append(temp)

            #we can also slap on jokers to either ends of cmpltdRuns
            for run in cmpltdRuns:
                temp1 = []     #with joker before
                temp2 = []     #with joker after
                temp3 = []     #with joker before and after
                add1 = False
                add2 = False

                if run[0].getRank() != 0:
                    #means its not an ace so we can add joker before     
                    temp1.append(joker)
                    temp3.append(joker)
                    add1 = True

                for card in run:
                    temp1.append(card)
                    temp2.append(card)
                    temp3.append(card)

                if run[len(run)-1].getRank() != 12:
                    #means its not a king so we can add joker after
                    temp2.append(joker)
                    temp3.append(joker)
                    add2 = True

                #before adding them to allRuns we need to check
                #if we were able to place the joker in the right spot
                if add1:
                    allRuns.append(temp1)
                if add2:
                    allRuns.append(temp2)
                if numJokers == 2 and add1 and add2 :
                    allRuns.append(temp3)

            #we might be able to merge merged runs
            toAdd = []
            for index in range(len(mrgblRuns)-1):
                currentRun = mrgblRuns[index]
                nextRun = mrgblRuns[index+1]
                #if last card of currentRun is the same as first card as nextRun
                if currentRun[len(currentRun)-1] == nextRun[len(nextRun)-1]:
                    #then they can be merged.
                    #the nextRun will receive the merger so that the merged run
                    #be checked next for further mergings
                    counter = 0
                    for card in currentRun:
                        nextRun.insert(counter,card)
                        counter += 1
                toAdd.append(mrgblRuns[index])
            for run in toAdd:
                allRuns.append(run)

            if numJokers == 2:
                #we can slap on jokers to the end of our runs.
                #note that since one joker has already been used
                #we can all add one more joker, not two more
                #We can also merge again. lol. Note that another
                #merger must merge two runs of size at least 3
                #so there is maximum one more merger available
                
                #first let's slap on jokers
                for run in toAdd:
                    add = False
                    temp1 = []  #to put joker before the run
                    temp2 = []  #to put joker after the run
                    for card in run:
                        temp1.append(card)
                        temp2.append(card)
                    if run[1].getRank() != 0:
                        temp1.append(joker)
                        allRuns.append(temp1)
                    if run[0].getRank() != 0:
                        temp2.insert(0,joker)
                        allRuns.append(temp2)

                #now let's see if we can merge again
                #remember this can only occur once if at all
                for index in range(len(mrgblRuns)-1):
                    current = mrgblRuns[index]
                    currentLast = current[len(current)-1]
                    currentRank = currentLast.getRank()
                    currentSuit = currentLast.getSuit()

                    following = mrgblRuns[index+1]
                    followingFirst = following[len(following)-1]
                    followingRank = followingFirst.getRank()
                    followingSuit = followingFirst.getSuit()

                    if currentRank == followingRank and currentSuit == followingSuit:                    
                        #means they can be merged
                        temp = []
                        for card in current:
                            temp.append(card)
                        card.append(joker)
                        for card in following:
                            temp.append(card)
                        toAdd.append(temp)
            
            for run in toAdd:
                allRuns.append(run)

        return allRuns

    #sorts the cards so that they are in ascending order
    #irrespective of suit
    def sortByRank(self):
        self.cards.sort()

    #sorts the spades, then hearts, clubs, diamonds
    #by rank
    def sortBySuitThenRank(self):
        self.sortByRank()
        spades = []
        hearts = []
        clubs = []
        diamonds = []
        jokers = []

        for card in self.cards:
            suit = card.getSuit()
            if suit >= 2:
                if suit == 2:
                    clubs.append(card)
                elif suit == 3:
                    diamonds.append(card)
                else:
                    jokers.append(card)
            else:
                if suit == 0:
                    spades.append(card)
                else:
                    hearts.append(card)

        sortedCards = spades+hearts+clubs+diamonds+jokers
        self.cards = sortedCards

    def __repr__(self):
        string = "["
        for index in range(self.trueSize):
            string += str(self.cards[index])
            if index == self.trueSize-1:
                string += "]"
            else:
                string += ", "

        return string



class Ordering:
    #value is a number
    #order is a list that contains 3 lists. 
    #   the first list contains lists of groups
    #   the second list contains lists of runs
    #   the third list contains cards in neither group or run lists
    def __init__(self, order):
        self.order = order
        self.setValue()

    def setValue(self):
        unused = self.order[2]

        value = 0
        for card in unused:
            rank = card.getRank()
            if rank == 13:
                rank = 15
            value += rank+1

        self.value = value

    def getValue(self):
        return self.value

    def getOrder(self):
        return self.order

    def getGroups(self):
        return self.order[0]

    def getRuns(self):
        return self.order[1]

    def getUnused(self):
        return self.order[2]

    def cmpIdentity(self, other):
        return (self == other and
               self.getRuns() == other.getRuns() and
               self.getGroups() == other.getGroups())

    def __str__(self):
        games = self.order[0]
        runs = self.order[1]
        unused = self.order[2]
        
        string = ""
        string += str(self.value)+": "
        for game in games:
            string += "G:("
            for card in game:
                string += str(card) + ","
            string+=") "
        for run in runs:
            string += "R:("
            for card in run:
                string += str(card) + ","
            string+=") "
        for card in unused:
            string += str(card) + ", "

        return string
  
    def __repr__(self):
        return ("%s") % (str(self.value))

    def __cmp__(self, other):
        return cmp(self.value, other.value)

    def __eq__(self,other):
        return(self.value == other.value)

    def __ne__(self, other):
        return(self.value != other.value)

    def __lt__(self, other):
        return(self.value < other.value)

    def __le__(self, other):
        return(self.value <= other.value)

    def __gt__(self, other):
        return (self.value > other.value)

    def __ge__(self, other):
        return (self.value >= other.value)



class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.isValid()

    def isValid(self):
        #note that the joker is of suit 4 and rank 13
        assert(self.suit<=4 and self.suit>=0),"Suit should be a number between 0 and 4"
        assert(self.rank<=13 and self.rank>=0),"Rank should be a number between 0 and 13"
        if self.rank == 13:
            assert(self.suit == 4),"If rank is 13, suit needs to be 4"
        if self.suit == 4:
            assert(self.rank == 13),"If suit is 4, rank needs to be 13"

    def getCard(self):
        return([self.getRank(), self.getSuit()])

    def getRank(self):
        return(self.rank)

    def getSuit(self):
        return(self.suit)

    #returns true if it's the exact same card
    def cmpIdentity(self, other):
        return self.__str__() == other.__str__()

    def __repr__(self):
        if self.rank == 13:
            return ("%s") % ("Joker")
        elif self.rank == 12:
            rank = "K"
        elif self.rank == 11:
            rank = "Q"
        elif self.rank == 10:
            rank = "J"
        else:
            rank = str(self.rank+1)

        if self.suit == 0:
            suit = "S"
        elif self.suit == 1:
            suit = "H"
        elif self.suit == 2:
            suit = "C"
        elif self.suit == 3:
            suit = "D"
        
        return ("%s%s") % (rank,suit)

    def __str__(self):
        return self.__repr__()

    #note that suit is irrelevant for comparison meaning a 7H and a 7D 
    #will return 0 despite them not being the same card
    def __cmp__(self, other):
        return cmp(self.rank, other.rank)

    def __eq__(self,other):
        return(self.rank == other.rank)

    def __ne__(self, other):
        return(self.rank != other.rank)

    def __lt__(self, other):
        return(self.rank < other.rank)

    def __le__(self, other):
        return(self.rank <= other.rank)

    def __gt__(self, other):
        return (self.rank > other.rank)

    def __ge__(self, other):
        return (self.rank >= other.rank)

def main1():
    card0 = Card(9,1)
    card1 = Card(3,1)
    card2 = Card(4,1)
    card3 = Card(6,1)
    card4 = Card(7,1)
    card5 = Card(13,4)
    card6 = Card(13,4)
    cards = [card0,card1,card2,card3,card4,card5,card6]

    hand = Hand(cards)
    master = hand.bestOrder()
    for ordering in master:
        print(ordering)

    hand.validateRun([card0,card1,card2,card5,card6,card4,card3])


main()