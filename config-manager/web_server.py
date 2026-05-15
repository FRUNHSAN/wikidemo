"""
配置管理Web服务器
提供REST API和Web UI
"""

from flask import Flask, request, jsonify, send_from_directory
from config_engine import get_config_engine
from dataclasses import asdict
import sys
from pathlib import Path

# 添加log-manager到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'log-manager'))
from log_manager import get_log_manager

app = Flask(__name__, static_folder='.', template_folder='.')
engine = get_config_engine()
log_mgr = get_log_manager()


@app.route('/')
def index():
    """提供Web UI"""
    return send_from_directory('.', 'web_ui.html')


@app.route('/api/config/<section>', methods=['GET'])
def get_config(section):
    """获取配置"""
    key = request.args.get('key')
    value = engine.get_config(section, key)
    return jsonify({'success': True, 'value': value})


@app.route('/api/config/<section>', methods=['POST'])
def set_config(section):
    """设置配置"""
    data = request.json
    key = data.get('key')
    value = data.get('value')

    success = engine.set_config(section, key, value)

    if success:
        return jsonify({'success': True, 'message': '配置已保存'})
    else:
        return jsonify({'success': False, 'message': '配置保存失败'}), 400


@app.route('/api/config/schema/<section>', methods=['GET'])
def get_schema(section):
    """获取配置schema"""
    schema = engine.get_schema(section)
    if schema:
        return jsonify({
            'success': True,
            'schema': {
                'id': schema.id,
                'title': schema.title,
                'description': schema.description,
                'fields': [
                    {
                        'name': f.name,
                        'type': f.type,
                        'default': f.default,
                        'description': f.description,
                        'options': f.options
                    }
                    for f in schema.fields
                ]
            }
        })
    else:
        return jsonify({'success': False}), 404


@app.route('/api/config/history', methods=['GET'])
def get_history():
    """获取配置历史"""
    limit = request.args.get('limit', 20, type=int)
    history = engine.get_history(limit)
    return jsonify({'success': True, 'history': history})


@app.route('/api/config/export', methods=['GET'])
def export_config():
    """导出配置"""
    format = request.args.get('format', 'json')
    data = engine.export_config(format)
    return data, 200, {'Content-Type': f'application/{format}'}


@app.route('/api/config/import', methods=['POST'])
def import_config():
    """导入配置"""
    data = request.get_data(as_text=True)
    format = request.args.get('format', 'json')
    success = engine.import_config(data, format)

    if success:
        return jsonify({'success': True, 'message': '配置已导入'})
    else:
        return jsonify({'success': False, 'message': '导入失败'}), 400


@app.route('/api/plugins', methods=['GET'])
def get_plugins():
    """获取插件列表"""
    plugins = engine.get_config('plugins', 'plugins')
    return jsonify({'success': True, 'plugins': plugins or {}})


@app.route('/api/plugins/<plugin_name>/toggle', methods=['POST'])
def toggle_plugin(plugin_name):
    """切换插件状态"""
    current = engine.get_config('plugins', f'plugins.{plugin_name}.enabled')
    new_state = not current if isinstance(current, bool) else True

    success = engine.set_config('plugins', f'plugins.{plugin_name}.enabled', new_state)

    if success:
        return jsonify({'success': True, 'enabled': new_state})
    else:
        return jsonify({'success': False}), 400


# ==========================================
# 日志管理API
# ==========================================

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取日志文件列表"""
    pattern = request.args.get('pattern', '*.log')
    files = log_mgr.get_log_files(pattern)
    return jsonify({
        'success': True,
        'files': [asdict(f) for f in files]
    })


@app.route('/api/logs/<filename>', methods=['GET'])
def read_log(filename):
    """读取日志内容"""
    lines = request.args.get('lines', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    result = log_mgr.read_log(filename, lines=lines, offset=offset)
    return jsonify(result)


@app.route('/api/logs/<filename>/tail', methods=['GET'])
def tail_log(filename):
    """查看日志末尾"""
    lines = request.args.get('lines', 50, type=int)
    result = log_mgr.tail_log(filename, lines=lines)
    return jsonify(result)


@app.route('/api/logs/search', methods=['GET'])
def search_logs():
    """搜索日志"""
    keyword = request.args.get('keyword', '')
    case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
    max_results = request.args.get('max_results', 100, type=int)

    if not keyword:
        return jsonify({'success': False, 'error': '请提供搜索关键词'}), 400

    results = log_mgr.search_logs(keyword, case_sensitive, max_results)
    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    })


@app.route('/api/logs/rotate', methods=['POST'])
def rotate_logs():
    """轮转日志"""
    dry_run = request.args.get('dry_run', 'false').lower() == 'true'
    result = log_mgr.rotate_logs(dry_run=dry_run)
    return jsonify(result)


@app.route('/api/logs/cleanup', methods=['POST'])
def cleanup_logs():
    """清理旧日志"""
    days = request.args.get('days', 30, type=int)
    dry_run = request.args.get('dry_run', 'false').lower() == 'true'
    result = log_mgr.cleanup_logs(days=days, dry_run=dry_run)
    return jsonify(result)


@app.route('/api/logs/stats', methods=['GET'])
def log_stats():
    """获取日志统计"""
    stats = log_mgr.get_log_stats()
    return jsonify({'success': True, 'stats': stats})


if __name__ == '__main__':
    print("=" * 60)
    print("  Wiki.js 配置管理服务器")
    print("=" * 60)
    print()
    print("访问地址: http://localhost:5000")
    print("日志管理: http://localhost:5000/api/logs")
    print()
    print("按 Ctrl+C 停止服务器")
    print()

    app.run(host='0.0.0.0', port=5000, debug=True)
