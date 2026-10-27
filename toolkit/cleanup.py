import os
from pathlib import Path
import stat
import time

from .helpers import ToolError, confirm, format_bytes, logged_action, read_number, run_menu
from .cleanup_locations import discover_cleanup_locations
from .recycling import recycle_file
from .windows import is_fixed_drive


# Python OOP - Classes
class CleanupTool:
    def __init__(self, store):
        self.store = store
        self.user_temp = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Temp"
        self.windows_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        self.program_data = Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        self.device_locations = {}
        # Python Data Structures - List
        self.protected = [
            self.windows_root,
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
            self.program_data,
            Path(__file__).resolve().parents[1],
            self.store.folder.resolve(),
        ]
        self.appdata = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")).parent
        self.skipped_names = {".git", ".venv", "venv", "node_modules", "$recycle.bin",
                              "system volume information", "recovery", "config.msi",
                              "windows", "program files", "program files (x86)", "programdata",
                              "boot", "efi", "documents and settings"}

    def run(self):
        run_menu("CLEAN UP FILES", {
            "1": ("Scan a folder you choose", lambda: self.clean(False)),
            "2": ("Scan personal temporary files (at least 24 hours old)", lambda: self.clean(True)),
            "3": ("Scan this computer for junk and temporary files", self.clean_device),
        })

    def validate_path(self, path, cleanup_root=None):
        path = Path(os.path.abspath(path))
        scope = None
        if cleanup_root is not None:
            scope = Path(os.path.abspath(cleanup_root))
            # Python Flow Control - Conditionals
            if scope not in self.device_locations or not path.is_relative_to(scope):
                raise ToolError("The file is outside a recognized cleanup location.")
        if str(path).startswith("\\\\") or path == Path(path.anchor):
            raise ToolError("Choose a folder on a local fixed drive, below the drive root.")
        if not is_fixed_drive(path):
            raise ToolError("Cleanup supports local fixed drives only, where Windows can offer recycling.")
        # Python Flow Control - Loops
        for part in (path, *path.parents):
            info = part.lstat()
            attributes = getattr(info, "st_file_attributes", 0)
            if stat.S_ISLNK(info.st_mode) or attributes & 0x400:
                raise ToolError("Symbolic links, junctions, and other reparse points are skipped.")
            if part.name.casefold() in self.skipped_names:
                known_parent = (scope is not None and part in scope.parents
                                and part.name.casefold() in {"windows", "programdata"})
                if not known_parent:
                    raise ToolError("This folder is protected by the cleanup rules.")
        resolved = path.resolve(strict=True)
        for protected in self.protected:
            if resolved.is_relative_to(protected.resolve()):
                known_subtree = (scope is not None and protected in (self.windows_root, self.program_data)
                                 and scope != protected and scope.is_relative_to(protected))
                if not known_subtree:
                    raise ToolError("Windows, installed software, and Toolkit files are protected.")
        if (scope is None and resolved.is_relative_to(self.appdata.resolve())
                and not resolved.is_relative_to(self.user_temp.resolve())):
            raise ToolError("Application data is protected; use the personal Temp option instead.")
        if resolved in (Path.home().resolve(), Path.home().parent.resolve()):
            raise ToolError("Choose a specific folder, rather than an entire user profile.")
        return resolved

    def signature(self, info):
        # Python Data Structures - Tuple
        return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)

    # Python Recursion
    def scan_folder(self, folder, depth, cutoff=None, cleanup_root=None, suffixes=None):
        root = self.validate_path(folder, cleanup_root)
        if not root.is_dir():
            raise ToolError("The selected path is not a folder.")
        candidates = []
        # Python Data Structures - Set
        seen = set()
        stats = {"visited": 0, "skipped": 0, "limited": False}

        def visit(current, remaining):
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        if stats["visited"] >= 5000 or len(candidates) >= 200:
                            stats["limited"] = True
                            return
                        stats["visited"] += 1
                        try:
                            path = self.validate_path(Path(entry.path), cleanup_root)
                            info = path.lstat()
                            
                            if getattr(info, "st_file_attributes", 0) & (0x2 | 0x4):
                                stats["skipped"] += 1
                                continue
                            if stat.S_ISDIR(info.st_mode):
                                if remaining > 0:

                                    visit(path, remaining - 1)
                            elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                                if cutoff is not None and info.st_mtime > cutoff:
                                    continue
                                if suffixes is not None and path.suffix.casefold() not in suffixes:
                                    continue
                                key = os.path.normcase(str(path))
                                if key not in seen:
                                    seen.add(key)
                                    candidates.append({"path": path, "size": info.st_size,
                                                       "signature": self.signature(info), "root": root,
                                                       "cleanup_root": cleanup_root})
                        except (OSError, ToolError):
                            stats["skipped"] += 1
            except OSError:
                if current == root:
                    raise
                stats["skipped"] += 1

        visit(root, depth)
        # Python Lambda Functions
        candidates.sort(key=lambda candidate: candidate["size"], reverse=True)
        return root, candidates, stats

    @logged_action
    def clean(self, temporary=False):
        if temporary:
            folder = self.user_temp
            cutoff = time.time() - 24 * 60 * 60
        else:
            raw = input('Folder path (or 0 to cancel): ').strip().strip('"')
            if raw == "0":
                return "cancelled"
            if not raw:
                raise ValueError("Enter a folder path.")
            folder = Path(os.path.expandvars(raw)).expanduser()
            cutoff = None
        print("\nWhere should we look for files?")
        print("1. Only this folder")
        print("2. This folder and its subfolders (up to 5 levels)")
        print("0. Cancel")
        scan_choice = read_number("Choose an option: ", 0, 2)
        
        if scan_choice == 0:
            return "cancelled"
        depth = 5 if scan_choice == 2 else 0
        root, candidates, stats = self.scan_folder(folder, depth, cutoff)
        print(f"\nFolder: {root}\nSkipped/unreadable entries: {stats['skipped']}")
        if stats["limited"]:
            print("Preview limit reached (200 candidates or 5,000 entries). Choose a narrower folder for more.")
        return self.review_candidates(candidates, root)

    @logged_action
    def clean_device(self):
        print("\nCOMPUTER JUNK AND TEMPORARY FILES")
        print("Checking known cleanup locations on local drives and registered user profiles.")
        print("Temporary files must be at least 24 hours old; crash reports must be at least 7 days old.")
        print("Crash reports can help diagnose problems; review them before removing them.")
        print("Administrator access may be needed for Windows Temp and other users' folders.")
        locations, warnings = discover_cleanup_locations(self.user_temp)
        
        self.device_locations = {location["path"]: location for location in locations}
        for warning in warnings:
            print(f"Location discovery: {warning}")
        candidates = []
        seen = set()
        limited = False
        checked = 0
        skipped = 0
        now = time.time()
        for location in locations:
            print(f"\nChecking {location['label']}: {location['path']}")
            try:
                cutoff = now - location["days"] * 24 * 60 * 60
                root, found, stats = self.scan_folder(location["path"], 5, cutoff,
                                                       cleanup_root=location["path"],
                                                       suffixes=location["suffixes"])
                checked += 1
                skipped += stats["skipped"]
                limited = limited or stats["limited"]
                print(f"  Found {len(found)} candidates; skipped/unreadable entries: {stats['skipped']}")
                for candidate in found:
                    key = os.path.normcase(str(candidate["path"]))
                    if key not in seen:
                        seen.add(key)
                        candidate["source"] = location["label"]
                        candidates.append(candidate)
                
                candidates.sort(key=lambda candidate: candidate["size"], reverse=True)
                if len(candidates) > 1000:
                    candidates = candidates[:1000]
                    limited = True
            except FileNotFoundError:
                print("  Not present on this computer.")
            except PermissionError:
                print("  Access denied. Run as administrator to include this location.")
            except (OSError, ToolError) as error:
                print(f"  Skipped: {error}")
        print(f"\nChecked {checked}/{len(locations)} known locations; skipped/unreadable entries: {skipped}.")
        print("This checks common cleanup folders; personal documents and installed apps are not searched.")
        if limited:
            print("Preview is limited: up to 200 files/5,000 entries per location and 1,000 files overall.")
        print("Subfolders are included up to 5 levels. Totals cover only the displayed candidates.")
        return self.review_candidates(candidates)

    
    def review_candidates(self, candidates, root=None):
        if not candidates:
            print("No eligible files were found within these scan limits.")
            return "no candidates"
        print("These files are candidates you must review; the app cannot know whether they are useful.")
        for number, candidate in enumerate(candidates, start=1):
            display_path = candidate["path"].relative_to(root) if root is not None else candidate["path"]
            print(f"{number:>3}. {format_bytes(candidate['size']):>12}  {display_path}")
            if "source" in candidate:
                print(f"     {candidate['source']}")
        total = sum(candidate["size"] for candidate in candidates)
        print(f"Preview total: {len(candidates)} files, {format_bytes(total)}")
        print("Windows will be asked to move them to the Recycle Bin. No folders are removed.")
        print("Space is usually not reclaimed until you empty the Recycle Bin yourself.")
        if not confirm(f"Clean all {len(candidates)} files shown above?"):
            return "cancelled"
        recycled = 0
        for candidate in candidates:
            try:
                path = self.validate_path(candidate["path"], candidate.get("cleanup_root"))
                selected_root = candidate.get("root", root)
                if selected_root is None or not path.is_relative_to(selected_root):
                    raise ToolError("The file is no longer inside the selected folder.")
                info = path.lstat()
                if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                        or getattr(info, "st_file_attributes", 0) & (0x2 | 0x4)
                        or self.signature(info) != candidate["signature"]):
                    raise ToolError("The file changed after the preview; scan it again.")
                
                recycle_file(path)
                recycled += 1
                print(f"Recycling request completed: {path.name}")
            except (OSError, ToolError) as error:
                print(f"Skipped {candidate['path'].name}: {error}")
        print(f"Completed {recycled}/{len(candidates)} recycling requests. Check the Recycle Bin to restore files.")
        return f"recycled {recycled}/{len(candidates)}"
