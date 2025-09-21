# 메인 UI: 문제 입력, 퍼징 실행, 트리거 실행, 보드/기여도 표시만 담당함

import streamlit as st
import pandas as pd

from app_utils import init_states, PERSONAS
from purging import run_purging
from triggering import trigger_one_round_full

# 세션 상태 초기화함
init_states()

st.title("브레인스토밍 MVP — 퍼징/트리거(모듈 분리)")

# 문제 정의 입력함
st.session_state["brain_problem"] = st.text_input("문제 정의", st.session_state["brain_problem"])

# 버튼 영역
colA, colB, colC = st.columns(3)
with colA:
    if st.button("퍼징 실행 (4×10)"):
        run_purging()
with colB:
    if st.button("트리거 라운드 실행 (전체 보드 기반)"):
        lt = trigger_one_round_full()
        if lt:
            st.success(f"추가됨: [{lt['agent']}] ({lt['op']}) {lt['idea']}")
with colC:
    if st.button("새 세션 시작 (보드+히스토리 초기화)"):
        # app_utils.init_states()는 초기 생성만 하므로 직접 초기화함
        st.session_state["board"] = []
        st.session_state["brains"] = {p: {"history": [], "ideas": [], "count": 0} for p in PERSONAS}
        st.session_state["phase"] = "purging"
        st.success("초기화 완료함")

# 보드 표 표시함
st.subheader("공유 보드 (표)")
if st.session_state["board"]:
    df = pd.DataFrame(st.session_state["board"], columns=["agent", "idea"])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("보드가 비어 있음")

# 마지막 트리거 정보 표시함
st.subheader("마지막 트리거 정보")
lt = st.session_state.get("last_trigger")
if lt:
    st.write(f"- 에이전트: {lt['agent']}")
    st.write(f"- 정신 연산: {lt['op']}")
    st.write("- 참고 아이디어:")
    for p in lt["picked"]:
        st.write(f"  ※ {p}")
    st.write(f"- 결과 아이디어: {lt['idea']}")
else:
    st.info("아직 트리거 기록 없음")

# 기여도 차트 표시함
st.subheader("기여도 분포")
st.bar_chart({p: st.session_state["brains"][p]["count"] for p in PERSONAS})
