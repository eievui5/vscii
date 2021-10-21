import vscii

class InventoryMenu(vscii.FBElement):
    def _render(self, parent: vscii.FrameBuffer):
        title: str = "Inventory"
        parent.blit(title, self.anch_x + (self.width - len(title)) // 2 , self.anch_y)

def game():
    # Create a framebuffer.
    framebuffer = vscii.FrameBuffer()

    # Construct this screen's tree.
    nodes = vscii.read_tree({
        "screen" : (vscii.FullScreen(), {
            "vsplit" : (vscii.VSplit(), {
                "player_console" : vscii.TextDisplay(),
                "inventory" : InventoryMenu()
            })
        })
    })

    framebuffer.add_elem(nodes["screen"])

    # Process player commands.
    while True:
        command: str = framebuffer.input(
            nodes["player_console"].get_left() + 2,
            nodes["player_console"].get_bottom() - 2
        )
        if command == "exit":
            break
        else:
            nodes["player_console"].print("Unknown command: \"" + command + "\"")

def input_test():
    framebuffer = vscii.FrameBuffer()

    console = vscii.TextDisplay()
    console.margin = 3
    console.print("\n")
    framebuffer.add_elem(console)
    for i in range(4):
        console.print(framebuffer.input(0, 0))
    framebuffer.blit("Choose one!", 0, 0)

    selection: int = vscii.SelectList.input(framebuffer, vscii.SelectList(2, 3, 4, "-"))
    framebuffer.remove_elem(console)
    framebuffer.reset()
    framebuffer.blit(str(selection) + " is a great choice!", 6, 2)
    framebuffer.render()

    framebuffer.getch()

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
    nodes["console2"].print("L\n o\n  w\n   e\n    r")
    nodes["console2"].print("world?")
    nodes["console1"].print("Goodbye World!")
    framebuffer.render()
    nodes["console1"].print(
        framebuffer.input(nodes["console1"].get_left() + 2,
        nodes["console1"].get_bottom() - 2)
    )

    framebuffer.getch()

def __main__():
    tree_test()

if __name__ == "__main__":
    __main__()