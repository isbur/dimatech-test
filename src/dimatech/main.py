from sanic import Request, Sanic
from sanic.exceptions import Forbidden, NotFound, Unauthorized
from sanic.response import JSONResponse, json
from sanic_ext import Extend
from sanic_ext.exceptions import ValidationError

from dimatech.api import register_blueprints
from dimatech.api.errors import Conflict, format_validation_detail
from dimatech.config import settings
from dimatech.db.session import setup_db


def create_app() -> Sanic:
    app = Sanic("dimatech")
    app.config.OAS = True
    app.config.OAS_UI_DEFAULT = "swagger"
    Extend(app)
    app.config.SWAGGER_UI_CONFIGURATION = {
        **getattr(app.config, "SWAGGER_UI_CONFIGURATION", {}),
        "persistAuthorization": True,
    }
    app.ext.openapi.add_security_scheme(
        "BearerAuth",
        "http",
        scheme="bearer",
        bearer_format="JWT",
        description="JWT access token from POST /api/v1/auth/login",
    )

    register_blueprints(app)
    setup_db(app)

    @app.exception(ValidationError)
    async def handle_validation_error(
        request: Request,
        exception: ValidationError,
    ) -> JSONResponse:
        return json(
            {
                "detail": format_validation_detail(request, exception),
            },
            status=422,
        )

    @app.exception(Unauthorized)
    async def handle_unauthorized(
        _request: Request,
        exception: Unauthorized,
    ) -> JSONResponse:
        return json(
            {"detail": exception.args[0] if exception.args else "Unauthorized"},
            status=401,
        )

    @app.exception(Forbidden)
    async def handle_forbidden(
        _request: Request,
        exception: Forbidden,
    ) -> JSONResponse:
        return json(
            {"detail": exception.args[0] if exception.args else "Forbidden"},
            status=403,
        )

    @app.exception(NotFound)
    async def handle_not_found(
        _request: Request,
        exception: NotFound,
    ) -> JSONResponse:
        return json(
            {"detail": exception.args[0] if exception.args else "Not found"},
            status=404,
        )

    @app.exception(Conflict)
    async def handle_conflict(
        _request: Request,
        exception: Conflict,
    ) -> JSONResponse:
        return json(
            {"detail": exception.args[0] if exception.args else "Conflict"},
            status=409,
        )

    @app.get("/health")
    async def health(_request: Request) -> JSONResponse:
        return json({"status": "ok"})

    return app



if __name__ == "__main__":
    application = create_app()
    application.run(host=settings.host, port=settings.port, debug=True)
