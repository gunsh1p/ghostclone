from enum import Enum


class ProjectType(str, Enum):
    JAVA = "Java"
    GO = "Golang"
    PYTHON = "Python"


class PipelineStatus(str, Enum):
    CREATED = "created"
    WAITING_FOR_RESOURCE = "waiting_for_resource"
    PREPARING = "preparing"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
