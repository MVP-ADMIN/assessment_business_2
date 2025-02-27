from .refund import refund_bp
from .agent import agent_bp
from .order import order_bp

def init_routes(app):
    app.register_blueprint(refund_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(order_bp) 