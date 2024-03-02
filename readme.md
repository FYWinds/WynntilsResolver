# Wynntils Resolver
## A simple resolver to anaslyeze wynntils' coded equipment in chat.

### Requires
[![Python >= 3.8](https://img.shields.io/badge/python>=3.8-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)

### Install
```bash
pip install wynntilsresolver -U
```


### Usage
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
