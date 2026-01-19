import pygame
import random

# game part
card_deck         = []    # card deck
player1_deck      = []    # player deck
player2_deck      = []    # bot deck
table_at_deck     = []    # attack deck
table_def_deck    = []    # defence deck
animation_list    = []    # list with cards to animate(fron deck to player)
anim_to_table     = []    # list with cards to animate(fron player to table)
all_addable_cards = []    # list of cards to add when attacking (only numbers)
trump_card        = ''    # trump card
able_to_grab      = False
want_to_grab      = 0

"""Game Functions"""

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

def take_from_deck(player_deck,animation_active = True):
    """fill player deck with cards"""
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

def lowest_card(player_deck):
    lowest_player_card = 'x20'
    for cards in player_deck:
        if cards[0] == trump_card[0] and int(cards[-2:]) < int(lowest_player_card[-2:]):
            lowest_player_card = cards
    return lowest_player_card[-2:]

def who_moves_first():
    global attack_player
    if lowest_card(player1_deck) < lowest_card(player2_deck):
        attack_player = 1
    else:
        attack_player = 2

def end_screen(end_x_cord, final_text):
    """render final screen"""
    screen.fill((0, 55, 0))
    end_font = pygame.font.Font("font/pixel_font.ttf", 70)
    end_text = end_font.render(final_text, True, (0, 0, 0))
    screen.blit(end_text, (end_x_cord, 350))

def win_check():
    """check if player won and stop the game"""
    if player1_deck == [] and card_deck == []:
        end_screen(500,'You Win!')
    if player2_deck == [] and card_deck == []:
        end_screen(250,'Opponent Wins!')

def op_deck(player_deck):
    """returning the opposite deck"""
    if player_deck == player1_deck:
        return player2_deck
    else:
        return player1_deck

def player_change_at(player_deck):
    """if opponent defended himself, switching the player"""
    global table_at_deck,table_def_deck,attack_player
    # taking cards
    take_from_deck(player_deck)
    take_from_deck(op_deck(player_deck))
    # cleaning the table
    table_at_deck = []
    table_def_deck = []
    # changing the player
    if player_deck == player1_deck:
        attack_player = 2
    else:
        attack_player = 1

def player_change_def(player_deck):
    """if opponent didn't defend himself, not switching the player"""
    global table_at_deck,table_def_deck,attack_player,able_to_grab,want_to_grab
    # make player grab cards from table
    if player_deck == player1_deck:
        want_to_grab = 1
    else:
        want_to_grab = 2
    if able_to_grab:
        for card_at in table_at_deck:
            player_deck.append(card_at)
        for card_def in table_def_deck:
            player_deck.append(card_def)
        # taking cards
        take_from_deck(op_deck(player_deck))
        # cleaning the table
        table_at_deck = []
        table_def_deck = []
        able_to_grab = False
        want_to_grab = 0


def attack_button(number,player_deck):
    """Checking if attack card works"""
    if table_at_deck == [] or player_deck[number][-2:] in all_addable_cards:
        table_at_deck.append(player_deck.pop(number))
        return True
    else:
        return False

def defence_button(number,player_deck):
    """Checking if defence card works"""
    if ((int(player1_deck[number][-2:]) > int(table_at_deck[-1][-2:]) and player1_deck[number][0] == table_at_deck[-1][0])
    or (player1_deck[number][0] == trump_card[0] and table_at_deck[-1][0] != trump_card[0])):
        table_def_deck.append(player_deck.pop(number))
        return True
    else:
        return False

def all_addable_cards_calc():
    """calculating all addable cards"""
    global all_addable_cards
    all_addable_cards = []
    for cards in table_at_deck:
        all_addable_cards.append(cards[-2:])
    for cards in table_def_deck:
        all_addable_cards.append(cards[-2:])

"""Bot Brain Functions"""

def attack_calc(bot_move) -> str:
    # choosing the card
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
    # choosing the card
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
    global all_addable_cards,able_to_grab
    bot_move = []
    if player_deck == player1_deck:
        number = 1
        op_num = 2
    else:
        number = 2
        op_num = 1
    # bot attack moves !!!
    print(want_to_grab == op_num)
    if (attack_player == 2 and player_deck == player2_deck) or (attack_player == 1 and player_deck == player1_deck):
        if len(table_at_deck) == len(table_def_deck) or (want_to_grab == op_num):
            for cards in player_deck:
                if not table_at_deck or cards[-2:] in all_addable_cards:
                    bot_move.append(cards)
            if not bot_move:
                if want_to_grab == op_num:
                    able_to_grab = True
                    #time.sleep(2)
                    player_change_def(op_deck(player_deck))
                else:
                    player_change_at(player_deck)
                return
            else:
                final_move = attack_calc(bot_move)
                if final_move == "":
                    if want_to_grab == op_num:
                        able_to_grab = True
                        #time.sleep(2)
                        player_change_def(op_deck(player_deck))
                    else:
                        player_change_at(player_deck)
                    return
                else:
                    table_at_deck.append(final_move)
                    player_deck.remove(final_move)
                    return



    # bot defence moves !!!
    if (attack_player == 1 and player_deck == player2_deck) or (attack_player == 2 and player_deck == player1_deck):
        if len(table_at_deck) > len(table_def_deck):
            for cards in player_deck:
                if cards[-2:] > table_at_deck[-1][-2:] and cards[0] == table_at_deck[-1][0]:
                    bot_move.append(cards)
                if cards[0] == trump_card[0] and table_at_deck[-1][0] != trump_card[0]:
                    bot_move.append(cards)
            if not bot_move or want_to_grab == number:
                player_change_def(player_deck)
                return
            else:
                final_move = defence_calc(bot_move,player2_deck)
                if final_move == "":
                    player_change_def(player_deck)
                    return
                else:
                    table_def_deck.append(final_move)
                    player_deck.remove(final_move)
                    return

# creating decks
create_deck()
take_from_deck(player1_deck,False)
take_from_deck(player2_deck,False)

# pygame initialization
pygame.init()
screen = pygame.display.set_mode((1500, 800))
clock = pygame.time.Clock()

# textures
textures = {
    '15'          : pygame.image.load("textures/15.png").convert_alpha(),
    '14'          : pygame.image.load("textures/14.png").convert_alpha(),
    '13'          : pygame.image.load("textures/13.png").convert_alpha(),
    '12'          : pygame.image.load("textures/12.png").convert_alpha(),
    '10'          : pygame.image.load("textures/10.png").convert_alpha(),
    '09'          : pygame.image.load("textures/09.png").convert_alpha(),
    '08'          : pygame.image.load("textures/08.png").convert_alpha(),
    '07'          : pygame.image.load("textures/07.png").convert_alpha(),
    '06'          : pygame.image.load("textures/06.png").convert_alpha(),
    'h'           : pygame.image.load("textures/h.png").convert_alpha(),
    'd'           : pygame.image.load("textures/d.png").convert_alpha(),
    's'           : pygame.image.load("textures/s.png").convert_alpha(),
    'c'           : pygame.image.load("textures/c.png").convert_alpha(),
    'button'      : pygame.image.load("textures/button.png").convert_alpha(),
    'empty_card'  : pygame.image.load("textures/empty_card.png").convert_alpha(),
    'face_down'   : pygame.image.load("textures/face_down.png").convert_alpha(),
    'deck_side'   : pygame.image.load("textures/deck_side.png").convert_alpha(),
    'trump_empty' : pygame.image.load("textures/empty_card.png").convert_alpha(),
    'trump_num'   : pygame.image.load(f"textures/{trump_card[-2:]}.png").convert_alpha(),
    'trump_suit'  : pygame.image.load(f"textures/{trump_card[0]}.png").convert_alpha(),
}
# resizing
for texture in textures.keys():
    if texture != 'button':
        textures[texture] = pygame.transform.scale(textures[texture], (95, 135))
textures['trump_empty'] = pygame.transform.rotate(textures['trump_empty'], 90)
textures['trump_num'] = pygame.transform.rotate(textures['trump_num'], 90)
textures['trump_suit'] = pygame.transform.rotate(textures['trump_suit'], 90)
textures['button'] = pygame.transform.scale(textures['button'], (95, 55))

# all buttons (start x start y length x length y)
button_T = pygame.Rect(800, 340, 135, 95)
button_0 = pygame.Rect(890, 470, 95, 55)
button_1 = pygame.Rect(15, 600, 95, 135)
button_2 = pygame.Rect(120, 600, 95, 135)
button_3 = pygame.Rect(225, 600, 95, 135)
button_4 = pygame.Rect(330, 600, 95, 135)
button_5 = pygame.Rect(435, 600, 95, 135)
button_6 = pygame.Rect(540, 600, 95, 135)
button_7 = pygame.Rect(645, 600, 95, 135)
button_8 = pygame.Rect(750, 600, 95, 135)
button_9 = pygame.Rect(855, 600, 95, 135)
button_10 = pygame.Rect(960, 600, 95, 135)
button_11 = pygame.Rect(1065, 600, 95, 135)
button_12 = pygame.Rect(1170, 600, 95, 135)
all_buttons = [
    button_1, button_2, button_3, button_4,button_5,button_6,
    button_7,button_8,button_9,button_10,button_11,button_12,
]

# starting values
attack_player = 0
running = True
anim_bool = True
anim2_bool = True
animation = ''
card_pos_dict = {
    'm_size_x' : 95,
    'm_size_y' : 55,
    'm_cord_x' : 880,
    'm_cord_y' : 470,
    't_cord_x' : 800
}

# deciding who moves first
who_moves_first()
# main cycle
while running:
    # bot making a move
    all_addable_cards_calc()
    bot_brain(player2_deck)

    """ INPUT """
    # mouse on card input
    mouse_pos = pygame.mouse.get_pos()
    mouse_lock = None
    if button_0.collidepoint(mouse_pos):
        mouse_lock = -1
    elif button_T.collidepoint(mouse_pos):
        mouse_lock = -2
    for num, button in enumerate(all_buttons):
        if button.collidepoint(mouse_pos):
            mouse_lock = num
            break
    # mouse click input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # attack input
        if event.type == pygame.MOUSEBUTTONDOWN and attack_player == 1:
            if button_0.collidepoint(event.pos) and len(table_at_deck) == len(table_def_deck) >= 1:
                player_change_at(player1_deck)
            elif button_0.collidepoint(event.pos) and len(table_at_deck) > len(table_def_deck) and want_to_grab:
                able_to_grab = True
                player_change_def(player2_deck)
            for num, button in enumerate(all_buttons):
                if button.collidepoint(event.pos) and len(player1_deck) >= num + 1:
                    attack_button(num,player1_deck)
                    break
        # defence input
        elif event.type == pygame.MOUSEBUTTONDOWN and attack_player == 2 and len(table_at_deck) >= len(table_def_deck):
            if button_0.collidepoint(event.pos):
                player_change_def(player1_deck)
                print('button 0 pressed')
            for num, button in enumerate(all_buttons):
                if button.collidepoint(event.pos):
                    defence_button(num,player1_deck)
                    break

    """ OUTPUT """
    # background
    screen.fill((0, 55, 0))
    '''
    # bot cards output
    x_cord = 15
    for index, card in enumerate(player2_deck):
        index_list = 10
        for index2 in range(len(animation_list)):
            if int(animation_list[index2][1]) <= index_list and animation_list[index2][0] == 'pl2':
                index_list = animation_list[index2][1]
        if index_list == 10 or index_list > index:
            screen.blit(textures['face_down'], (x_cord, 60))
            x_cord += 105
    '''
    # op cards output for testing
    x_cord = 15
    for card in player2_deck: 
        screen.blit(textures['empty_card'], (x_cord, 60))
        screen.blit(textures[card[-2:]], (x_cord, 60))
        screen.blit(textures[card[0]], (x_cord, 60))
        x_cord += 105

    # player cards output
    x_cord = 15
    for index, card in enumerate(player1_deck):
        # Y cord calculation
        if card not in card_pos_dict:
            card_pos_dict[card] = 600
        if mouse_lock == index:
            if 570 <= card_pos_dict[card]:
                card_pos_dict[card] -= 5
        elif card_pos_dict[card] <= 595:
            card_pos_dict[card] += 5
        y_cord = card_pos_dict[card]
        index_list = 10
        # card poping up animation
        for index2 in range(len(animation_list)):
            if int(animation_list[index2][1]) <= index_list and animation_list[index2][0] == 'pl1':
                index_list = animation_list[index2][1]
        if index_list == 10 or index_list > index:
            screen.blit(textures['empty_card'], (x_cord, y_cord))
            screen.blit(textures[card[-2:]], (x_cord, y_cord))
            screen.blit(textures[card[0]], (x_cord, y_cord))
            x_cord += 105

    # table output
    p_y_cord = 0
    if want_to_grab == 1:
        p_y_cord += 100
    elif want_to_grab == 2:
        p_y_cord -= 100
    # attack cards
    x_cord = 40
    y_cord = 340 + p_y_cord
    for card in table_at_deck:
        screen.blit(textures['empty_card'], (x_cord, y_cord))
        screen.blit(textures[card[-2:]], (x_cord, y_cord))
        screen.blit(textures[card[0]], (x_cord, y_cord))
        x_cord += 125
        if y_cord == 340:
            y_cord = 310
        else: y_cord = 340
    # defence cards
    x_cord = 60
    y_cord = 360 + p_y_cord
    for card in table_def_deck:
        screen.blit(textures['empty_card'], (x_cord, y_cord))
        screen.blit(textures[card[-2:]], (x_cord, y_cord))
        screen.blit(textures[card[0]], (x_cord, y_cord))
        x_cord += 125
        if y_cord == 360:
            y_cord = 330
        else:
            y_cord = 360

    # deck output
    if card_deck != []:
        # trump card animation
        if mouse_lock == -2:
            if 770 < card_pos_dict['t_cord_x']:
                card_pos_dict['t_cord_x'] -= 4
        elif card_pos_dict['t_cord_x'] < 800:
            card_pos_dict['t_cord_x'] += 4
        x_cord = card_pos_dict['t_cord_x']
        y_cord = 340
        screen.blit(textures['trump_empty'], (x_cord, y_cord))
        screen.blit(textures['trump_suit'], (x_cord, y_cord))
        screen.blit(textures['trump_num'], (x_cord, y_cord))
        # deck output
        if len(card_deck) > 1:
            screen.blit(textures['face_down'], (890, 320))
            screen.blit(textures['deck_side'], (875, 320))
            font = pygame.font.Font("font/pixel_font.ttf", 40)
            text = font.render(str(len(card_deck)), True, (0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), (890, 365, 95, 45))
            screen.blit(text, (900, 370))
    else:
        screen.blit(textures['trump_suit'], (800, 340))

    # button to change player and it's animation
    if mouse_lock == -1:
        if card_pos_dict['m_size_x'] < 104:
            card_pos_dict['m_size_x'] += 2
            card_pos_dict['m_size_y'] += 2
            card_pos_dict['m_cord_x'] -= 1
            card_pos_dict['m_cord_y'] -= 1
    elif 96 < card_pos_dict['m_size_x']:
        card_pos_dict['m_size_x'] -= 2
        card_pos_dict['m_size_y'] -= 2
        card_pos_dict['m_cord_x'] += 1
        card_pos_dict['m_cord_y'] += 1
    x_size = card_pos_dict['m_size_x']
    y_size = card_pos_dict['m_size_y']
    x_cord = card_pos_dict['m_cord_x']
    y_cord = card_pos_dict['m_cord_y']
    textures['button'] = pygame.transform.scale(textures['button'],(x_size, y_size))
    screen.blit(textures['button'], (x_cord, y_cord))

    # taking cards from deck animation
    if animation_list:
        if anim_bool:
            animation = animation_list[0]
            anim_bool = False
            card_pos_dict['anim_x_cord'] = 890
            card_pos_dict['anim_y_cord'] = 320
    if 'anim_x_cord' in card_pos_dict:
        if card_pos_dict['anim_x_cord'] > 350:
            card_pos_dict['anim_x_cord'] -= 50
            if animation[0] == 'pl1':
                card_pos_dict['anim_y_cord'] += 25
            else:
                card_pos_dict['anim_y_cord'] -= 25
            x_cord = card_pos_dict['anim_x_cord']
            y_cord = card_pos_dict['anim_y_cord']
            screen.blit(textures['face_down'], (x_cord, y_cord))
            if not card_pos_dict['anim_x_cord'] > 350:
                del animation_list[0]
                anim_bool = True

    # putting card on the table animation
    if anim_to_table:
        if anim2_bool:
            animation = anim_to_table[0]
            anim2_bool = False


    # if anyone wins
    win_check()
    # end of the tick
    pygame.display.flip()
    clock.tick(60)