# fastApI

<!-- To create a virtual environment -->

```bash
python3 -m venv .venv
```

<!-- Activate the new virtual environment  -->

```bash
source .venv/bin/activate
```

<!-- Deactivate the Virtual Environment -->

```bash
deactivate
```

<!-- Upgrade pip -->

```bash
python -m pip install --upgrade pip
```

<!-- Add .gitigonre -->

```bash
echo "*" > .venv/.gitignore
```

<!-- Install dependencies form requirements -->

```bash
pip install -r requirements.txt
```

<!-- Run program -->

```bash
python main.py
```

<!-- Checking a virtual environment -->

```bash
which python
```

<!-- Run the code -->

```bash
fastapi dev main.py
```

<!-- To generate a secure random secret key  -->

```bash
    openssl rand -hex 32
```

<!-- FastAPI CLI - Development mode -->

```bash
 Serving at: http://127.0.0.1:8000
 API docs: http://127.0.0.1:8000/docs
 Alternative API docs http://127.0.0.1:8000/redoc
 Check openapi.json  http://127.0.0.1:8000/openapi.json
```

├─── api - The folder containing the api endpoints, models, repositories etc.
├─── dependencies - Global dependencies used for the entire application like the current user.
├─── middleware - Global middleware associated with the entire application.
├─── setup - Scripts used to install the system. like creating tables, adding views etc
├─── static - static files like logo.png
├─── tables - Application tables definitions. a file for each table
└─── utilities - Functions, classes to help with application development. Collections, Database wrappers, password hashers etc
