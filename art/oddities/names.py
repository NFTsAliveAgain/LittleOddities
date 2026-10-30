"""Whimsical, original character names (first name + compound surname)."""
from __future__ import annotations

FIRST = """Pip Mungo Tilly Bram Nim Oona Fizz Gubbins Wren Otto Pim Lulu Barnaby Dot Figgy Rufus Tansy Ziggy Mabel
Noodle Clem Bix Hettie Juno Kip Marlo Nell Ozzie Pocket Quill Rosco Saffy Tuck Umber Vesper Wally Yoyo Zuzu Alfie Bunty
Crumpet Dinky Elmo Flossie Gus Hazel Iggy Jojo Kiki Loaf Moss Nubbin Olive Pudge Rolo Sprout Toffee Ulla Waffles Bean
Cosmo Dabble Echo Fable Gizmo Honey Inky Jelly Kettle Lark Merry Nutmeg Opal Peppy Quinn Ripple Sunny Tinker Velvet
Widget Bloop Cricket Doodle Ember Fudge Gumbo Hopper Jinx Kazoo Lentil Mochi Nacho Parsnip Pickle Scoot Tater Zest""".split()

ROOTS = """Puddle Crumb Wobble Button Nibble Fizzle Pickle Thistle Bumble Muddle Sprocket Tumble Waffle Doodle Kettle
Noodle Pebble Bramble Fumble Giggle Jumble Marble Nugget Pocket Riddle Snuggle Tinker Truffle Whisker Zigzag Biscuit
Cobble Dapple Fiddle Gobble Hobble Mumble Rumble Scribble Sniffle Squiggle Twiddle Wiggle Bauble Crinkle""".split()

ENDS = """worth bottom wick ton ford by kins sworth field more ley ham shaw wood berry well stone brook dale wig
pants socks nose foot top hat whistle""".split()


class NameMaker:
    def __init__(self, rng):
        self.rng = rng
        self.used = set()

    def next(self) -> str:
        for _ in range(10000):
            name = f"{self.rng.choice(FIRST)} {self.rng.choice(ROOTS)}{self.rng.choice(ENDS)}"
            if name not in self.used:
                self.used.add(name)
                return name
        raise RuntimeError("ran out of unique names")
