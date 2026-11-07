from dataclasses import dataclass
from typing import List


@dataclass
class Record:
    article_no: str
    title: str
    part: str
    text: str
    amended_by: List[str]
    source_page: int