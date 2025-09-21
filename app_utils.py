# 공통 유틸: OpenAI 클라이언트, 페르소나, 세션상태 초기화, 공용 함수 정의함
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv; load_dotenv()

# OpenAI 클라이언트 생성함
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 페르소나 정의함(모델/온도 포함)
PERSONAS = {
    "Woojin": {"bio": "인체공학 교수, 외향적",              "model": "gpt-4o-mini", "temperature": 1.2},
    "John":   {"bio": "정원사, 내향적·평가 민감",           "model": "gpt-4o-mini", "temperature": 1.0},
    "Xingda": {"bio": "화가, 내향적·멀티모달 연상 강함",     "model": "gpt-4o-mini", "temperature": 1.3},
    "Ricardo":{"bio": "피트니스 트레이너, 프리라이더 성향", "model": "gpt-4o-mini", "temperature": 1.1},
}

# 세션 상태 초기화함
def init_states():
    if "brain_problem" not in st.session_state:
        st.session_state["brain_problem"] = "LLM 기반 비즈니스 아이디어"
    if "brains" not in st.session_state:
        st.session_state["brains"] = {p: {"history": [], "ideas": [], "count": 0} for p in PERSONAS}
    if "board" not in st.session_state:
        st.session_state["board"] = []  # [(agent, idea)]
    if "phase" not in st.session_state:
        st.session_state["phase"] = "purging"

# 해당 페르소나의 ‘고유 뇌’ 역할 시스템 메시지 반환함
def persona_prompt_header(persona: str) -> list[dict]:
    bio = PERSONAS[persona]["bio"]
    sys = f"너는 아이디어 브레인스토밍 에이전트임. 역할: {persona}({bio}). 출력은 한국어 한 줄 아이디어 중심."
    return [{"role": "system", "content": sys}]

def chat_once_for_persona(persona: str, user_content: str) -> str:
    brain = st.session_state["brains"][persona]
    model = PERSONAS[persona]["model"]
    temp  = PERSONAS[persona]["temperature"]

    # 히스토리가 비어있으면 시스템 프롬프트 주입함
    if not brain["history"]:
        brain["history"].extend(persona_prompt_header(persona))

    # 사용자 입력 추가
    brain["history"].append({"role": "user", "content": user_content})

    # 히스토리 길이 제한함. 너무 길어지면 최근 12 turn만 유지함(시스템 포함)
    MAX_MSG = 25
    if len(brain["history"]) > MAX_MSG:
        brain["history"] = [brain["history"][0]] + brain["history"][-(MAX_MSG - 1):]

    # 호출
    resp = client.chat.completions.create(
        model=model,
        messages=brain["history"],
        temperature=temp,
    )
    out = resp.choices[0].message.content.strip()
    
    # 어시스턴트 응답을 히스토리에 저장함
    brain["history"].append({"role": "assistant", "content": out})
    return out

def add_to_board(agent: str, idea: str):
    st.session_state["board"].append((agent, idea))
    st.session_state["brains"][agent]["ideas"].append(idea)
    st.session_state["brains"][agent]["count"] += 1
