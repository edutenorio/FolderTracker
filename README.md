# FolderTracker

FolderTracker is a Python program designed to track and synchronize two folders. It provides an efficient way to keep your directories in sync, making it ideal for backup purposes or maintaining consistency across multiple locations.

## Features

- Track changes in two specified folders
- Synchronize contents between folders
- Prepare synchronization actions before execution
- Detailed logging for synchronization activities
- Conflict resolution for files modified in both locations

## Project Structure

- `main.py`: Entry point of the application
- `project_manager.py`: Manages project-related operations
- `sync_manager.py`: Core synchronization logic
- `ui.py`: Contains the user interface code
- `requirements.txt`: Lists all required Python packages
- `img/`: Directory containing image assets (icon-file-16.png, icon-folder-16.png)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/FolderTracker.git
   ```

2. Navigate to the project directory:
   ```
   cd FolderTracker
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the main script:
   ```
   python main.py
   ```

2. Follow the on-screen instructions to set up your folders and start synchronization.

## Dependencies

FolderTracker relies on several Python packages:

- Pillow: For image processing tasks
- Pygments: For syntax highlighting in logs
- Icecream: For enhanced debugging
- Colorama: For colored console output
- Python-dotenv: For managing environment variables

For a complete list of dependencies, see `requirements.txt`.

## Logging

FolderTracker maintains detailed logs:

- `sync_manager.log`: Records synchronization activities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Contact

Eduardo Tenorio Bastos - edutenorio@gmail.com

Project Link: [https://github.com/yourusername/FolderTracker](https://github.com/yourusername/FolderTracker)
