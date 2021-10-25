# VSCII - A terminal GUI library.

This project requires ANSI-compatability and may have issues running on
Windows terminals.

Since VSCII is terminal-based, pre-recorded inputs such as debug tests can
be piped into the program to automatically verify behavior
- Ex: (`python3 main.py < record.txt`)

The framebuffer does not print upon each write. Instead, the user must call
`render()` to push the changes to stdout. However, any frame buffer functions
which block the main thread, such as `input_line()` or `getch()`, will call
`render()` for the user.

# Getting started

1. [Hello World!](#hello-world!)
2. [Elements](#elements)
3. [Trees](#trees)
4. [Splits](#splits)
5. [Custom Elements](#custom-elements)

## Hello World!

To make your own programs using VSCII, just `import vscii` in your program and
create a FrameBuffer to get started.

```
import vscii

framebuffer = FrameBuffer()
```

Creating a new framebuffer automatically configures the terminal for displaying
graphics, so all you have to do is call a function like `blit` to draw on the
screen.

```
# Print "Hello World!" at (0, 0)
framebuffer.blit("Hello World!", 0, 0)
```

However, if you run this, the program will seemingly display nothing. This is
because VSCII's FrameBuffer cleans the terminal and returns it to its original
state upon deconstruction. Instead, we want to wait for the user's input before
ending the program, which can be accomplished with `getch()`.

```
# Print "Hello World!" at (0, 0)
framebuffer.blit("Hello World!", 0, 0)

# Wait for a single input before continuing.
framebuffer.getch()
```

`getch()` additionally calls `render()`, which pushes all the changes made to
the framebuffer to the terminal, allowing the user to see it. If you ever need
to force the screen to update for any reason, just call `render()`

```
framebuffer.render()
```

## Elements

While being able to draw anywhere on the terminal is super useful, we're still
limited to static positions which are limited to the *size* of the user's
terminal window. However, VSCII includes two powerful tools to draw dynamically
sized graphics: Elements and Containers.

Containers are Elements which contain other Elements, and regular Elements
simply draw things to the screen. To get started, create a `FullScreen` Element
and add it to the framebuffer.

```
fullscreen = vscii.FullScreen()
framebuffer.add_elem(fullscreen)
```

Now the `fullscreen` container will automatically set the width and height of
it's children to match the size of the user's terminal.

To take advantage of this, we can add a child to the fullscreen container, a
`TextDisplay`

```
text_display = vscii.TextDisplay()
fullscreen.add_child(text_display)
```

You should now see a border of #s around the screen. This is because
`TextDisplay` draws a border around itself, using it's width and height.

Now you can print text to the screen which automatically wraps according to the
user's terminal size!

```
text_display.print("This text is quite short...\n")
text_display.print("This\ntext\nhas\nnew\nlines\n)
text_display.print("This text is veeeeeeeery long, and should wrap around to the next line on small terminal windows. Try resizing and making the window a bit shorter!)
```

## Trees

To make the organization of elements easier, VSCII provides a `read_tree()`
function to convert a dictionary of elements into an already-configured tree.
`read_tree()` expects a dictionary of string keys which refer to either tuples
or FBElements.

Each node on the tree is a string key, followed by either a tuple or an
FBElement. If a tuple is encountered, the first member should be the node's
class, and the second, a sub-tree. For example:

```
import vscii

# Create a framebuffer and tree of elements.
framebuffer = vscii.FrameBuffer()
nodes = vscii.read_tree({
    "fullscreen": (vscii.FullScreen(), {
        "text_display": vscii.TextDisplay(),
    }),
})

# Add the root of the tree to the framebuffer and print!
framebuffer.add_elem(nodes["fullscreen"])
nodes["text_display"].print("Hello Tree!")

framebuffer.getch()
```

## Splits

Using this new tree structure, we can much more easily create a more advanced
design. Let's introduce a `VSplit` and a second `TextDisplay` which will split
the screen with the first.

```
import vscii

# Create a framebuffer and tree of elements.
framebuffer = vscii.FrameBuffer()
nodes = vscii.read_tree({
    "fullscreen" : (vscii.FullScreen(), {
        "vsplit" : (vscii.VSplit(), {
            "text_left": vscii.TextDisplay(),
            "text_right": vscii.TextDisplay(),
        })
    }),
})

# Add the root of the tree to the framebuffer and print!
framebuffer.add_elem(nodes["fullscreen"])
nodes["text_left"].print("Hello Left!")
nodes["text_left"].print("Hello Right!")

framebuffer.getch()
```

Now the screen is evenly split between each TextDisplay object. Splits can be
nested to make even more advance designs.

## Custom Elements

Oftentimes you'll want custom elements that provide greater control than VSCII's
included elements. Writing your own is easy, and completely compatable with
other containers and elements.

To start, create a new class that inherits from `vscii.FBElement`.

```
class GroceryList(vscii.FBElement):
    pass
```

`FBElement` includes a few variables which containers can rely on for managing
elements, as well as a `_render()` function which `FrameBuffer` calls upon each
redraw.

```
class FBElement(object):
    """ Base class for Frame Buffer Elements.\n
    """
    anch_x = 0
    anch_y = 0
    width = 0
    height = 0

    def _render(self, parent: FrameBuffer):
        return
```

Let's add to our grocery list to allow the user to modify it:

```
class GroceryList(vscii.FBElement):
    groceries = ""

    def add_grocery(self, grocery):
        self.groceries += grocery + "\n"
```

And now we'll write a little `_render` function to center the text on the
grocery list element. The frame buffer passes itself to the render function as
the `parent` argument, which we can use to draw our element.

```
def _render(self, parent):
    y = 0
    for line in self.groceries.splitlines():
        # Center the text and draw it on a new row.
        parent.blit(line, self.anch_x + (self.width - len(line)) // 2, y)
        y += 1
```

Now just add `GroceryList` to a tree and write some groceries to it!

```
framebuffer = vscii.FrameBuffer()
fullscreen = vscii.FullScreen()
grocery_list = GroceryList()

framebuffer.add_elem(fullscreen)
fullscreen.add_child(grocery_list)

grocery_list.add_grocery("Apples")
grocery_list.add_grocery("Milk")
grocery_list.add_grocery("Soap")
grocery_list.add_grocery("Coffee Beans")

# Press any key to end...
framebuffer.getch()
```

You should see each string in a sequential list, centered according to the
list's width.

```
       Apples
        Milk
        Soap
    Coffee Beans
```