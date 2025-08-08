# Improvements:
# - deal with empty folders
# - add ignore list
# - backup new and modified files
# - recover a file version from a previous sync
import errno
import hashlib
import json
import os
import logging
import shutil
from datetime import datetime

from dotenv import load_dotenv
from icecream import ic

load_dotenv()
DEBUG = bool(int(os.environ.get("DEBUG", 0)))


def set_logger(logger_name, level=logging.WARNING, fmt='%(asctime)s - %(levelname)s - %(message)s', stream=True,
               log_file=None):
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(stream_handler)
    if (log_file is not None) and (log_file != ''):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(file_handler)
    logger.setLevel(level)
    logger.propagate = False

set_logger("SYNC", level=logging.DEBUG if DEBUG else logging.INFO, log_file="sync_manager.log")
logger = logging.getLogger("SYNC")





class SyncManager:
    def __init__(self, **kwargs):
        self._folder_a, self._folder_b = None, None
        self._set_folder("A", kwargs.get("folder_a", None))
        self._set_folder("B", kwargs.get("folder_b", None))
        self._history = kwargs.get("history", {})
        self._future_common_state = {}
        self._sync_actions = {}
        # self._history_file = kwargs.get("history_file", "sync_history.json")
        logger.debug("SyncManager initialized")

    @property
    def folder_a(self):
        return self._folder_a

    @folder_a.setter
    def folder_a(self, value):
        self._set_folder("A", value)

    @property
    def folder_b(self):
        return self._folder_b

    @folder_b.setter
    def folder_b(self, value):
        self._set_folder("B", value)

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value):
        self._history = dict(value)

    @property
    def sync_actions(self):
        return self._sync_actions

    @property
    def future_common_state(self):
        return self._future_common_state

    def get_latest_history(self):
        return self._history[max(self._history.keys())] if self._history else None

    def _set_folder(self, which: str, value):
        if not value:
            setattr(self, f"_folder_{which.lower()}", None)
            logger.debug(f"Folder {which.upper()} set to None")
            return
        # Assume the value is a valid directory, check only if it exists.
        if not os.path.exists(value):
            logger.debug(f"Folder {which.upper()} does not exist and is being created: \"{value}\"")
            os.makedirs(value)
        setattr(self, f"_folder_{which.lower()}", value)
        logger.debug(f"Folder {which.upper()} set to: \"{value}\"")

    # def sync(self):
    #     """
    #     Synchronize files and folders between two directories.
    #
    #     This method scans both folders for changes, compares them with the previous sync history,
    #     and performs the necessary actions to keep both folders in sync. It handles file creation,
    #     deletion, and modification, as well as conflict resolution when files are modified in both folders.
    #
    #     The synchronization process includes the following steps:
    #     1. Scan both folders and compare with the previous sync history.
    #     2. Identify new, modified, and deleted files/folders.
    #     3. Copy new and modified files/folders to the other directory.
    #     4. Delete files/folders that have been removed from one directory.
    #     5. Handle conflicts by creating conflict copies when files are modified in both directories.
    #     6. Update the sync history with the new state of both folders.
    #
    #     This method does not take any parameters and does not return any value.
    #     The synchronization results are logged using the configured logger.
    #
    #     Raises:
    #         Any exceptions that occur during file operations (e.g., PermissionError, IOError)
    #         will be logged as errors but not explicitly raised by this method.
    #     """
    #     # Scan both folders for changes and update history
    #     folder_states = [self.scan_folder(self.folder_a), self.scan_folder(self.folder_b)]
    #     common_state = self._history[sorted(self._history.keys())[-1]] if self._history else {}
    #     new_common_state = {}
    #     # Run through all files in both folders and history
    #     union_list = set(list(folder_states[0].keys()) + list(folder_states[1].keys()) + list(common_state.keys()))
    #     logger.info("Sync started")
    #     for rel_path in union_list:
    #         props_a = folder_states[0].get(rel_path, {})
    #         props_b = folder_states[1].get(rel_path, {})
    #         props_history = common_state.get(rel_path, {})
    #         if props_a and props_b:
    #             # Exists in both folders
    #             if props_a['hash'] == props_b['hash']:
    #                 # Files/Folders are identical, no action needed
    #                 new_common_state[rel_path] = props_a
    #                 logger.debug(f"{props_a.get('type').title()} \"{rel_path}\" is identical in both folders")
    #             elif props_a['hash'] == props_history.get('hash'):
    #                 # File B has changed, copy to A
    #                 self._copy_file(self.folder_b, self.folder_a, rel_path)
    #                 new_common_state[rel_path] = props_b
    #                 logger.info(f"{props_a.get('type').title()} \"{rel_path}\" updated in folder B, copying to folder A")
    #             elif props_b['hash'] == props_history.get('hash'):
    #                 # File A has changed, copy to B
    #                 self._copy_file(self.folder_a, self.folder_b, rel_path)
    #                 new_common_state[rel_path] = props_a
    #                 logger.info(f"{props_a.get('type').title()} \"{rel_path}\" updated in folder A, copying to folder B")
    #             else:
    #                 # Both files have changed, create conflict copies
    #                 new_file_a, new_file_b = self._handle_conflict(rel_path, props_a, props_b)
    #                 new_common_state[new_file_a] = SyncManager.get_props(os.path.join(self.folder_a, new_file_a), new_file_a)
    #                 new_common_state[new_file_b] = SyncManager.get_props(os.path.join(self.folder_b, new_file_b), new_file_b)
    #                 tag = "updated" if props_history else "created"
    #                 logger.info(f"File \"{rel_path}\" {tag} in both folders, creating conflict copies \"{new_file_a}\" and \"{new_file_b}\"")
    #         elif props_a:
    #             # File/Folder exists only in folder A
    #             if props_history:
    #                 # File was deleted from B, delete from A
    #                 if props_history.get("type") == "file":
    #                     self._delete_file(self.folder_a, rel_path)
    #                 else:
    #                     self._delete_folder(self.folder_a, rel_path)
    #                 logger.info(f"File \"{rel_path}\" deleted from folder B, removing from folder A")
    #             else:
    #                 # New file in A, copy to B
    #                 if props_a.get("type") == "file":
    #                     self._copy_file(self.folder_a, self.folder_b, rel_path)
    #                 else:
    #                     self._create_folder(self.folder_b, rel_path)
    #                 new_common_state[rel_path] = props_a
    #                 logger.info(f"New file \"{rel_path}\" in folder A, copying to folder B")
    #         elif props_b:
    #             # File/Folder exists only in folder B
    #             if props_history:
    #                 # File was deleted from A, delete from B
    #                 if props_history.get("type") == "file":
    #                     self._delete_file(self.folder_b, rel_path)
    #                 else:
    #                     self._delete_folder(self.folder_b, rel_path)
    #                 logger.info(f"File \"{rel_path}\" deleted from folder A, removing from folder B")
    #             else:
    #                 # New file/folder in B, copy to A
    #                 if props_b.get("type") == "file":
    #                     self._copy_file(self.folder_b, self.folder_a, rel_path)
    #                 else:
    #                     self._create_folder(self.folder_a, rel_path)
    #                 new_common_state[rel_path] = props_b
    #                 logger.info(f"New file \"{rel_path}\" in folder B, copying to folder A")
    #     # Update history
    #     self._history[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = new_common_state
    #     logger.info("Sync finished")

    def prep_sync(self):
        # Scan both folders for changes and update history
        folder_states = [self.scan_folder(self.folder_a), self.scan_folder(self.folder_b)]
        common_state = self._history[sorted(self._history.keys())[-1]] if self._history else {}
        self._sync_actions = {}
        self._future_common_state = {}
        # Run through all files in both folders and history
        union_list = set(list(folder_states[0].keys()) + list(folder_states[1].keys()) + list(common_state.keys()))
        for rel_path in union_list:
            props_a = folder_states[0].get(rel_path, {})
            props_b = folder_states[1].get(rel_path, {})
            props_history = common_state.get(rel_path, {})
            if props_a and props_b:
                # Exists in both folders
                if props_a['hash'] == props_b['hash']:
                    # Files/Folders are identical, no action needed
                    self._sync_actions[rel_path] = "no action"
                    self._future_common_state[rel_path] = props_a | {"tag": "unchanged" if props_history else "new a b"}
                elif props_a['hash'] == props_history.get('hash'):
                    # File B has changed, copy to A
                    self._sync_actions[rel_path] = "copy file to A"
                    self._future_common_state[rel_path] = props_b | {"tag": "updated b"}
                elif props_b['hash'] == props_history.get('hash'):
                    # File A has changed, copy to B
                    self._sync_actions[rel_path] = "copy file to B"
                    self._future_common_state[rel_path] = props_a | {"tag": "updated a"}
                else:
                    # Both files have changed, create conflict copies
                    self._sync_actions[rel_path] = "conflict keep both"
                    self._future_common_state[rel_path] = {f"{k}_a": v for (k, v) in props_a.items() if k != "type"} | {
                        f"{k}_b": v for (k, v) in props_b.items() if k != "type"} | {"tag": "conflict",
                                                                                     "type": props_a.get("type")}
            elif props_a:
                # File/Folder exists only in folder A
                if props_history:
                    # File was deleted from B, delete from A
                    if props_history.get("type") == "file":
                        self._sync_actions[rel_path] = "delete file from A"
                    else:
                        self._sync_actions[rel_path] = "delete folder from A"
                    self._future_common_state[rel_path] = props_a | {"tag": "deleted b"}
                else:
                    # New file in A, copy to B
                    if props_a.get("type") == "file":
                        self._sync_actions[rel_path] = "copy file to B"
                    else:
                        self._sync_actions[rel_path] = "create folder in B"
                    self._future_common_state[rel_path] = props_a | {"tag": "new a"}
            elif props_b:
                # File/Folder exists only in folder B
                if props_history:
                    # File was deleted from A, delete from B
                    if props_history.get("type") == "file":
                        self._sync_actions[rel_path] = "delete file from B"
                    else:
                        self._sync_actions[rel_path] = "delete folder from B"
                    self._future_common_state[rel_path] = props_b | {"tag": "deleted a"}
                else:
                    # New file/folder in B, copy to A
                    if props_b.get("type") == "file":
                        self._sync_actions[rel_path] = "copy file to A"
                    else:
                        self._sync_actions[rel_path] = "create folder in A"
                    self._future_common_state[rel_path] = props_b | {"tag": "new b"}
        return self._sync_actions

    def modify_action(self, rel_path: str, new_action: str):
        if rel_path not in self._sync_actions:
            raise ValueError(f"No action found for file/folder \"{rel_path}\"")
        self._sync_actions[rel_path] = new_action

    def execute_sync(self, sync_actions: dict = None):
        if not sync_actions:
            sync_actions = self._sync_actions
        new_common_list = {}
        for rel_path, action in sync_actions.items():
            if action == "no action":
                new_common_list[rel_path] = self.get_props(str(os.path.join(self.folder_a, rel_path)), rel_path)
            elif action == "copy file to A":
                self._copy_file(self.folder_b, self.folder_a, rel_path)
                new_common_list[rel_path] = self.get_props(str(os.path.join(self.folder_b, rel_path)), rel_path)
            elif action == "copy file to B":
                self._copy_file(self.folder_a, self.folder_b, rel_path)
                new_common_list[rel_path] = self.get_props(str(os.path.join(self.folder_a, rel_path)), rel_path)
            elif action == "create folder in A":
                self._create_folder(self.folder_a, rel_path)
                new_common_list[rel_path] = self.get_props(str(os.path.join(self.folder_b, rel_path)), rel_path)
            elif action == "create folder in B":
                self._create_folder(self.folder_b, rel_path)
                new_common_list[rel_path] = self.get_props(str(os.path.join(self.folder_a, rel_path)), rel_path)
            elif action == "delete file from A":
                self._delete_file(self.folder_a, rel_path)
            elif action == "delete file from B":
                self._delete_file(self.folder_b, rel_path)
            elif action == "delete folder from A":
                self._delete_folder(self.folder_a, rel_path)
            elif action == "delete folder from B":
                self._delete_folder(self.folder_b, rel_path)
            elif action.startswith("conflict"):
                props_a = self.get_props(str(os.path.join(self._folder_a, rel_path)), rel_path)
                props_b = self.get_props(str(os.path.join(self._folder_b, rel_path)), rel_path)
                if action.endswith("keep A"):
                    self._copy_file(self.folder_a, self.folder_b, rel_path)
                    new_common_list[rel_path] = props_a
                elif action.endswith("keep B"):
                    self._copy_file(self.folder_b, self.folder_a, rel_path)
                    new_common_list[rel_path] = props_b
                elif action.endswith("both"):
                    new_file_a, new_file_b = self._handle_conflict(rel_path, props_a, props_b)
                    new_common_list[new_file_a] = self.get_props(str(os.path.join(self.folder_a, new_file_a)), new_file_a)
                    new_common_list[new_file_b] = self.get_props(str(os.path.join(self.folder_b, new_file_b)), new_file_b)
                else:
                    logger.error(f"Invalid conflict resolution action: {action}")
                    raise ValueError(f"Invalid conflict resolution action: {action}")
            else:
                logger.error(f"Invalid action: {action}")
                raise ValueError(f"Invalid action: {action}")
        # Reset common state and sync actions
        self._future_common_state = {}
        self._sync_actions = {}
        # Update history
        self._history[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = new_common_list

    @staticmethod
    def _copy_file(src_folder: str, dest_folder: str, src_relpath: str, dest_relpath: str = None):
        if not dest_relpath:
            dest_relpath = src_relpath
        src_path = os.path.join(src_folder, src_relpath)
        dst_path = os.path.join(dest_folder, dest_relpath)
        try:
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            if os.path.exists(dst_path):
                os.remove(dst_path)  # Remove the existing file to avoid any issues with permissions
            shutil.copy2(src_path, dst_path)
        except PermissionError:
            logger.error(f"Permission denied when copying file: \"{src_path}\" -> \"{dst_path}\"")
        except FileNotFoundError:
            logger.error(f"Source file not found: \"{src_path}\"")
        except Exception as e:
            logger.error(f"Error copying file: \"{src_path}\" -> \"{dst_path}\". Error: {str(e)}")

    @staticmethod
    def _create_folder(folder: str, folder_relpath: str):
        folder_path = os.path.join(folder, folder_relpath)
        try:
            os.makedirs(folder_path, exist_ok=True)
            logger.debug(f"Folder created or already exists: \"{folder_path}\"")
        except PermissionError:
            logger.error(f"Permission denied when creating folder: \"{folder_path}\"")
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(f"Error creating folder: \"{folder_path}\". Error: {str(e)}")
            else:
                logger.debug(f"Folder already exists: \"{folder_path}\"")
        except Exception as e:
            logger.error(f"Unexpected error creating folder: \"{folder_path}\". Error: {str(e)}")

    @staticmethod
    def _delete_file(folder: str, file_relpath: str):
        file_path = os.path.join(folder, file_relpath)
        try:
            os.remove(file_path)
            logger.info(f"File successfully deleted: \"{file_path}\"")
        except FileNotFoundError:
            logger.warning(f"File not found when attempting to delete: \"{file_path}\"")
        except PermissionError:
            logger.error(f"Permission denied when deleting file: \"{file_path}\"")
        except IsADirectoryError:
            logger.error(f"Cannot delete \"{file_path}\": It's a directory, not a file")
        except OSError as e:
            if e.errno == errno.ENOTEMPTY:
                logger.error(f"Cannot delete \"{file_path}\": Directory not empty")
            else:
                logger.error(f"Error deleting file: \"{file_path}\". Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting file: \"{file_path}\". Error: {str(e)}")

    @staticmethod
    def _delete_folder(folder: str, folder_relpath: str):
        folder_path = os.path.join(folder, folder_relpath)
        try:
            shutil.rmtree(folder_path)
            logger.info(f"Folder successfully deleted: \"{folder_path}\"")
        except FileNotFoundError:
            logger.warning(f"Folder not found when attempting to delete: \"{folder_path}\"")
        except PermissionError:
            logger.error(f"Permission denied when deleting folder: \"{folder_path}\"")
        except OSError as e:
            if e.errno == errno.ENOTEMPTY:
                logger.error(f"Cannot delete \"{folder_path}\": Directory not empty")
            elif e.errno == errno.ENOTDIR:
                logger.error(f"Cannot delete \"{folder_path}\": Not a directory")
            else:
                logger.error(f"Error deleting folder: \"{folder_path}\". Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting folder: \"{folder_path}\". Error: {str(e)}")

    def _handle_conflict(self, file_relpath, file_a, file_b):
        # Create conflict copies in both folders
        relpath, ext = os.path.splitext(file_relpath)
        conflict_name_a = f"{relpath}_A{ext}"
        conflict_name_b = f"{relpath}_B{ext}"
        try:
            # Copy A's version to both folders
            self._copy_file(self.folder_a, self.folder_a, file_relpath, conflict_name_a)
            self._copy_file(self.folder_a, self.folder_b, file_relpath, conflict_name_a)
            # Copy B's version to both folders
            self._copy_file(self.folder_b, self.folder_a, file_relpath, conflict_name_b)
            self._copy_file(self.folder_b, self.folder_b, file_relpath, conflict_name_b)
            # Delete original files
            self._delete_file(self.folder_a, file_relpath)
            self._delete_file(self.folder_b, file_relpath)
            logger.info(
                f"Conflict handled for file: \"{file_relpath}\". Created copies: \"{conflict_name_a}\" and \"{conflict_name_b}\"")
            return conflict_name_a, conflict_name_b
        except Exception as e:
            logger.error(f"Error handling conflict for file: \"{file_relpath}\". Error: {str(e)}")

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def get_props(full_path: str, rel_path: str = None) -> dict:
        return {
            "type": "folder" if os.path.isdir(full_path) else "file",
            "ctime": os.path.getctime(full_path),
            "mtime": os.path.getmtime(full_path),
            "hash": SyncManager.calculate_file_hash(full_path) if os.path.isfile(full_path) else rel_path,
            "size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0,
        }

    @staticmethod
    def scan_folder(folder: str) -> dict:
        fmap = {}
        for root, dirs, files in os.walk(folder):
            for local_name in dirs + files:
                full_path = os.path.join(root, local_name)
                try:
                    rel_path = os.path.relpath(full_path, folder)
                    fmap[rel_path] = SyncManager.get_props(full_path, rel_path)
                except Exception as e:
                    logger.error(f"Error calculating hash for {'directory' if os.path.isdir(full_path) else 'file'} \"{full_path}\": {str(e)}")
        return fmap

    def get_folder_state(self, which: str):
        if which.lower() == "a":
            return self.scan_folder(self._folder_a)
        if which.lower() == "b":
            return self.scan_folder(self._folder_b)
        if which.lower().startswith("c"):
            return self.get_latest_history()
        if which.lower().startswith("f"):
            return self._future_common_state
        raise ValueError(f"Invalid folder: {which}")



if __name__ == "__main__":

    def set_logger(logger_name, level=logging.WARNING, fmt='%(asctime)s - %(levelname)s - %(message)s', stream=True, log_file=None):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        if stream:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(fmt))
            logger.addHandler(stream_handler)
        if (log_file is not None) and (log_file != ''):
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(fmt))
            logger.addHandler(file_handler)
        logger.setLevel(level)
        logger.propagate = False

    set_logger("SYNC", level=logging.DEBUG if DEBUG else logging.INFO, log_file="sync_manager.log")

    sync_manager = SyncManager()
    # sync_manager.folder_a = r"C:\Users\S7U05901\OneDrive - Subsea7\Documents\Projects\2025-05 DSVi SWIM Umbilical Replacement\Calculations"
    # sync_manager.folder_b = r"O:\S7EN-STRUCTURAL DESIGN FOR OPERATIONS\Projects\2025\DSVi\SWIM Umbilical Replacement\Calculations"
    sync_manager.folder_a = r"D:\temp\test_a"
    sync_manager.folder_b = r"D:\temp\test_b"
    sync_manager.history = json.load(open(r"D:\Users\edute\Dropbox\Programming\Python\Projects\FolderTracker\projects\project_test.json", "r"))["history"]
    # sync_manager.history_file = "history_test.json"
    # sync_manager.load_history()
    # sync_manager.sync()
    # sync_manager.save_history()
    sync_actions = sync_manager.prep_sync()
    sync_manager.execute_sync(sync_actions)

