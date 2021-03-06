from app import app, db
from app.models import Post, User, MicroPost, Tag, Category
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Post=Post, User=User, MicroPost=MicroPost, Tag=Tag, Category=Category)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
