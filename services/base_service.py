"""
services/base_service.py
Base class for the service menus to avoid repeating menu and delete code.
"""
from storage import save_data
from utils import (
    print_header,
    print_success,
    print_error,
    print_info,
    prompt_select,
    confirm_delete,
    InputCancelled
)

CANCEL_LABEL = "❌ Cancel"
BACK_LABEL = "🔙 Back to Main Menu"


def generate_next_id(items, prefix, id_attr):
    # Generate the next ID like SUB-001, SUB-002, etc.
    max_num = 0
    for item in items:
        value = getattr(item, id_attr)
        if value.startswith(prefix + "-"):
            num_part = value[len(prefix) + 1:]
            if num_part.isdigit():
                max_num = max(max_num, int(num_part))
    return f"{prefix}-{max_num + 1:03d}"


class BaseService:
    section_title = "Section"
    section_subtitle = ""
    menu_prompt = "Select an option:"
    menu_options = []

    def __init__(self, data):
        self.data = data

    def can_open(self):
        return True

    def can_delete(self, target):
        return True

    def save(self):
        if not save_data(self.data):
            print_error("Failed to save data to the file.")

    def next_id(self, items_key, prefix, id_attr):
        return generate_next_id(self.data[items_key], prefix, id_attr)

    def select_item(self, items, label_fn, message, with_cancel=True):
        labels = [label_fn(item) for item in items]
        if with_cancel:
            labels.append(CANCEL_LABEL)
        choice = prompt_select(message, labels)
        if choice is None or choice == CANCEL_LABEL:
            return None
        return items[labels.index(choice)]

    def select_subject(self, message="Select Course:"):
        subjects = self.data["subjects"]
        if not subjects:
            print_error("Please add a subject first.")
            return None
        return self.select_item(
            subjects,
            lambda s: f"[{s.subject_id}] {s.code} - {s.name}",
            message,
            with_cancel=False
        )

    def delete_record(self, items_key, label_fn, noun):
        # Select an item, ask for confirmation, then delete and save
        items = self.data[items_key]
        if not items:
            print_info(f"No {noun}s available.")
            return

        target = self.select_item(items, label_fn, f"Select {noun} to delete:")
        if target is None:
            return
        if not self.can_delete(target):
            return

        if confirm_delete(f"Are you sure you want to delete {label_fn(target)}?"):
            items.remove(target)
            self.save()
            print_success(f"{noun.capitalize()} deleted successfully.")
        else:
            print_info("Deletion cancelled.")

    def run(self):
        # Main loop for the current service menu
        while True:
            if not self.can_open():
                return

            print_header(self.section_title, self.section_subtitle)
            labels = [f"{i}. {label}" for i, (label, _) in enumerate(self.menu_options, 1)]
            labels.append(f"{len(self.menu_options) + 1}. {BACK_LABEL}")

            choice = prompt_select(self.menu_prompt, labels)
            if choice is None:
                return

            index = labels.index(choice)
            if index == len(self.menu_options):
                return

            method = getattr(self, self.menu_options[index][1])
            try:
                method()
            except InputCancelled:
                print_info("Action cancelled. Returning to menu.")