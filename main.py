import vscii

def container_test():
    framebuffer = vscii.FrameBuffer()

    vlist = vscii.HSplit()

    console0 = vscii.TextDisplay()
    vlist.add_child(console0)

    console2 = vscii.TextDisplay()
    vlist.add_child(console2)

    hlist = vscii.VSplit()
    hlist.width = framebuffer.get_width() * 4 // 5
    hlist.height = framebuffer.get_height() * 4 // 5
    hlist.add_child(vlist)

    console1 = vscii.TextDisplay()
    hlist.add_child(console1)

    center = vscii.Center()
    center.add_child(hlist)

    fullscreen = vscii.FullScreen()
    fullscreen.add_child(center)
    framebuffer.add_elem(fullscreen)

    console0.print("Hello World!")
    console2.print("L\n o\n  w\n   e\n    r")
    console2.print("world?")
    console1.print("Goodbye World!")
    framebuffer.render() # Force a render to update the sizes.
    console1.print(framebuffer.input(console2.get_left() + 2,
        console2.get_bottom() - 2)
    )

    framebuffer.getch()

def tree_test():
    framebuffer = vscii.FrameBuffer()
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

    framebuffer.add_elem(nodes["fullscreen"])

    nodes["console0"].print("Hello World!")
    nodes["console2"].print("Type something here: ")
    nodes["console1"].print("Goodbye World!")
    framebuffer.render()
    nodes["console2"].print(
        framebuffer.input(nodes["console2"].get_left() + 2,
        nodes["console2"].get_bottom() - 2) + "\nPress any key to continue."
    )

    framebuffer.getch()

def error_test():
    # Create a framebuffer and tree of elements.
    nodes = vscii.read_tree({
        "fullscreen": (vscii.FullScreen(), {
            # This will raise a type error because integers are not framebuffer
            # elements.
            "text_display": 0,
        }),
    })

    nodes["text_display"].print("Hello World!")

def __main__():
    try:
        tree_test()
        print("\033[32mPASS: Test case 1 did not raise an exception.")
    except:
        print("\033[31mFAIL: Test case 1 raised an exception.")

    try:
        error_test()
        print("\033[31mFAIL: Test case 2 did not raise an exception.")
    except:
        print("\033[32mPASS: Test case 2 raised an exception.")

    print("\033[0mFinished running test cases.")

if __name__ == "__main__":
    __main__()