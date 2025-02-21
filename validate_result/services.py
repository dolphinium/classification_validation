import csv
import os
from typing import List, Dict, Tuple
from models import SystemOutput, Annotation
from datetime import datetime

class DataService:
    def __init__(self, system_path: str, annotated_path: str):
        self.system_path = system_path
        self.annotated_path = annotated_path

    def read_system_output(self) -> List[SystemOutput]:
        if not os.path.exists(self.system_path):
            return []
            
        with open(self.system_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [SystemOutput(**row) for row in reader]

    def read_annotations(self) -> Dict[str, Annotation]:
        if not os.path.exists(self.annotated_path):
            return {}
            
        annotations = {}
        with open(self.annotated_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                annotations[row["file_id"]] = Annotation(
                    file_id=row["file_id"],
                    final_classification=row["final_classification"],
                    final_category=row["final_category"],
                    excluded=row["excluded"] == "True",
                    exclusion_note=row.get("exclusion_note", ""),
                    annotation_date=row.get("annotation_date", "")
                )
        return annotations

    def write_annotations(self, annotations: Dict[str, Annotation]) -> None:
        fieldnames = ["file_id", "final_classification", "final_category", "excluded", 
                     "exclusion_note", "annotation_date"]
        with open(self.annotated_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for annotation in annotations.values():
                writer.writerow({
                    "file_id": annotation.file_id,
                    "final_classification": annotation.final_classification or "",
                    "final_category": annotation.final_category or "",
                    "excluded": str(annotation.excluded),
                    "exclusion_note": annotation.exclusion_note or "",
                    "annotation_date": annotation.annotation_date or ""
                })

    def get_split_data(self) -> Tuple[List[dict], List[dict]]:
        system_outputs = self.read_system_output()
        annotations = self.read_annotations()
        
        annotated = []
        pending = []
        
        for output in system_outputs:
            annotation = annotations.get(output.file_id, Annotation(file_id=output.file_id))
            data = {
                **output.__dict__,
                "final_classification": annotation.final_classification,
                "final_category": annotation.final_category,
                "excluded": str(annotation.excluded),
                "exclusion_note": annotation.exclusion_note,
                "annotation_date": annotation.annotation_date
            }
            
            if annotation.annotation_date:
                annotated.append(data)
            else:
                pending.append(data)
                
        return annotated, pending