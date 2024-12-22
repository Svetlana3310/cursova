from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from api.models import db
from api.routes import routes
from api.auth import auth
from config import Config
import logging
import traceback

# Ініціалізація основних компонентів
app = Flask(__name__)
app.config.from_object(Config)

if not app.config.get("JWT_SECRET_KEY"):
    raise RuntimeError("JWT_SECRET_KEY is not set in the configuration!")

# Ініціалізація бази даних і міграцій
db.init_app(app)
migrate = Migrate(app, db)

# Ініціалізація JWT
jwt = JWTManager(app)

# Чорний список для відкликаних токенів
blacklist = set()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist

# Додаткові обробники для JWT


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"description": "Request does not contain an access token.", "error": "authorization_required"}), 401

# Глобальний обробник помилок


@app.errorhandler(Exception)
def handle_exception(e):
    response = {"type": type(e).__name__, "message": str(e)}
    if app.debug:
        response["traceback"] = "\n".join(traceback.format_exc().split("\n"))
    return jsonify(response), 500


# Реєстрація Blueprint'ів
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(routes, url_prefix="/api")

# Налаштування логування
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app.logger.info("Flask app starting up")

# Запуск застосунку
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
