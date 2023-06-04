from enum import Enum


class VersionAttributes(str, Enum):
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
