# scripts/visualize_smoketest.py
import os
import shutil
import subprocess
from typing import TypedDict, Annotated, List

# 1) LangGraph 가져오기
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 2) 최소 상태 정의
class MiniState(TypedDict):
    messages: Annotated[List, add_messages]
    counter: int

# 3) 더미 노드 함수
def hello_node(state: MiniState):
    msgs = state.get("messages", [])
    msgs = msgs + [{"role": "system", "content": "hello from node A"}]
    return {"messages": msgs, "counter": state.get("counter", 0) + 1}

def world_node(state: MiniState):
    msgs = state.get("messages", [])
    msgs = msgs + [{"role": "system", "content": "hello from node B"}]
    return {"messages": msgs, "counter": state.get("counter", 0) + 1}

def build_app():
    # 4) 그래프 구성
    g = StateGraph(MiniState)
    g.add_node("A", hello_node)
    g.add_node("B", world_node)

    g.add_edge(START, "A")
    g.add_edge("A", "B")
    g.add_edge("B", END)

    # 5) 컴파일
    app = g.compile()
    return app

def save_graph_images(app, fmt: str = "png"):
    """
    LangGraph 내부 그래프를 이미지/텍스트로 저장.
    우선순위:
      1) Graphviz → PNG/SVG
      2) Mermaid(.mmd) + (선택) mermaid-cli(mmdc) → PNG
      3) ASCII 콘솔 출력
    """
    os.makedirs("outputs", exist_ok=True)
    gg = app.get_graph()

    # 1) Graphviz 시도
    if fmt in {"png", "svg"}:
        try:
            if fmt == "png":
                out = "outputs/workflow_graph.png"
                gg.draw_png(out)
            else:
                out = "outputs/workflow_graph.svg"
                gg.draw_svg(out)
            print(f"[OK] Graphviz로 저장됨: {out}")
            return
        except Exception as e:
            print(f"[WARN] Graphviz 렌더 실패: {e}")

    # 2) Mermaid 저장 + mmdc 있으면 PNG 렌더
    try:
        mmd = gg.draw_mermaid()
        mmd_path = "outputs/workflow_graph.mmd"
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(mmd)
        print(f"[OK] Mermaid 소스 저장: {mmd_path}")

        if shutil.which("mmdc"):
            png_path = "outputs/workflow_graph_mermaid.png"
            subprocess.run(["mmdc", "-i", mmd_path, "-o", png_path, "-b", "transparent"], check=True)
            print(f"[OK] mmdc로 PNG 저장: {png_path}")
            return
        else:
            print("[INFO] mmdc가 없어 PNG 변환은 생략 (npm i -g @mermaid-js/mermaid-cli)")
    except Exception as e:
        print(f"[WARN] Mermaid 저장 실패: {e}")

    # 3) ASCII 출력
    try:
        print("\n[ASCII]")
        print(gg.draw_ascii())
    except Exception as e:
        print(f"[WARN] ASCII 출력 실패: {e}")

if __name__ == "__main__":
    app = build_app()
    # 실행도 살짝 돌려봄(필수 아님)
    for _ in app.stream({"messages": [], "counter": 0}):
        pass
    save_graph_images(app, fmt="png")  # "svg"로 바꿔도 됨
