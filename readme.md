# Wynntils Resolver
## A simple resolver to anaslyeze wynntils' coded equipment in chat.

### Built on
[![Python 3.9](https://img.shields.io/badge/python%203.9-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)

### Install
pip install wynntilsresolver

### Usage

Use as a package

```python
from wynntilsresolver import resolver

print(resolver.decode("󵿰Warp󵿲󵃨󵄴󵁤󵀠󵁤󵂄󵅥󵀀󵃌󵿲󵃗󵀄󵿱"))
# Item(name='Warp', ids=[0.88, 1.07, 0.55, 0.38, 0.55, 0.63, 1.1925, 0.3, 0.81], powders=[<Powder.AIR: 4>, <Powder.AIR: 4>, <Powder.AIR: 4>], rerolls=4)
```

Or initialite your own match pattern
```python
import re
from wynntilsresolver import Resolver

resolver = Resolver(pattern=re.compile(...))
```

Use the cli
```bash
WIP
```