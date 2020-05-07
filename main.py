'''         in the name of god
This program is an electrical circuit simulator.
This project has started on January 10, 2019 (10/1/2019 AD)
Authors : Ali Mozdian Fard (Back-end)
          Pooya Shams K (Front-end)
'''

# imports
import pygame, sys, json, os
pygame.init()
os.environ ["SDL_VIDEO_CENTERED"] = "1"

#default varaibles

PG_BREAD_BOARD_WINW = 864 # bread board window width
PG_BREAD_BOARD_WINH = 234 # bread board window height
PG_WINW = PG_BREAD_BOARD_WINW + 384 + 100 # pygame window width
PG_WINH = PG_BREAD_BOARD_WINH + 192 # pygame window height
pg_ls_point_poses  = []
pg_ls_button_rects = []
pg_ls_button_texts = []
pg_ls_color_rects  = []
pg_ls_printed      = [None] * 10
all_IC_codes = {"not":"7404", "and":"7408", "or":"7432", "xor":"7486", "xnor":"4077", "nor":"7402", "nand":"7400"}

#           R    G    B
WHITE   = (255, 255, 255)
BLACK   = ( 0 ,  0 ,  0 )
RED     = (255,  0 ,  0 )
GREEN   = ( 0 , 255,  0 )
BLUE    = ( 0 ,  0 , 255)
CYAN    = ( 0 , 255, 255)
MAGENTA = (255,  0 , 255)
YELLOW  = (255, 255,  0 )
GRAY    = (128, 128, 128)

BG_COLOR = WHITE
PG_BUTTON_BG_COLOR = BLACK
PG_BUTTON_FG_COLOR = CYAN
PG_WIRE_COLOR = GRAY
PG_PRINT_FG_COLOR = WHITE
PG_PRINT_BG_COLOR = BLACK
pg_ls_all_colors = [
[RED, GREEN, BLUE],
[CYAN, MAGENTA, YELLOW],
[BLACK, GRAY, WHITE]]

a, f = 0, 0
b, g = 1, 1
c, h = 2, 2
d, i = 3, 3
e, j = 4, 4

#making database(bread board):
#making margin bread board
VOLTAGE = 1
ls_up_posi = [VOLTAGE] * 50
ls_up_nega = [0] * 50
ls_down_posi = [None] * 50
ls_down_nega = [None] * 50
ls_margin_up = [ls_up_nega, ls_up_posi]
ls_margin_down = [ls_down_nega, ls_down_posi]

#making main bread board
ls_main_up = []
for i in range(64):
    ls_main_up.append([None]*5)
ls_main_down = []
for i in range(64):
    ls_main_down.append([None]*5)
ls_main = [ls_main_up, ls_main_down]
database = [ls_margin_up, ls_main, ls_margin_down]
#end

# LED
ls_LED = []

# Wires
ls_wire = []

# ICs
ls_IC = []

# Command
COMMANDS = []

#start defining functions:
def sync(ls):
    '''
    This function coordinates the list components,
    and return the new list.
    '''
    global VOLTAGE
    if VOLTAGE in ls and 0 in ls:
        pg_print(":( short connect :(")
        VOLTAGE = 0
    else:
        for item in range(len(ls)):
            if ls[item] == VOLTAGE:
                for i in range(len(ls)):
                    ls[i] = VOLTAGE
                break
            elif ls[item] == 0:
                for i in range(len(ls)):
                    ls[i] = 0
                break
    return ls


def detector(A, AB="A"):
    A_pos = A[0]
    A_leter = A[1]
    A_number = int(A[2:])-1
    A_pointer = database
    if A_pos != "m":
        if A_pos == "u":
            A_pointer = ls_margin_up
            if A_leter == "+":
                A_pointer = ls_up_posi
            elif A_leter == "-":
                A_pointer = ls_up_nega
        elif A_pos == "d":
            A_pointer = ls_margin_down
            if A_leter == "+":
                A_pointer = ls_down_posi
            elif A_leter == "-":
                A_pointer = ls_down_nega
        if AB == "A":
            A_address = "A_pointer["+str(A_number)+"]"
        elif AB == "B":
            A_address = "B_pointer["+str(A_number)+"]"
    elif A_pos == "m":
        A_pointer = ls_main
        if A_leter in 'abcde':
            A_pointer = ls_main_up
        elif A_leter in 'fghij':
            A_pointer = ls_main_down
        A_pointer = A_pointer[A_number]
        A_leter = str(eval(A_leter))
        if AB == "A":
            A_address = "A_pointer["+A_leter+"]"
        elif AB == "B":
            A_address = "B_pointer["+A_leter+"]"
    return A_pointer, A_address

# wire
def Connect_wire(A, B, color, wire_new):
    global database
    #A
    A_pointer, A_address = detector(A, "A")
    #B
    B_pointer, B_address = detector(B, "B")
    #sync & eval defined
    AB_ls = eval('['+A_address+', '+B_address+']')
    A_content, B_content = sync(AB_ls)
    exec(A_address+' = A_content')
    exec(B_address+' = B_content')
    if wire_new:
        ls_wire.append([A, B, color])
    else:
        return A_pointer, B_pointer

# LED
def make_LED(anode, cathode, color, rv):# rv : required_voltage
    ls_LED.append([anode, cathode, color, rv])

#check functions

def check_OnOff_LED(anode, cathode, rv):# required_voltage
    '''
    This function checks whether the lamp is lit or not.
    If lamp has to be on, return True
    else, return False
    '''
    A_pointer, A_address = detector(anode, "A")
    B_pointer, B_address = detector(cathode, "B")
    anode = eval(A_address)
    cathode = eval(B_address)
    if anode == None or cathode == None:
        return "OFF"
    difference_voltage = anode - cathode
    if difference_voltage < rv:
        return "OFF"
    elif rv <= difference_voltage < float(rv)+.5:
        return "ON"
    elif float(rv)+.5 <= difference_voltage < rv+1:
        return "BURNED"
    elif difference_voltage >= rv+1:
        return "EXPLODED"


def check_OnOff_IC(Vcc, GND):
    A_pointer, A_address = detector(Vcc, "A")
    B_pointer, B_address = detector(GND, "B")
    Vcc = eval(A_address)
    GND = eval(B_address)
    if Vcc != None and GND != None and Vcc-GND >= 5:
        return True
    return False


def check_LED():
    if len(ls_LED) > 0:
        pg_print("press any key to go to next LED")
        pg_print("num | \t", "con | \t", "anode | \t", "cathode | \t", "color | \t", "required_voltage")
        pg_getch()
        for i, (A, C, c, rv) in enumerate(ls_LED):
            condition = check_OnOff_LED(A, C, rv)
            pg_print(i+1, "\t\t",condition, "\t\t", A, "\t\t", C, "\t", c, "\t\t", rv)
            pg_getch()


def check_wire():
    """ outputs all of wires in the board """
    if len(ls_wire) > 0:
        pg_print("press any key to go to next wire")
        pg_print("num  " + (" ")*len(str(len(ls_wire))) + " : " + "\t" + "A" + "\t" + "B")
        i = 0
        for A, C, color in ls_wire:
            i += 1
            pg_print("wire "+str(i)+" : "+"\t"+A+(" "*(8-(len(A))+3))+C)
            pg_getch()


def check_IC():
    """ checks all ICs"""
    global ls_IC
    if len(ls_IC) > 0:
        pg_print("press any key to go to next IC")
        pg_print("num | \t", "Vcc | \t", "con | \t", "code | \t")
        pg_getch()
        for i, IC in enumerate(ls_IC):
            Vcc = IC[14]
            GND = IC[7]
            pg_print(i+1, "\t\t", Vcc, "\t", check_OnOff_IC(Vcc, GND), "\t", IC[0])
            pg_getch()

def check_point(A):
    A_pointer, A_address = detector(A)
    return eval(A_address)


# save & open function

def save(name):
    dct = {"LED": ls_LED, "wire": ls_wire, "IC": ls_IC, "commands": COMMANDS, "voltage": VOLTAGE}
    name += '.dgb'
    with open(name, 'w') as s:
        s.write(json.dumps(dct, indent=2))
    del dct

def open_file(name):
    global ls_wire, ls_LED, ls_IC, COMMANDS, VOLTAGE
    name += '.dgb'
    with open(name, 'r') as o:
        dct = json.loads(o.read())
    ls_LED = dct["LED"]
    ls_wire = dct["wire"]
    ls_IC = dct["IC"]
    COMMANDS = dct["commands"]
    VOLTAGE = dct["voltage"]
    del dct

# ctrl+Z
def del_item(i=-1):
    global COMMANDS, ls_LED, ls_wire, ls_IC
    if COMMANDS[i] in ls_LED:
        i2 = ls_LED.index(COMMANDS[i])
        if ls_LED[i2] == COMMANDS[i]:
            COMMANDS.pop(i)
            ls_LED.pop(i2)
    elif COMMANDS[i] in ls_wire:
        i2 = ls_wire.index(COMMANDS[i])
        if ls_wire[i2] == COMMANDS[i]:
            COMMANDS.pop(i)
            ls_wire.pop(i2)
    elif COMMANDS[i] in ls_IC:
        i2 = ls_IC.index(COMMANDS[i])
        if ls_IC[i2] == COMMANDS[i]:
            COMMANDS.pop(i)
            ls_IC.pop(i2)


# restart
def make_defaults(A, B, color):
    Connect_wire(A, B, color, True)
    COMMANDS.append(ls_wire[-1])
    refresh()

def restart():
    global ls_LED, ls_wire, ls_IC, COMMANDS, VOLTAGE
    ls_LED = []
    ls_wire = []
    ls_IC = []
    COMMANDS = []
    VOLTAGE = 1
    pg_clear()
    pg_print("\t\tWelcome to digi-board!\n\n")
    make_defaults("u+50", "d+50", RED)
    make_defaults("u-50", "d-50", BLUE)

# IC
def make_IC(p_vcc, code):
    global ls_IC
    ls = [code]
    n = int(p_vcc[2:])
    for i in range(7):
        ls.append('mf'+str(n+i))
    for i in range(6, -1, -1):
        ls.append('me'+str(n+i))
    ls_IC.append(ls)


# main gates
def gate_and(A, B):
    return A and B

def gate_not(A):
    if A == None:
        return None
    if A == 0:
        return VOLTAGE
    return 0

def gate_or(A, B):
    if A == None or B == None:
        return None
    return A or B


# gates
def gt_7408(A, B):
    A_pointer, A_address = detector(A, "A")
    B_pointer, B_address = detector(B, "B")
    A = eval(A_address)
    B = eval(B_address)
    return gate_and(A, B)

def gt_7404(A):
    A_pointer, A_address = detector(A, "A")
    A = eval(A_address)
    return gate_not(A)

def gt_7432(A, B):
    A_pointer, A_address = detector(A, "A")
    B_pointer, B_address = detector(B, "B")
    A = eval(A_address)
    B = eval(B_address)
    return gate_or(A, B)

def gt_7400(A, B):
    return gate_not(gt_7408(A, B))

def gt_7402(A, B):
    return gate_not(gt_7432(A, B))

def gt_7486(A, B):
    A_pointer, A_address = detector(A, "A")
    B_pointer, B_address = detector(B, "B")
    A = eval(A_address)
    B = eval(B_address)
    return gate_or(gate_and(gate_not(A), B), gate_and(A, gate_not(B)))

def gt_4077(A, B):
    return gate_not(gt_7486(A, B))


def ic_not(ls):
    A_pointer, A_address = detector(ls[7], "A")
    B_pointer, B_address = detector(ls[14], "B")
    GND = eval(A_address)
    Vcc = eval(B_address)
    if Vcc == None or GND == None:
        return
    if Vcc - GND >= 5:
        for i in range(1, 6, 2):
            A_pointer, A_address = detector(ls[i+1])
            exec(A_address+' = gt_7404(ls['+str(i)+'])')
        for i in range(13, 8, -2):
            A_pointer, A_address = detector(ls[i-1])
            exec(A_address+' = gt_7404(ls['+str(i)+'])')

def ic_no_not(ls):
    A_pointer, A_address = detector(ls[7], "A")
    B_pointer, B_address = detector(ls[14], "B")
    GND = eval(A_address)
    Vcc = eval(B_address)
    if Vcc == None or GND == None:
        return
    if Vcc - GND >= 5:
        A_pointer, A_address = detector(ls[3])
        exec(A_address+'= gt_'+ls[0]+'(ls[1], ls[2])')
        A_pointer, A_address = detector(ls[6])
        exec(A_address+'= gt_'+ls[0]+'(ls[4], ls[5])')
        A_pointer, A_address = detector(ls[8])
        exec(A_address+'= gt_'+ls[0]+'(ls[10], ls[9])')
        A_pointer, A_address = detector(ls[11])
        exec(A_address+'= gt_'+ls[0]+'(ls[13], ls[12])')


# refresh
def refresh_ICs():
    global ls_IC
    for i in ls_IC:
        if i[0] != "7404":
            ic_no_not(i)
        else:
            ic_not(i)

def pg_refresh():
    pygame.display.update()

def empty_board():
    for i in range(64):
        ls_main_up[i] = [None] * 5
        ls_main_down[i] = [None] * 5
    for i in range(50):
        ls_up_posi[i] = VOLTAGE
    # margin down
    for i in range(2):
        for j in range(50):
            database[2][i][j] = None

def refresh_wires():
    for ii in range(len(ls_wire)):
        for A, B, color in ls_wire:
            ls_A, ls_B = Connect_wire(A, B, color, False)
            ls_A[:] = sync(ls_A)
            ls_B[:] = sync(ls_B)
        for i in range(64):
            ls_main_up[i] = sync(ls_main_up[i])
            ls_main_down[i] = sync(ls_main_down[i])
        ls_down_posi[:] = sync(ls_down_posi)
        ls_down_nega[:] = sync(ls_down_nega)

def refresh():
    empty_board()
    for i in range(len(ls_IC)):
        refresh_wires()
        refresh_ICs()
    refresh_wires()
    pg_refresh()

# guide function
def guide():
    pg_print(''' WELCOME TO DIGI-BOARD GUIDE
    press any key to go to next tip.''')
    pg_getch()
    pg_print(" 1- voltage (number): This tool can change the voltage of bread board")
    pg_getch()
    pg_print(''' 2- planting tools:
    2.1- LED: This tool can plant a LED on your bread board
    2.2- wire: This tool can connect a wire on your bread board''')
    pg_getch()
    pg_print(''' 3- check tools:
    3.1- check voltage: This tool says how much is the voltage in your bread board.(measured in volt)
    3.2- check LED: This tool says about all of LED.
    (anodes pos, cathodes pos, color, required voltage)
    3.3- check wire: This tool says about anodes' & cathods' pos of all of wire.
    3.4- check (point): This tool says about the points content.''')
    pg_getch()
    pg_print(''' 4- system tools:
    4.1- screenshot: This tool can take a picture.
    4.2- save: This tool can save your new board.
    4.3- open: This tool can open your saved board.
    4.4- rename: This tool can change name of your new board''')
    pg_getch()
    pg_print(''' 5- deleting tools:
    5.1- z: This tool's mean 'Ctrl+Z'.
    5.2- del: This tool can delete an item. (like LED or wire)
    5.3- restart: This tool can restart your board & delete all of your LEDs and wires''')
    pg_getch()
    pg_print(" 6- refresh: This tool refreshs your board.")
    pg_getch()
    pg_print(" 7- clear: This tool can clear the terminal")
    pg_getch()
    pg_print(" 8- guide: this tool can declare to you, the tools")
    pg_getch()
    pg_print(" 9- quit: This tool closes your board.")
    pg_getch()
    pg_print("10- cod: This tool is just for debugging the programme by programmers of digi-board (Ali & Pooya)")
    pg_getch()

#### graphical functions ----------------------------------------------------------------------------------------------------
#### main window
def pg_surface():
    """ makes the pygame surface """
    global DISPLAYSURF
    DISPLAYSURF = pygame.display.set_mode((PG_WINW, PG_WINH))
    pygame.display.set_caption("digi-board")
    icon = pygame.image.load('digi-board.png')
    pygame.display.set_icon(icon)
    DISPLAYSURF.fill(BG_COLOR)

## helping functions
# writing on Surfaces
def pg_write(win, text, pos = (0, 0), file="freesanasbold.ttf", size=32, antialiased=True, bg_color=None, fg_color=(255, 255, 255), side="center"):
    """ writes with pygame in a particular point of surface"""
    fontobj = pygame.font.SysFont(file, size)
    textsurface = fontobj.render(text, antialiased, fg_color, bg_color)
    textrect = textsurface.get_rect()
    if side == "center":
        textrect.center = pos
    elif side == "topleft":
        textrect.topleft = pos
    win.blit(textsurface, textrect)

# cropping surface
def pg_cut_rect_from_surface(surface, rect):
    return surface.subsurface(rect)

# distance
def pg_distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**.5

# onRect
def pg_on_rect(rect, x, y):
    """ checks if one position is on one rect or not"""
    if rect[0] < x < rect[0]+rect[2] and rect[1] < y < rect[1]+rect[3]:
        return True
    return False

def pg_on_circle(x1, y1, x2, y2, r):
    """ checks if one point is on one circle or not """
    if pg_distance(x1, y1, x2, y2) < r:
        return True
    return False

# on line
def pg_on_line(ap, bp, cp, er=3):
    x1, y1 = ap
    x2, y2 = bp
    x3, y3 = cp
    bx, kx = max(x1, x2), min(x1, x2)
    by, ky = max(y1, y2), min(y1, y2)
    if kx <= x3 <= bx and ky <= y3 <= by:
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            if abs(x1-x3)<er:
                return True
            return False
        elif dy == 0:
            if abs(y1-y3)<er:
                return True
            return False
        else:
            m = dy / dx
        b = y1 - m * x1
        y = m*x3+b
        if abs(y-y3) < er:
            return True
    return False

# float -> int
def pg_float_int(f):
    """ returns int(f) if possible """
    if f%1 == 0:
        return int(f)
    return f

# decrease color
def pg_decrease_color(color):
    """ decrease the colors brightness """
    r, g, b = color
    color = [r, g, b]
    for i in range(len(color)):
        if color[i] < 120:
            color[i] = 0
            continue
        color[i] -= 100
    return tuple(color)

# change the name
def pg_change_name(name):
    pygame.display.set_caption('digi-board: ' + name)

### Making listes
## point poses
def pg_Make_point_poses():
    """ makes an empty list of points poses in the
    pygame surface to be filled later in other functions
    (and also global the list)"""
    global pg_ls_point_poses
    pg_ls_up_posi = [None] * 50
    pg_ls_up_nega = [None] * 50
    pg_ls_down_posi = [None] * 50
    pg_ls_down_nega = [None] * 50
    pg_ls_margin_up = [pg_ls_up_posi, pg_ls_up_nega]
    pg_ls_margin_down = [pg_ls_down_posi, pg_ls_down_nega]
    pg_ls_main_up = []
    for i in range(64):
        pg_ls_main_up.append([None]*5)
    pg_ls_main_down = []
    for i in range(64):
        pg_ls_main_down.append([None]*5)
    pg_ls_main = [pg_ls_main_up, pg_ls_main_down]
    pg_ls_point_poses = [pg_ls_margin_up, pg_ls_main, pg_ls_margin_down]

## buttons texts
def pg_Make_button_texts():
    global pg_ls_button_texts
    pg_ls_button_texts = [
    ["voltage"],
    ["wire", "LED", ],
    ["not", "and", "or", "xor", "xnor", "nor", "nand"],
    ["check:", "voltage", "LED", "wire", "IC", "point"],
    ["screenshot", "save", "open", "rename"],
    ["button background color", "button foreground color"],
    ["terminal background color", "terminal foreground color"],
    ["undo", "delete", "restart"],
    ["refresh", "clear"],
    ["help", "credits", "quit"]]
    return pg_ls_button_texts

## buttons rects
def pg_Make_button_rects():
    global pg_ls_button_rects
    texts = pg_Make_button_texts()
    for i in texts:
        pg_ls_button_rects.append([None]*len(i))
    return pg_ls_button_rects

## color rects
def pg_Make_color_rects():
    global pg_ls_color_rects, pg_ls_all_colors
    for i in pg_ls_all_colors:
        pg_ls_color_rects.append([None]*len(i))
    return pg_ls_color_rects

### drawing main parts on the window
## printed texts
def pg_print(*value, sep=" ", end="\n", length=10):
    """ uses a little space to write the printed things"""
    global pg_ls_printed
    text = ""
    for t in value:
        text += str(t) + sep
    text += end
    text = text.replace("\t", "        ")
    text = text.split("\n")
    pg_ls_printed.extend(text)
    if len(pg_ls_printed) > length:
        pg_ls_printed = pg_ls_printed [-length-1:-1]
    pg_draw_printed(DISPLAYSURF, 0, PG_BREAD_BOARD_WINH, PG_BREAD_BOARD_WINW, PG_WINH, None, PG_PRINT_FG_COLOR)
    pygame.display.update()
    return pg_ls_printed

def pg_draw_printed(win, x, y, width, height, bg, fg):
    """ draws all printed text in the window """
    global pg_ls_printed
    m = len(pg_ls_printed)
    w = width - x - 8
    h = (height - y) // m
    win.fill(PG_PRINT_BG_COLOR, (x, y, width-x, height-y))
    def write_nth_line(win, x, y, w, h, bg, fg, n, m, text):
        """ writes the text in the nth line of m ones """
        x += 4
        y += 4 + h*n
        pg_write(win, text, pos=(x, y), size=25, bg_color=bg, fg_color=fg, side="topleft")
    for i, text in enumerate(pg_ls_printed):
        write_nth_line(win, x, y, w, h, bg, fg, i, m, text)

def pg_clear(length=10):
    global pg_ls_printed
    pg_ls_printed = [""] * length

## buttons
def pg_draw_buttons (win, x, y, width, height, first=False):
    """ this function ``just`` draws the buttons on 
    the right side of the bread board """
    global pg_ls_button_texts
    def n_rect_write(win, x, y, width, height, n, m, l, lis, bg, fg):
        """ draws n rects in the m th row of 
        l ones and writes the lis on them"""
        w = (width - x) // n
        h = height // l
        y += (h+1)*m
        for i in range(n):
            xx = x+((w+1)*i)
            r = (xx, y, w-2, h)
            pygame.draw.rect(win, bg, r)
            pg_write(win, lis[i], pos=(xx+w//2, y+h//2), size=24, antialiased=False, fg_color=fg)
            if first:
                pg_ls_button_rects [m][i] = r

    ll = len(pg_ls_button_texts)
    for i in range(ll):
        n_rect_write(win, x, y, width, height, len(pg_ls_button_texts[i]), i,
                     ll, pg_ls_button_texts[i], PG_BUTTON_BG_COLOR,
                     PG_BUTTON_FG_COLOR)

## colors pool ;p
def pg_draw_color_pool(win, x, y, width, height, first=False):
    """ draws the colors pool in a specific rect """
    global pg_ls_all_colors, pg_ls_color_rects
    width, height = width-x, height-y
    def n_rect(win, x, y, width, height, n, m,colorlis, first=first):
        """ draws the nth line of m lines of rects of color """
        ll = len(colorlis)
        w = (width-8) // ll
        h = (height-8-2*m) // m
        y += 4 + (h+2)*n
        x += 4 - (2+w)
        for i in range(ll):
            x += 2+w
            r = (x, y, w, h)
            pygame.draw.rect(win, colorlis[i], r)
            pygame.draw.rect(win, BLACK, r, 2)
            if first:
                pg_ls_color_rects[n][i] = r
    #
    ll = len(pg_ls_all_colors)
    for i, lis in enumerate(pg_ls_all_colors):
        n_rect(win, x, y, width, height, i, ll, lis)

## LEDs
def pg_draw_LEDs(win):
    for LED in ls_LED:
        color = LED[2]
        condition = check_OnOff_LED(*LED[:2], LED[3])
        if condition == "OFF":
            color = pg_decrease_color(color)
        elif condition == "BURNED":
            color = BLACK
        elif condition == "EXPLODED":
            color = (127, 127, 127)
        x1, y1 = pg_point_pos(LED[0])
        x2, y2 = pg_point_pos(LED[1])
        x1, y1 = x1+4, y1+4
        x2, y2 = x2+4, y2+4
        pos = x1+(x2-x1)//2, y1+(y2-y1)//2
        pygame.draw.line(win, color, (x1, y1), (x2, y2), 2)
        pygame.draw.circle(win, color, pos, 10)

## wires
# one wire
def pg_draw_wire(win, A, B, color):
    """ draws one given wire between two points (A, B)"""
    A, B = map(pg_point_pos, (A, B))
    A = A[0]+4, A[1]+4
    B = B[0]+4, B[1]+4
    pygame.draw.line(win, color, A, B, 2)
# all wires
def pg_draw_wires(win):
    """ draws all of the wires in the board """
    for A, B, color in ls_wire:
        pg_draw_wire(win, A, B, color)
        Connect_wire(A, B, color, False)

## IC
# one
def pg_draw_IC(win, IC):
    """ draws one ic """
    p_GND = IC[14]
    code = IC[0]
    x, y = pg_point_pos(p_GND)
    w = 12*7
    h = 13
    rect = (x, y+5+8, w-4, h)
    pygame.draw.rect(win, BLACK, rect)
    pg_write(win, code, (rect[0]+rect[2]//2, rect[1]+rect[3]//2), size=16, antialiased=True, fg_color=WHITE, side="center")
    #pygame.draw.arc(win, RED, (x, y+5+8 + 2, 8, 8), 180, 270)
    for i in range(1, 8):
        xi, yi = pg_point_pos(IC[i])
        pygame.draw.line(win, GRAY, (xi+4, yi+4), (xi+4, yi-4))
    for i in range(8, 15):
        xi, yi = pg_point_pos(IC[i])
        pygame.draw.line(win, GRAY, (xi+4, yi+4), (xi+4, yi+4+8))

# all
def pg_draw_ICs(win):
    """ draws all ICs """
    for i in range(len(ls_IC)):
        pg_draw_IC(win, ls_IC[i])

## bread board
def pg_draw_board(win, width=PG_BREAD_BOARD_WINW, height=PG_BREAD_BOARD_WINH, first=False):
    """ draws the board on pygame surface """
    #    dot_width = 8
    #    dot_gap = 4
    #    width_max_dots = 64
    #    width_min_dots = 50
    #    height_dots = 14
    ##########################
    # to be changed basicly
    ##########################
    global pg_ls_point_poses
    pygame.draw.rect(win, BLACK, (4, 4, width-8, height-8), 2)
    def pg_margin(x, y, cycle, first=first):
        for i in range(2):
            for j in range(10):
                for k in range(5):
                    color = BLACK
                    dot = database[cycle][i][j*5+k]
                    if dot == VOLTAGE:
                        color = RED
                    elif dot == 0:
                        color = BLUE
                    if cycle == 0 and j==0 and k == 0:
                        color = BLACK
                        xx, yy = ((j * 6 + k) * 12) + x, i * 12 + y
                        pygame.draw.line(win, color, (xx, yy+4), (6, yy+4))
                    xx, yy = ((j*6+k)*12)+x, i*12+y
                    pygame.draw.rect(win, color, (xx, yy, 8, 8))
                    if first:
                        pg_ls_point_poses[cycle][i][j*5+k] = (xx, yy)


    def pg_main(x, y, lis, cycle, first=first):
        for i in range(64):
            for j in range(5):
                if i == 0:
                    pg_write(win, lis[j], pos=(i*12+x-6, j*12+y+4), size=16, fg_color=BLACK)
                if cycle == 0 and j == 0 and ((i+1)%5 == 0 or i == 0 or i == 63):
                    pg_write(win, str(i+1), pos=(i*12+x+4, j*12+y-4), size=16, fg_color=BLACK)
                if cycle == 1 and j == 4 and ((i+1)%5 == 0 or i == 0 or i == 63):
                    pg_write(win, str(i+1), pos=(i*12+x+4, j*12+y+14), size=16, fg_color=BLACK)
                p = database[1][cycle][i][j]
                color = BLACK
                if p == VOLTAGE:
                    color = RED
                elif p == 0:
                    color = BLUE
                elif p == None:
                    color = BLACK
                pygame.draw.rect(win, color, (i*12+x, j*12+y, 8, 8))
                if first:
                    pg_ls_point_poses[1][cycle][i][j] = (i*12+x, j*12+y,)

    pg_margin((width-696)//2, 8, 0)
    pg_margin((width-696)//2, height-(8+20), 2)
    pg_main((width-768)//2, 24+8+16 , "abcde", 0)
    pg_main((width-768)//2, height-(24+8+16 + 60), "fghij", 1)
    pg_draw_LEDs(win)
    pg_draw_wires(win)
    pg_draw_ICs(win)

### inputting and helping in input functions

## help
# point
def pg_point_pos_index(A):
    A_pos = A[0].lower()
    A_letter = A[1].lower()
    A_number = int(A[2:])-1
    pos = "umd".index(A_pos)
    letter = A_letter
    num = A_number
    if A_pos == "m":
        if letter in "abcde":
            return pos, 0, num, "abcde".index(letter)
        elif letter in "fghij":
            return pos, 1, num, "fghij".index(letter)
    elif A_pos in "ud":
        if letter in "-+":
            return pos, "-+".index(letter), num

def pg_point_pos(A):
    global pg_ls_point_poses
    A_pos = A[0]
    if A_pos == "m":
        a, b, c, d = pg_point_pos_index(A)
        return pg_ls_point_poses [a][b][c][d]
    elif A_pos in "ud":
        a, b, c = pg_point_pos_index(A)
        return pg_ls_point_poses[a][b][c]

def pg_convert_index_to_board_language(indexes):
    if indexes == None:
        return None
    A_pos = "umd"[indexes[0]]
    if A_pos == "m":
        A_letter = "abcdefghij"[indexes[3]+(indexes[1]*5)]
        A_num = indexes[2]
    else:
        A_letter = "-+"[indexes[1]]
        A_num = indexes[2]
    return A_pos+A_letter+str(A_num+1)

def pg_clicked_point_index(pos):
    """ checks if a clicked point in the surface is
    a point in the board or not.
    and if so, it returns the adress by the indexes """
    x, y = pos
    for m in [pg_ls_point_poses[0], pg_ls_point_poses[2]]: # m is the margin
        for q in m: # q is the positive or negative part of margins
            for p in q: # p is the position
                if pg_on_rect(tuple(p)+(8, 8), x, y):
                    return [pg_ls_point_poses[0], None, pg_ls_point_poses[2]].index(m), m.index(q), q.index(p)
    for s in pg_ls_point_poses[1]: # s is the side in main (main_up or main_down)
        for row in s: # row has 64 cases
            for p in row:
                if pg_on_rect(tuple(p)+(8, 8), x, y):
                    return 1, pg_ls_point_poses[1].index(s), s.index(row), row.index(p)
    return None # returns None if the clicked point is not on the points on the surface

## get
# clicked point
def pg_get_clicked_point():
    """ returns the pygame clicked point pos """
    global pg_ls_button_rects
    while True:
        pg_reset_screen()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                return e.pos

# button
def pg_get_button(pos):
    """ this function checks if one
    clicked point is button or not 
    and returns the button"""
    global pg_ls_button_rects
    global pg_ls_button_texts
    for i, row in enumerate(pg_ls_button_rects):
        for j, rect in enumerate(row):
            if pg_on_rect(rect, *pos):
                if i == 3:
                    if pg_ls_button_texts[i][j] != "check:":
                        return "check "+ pg_ls_button_texts[i][j]
                    return "check"
                return pg_ls_button_texts[i][j]
    return None # returns None if the clicked point is not a button

# color
def pg_get_color(pos):
    """ gets the given color by pos returns
    None if there is no color clicked """
    global pg_ls_all_colors, pg_ls_color_rects
    for i, row in enumerate(pg_ls_color_rects):
        for j , rect in enumerate(row):
            if pg_on_rect(rect, *pos):
                return pg_ls_all_colors[i][j]
    return None # so there is no color clicked

# string inputting
def pg_get_str_input(default_text=""):
    """ catches everything that user writes and yields it """
    answer = default_text
    yield answer
    answer = pg_getch()
    if answer == "\r":
        return answer
    yield answer
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                u = e.unicode
                if u == "\r":
                    return answer
                elif u == "\b":
                    answer = answer[:-1]
                    yield answer
                else:
                    answer += u
                    yield answer

# integer inputting
def pg_get_int_input(default_text="0"):
    """ catches every number that user writes and yields it """
    nums = "1234567890"
    if default_text.isnumeric():
        answer = default_text
    else:
        answer = "0"
    yield answer
    answer = pg_getnumch()
    if answer == "\r":
        return answer
    yield answer
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                u = e.unicode
                if u == "\r":
                    return answer
                elif u == "\b":
                    answer = answer[:-1]
                    yield answer
                elif u in nums:
                    answer += u
                    yield answer

# float(decimal) inputting
def pg_get_float_input(default_text="0.0"):
    """ catches every number or '.' that user writes and yields it """
    nums = "1234567890."
    if default_text.isdecimal():
        answer = default_text
    else:
        answer = "0.0"
    yield answer
    answer = pg_getfloatch(True)
    if answer == "\r":
        return answer
    elif answer == ".":
        answer = "0."
    yield answer
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                u = e.unicode
                if u == "\r":
                    return answer
                elif u == "\b":
                    answer = answer[:-1]
                    yield answer
                elif u in nums:
                    if u != "." or (u == "." and answer.count(".") == 0):
                        answer += u
                    yield answer


def pg_get_item(pos):
    """ returns the clicked item """
    for i, wire in enumerate(ls_wire):
        p1 = pg_point_pos(wire[0])
        p2 = pg_point_pos(wire[1])
        p1 = p1[0]+4, p1[1]+4
        p2 = p2[0]+4, p2[1]+4
        if pg_on_line(p1, p2, pos):
            if  i > 1:
                return "wire", i
    for i, LED in enumerate(ls_LED):
        x1, y1 = pg_point_pos(LED[0])
        x2, y2 = pg_point_pos(LED[1])
        x1, y1 = x1+4, y1+4
        x2, y2 = x2+4, y2+4
        x3, y3 = (x1+x2)//2, (y1+y2)//2
        if pg_on_line((x1, y1), (x2, y2), pos) or pg_on_circle(x3, y3, pos[0], pos[1], 10):
            return "LED", i
    for i, IC in enumerate(ls_IC):
        x, y = pg_point_pos(IC[14])
        rect = (x, y, 12*7-4, 12*2)
        if pg_on_rect(rect, x, y):
            return "IC", i
    return None  # returns None if there is no wire clicked

# wire
def pg_input_item():
    global COMMANDS, ls_wire, ls_LED
    item = pg_get_item(pg_get_clicked_point())
    pg_print("the items index is :", item)
    while item == None:
        item = pg_get_item(pg_get_clicked_point())
        pg_print("the items index is :", item)
    if item[0] == "wire":
        return COMMANDS.index(ls_wire[item[1]])
    elif item[0] == "LED":
        return COMMANDS.index(ls_LED[item[1]])
    elif item[0] == "IC":
        return COMMANDS.index(ls_IC[item[1]])

# getch (c++ function found in python's msvcrt module)
def pg_getch():
    """ catches the first key pressed by user and returns it """
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                return e.unicode

# get num ch (getch just for numbers)
def pg_getnumch():
    """ catches the first number pressed and returns """
    nums = "1234567890\r"
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                u = e.unicode
                if u in nums:
                    return u

# get decimal ch (getch for float)
def pg_getfloatch(dotallowed=False):
    """ catches the first decimal number pressed and returns """
    numsp = ".1234567890\r"
    nums  = "1234567890\r"
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                u = e.unicode
                if u in numsp:
                    if u == "." and dotallowed or u in nums:
                        return u

## input
# point
def pg_check_clicked_point(pos):
    """ checks the clicked pos and returns the position in
    board language or returns None if the pos is empty"""
    return pg_convert_index_to_board_language(pg_clicked_point_index(pos))


def pg_input_point():
    A = pg_check_clicked_point(pg_get_clicked_point())
    while A == None:
        A = pg_check_clicked_point(pg_get_clicked_point())
    return A

# button
def pg_input_button():
    button = pg_get_button(pg_get_clicked_point())
    while button == None:
        button = pg_get_button(pg_get_clicked_point())
    return button

# color
def pg_input_color():
    color = pg_get_color(pg_get_clicked_point())
    while color == None:
        color = pg_get_color(pg_get_clicked_point())
    return color

# string inputting
def pg_str_input(prompt="", default_text=""):
    """ inputs a string """
    global pg_ls_printed
    pg_print(prompt)
    pg_print(default_text)
    for answer in pg_get_str_input(default_text):
        pg_ls_printed.pop()
        pg_print(answer)
    return answer

# integer inputting
def pg_int_input(prompt="", default_text="0"):
    """ inputs an integer """
    global pg_ls_printed
    pg_print(prompt)
    pg_print(default_text)
    for answer in pg_get_int_input(default_text):
        if answer == "":
            answer = "0"
        pg_ls_printed.pop()
        pg_print(answer)
    try:
        return int(answer)
    except:
        print("can't make an integer")

# float(decimal) inputting
def pg_float_input(prompt="", default_text="0.0"):
    """ inputs a float(decimal) """
    global pg_ls_printed
    pg_print(prompt)
    pg_print(default_text)
    for answer in pg_get_float_input(default_text):
        if answer == "":
            answer = "0.0"
        pg_ls_printed.pop()
        pg_print(answer)
    try:
        return float(answer)
    except:
        print("can't make a float")

# float -> int inputting
def pg_float_int_input(prompt="", default_text=""):
    """ returns the int of the inputted float if possible """
    try :
        return pg_float_int(pg_float_input(prompt, default_text))
    except:
        print("can't make any int or float")

# screenshot
def pg_screenshot(win, rect, name):
    """ screenshots """
    pygame.image.save(pg_cut_rect_from_surface(win, rect), name)

### resetting the main window

def pg_reset_screen():
    win = DISPLAYSURF
    win.fill(BG_COLOR)
    pg_draw_board(win)
    pg_draw_buttons(win, PG_BREAD_BOARD_WINW+4, 5, PG_WINW-4, PG_BREAD_BOARD_WINH-10)
    pg_draw_color_pool(win, PG_WINW-192, PG_BREAD_BOARD_WINH, PG_WINW, PG_WINH)
    pg_draw_printed(win, 0, PG_BREAD_BOARD_WINH, PG_BREAD_BOARD_WINW, PG_WINH, None, PG_PRINT_FG_COLOR)
    pg_refresh()


#end defining functions.

# setting up the main window and making lists
# to use them later in inputting functions

pg_surface()
pg_Make_point_poses()
pg_Make_button_rects()
pg_Make_color_rects()
pg_draw_color_pool(DISPLAYSURF, PG_WINW-192, PG_BREAD_BOARD_WINH, PG_WINW, PG_WINH, True)
pg_draw_buttons(DISPLAYSURF, PG_BREAD_BOARD_WINW, 5, PG_WINW, PG_BREAD_BOARD_WINH, True)
pg_draw_board(DISPLAYSURF, first=True)
DISPLAYSURF.fill(BG_COLOR)
pg_draw_board(DISPLAYSURF)
pg_print("\t\tWelcome to digi-board!\n\n")
pg_draw_printed(DISPLAYSURF, 0, PG_BREAD_BOARD_WINH, PG_BREAD_BOARD_WINW , PG_WINH, None, PG_BUTTON_FG_COLOR)
pg_draw_color_pool(DISPLAYSURF, PG_WINW-192, PG_BREAD_BOARD_WINH, PG_WINW, PG_WINH)
refresh()
make_defaults("u+50", "d+50", RED)
make_defaults("u-50", "d-50", BLUE)


name = "No name"
running = True
i = 0
#main loop
while running:
    #
    mode = pg_input_button()
    if mode == "voltage":
        v = pg_float_int_input("please enter the voltage you want measured in volts:", "1")
        VOLTAGE = v
        pg_print("the voltage is set to :", VOLTAGE)
        refresh()
        del v

    elif mode == "wire":
        # A
        pg_print("Please select A position.")
        A = pg_input_point()
        pg_print("got A point")
        # B
        pg_print("Please select B position.")
        B = pg_input_point()
        pg_print("got B point")
        pg_print("please select the wire color")
        color = pg_input_color()
        pg_print("Wire connected :)")
        Connect_wire(A, B, color, True)
        COMMANDS.append(ls_wire[-1])
        refresh()
        del A, B

    elif mode == "LED":
        # anode
        pg_print("Please select anode position.")
        anode = pg_input_point()
        pg_print("got anode")
        # cathode
        pg_print("Please select cathode position.")
        cathode = pg_input_point()
        pg_print("got cathode")
        # color
        pg_print("choose your LED color")
        color = None
        try:
            color = pg_input_color()
        except:
            pg_print(color, "had !!!ERROR!!!")
            del anode, cathode, color
            continue
        # required_voltage
        rv = pg_float_int_input("required voltage to turn on LED? ", "0")
        make_LED(anode, cathode, color, rv)
        pg_print("LED placed")
        COMMANDS.append(ls_LED[-1])
        del anode, cathode, color, rv

    elif mode in all_IC_codes:
        pg_print("please select the Vcc point")
        point = pg_input_point()
        make_IC(point, all_IC_codes[mode])
        COMMANDS.append(ls_IC[-1])
        pg_print("IC placed")

    elif mode[:5] == "check":
        if mode[6:] == "LED":
            check_LED()
            pg_print("checked")
        elif mode[6:] == "wire":
            check_wire()
            pg_print("checked")
        elif mode[6:] == "voltage":
            pg_print("the voltage is : ", VOLTAGE)
            pg_print("checked")
        elif mode[6:] == "point":
            pg_print("Please select your point")
            A = pg_input_point()
            try:
                pg_print(A, ":", check_point(A))
            except:
                pg_print("Your point does not exist!")
            del A
        elif mode[6:] == "IC":
            check_IC()
            pg_print("checked")
        else:
            pg_print("this line wasn't supposed to be printed!!!")

    elif mode == "screenshot":
        image_name = pg_str_input("What is your image files name? ", name)
        if image_name == "":
            image_name = "No name"
        image_format = "png"
        pg_screenshot(DISPLAYSURF, (0, 0, PG_BREAD_BOARD_WINW, PG_BREAD_BOARD_WINH), image_name+"."+image_format)
        pg_print("image file saved")
        del image_format, image_name

    elif mode == "save":
        if name == "No name":
            name = pg_str_input("What's your files name? ", name)
            if name == "":
                name = "No name"
            pg_change_name(name)
        save(name)
        pg_print("file saved")

    elif mode == "open":
        name = pg_str_input("what's your files name? ", name)
        if os.path.exists(name+".dgb"):
            try:
                open_file(name)
            except:
                pg_print(name, "isn't in this folder!")
            else:
                pg_change_name(name)
                refresh()
        else:
            pg_print(name, "doesn't exist!")

    elif mode == "rename":
        name = pg_str_input("what's your files name? ", name)
        pg_change_name(name)

    elif mode == "undo":
        if COMMANDS != []:
            del_item()
            refresh()
        else:
            pg_print("No item is on bread board!")

    elif mode == "button background color":
        pg_print("please select the color")
        PG_BUTTON_BG_COLOR = pg_input_color()

    elif mode == "button foreground color":
        pg_print("please select the color")
        PG_BUTTON_FG_COLOR = pg_input_color()

    elif mode == "terminal background color":
        pg_print("please select the color")
        PG_PRINT_BG_COLOR = pg_input_color()

    elif mode == "terminal foreground color":
        pg_print("please select the color")
        PG_PRINT_FG_COLOR = pg_input_color()

    elif mode == "delete":
        if len(COMMANDS) > 0:
            pg_print("select the item to delete")
            i_del = 0
            i_del = pg_input_item()
            try:
                del_item(i_del)
                refresh()
                pg_print("deleted")
            except:
                pg_print("not enough items to delete the requiered item!")
            del i_del
        else:
            pg_print("there is no item on the board to delete")

    elif mode == "restart":
        restart()

    elif mode == "refresh":
        refresh()

    elif mode == "clear":
        pg_clear()

    elif mode == "help":
        guide()

    elif mode == "credits":
        pg_print("physical & algorythmical code: Ali Mozdian fard")
        pg_print("graphical code & designer: Pooya Shams")

    elif mode == "quit":
        running = False
        pygame.quit()
        sys.exit()

    else:
        pg_print("This command is not defined! see help.")

    pg_reset_screen()
    refresh()

pygame.quit()
sys.exit()
