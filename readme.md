# Wynntils Resolver
## A simple resolver to anaslyeze wynntils' coded equipment in chat.

### Requires
[![Python >= 3.8](https://img.shields.io/badge/python>=3.8-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)

### Install
```bash
pip install wynntilsresolver -U
```


### Usage
#### Use Predefined Resolvers
```python
from wynntilsresolver.item import GearItemResolver

shiny_warp = "󰀀󰄀󰉗󶅲󷀀󰌉󰀘󵜢󴵅󶈑󴝑󷐙󵀄󶸥󵠦󶠄󰌃󿞼󰘄󸨁􏿮"
sw = GearItemResolver.from_utf16(shiny_warp)

assert sw.name == "Warp"
assert sw.identifications
assert sw.identifications == [
    Identification(id="rawAgility", internal_id=41, base=20, roll=-1, value=20),
    Identification(id="healthRegen", internal_id=24, base=-200, roll=87, value=-174),
    Identification(id="manaRegen", internal_id=34, base=-45, roll=77, value=-35),
    Identification(id="reflection", internal_id=69, base=90, roll=98, value=88),
    Identification(id="exploding", internal_id=17, base=50, roll=71, value=36),
    Identification(id="walkSpeed", internal_id=81, base=180, roll=116, value=209),
    Identification(id="healthRegenRaw", internal_id=25, base=-600, roll=80, value=-480),
    Identification(id="airDamage", internal_id=4, base=15, roll=110, value=16),
    Identification(id="raw1stSpellCost", internal_id=37, base=4, roll=88, value=4),
    Identification(id="raw2ndSpellCost", internal_id=38, base=-299, roll=104, value=-311),
]
assert sw.powder
assert sw.powder.powder_slots == 3
assert sw.powder.powders == ["A6", "A6", "A6"]
assert sw.shiny
assert sw.shiny.name == "warsWon"
assert sw.shiny.value == 69
assert sw.shiny.display_name == "Wars Won"
assert sw.shiny.internal_id == 4
assert sw.reroll == 0
```

#### Create your own resolver
```python
from typing import Optional

from wynntilsresolver.blocks import GearItem, Name,Identifications, Reroll, Powder, Shiny
from wynntilsresolver.resolver import Resolver

# Create a custom resolver like this
class MyResolver2(Resolver):
    item_type: GearItem
    name: Name
    identifications: Optional[Identifications]
    reroll: Optional[Reroll]
    powder: Optional[Powder]
    shiny: Optional[Shiny]

shiny_warp = "󰀀󰄀󰉗󶅲󷀀󰌉󰀘󵜢󴵅󶈑󴝑󷐙󵀄󶸥󵠦󶠄󰌃󿞼󰘄󸨁􏿮"

# Decode from Artemis shared utf16 text
b = MyResolver2.from_utf16(shiny_warp)

print(b.name.name) # Warp
if b.identifications:
    # Identification(id='rawAgility', internal_id=41, base=20, roll=-1, value=20)
    b.identifications.identifications[0]
```
