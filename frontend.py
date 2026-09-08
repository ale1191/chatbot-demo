import streamlit as st
import requests

# ============ 页面配置 ============
st.set_page_config(
    page_title="AI 聊天助手",
    page_icon="💬",
    layout="centered",
)

st.title("💬 AI 聊天助手")
st.caption("基于 FastAPI + Streamlit + DeepSeek 构建")


# ============ 侧边栏：后端地址 + 清空对话 ============
API_URL = st.sidebar.text_input(
    "后端地址",
    value="http://127.0.0.1:8000/chat",
    help="FastAPI 后端的 /chat 接口地址",
)

with st.sidebar:
    st.divider()
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with st.sidebar:
    try:
        info = requests.get(API_URL.replace("/chat", "/info"), timeout=5).json()
        mode_emoji = "🟢" if info["mode"] == "real" else "🟡"
        st.write(f"{mode_emoji} 模式: {info['mode']}")
        st.write(f"🤖 模型: {info['model']}")
    except Exception:
        st.write("❌ 连不上后端")


# ============ 1. 初始化对话历史 ============
# st.session_state 是页面级存储，跨 rerun 保持，刷新页面会清空
if "messages" not in st.session_state:
    st.session_state.messages = []


# ============ 2. 显示历史对话 ============
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):                                # 角色气泡
        st.markdown(msg["content"])                                    # 气泡内显示内容


# ============ 3. 输入框 + 发送 ============
if prompt := st.chat_input("说点什么...（按 Enter 发送）"):
    # 3.1 把用户消息加入历史并立刻显示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3.2 调 FastAPI 后端（在 AI 气泡里显示）
    with st.chat_message("assistant"):
        with st.spinner("🤔 思考中..."):
            try:
                resp = requests.post(
                    API_URL,
                    json={
                        "message": prompt,
                        # 不含刚加的 user（让后端拼接，避免重复）
                        "history": st.session_state.messages[:-1],
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                reply = resp.json()["reply"]
            except requests.exceptions.Timeout:
                reply = "❌ 请求超时（>30s），请稍后重试"
            except requests.exceptions.ConnectionError:
                reply = "❌ 连不上后端，请检查 FastAPI 是否启动（python backend.py）"
            except Exception as e:
                reply = f"❌ 出错了：{type(e).__name__}: {e}"

        st.markdown(reply)

    # 3.3 把 AI 回复加入历史
    st.session_state.messages.append({"role": "assistant", "content": reply})
