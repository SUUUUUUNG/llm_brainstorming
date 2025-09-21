# 퍼징 로직(4명×10개) 

import time
import streamlit as st
from app_utils import PERSONAS, chat_once_for_persona, add_to_board

# 안전한 라인 파서임
def parse_ideas(text: str, max_n: int = 10) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        s = s.lstrip("-•*").strip()
        if s and s[:3].strip()[:1].isdigit():
            # "1) ..." 또는 "2. ..." 번호 제거함
            s = s.split(")", 1)[-1] if ")" in s[:3] else s.split(".", 1)[-1] if "." in s[:3] else s
            s = s.strip()
        if s:
            lines.append(s)
        if len(lines) >= max_n:
            break
    return lines

# 에이전트별 10개 생성(재시도 포함)함
def purge_10_for(persona: str) -> list[str]:
    user = (
        f"브레인스토밍 문제: {st.session_state['brain_problem']}\n"
        f"조건: 한 줄 아이디어 10개를 '각 줄마다 하나씩' 출력. 번호/불릿 없이 줄바꿈으로만 구분."
    )
    tries, last_err = 0, None
    while tries < 3:
        tries += 1
        try:
            out = chat_once_for_persona(persona, user)
            ideas = parse_ideas(out, 10)
            if ideas:
                return ideas
            # 포맷 미준수 시 재유도함
            out = chat_once_for_persona(persona, "방금 답변을 '한 줄 아이디어 10개, 줄바꿈만' 규칙에 맞춰 다시 출력.")
            ideas = parse_ideas(out, 10)
            if ideas:
                return ideas
        except Exception as e:
            last_err = e
            time.sleep(0.8)  # rate limit 완화용
    st.error(f"[{persona}] 퍼징 실패: {last_err}")
    return []

# 퍼징 전체 실행(4명×10개)함
def run_purging():
    # 보드 초기화는 1회만 수행함
    st.session_state["board"].clear()
    st.session_state["phase"] = "purging"

    summary: dict[str, int] = {}
    # Streamlit 최신(>=1.29)에서 상태 표시 사용함, 아니면 fallback함
    try:
        for persona in PERSONAS.keys():
            with st.status(f"[{persona}] 아이디어 생성 중...", expanded=False) as status:
                ideas = purge_10_for(persona)
                for idea in ideas:
                    add_to_board(persona, idea)
                    time.sleep(0.1)
                summary[persona] = len(ideas)
                status.update(label=f"[{persona}] 완료: {len(ideas)}개", state="complete")
    except Exception:
        for persona in PERSONAS.keys():
            st.write(f"[{persona}] 아이디어 생성 중...")
            ideas = purge_10_for(persona)
            for idea in ideas:
                add_to_board(persona, idea)
                time.sleep(0.1)
            summary[persona] = len(ideas)
            st.write(f"[{persona}] 완료: {len(ideas)}개")

    st.session_state["phase"] = "triggering"
    st.success("퍼징 완료 → Phase: triggering")
    st.write("에이전트별 생성 개수:", summary)
