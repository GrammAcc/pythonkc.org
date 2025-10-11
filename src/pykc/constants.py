import enum
import functools
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/Chicago")

DATE_FORMAT = "%a %d %b %Y"
TIME_FORMAT = "%I:%M%p"
DATETIME_FORMAT = f"{DATE_FORMAT}, {TIME_FORMAT}"


class EventIntervalType(enum.IntEnum):
    """Represents the frequency for scheduling recurring events.

    Important:
        The integer values in this enum are significant and should not be changed.
        They are used as inputs for modular arithmetic when computing visit dates.
    """

    DAILY = 20
    WEEKLY = 21
    MONTHLY = 1
    QUARTERLY = 3
    SEMIYEARLY = 6
    YEARLY = 12


class App(enum.IntFlag):
    MEMBERS = enum.auto()
    EVENTS = enum.auto()
    CONTENT = enum.auto()


# Note: We use IntEnum instead of IntFlag because we are mostly using this
# enum in database operations or with integers coming from the database, so
# we don't gain much from the extra dunder methods of an IntFlag enum, and
# the implicit conversion between Flag and int provided by IntFlag will likely
# only make debugging more difficult when we see unexpected values in the logs.
class MemberPermissions(enum.IntEnum):
    """Enum representing specific permissions for actions that can be performed
    on the site. Member roles are formed by ORing together different permissions
    under each role.

    Security:
        Changes to this enum will affect user access at runtime since these
        permissions are stored in the database, so any deployment that includes
        a change to this enum MUST also include a data migration to reapply user roles
        for all existing members.

        This can be mitigated by storing the role name as a string value in the database
        and then mapping that to the appropriate permissions mask in the `MemberRoles` enum at
        runtime, but that requires some refactoring and a schema change, and it is uncommon that
        we will need to add/remove permissions, so that has not been implemented.
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 1 << count

    MODIFY_MEMBER_STATUS = 1
    MODIFY_EVENTS = 2
    MODIFY_PAGES = 4
    MODIFY_API_ACCESS = 8
    MODIFY_MEMBER_ROLES = 16


class MemberRoles(enum.IntEnum):
    """Enum representing groupings of different permissions as bitmasks to simplify setting
    role-based permissions on members."""

    MEMBER = 0
    MODERATOR = MemberPermissions.MODIFY_MEMBER_STATUS
    DEVELOPER = (
        MemberPermissions.MODIFY_PAGES
        | MemberPermissions.MODIFY_API_ACCESS
        | MemberPermissions.MODIFY_MEMBER_STATUS
    )
    EVENT_MANAGER = MemberPermissions.MODIFY_EVENTS | MemberPermissions.MODIFY_MEMBER_STATUS
    # Organizer has all permissions.
    ORGANIZER = functools.reduce(lambda acc, el: acc | el, list(MemberPermissions), 0)
