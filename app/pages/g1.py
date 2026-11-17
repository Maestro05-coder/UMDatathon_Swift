import sys
from pathlib import Path

HERE = Path(__file__).parent
for p in (str(HERE), str(HERE.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)

from _group import render  # noqa: E402

render("g1")
