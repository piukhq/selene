import os
from flask_script import Manager, Server
from app import create_app
import settings

app = create_app()
manager = Manager(app)

manager.add_command("runserver", Server(port=settings.DEV_PORT, host=settings.DEV_HOST))

HERE = os.path.abspath(os.path.dirname(__file__))
UNIT_TEST_PATH = os.path.join(HERE, 'app', 'tests')

if __name__ == '__main__':
    manager.run()
