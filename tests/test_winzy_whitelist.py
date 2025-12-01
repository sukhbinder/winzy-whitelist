import pytest
import winzy_whitelist as w
from unittest.mock import patch, mock_open


from argparse import Namespace, ArgumentParser


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_args(["hello"])
    assert result.app_name == "hello"
    assert result.alt_app_name is None


def test_find_exe_path_not_found():
    with pytest.raises(FileNotFoundError):
        w.find_exe_path("non_existent_app")


@patch('shutil.which', return_value='/fake/path/to/executable.exe')
def test_find_exe_path_success(mock_which):
    path = w.find_exe_path("any_app")
    assert path == '/fake/path/to/executable.exe'
    # Test that it adds .exe
    w.find_exe_path("any_app")
    mock_which.assert_called_with("any_app.exe")
    # Test that it doesn't add .exe if it's already there
    w.find_exe_path("any_app.exe")
    mock_which.assert_called_with("any_app.exe")


@patch('os.path.exists', return_value=True)
def test_ensure_script_exists_already_exists(mock_exists):
    script_path = w._ensure_script_exists('/fake/dir', 'app_name')
    assert script_path == '/fake/dir/app_name-script.py'


@patch('os.path.exists', return_value=False)
@patch('winzy_whitelist._detect_module')
@patch('builtins.open', new_callable=mock_open)
def test_ensure_script_exists_creates_script(mock_open_file, mock_detect_module, mock_exists):
    class MockEntryPoint:
        def __init__(self, name, value, module, attr):
            self.name = name
            self.value = value
            self.module = module
            self.attr = attr

    mock_detect_module.return_value = MockEntryPoint(
        name='app_name',
        value='my_module:main',
        module='my_module',
        attr='main'
    )

    script_path = w._ensure_script_exists('/fake/dir', 'app_name')
    assert script_path == '/fake/dir/app_name-script.py'
    mock_open_file.assert_called_once_with('/fake/dir/app_name-script.py', 'w', encoding='utf-8')
    handle = mock_open_file()
    handle.write.assert_called_once()
    written_content = handle.write.call_args[0][0]
    assert "import my_module" in written_content
    assert "sys.exit(my_module.main())" in written_content


@patch('os.path.exists', return_value=False)
@patch('winzy_whitelist._detect_module', return_value=None)
def test_ensure_script_exists_no_module(mock_detect_module, mock_exists):
    script_path = w._ensure_script_exists('/fake/dir', 'app_name')
    assert script_path is None


@patch('winzy_whitelist._ensure_script_exists', return_value='/fake/dir/app_name-script.py')
@patch('builtins.open', new_callable=mock_open)
def test_create_batchfile(mock_open_file, mock_ensure_script):
    w.create_batchfile('app_name', '/fake/dir/app.exe')
    mock_open_file.assert_called_once_with('/fake/dir/app_name.bat', 'w', encoding='utf-8')
    handle = mock_open_file()
    handle.write.assert_called_once_with('@python "%~dp0app_name-script.py" %*\n@exit /b %ERRORLEVEL%\n')


@patch('winzy_whitelist._ensure_script_exists', return_value='/fake/dir/app_name-script.py')
@patch('builtins.open', new_callable=mock_open)
def test_create_batchfile_alt_name(mock_open_file, mock_ensure_script):
    w.create_batchfile('app_name', '/fake/dir/app.exe', alt_app_name='alt_name')
    mock_open_file.assert_called_once_with('/fake/dir/alt_name.bat', 'w', encoding='utf-8')
    handle = mock_open_file()
    handle.write.assert_called_once_with('@python "%~dp0app_name-script.py" %*\n@exit /b %ERRORLEVEL%\n')


def test_plugin(capsys):
    w.wlist_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``winzy`` plugin." in captured.out
