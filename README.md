# Task Time Tracker
A to-do list app that asks you to forecast how much time each task will take.

## Installation
To install on a new machine:
1. Create a virtual environment (`python3 -m venv env`)
2. Install required dependencies (`python3 -m pip install -r requirements.txt`)
3. Migrate (`python3 manage.py migrate`)
4. Create a `.env` file at the root level and add a `SECRET_KEY` to it (you can get one by entering into your terminal `python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)

## Running
To run the project on your machine, enter `python3 manage.py runserver` in your terminal.

## Testing
To run the testing suite, enter `python3 manage.py test` in your terminal.

## Structure
The project is divided into the `task_time_tracker` app, which contains all models, views, templates, etc., and the `task_time_tracker_project` directory, which contains settings modules (for both development and production), top-level URLs, and a server.

## License
The MIT License (MIT). Copyright © 2022 Jeff Martin. See `LICENSE` file for full license.
