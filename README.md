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
The MIT License (MIT)

Copyright © 2022 Jeff Martin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
