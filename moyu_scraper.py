#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摸鱼人日历爬虫 - 获取最新摸鱼人日历文章链接
"""

import requests
from bs4 import BeautifulSoup
import re
import html
import json
from typing import Optional, Dict, Any, List
import logging
import urllib.parse
from PIL import Image
import io

# 配置变量 - 容易修改的微信公众号链接
DEFAULT_WECHAT_URL = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxOTYyMzczNA==&action=getalbum&album_id=3743225907507462153&subscene=0&scenenote=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzAxOTYyMzczNA%3D%3D%26mid%3D2454356650%26idx%3D3%26sn%3Db1b9c97cc7bf61037ec23358ae49fc21%26chksm%3D8d7e87d0789afd79bba17838c0ebc30032a48ec592b15ce631c617d8f7b6489ae1854217123d%26xtrack%3D1%26scene%3D0%26subscene%3D7%26clicktime%3D1756172088%26enterid%3D1756172088%26sessionid%3D0%26ascene%3D7%26fasttmpl_type%3D0%26fasttmpl_fullversion%3D7876133-zh_CN-zip%26fasttmpl_flag%3D0%26realreporttime%3D1756172088652%26devicetype%3Dandroid-34%26version%3D2800315a%26nettype%3DWIFI%26abtest_cookie%3DAAACAA%253D%253D%26lang%3Dzh_CN%26session_us%3Dgh_a589f1b94a1b%26countrycode%3DCN%26exportkey%3Dn_ChQIAhIQA1t5yUVrdVlsNJ%252BopF7QRhLlAQIE97dBBAEAAAAAAC95BmOr4xkAAAAOpnltbLcz9gKNyK89dVj0h%252BwXpZKnm7RtJodhDfgbbsdkbhy7ZitAguP5Two94sEUtw%252FYDRFprtqBkW2tlQNNvpF01VvSM4xB8RMqIaTysNoP1JE85ZM8veAIqTDFgJlwFhmTr2nWFg6udZ8Nm%252FQ8mFP8oMFVh6hWIAaevoH8Y8NcrOCQ%252FJ1vMpBvp5yRy7HPltQZodArcVo7xi5OWzUWUx9%252BV%252BG31dFR74uONPXkZ26YqV5Bj5Uy%252Bm8UxYBKe4hBpDQxxpT%252Fzqzrv%252BKrEqw%253D%26pass_ticket%3DV35uCaA010EVXzou5598fycnm212HGyeKi21hYdh%252BSZvDprAS0eJTLODJbUV9tt2%26wx_header%3D3&nolastread=1#wechat_redirect"

class MoyuScraper:
    """摸鱼人日历爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def get_latest_moyu_link(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取最新的摸鱼人日历文章链接
        
        Args:
            url: 微信公众号文章页面URL
            
        Returns:
            包含最新文章信息的字典，包括标题和链接
        """
        try:
            self.logger.info(f"正在获取页面内容: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有包含摸鱼人日历的文章项
            moyu_articles = []
            
            # 方法1: 查找带有data-link和data-title的li元素
            article_items = soup.find_all('li', {'class': 'album__list-item', 'data-link': True, 'data-title': True})
            
            for item in article_items:
                title = item.get('data-title', '')
                link = item.get('data-link', '')
                msgid = item.get('data-msgid', '')
                
                # 过滤摸鱼人日历相关文章
                if '摸鱼人日历' in title and link:
                    # 解码HTML实体
                    link = html.unescape(link)
                    moyu_articles.append({
                        'title': title,
                        'link': link,
                        'msgid': int(msgid) if msgid.isdigit() else 0
                    })
            
            if not moyu_articles:
                self.logger.warning("未找到摸鱼人日历相关文章")
                return None
            
            # 直接取第一篇文章，因为列表中第一篇永远是最新的
            latest_article = moyu_articles[0]
            
            self.logger.info(f"找到最新文章: {latest_article['title']}")
            self.logger.info(f"文章链接: {latest_article['link']}")
            
            return {
                'title': latest_article['title'],
                'link': latest_article['link'],
                'msgid': latest_article['msgid']
            }
            
        except requests.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"解析失败: {e}")
            return None
    
    def get_latest_moyu_link_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        从本地HTML文件获取最新的摸鱼人日历文章链接
        
        Args:
            file_path: HTML文件路径
            
        Returns:
            包含最新文章信息的字典
        """
        try:
            self.logger.info(f"正在读取本地文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找所有包含摸鱼人日历的文章项
            moyu_articles = []
            
            # 查找带有data-link和data-title的li元素
            article_items = soup.find_all('li', {'class': 'album__list-item', 'data-link': True, 'data-title': True})
            
            for item in article_items:
                title = item.get('data-title', '')
                link = item.get('data-link', '')
                msgid = item.get('data-msgid', '')
                
                # 过滤摸鱼人日历相关文章
                if '摸鱼人日历' in title and link:
                    # 解码HTML实体
                    link = html.unescape(link)
                    moyu_articles.append({
                        'title': title,
                        'link': link,
                        'msgid': int(msgid) if msgid.isdigit() else 0
                    })
            
            if not moyu_articles:
                self.logger.warning("未找到摸鱼人日历相关文章")
                return None
            
            # 直接取第一篇文章，因为列表中第一篇永远是最新的
            latest_article = moyu_articles[0]
            
            self.logger.info(f"找到最新文章: {latest_article['title']}")
            self.logger.info(f"文章链接: {latest_article['link']}")
            
            return {
                'title': latest_article['title'],
                'link': latest_article['link'],
                'msgid': latest_article['msgid']
            }
            
        except FileNotFoundError:
            self.logger.error(f"文件不存在: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"解析失败: {e}")
            return None
    
    def get_article_images(self, article_url: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取文章内的图片链接
        
        Args:
            article_url: 文章详情页面URL
            
        Returns:
            包含图片信息的列表
        """
        try:
            self.logger.info(f"正在获取文章图片: {article_url}")
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            images = []
            
            # 查找所有图片标签
            img_tags = soup.find_all('img')
            
            for idx, img in enumerate(img_tags):
                # 获取图片URL，优先使用data-src，然后是src
                img_url = img.get('data-src') or img.get('src')
                
                if not img_url:
                    continue
                
                # 解码HTML实体
                img_url = html.unescape(img_url)
                
                # 获取图片相关属性
                img_info = {
                    'url': img_url,
                    'alt': img.get('alt', ''),
                    'index': idx,
                    'class': ' '.join(img.get('class', [])),
                    'data_type': img.get('data-type', ''),
                    'width': img.get('data-w', ''),
                    'height': img.get('data-h', ''),
                    'data_ratio': img.get('data-ratio', ''),
                    'data_croporisrc': img.get('data-croporisrc', '')
                }
                
                # 过滤出微信图片链接
                if 'mmbiz.qpic.cn' in img_url:
                    images.append(img_info)
            
            self.logger.info(f"找到 {len(images)} 张微信图片")
            return images if images else None
            
        except requests.RequestException as e:
            self.logger.error(f"请求文章页面失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"解析文章图片失败: {e}")
            return None
    
    def get_main_calendar_image(self, article_url: str) -> Optional[str]:
        """
        获取文章中的主要日历图片
        
        Args:
            article_url: 文章详情页面URL
            
        Returns:
            主要日历图片的URL
        """
        images = self.get_article_images(article_url)
        
        if not images:
            return None
        
        # 优化的摸鱼人日历图片识别逻辑
        calendar_candidates = []
        total_images = len(images)
        
        for img in images:
            score = 0
            width = img.get('width')
            height = img.get('height')
            ratio = img.get('data_ratio')
            img_class = img.get('class', '')
            index = img.get('index', 0)
            img_url = img.get('url', '')
            alt_text = img.get('alt', '').lower()
            
            # 跳过明显不是日历的小图片
            if width and width.isdigit() and int(width) < 400:
                continue
            
            # 摸鱼人日历特征识别
            # 1. 尺寸特征：摸鱼人日历通常是正方形或接近正方形
            if width and height and width.isdigit() and height.isdigit():
                w, h = int(width), int(height)
                aspect_ratio = w / h
                
                # 摸鱼人日历的典型宽高比范围
                if 0.9 <= aspect_ratio <= 1.1:  # 接近正方形
                    score += 40
                elif 0.8 <= aspect_ratio <= 1.3:  # 略微长方形
                    score += 25
                
                # 典型的摸鱼人日历尺寸（通常在600-1200像素范围）
                if 600 <= w <= 1200 and 600 <= h <= 1200:
                    score += 30
                elif w >= 500 and h >= 500:
                    score += 20
            
            # 2. 比例权重：data-ratio接近1的图片
            if ratio:
                try:
                    ratio_val = float(ratio)
                    if 0.9 <= ratio_val <= 1.1:  # 接近正方形
                        score += 35
                    elif 0.8 <= ratio_val <= 1.3:
                        score += 20
                except:
                    pass
            
            # 3. 位置权重：摸鱼人日历通常在文章前半部分
            if total_images > 1:
                # 前30%的图片得分更高（通常日历图在文章开头）
                if index <= total_images * 0.3:
                    score += 35
                elif index <= total_images * 0.6:
                    score += 20
                else:
                    score -= 10  # 后面的图片可能是其他内容
            
            # 4. CSS类权重
            if 'rich_pages' in img_class or 'wxw-img' in img_class:
                score += 25
            if 'rich_media' in img_class:
                score += 15
            
            # 5. Alt文本特征识别
            calendar_keywords = ['摸鱼', '日历', 'calendar', '今天', '星期', '节日', '假期']
            for keyword in calendar_keywords:
                if keyword in alt_text:
                    score += 20
                    break
            
            # 6. URL特征权重
            url_keywords = ['calendar', 'date', 'day', 'moyu', '摸鱼']
            for keyword in url_keywords:
                if keyword in img_url.lower():
                    score += 15
                    break
            
            # 7. 文件大小推测（通过URL参数）
            # 摸鱼人日历图片通常比较大，包含丰富内容
            if 'wx_fmt=png' in img_url or 'wx_fmt=jpeg' in img_url:
                score += 10
            
            # 8. 排除明显不是日历的图片
            exclude_keywords = ['avatar', 'logo', 'icon', 'qrcode', '二维码', '头像']
            for keyword in exclude_keywords:
                if keyword in alt_text or keyword in img_url.lower():
                    score -= 30
                    break
            
            calendar_candidates.append((score, img))
            
            self.logger.debug(f"图片 {index}: 尺寸={width}x{height}, 比例={ratio}, 类={img_class}, 得分={score}")
        
        if not calendar_candidates:
            # 如果没有合适的候选图片，选择第一张较大的图片
            for img in images:
                width = img.get('width')
                if width and width.isdigit() and int(width) >= 300:
                    if img.get('data_croporisrc'):
                        return img['data_croporisrc']
                    else:
                        return img['url']
            return images[0]['url'] if images else None
        
        # 按得分排序，选择得分最高的图片
        calendar_candidates.sort(key=lambda x: x[0], reverse=True)
        best_candidate = calendar_candidates[0]
        main_image = best_candidate[1]
        
        self.logger.info(f"选择的摸鱼人日历图片: 索引={main_image.get('index')}, 得分={best_candidate[0]}, 尺寸={main_image.get('width')}x{main_image.get('height')}")
        
        # 优先返回高质量原图
        if main_image.get('data_croporisrc'):
            return main_image['data_croporisrc']
        else:
            return main_image['url']
    
    def verify_calendar_image(self, image_url: str) -> bool:
        """
        验证图片是否为摸鱼人日历图片
        
        Args:
            image_url: 图片URL
            
        Returns:
            是否为摸鱼人日历图片
        """
        try:
            # 下载图片进行验证
            response = self.session.get(image_url, timeout=15)
            response.raise_for_status()
            
            # 使用PIL打开图片
            img = Image.open(io.BytesIO(response.content))
            width, height = img.size
            
            # 摸鱼人日历的典型特征验证
            aspect_ratio = width / height
            
            # 1. 尺寸验证：摸鱼人日历通常是正方形或接近正方形，且尺寸较大
            if width < 400 or height < 400:
                self.logger.debug(f"图片尺寸过小: {width}x{height}")
                return False
            
            if not (0.7 <= aspect_ratio <= 1.4):
                self.logger.debug(f"图片宽高比不符合日历特征: {aspect_ratio}")
                return False
            
            # 2. 文件大小验证：摸鱼人日历内容丰富，文件通常较大
            content_length = len(response.content)
            if content_length < 50000:  # 小于50KB的图片可能不是日历
                self.logger.debug(f"图片文件过小: {content_length} bytes")
                return False
            
            # 3. 颜色复杂度验证：摸鱼人日历通常包含多种颜色
            # 转换为RGB模式进行分析
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 简单的颜色复杂度检测：统计不同颜色的数量
            colors = img.getcolors(maxcolors=256*256*256)
            if colors and len(colors) < 100:  # 颜色种类太少可能不是复杂的日历图
                self.logger.debug(f"图片颜色种类过少: {len(colors)}")
                return False
            
            self.logger.info(f"图片验证通过: {width}x{height}, 文件大小: {content_length} bytes, 宽高比: {aspect_ratio:.2f}")
            return True
            
        except Exception as e:
            self.logger.warning(f"图片验证失败: {e}")
            return True  # 验证失败时默认认为是有效图片
    
    def get_complete_moyu_info(self, url: str = None, file_path: str = None, verify_image: bool = True) -> Optional[Dict[str, Any]]:
        """
        获取完整的摸鱼人日历信息，包括文章链接和日历图片
        
        Args:
            url: 微信公众号文章页面URL（可选）
            file_path: 本地HTML文件路径（可选）
            verify_image: 是否验证图片（可选，默认True）
            
        Returns:
            包含文章信息和图片链接的字典
        """
        # 先获取最新文章链接
        if url:
            article_info = self.get_latest_moyu_link(url)
        elif file_path:
            article_info = self.get_latest_moyu_link_from_file(file_path)
        else:
            self.logger.error("必须提供URL或文件路径")
            return None
        
        if not article_info:
            return None
        
        # 获取文章中的日历图片
        article_url = article_info['link']
        calendar_image = self.get_main_calendar_image(article_url)
        
        # 如果启用验证且找到了图片，进行验证
        if calendar_image and verify_image:
            if not self.verify_calendar_image(calendar_image):
                self.logger.warning("图片验证失败，尝试获取备选图片")
                # 如果验证失败，尝试获取其他候选图片
                images = self.get_article_images(article_url)
                if images and len(images) > 1:
                    # 尝试第二个候选图片
                    for img in images[1:]:
                        candidate_url = img.get('data_croporisrc') or img['url']
                        if self.verify_calendar_image(candidate_url):
                            calendar_image = candidate_url
                            self.logger.info(f"找到验证通过的备选图片: {calendar_image}")
                            break
        
        # 合并信息
        complete_info = article_info.copy()
        complete_info['calendar_image'] = calendar_image
        
        if calendar_image:
            self.logger.info(f"找到日历图片: {calendar_image}")
        else:
            self.logger.warning("未能获取到日历图片")
        
        return complete_info


def main():
    """主函数"""
    scraper = MoyuScraper()
    
    # 使用配置的微信链接获取完整信息
    print(f"正在从微信链接获取数据: {DEFAULT_WECHAT_URL[:100]}...")
    result = scraper.get_complete_moyu_info(url=DEFAULT_WECHAT_URL)
    
    if result:
        print("\n========== 最新摸鱼人日历文章 ==========")
        print(f"标题: {result['title']}")
        print(f"链接: {result['link']}")
        print(f"消息ID: {result['msgid']}")
        if result.get('calendar_image'):
            print(f"日历图片: {result['calendar_image']}")
        print("=====================================\n")
        
        # 保存到JSON文件
        with open('latest_moyu_article.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("结果已保存到 latest_moyu_article.json")
    else:
        print("未能获取到最新的摸鱼人日历文章")


if __name__ == "__main__":
    main()