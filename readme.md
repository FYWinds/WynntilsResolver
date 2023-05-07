# Wynntils Resolver
## A simple resolver to anaslyeze wynntils' coded equipment in chat.

### Built on
[![Python 3.8](https://img.shields.io/badge/python%203.8-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)

### Install
```bash
pip install wynntilsresolver
```

### Usage

Use as a package

```python
from wynntilsresolver import resolver

print(resolver.decode("󵿰Warp󵿲󵃨󵄴󵁤󵀠󵁤󵂄󵅥󵀀󵃌󵿲󵃗󵀄󵿱"))
# Item(name='Warp', ids=[232, 308, 100, 32, 100, 132, 357, 0, 204], powders=[AIR, AIR, AIR], rerolls=4)
print(resolver.decode_to_json("󵿰Warp󵿲󵃨󵄴󵁤󵀠󵁤󵂄󵅥󵀀󵃌󵿲󵃗󵀄󵿱"))
# {'name': 'Warp', 'ids': [232, 308, 100, 32, 100, 132, 357, 0, 204], 'powders': ['AIR', 'AIR', 'AIR'], 'rerolls': 4}
```

> The calculation of the true roll value will rely on the identifications differ between the items.
> Please calculate using the following algorithm:

```python
if baseValue > 100:
    trueRoll = ((id/4 + 30) / 100) * baseValue
else:
    trueRoll = idRange.low + id/4
```

Or initialite with your own match pattern
```python
import re
from wynntilsresolver import Resolver

resolver = Resolver(pattern=re.compile(...))
```

Use the cli

This will defaulted decode the item into json format
```bash
pip install wynntilsresolver[cli]
python -m wynntilsresolver 󵿰Warp󵿲󵃨󵄴󵁤󵀠󵁤󵂄󵅥󵀀󵃌󵿲󵃗󵀄󵿱 
# In some terminal environment, you are not able to input some of the unicode string and will result in an ItemNotValidError
```