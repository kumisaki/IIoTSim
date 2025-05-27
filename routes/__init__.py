from .project_routes import project_bp
from .model_routes import model_bp
from .device_routes import device_bp
from .setting_routes import setting_bp  

def register_routes(app):
    app.register_blueprint(project_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(device_bp)
    app.register_blueprint(setting_bp) 