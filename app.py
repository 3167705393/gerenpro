"""项目展示网站首页"""

import streamlit as st
from pathlib import Path
from data_manager import (
    get_all_projects, read_file_content, get_file_icon, is_deployed
)

st.set_page_config(
    page_title="项目作品集",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed" if is_deployed() else "expanded",
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main .block-container {padding-top: 2rem;}
    .page-header {
        text-align: center; padding: 2rem 0 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -2rem -2rem 2rem -2rem; border-radius: 0 0 20px 20px;
    }
    .page-header h1 {color: white; font-size: 2.5rem; margin: 0;}
    .page-header p {color: rgba(255,255,255,0.9); margin-top: 0.5rem;}
    .project-card {
        background: white; border-radius: 16px; overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .project-card:hover {transform: translateY(-5px); box-shadow: 0 12px 40px rgba(102,126,234,0.2);}
    .card-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem; color: white;
    }
    .card-title {font-size: 1.2rem; font-weight: 600; margin: 0 0 0.3rem 0;}
    .card-summary {font-size: 0.9rem; opacity: 0.9; margin: 0;}
    .card-body {padding: 1rem;}
    .tech-tag {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        color: #667eea; padding: 0.2rem 0.6rem; border-radius: 12px;
        font-size: 0.75rem; margin-right: 0.3rem;
    }
    .empty-state {
        text-align: center; padding: 4rem 2rem;
        background: #f8f9ff; border-radius: 20px; margin: 2rem 0;
        border: 2px dashed #667eea40;
    }
    .stats-bar {
        text-align: center; padding: 1rem;
        background: #f8f9ff; border-radius: 12px; margin-bottom: 2rem;
    }
    .stat-number {font-size: 2rem; font-weight: 700; color: #667eea;}
</style>
""", unsafe_allow_html=True)


def render_project_card(project: dict):
    pid = project["id"]
    tech_tags = "".join([f'<span class="tech-tag">{t}</span>' for t in project.get("tech_stack", [])])
    summary = project.get("summary") or project.get("description", "")[:80] or "暂无描述"

    st.markdown(f'''
    <div class="project-card">
        <div class="card-header">
            <h3 class="card-title">{project['name']}</h3>
            <p class="card-summary">{summary}</p>
        </div>
        <div class="card-body">{tech_tags}</div>
    </div>
    ''', unsafe_allow_html=True)

    btns = []
    if project.get("github_url"): btns.append(("🐙 GitHub", project["github_url"], "link"))
    if project.get("demo_url"): btns.append(("🚀 演示", project["demo_url"], "link"))
    if project.get("doc_path"): btns.append((f"{get_file_icon(Path(project['doc_path']).suffix)} 文档", pid, "doc"))

    if btns:
        cols = st.columns(len(btns))
        for i, (label, url, typ) in enumerate(btns):
            with cols[i]:
                if typ == "link":
                    st.link_button(label, url, use_container_width=True)
                else:
                    if st.button(label, key=f"doc_{pid}", use_container_width=True):
                        st.session_state.view_doc = pid


def render_doc_viewer(project: dict):
    st.markdown(f"### 📄 {project['name']}")
    content, ftype = read_file_content(project.get("doc_path", ""))
    ext = Path(project.get("doc_path", "")).suffix.lower()

    if ext == ".md":
        st.markdown(content)
    elif ftype == "html":
        st.components.v1.html(content, height=400, scrolling=True)
    elif ftype != "binary":
        st.code(content, language=ftype)
    else:
        st.info(f"文件: {project.get('doc_path')}")

    if st.button("← 返回", key="back"):
        st.session_state.view_doc = None
        st.rerun()


def main():
    if "view_doc" not in st.session_state:
        st.session_state.view_doc = None

    st.markdown('<div class="page-header"><h1>🎯 项目作品集</h1><p>展示我的创意与代码</p></div>', unsafe_allow_html=True)

    projects = get_all_projects()

    if not projects:
        st.markdown('<div class="empty-state"><h3>📭 还没有项目</h3><p>前往「项目管理」添加项目</p></div>', unsafe_allow_html=True)
        return

    st.markdown(f'<div class="stats-bar"><span class="stat-number">{len(projects)}</span> 个项目</div>', unsafe_allow_html=True)

    # 查看文档
    viewing = next((p for p in projects if p["id"] == st.session_state.view_doc), None)
    if viewing:
        render_doc_viewer(viewing)
        return

    # 项目列表
    for i in range(0, len(projects), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(projects):
                with col:
                    render_project_card(projects[i + j])


if __name__ == "__main__":
    main()