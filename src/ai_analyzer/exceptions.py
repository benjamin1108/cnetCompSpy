# 定义自定义异常类
class AIAnalyzerError(Exception):
    """AI分析器模块的基础异常类"""
    pass

class ParseError(AIAnalyzerError):
    """AI响应解析错误"""
    pass

class APIError(AIAnalyzerError):
    """API调用相关错误 (网络、HTTP状态码、请求构建等)"""
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text 