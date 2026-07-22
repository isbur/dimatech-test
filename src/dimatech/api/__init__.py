from sanic import Blueprint

from dimatech.api.admin import bp as admin_bp
from dimatech.api.auth import bp as auth_bp
from dimatech.api.users import bp as users_bp
from dimatech.api.webhooks import bp as webhooks_bp

API_PREFIX = "/api/v1"


def register_blueprints(app) -> None:
    api = Blueprint.group(
        auth_bp,
        users_bp,
        admin_bp,
        webhooks_bp,
        url_prefix=API_PREFIX,
    )
    app.blueprint(api)
