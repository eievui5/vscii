
import re
import vscii

class Entity(object):
    health: int = 100
    max_health: int = 100
    name: str = ""

    def __init__(self, name = ""):
        self.name = name

class Player(Entity):
    pass

framebuffer: vscii.FrameBuffer
nodes: dict = {}
player = Player()
enemy: Entity = None

class Item(object):
    name: str = ""

    def __init__(self, name = ""):
        self.name = name

    def use(self):
        nodes["player_console"].print(f"{self.name} cannot be used right now.\n")

class Weapon(Item):
    def use(self):
        global enemy

        if not enemy is None:
            nodes["player_console"].print(f"You strike the {enemy.name} with your {self.name}.\n")
            enemy = None
        else:
            nodes["player_console"].print(f"You swing the {self.name} in the air.\n")

class Heal(Item):
    magnitude: int

    def __init__(self, name = "", magnitude = 10):
        self.name = name
        self.magnitude = magnitude

    def use(self):
        global player

        value = self.magnitude if player.health + self.magnitude < player.max_health else player.max_health - player.health
        player.health += value
        nodes["player_console"].print(f"You consumed the {self.name} and healed {value} points of health.\n")
        nodes["inventory"].items.remove(self)

class InventoryMenu(vscii.FBElement):
    items: list

    def __init__(self):
        self.items = [Weapon("Sword"), Heal("Food", 10)]

    def _render(self, parent: vscii.FrameBuffer):
        title: str = "Inventory"

        # Decorate.
        parent.blit(vscii.create_rect("|", 1, self.height), self.anch_x, self.anch_y)
        parent.blit(vscii.create_rect("|", 1, self.height), self.anch_x + self.width - 1, self.anch_y)
        parent.blit(vscii.create_rect("_", self.width - 2, 1), self.anch_x + 1, self.anch_y + self.height - 1)

        # Draw title text.
        parent.blit(title, self.anch_x + (self.width - len(title)) // 2, self.anch_y + 1)

        # List inventory items.
        for i in range(len(self.items)):
            parent.blit(self.items[i].name, self.anch_x + 4, self.anch_y + 2 + i)

    def get_item(self, item: str) -> Item:
        for i in self.items:
            if i.name.casefold() == item.casefold():
                return i
        return None

class PlayerMenu(vscii.FBElement):
    def _render(self, parent):
        global player

        # Decorate.
        parent.blit(vscii.create_rect("|", 1, self.height), self.anch_x, self.anch_y)
        parent.blit(vscii.create_rect("|", 1, self.height), self.anch_x + self.width - 1, self.anch_y)
        parent.blit(vscii.create_rect("_", self.width - 2, 1), self.anch_x + 1, self.anch_y + self.height - 1)

        # Draw player name
        parent.blit(player.name, self.anch_x + (self.width - len(player.name)) // 2, self.anch_y + 1)

        # Draw player info.
        parent.blit(f"Health: {player.health} / {player.max_health}",
            self.anch_x + 4, self.anch_y + 3)

class Environment(vscii.FBElement):
    def _render(self, parent: vscii.FrameBuffer):
        parent.blit(vscii.create_rect("#", self.width, self.height - 1), self.anch_x, self.anch_y)
        parent.blit(vscii.create_rect("_", self.width, 1), self.anch_x, self.anch_y + self.height - 1)

class PlayerConsole(vscii.TextDisplay):
    def _render(self, parent: vscii.FrameBuffer):
        result: str = ""
        for i in self.buffer.splitlines():
            x_off = 0
            for i in i.split():
                if x_off + len(i) > self.width - 2 - self.margin:
                    result += "\n"
                    x_off = 0
                result += i + " "
                x_off += len(i) + 1
            result += "\n"
        self.buffer = result
        while len(self.buffer.splitlines()) >= self.height - 2:
            self.buffer = self.buffer[self.buffer.find("\n") + 1:]

        parent.blit(result, self.anch_x, self.anch_y)

    def input(self, parent: vscii.FrameBuffer) -> str:
        return parent.input(self.get_left(), self.get_bottom() - 1, self.width)


def select_item() -> Item:
    return nodes["inventory"].items[vscii.SelectList.input(framebuffer,
        nodes["inventory"].get_left() + 2,
        nodes["inventory"].get_top() + 2,
        len(nodes["inventory"].items), "→"
    )]

def game():
    global enemy
    global framebuffer
    global nodes

    # Create a framebuffer.
    framebuffer = vscii.FrameBuffer()
    # Make the framebuffer volatile so that it redraws each frame.
    framebuffer.volatile = True

    # Construct this screen's tree.
    nodes = vscii.read_tree({
        "screen" : (vscii.FullScreen(), {
            "vsplit" : (vscii.VSplit(), {
                "lefthsplit" : (vscii.HSplit(), {
                    "environment" : Environment(),
                    "player_console" : PlayerConsole(),
                }),
                "righthsplit" : (vscii.HSplit(), {
                    "inventory" : InventoryMenu(),
                    "player_menu" : PlayerMenu(),
                }),
            })
        })
    })
    framebuffer.add_elem(nodes["screen"])

    # Configure nodes.
    nodes["player_console"].border = ""

    framebuffer.render()

    nodes["player_console"].print("What is your name?")
    player.name = nodes["player_console"].input(framebuffer)
    nodes["player_console"].clear()

    # Process player commands.
    enemy = Entity("Test")
    nodes["player_console"].print(f"A {enemy.name} appeared!\n")
    while True:
        command: list = nodes["player_console"].input(framebuffer).strip().split()

        if not command:
            continue

        if command[0] == "exit":
            break
        elif command[0] == "use":
            # Either allow the player to select options directly from the
            # inventory, or to pass an item name as an argument to `use`.
            item = None
            if len(command) > 1:
                item = nodes["inventory"].get_item(command[1])
            else:
                item = select_item()

            if not item is None:
                item.use()
            else:
                # Decide between "a" and "an" using a regex.
                nodes["player_console"].print(f"You don't have any"
                    + ("n" if re.match(r"^[aeiou]", command[1]) else "")
                    + f" \"{command[1]}\" right now.")
        else:
            nodes["player_console"].print(f"Unknown command: \"{command}\"\n")

def __main__():
    game()

if __name__ == "__main__":
    __main__()