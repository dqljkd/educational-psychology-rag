from __future__ import annotations

from pathlib import Path
from typing import List

import streamlit as st
from dotenv import load_dotenv

from backend.config import AppConfig
from backend.rag_service import RagService


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "data" / "documents"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

EXAMPLE_QUESTIONS = [
    "学生考试前总是失眠怎么办？",
    "家长总是催孩子学习，孩子更焦虑怎么办？",
    "班主任发现学生情绪异常应该怎么做？",
    "学生拖延作业是不是懒？",
    "如何培养学生的学习动机？",
    "怎样做更温和但有效的家校沟通？",
]


def save_uploads(uploaded_files) -> List[Path]:
    saved_paths: List[Path] = []
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for uploaded in uploaded_files:
        destination = DOCS_DIR / uploaded.name
        destination.write_bytes(uploaded.getbuffer())
        saved_paths.append(destination)
    return saved_paths


def build_service() -> RagService:
    load_dotenv(BASE_DIR / ".env")
    config = AppConfig.from_env(BASE_DIR)
    return RagService(config)


def bootstrap_knowledge_base(service: RagService) -> None:
    if st.session_state.get("kb_bootstrapped"):
        return

    try:
        with st.spinner("正在检查并初始化教育心理学知识库..."):
            result = service.bootstrap_processed_knowledge()
        st.session_state.kb_bootstrapped = True
        st.session_state.kb_bootstrap_result = result
    except Exception as exc:
        st.session_state.kb_bootstrap_error = str(exc)


def apply_custom_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(236, 244, 241, 0.95), transparent 34%),
                radial-gradient(circle at top right, rgba(244, 235, 223, 0.9), transparent 30%),
                linear-gradient(180deg, #f7f3ec 0%, #f2f6f2 45%, #eef3f5 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1220px;
        }
        h1, h2, h3 {
            color: #20362f;
            letter-spacing: -0.02em;
        }
        .hero-card, .soft-card, .result-card {
            border-radius: 22px;
            padding: 1.2rem 1.25rem;
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(32, 54, 47, 0.08);
            box-shadow: 0 18px 50px rgba(36, 53, 45, 0.08);
        }
        .hero-card {
            padding: 1.4rem 1.45rem;
            background: linear-gradient(135deg, rgba(255,255,255,0.82), rgba(241,247,243,0.88));
            margin-bottom: 1rem;
        }
        .hero-kicker {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #5f766d;
            margin-bottom: 0.55rem;
            font-weight: 700;
        }
        .hero-title {
            font-size: 2rem;
            line-height: 1.08;
            font-weight: 700;
            color: #20362f;
            margin-bottom: 0.55rem;
        }
        .hero-copy {
            color: #466158;
            font-size: 1rem;
            line-height: 1.7;
        }
        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }
        .pill {
            padding: 0.4rem 0.78rem;
            border-radius: 999px;
            background: rgba(214, 229, 221, 0.8);
            color: #24473a;
            font-size: 0.86rem;
            border: 1px solid rgba(36, 71, 58, 0.08);
        }
        .section-note {
            color: #567168;
            font-size: 0.95rem;
            line-height: 1.65;
        }
        .example-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.65rem;
            margin-top: 0.75rem;
        }
        .example-item {
            padding: 0.8rem 0.9rem;
            border-radius: 16px;
            background: rgba(247, 244, 238, 0.92);
            border: 1px solid rgba(89, 111, 101, 0.08);
            color: #314a41;
            font-size: 0.92rem;
            line-height: 1.5;
        }
        .sidebar-caption {
            color: #5a6f68;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stTextInput"] input {
            border-radius: 16px !important;
            background: rgba(255,255,255,0.88) !important;
        }
        div[data-testid="stExpander"] details {
            border-radius: 18px;
            border: 1px solid rgba(32, 54, 47, 0.08);
            background: rgba(255,255,255,0.72);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Educational Psychology Support</div>
            <div class="hero-title">更温和、更可靠的教育心理学知识检索与支持</div>
            <div class="hero-copy">
                这个系统面向学生、家长和一线教师，优先提供教育心理学视角下的解释、观察框架和可执行建议。
                当问题涉及高风险信号时，系统会明确提醒寻求学校心理老师、监护人或专业机构支持。
            </div>
            <div class="pill-row">
                <div class="pill">学习动机</div>
                <div class="pill">考试焦虑</div>
                <div class="pill">家校沟通</div>
                <div class="pill">课堂支持</div>
                <div class="pill">情绪调节</div>
                <div class="pill">学校心理支持</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_examples() -> None:
    items = "".join([f'<div class="example-item">{question}</div>' for question in EXAMPLE_QUESTIONS])
    st.markdown(
        f"""
        <div class="soft-card">
            <h3 style="margin-top:0;">常见提问方向</h3>
            <div class="section-note">如果你暂时不知道怎么提问，可以从这些典型场景开始。</div>
            <div class="example-grid">{items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="教育心理学 RAG 知识库", layout="wide")
    apply_custom_theme()

    service = build_service()
    bootstrap_knowledge_base(service)

    with st.sidebar:
        st.markdown("## 知识库管理")
        st.markdown(
            '<div class="sidebar-caption">上传新资料，或导入已经清洗完成的教育心理学知识文件。</div>',
            unsafe_allow_html=True,
        )
        uploaded_files = st.file_uploader(
            "上传原始资料",
            type=["txt", "md", "pdf", "jsonl"],
            accept_multiple_files=True,
        )
        if st.button("导入并建立索引", use_container_width=True, type="primary"):
            if not uploaded_files:
                st.warning("请先上传至少一个文件。")
            else:
                paths = save_uploads(uploaded_files)
                result = service.ingest_files(paths)
                st.success(
                    f"已写入 {result['documents']} 个文档，生成 {result['chunks']} 个切片，索引名：{service.config.collection_name}"
                )

        structured_files = sorted(PROCESSED_DIR.glob("*.jsonl"))
        if st.button("导入已清洗知识库", use_container_width=True):
            if not structured_files:
                st.warning("当前 `data/processed/` 下没有可导入的结构化知识文件。")
            else:
                service.reset_collection()
                result = service.ingest_files(structured_files)
                st.success(
                    f"已从结构化文件导入 {result['chunks']} 条知识记录，当前集合：{service.config.collection_name}"
                )

        st.divider()
        st.subheader("系统状态")
        st.code(
            "\n".join(
                [
                    f"Collection: {service.config.collection_name}",
                    f"Vector DB: {service.config.vector_store_dir}",
                    f"Raw Documents: {DOCS_DIR}",
                    f"Structured Data: {PROCESSED_DIR}",
                    f"Top K: {service.config.top_k}",
                    f"Indexed Chunks: {service.collection_count()}",
                ]
            )
        )
        st.caption("建议优先导入已清洗知识库，再补充原始 PDF 作为证据层。")
        if st.session_state.get("kb_bootstrap_result"):
            result = st.session_state["kb_bootstrap_result"]
            if result.get("chunks"):
                st.success(f"知识库已就绪：当前索引 {service.collection_count()} 条记录。")
        if st.session_state.get("kb_bootstrap_error"):
            st.error(f"知识库初始化失败：{st.session_state['kb_bootstrap_error']}")

    left_col, right_col = st.columns([1.8, 1.2], gap="large")

    with left_col:
        render_hero()
        render_examples()
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("问答支持")
        st.markdown(
            '<div class="section-note">你可以直接输入学生、家长或教师遇到的真实情境，系统会结合知识库给出更清晰、温和的回答。</div>',
            unsafe_allow_html=True,
        )
        question = st.text_area(
            "描述你的问题或场景",
            placeholder="例如：学生考试前总是失眠怎么办？",
            height=120,
        )
        top_k = st.slider("检索参考片段数 Top K", min_value=1, max_value=8, value=service.config.top_k)

        if st.button("检索并生成答案", use_container_width=True):
            if not question.strip():
                st.warning("请输入问题。")
            else:
                answer = service.answer_question(question.strip(), top_k=top_k)
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### 回答建议")
                st.markdown(answer["answer"])
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("### 检索证据")
                for idx, item in enumerate(answer["contexts"], start=1):
                    title = f"[{idx}] {item['source']}"
                    if item.get("topic"):
                        title = f"{title} | {item['topic']}"
                    with st.expander(title):
                        st.caption(f"score: {item['score']:.4f}")
                        if item.get("category"):
                            st.caption(f"category: {item['category']}")
                        if item.get("risk_level"):
                            st.caption(f"risk: {item['risk_level']}")
                        st.write(item["content"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("资料检索")
        st.markdown(
            '<div class="section-note">如果你想先看知识库里有哪些相关依据，可以只做检索，不生成最终回答。</div>',
            unsafe_allow_html=True,
        )
        search_query = st.text_input("只检索资料片段", placeholder="输入一个主题词或问题")
        if st.button("执行检索", use_container_width=True):
            if not search_query.strip():
                st.warning("请输入检索词。")
            else:
                results = service.search(search_query.strip(), top_k=top_k)
                for idx, item in enumerate(results, start=1):
                    title = f"[{idx}] {item['source']}"
                    if item.get("topic"):
                        title = f"{title} | {item['topic']}"
                    with st.expander(title):
                        st.caption(f"score: {item['score']:.4f}")
                        if item.get("category"):
                            st.caption(f"category: {item['category']}")
                        st.write(item["content"])
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("原始文档")
        files = sorted(DOCS_DIR.glob("*")) if DOCS_DIR.exists() else []
        if not files:
            st.caption("当前还没有已保存的知识库文档。")
        for file_path in files:
            st.markdown(f"- `{file_path.name}`")
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("结构化知识文件")
        processed_files = sorted(PROCESSED_DIR.glob("*.jsonl")) if PROCESSED_DIR.exists() else []
        if not processed_files:
            st.caption("当前还没有已清洗的结构化知识文件。")
        for file_path in processed_files:
            st.markdown(f"- `{file_path.name}`")
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("项目文档")
        st.markdown(
            "\n".join(
                [
                    "- 评估标准：`docs/evaluation.md`",
                    "- 领域知识说明：`docs/domain_knowledge.md`",
                    "- 架构文档：`docs/architecture.md`",
                    "- 部署文档：`docs/deployment.md`",
                    "- API 文档：`docs/api.md`",
                    "- 评测集模板：`data/eval/golden_set_template.csv`",
                ]
            )
        )
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
