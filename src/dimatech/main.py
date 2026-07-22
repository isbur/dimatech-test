from sanic import Request, Sanic
from sanic.response import JSONResponse, json
from sanic_ext import Extend
from sanic_ext.exceptions import ValidationError

from dimatech.api import register_blueprints
from dimatech.config import settings
from dimatech.db.session import setup_db


def create_app() -> Sanic:
    app = Sanic("dimatech")
    app.config.OAS = True
    app.config.OAS_UI_DEFAULT = "swagger"
    Extend(app)

    register_blueprints(app)
    setup_db(app)

    @app.exception(ValidationError)
    async def handle_validation_error(
        _request: Request,
        exception: ValidationError,
    ) -> JSONResponse:
        return json(
            {
                "description": "Unprocessable Entity",
                "status": 422,
                "message": exception.message,
            },
            status=422,
        )

    @app.get("/health")
    async def health(_request: Request) -> JSONResponse:
        return json({"status": "ok"})

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host=settings.host, port=settings.port, debug=True)
