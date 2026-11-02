import sys
from pathlib import Path

from flask import Flask

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / "src"))

from view.web import vista_credito


app = Flask(__name__, template_folder=str(project_root / "templates"))
app.register_blueprint(vista_credito.vista)


if __name__ == "__main__":
    app.run(debug=False)