from openclaw_hello_python.cli import main


def test_default_greeting(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out.strip()
    assert out == "Hello, OpenClaw!"


def test_custom_name(capsys):
    assert main(["--name", "Steve"]) == 0
    out = capsys.readouterr().out.strip()
    assert out == "Hello, Steve!"
