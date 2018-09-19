import os

from app import create_app

app = create_app()

HERE = os.path.abspath(os.path.dirname(__file__))
UNIT_TEST_PATH = os.path.join(HERE, 'app', 'tests')


@app.cli.command()
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([UNIT_TEST_PATH, '--verbose'])
    return exit_code


if __name__ == '__main__':
    app.run()
