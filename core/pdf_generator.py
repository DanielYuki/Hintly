"""
PDF report generation using reportlab.

Creates professional PDF reports for course materials.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)

from core.config import Config, get_config
from core.classroom_api import CourseMaterial, CourseWork, Course


class PDFGenerator:
    """
    Generates PDF reports for Google Classroom content.

    Supports material reports and course summaries.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize PDF generator.

        Args:
            config: Configuration instance
        """
        self.config = config or get_config()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Title"],
                fontSize=24,
                spaceAfter=20,
                textColor=colors.HexColor("#1a1a2e"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=8,
                textColor=colors.HexColor("#16213e"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BodyText",
                parent=self.styles["Normal"],
                fontSize=11,
                spaceBefore=6,
                spaceAfter=6,
                leading=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Metadata",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.gray,
            )
        )

    def generate_material_report(
        self,
        material: CourseMaterial,
        course: Course,
        analysis: str = "",
        summary: str = "",
        key_topics: list[str] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate a PDF report for a course material.

        Args:
            material: The CourseMaterial to report on
            course: The parent Course
            analysis: AI-generated analysis text
            summary: Summary of the material
            key_topics: List of key topics/concepts
            output_path: Optional custom output path

        Returns:
            Path to generated PDF file
        """
        if output_path is None:
            # Generate filename from material title
            safe_title = "".join(
                c if c.isalnum() or c in " -_" else "_"
                for c in material.title
            )[:50]
            filename = f"report_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = self.config.reports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build content
        story = []

        # Title
        story.append(Paragraph(material.title, self.styles["CustomTitle"]))

        # Metadata
        meta_text = f"Course: {course.name}"
        if course.section:
            meta_text += f" | Section: {course.section}"
        if material.creation_time:
            meta_text += f" | Created: {material.creation_time[:10]}"
        story.append(Paragraph(meta_text, self.styles["Metadata"]))
        story.append(Spacer(1, 15))

        # Description
        if material.description:
            story.append(Paragraph("Description", self.styles["SectionHeader"]))
            story.append(Paragraph(material.description, self.styles["BodyText"]))
            story.append(Spacer(1, 10))

        # Summary
        if summary:
            story.append(Paragraph("Summary", self.styles["SectionHeader"]))
            story.append(Paragraph(summary, self.styles["BodyText"]))
            story.append(Spacer(1, 10))

        # Key Topics
        if key_topics:
            story.append(Paragraph("Key Topics", self.styles["SectionHeader"]))
            items = [
                ListItem(Paragraph(topic, self.styles["BodyText"]))
                for topic in key_topics
            ]
            story.append(
                ListFlowable(items, bulletType="bullet", leftIndent=20)
            )
            story.append(Spacer(1, 10))

        # Analysis
        if analysis:
            story.append(Paragraph("Analysis", self.styles["SectionHeader"]))
            story.append(Paragraph(analysis, self.styles["BodyText"]))
            story.append(Spacer(1, 10))

        # Attached Resources
        if material.materials:
            story.append(Paragraph("Attached Resources", self.styles["SectionHeader"]))
            table_data = [["Type", "Title", "Link"]]
            for mat in material.materials:
                table_data.append([
                    mat.type.replace("_", " ").title(),
                    mat.title or "Untitled",
                    mat.url[:50] + "..." if mat.url and len(mat.url) > 50 else (mat.url or "N/A"),
                ])

            table = Table(table_data, colWidths=[1.2 * inch, 2.5 * inch, 3 * inch])
            table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ])
            )
            story.append(table)
            story.append(Spacer(1, 10))

        # Footer
        story.append(Spacer(1, 20))
        footer_text = f"Generated by Hintly on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        story.append(Paragraph(footer_text, self.styles["Metadata"]))

        # Build PDF
        doc.build(story)

        return output_path

    def generate_course_summary(
        self,
        course: Course,
        coursework_count: int = 0,
        materials_count: int = 0,
        summary: str = "",
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate a summary PDF for a course.

        Args:
            course: The Course to summarize
            coursework_count: Number of coursework items
            materials_count: Number of materials
            summary: AI-generated summary
            output_path: Optional custom output path

        Returns:
            Path to generated PDF file
        """
        if output_path is None:
            safe_name = "".join(
                c if c.isalnum() or c in " -_" else "_"
                for c in course.name
            )[:50]
            filename = f"course_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = self.config.reports_dir / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        story = []

        # Title
        story.append(Paragraph(f"Course Summary: {course.name}", self.styles["CustomTitle"]))

        # Course info
        if course.section:
            story.append(Paragraph(f"Section: {course.section}", self.styles["Metadata"]))
        story.append(Spacer(1, 15))

        # Description
        if course.description:
            story.append(Paragraph("Description", self.styles["SectionHeader"]))
            story.append(Paragraph(course.description, self.styles["BodyText"]))
            story.append(Spacer(1, 10))

        # Stats
        story.append(Paragraph("Course Statistics", self.styles["SectionHeader"]))
        stats_data = [
            ["Metric", "Count"],
            ["Coursework Items", str(coursework_count)],
            ["Materials", str(materials_count)],
            ["State", course.state],
        ]
        stats_table = Table(stats_data, colWidths=[2 * inch, 2 * inch])
        stats_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(stats_table)
        story.append(Spacer(1, 15))

        # Summary
        if summary:
            story.append(Paragraph("Summary", self.styles["SectionHeader"]))
            story.append(Paragraph(summary, self.styles["BodyText"]))
            story.append(Spacer(1, 10))

        # Links
        if course.alternate_link:
            story.append(Paragraph("Links", self.styles["SectionHeader"]))
            story.append(
                Paragraph(f"View in Classroom: {course.alternate_link}", self.styles["BodyText"])
            )

        # Footer
        story.append(Spacer(1, 20))
        footer_text = f"Generated by Hintly on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        story.append(Paragraph(footer_text, self.styles["Metadata"]))

        doc.build(story)

        return output_path
