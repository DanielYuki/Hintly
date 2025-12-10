"""
Google Classroom API wrapper.

Provides a clean interface for accessing Google Classroom data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from core.auth import OAuth2Flow
from core.config import Config, get_config


class CourseState(Enum):
    """Course state in Google Classroom."""
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    PROVISIONED = "PROVISIONED"
    DECLINED = "DECLINED"
    SUSPENDED = "SUSPENDED"


class CourseWorkType(Enum):
    """Type of coursework."""
    ASSIGNMENT = "ASSIGNMENT"
    SHORT_ANSWER_QUESTION = "SHORT_ANSWER_QUESTION"
    MULTIPLE_CHOICE_QUESTION = "MULTIPLE_CHOICE_QUESTION"


@dataclass
class Course:
    """Represents a Google Classroom course."""
    id: str
    name: str
    section: Optional[str] = None
    description: Optional[str] = None
    room: Optional[str] = None
    state: str = "ACTIVE"
    enrollment_code: Optional[str] = None
    alternate_link: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "Course":
        """Create Course from API response."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            section=data.get("section"),
            description=data.get("descriptionHeading"),
            room=data.get("room"),
            state=data.get("courseState", "ACTIVE"),
            enrollment_code=data.get("enrollmentCode"),
            alternate_link=data.get("alternateLink"),
        )


@dataclass
class Material:
    """Represents an attachment or material."""
    type: str  # driveFile, youtubeVideo, link, form
    title: Optional[str] = None
    url: Optional[str] = None
    drive_file_id: Optional[str] = None
    youtube_id: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "Material":
        """Create Material from API response."""
        if "driveFile" in data:
            drive = data["driveFile"]["driveFile"]
            return cls(
                type="driveFile",
                title=drive.get("title"),
                url=drive.get("alternateLink"),
                drive_file_id=drive.get("id"),
            )
        elif "youtubeVideo" in data:
            yt = data["youtubeVideo"]
            return cls(
                type="youtubeVideo",
                title=yt.get("title"),
                url=f"https://youtube.com/watch?v={yt.get('id', '')}",
                youtube_id=yt.get("id"),
            )
        elif "link" in data:
            link = data["link"]
            return cls(
                type="link",
                title=link.get("title"),
                url=link.get("url"),
            )
        elif "form" in data:
            form = data["form"]
            return cls(
                type="form",
                title=form.get("title"),
                url=form.get("formUrl"),
            )
        return cls(type="unknown")


@dataclass
class CourseWork:
    """Represents coursework (assignment, question, etc.)."""
    id: str
    course_id: str
    title: str
    work_type: str
    description: Optional[str] = None
    state: str = "PUBLISHED"
    max_points: Optional[float] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    materials: list[Material] = field(default_factory=list)
    alternate_link: Optional[str] = None
    creation_time: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "CourseWork":
        """Create CourseWork from API response."""
        # Parse materials
        materials = []
        for mat in data.get("materials", []):
            materials.append(Material.from_api(mat))

        # Parse due date
        due_date = None
        if "dueDate" in data:
            d = data["dueDate"]
            due_date = f"{d.get('year', 0):04d}-{d.get('month', 0):02d}-{d.get('day', 0):02d}"

        due_time = None
        if "dueTime" in data:
            t = data["dueTime"]
            due_time = f"{t.get('hours', 0):02d}:{t.get('minutes', 0):02d}"

        return cls(
            id=data.get("id", ""),
            course_id=data.get("courseId", ""),
            title=data.get("title", ""),
            work_type=data.get("workType", "ASSIGNMENT"),
            description=data.get("description"),
            state=data.get("state", "PUBLISHED"),
            max_points=data.get("maxPoints"),
            due_date=due_date,
            due_time=due_time,
            materials=materials,
            alternate_link=data.get("alternateLink"),
            creation_time=data.get("creationTime"),
        )


@dataclass
class CourseMaterial:
    """Represents course materials (resources for students)."""
    id: str
    course_id: str
    title: str
    description: Optional[str] = None
    state: str = "PUBLISHED"
    materials: list[Material] = field(default_factory=list)
    alternate_link: Optional[str] = None
    creation_time: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "CourseMaterial":
        """Create CourseMaterial from API response."""
        materials = []
        for mat in data.get("materials", []):
            materials.append(Material.from_api(mat))

        return cls(
            id=data.get("id", ""),
            course_id=data.get("courseId", ""),
            title=data.get("title", ""),
            description=data.get("description"),
            state=data.get("state", "PUBLISHED"),
            materials=materials,
            alternate_link=data.get("alternateLink"),
            creation_time=data.get("creationTime"),
        )


@dataclass
class Announcement:
    """Represents a course announcement."""
    id: str
    course_id: str
    text: str
    state: str = "PUBLISHED"
    materials: list[Material] = field(default_factory=list)
    alternate_link: Optional[str] = None
    creation_time: Optional[str] = None
    creator_user_id: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "Announcement":
        """Create Announcement from API response."""
        materials = []
        for mat in data.get("materials", []):
            materials.append(Material.from_api(mat))

        return cls(
            id=data.get("id", ""),
            course_id=data.get("courseId", ""),
            text=data.get("text", ""),
            state=data.get("state", "PUBLISHED"),
            materials=materials,
            alternate_link=data.get("alternateLink"),
            creation_time=data.get("creationTime"),
            creator_user_id=data.get("creatorUserId"),
        )


class ClassroomClient:
    """
    Google Classroom API client.

    Provides methods to list and retrieve courses, coursework,
    materials, and announcements.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Classroom client.

        Args:
            config: Configuration instance (uses global config if not provided)
        """
        self.config = config or get_config()
        self._service = None
        self._auth = OAuth2Flow(self.config)

    @property
    def service(self):
        """Get or create the Classroom API service."""
        if self._service is None:
            credentials = self._auth.get_credentials()
            if not credentials:
                raise RuntimeError(
                    "Not authenticated. Run 'python scripts/auth.py --setup' first."
                )
            self._service = build("classroom", "v1", credentials=credentials)
        return self._service

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self._auth.check_auth()

    # ========== Courses ==========

    def list_courses(self, state: Optional[str] = None) -> list[Course]:
        """
        List all accessible courses.

        Args:
            state: Filter by course state (ACTIVE, ARCHIVED, etc.)

        Returns:
            List of Course objects
        """
        courses = []
        page_token = None

        while True:
            params = {"pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            if state:
                params["courseStates"] = [state]

            response = self.service.courses().list(**params).execute()

            for course_data in response.get("courses", []):
                courses.append(Course.from_api(course_data))

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return courses

    def get_course(self, course_id: str) -> Course:
        """
        Get a specific course by ID.

        Args:
            course_id: The course ID

        Returns:
            Course object
        """
        response = self.service.courses().get(id=course_id).execute()
        return Course.from_api(response)

    # ========== Coursework ==========

    def list_coursework(
        self,
        course_id: str,
        state: str = "PUBLISHED"
    ) -> list[CourseWork]:
        """
        List coursework in a course.

        Args:
            course_id: The course ID
            state: Filter by state (PUBLISHED, DRAFT, etc.)

        Returns:
            List of CourseWork objects
        """
        coursework = []
        page_token = None

        while True:
            params = {"courseId": course_id, "pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            if state:
                params["courseWorkStates"] = [state]

            response = self.service.courses().courseWork().list(**params).execute()

            for work_data in response.get("courseWork", []):
                coursework.append(CourseWork.from_api(work_data))

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return coursework

    def get_coursework(self, course_id: str, coursework_id: str) -> CourseWork:
        """
        Get specific coursework by ID.

        Args:
            course_id: The course ID
            coursework_id: The coursework ID

        Returns:
            CourseWork object
        """
        response = (
            self.service.courses()
            .courseWork()
            .get(courseId=course_id, id=coursework_id)
            .execute()
        )
        return CourseWork.from_api(response)

    # ========== Course Materials ==========

    def list_materials(self, course_id: str) -> list[CourseMaterial]:
        """
        List course materials.

        Args:
            course_id: The course ID

        Returns:
            List of CourseMaterial objects
        """
        materials = []
        page_token = None

        while True:
            params = {"courseId": course_id, "pageSize": 100}
            if page_token:
                params["pageToken"] = page_token

            response = (
                self.service.courses()
                .courseWorkMaterials()
                .list(**params)
                .execute()
            )

            for mat_data in response.get("courseWorkMaterial", []):
                materials.append(CourseMaterial.from_api(mat_data))

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return materials

    def get_material(self, course_id: str, material_id: str) -> CourseMaterial:
        """
        Get specific course material by ID.

        Args:
            course_id: The course ID
            material_id: The material ID

        Returns:
            CourseMaterial object
        """
        response = (
            self.service.courses()
            .courseWorkMaterials()
            .get(courseId=course_id, id=material_id)
            .execute()
        )
        return CourseMaterial.from_api(response)

    # ========== Announcements ==========

    def list_announcements(self, course_id: str) -> list[Announcement]:
        """
        List course announcements.

        Args:
            course_id: The course ID

        Returns:
            List of Announcement objects
        """
        announcements = []
        page_token = None

        while True:
            params = {"courseId": course_id, "pageSize": 100}
            if page_token:
                params["pageToken"] = page_token

            response = (
                self.service.courses()
                .announcements()
                .list(**params)
                .execute()
            )

            for ann_data in response.get("announcements", []):
                announcements.append(Announcement.from_api(ann_data))

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return announcements
