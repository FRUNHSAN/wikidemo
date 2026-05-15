"""
AI服务客户端
支持OpenAI、Claude等主流AI服务
提供统一的AI接口供插件调用
"""

import os
import logging
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger('AIClient')


class AIClientBase(ABC):
    """AI客户端基类"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass

    @abstractmethod
    def summarize(self, text: str, **kwargs) -> str:
        """总结文本"""
        pass

    @abstractmethod
    def extract_keywords(self, text: str, **kwargs) -> List[str]:
        """提取关键词"""
        pass


class OpenAIClient(AIClientBase):
    """OpenAI客户端"""

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model

        if not self.api_key:
            logger.warning("OpenAI API Key未配置，AI功能将不可用")

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """生成文本"""
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content.strip()

        except ImportError:
            logger.error("未安装openai库，请运行: pip install openai")
            return ""
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return ""

    def summarize(self, text: str, max_words: int = 200) -> str:
        """总结文本"""
        prompt = f"""请对以下内容进行简洁的总结（{max_words}字以内），突出关键信息：

{text}

总结："""

        return self.generate(prompt, max_tokens=500, temperature=0.5)

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        prompt = f"""请从以下文本中提取最重要的{max_keywords}个关键词，以逗号分隔：

{text}

关键词："""

        result = self.generate(prompt, max_tokens=100, temperature=0.3)
        return [kw.strip() for kw in result.split(',') if kw.strip()]

    def classify_content(self, text: str, categories: List[str] = None) -> str:
        """分类内容"""
        if not categories:
            categories = ["技术", "新闻", "教程", "观点", "其他"]

        categories_str = ", ".join(categories)
        prompt = f"""请将以下内容分类到以下类别之一：{categories_str}

内容：
{text}

类别："""

        return self.generate(prompt, max_tokens=50, temperature=0.3)

    def translate(self, text: str, target_language: str = "中文") -> str:
        """翻译文本"""
        prompt = f"""请将以下内容翻译成{target_language}：

{text}

翻译："""

        return self.generate(prompt, temperature=0.3)


class ClaudeClient(AIClientBase):
    """Anthropic Claude客户端"""

    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.model = model

        if not self.api_key:
            logger.warning("Claude API Key未配置")

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """生成文本"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            message = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text.strip()

        except ImportError:
            logger.error("未安装anthropic库，请运行: pip install anthropic")
            return ""
        except Exception as e:
            logger.error(f"Claude API调用失败: {e}")
            return ""

    def summarize(self, text: str, max_words: int = 200) -> str:
        """总结文本"""
        prompt = f"""请对以下内容进行简洁的总结（{max_words}字以内）：

{text}"""

        return self.generate(prompt, max_tokens=500)

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        prompt = f"""请从以下文本中提取最重要的{max_keywords}个关键词，以逗号分隔：

{text}"""

        result = self.generate(prompt, max_tokens=100)
        return [kw.strip() for kw in result.split(',') if kw.strip()]


class AIFactory:
    """AI客户端工厂"""

    @staticmethod
    def create(provider: str = "openai", **kwargs) -> AIClientBase:
        """
        创建AI客户端

        Args:
            provider: AI服务提供商 ("openai", "claude")
            **kwargs: 其他参数

        Returns:
            AIClientBase实例
        """
        if provider == "openai":
            return OpenAIClient(**kwargs)
        elif provider == "claude":
            return ClaudeClient(**kwargs)
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")


# 全局AI客户端实例
_ai_client = None


def get_ai_client(provider: str = "openai", **kwargs) -> AIClientBase:
    """获取全局AI客户端实例"""
    global _ai_client

    if _ai_client is None:
        _ai_client = AIFactory.create(provider, **kwargs)

    return _ai_client


def reset_ai_client():
    """重置AI客户端"""
    global _ai_client
    _ai_client = None
