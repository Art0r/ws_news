from dataclasses import dataclass
from typing import Optional


@dataclass
class HtmlTag:
    _class: Optional[str] = None
    _tag: Optional[str] = None
    _xpath: Optional[str] = None
