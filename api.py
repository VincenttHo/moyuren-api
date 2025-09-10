#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摸鱼人日历API - 提供获取最新摸鱼人日历文章链接的API接口
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
import requests
from moyu_scraper import MoyuScraper, DEFAULT_WECHAT_URL

app = Flask(__name__)
CORS(app)  # 允许跨域请求

scraper = MoyuScraper()

@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        'message': '摸鱼人日历API',
        'version': '1.0.0',
        'endpoints': {
            '/latest': 'GET - 获取最新摸鱼人日历文章链接（支持参数: url, include_image=true/false）',
            '/image': 'GET - 直接返回最新日历图片数据流（无需参数，浏览器可直接显示）',
            '/health': 'GET - 健康检查'
        }
    })

@app.route('/latest', methods=['GET'])
def get_latest_moyu():
    """获取最新的摸鱼人日历文章链接"""
    try:
        # 获取URL参数，如果没有提供则使用本地示例文件
        url = request.args.get('url')
        include_image = request.args.get('include_image', 'true').lower() == 'true'
        
        if url:
            # 从提供的URL获取
            if include_image:
                result = scraper.get_complete_moyu_info(url=url)
            else:
                result = scraper.get_latest_moyu_link(url)
        else:
            # 从本地示例文件获取，如果不存在则使用默认微信链接
            sample_file = os.path.join(os.path.dirname(__file__), 'sample.html')
            if os.path.exists(sample_file):
                if include_image:
                    result = scraper.get_complete_moyu_info(file_path=sample_file)
                else:
                    result = scraper.get_latest_moyu_link_from_file(sample_file)
            else:
                # 使用默认的微信链接作为备选
                if include_image:
                    result = scraper.get_complete_moyu_info(url=DEFAULT_WECHAT_URL)
                else:
                    result = scraper.get_latest_moyu_link(DEFAULT_WECHAT_URL)
        
        if result:
            return jsonify({
                'success': True,
                'data': result,
                'message': '成功获取最新摸鱼人日历文章'
            })
        else:
            return jsonify({
                'success': False,
                'error': '未找到摸鱼人日历文章',
                'message': '请检查URL是否正确或页面是否包含摸鱼人日历内容'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '服务器内部错误'
        }), 500

@app.route('/image', methods=['GET'])
def get_calendar_image():
    """直接返回最新日历图片数据流"""
    try:
        # 获取最新的日历图片URL
        result = scraper.get_complete_moyu_info(url=DEFAULT_WECHAT_URL)
        
        if not result or not result.get('calendar_image'):
            return jsonify({
                'success': False,
                'error': '未找到日历图片',
                'message': '无法获取到最新的摸鱼人日历图片'
            }), 404
        
        image_url = result['calendar_image']
        
        # 获取图片数据
        image_response = requests.get(image_url, timeout=30, stream=True)
        image_response.raise_for_status()
        
        # 获取内容类型，默认为image/jpeg
        content_type = image_response.headers.get('Content-Type', 'image/jpeg')
        
        # 返回图片数据流
        def generate():
            for chunk in image_response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            content_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',  # 缓塘1小时
                'Content-Disposition': 'inline'  # 浏览器内显示
            }
        )
            
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'获取图片失败: {str(e)}',
            'message': '无法下载图片数据'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '服务器内部错误'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': '摸鱼人日历API',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': 'API接口不存在',
        'message': '请检查请求的URL路径'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'message': '请稍后重试或联系管理员'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"摸鱼人日历API启动中...")
    print(f"访问地址: http://localhost:{port}")
    print(f"API文档: http://localhost:{port}/")
    print(f"获取最新文章: http://localhost:{port}/latest")
    
    app.run(host='0.0.0.0', port=port, debug=debug)