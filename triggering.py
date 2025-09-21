# 트리거링 로직(전체 보드 참고 + 정신 연산 표기)

import random
import streamlit as st
from app_utils import chat_once_for_persona, add_to_board, PERSONAS

# 참여 가중치(성격 반영)
AGENT_WEIGHTS = {
    "Woojin": 0.40,
    "John":   0.20,
    "Xingda": 0.20,
    "Ricardo":0.20,
}

# 연산 목록·선호도
MENTAL_OPS = ["generalization", "instantiation", "improving", "combining", "free_association"]
OP_WEIGHTS = {
    "Woojin":  {"generalization":0.15, "instantiation":0.15, "improving":0.25, "combining":0.30, "free_association":0.15},
    "John":    {"generalization":0.20, "instantiation":0.35, "improving":0.25, "combining":0.10, "free_association":0.10},
    "Xingda":  {"generalization":0.25, "instantiation":0.10, "improving":0.15, "combining":0.20, "free_association":0.30},
    "Ricardo": {"generalization":0.20, "instantiation":0.20, "improving":0.20, "combining":0.20, "free_association":0.20},
}

def weighted_choice(weight_map: dict[str, float]) -> str:
    names   = list(weight_map.keys())
    weights = list(weight_map.values())
    return random.choices(names, weights=weights, k=1)[0]

def build_op_prompt(problem: str, agent: str, op: str, all_ideas: list[str], picked: list[str]) -> str:
    board_txt  = "\n".join(f"- {x}" for x in all_ideas)
    picked_txt = "\n".join(f"- {p}" for p in picked)
    op_desc = {
        "generalization":   "보드 아이디어를 더 넓은 개념으로 일반화함",
        "instantiation":    "개념 아이디어를 구체적 사례/타깃으로 특화함",
        "improving":        "기존 아이디어를 비용/품질/속도/사용성 중 한 측면에서 개선함",
        "combining":        "서로 다른 2~3개 아이디어를 결합하여 새 아이디어를 만듦",
        "free_association": "보드 아이디어에서 연상되는 개념으로 자유롭게 확장함",
    }[op]
    return (
        f"브레인스토밍 문제: {problem}\n"
        f"역할: {agent}({PERSONAS[agent]['bio']})\n"
        f"공유 보드(전체):\n{board_txt}\n\n"
        f"트리거 연산: {op} — {op_desc}\n"
        f"참고 아이디어:\n{picked_txt}\n\n"
        f"규칙:\n- 한국어 한 줄 아이디어 1개만 출력\n- 번호/불릿/따옴표/설명 금지"
    )

def trigger_one_round_full():
    if not st.session_state["board"]:
        st.warning("보드 비어 있음. 먼저 퍼징 실행 필요함")
        return None

    agent = weighted_choice(AGENT_WEIGHTS)
    op    = weighted_choice(OP_WEIGHTS[agent])
    all_ideas = [idea for _, idea in st.session_state["board"]]

    if op == "combining" and len(all_ideas) >= 2:
        picked = random.sample(all_ideas, k=2)
    else:
        picked = [random.choice(all_ideas)]

    user_prompt = build_op_prompt(st.session_state["brain_problem"], agent, op, all_ideas, picked)
    idea = chat_once_for_persona(agent, user_prompt)
    add_to_board(agent, idea)

    st.session_state["last_trigger"] = {"agent": agent, "op": op, "picked": picked, "idea": idea}
    return st.session_state["last_trigger"]
