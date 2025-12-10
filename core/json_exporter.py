"""
JSON data export utilities.

Exports course data to JSON format for further processing.
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from typing import Optional, Any

from core.config import Config, get_config
from core.classroom_api import Course, CourseWork, CourseMaterial, Announcement


class JSONExporter:
    """
    Exports Google Classroom data to JSON format.

    Supports exporting courses, coursework, materials, and announcements.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize JSON exporter.

        Args:
            config: Configuration instance
        """
        self.config = config or get_config()

    def _to_dict(self, obj: Any) -> dict:
        """Convert dataclass to dict, handling nested objects."""
        if hasattr(obj, "__dataclass_fields__"):
            result = {}
            for field_name, field_info in obj.__dataclass_fields__.items():
                value = getattr(obj, field_name)
                if isinstance(value, list):
                    result[field_name] = [self._to_dict(item) for item in value]
                elif hasattr(value, "__dataclass_fields__"):
                    result[field_name] = self._to_dict(value)
                else:
                    result[field_name] = value
            return result
        return obj

    def export_course(
        self,
        course: Course,
        coursework: list[CourseWork] = None,
        materials: list[CourseMaterial] = None,
        announcements: list[Announcement] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Export complete course data to JSON.

        Args:
            course: The Course to export
            coursework: Optional list of coursework
            materials: Optional list of materials
            announcements: Optional list of announcements
            output_path: Optional custom output path

        Returns:
            Path to exported JSON file
        """
        if output_path is None:
            safe_name = "".join(
                c if c.isalnum() or c in " -_" else "_"
                for c in course.name
            )[:50]
            filename = f"export_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = self.config.exports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "exported_at": datetime.now().isoformat(),
            "course": self._to_dict(course),
        }

        if coursework is not None:
            data["coursework"] = [self._to_dict(cw) for cw in coursework]

        if materials is not None:
            data["materials"] = [self._to_dict(mat) for mat in materials]

        if announcements is not None:
            data["announcements"] = [self._to_dict(ann) for ann in announcements]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path

    def export_courses_list(
        self,
        courses: list[Course],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Export list of courses to JSON.

        Args:
            courses: List of courses to export
            output_path: Optional custom output path

        Returns:
            Path to exported JSON file
        """
        if output_path is None:
            filename = f"courses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = self.config.exports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "exported_at": datetime.now().isoformat(),
            "count": len(courses),
            "courses": [self._to_dict(course) for course in courses],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path

    def export_coursework_list(
        self,
        course: Course,
        coursework: list[CourseWork],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Export list of coursework to JSON.

        Args:
            course: The parent course
            coursework: List of coursework to export
            output_path: Optional custom output path

        Returns:
            Path to exported JSON file
        """
        if output_path is None:
            safe_name = "".join(
                c if c.isalnum() or c in " -_" else "_"
                for c in course.name
            )[:30]
            filename = f"coursework_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = self.config.exports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "exported_at": datetime.now().isoformat(),
            "course": self._to_dict(course),
            "count": len(coursework),
            "coursework": [self._to_dict(cw) for cw in coursework],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path

    def export_materials_list(
        self,
        course: Course,
        materials: list[CourseMaterial],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Export list of materials to JSON.

        Args:
            course: The parent course
            materials: List of materials to export
            output_path: Optional custom output path

        Returns:
            Path to exported JSON file
        """
        if output_path is None:
            safe_name = "".join(
                c if c.isalnum() or c in " -_" else "_"
                for c in course.name
            )[:30]
            filename = f"materials_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = self.config.exports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "exported_at": datetime.now().isoformat(),
            "course": self._to_dict(course),
            "count": len(materials),
            "materials": [self._to_dict(mat) for mat in materials],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path
