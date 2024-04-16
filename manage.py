from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import main, db 
migrate = Migrate(main, db)
manager = Manager(main)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
