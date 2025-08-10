import os
import json
from icecream import ic
from dotenv import load_dotenv
import uuid

from sync_manager import SyncManager

load_dotenv()
DEBUG = os.environ.get("DEBUG", False)
PROJECTS_DIR = os.environ.get("PROJECTS_DIR")
# PROJECT_LIST_FILE = os.path.join(PROJECTS_DIR, "project_list.json")

class Project:
    def __init__(self, **kwargs):
        self._config = {
            "project_name": kwargs.get("project_name", ""),
            "project_path": kwargs.get("project_path", f"{os.path.join(PROJECTS_DIR, uuid.uuid4().hex)}.json"),
            "folder_a": kwargs.get("folder_a", ""),
            "folder_b": kwargs.get("folder_b", ""),
            "history": kwargs.get("history", {}),
        }
        self._sync_manager = SyncManager(**self._config)
        self._modified = False

    def __str__(self):
        return (f"Project: \"{self._config['project_name']}\", "
                f"Folder A: \"{self._config['folder_a']}\", Folder B: \"{self._config['folder_b']}\"")

    def __repr__(self):
        return self.__str__()

    def load_from_file(self):
        self._config.update(json.load(open(self._config["project_path"], "r")))
        self._sync_manager = SyncManager(**self._config)
        self._modified = False

    def save_to_file(self):
        self._config["history"] = self._sync_manager.history
        with open(self._config["project_path"], "w") as f:
            json.dump(self._config, f, indent=4)
            f.close()
        self._modified = False

    # @property
    # def sync_manager(self):
    #     return self._sync_manager

    @property
    def project_name(self):
        return self._config.get("project_name", "")

    @project_name.setter
    def project_name(self, value):
        if self._config["project_name"] == str(value):
            return
        self._config["project_name"] = str(value)
        self._modified = True

    @property
    def folder_a(self):
        return self._config.get("folder_a", "")

    @property
    def folder_b(self):
        return self._config.get("folder_b", "")

    @property
    def history(self):
        return self._config.get("history", {})

    # @history.setter
    # def history(self, value):
    #     if self._config["history"] == dict(value):
    #         return
    #     self._sync_manager.history = dict(value)
    #     self._config["history"] = self._sync_manager.history
    #     self._modified = True

    @property
    def modified(self):
        return self._modified

    def get_config(self):
        return self._config.copy()

    def get_folder_state(self, which: str):
        return self._sync_manager.get_folder_state(which)

    def prep_sync(self):
        self._sync_manager.prep_sync()

    def get_sync_actions(self):
        return self._sync_manager.sync_actions

    def has_sync_actions(self) -> bool:
        return (self._sync_manager.sync_actions is not None) and (len(self._sync_manager.sync_actions) > 0)

    def has_conflicts(self) -> bool:
        return self.has_sync_actions() and any("conflict" in self._sync_manager.sync_actions[action] for action in self._sync_manager.sync_actions)

    def get_conflicts(self) -> dict:
        if not self._sync_manager.sync_actions:
            return {}
        return {k: v for k, v in self._sync_manager.sync_actions.items() if "conflict" in v}

    def modify_action(self, rel_path: str, new_action: str):
        self._sync_manager.modify_action(rel_path, new_action)

    def get_future_common_state(self):
        return self._sync_manager.future_common_state

    def execute_sync(self):
        self._sync_manager.execute_sync()
        self._config["history"] = self._sync_manager.history
        self.save_to_file()
        self._modified = False

class ProjectManager:
    def __init__(self):
        self.projects = []
        self._active_project = None

    @property
    def active_project(self):
        return self._active_project

    @active_project.setter
    def active_project(self, value):
        self._active_project = value if isinstance(value, Project) else self.get_project_by_name(str(value))

    def load_projects(self):
        if not os.path.exists(PROJECTS_DIR):
            os.makedirs(PROJECTS_DIR)
        self.projects.clear()
        for project_path in [os.path.join(PROJECTS_DIR, fname) for fname in os.listdir(PROJECTS_DIR)]:
            if os.path.splitext(project_path)[1] != ".json":
                continue
            project_config = json.load(open(project_path, "r"))
            project_config["project_path"] = os.path.abspath(project_path)
            self.projects.append(Project(**project_config))

    def create_project(self, **kwargs):
        """
        Create a new project with the given configuration.

        This function creates a new Project object with the provided configuration,
        adds it to the projects list, and sets it as the active project.

        Args:
            **kwargs: Arbitrary keyword arguments.
                Possible keys include:
                - project_name (str): The name of the project.
                - local_path (str): The local path of the project.
                - remote_path (str): The remote path of the project.

        Returns:
            None

        Side effects:
            - Appends a new Project object to self.projects.
            - Sets self.active_project to the newly created project.
        """
        project = Project(**kwargs)
        self.projects.append(project)
        self._active_project = project

    def load_project_from_file(self, project_name):
        project = self.get_project_by_name(project_name)
        project.load_from_file()

    def save_active(self):
        if self._active_project:
            self._active_project.save_to_file()

    def save_active_as(self, new_project_name):
        if not self._active_project:
            return
        new_config = self._active_project.get_config()
        new_config["project_name"] = new_project_name
        del new_config["project_path"]
        new_project = Project(**new_config)
        self.projects.append(new_project)
        self._active_project = new_project
        self._active_project.save_to_file()

    def set_active_project(self, project_name):
        """
        Set the active project based on the given project name.

        This function searches through the list of projects and sets the active
        project to the project that matches the given project name.

        Args:
            project_name (str): The name of the project to set as active.

        Returns:
            None

        Side effects:
            - Sets self.active_project to the Project object matching the given name.
        """
        project = self.get_project_by_name(project_name)
        if project:
            self._active_project = project

    def get_project_by_name(self, project_name):
        """
        Retrieve a project from the project list by its name.

        This function searches through the list of projects and returns the project
        that matches the given project name.

        Args:
            project_name (str): The name of the project to search for.

        Returns:
            Project or None: The Project object if a match is found, None otherwise.
        """
        for project in self.projects:
            if project.project_name == project_name:
                return project
        return None
    
    def get_project_names(self):
        """
        Retrieve a list of all project names.

        This function iterates through all projects in the ProjectManager
        and returns a list containing the names of each project.

        Returns:
            list: A list of strings, where each string is the name of a project.
                  The list will be empty if there are no projects.
        """
        return [project.project_name for project in self.projects]


if __name__ == "__main__" and DEBUG:
    pm = ProjectManager()
    pm.load_projects()
    ic(pm.projects)