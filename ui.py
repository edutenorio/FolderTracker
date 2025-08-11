import platform
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
import tkinter.font as tkfont
import os
from dotenv import load_dotenv
from icecream import ic
from PIL import Image, ImageTk
# import ttkbootstrap as tb

from project_manager import ProjectManager

load_dotenv()
DEBUG = bool(os.environ.get("DEBUG", False))
PROJECTS_DIR = str(os.environ.get("PROJECTS_DIR"))
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
        self.clear()
        if not folder_state:
            return
        directories = sorted([entry for entry in folder_state if folder_state[entry]["type"] == "folder"])
        files = sorted([entry for entry in folder_state if folder_state[entry]["type"] == "file"])
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


class ConflictDialog(simpledialog.Dialog):
    def __init__(self, parent, conflicts, future_state, **kwargs):
        self.result = None
        self.conflicts = conflicts
        self.future_state = future_state
        self.selections = [action.split()[-1] for action in conflicts.values()]
        self.current_index = 0
        super().__init__(parent, title="Conflict Resolution")

    def body(self, master):
        self.result = None
        default_font = tkfont.nametofont("TkDefaultFont").copy()
        bold_font = default_font.copy()
        bold_font.configure(weight="bold")
        self.filename_label = ttk.Label(master, text="", font=bold_font)
        self.filename_label.grid(row=0, column=0, columnspan=4, pady=10)
        ttk.Label(master, text="Size:\nCreated:\nModified:", justify=tk.LEFT).grid(row=1, column=0, sticky="w")
        ttk.Label(master, text="Size:\nCreated:\nModified:", justify=tk.LEFT).grid(row=1, column=2, sticky="w")
        self.a_info = ttk.Label(master, text="", justify=tk.LEFT)
        self.a_info.grid(row=1, column=1, padx=10, sticky="w")
        self.b_info = ttk.Label(master, text="", justify=tk.LEFT)
        self.b_info.grid(row=1, column=3, padx=10, sticky="w")
        self.choice = tk.StringVar()
        self.options = [("Keep folder A version", "A"), ("Keep folder B version", "B"), ("Keep both (rename)", "both")]
        self.radio_buttons = [
            ttk.Radiobutton(master, text="Keep folder A version", variable=self.choice, value="A"),
            ttk.Radiobutton(master, text="Keep folder B version", variable=self.choice, value="B"),
            ttk.Radiobutton(master, text="Keep both (rename)", variable=self.choice, value="both")
        ]
        self.radio_buttons[0].grid(row=2, column=0, columnspan=2, sticky="w", padx=10)
        self.radio_buttons[1].grid(row=2, column=2, columnspan=2, sticky="w", padx=10)
        self.radio_buttons[2].grid(row=3, column=0, columnspan=4, sticky="s", padx=10)
        # for i, (label, value) in enumerate(self.options):
        #     rb = ttk.Radiobutton(master, text=label, variable=self.choice, value=value)
        #     rb.grid(row=2+i, column=0, columnspan=2, sticky="w", padx=10)
        #     self.radio_buttons.append(rb)
        # Navigation and action buttons
        self.nav_frame = ttk.Frame(master)
        self.nav_frame.grid(row=6, column=0, columnspan=4, pady=(10, 0))
        self.prev_button = ttk.Button(self.nav_frame, text="Previous", command=self.prev_conflict)
        self.prev_button.grid(row=0, column=0, padx=5)
        self.next_button = ttk.Button(self.nav_frame, text="Next", command=self.next_conflict)
        self.next_button.grid(row=0, column=1, padx=5)
        self.update_ui()
        return self.radio_buttons[0]

    def buttonbox(self):
        box = ttk.Frame(self)
        ok_btn = ttk.Button(box, text="OK", width=10, command=self.ok)
        ok_btn.pack(side="left", padx=5, pady=5)
        cancel_btn = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        cancel_btn.pack(side="right", padx=5, pady=5)
        box.pack()

    def update_ui(self):
        filepath, action = list(self.conflicts.items())[self.current_index]
        state = self.future_state[filepath]
        relpath, filename = os.path.split(filepath)
        self.filename_label.config(text=f"{filepath}")
        a_stats = {k[:-2]: v for k, v in state.items() if k.endswith("_a")}
        b_stats = {k[:-2]: v for k, v in state.items() if k.endswith("_b")}
        def format_info(stats):
            if not stats:
                return "File does not exist"
            units = ['B', 'KB', 'MB', 'GB']
            fsize, unit_index = stats["size"], 0
            while fsize >= 1024:
                fsize /= 1024
                unit_index += 1
            size = (f"{fsize:.0f}" if unit_index == 0 else f"{fsize:.2f}") + f" {units[unit_index]}"
            ctime = datetime.fromtimestamp(stats["ctime"]).strftime("%d-%m-%Y %H:%M:%S")
            mtime = datetime.fromtimestamp(stats["mtime"]).strftime("%d-%m-%Y %H:%M:%S")
            return f"{size}\n{ctime}\n{mtime}"
        self.a_info.config(text=format_info(a_stats))
        self.b_info.config(text=format_info(b_stats))
        # if len(self.selections) <= self.current_index:
        #     self.selections.append("both")
        self.choice.set(self.selections[self.current_index])
        # Enable/disable prev/next buttons
        self.prev_button.config(state="normal" if self.current_index > 0 else "disabled")
        self.next_button.config(state="normal" if self.current_index < len(self.conflicts) - 1 else "disabled")

    def prev_conflict(self):
        self.selections[self.current_index] = self.choice.get()
        self.current_index -= 1
        self.update_ui()

    def next_conflict(self):
        self.selections[self.current_index] = self.choice.get()
        self.current_index += 1
        self.update_ui()

    def ok(self, event=None):
        self.selections[self.current_index] = self.choice.get()
        self.result = self.selections
        self.destroy()

    def cancel(self, event=None):
        self.result = None
        self.destroy()


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
        self.filemenu.add_command(label="Save Project As...", command=self.save_active_project_as)
        self.filemenu.add_command(label="Delete Project...", command=self.delete_project)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.syncmenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Sync", menu=self.syncmenu)
        self.syncmenu.add_command(label="Open Folder A", command=self.open_folder_a)
        self.syncmenu.add_command(label="Open Folder B", command=self.open_folder_b)
        self.syncmenu.add_separator()
        self.syncmenu.add_command(label="Prepare Sync", command=self.prep_sync)
        self.syncmenu.add_command(label="Handle Conflicts", command=self.handle_conflicts)
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
            self.syncmenu.entryconfig("Handle Conflicts", state=tk.NORMAL if self.project_manager.active_project.has_conflicts() else tk.DISABLED)
            self.syncmenu.entryconfig("Sync Now", state=tk.NORMAL if self.project_manager.active_project.has_sync_actions() else tk.DISABLED)
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
        # Project name validation
        name = simpledialog.askstring("New Project", "Enter project name:")
        if not name:
            return
        if name in self.project_manager.get_project_names():
            messagebox.showerror("Error", "Project already exists.")
            return
        # Project folders validation
        path_a = tk.filedialog.askdirectory(title=f"Select Folder A", initialdir=".")
        if not path_a:
            return
        path_b = tk.filedialog.askdirectory(title=f"Select Folder B", initialdir=".")
        if not path_b:
            return
        # Create and set active project
        self.project_manager.create_project(project_name=name, folder_a=path_a, folder_b=path_b)
        self.refresh_folder_frames()
        self.update_ui()

    def open_project(self):
        self.ask_to_save_changes()
        self.project_manager.load_projects()
        dialog = OpenProjectDialog(self, title="Open Project", project_names=self.project_manager.get_project_names())
        if dialog.selection:
            self.project_manager.active_project = dialog.selection
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

    def save_active_project_as(self):
        if not self.project_manager.active_project:
            messagebox.showerror("Error", "No project selected.")
            return
        name = simpledialog.askstring("Save Project As", "Enter project name:")
        if not name:
            return
        if name in self.project_manager.get_project_names():
            messagebox.showerror("Error", "Project already exists.")
            return
        self.project_manager.save_active_as(name)
        self.update_ui()

    def delete_project(self):
        if messagebox.askyesno("Confirm Delete", "Do you really want to delete the current project?\nThis operation cannot be undone."):
            self.project_manager.delete_project(self.project_manager.active_project)
            self.refresh_folder_frames()
            self.update_ui()

    @staticmethod
    def open_folder(path):
        if not path or not os.path.isdir(path):
            messagebox.showerror("Error", f"Invalid folder path: \"{path}\"")
            return
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: \"{path}\"\n{e}")

    def open_folder_a(self):
        self.open_folder(self.project_manager.active_project.folder_a)

    def open_folder_b(self):
        self.open_folder(self.project_manager.active_project.folder_b)

    def prep_sync(self):
        self.project_manager.active_project.prep_sync()
        self.refresh_folder_frames(tags=True)
        self.update_ui()

    def handle_conflicts(self):
        conflicts = self.project_manager.active_project.get_conflicts()
        future_state = {k: v for k, v in self.project_manager.active_project.get_future_common_state().items() if k in conflicts.keys()}
        dialog = ConflictDialog(self, conflicts, future_state)
        if dialog.result:
            for i, k in enumerate(conflicts.keys()):
                self.project_manager.active_project.modify_action(k, " ".join(conflicts[k].split()[0:2] + [dialog.result[i]]))

    def sync_now(self):
        self.project_manager.active_project.execute_sync()
        self.refresh_folder_frames()

    def show_about_dialog(self):
        AboutDialog(self)
