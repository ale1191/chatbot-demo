import os
from dotenv import load_dotenv
load_dotenv()
import requests
from typing import List
from pydantic import BaseModel, Field
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ============ LLM 调用函数 ============
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
URL = "https://api.deepseek.com/v1/chat/completions"


def call_llm(messages: list, temperature: float = 0.7) -> str:
    """调 LLM；没 API Key 时降级为 echo（方便学习）"""
    if not API_KEY:
        last = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "（没找到用户消息）",
        )
        return f"[模拟回复] 你说的是：{last}"

    try:
        resp = requests.post(
            URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": "deepseek-chat", "messages": messages, "temperature": temperature},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[调用失败] {type(e).__name__}: {e}"


# ============ 数据模型（Pydantic）============
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)        # 消息内容
    temperature: float = Field(0.7, ge=0.0, le=2.0)                 # 温度 0-2
    history: List[dict] = Field(default_factory=list)                # 多轮历史


class ChatResponse(BaseModel):
    reply: str
    model: str = "deepseek-chat"
    used_real_api: bool


# ============ 创建应用 + 加 CORS ============
app = FastAPI(title="我的 AI 聊天 API", version="1.0")

# 任务 1.A：CORS 中间件 —— 允许浏览器跨域调用
# 没有 CORS，Streamlit 前端会被浏览器拦截
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                                              # 生产环境写死域名
    allow_credentials=True,
    allow_methods=["*"],                                              # 允许所有 HTTP 方法
    allow_headers=["*"],
)


# 任务 1.B：统一错误处理 —— 兜底所有未捕获的异常
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    """任何未捕获的异常都返回 JSON 而不是 HTML"""
    return JSONResponse(
        status_code=500,
        content={
            "error": type(exc).__name__,
            "message": str(exc),
            "path": str(request.url),
        },
    )


# ============ 接口定义 ============
@app.get("/")
def root():
    """健康检查"""
    return {"status": "running", "has_api_key": bool(API_KEY)}
@app.get("/info")
def info():
    return {
        "model": "deepseek-chat",
        "has_api_key": bool(API_KEY),
        "mode": "real" if API_KEY else "mock",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """核心聊天接口（前端 Streamlit 调这个）"""
    messages = list(req.history) + [{"role": "user", "content": req.message}]
    reply = call_llm(messages, temperature=req.temperature)
    return ChatResponse(reply=reply, used_real_api=bool(API_KEY))


# ============ 启动 ============
if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 后端启动: http://127.0.0.1:8000")
    print("📖 API 文档: http://127.0.0.1:8000/docs")
    print("=" * 50)
    if not API_KEY:
        print("⚠️  未设置 DEEPSEEK_API_KEY，将使用 echo 模拟回复")
        print("   设置方法 (Windows): set DEEPSEEK_API_KEY=sk-xxx")
        print("   设置方法 (Mac/Linux): export DEEPSEEK_API_KEY=sk-xxx")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
