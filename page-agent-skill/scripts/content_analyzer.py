#!/usr/bin/env python3
"""
内容分析模块 - 使用DeepSeek API进行深度内容分析
"""

import json
import time
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """内容分析器，使用DeepSeek API进行深度分析"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化内容分析器
        
        Args:
            api_key: DeepSeek API密钥，如果为None则使用模拟分析
        """
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.use_real_api = api_key is not None
        
        if self.use_real_api:
            logger.info("使用真实的DeepSeek API进行分析")
        else:
            logger.info("使用模拟的DeepSeek分析（无API密钥）")
    
    def analyze_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析网页内容
        
        Args:
            content_data: 从content_extractor提取的内容数据
            
        Returns:
            分析结果字典
        """
        try:
            if self.use_real_api:
                return self._analyze_with_deepseek(content_data)
            else:
                return self._simulate_analysis(content_data)
        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return self._create_error_analysis(content_data)
    
    def _analyze_with_deepseek(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用真实的DeepSeek API进行分析"""
        try:
            # 准备分析提示
            analysis_prompt = self._create_analysis_prompt(content_data)
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的网页内容分析师。请分析网页内容并提供详细的评估报告。"
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result["choices"][0]["message"]["content"]
            
            # 解析分析结果
            return self._parse_analysis_result(analysis_text, content_data)
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"DeepSeek API调用失败，使用模拟分析: {e}")
            return self._simulate_analysis(content_data)
        except Exception as e:
            logger.error(f"DeepSeek分析处理失败: {e}")
            return self._simulate_analysis(content_data)
    
    def _simulate_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟DeepSeek分析（当没有API密钥时使用）"""
        logger.info("执行模拟内容分析")
        
        # 提取关键信息
        title = content_data.get("title", "无标题")
        text_content = content_data.get("text_content", "")
        word_count = len(text_content.split())
        
        # 分析内容质量
        quality_score = self._calculate_quality_score(content_data)
        
        # 生成分析报告
        analysis = {
            "quality_assessment": {
                "overall_score": quality_score,
                "readability": self._assess_readability(text_content),
                "depth": self._assess_depth(text_content),
                "originality": self._assess_originality(text_content),
                "engagement": self._assess_engagement(text_content)
            },
            "content_structure": {
                "has_introduction": "引言" in text_content[:500] or "介绍" in text_content[:500],
                "has_conclusion": "结论" in text_content[-500:] or "总结" in text_content[-500:],
                "section_count": text_content.count("\n\n") + 1,
                "average_section_length": word_count / max(1, text_content.count("\n\n") + 1)
            },
            "target_audience": self._identify_audience(text_content),
            "key_topics": self._extract_key_topics(text_content),
            "recommendations": self._generate_recommendations(content_data, quality_score),
            "analysis_method": "simulated_analysis"
        }
        
        return analysis
    
    def _create_analysis_prompt(self, content_data: Dict[str, Any]) -> str:
        """创建分析提示"""
        title = content_data.get("title", "无标题")
        text_content = content_data.get("text_content", "")[:3000]  # 限制长度
        meta_description = content_data.get("meta_description", "")
        
        prompt = f"""请分析以下网页内容并提供专业评估：

网页标题: {title}
元描述: {meta_description}
内容长度: {len(text_content)} 字符

网页内容:
{text_content}

请提供以下分析：
1. 内容质量评估（可读性、深度、原创性、参与度）
2. 内容结构分析
3. 目标受众识别
4. 关键主题提取
5. 改进建议

请以JSON格式返回分析结果，包含具体的评分和建议。"""
        
        return prompt
    
    def _parse_analysis_result(self, analysis_text: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析DeepSeek返回的分析结果"""
        try:
            # 尝试提取JSON部分
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                analysis = json.loads(json_str)
                analysis["analysis_method"] = "deepseek_api"
                return analysis
        except json.JSONDecodeError:
            logger.warning("无法解析DeepSeek返回的JSON，使用模拟分析")
        
        # 如果无法解析，使用模拟分析
        return self._simulate_analysis(content_data)
    
    def _calculate_quality_score(self, content_data: Dict[str, Any]) -> float:
        """计算内容质量分数"""
        text_content = content_data.get("text_content", "")
        word_count = len(text_content.split())
        
        # 基于多个因素计算分数
        score = 0.0
        
        # 内容长度
        if word_count > 1000:
            score += 0.3
        elif word_count > 500:
            score += 0.2
        elif word_count > 200:
            score += 0.1
        
        # 标题质量
        title = content_data.get("title", "")
        if title and len(title) > 10 and len(title) < 70:
            score += 0.2
        
        # 元描述质量
        meta_desc = content_data.get("meta_description", "")
        if meta_desc and len(meta_desc) > 50 and len(meta_desc) < 160:
            score += 0.1
        
        # 图片数量
        images = content_data.get("images", [])
        if len(images) >= 3:
            score += 0.1
        
        # 链接质量
        links = content_data.get("links", [])
        if len(links) >= 5:
            score += 0.1
        
        # 结构质量
        paragraphs = text_content.count('\n\n')
        if paragraphs >= 5:
            score += 0.2
        
        return min(1.0, score)
    
    def _assess_readability(self, text: str) -> str:
        """评估可读性"""
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        if sentence_count == 0:
            return "未知"
        
        avg_words_per_sentence = word_count / sentence_count
        
        if avg_words_per_sentence < 15:
            return "优秀"
        elif avg_words_per_sentence < 25:
            return "良好"
        elif avg_words_per_sentence < 35:
            return "一般"
        else:
            return "较差"
    
    def _assess_depth(self, text: str) -> str:
        """评估内容深度"""
        word_count = len(text.split())
        
        if word_count > 1500:
            return "深度"
        elif word_count > 800:
            return "中等"
        elif word_count > 300:
            return "基础"
        else:
            return "浅显"
    
    def _assess_originality(self, text: str) -> str:
        """评估原创性（简化版本）"""
        # 这是一个简化的评估，实际应用中可能需要更复杂的算法
        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        
        if total_words == 0:
            return "未知"
        
        uniqueness_ratio = unique_words / total_words
        
        if uniqueness_ratio > 0.7:
            return "高"
        elif uniqueness_ratio > 0.5:
            return "中等"
        else:
            return "低"
    
    def _assess_engagement(self, text: str) -> str:
        """评估参与度"""
        # 基于问题、感叹号、第二人称等指标
        question_count = text.count('?')
        exclamation_count = text.count('!')
        you_count = text.lower().count('你') + text.lower().count('您')
        
        engagement_score = question_count + exclamation_count * 0.5 + you_count * 0.3
        
        if engagement_score > 10:
            return "高"
        elif engagement_score > 5:
            return "中等"
        elif engagement_score > 2:
            return "低"
        else:
            return "很低"
    
    def _identify_audience(self, text: str) -> list:
        """识别目标受众"""
        audiences = []
        text_lower = text.lower()
        
        # 基于关键词识别受众
        business_keywords = ['企业', '公司', '商业', '营销', '销售', '管理', '领导']
        tech_keywords = ['技术', '编程', '代码', '开发', '软件', '硬件', 'AI', '人工智能']
        general_keywords = ['生活', '健康', '教育', '学习', '旅行', '美食']
        
        if any(keyword in text_lower for keyword in business_keywords):
            audiences.append("商业人士")
        if any(keyword in text_lower for keyword in tech_keywords):
            audiences.append("技术人员")
        if any(keyword in text_lower for keyword in general_keywords):
            audiences.append("普通读者")
        
        if not audiences:
            audiences.append("一般受众")
        
        return audiences
    
    def _extract_key_topics(self, text: str, max_topics: int = 5) -> list:
        """提取关键主题"""
        # 简化的主题提取，实际应用中可能需要NLP技术
        words = text.lower().split()
        common_words = {'的', '了', '在', '是', '和', '与', '或', '有', '我', '你', '他', '她', '它', '这', '那'}
        
        # 过滤常见词，统计词频
        word_freq = {}
        for word in words:
            if len(word) > 1 and word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 获取最常见的词作为主题
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topics = [word for word, freq in sorted_words[:max_topics]]
        
        return topics
    
    def _generate_recommendations(self, content_data: Dict[str, Any], quality_score: float) -> list:
        """生成改进建议"""
        recommendations = []
        text_content = content_data.get("text_content", "")
        word_count = len(text_content.split())
        
        # 基于质量分数生成建议
        if quality_score < 0.5:
            recommendations.append("内容质量较低，建议增加更多有价值的信息")
        
        if word_count < 500:
            recommendations.append("内容较短，建议扩展内容深度和广度")
        
        if not content_data.get("meta_description"):
            recommendations.append("缺少元描述，建议添加50-160字符的描述")
        
        images = content_data.get("images", [])
        if len(images) < 2:
            recommendations.append("图片较少，建议添加相关图片提高可读性")
        
        links = content_data.get("links", [])
        if len(links) < 3:
            recommendations.append("内部链接较少，建议添加相关内部链接")
        
        # 确保有建议
        if not recommendations:
            recommendations.append("内容质量良好，继续保持")
        
        return recommendations
    
    def _create_error_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建错误分析结果"""
        return {
            "quality_assessment": {
                "overall_score": 0.0,
                "readability": "未知",
                "depth": "未知",
                "originality": "未知",
                "engagement": "未知"
            },
            "content_structure": {
                "has_introduction": False,
                "has_conclusion": False,
                "section_count": 0,
                "average_section_length": 0
            },
            "target_audience": ["未知"],
            "key_topics": [],
            "recommendations": ["分析过程中出现错误，请检查网络连接或API配置"],
            "analysis_method": "error",
            "error": True
        }


if __name__ == "__main__":
    # 测试代码
    import sys
    logging.basicConfig(level=logging.INFO)
    
    # 创建测试数据
    test_data = {
        "title": "测试网页标题",
        "text_content": "这是一个测试网页内容。它包含一些信息供分析使用。网页内容分析是一个重要的SEO优化步骤。",
        "meta_description": "测试元描述",
        "images": ["image1.jpg", "image2.jpg"],
        "links": ["https://example.com/page1", "https://example.com/page2"]
    }
    
    analyzer = ContentAnalyzer()
    result = analyzer.analyze_content(test_data)
    
    print("分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))