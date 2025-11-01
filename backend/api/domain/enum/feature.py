from enum import Enum


class Feature(str, Enum):
    CHAT = "chat"
    REPORT = "report"
    ANALYTICS = "analytics"
    ORGANIZATION = "organization"
    TEAMS = "teams"
    STRIPE = "stripe"
