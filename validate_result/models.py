from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class SystemOutput:
    file_id: str
    transcript: str
    classification: str
    category: str
    justification: str

@dataclass
class Annotation:
    file_id: str
    final_classification: Optional[str] = None
    final_category: Optional[str] = None
    excluded: bool = False
    exclusion_note: Optional[str] = None
    annotation_date: Optional[str] = None