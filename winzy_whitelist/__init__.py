import winzy
import os
import sys
import shutil

def find_exe_path(app_name):
    # Check if the app_name contains an extension. If not, add .exe to it
    if not app_name.endswith(".exe"):
        app_name += ".exe"
    # Use shutil.which to find the executable in the PATH directories
    exe_path = shutil.which(app_name)
    if exe_path:
        return exe_path
    raise FileNotFoundError(f"Executable {app_name} not found in PATH.")

def create_batchfile(app_name, exe_path, alt_app_name):
    # Determine the folder containing the executable
    script_folder = os.path.dirname(exe_path)
    # Define the Python script file name and path
    python_script_name = f"{app_name}-script.py"
    python_script_path = os.path.join(script_folder, python_script_name)
    # Check if the Python script file exists
    if not os.path.isfile(python_script_path):
        print(f"Python script {python_script_name} not found in {script_folder}.")
        sys.exit(1)

    if not alt_app_name:
        alt_app_name = app_name
    # Define the batch file name and path
    batch_file_name = f"{alt_app_name}.bat"
    batch_file_path = os.path.join(script_folder, batch_file_name)
    # Create the batch file with the specified content
    with open(batch_file_path, "w") as batch_file:
        batch_file.write(f"@python {python_script_name} %*\n")
        batch_file.write("@exit /b %ERRORLEVEL%\n")
    print(f"Batch file created at: {batch_file_path}")

def create_parser(subparser):
    parser = subparser.add_parser(
        "wlist", description="Whitelist python created exe's to make them bat scripts"
    )
    # Add subprser arguments here.
    parser.add_argument(
        "app_name",
        type=str,
        help="The name of the application executable (without extension).",
    )
    parser.add_argument(
        "-at",
        "--alt-app-name",
        type=str,
        default=None,
        help="The Alternate name of the application batch file (without extension).",
    )
    return parser

class Plugin:
    """Whitelist python created exe's to make them bat scripts"""

    __name__ = "wlist"

    @winzy.hookimpl
    def register_commands(self, subparser):
        parser = create_parser(subparser)
        parser.set_defaults(func=self.main)

    def main(self, args):
        app_name = args.app_name
        alt_app_name = args.alt_app_name

        try:
            exe_path = find_exe_path(app_name)
            create_batchfile(app_name, exe_path, alt_app_name)
        except FileNotFoundError as e:
            print(e)

    def hello(self, args):
        # this routine will be called when "winzy "wlist is called."
        print("Hello! This is an example ``winzy`` plugin.")

wlist_plugin = Plugin()
