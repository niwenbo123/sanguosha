import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def get_base_dir():
    """获取项目根目录的绝对路径，兼容各种运行方式"""
    # 方法1：从当前文件位置计算（最可靠，不受工作目录影响）
    current_file = os.path.abspath(__file__)
    # 当前文件是 app/__init__.py，所以需要上两级目录
    base_dir = os.path.dirname(os.path.dirname(current_file))
    
    # 验证模板目录是否存在
    templates_dir = os.path.join(base_dir, 'app', 'templates')
    if os.path.exists(templates_dir):
        return base_dir
    
    # 方法2：从入口脚本位置计算
    if len(sys.argv) > 0 and sys.argv[0]:
        entry_script = os.path.abspath(sys.argv[0])
        entry_dir = os.path.dirname(entry_script)
        templates_dir = os.path.join(entry_dir, 'app', 'templates')
        if os.path.exists(templates_dir):
            return entry_dir
    
    # 方法3：PyInstaller 打包后的运行环境
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    
    # 方法4：从环境变量获取
    if 'SANGUOSHA_BASE_DIR' in os.environ:
        env_base = os.path.abspath(os.environ['SANGUOSHA_BASE_DIR'])
        templates_dir = os.path.join(env_base, 'app', 'templates')
        if os.path.exists(templates_dir):
            return env_base
    
    # 最后回退到当前工作目录（仅作为最后的备选）
    return os.path.abspath('.')

BASE_DIR = get_base_dir()

def create_app():
    # 使用绝对路径配置模板和静态文件目录
    templates_folder = os.path.join(BASE_DIR, 'app', 'templates')
    static_folder = os.path.join(BASE_DIR, 'app', 'static')
    
    # 确保目录存在
    if not os.path.exists(templates_folder):
        raise RuntimeError(f"模板目录不存在: {templates_folder}")
    
    app = Flask(__name__, 
                template_folder=templates_folder,
                static_folder=static_folder)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'sanguo-sha-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:niwenbo123@localhost/sanguo_assistant?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        from app import preset_data
        preset_data.init_preset_data()

    return app