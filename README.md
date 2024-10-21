# fastApI

<!-- To create a virtual environment -->

```bash
python3 -m venv .venv
```

<!-- Activate the new virtual environment  -->

```bash
source .venv/bin/activate
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

<!-- FastAPI CLI - Development mode -->

```bash
 Serving at: http://127.0.0.1:8000
 API docs: http://127.0.0.1:8000/docs
 Alternative API docs http://127.0.0.1:8000/redoc
 Check openapi.json  http://127.0.0.1:8000/openapi.json
```
