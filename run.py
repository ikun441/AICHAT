import os
import yaml
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import importlib
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载配置
def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        return {}

config = load_config()

# 初始化Flask应用
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = config.get("server", {}).get("secret_key", "default_secret_key")

# 动态加载函数处理模块
def load_function_handler(function_name: str):
    """动态加载函数处理模块
    
    Args:
        function_name: 函数名称
        
    Returns:
        函数处理类实例
    """
    try:
        # 将函数名转换为模块名，例如：chat -> chat
        module_name = function_name.lower()
        
        # 导入模块
        module_path = f"function_call.{module_name}"
        module = importlib.import_module(module_path)
        
        # 获取处理类
        # 将函数名转换为类名，例如：chat -> ChatFunction
        class_name = "".join(word.capitalize() for word in module_name.split("_")) + "Function"
        handler_class = getattr(module, class_name)
        
        # 返回实例
        return handler_class()
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to load function handler for {function_name}: {str(e)}")
        return None

# 身份验证装饰器
def auth_required(f):
    """身份验证装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

def check_auth(username: str, password: str) -> bool:
    """检查用户名和密码
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        是否验证通过
    """
    server_config = config.get("server", {})
    return username == server_config.get("user") and password == server_config.get("password")

# 路由定义
@app.route('/')
@auth_required
def index():
    """网页首页
    
    Returns:
        渲染后的首页模板
    """
    return render_template('index.html')

@app.route('/api/function_call', methods=['POST'])
@auth_required
def function_call():
    """函数调用API
    
    Returns:
        处理结果的JSON响应
    """
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Invalid request data"}), 400
        
        # 提取函数名和参数
        function_name = data.get("function")
        params = data.get("params", {})
        
        if not function_name:
            return jsonify({"status": "error", "message": "Missing function name"}), 400
        
        # 加载函数处理器
        handler = load_function_handler(function_name)
        if not handler:
            return jsonify({"status": "error", "message": f"Function {function_name} not found"}), 404
        
        # 执行函数
        result = handler.execute(params)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in function_call: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 启动应用
if __name__ == "__main__":
    host = config.get("server", {}).get("host", "127.0.0.1")
    port = config.get("server", {}).get("port", 5001)
    lan_enabled = config.get("server", {}).get("LAN", "disabled") == "enabled"
    
    if lan_enabled:
        # 允许局域网访问
        host = "0.0.0.0"
    
    logger.info(f"Starting server on {host}:{port}, LAN access: {'enabled' if lan_enabled else 'disabled'}")
    app.run(host=host, port=port, debug=False)
import os
import yaml
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.security import check_password_hash, generate_password_hash
import importlib
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载配置
def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        return {}

config = load_config()

# 初始化Flask应用
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = config.get("server", {}).get("secret_key", "default_secret_key")

# 动态加载函数处理模块
def load_function_handler(function_name: str):
    """动态加载函数处理模块
    
    Args:
        function_name: 函数名称
        
    Returns:
        函数处理类实例
    """
    try:
        # 将函数名转换为模块名，例如：chat -> chat
        module_name = function_name.lower()
        
        # 导入模块
        module_path = f"function_call.{module_name}"
        module = importlib.import_module(module_path)
        
        # 获取处理类
        # 将函数名转换为类名，例如：chat -> ChatFunction
        class_name = "".join(word.capitalize() for word in module_name.split("_")) + "Function"
        handler_class = getattr(module, class_name)
        
        # 返回实例
        return handler_class()
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to load function handler for {function_name}: {str(e)}")
        return None

# 身份验证装饰器
def auth_required(f):
    """身份验证装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

def check_auth(username: str, password: str) -> bool:
    """检查用户名和密码
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        是否验证通过
    """
    server_config = config.get("server", {})
    return username == server_config.get("user") and password == server_config.get("password")

# 路由定义
@app.route('/')
@auth_required
def index():
    """网页首页
    
    Returns:
        渲染后的首页模板
    """
    return render_template('index.html')

@app.route('/api/function_call', methods=['POST'])
@auth_required
def function_call():
    """函数调用API
    
    Returns:
        处理结果的JSON响应
    """
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Invalid request data"}), 400
        
        # 提取函数名和参数
        function_name = data.get("function")
        params = data.get("params", {})
        
        if not function_name:
            return jsonify({"status": "error", "message": "Missing function name"}), 400
        
        # 加载函数处理器
        handler = load_function_handler(function_name)
        if not handler:
            return jsonify({"status": "error", "message": f"Function {function_name} not found"}), 404
        
        # 执行函数
        result = handler.execute(params)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in function_call: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 启动应用
if __name__ == "__main__":
    host = config.get("server", {}).get("host", "127.0.0.1")
    port = config.get("server", {}).get("port", 5001)
    lan_enabled = config.get("server", {}).get("LAN", "disabled") == "enabled"
    
    if lan_enabled:
        # 允许局域网访问
        host = "0.0.0.0"
    
    logger.info(f"Starting server on {host}:{port}, LAN access: {'enabled' if lan_enabled else 'disabled'}")
    app.run(host=host, port=port, debug=False)