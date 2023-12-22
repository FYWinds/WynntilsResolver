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
from wynntilsresolver import Item

text_toxo = "󰀀󰄀󰉔󶽸󶽰󶱡󷍭󶽳󶥳󰀃󰔀󱱛󲅀󱴰󴽓󲉴󰓆󳿿"

item = Item.from_utf16(
    text_toxo,
    id_map,
    shiny_map,
    item_map,
).dump()
