from .refund import refund_bp

def init_routes(app):
    app.register_blueprint(refund_bp) 