from data_manager import load_data, save_data


GROUPS_FILE = "groups.json"
USERS_FILE = "users.json"


def create_group(name, description, created_by):
    """Create a new work group."""

    name = name.strip()
    description = description.strip()

    if not name:
        return False, "Group name cannot be empty."

    if not name[0].isascii() or not name[0].isalpha():
        return False, "Group name must start with an English letter."

    groups = load_data(GROUPS_FILE)

    for group in groups:
        if group.get("name", "").lower() == name.lower():
            return False, "Group name already exists."

    group_id = max(
        (group.get("id", 0) for group in groups),
        default=0
    ) + 1

    new_group = {
        "id": group_id,
        "name": name,
        "description": description,
        "created_by": created_by,
        "members": []
    }

    groups.append(new_group)
    save_data(GROUPS_FILE, groups)

    return True, f"Group '{name}' created successfully. ID: {group_id}"


def get_all_groups():
    """Return all work groups."""

    return load_data(GROUPS_FILE)


def get_group_by_id(group_id):
    """Find a group using its ID."""

    groups = load_data(GROUPS_FILE)

    for group in groups:
        if group.get("id") == group_id:
            return group

    return None


def add_member_to_group(group_id, username):
    """Add an active team member to a group."""

    groups = load_data(GROUPS_FILE)
    users = load_data(USERS_FILE)

    group = next(
        (item for item in groups if item.get("id") == group_id),
        None
    )

    if group is None:
        return False, "Group not found."

    user = next(
        (
            item for item in users
            if item.get("username", "").lower() == username.strip().lower()
            and item.get("role") == "member"
            and item.get("active", True)
        ),
        None
    )

    if user is None:
        return False, "Active team member not found."

    if any(
        member.lower() == user["username"].lower()
        for member in group["members"]
    ):
        return False, "User is already in this group."

    group["members"].append(user["username"])
    save_data(GROUPS_FILE, groups)

    return True, f"{user['username']} added to '{group['name']}'."


def remove_member_from_group(group_id, username):
    """Remove a member from a group."""

    groups = load_data(GROUPS_FILE)

    group = next(
        (item for item in groups if item.get("id") == group_id),
        None
    )

    if group is None:
        return False, "Group not found."

    member = next(
        (
            item for item in group["members"]
            if item.lower() == username.strip().lower()
        ),
        None
    )

    if member is None:
        return False, "Member is not in this group."

    group["members"].remove(member)
    save_data(GROUPS_FILE, groups)

    return True, f"{member} removed from '{group['name']}'."


def get_group_members(group_id):
    """Return the usernames belonging to a group."""

    group = get_group_by_id(group_id)

    if group is None:
        return []

    return group["members"]
