#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摸鱼人日历API - 提供获取最新摸鱼人日历文章链接的API接口
"""

from flask import Flask, jsonify, request, Response
import os
import requests
from moyu_scraper import MoyuScraper, DEFAULT_WECHAT_URL

app = Flask(__name__)
scraper = MoyuScraper()

@app.route('/', methods=['GET'])
def index():
    """API文档首页"""
    return jsonify({
        'message': '摸鱼人日历API',
        'version': '1.0.0',
        'endpoints': {
            '/latest': '获取最新摸鱼人日历文章链接',
            '/image': '直接返回最新日历图片数据流',
            '/health': '健康检查'
        }
    })

@app.route('/latest', methods=['GET'])
def get_latest_moyu():
    """获取最新的摸鱼人日历文章链接和图片"""
    try:
        # 获取URL参数，如果没有提供则使用默认URL
        url = request.args.get('url', DEFAULT_WECHAT_URL)
        
        # 获取完整的摸鱼人日历信息
        result = scraper.get_complete_moyu_info(url=url)
        
        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': '未找到摸鱼人日历文章'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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
                'error': '未找到日历图片'
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
                'Cache-Control': 'public, max-age=3600',  # 缓存1小时
                'Content-Disposition': 'inline'  # 浏览器内显示
            }
        )
            
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'获取图片失败: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)