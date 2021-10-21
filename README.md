# VSCII - A terminal-based dungeon crawler written in Python.

This project requires ANSI-compatability and may have issues running on
Windows terminals.

The game will be "frame-based", clearing the terminal for each update rather
than outputting a continuous stream of text. Custom input functions must be used
to make sure that the user does not interfere with the design.

Since VSCII is terminal-based, pre-recorded inputs such as debug tests can
be piped into the program to automatically verify behavior
- Ex: (`python3 main.py < record.txt`)

The framebuffer does not print upon each write. Instead, the user must call
`render()` to push the changes to stdout. However, any frame buffer functions
which block the main thread, such as `input_line()` or `getch()`, will call
`render()` for the user.

## The Frame Buffer

The frame buffer is the root object in VSCII. This handles input and output and
contains all sub-containers and elements.

## Elements

Elements are the most important aspect of VSCII. They are used to interface with
the framebuffer object to draw more advanced graphics upon each render call.

## Containers

Containers can be used to dynamically resize Elements as the program runs. The
most important Container is FullScreen, which checks the size of the terminal
each draw and passes that size on to its children. Containers can contain other
Containers, which allows them to recursively split into more intricate blocks.

## Trees

Trees can be used to more quickly manipulate the structure of a scene. As
opposed to creating many objects and linking them to each other, a dictionary is
used to form a visual tree structure which can be processed into a dictionary of
nodes with inheritance properly configured.

An example tree:
```
    nodes = vscii.read_tree({
        "fullscreen": (vscii.FullScreen(), {
            "hsplit": (vscii.HSplit(), {
                "vsplit": (vscii.VSplit(), {
                    "console0": vscii.TextDisplay(),
                    "console1": vscii.TextDisplay(),
                }),
                "console2": vscii.TextDisplay(),
            }),
        }),
    })
```

Each node on the tree is a string key, followed by either a tuple or an
FBElement. If a tuple is encountered, the first member should be the node's
class, and the second, a sub-tree.