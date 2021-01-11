from logic import *

people = ["Cousin", "Grandfather", "Husband", "Mother", "Sister"]
backdrop = ["Beach", "House", "Mountains", "Park", "Restaurant"]
event = ["Birthday", "Engagement", "Firstchild", "Graduation", "Wedding"]
gift = ["Book", "Bracelet", "Cnadlesticks", "Musicbox", "Necklace"]

symbols = []

knowledge = And()

for person in people:
    for back in backdrop:
        for ev in event:
            for fi in gift:
                symbols.append(Symbol(f"{person}{back}{ev}{fi}"))

# Each person belongs to a house.
for person in people:
    knowledge.add(Or(
        for back in backdrop:
            Symbol(f"{person}{back}{*}{*}"),
    ))


# Only one house per person.
for person in people:
    for h1 in houses:
        for h2 in houses:
            if h1 != h2:
                knowledge.add(
                    Implication(Symbol(f"{person}{h1}"),
                                Not(Symbol(f"{person}{h2}")))
                )

# Only one person per house.
for house in houses:
    for p1 in people:
        for p2 in people:
            if p1 != p2:
                knowledge.add(
                    Implication(Symbol(f"{p1}{house}"),
                                Not(Symbol(f"{p2}{house}")))
                )

knowledge.add(
    Or(Symbol("GilderoyGryffindor"), Symbol("GilderoyRavenclaw"))
)

knowledge.add(
    Not(Symbol("PomonaSlytherin"))
)

knowledge.add(
    Symbol("MinervaGryffindor")
)

for symbol in symbols:
    if model_check(knowledge, symbol):
        print(symbol)
