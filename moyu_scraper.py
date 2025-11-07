#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摸鱼人日历爬虫 - 获取最新摸鱼人日历文章链接和图片
"""

import requests
from bs4 import BeautifulSoup
import html
import json
import logging
from typing import Optional, Dict, Any, List

# 配置变量 - 容易修改的微信公众号链接
DEFAULT_WECHAT_URL = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxOTYyMzczNA==&action=getalbum&album_id=3743225907507462153&subscene=0&scenenote=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzAxOTYyMzczNA%3D%3D%26mid%3D2454356650%26idx%3D3%26sn%3Db1b9c97cc7bf61037ec23358ae49fc21%26chksm%3D8d7e87d0789afd79bba17838c0ebc30032a48ec592b15ce631c617d8f7b6489ae1854217123d%26xtrack%3D1%26scene%3D0%26subscene%3D7%26clicktime%3D1756172088%26enterid%3D1756172088%26sessionid%3D0%26ascene%3D7%26fasttmpl_type%3D0%26fasttmpl_fullversion%3D7876133-zh_CN-zip%26fasttmpl_flag%3D0%26realreporttime%3D1756172088652%26devicetype%3Dandroid-34%26version%3D2800315a%26nettype%3DWIFI%26abtest_cookie%3DAAACAA%253D%253D%26lang%3Dzh_CN%26session_us%3Dgh_a589f1b94a1b%26countrycode%3DCN%26exportkey%3Dn_ChQIAhIQA1t5yUVrdVlsNJ%252BopF7QRhLlAQIE97dBBAEAAAAAAC95BmOr4xkAAAAOpnltbLcz9gKNyK89dVj0h%252BwXpZKnm7RtJodhDfgbbsdkbhy7ZitAguP5Two94sEUtw%252FYDRFprtqBkW2tlQNNvpF01VvSM4xB8RMqIaTysNoP1JE85ZM8veAIqTDFgJlwFhmTr2nWFg6udZ8Nm%252FQ8mFP8oMFVh6hWIAaevoH8Y8NcrOCQ%252FJ1vMpBvp5yRy7HPltQZodArcVo7xi5OWzUWUx9%252BV%252BG31dFR74uONPXkZ26YqV5Bj5Uy%252Bm8UxYBKe4hBpDQxxpT%252Fzqzrv%252BKrEqw%253D%26pass_ticket%3DV35uCaA010EVXzou5598fycnm212HGyeKi21hYdh%252BSZvDprAS0eJTLODJbUV9tt2%26wx_header%3D3&nolastread=1#wechat_redirect"

class MoyuScraper:
    """摸鱼人日历爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            return {
                'title': latest_article['title'],
                'link': latest_article['link'],
                'msgid': latest_article['msgid']
            }
            
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
                    'index': idx,
                    'data_croporisrc': img.get('data-croporisrc', '')
                }
                
                # 过滤出微信图片链接
                if 'mmbiz.qpic.cn' in img_url:
                    images.append(img_info)
            
            self.logger.info(f"找到 {len(images)} 张微信图片")
            return images if images else None
            
        except Exception as e:
            self.logger.error(f"解析文章图片失败: {e}")
            return None
    
    def get_main_calendar_image(self, article_url: str) -> Optional[str]:
        """
        获取文章中的主要日历图片（简化版）
        
        Args:
            article_url: 文章详情页面URL
            
        Returns:
            主要日历图片的URL
        """
        images = self.get_article_images(article_url)
        
        if not images:
            return None
        
        # 核心图片匹配逻辑：
        # 1. 优先查找URL中包含'640?wx_fmt=png&from=appmsg'的图片
        for img in images:
            img_url = img.get('url', '')
            if '640?wx_fmt=png&from=appmsg' in img_url:
                self.logger.info(f"找到符合条件的日历图片: {img_url}")
                # 优先返回高质量原图
                if img.get('data_croporisrc'):
                    return img['data_croporisrc']
                else:
                    return img_url
        
        # 2. 如果没找到完全匹配的，返回第二张图片
        if len(images) >= 2:
            img = images[1]  # 返回第二张图片
            self.logger.info(f"返回第二张图片作为日历图片")
            if img.get('data_croporisrc'):
                return img['data_croporisrc']
            else:
                return img['url']
        
        # 3. 如果连两张图片都没有，返回第一张
        if images:
            img = images[0]
            self.logger.warning(f"只找到一张图片，返回第一张作为日历图片")
            if img.get('data_croporisrc'):
                return img['data_croporisrc']
            else:
                return img['url']
        
        return None
    
    def get_complete_moyu_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取完整的摸鱼人日历信息，包括文章链接和日历图片
        
        Args:
            url: 微信公众号文章页面URL
            
        Returns:
            包含文章信息和图片链接的字典
        """
        # 先获取最新文章链接
        article_info = self.get_latest_moyu_link(url)
        
        if not article_info:
            return None
        
        # 获取文章中的日历图片
        article_url = article_info['link']
        calendar_image = self.get_main_calendar_image(article_url)
        
        # 合并信息
        complete_info = article_info.copy()
        if calendar_image:
            complete_info['calendar_image'] = calendar_image
        
        return complete_info


def main():
    """主函数"""
    scraper = MoyuScraper()
    
    # 使用配置的微信链接获取完整信息
    print(f"正在从微信链接获取数据: {DEFAULT_WECHAT_URL[:100]}...")
    article_info = scraper.get_latest_moyu_link(DEFAULT_WECHAT_URL)
    
    if article_info:
        print("\n========== 最新摸鱼人日历文章 ==========")
        print(f"标题: {article_info['title']}")
        print(f"链接: {article_info['link']}")
        print(f"消息ID: {article_info['msgid']}")
        
        # 获取日历图片
        calendar_image = scraper.get_main_calendar_image(article_info['link'])
        if calendar_image:
            print(f"日历图片: {calendar_image}")
            article_info['calendar_image'] = calendar_image
        
        print("=====================================\n")
        
        # 保存到JSON文件
        with open('latest_moyu_article.json', 'w', encoding='utf-8') as f:
            json.dump(article_info, f, ensure_ascii=False, indent=2)
        print("结果已保存到 latest_moyu_article.json")
    else:
        print("未能获取到最新的摸鱼人日历文章")


if __name__ == "__main__":
    main()