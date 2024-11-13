import pytest
import winzy_whitelist as w

from argparse import Namespace, ArgumentParser

def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_args(['hello'])
    assert result.app_name == "hello"
    assert result.alt_app_name is None


def test_plugin(capsys):
    w.wlist_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``winzy`` plugin." in captured.out
