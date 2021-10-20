""" VSCII is a terminal GUI library.\n
It supports frame buffer rendering and various modular elements which allow the
user to expand upon the library with their own elements and containers.
"""

import curses

class FrameBuffer(object):
    """ Central framebuffer object.\n
    This handles stdin and stdout for the user, maintaining a text-based frame
    buffer of a given width and height. It supports primative drawing functions
    such as `blit()`.\n
    Elements can be added to the framebuffer using `add_elem()`. Elements can 
    contain a `render()` function which will be excuted each time the frame
    buffer is rendered. This can be used for things such as text boxes or
    graphical windows.
    """
    # All ncurses access should be encapsulated through this class.

    elements: list = []
    _window = None
    _buffer: list

    def __init__(self):
        self._window = curses.initscr()
        self._window.keypad(True)
        self.reset()
        curses.start_color()
        curses.noecho()

    def __del__(self):
        curses.echo()
        curses.endwin()

    def add_elem(self, elem):
        """ Add an element to this framebuffer.\n
        Elements are rendering objects which have the ability to redraw upon
        each render.
        """
        self.elements.append(elem)
    
    def blit(self, blit: str, xpos: int, ypos: int, transparent: str = ""):
        """ Place a rectangular graphic onto the framebuffer, overwriting anything
        under it.\n
        An optional transparency char can be provided which will be
        ignored (leaving the underlying art the same)
        """
        i = 0
        x = 0
        y = 0

        while len(blit) > i:
            if blit[i] == "\n":
                x = 0
                y += 1
            else:
                if blit[i] != transparent:
                    self._buffer[xpos + x + (ypos + y) * self.get_width()] =  blit[i]
                x += 1
            i += 1

    def del_elem(self, elem):
        """ Delete an element.\n
        """
        self.elements.remove(elem)
        del(elem)

    def getch(self) -> int:
        """ Get a single keyboard input.\n
        """
        self.render()
        return self._window.getch()

    def get_width(self) -> int:
        return self._window.getmaxyx()[1]
    
    def get_height(self) -> int:
        return self._window.getmaxyx()[0]

    def text_input(self, row: int, column: int, max_length: int = 80):
        """ Allow the user to input a line of text.\n
        The text will be returned when the user presses the enter key. This text
        input can appear anywhere on the screen. An optional max length can be
        provided.
        """
        self.render()
        curses.echo()
        result: str = self._window.getstr(row, column, max_length).decode("utf-8")
        curses.noecho()
        return result

    def render(self):
        """ Draw all screen elements and display to the terminal.\n
        This function is automatically called by input functions such as
        `text_input` and `getch`.
        """
        for i in self.elements:
            i._render(self)


        for i in range(self.get_height() - 1):
            result: str = ""

            for char in self._buffer[i * self.get_width():(i + 1) * self.get_width()]:
                result += char
            
            self._window.addstr(i, 0, result)
        self._window.refresh()
    
    def reset(self):
        """ Reset the drawing area.\n
        Recreates the framebuffer, adjusting to fit the terminal's current size.
        """
        self._buffer = list(" " * self.get_width() * self.get_height())

class FBElement(object):
    """ Base class for Frame Buffer Elements.\n
    """
    anch_x: int
    anch_y: int
    width: int
    height: int

    def _render(self, parent: FrameBuffer):
        return

class FBContainer(FBElement):
    """ Base class for maintaining child elements.\n
    """
    children: list

    def __init__(self):
        self.children = list()

    def add_child(self, child: FBElement):
        self.children.append(child)
    
    def del_child(self, child: FBElement):
        self.children.remove(child)
        del(child)

    def _render(self, parent: FrameBuffer):
        for child in self.children:
            child._render(parent)

class FullScreen(FBContainer):
    def _render(self, parent: FrameBuffer):
        for child in self.children:
            child.anch_x = 0
            child.anch_y = 0
            child.width = parent.get_width() - 2
            child.height = parent.get_height() - 3
            child._render(parent)

class HorizontalList(FBContainer):
    def _render(self, parent):
        for i in range(len(self.children)):
            if self.children[i] == self:
                continue
            self.children[i].anch_x = self.width // len(self.children) * i
            self.children[i].anch_y = self.anch_y
            self.children[i].width = self.width // len(self.children)
            self.children[i].height = self.height
            self.children[i]._render(parent)

class VeriticalList(FBContainer):
    def _render(self, parent):
        for i in range(len(self.children)):
            if self.children[i] == self:
                continue
            self.children[i].anch_x = self.anch_x
            self.children[i].anch_y = self.height // len(self.children) * i
            self.children[i].width = self.width
            self.children[i].height = self.height // len(self.children)
            self.children[i]._render(parent)

class TextDisplay(FBElement):
    """ Maintain a list of text entries.\n
    Will display a block of text which can be added to by use of the `print()`
    function. This can be anchored somewhere on the framebuffer and will be
    updated each redraw.
    """
    back: str
    border: str
    buffer: str = ""
    fix_x: int
    fix_y: int
    margin: int

    def __init__(self, anch_x: int, anch_y: int, width: int, height: int,
            border: str = "#", back: str = " ", margin: int = 1, ):
        self.anch_x = anch_x
        self.anch_y = anch_y
        self.back = back
        self.border = border
        self.margin = margin
        self.height = height
        self.width = width

    def _render(self, parent: FrameBuffer):
        parent.blit(add_border(create_rect(self.back, self.width, self.height),
            self.border, self.back), self.anch_x, self.anch_y)

        parent.blit(self.buffer, self.anch_x + 1, self.anch_y + 1)

    def print(self, string: str):
        """ Push a new line of text to the text field.\n
        """
        for i in string.splitlines():
            if len(i) < self.width - self.margin * 2:
                i += self.back * (self.width - self.margin * 2 - len(i))
            else:
                i = i[0:self.width - self.margin * 2]
            self.buffer += self.back * self.margin + i + self.back * self.margin + "\n"

class SelectList(FBElement):
    background: str
    entries: int
    selected: str
    _curpos: int = 0

    def __init__(self, anch_x: int, anch_y: int, entries: int,
            selected: str = "#", background: str = " "):
        self.anch_x = anch_x
        self.anch_y = anch_y
        self.background = background
        self.entries = entries
        self.selected = selected

    def _render(self, parent: FrameBuffer):
        parent.blit(create_rect(self.background, 1, self.entries), self.anch_x,
            self.anch_y)
        parent.blit(self.selected, self.anch_x, self.anch_y + self._curpos)

    @staticmethod
    def input(parent: FrameBuffer, selection) -> int:
        parent.add_elem(selection)

        while (1):
            parent.render()

            inchar: int = parent.getch()

            if inchar == curses.KEY_UP:
                selection.movecur(-1)
            elif inchar == curses.KEY_DOWN:
                selection.movecur(1)

            if inchar == curses.KEY_ENTER or inchar == ord('\n'):
                break
        
        result: int = selection._curpos
        parent.del_elem(selection)
        return result

    def movecur(self, pos: int):
        """ Move the selection cursor by `pos`.\n
        """
        if not (self._curpos + pos < 0 or self._curpos + pos >= self.entries):
            self._curpos += pos

def add_border(string: str, border: str = " ", background: str = " ") -> str:
    """ Add a border around a string.\n
    This is a convienience function to draw a rectangular area around a string.
    """
    line_len = 0
    
    for i in string.split("\n"):
        if len(i) > line_len:
            line_len = len(i)

    result = border * (line_len + 2) + "\n"

    for i in string.split("\n"):
        result += border + i + (line_len - len(i)) * background + border + "\n";

    result += border * (line_len + 2)

    return result

def create_rect(string: str, width: int, height: int) -> str:
    """ Creates a rectangle which can be displayed to the frame buffer.\n
    """
    return string * width + ("\n" + string * width) * (height - 1)
