import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
import os
from dotenv import load_dotenv
from icecream import ic
from PIL import Image, ImageTk
# import ttkbootstrap as tb

from project_manager import ProjectManager

load_dotenv()
DEBUG = os.environ.get("DEBUG", False)
PROJECTS_DIR = os.environ.get("PROJECTS_DIR")
PROJECT_LIST_FILE = os.path.join(PROJECTS_DIR, "project_list.json")
ICON_FILE = str(os.environ.get("ICON_FILE"))


class OpenProjectDialog(simpledialog.Dialog):
    def __init__(self, parent, title="Open Project", project_names=None):
        self.selection = None
        self.listbox = None
        self.project_names = project_names if project_names else []
        super().__init__(parent, title=title)
        # self.iconbitmap(ICON_FILE)

    def body(self, master):
        tk.Label(master, text="Select a Project:").pack(padx=10, pady=10)
        self.listbox = tk.Listbox(master, selectmode=tk.SINGLE)
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        if self.project_names:
            for project_name in self.project_names:
                self.listbox.insert(tk.END, project_name)
            self.listbox.select_set(0)
        return self.listbox

    def apply(self):
        selection = self.listbox.curselection()
        if selection:
            self.selection = self.listbox.get(selection[0])


class AboutDialog(simpledialog.Dialog):
    def __init__(self, parent, title="About Folder Sync"):
        super().__init__(parent, title=title)
        # self.iconbitmap(ICON_FILE)
        self.logo = None

    def body(self, master):
        try:
            img = Image.open(ICON_FILE)
            img = img.resize((64, 64))
            self.logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(master, image=self.logo)
            logo_label.pack(pady=(20, 10))
        except Exception:
            tk.Label(master, text="[Logo not found]").pack(pady=(20, 10))

        tk.Label(master, text="Folder Sync", font=("Helvetica", 14, "bold")).pack(pady=5)
        tk.Label(master, text="Version 1.0").pack()
        tk.Label(master, text="© 2025 Eduardo Tenório Bastos").pack(pady=(0, 10))
        tk.Label(
            master,
            text="A utility to synchronize folders.",
            wraplength=250,
            justify=tk.CENTER
        ).pack(pady=10)

        return None  # No initial focus widget

    def buttonbox(self):
        box = tk.Frame(self)
        ttk.Button(box, text="Close", width=10, command=self.ok).pack(pady=10)
        box.pack()



class FileTree(ttk.Treeview):
    def __init__(self, master, path=None, **kwargs):
        super().__init__(master)
        self.path = path
        # self.tag_configure('folder', foreground='black', font=("", 10, 'bold'))
        # self.tag_configure('folder_empty', foreground='gray', font=("", 10, "italic"))
        # self.tag_configure('file', foreground='black', font=("", 10))
        self.icon_file = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-file-16.png")))
        self.icon_delete_file = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-delete-file-16.png")))
        self.icon_new_file = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-new-file-16.png")))
        self.icon_update_file = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-update-file-16.png")))
        self.icon_conflict_file = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-conflict-file-16.png")))
        self.icon_folder = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-folder-16.png")))
        self.icon_delete_folder = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-delete-folder-16.png")))
        self.icon_new_folder = ImageTk.PhotoImage(Image.open(os.path.join("img", "icons8-new-folder-16.png")))
        self.tag_configure("file", image=self.icon_file)
        self.tag_configure("delete file", image=self.icon_delete_file, foreground="red")
        self.tag_configure("new file", image=self.icon_new_file, foreground="green")
        self.tag_configure("update file", image=self.icon_update_file, foreground="blue")
        self.tag_configure("conflict file", image=self.icon_conflict_file, background="yellow", foreground="blue")
        self.tag_configure("folder", image=self.icon_folder)
        self.tag_configure("delete folder", image=self.icon_delete_folder, foreground="red")
        self.tag_configure("new folder", image=self.icon_new_folder, foreground="green")
        # self.tag_configure("unchanged")
        # self.tag_configure("new a")
        # self.tag_configure("new b")
        # self.tag_configure("new a b")
        # self.tag_configure("updated a")
        # self.tag_configure("updated b")
        # self.tag_configure("conflict")
        # self.tag_configure("deleted a")
        # self.tag_configure("deleted b")
        # self.build_tree("", path)
        self["show"] = "tree"  # remove the header row and make the tree look more like a list

    # def build_tree(self, parent, path):
    #     if not path:
    #         return
    #     try:
    #         entries = sorted(os.listdir(path))
    #     except PermissionError:
    #         return
    #     directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    #     files = [entry for entry in entries if os.path.isfile(os.path.join(path, entry))]
    #     for entry in directories:
    #         full_path = os.path.join(path, entry)
    #         if os.path.isdir(full_path):
    #             node_id = self.insert(parent, "end", text=entry, open=False, tags=("folder",), image=self.icon_folder)
    #             # self.insert(node_id, 'end', text='Empty', tags=("folder_empty",))
    #             self.build_tree(node_id, full_path)
    #     for entry in files:
    #         full_path = os.path.join(path, entry)
    #         if not os.path.isdir(full_path):
    #             self.insert(parent, 'end', text=entry, open=True, tags=("file",), image=self.icon_file)

    def build_tree_from_state(self, folder_state: dict):
        directories = sorted([entry for entry in folder_state if folder_state[entry]["type"] == "folder"])
        files = sorted([entry for entry in folder_state if folder_state[entry]["type"] == "file"])
        self.clear()
        for directory in directories:
            parent, item = os.path.split(directory)
            state_tag = folder_state[directory].get("tag", "")
            item_tag = "new folder" if "new" in state_tag else ("delete folder" if "delete" in state_tag else "folder")
            self.insert(parent, "end", text=item, open=False, tags=(item_tag,), iid=directory)
        for file in files:
            parent, item = os.path.split(file)
            state_tag = folder_state[file].get("tag", "")
            item_tag = "new file" if "new" in state_tag else ("delete file" if "delete" in state_tag else ("update file" if "update" in state_tag else ("conflict file" if "conflict" in state_tag else "file")))
            self.insert(parent, "end", text=item, tags=(item_tag,), iid=file)

    def get_full_path(self, item):
        parts = []
        while item:
            parts.insert(0, self.item(item, 'text'))
            item = self.parent(item)
        return os.path.join(self.path, *parts)

    def clear(self):
        self.delete(*self.get_children())


class FileTreeFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        self._title = kwargs.pop("title", "...")
        self._path = kwargs.pop("path", "")
        super().__init__(parent, **kwargs)
        self.label_title = ttk.Label(self, text=self._title)
        self.label_path = ttk.Label(self, text=self._path)
        self.filetree = FileTree(self, path=self._path)
        self.label_title.pack(padx=3, pady=3)
        self.label_path.pack(padx=3, pady=3)
        self.filetree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = str(value)
        self.label_title.config(text=self._title)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = str(value)
        self.label_path.config(text=self._path)


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Folder Sync")
        self.iconbitmap(default=ICON_FILE)
        # self.geometry("600x400")
        # App objects
        self.project_manager = ProjectManager()
        self.project_manager.load_projects()
        # App variables
        self.s_project_name = tk.StringVar()
        self.s_project_dir = tk.StringVar()
        self.s_folder_a = tk.StringVar()
        self.s_folder_b = tk.StringVar()
        self.s_status = tk.StringVar()
        # Create menu bar
        self.menubar = tk.Menu(self, tearoff=0)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="New Project...", command=self.create_new_project)
        self.filemenu.add_command(label="Open Project...", command=self.open_project)
        self.filemenu.add_command(label="Save Project...", command=self.save_active_project)
        self.filemenu.add_command(label="Save Project As...", command=self.not_implemented)
        self.filemenu.add_command(label="Delete Project...", command=self.not_implemented)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.syncmenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Sync", menu=self.syncmenu)
        self.syncmenu.add_command(label="Set Folder A", command=self.select_folder_a)
        self.syncmenu.add_command(label="Set Folder B", command=self.select_folder_b)
        self.syncmenu.add_separator()
        self.syncmenu.add_command(label="Prepare Sync", command=self.prep_sync)
        self.syncmenu.add_command(label="Handle Conflicts", command=self.not_implemented)
        self.syncmenu.add_command(label="Sync Now", command=self.sync_now)
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label="Help", command=self.not_implemented)
        self.helpmenu.add_command(label="About", command=self.show_about_dialog)
        self.config(menu=self.menubar)
        # Project Frame
        self.frame_folder_a = FileTreeFrame(self, title="Folder A")
        self.frame_common = FileTreeFrame(self, title="Common")
        self.frame_folder_b = FileTreeFrame(self, title="Folder B")
        self.frame_folder_a.grid(row=0, column=0, sticky="NSEW")
        self.frame_common.grid(row=0, column=1, sticky="NSEW")
        self.frame_folder_b.grid(row=0, column=2, sticky="NSEW")
        self.statusbar = tk.Label(self, textvariable=self.s_status, bd=1, relief=tk.SUNKEN, anchor=tk.S, justify=tk.LEFT)
        self.statusbar.grid(row=1, column=0, columnspan=3, sticky="NSEW")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.update_ui()

    @staticmethod
    def not_implemented():
        messagebox.showinfo("Not Implemented", "This feature is not yet implemented.")

    def quit(self):
        self.ask_to_save_changes()
        super().quit()


    def update_ui(self):
        if self.project_manager.active_project:
            self.s_project_name.set(self.project_manager.active_project.project_name)
            self.s_folder_a.set(self.project_manager.active_project.folder_a)
            self.s_folder_b.set(self.project_manager.active_project.folder_b)
            # Labels
            # Menu update
            self.menubar.entryconfig("Sync", state=tk.NORMAL)
            # Status bar update
            self.s_status.set(f"Current Project: {self.project_manager.active_project.project_name}")
        else:
            self.menubar.entryconfig("Sync", state=tk.DISABLED)
            self.s_status.set("No project selected.")

    def refresh_folder_frames(self, which: str = "abc", tags=False):
        if not self.project_manager.active_project:
            self.frame_folder_a.filetree.clear()
            self.frame_folder_a.path = ""
            self.frame_folder_b.filetree.clear()
            self.frame_folder_b.path = ""
            self.frame_common.filetree.clear()
            return
        if "a" in which.lower():
            self.frame_folder_a.filetree.build_tree_from_state(self.project_manager.active_project.get_folder_state("a"))
            self.frame_folder_a.path = self.project_manager.active_project.folder_a
        if "b" in which.lower():
            self.frame_folder_b.filetree.build_tree_from_state(self.project_manager.active_project.get_folder_state("b"))
            self.frame_folder_b.path = self.project_manager.active_project.folder_b
        if "c" in which.lower():
            if tags:
                self.frame_common.filetree.build_tree_from_state(self.project_manager.active_project.get_future_common_state())
            else:
                self.frame_common.filetree.build_tree_from_state(self.project_manager.active_project.get_folder_state("common"))

    def create_new_project(self):
        self.ask_to_save_changes()
        name = simpledialog.askstring("New Project", "Enter project name:")
        # To be implemented: create a dialog to ask for local and remote paths
        if not name:
            return
        if name in self.project_manager.get_project_names():
            messagebox.showerror("Error", "Project already exists.")
            return
        self.project_manager.create_project(project_name=name)
        self.update_ui()

    def open_project(self):
        self.ask_to_save_changes()
        self.project_manager.load_projects()
        dialog = OpenProjectDialog(self, title="Open Project", project_names=self.project_manager.get_project_names())
        if dialog.selection:
            self.project_manager.set_active_project(dialog.selection)
            self.refresh_folder_frames()
            self.update_ui()

    def ask_to_save_changes(self):
        if not self.project_manager.active_project:
            return
        if not self.project_manager.active_project.modified:
            return
        if messagebox.askyesno("Save Changes", "Do you want to save changes to the current project?"):
            self.project_manager.save_active()

    def save_active_project(self):
        if self.project_manager.active_project:
            self.project_manager.save_active()
            self.update_ui()
        else:
            messagebox.showerror("Error", "No project selected.")

    def select_folder_a(self):
        path = self.select_folder("a")
        if not path:
            return
        self.s_folder_a.set(path)
        self.project_manager.active_project.folder_a = path
        self.refresh_folder_frames("a")

    def select_folder_b(self):
        path = self.select_folder("b")
        if not path:
            return
        self.s_folder_b.set(path)
        self.project_manager.active_project.folder_b = path
        self.refresh_folder_frames("b")

    def select_folder(self, which: str):
        if which.lower() not in ["a", "b"]:
            raise ValueError("Invalid folder choice.")
        return tk.filedialog.askdirectory(title=f"Select Folder {which.upper()}", initialdir=self.s_folder_a.get() if which.lower() == "a" else self.s_folder_b.get())

    def prep_sync(self):
        self.project_manager.active_project.prep_sync()
        self.refresh_folder_frames(tags=True)
        self.update_ui()

    def sync_now(self):
        self.project_manager.active_project.execute_sync()
        self.refresh_folder_frames()

    def show_about_dialog(self):
        AboutDialog(self)
