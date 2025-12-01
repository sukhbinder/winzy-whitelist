import winzy
import os
import sys
import shutil
from importlib.metadata import entry_points


def find_console_script(entry_name):
    eps = entry_points()
    # In newer versions entry_points() returns an object with .select
    # Try both APIs for compatibility:
    try:
        group_eps = eps.select(group="console_scripts")
    except AttributeError:
        group_eps = eps.get("console_scripts", [])
    for ep in group_eps:
        if ep.name == entry_name:
            # ep.value, ep.module, ep.attr  # ep.value like 'package.module:func'
            return ep
    return None


def find_exe_path(app_name):
    # Check if the app_name contains an extension. If not, add .exe to it
    if not app_name.lower().endswith(".exe"):
        app_name = app_name + ".exe"
    path = shutil.which(app_name)
    if not path:
        raise FileNotFoundError(f"Could not find {app_name} on PATH")
    return path


def _detect_module(app_name):
    ep = find_console_script(app_name)
    return ep


def _ensure_script_exists(script_folder, app_name):
    """
    Ensure that {app_name}-script.py exists in script_folder.
    If missing, attempt to detect module and create:
        from <module> import cli
        import sys
        sys.exit(cli())
    """
    script_name = f"{app_name}-script.py"
    script_path = os.path.join(script_folder, script_name)
    if os.path.exists(script_path):
        return script_path

    module_name = _detect_module(app_name)

    if module_name:
        line = module_name.value.replace(":", ".") + "()"
        content = (
            f"import {module_name.module}\n"
            "import sys\n"
            "if __name__ == '__main__':\n"
            f"    sys.exit({line})\n"
        )

        try:
            with open(script_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"Created missing script: {script_path}")
        except OSError as e:
            print(f"Failed to create script {script_path}: {e}")
            raise

        return script_path
    return None


def create_batchfile(app_name, exe_path, alt_app_name=None):
    # Determine the folder containing the executable
    script_folder = os.path.dirname(exe_path)
    # ensure script exists, passing exe_path for detection heuristics
    try:
        script_path = _ensure_script_exists(script_folder, app_name)
    except Exception:
        print(f"Could not create companion script for {app_name}-script.py")
        sys.exit(1)

    bat_name = (alt_app_name or app_name) + ".bat"
    bat_path = os.path.join(script_folder, bat_name)

    # Use the script file name (not absolute) so the batch file stays portable within the folder
    script_name = os.path.basename(script_path)
    bat_contents = f'@python "%~dp0{script_name}" %*\\r\\n@exit /b %ERRORLEVEL%\\r\\n'
    with open(bat_path, "w", encoding="utf-8") as fh:
        fh.write(bat_contents)
    print(bat_path)


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
