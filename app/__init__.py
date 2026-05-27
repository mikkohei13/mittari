from flask import Flask


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    from app.routes import main_bp, stats_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(stats_bp)

    return app
