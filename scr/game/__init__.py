
import copy
from game.card import Card
from game.table import Table, Log
from game.fn_init import init
from game.fn_viewpoint import viewpoint, UserInfo
from game.brain import Brain




class Player:
    def __init__(self):
        self.cards: list[Card] = []


class Game:
    def __init__(self) -> None:
        self.table: Table = Table()
        self.players: list[Player] = [Player(),Player()]
        self.deck: list[Card] = []
        self.trump: Card
        self.has_pile: bool = False

        self.logs: list[Log] = []
        
        self.active: int # player id
        self.attacker: int # player id
        self.defender: int # player id

        self.winner: None | int = None

        self.brain = Brain()

        self.init()



    def init(self) -> None:
        init(self)


    def viewpoint(self, id: int) -> UserInfo:
        return viewpoint(self, id)



    def reset_match(self, status: int) -> None:
        
        # if cards gone into pile
        if status == -1:
            self.has_pile = True
            # change attack player
            self.defender, self.attacker = self.attacker, self.defender
        else:
            for cards in self.table.cards:
                self.players[status].cards.extend(cards)
        # add Logs
        self.logs.append( Log(
            table = copy.deepcopy(self.table),
            status = status
        ))
        # clean the table
        self.table = Table()
        self.active = self.attacker
        # grab cards
        self.grab_cards()
        self.sort_cards()



    
    def grab_cards(self) -> None:
        # previous attacker grabs first
        while self.deck and len(self.players[self.attacker].cards) < 6:
            self.players[self.attacker].cards.append(self.deck.pop())
        # previous defender grabs last
        while self.deck and len(self.players[self.defender].cards) < 6:
            self.players[self.defender].cards.append(self.deck.pop())



    def sort_cards(self) -> None:
        # divide by suit
        for player in self.players:
            sorted = [[],[],[],[]]
            for card in player.cards:
                sorted[card.suit.value].append(card)

            # sort individualy
            for sorted_suits in sorted:
                sorted_suits.sort(key=lambda card: card.num)

            # move trump card to the front
            sorted.append(sorted.pop(self.trump.suit.value))
            player.cards = sum(sorted, [])



    def check_win(self) -> bool:
        for id, player in enumerate(self.players):
            if not player.cards and not self.deck:
                self.winner = id
                return True
        return False



    def play(self, index: int) -> None:
        # game is finished
        if self.winner != None:
            return

        # index out of bound
        if index < -1 or index >= len(self.players[self.active].cards):
            return
        
        match self.active:
            case self.attacker as id: 

                # end attack
                if index == -1: 
                    if len(self.table.cards) > 0:
                        self.reset_match(-1)

                # add cards
                elif self.table.can_attack(self.players[id].cards[index], self.has_pile):
                    self.table.cards.append([self.players[id].cards.pop(index)])
                    # change active
                    self.active = self.defender

            case self.defender as id: 

                # grab table cards
                if index == -1:
                    self.reset_match(self.defender)

                # defend last attack card
                elif self.table.can_defend(self.players[id].cards[index], self.trump.suit):
                    self.table.cards[-1].append(self.players[id].cards.pop(index))
                    # change active
                    self.active = self.attacker

        self.check_win()




    def opposite_id(self, id: int) -> int:
        return 0 if id == 1 else 1



    def __str__(self) -> str:
        return(f"""\n\n
Deck length: {len(self.deck)}
Trump card: {self.trump}
Active player: {self.active}
Player 0 cards: {self.players[0].cards}
Table : {self.table.cards}
Player 1 cards: {self.players[1].cards}

Game winner: {self.winner}
        \n\n""")
        

    
        

