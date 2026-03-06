from enum import Enum as PyEnum


class UserStatusEnum(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class RoleTypeEnum(str, PyEnum):
    CUSTOMER = "customer"
    AGENT = "agent"
    MECHANIC = "mechanic"
    ADMIN = "admin"
    HUB_MANAGER = "hub_manager"
    TECHNICIAN = "technician"
