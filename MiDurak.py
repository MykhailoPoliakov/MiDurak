import pygame
import random
import sys, os
import json

# game part
card_deck         = []    # card deck
player1_deck      = []    # player deck
player2_deck      = []    # bot deck
table_at_deck     = []    # attack deck
table_def_deck    = []    # defence deck
trump_card        = ''    # trump card
attack_player     = 0
# taking cards from deck animation
animation_list    = []    # list with cards to animate(fron deck to player)
# throw card out animation
anim_at_throw     = []
anim_def_throw    = []
# grabbing animation
grab_it           = 0
want_to_grab      = 0     # if any player is grabbing cards from the table
able_to_grab      = False # player permission to grab card from the table
anim_at_player    = []
animated_at_cards = []
anim_def_player   = []
animated_def_cards= []
# putting cards on the table animation
anim_at_table     = []    # list with cards to animate(fron player to attack table)
anim_def_table    = []    # list with cards to animate(fron player to defence table)
# taking from the deck animation
take_f_deck_queue = []    # stores data about taking cards from the deck
able_to_take      = True
# if cards were beaten already
cards_been_beaten = False
# menu
pause_mode        = False
menu_mode         = True
stat_mode         = False
# timer and win
time_is_up        = False
win_happened      = False

# starting values
all_addable_cards = []    # list of cards to add when attacking (only numbers)
card_anim_dict    = {}
trump_match = {
    'h' : 'r',
    'd' : 'r',
    'c' : 'b',
    's' : 'b'
}
card_pos_dict = {
    'anim_but'  : 0,
    'anim_trump': 0,
    'p_y_cord'  : 0,
    'menu_up'   : 0,
    'menu_mid'  : 0,
    'menu_down' : 0,
}
bool_dict = {
    'throw_at_bool'  : True,
    'throw_def_bool' : True,
    'table_at_bool'  : True,
    'table_def_bool' : True,
    'grab_at_bool'   : True,
    'grab_def_bool'  : True,
    'anim_bool'      : True,
}
card_pos_dict_copy = card_pos_dict.copy()
bool_dict_copy = bool_dict.copy()
# checking player statistic
file_name = "user_data.json"
if os.path.exists(file_name):
    with open(file_name,"r",encoding="utf-8") as json_file:
        user_data = json.load(json_file)
else:
    user_data = {
        'user_games': 0,
        'user_wins': 0
    }

"""Small Game Functions"""
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

def create_deck():
    """creating a deck of cards"""
    global trump_card
    card_types = ['06', '07', '08', '09', '10', '12', '13', '14', '15']
    suit_types = ['s', 'h', 'd', 'c']
    for cards in card_types:
        for suit in suit_types:
            card_deck.append(suit + cards)
    random.shuffle(card_deck)
    trump_card = card_deck[0]

def free_to_move(win=False) -> bool:
    if (not anim_def_table and not anim_at_table and not animation_list and not take_f_deck_queue and not anim_at_player
        and not anim_at_player and not anim_def_player and not pause_mode and not menu_mode and not stat_mode):
        if win or not win_happened:
            return True
    return False

def all_addable_cards_calc():
    """calculating all addable cards"""
    global all_addable_cards
    all_addable_cards = []
    for cards in table_at_deck:
        all_addable_cards.append(cards[-2:])
    for cards in table_def_deck:
        all_addable_cards.append(cards[-2:])

def first_beat() -> bool:
    """checks if the first cards were beaten"""
    if cards_been_beaten:
        length = 5
    else:
        length = 4
    if length >= len(table_at_deck) :
        return True
    else:
        return False

def op_deck(player_deck):
    """returning the opposite deck"""
    if player_deck == player1_deck:
        return player2_deck
    else:
        return player1_deck

"""Big Game Functions"""
def who_moves_first():
    """decides who moves first"""
    def lowest_card(player_deck):
        """finds the lowest trump card in a deck"""
        lowest_player_card = 'x20'
        for cards in player_deck:
            if cards[0] == trump_card[0] and int(cards[-2:]) < int(lowest_player_card[-2:]):
                lowest_player_card = cards
        return lowest_player_card[-2:]
    global attack_player
    if lowest_card(card_deck[-6:]) < lowest_card(card_deck[-12:-6]):
        attack_player = 1
    else:
        attack_player = 2

def timer():
    """timer for player, stops the game if needed"""
    global time_is_up
    if not hasattr(timer, 'time'):
        timer.time = 2100
        timer.old_at = table_at_deck
        timer.old_def = table_def_deck
    if not pause_mode and free_to_move():
        timer.time -= 1
    if timer.old_at != table_at_deck or timer.old_def != table_def_deck or menu_mode:
        timer.time = 2100
    timer.old_at = table_at_deck.copy()
    timer.old_def = table_def_deck.copy()
    if timer.time <= 0:
        time_is_up = True
    return timer.time

def take_from_deck(animation_active = True):
    """fill player deck with cards"""
    global table_at_deck, table_def_deck, animated_at_cards, animated_def_cards
    if take_f_deck_queue and not anim_at_player and not anim_at_throw and not anim_def_throw and not menu_mode:
        table_at_deck = []
        table_def_deck = []
        animated_at_cards = []
        animated_def_cards = []
        for take in take_f_deck_queue:
            if take == 1:
                player_deck = player1_deck
            else:
                player_deck = player2_deck
            player_take = True  # has 6 cards
            while player_take:
                if card_deck != [] and len(player_deck) < 6:
                    if animation_active:
                        card_info = len(player_deck)
                        if player_deck == player1_deck:
                            animation_list.append(('pl1',card_info))
                        else:
                            animation_list.append(('pl2',card_info))
                    player_deck.append(card_deck.pop()) #pop(-1)
                else:
                    player_take = False
            del take_f_deck_queue[0]

def win_check():
    """check if player won and stop the game"""
    def end_screen(final_text):
        """render final screen"""
        x_add = 0
        time = win_check.time - 1
        if 300 < time < 400:
            x_add = (time - 300) * 8
        if time < 400:
            screen.blit(textures['back_pattern'],(0,0))
            screen.blit(textures['win_panel'],(0,270))
            end_font = pygame.font.Font(resource_path("font/pixel_font.ttf"), 70)
            end_text = end_font.render(final_text, True, (0, 0, 0))
            screen.blit(end_text, (250 - x_add, 350))
    global menu_mode, win_happened, time_is_up
    if not hasattr(win_check, 'time') or not win_happened:
        win_check.time = 500
    if not card_deck and free_to_move(True):
        if not player1_deck:
            end_screen('   You Win!   ')
            if not win_happened:
                user_data['user_wins'] += 1
                with open(file_name, "w", encoding="utf-8") as json_file_f:
                    json.dump(user_data, json_file_f, ensure_ascii=False, indent=4, sort_keys=True)
            win_happened = True
        if not player2_deck:
            end_screen('Opponent Wins!')
            win_happened = True
    elif time_is_up:
        end_screen(' Time Is Up!  ')
        win_happened = True
    if win_happened:
        win_check.time -= 1
        if win_check.time <= 0:
            time_is_up = False
            win_happened = False
            menu_mode = True

def player_change_at(player_deck):
    """if opponent defended himself, switching the player"""
    global table_at_deck,table_def_deck,attack_player, cards_been_beaten, anim_at_throw, anim_def_throw
    cards_been_beaten = True
    anim_at_throw = table_at_deck.copy()
    anim_def_throw = table_def_deck.copy()
    # allowing card taking and changing the player
    if player_deck == player1_deck:
        take_f_deck_queue.append(1)
        take_f_deck_queue.append(2)
        attack_player = 2
    else:
        take_f_deck_queue.append(2)
        take_f_deck_queue.append(1)
        attack_player = 1

def player_change_def(player_deck):
    """if opponent didn't defend himself, not switching the player"""
    global table_at_deck,table_def_deck,attack_player,able_to_grab,want_to_grab
    # make player grab cards from table
    want_to_grab = 1 if player_deck == player1_deck else 2
    if able_to_grab:
        for card_at in table_at_deck:
            player_deck.append(card_at)
            anim_at_player.append((card_at, table_at_deck.index(card_at), player_deck.index(card_at), want_to_grab))
        for card_def in table_def_deck:
            player_deck.append(card_def)
            anim_def_player.append((card_def, table_def_deck.index(card_def), player_deck.index(card_def), want_to_grab))
        # allowing taking cards
        if player_deck == player1_deck:
            take_f_deck_queue.append(2)
        else:
            take_f_deck_queue.append(1)
        # cleaning the table
        able_to_grab = False
        want_to_grab = 0

def attack_button(number,player_deck):
    """Checking if attack card works"""
    if table_at_deck == [] or player_deck[number][-2:] in all_addable_cards:
        table_at_deck.append(player_deck[number])
        anim_at_table.append(
            (player_deck[number], attack_player, number, table_at_deck.index(player_deck[number])))
        del player_deck[number]
        return True
    else:
        return False

def defence_button(number,player_deck):
    """Checking if defence card works"""
    if len(player_deck) > number:
        if ((int(player1_deck[number][-2:]) > int(table_at_deck[-1][-2:]) and player1_deck[number][0] == table_at_deck[-1][0])
        or (player1_deck[number][0] == trump_card[0] and table_at_deck[-1][0] != trump_card[0])):
            table_def_deck.append(player_deck[number])
            anim_def_table.append(
                (player_deck[number], attack_player, number, table_def_deck.index(player_deck[number]))
            )
            del player_deck[number]
            return True
    return False

"""Animation Functions"""
def animation_calc(calc_bool,start_x, start_y, final_x, final_y, anim_name, list_to_del, blit = ('x20','','')):
    if bool_dict[calc_bool]:
        card_pos_dict[anim_name + "diff_x"] = (final_x - start_x) / 10
        card_pos_dict[anim_name + "diff_y"] = (final_y - start_y) / 10
        card_pos_dict[anim_name + "active_x"] = start_x
        card_pos_dict[anim_name + "active_y"] = start_y
        bool_dict[calc_bool] = False
        if blit[1] == 'remember_at_card' or blit[1] == 'remember_def_card':
            card_pos_dict[blit[1]] = blit[0]
    if (start_x <= card_pos_dict[anim_name + "active_x"] <= final_x - card_pos_dict[anim_name + "diff_x"] or
            start_x >= card_pos_dict[anim_name + "active_x"] >= final_x - card_pos_dict[anim_name + "diff_x"]):
        card_pos_dict[anim_name + "active_x"] += card_pos_dict[anim_name + "diff_x"]
        card_pos_dict[anim_name + "active_y"] += card_pos_dict[anim_name + "diff_y"]
        if blit[1] == 'take_from_deck':
            screen.blit(textures['face_down'], (card_pos_dict[anim_name + "active_x"], card_pos_dict[anim_name + "active_y"]))
    else:
        bool_dict[calc_bool] = True
        if blit[1] == 'remember_at_card':
            animated_at_cards.append(card_pos_dict[blit[1]])
        elif blit[1] == 'remember_def_card':
            animated_def_cards.append(card_pos_dict[blit[1]])
        del list_to_del[0]
    return card_pos_dict[anim_name + "active_x"], card_pos_dict[anim_name + "active_y"]

def menu_button_anim(pos_dict, text_menu, text_pause, text_stat, menu_y_cord):
    menu_size = card_pos_dict[pos_dict] * 2
    menu_dev_2 = int(card_pos_dict[pos_dict] / 2)
    textures['menu_button'] = pygame.transform.scale(textures['menu_button'], (420 + menu_size, 100 + menu_size))
    screen.blit(textures['menu_button'], (525 - card_pos_dict[pos_dict], menu_y_cord - card_pos_dict[pos_dict]))
    menu_font = pygame.font.Font(resource_path("font/pixel_font.ttf"), 40 + menu_dev_2)
    if menu_mode:
        menu_text = menu_font.render(text_menu, True, (0, 0, 0))
    elif stat_mode:
        menu_text = menu_font.render(text_stat, True, (0, 0, 0))
    else:
        menu_text = menu_font.render(text_pause, True, (0, 0, 0))
    return menu_text, (570 - card_pos_dict[pos_dict], menu_y_cord + 30 - menu_dev_2)

def take_button_anim() -> str:
    if attack_player == 1 and free_to_move():
        if len(table_at_deck) == len(table_def_deck) >= 1:
            return "Done"
        elif len(table_at_deck) > len(table_def_deck) and want_to_grab:
            return "Done"
    elif attack_player == 2 and len(table_at_deck) > len(table_def_deck) and free_to_move():
        return "Take"
    return ""

"""Bot Brain Functions"""
def attack_calc(bot_move) -> str:
    """chooses the best attack card to play"""
    # choosing the card
    if not bot_move:
        return ""
    found_good_card = False
    main_card = 'x20'
    for cards in bot_move:
        if int(cards[-2:]) < int(main_card[-2:]) and cards[0] != trump_card[0]:
            main_card = cards
            found_good_card = True
    if main_card == 'x20':
        for cards in bot_move:
            if int(cards[-2:]) < int(main_card[-2:]):
                main_card = cards
    if main_card == 'x20':
        main_card = bot_move[0]
    # if it is the first move, there is a good card or deck is empty
    if not table_at_deck or found_good_card or not card_deck:
        return main_card
    else:
        return ""

def defence_calc(bot_move,player_deck) -> str:
    """chooses the best defence card to play"""
    # choosing the card
    if not bot_move:
        return ""
    found_good_card = False
    found_mid_card = False
    main_card = 'x20'
    for cards in bot_move:
        if int(cards[-2:]) < int(main_card[-2:]) and cards[0] != trump_card[0]:
            main_card = cards
            found_good_card = True
    if main_card == 'x20':
        for cards in bot_move:
            if int(cards[-2:]) < int(main_card[-2:]):
                main_card = cards
                found_mid_card = True
    if main_card == 'x20':
        main_card = bot_move[0]
    # if card is ok, deck is empty or stakes are high
    if found_good_card or (found_mid_card and int(main_card[-2:]) <= 10) or not card_deck:
        return main_card
    elif (len(table_at_deck) > 4) or (len(player_deck) > 8):
        return main_card
    else:
        return ""

def bot_brain(player_deck):
    """makes a bot move"""
    global all_addable_cards,able_to_grab, want_to_grab
    if not free_to_move():
        return
    bot_move = []
    number = 1 if player_deck == player1_deck else 2
    op_num = 2 if player_deck == player1_deck else 1
    # bot attack moves
    if (attack_player == 1 and player_deck == player1_deck) or (attack_player == 2 and player_deck == player2_deck):
        if len(table_at_deck) == len(table_def_deck) or (want_to_grab == op_num):
            for cards in player_deck:
                if not table_at_deck or cards[-2:] in all_addable_cards:
                    bot_move.append(cards)
            final_move = attack_calc(bot_move)
            if final_move == "":
                if want_to_grab == op_num:
                    able_to_grab = True
                    player_change_def(op_deck(player_deck))
                else:
                    player_change_at(player_deck)
                return
            elif not first_beat():
                player_change_at(player_deck)
                return
            table_at_deck.append(final_move)
            anim_at_table.append(
                (final_move,attack_player,player_deck.index(final_move),table_at_deck.index(final_move)))
            player_deck.remove(final_move)
            return
        return
    # bot defence moves
    if (attack_player == 1 and player_deck == player2_deck) or (attack_player == 2 and player_deck == player1_deck):
        if len(table_at_deck) > len(table_def_deck):
            for cards in player_deck:
                if cards[-2:] > table_at_deck[-1][-2:] and cards[0] == table_at_deck[-1][0]:
                    bot_move.append(cards)
                if cards[0] == trump_card[0] and table_at_deck[-1][0] != trump_card[0]:
                    bot_move.append(cards)
            final_move = defence_calc(bot_move, player2_deck)
            if final_move == "":
                want_to_grab = number
                return
            elif want_to_grab != number:
                table_def_deck.append(final_move)
                anim_def_table.append(
                    (final_move, attack_player, player_deck.index(final_move), table_def_deck.index(final_move))
                )
                player_deck.remove(final_move)
                return
    return

def game_init():
    """starting the game"""
    global card_deck, player1_deck, player2_deck, table_at_deck, table_def_deck, animation_list, card_pos_dict
    global anim_at_throw,anim_def_throw,grab_it,want_to_grab,take_f_deck_queue, card_anim_dict,bool_dict
    global able_to_grab,anim_at_player, animated_at_cards,anim_def_player,animated_def_cards
    global anim_at_table,anim_def_table,able_to_take,cards_been_beaten
    # resetting everything
    card_deck = []
    player1_deck = []
    player2_deck = []
    table_at_deck = []
    table_def_deck = []
    animation_list = []
    anim_at_throw = []
    anim_def_throw = []
    grab_it = 0
    want_to_grab = 0
    able_to_grab = False
    anim_at_player = []
    animated_at_cards = []
    anim_def_player = []
    animated_def_cards = []
    anim_at_table = []
    anim_def_table = []
    take_f_deck_queue = []
    able_to_take = True
    cards_been_beaten = False
    card_anim_dict = {}
    card_pos_dict = card_pos_dict_copy
    bool_dict = bool_dict_copy
    # creating decks
    create_deck()
    take_f_deck_queue.append(1)
    take_f_deck_queue.append(2)
    who_moves_first()
    # remaking the trump card
    textures['trump_num'] = pygame.image.load(resource_path(f"textures/{trump_card[-2:]  + trump_match[trump_card[0]]}.png")).convert_alpha()
    textures['trump_suit'] = pygame.image.load(resource_path(f"textures/{trump_card[0]}.png")).convert_alpha()
    textures['trump_num'] = pygame.transform.scale(textures['trump_num'], (120, 175))
    textures['trump_suit'] = pygame.transform.scale(textures['trump_suit'], (120, 175))
    textures['trump_num'] = pygame.transform.rotate(textures['trump_num'], 90)
    textures['trump_suit'] = pygame.transform.rotate(textures['trump_suit'], 90)
    # player started the game
    user_data['user_games'] += 1
    with open(file_name, "w", encoding="utf-8") as json_file_f:
        json.dump(user_data, json_file_f, ensure_ascii=False, indent=4, sort_keys=True)

# creating fake deck
create_deck()

# pygame initialization
pygame.init()
screen = pygame.display.set_mode((1500, 800))
screen = pygame.display.set_mode((1500, 800), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (0, 55, 0)
screen.fill(background_color)

# textures
textures = {
    '15r'         : pygame.image.load(resource_path("textures/15r.png")).convert_alpha(),
    '14r'         : pygame.image.load(resource_path("textures/14r.png")).convert_alpha(),
    '13r'         : pygame.image.load(resource_path("textures/13r.png")).convert_alpha(),
    '12r'         : pygame.image.load(resource_path("textures/12r.png")).convert_alpha(),
    '10r'         : pygame.image.load(resource_path("textures/10r.png")).convert_alpha(),
    '09r'         : pygame.image.load(resource_path("textures/09r.png")).convert_alpha(),
    '08r'         : pygame.image.load(resource_path("textures/08r.png")).convert_alpha(),
    '07r'         : pygame.image.load(resource_path("textures/07r.png")).convert_alpha(),
    '06r'         : pygame.image.load(resource_path("textures/06r.png")).convert_alpha(),
    '15b'         : pygame.image.load(resource_path("textures/15b.png")).convert_alpha(),
    '14b'         : pygame.image.load(resource_path("textures/14b.png")).convert_alpha(),
    '13b'         : pygame.image.load(resource_path("textures/13b.png")).convert_alpha(),
    '12b'         : pygame.image.load(resource_path("textures/12b.png")).convert_alpha(),
    '10b'         : pygame.image.load(resource_path("textures/10b.png")).convert_alpha(),
    '09b'         : pygame.image.load(resource_path("textures/09b.png")).convert_alpha(),
    '08b'         : pygame.image.load(resource_path("textures/08b.png")).convert_alpha(),
    '07b'         : pygame.image.load(resource_path("textures/07b.png")).convert_alpha(),
    '06b'         : pygame.image.load(resource_path("textures/06b.png")).convert_alpha(),
    'h'           : pygame.image.load(resource_path("textures/h.png")).convert_alpha(),
    'd'           : pygame.image.load(resource_path("textures/d.png")).convert_alpha(),
    's'           : pygame.image.load(resource_path("textures/s.png")).convert_alpha(),
    'c'           : pygame.image.load(resource_path("textures/c.png")).convert_alpha(),
    'table'       : pygame.image.load(resource_path("textures/table.png")).convert_alpha(),
    'button_up'   : pygame.image.load(resource_path("textures/button_up.png")).convert_alpha(),
    'button_down' : pygame.image.load(resource_path("textures/button_down.png")).convert_alpha(),
    'button_active': pygame.image.load(resource_path("textures/button_active.png")).convert_alpha(),
    'button_passive': pygame.image.load(resource_path("textures/button_passive.png")).convert_alpha(),
    'empty_card'  : pygame.image.load(resource_path("textures/empty_card.png")).convert_alpha(),
    'beaten_card' : pygame.image.load(resource_path("textures/beaten_card.png")).convert_alpha(),
    'face_down'   : pygame.image.load(resource_path("textures/face_down.png")).convert_alpha(),
    'deck_side'   : pygame.image.load(resource_path("textures/deck_side.png")).convert_alpha(),
    'trump_empty' : pygame.image.load(resource_path("textures/empty_card.png")).convert_alpha(),
    'trump_num'   : pygame.image.load(resource_path(f"textures/{trump_card[-2:]  + trump_match[trump_card[0]]}.png")).convert_alpha(),
    'trump_suit'  : pygame.image.load(resource_path(f"textures/{trump_card[0]}.png")).convert_alpha(),
    'loading'     : pygame.image.load(resource_path("textures/loading.png")).convert_alpha(),
    'menu'        : pygame.image.load(resource_path("textures/menu.png")).convert_alpha(),
    'menu_button' : pygame.image.load(resource_path("textures/menu_button.png")).convert_alpha(),
    'pause'       : pygame.image.load(resource_path("textures/pause.png")).convert_alpha(),
    'win_panel'   : pygame.image.load(resource_path("textures/win_panel.png")).convert_alpha(),
    'back_pattern': pygame.image.load(resource_path("textures/back_pattern.png")).convert_alpha(),
}
# resizing
for texture in textures.keys():
    if ((len(texture) == 3 and int(texture[:2]) in range(6,16)) or
    texture in ['h','d','s','c','empty_card','beaten_card','face_down','trump_empty','deck_side']):
        textures[texture] = pygame.transform.scale(textures[texture], (120, 175))
textures['trump_empty'] = pygame.transform.rotate(textures['trump_empty'], 90)
textures['table'] = pygame.transform.scale(textures['table'], (1325, 340))
textures['menu'] = pygame.transform.scale(textures['menu'], (640, 450))
textures['win_panel'] = pygame.transform.scale(textures['win_panel'], (1500, 240))

# all buttons (start x start y length x length y)
button_P = pygame.Rect(1400, 15, 80, 80)
button_U = pygame.Rect(525, 320, 420, 100)
button_M = pygame.Rect(525, 445, 420, 100)
button_D = pygame.Rect(525, 570, 420, 100)
button_R = pygame.Rect(0, 0, 80, 80)
button_T = pygame.Rect(1030, 292, 175, 120)
button_0 = pygame.Rect(1025, 460, 230, 70)
all_buttons = {}
for index in range(36):
    all_buttons["button_" + str(index + 1)] = None
all_table_buttons = {}

# main cycle
running = True
while running:
    x_add_player_deck = (125 if len(player1_deck) <= 10 else 125 - (len(player1_deck) - 10) * 6) if len(player1_deck) < 22 else 59
    x_add_bot_deck = (125 if len(player2_deck) <= 10 else 125 - (len(player2_deck) - 10) * 6) if len(player2_deck) < 22 else 59
    x_cord = 15
    for button in all_buttons.keys():
        all_buttons[button] = pygame.Rect(x_cord, 600, 120, 175)
        x_cord += x_add_player_deck
    for index in range(6):
        y_add = 0
        if grab_it == 1:
            y_add = 100
        elif grab_it == 2:
            y_add = -100
        all_table_buttons["button_" + str(index + 1)] = pygame.Rect(
            40 + 145 * index, 300 + y_add if index % 2 == 0 else 270 + y_add, 150, 215)
    # take from the deck
    take_from_deck()
    # bot making a move
    all_addable_cards_calc()
    bot_brain(player2_deck)

    """ INPUT """
    # mouse on card input
    mouse_pos = pygame.mouse.get_pos()
    mouse_lock = None
    if button_U.collidepoint(mouse_pos):
        mouse_lock = -3
    elif button_M.collidepoint(mouse_pos):
        mouse_lock = -4
    elif button_D.collidepoint(mouse_pos):
        mouse_lock = -5
    if not menu_mode and not pause_mode and not stat_mode:
        if button_0.collidepoint(mouse_pos):
            mouse_lock = -1
        elif button_T.collidepoint(mouse_pos):
            mouse_lock = -2
        for button in all_buttons:
            if all_buttons[button].collidepoint(mouse_pos):
                mouse_lock = int(button[7:]) - 1
                break
        for button in all_table_buttons:
            if all_table_buttons[button].collidepoint(mouse_pos):
                mouse_lock = 50 + int(button[7:])
                break

    # mouse click input
    for event in pygame.event.get():
        # ways to exit
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        # menu input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if menu_mode:
                if button_U.collidepoint(mouse_pos):
                    menu_mode = False
                    game_init()
                elif button_M.collidepoint(mouse_pos):
                    running = False
                elif button_D.collidepoint(mouse_pos):
                    menu_mode = False
                    stat_mode = True
            elif stat_mode:
                if button_R.collidepoint(mouse_pos):
                    user_data = {'user_games': 0, 'user_wins': 0}
                    with open(file_name, "w", encoding="utf-8") as json_file_f:
                        json.dump(user_data, json_file_f, ensure_ascii=False, indent=4, sort_keys=True)
                if button_D.collidepoint(mouse_pos):
                    menu_mode = True
                    stat_mode = False
            elif pause_mode:
                if button_U.collidepoint(mouse_pos):
                    pause_mode = False
                elif button_M.collidepoint(mouse_pos):
                    pause_mode = False
                    menu_mode = True
                elif button_D.collidepoint(mouse_pos):
                    menu_mode = False
                    stat_mode = True
            else:
                if button_P.collidepoint(mouse_pos) and not menu_mode:
                    pause_mode = True
        # attack input
        if event.type == pygame.MOUSEBUTTONDOWN and attack_player == 1 and free_to_move():
            if button_0.collidepoint(event.pos) and len(table_at_deck) == len(table_def_deck) >= 1:
                player_change_at(player1_deck)
            elif button_0.collidepoint(event.pos) and len(table_at_deck) > len(table_def_deck) and want_to_grab:
                able_to_grab = True
                player_change_def(player2_deck)
            for button in all_buttons:
                if all_buttons[button].collidepoint(event.pos) and len(player1_deck) >= int(button[7:]) and first_beat():
                    attack_button(int(button[7:]) -1,player1_deck)
                    break
        # defence input
        elif (event.type == pygame.MOUSEBUTTONDOWN and attack_player == 2 and
              len(table_at_deck) > len(table_def_deck) and free_to_move()):
            if button_0.collidepoint(event.pos):
                want_to_grab = 1
            for button in all_buttons:
                if all_buttons[button].collidepoint(event.pos):
                    defence_button(int(button[7:]) -1,player1_deck)
                    break

    """ OUTPUT """
    # background
    screen.blit(textures['back_pattern'], (0, 0))
    screen.blit(textures['table'], (5, 235))

    # button to change player and it's animation
    if mouse_lock == -1:
        if card_pos_dict['anim_but'] < 5:
            card_pos_dict['anim_but'] += 1
    elif 0 < card_pos_dict['anim_but']:
        card_pos_dict['anim_but'] -= 1
    anim_but = card_pos_dict['anim_but']
    textures['button_up'] = pygame.transform.scale(textures['button_up'], (240 , 80 ))
    textures['button_down'] = pygame.transform.scale(textures['button_down'], (240 , 80 ))
    screen.blit(textures['button_up'], (1020, 455))
    move = take_button_anim()
    if move:
        textures['button_active'] = pygame.transform.scale(textures['button_active'],(240, 80))
        screen.blit(textures['button_active'], (1020, 455 + anim_but * 2))
        font = pygame.font.Font(resource_path("font/pixel_font.ttf"), 40)
        text = font.render(move, True, (100, 0, 0))
        screen.blit(text, (1057, 470 + anim_but * 2))
    else:
        textures['button_passive'] = pygame.transform.scale(textures['button_passive'],(240, 80))
        screen.blit(textures['button_passive'], (1020, 455))
    screen.blit(textures['button_down'], (1020, 455))

    # deck output
    if card_deck != []:
        # trump card animation
        if mouse_lock == -2:
            if 30 > card_pos_dict['anim_trump']:
                card_pos_dict['anim_trump'] += 4
        elif card_pos_dict['anim_trump'] > 0:
            card_pos_dict['anim_trump'] -= 4
        screen.blit(textures['trump_empty'], (1030 - card_pos_dict['anim_trump'], 292))
        screen.blit(textures['trump_suit'], (1030 - card_pos_dict['anim_trump'], 292))
        screen.blit(textures['trump_num'], (1030 - card_pos_dict['anim_trump'], 292))
        # deck output
        if len(card_deck) > 1:
            screen.blit(textures['deck_side'], (1125, 265))
            screen.blit(textures['face_down'], (1140, 265))
            pygame.draw.rect(screen, (255, 255, 255), (1140, 330, 120, 45))
            font = pygame.font.Font(resource_path("font/pixel_font.ttf"), 40)
            text = font.render(str(len(card_deck)), True, (0, 0, 0))
            screen.blit(text, (1163, 335))

    else:
        screen.blit(textures['trump_suit'], (800, 340))

    # timer output
    y_length = int(timer() / 7)
    if y_length > 115:
        add_color = 80
    elif add_color > 0:
        add_color -= 5
    pygame.draw.rect(screen, (0, 0, 0), (1385, 265, 55, 275))
    pygame.draw.rect(screen, (255, 128 + int(add_color/2) ,add_color), (1385, 560 - y_length, 55, y_length))
    screen.blit(textures['loading'], (1375, 240))

    # opponent cards output
    for index, card in enumerate(player2_deck):
        card_pop = True
        index_list = 10
        for index2 in range(len(animation_list)):
            if int(animation_list[index2][1]) <= index_list and animation_list[index2][0] == 'pl2':
                index_list = animation_list[index2][1]
        if not (index_list == 10 or index_list > index):
            card_pop = False
        if card in table_at_deck or card in table_def_deck:
            card_pop = False
        if card in animated_def_cards or card in animated_at_cards:
            card_pop = True
        # output
        if card_pop:
            screen.blit(textures['face_down'], (15 + x_add_bot_deck * index, 30))
            # to see bot cards

    # player cards output
    for card in card_anim_dict.copy():
        if card not in player1_deck and not card in ['51','52','53','54','55','56']:
            del card_anim_dict[card]
    for index, card in enumerate(player1_deck):
        # cord calculation
        x_cord = 15 + x_add_player_deck * index
        if card not in card_anim_dict:
            card_anim_dict[card] = 600
        if mouse_lock == index:
            if 570 <= card_anim_dict[card]:
                card_anim_dict[card] -= 5
        elif card_anim_dict[card] <= 595:
            card_anim_dict[card] += 5
        y_cord = card_anim_dict[card]
        # if card pop up
        card_pop = True
        index_list = 10
        for index2 in range(len(animation_list)):
            if int(animation_list[index2][1]) <= index_list and animation_list[index2][0] == 'pl1':
                index_list = animation_list[index2][1]
        if not (index_list == 10 or index_list > index):
            card_pop = False
        if card in table_at_deck or card in table_def_deck:
            card_pop = False
        if card in animated_def_cards or card in animated_at_cards:
            card_pop = True
        # output
        if card_pop:
            screen.blit(textures['empty_card'], (x_cord, y_cord))
            screen.blit(textures[card[-2:] + trump_match[card[0]]], (x_cord, y_cord))
            screen.blit(textures[card[0]], (x_cord, y_cord))

    # table output
    # grabbing animation
    if want_to_grab == 1:
        grab_it = 1
    elif want_to_grab == 2:
        grab_it = 2
    if grab_it == 1:
        if card_pos_dict['p_y_cord'] < 100:
            card_pos_dict['p_y_cord'] += 4
    elif grab_it == 2:
        if card_pos_dict['p_y_cord'] > -100:
            card_pos_dict['p_y_cord'] -= 4
    else:
        card_pos_dict['p_y_cord'] = 0
    if not table_at_deck:
        grab_it = 0
    y_add = card_pos_dict['p_y_cord']
    # attack cards and crazy animation calculations
    for index, card in enumerate(table_at_deck):
        if card in animated_at_cards:
            continue
        # check the table animation
        if str(51 + index) not in card_anim_dict:
            card_anim_dict[str(51 + index)] = 0
        if index < len(table_def_deck):
            if mouse_lock == 51 + index:
                if 16 >= card_anim_dict[str(51 + index)]:
                    card_anim_dict[str(51 + index)] += 4
            elif card_anim_dict[str(51 + index)] > 0:
                card_anim_dict[str(51 + index)] -= 2
        else:
            card_anim_dict[str(51 + index)] = 0
        anim_add = card_anim_dict[str(51 + index)]
        x_cord = 40 + 145 * index - anim_add
        y_cord = 300 + y_add - anim_add if index % 2 == 0 else 270 + y_add - anim_add
        # throwing card off animation
        if anim_at_throw and card == anim_at_throw[0]:
            x_cord, y_cord = animation_calc('throw_at_bool', x_cord, y_cord, -200, 305,
                'throw_at', anim_at_throw, (card, 'remember_at_card'))
        # grabbing cards from table animation
        elif anim_at_player and anim_at_player[0][0] == card:
            x_add_deck = x_add_player_deck if anim_at_player[0][-1] == 1 else x_add_bot_deck
            x_cord, y_cord = animation_calc('grab_at_bool',
                x_cord, y_cord, 15 + x_add_deck * anim_at_player[0][2], 600 if anim_at_player[0][-1] == 1 else 30,
                'grab_at', anim_at_player, (card, 'remember_at_card'))
        # putting cards on the table animation
        elif anim_at_table and anim_at_table[-1][0] == card:
            table_at_start_y = 600 if anim_at_table[-1][1] == 1 else 30
            x_add_deck = x_add_player_deck if anim_at_table[-1][1] == 1 else x_add_bot_deck
            x_cord, y_cord = animation_calc('table_at_bool',
                15 + x_add_deck * anim_at_table[-1][2], table_at_start_y, 40 + 145 * anim_at_table[-1][3], y_cord,
                'table_at', anim_at_table)
        # final output
        output_card = 'empty_card' if index >= len(table_def_deck) else 'beaten_card'
        screen.blit(textures[output_card], (x_cord, y_cord))
        screen.blit(textures[card[-2:] + trump_match[card[0]]], (x_cord, y_cord))
        screen.blit(textures[card[0]], (x_cord, y_cord))
    # defence cards and crazy animation calculations
    for index, card in enumerate(table_def_deck):
        if card in animated_def_cards:
            continue
        anim_add = card_anim_dict[str(51 + index)]
        x_cord = 70 + 145 * index + anim_add
        y_cord = 340 + y_add + anim_add if index % 2 == 0 else 310 + y_add + anim_add
        # throwing card off animation
        if anim_def_throw and card == anim_def_throw[0]:
            x_cord, y_cord = animation_calc('throw_def_bool', x_cord, y_cord, -200, 305,
                'throw_def', anim_def_throw, (card, 'remember_def_card'))
        # grabbing cards from table animation
        elif anim_def_player and anim_def_player[0][0] == card:
            x_add_deck = x_add_player_deck if anim_def_player[0][-1] == 1 else x_add_bot_deck
            x_cord, y_cord = animation_calc('grab_def_bool',
                x_cord, y_cord, 15 + x_add_deck * anim_def_player[0][2], 600 if anim_def_player[0][-1] == 1 else 30,
                'grab_def', anim_def_player, (card,'remember_def_card'))
        # putting cards on the table animation
        elif anim_def_table and anim_def_table[-1][0] == card:
            table_def_start_y = 30 if anim_def_table[-1][1] == 1 else 600
            x_add_deck = x_add_bot_deck if anim_def_table[-1][1] == 1 else x_add_player_deck
            x_cord, y_cord = animation_calc('table_def_bool',
                15 + x_add_deck * anim_def_table[-1][2], table_def_start_y, 70 + 145 * anim_def_table[-1][3], y_cord,
                'table_def', anim_def_table)
        # final output
        screen.blit(textures['empty_card'], (x_cord, y_cord))
        screen.blit(textures[card[-2:] + trump_match[card[0]]], (x_cord, y_cord))
        screen.blit(textures[card[0]], (x_cord, y_cord))

    # taking cards from deck animation
    if animation_list:
        x_add_deck = x_add_player_deck if animation_list[0][0] == 'pl1' else x_add_bot_deck
        animation_calc('anim_bool',
            1140, 285, 15 + x_add_deck * animation_list[0][1] - 1, 600 if animation_list[0][0] == 'pl1' else 30,
            'deck', animation_list, (card,'take_from_deck'))

    # menu
    screen.blit(textures['pause'], (1365, 15))
    if pause_mode or menu_mode or stat_mode:
        # background
        screen.blit(textures['back_pattern'], (0, 0))
        screen.blit(textures['menu'], (415, 150))
        # buttons
        for num, menu_button in [(-3, 'menu_up'), (-4, 'menu_mid'), (-5, 'menu_down')]:
            if mouse_lock == num:
                if card_pos_dict[menu_button] < 10:
                    card_pos_dict[menu_button] += 2
            elif card_pos_dict[menu_button] > 0:
                card_pos_dict[menu_button] -= 1
        if menu_mode:
            screen.blit(*menu_button_anim('menu_up', "  play  ", "continue","", 320))
            screen.blit(*menu_button_anim('menu_mid', "  exit  ", "  menu  ","", 445))
            screen.blit(*menu_button_anim('menu_down',"  info  ", "", " return ", 570))
        elif pause_mode:
            screen.blit(*menu_button_anim('menu_up', "  play  ", "continue", "", 320))
            screen.blit(*menu_button_anim('menu_mid', "  exit  ", "  menu  ", "", 445))
        else:
            font = pygame.font.Font(resource_path("font/sans.ttf"), 30)
            text = font.render(f"Games played : {user_data['user_games']}", True, (0, 0, 0))
            screen.blit(text, (450, 320))
            text = font.render(f"Games won    : {user_data['user_wins']}", True, (0, 0, 0))
            screen.blit(text, (450, 370))
            screen.blit(*menu_button_anim('menu_down', "", "", " return ", 570))

    # if anyone wins
    win_check()
    # end of the tick
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
