import vscii

def container_test():
    framebuffer = vscii.FrameBuffer()
    fullscreen = vscii.FullScreen()
    hlist = vscii.HorizontalList()
    vlist = vscii.VeriticalList()
    console0 = vscii.TextDisplay(0, 0, 20, 20)
    console1 = vscii.TextDisplay(0, 0, 20, 20)
    console2 = vscii.TextDisplay(0, 0, 20, 20)

    vlist.add_child(console0)
    vlist.add_child(console2)
    fullscreen.add_child(hlist)
    hlist.add_child(vlist)
    hlist.add_child(console1)
    framebuffer.add_elem(fullscreen)

    console0.print("Hello World!")
    console2.print("L\n o\n  w\n   e\n    r")
    console2.print("world?")
    console1.print("Goodbye World!")
    framebuffer.reset()

    framebuffer.getch()

def input_test():
    framebuffer = vscii.FrameBuffer()

    console = vscii.TextDisplay(0, 1, 30, 10, "#", " ", 3)
    console.print("\n")
    framebuffer.add_elem(console)
    for i in range(4):
        console.print(framebuffer.text_input(0, 0))
    framebuffer.blit("Choose one!", 0, 0)

    selection: int = vscii.SelectList.input(framebuffer, vscii.SelectList(2, 3, 4, "-"))
    framebuffer.del_elem(console)
    framebuffer.reset()
    framebuffer.blit(str(selection) + " is a great choice!", 6, 2)
    framebuffer.render()

    framebuffer.getch()

def __main__():
    container_test()

if __name__ == "__main__":
    __main__()