"""项目展示网站首页"""

import streamlit as st
from pathlib import Path
from services.data_manager import (
    get_all_projects,
    read_file_content,
    get_file_icon,
    is_deployed,
)

# 页面配置
st.set_page_config(
    page_title="项目作品集",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed" if is_deployed() else "expanded",
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 主容器 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 页面标题 */
    .page-header {
        text-align: center;
        padding: 2rem 0 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -2rem -2rem 2rem -2rem;
        border-radius: 0 0 20px 20px;
    }

    .page-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    .page-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* 项目卡片 */
    .project-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
    }

    .project-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }

    .card-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        color: white;
    }

    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }

    .card-summary {
        font-size: 0.95rem;
        opacity: 0.95;
        line-height: 1.5;
        margin: 0;
    }

    .card-description {
        font-size: 0.9rem;
        opacity: 0.85;
        line-height: 1.5;
        margin: 0.5rem 0 0 0;
    }

    .card-body {
        padding: 1.5rem;
    }

    .tech-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .tech-tag {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        color: #667eea;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* 空状态 */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        border-radius: 20px;
        margin: 2rem 0;
        border: 2px dashed #667eea40;
    }

    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .empty-state h3 {
        color: #333;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .empty-state p {
        color: #666;
        font-size: 1rem;
    }

    /* 统计信息 */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 1rem;
        background: #f8f9ff;
        border-radius: 12px;
        margin-bottom: 2rem;
    }

    .stat-item {
        text-align: center;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }

    .stat-label {
        font-size: 0.85rem;
        color: #666;
    }

    /* 文件预览区 */
    .file-preview {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def get_code_language(file_type: str) -> str:
    """根据文件类型返回代码高亮语言"""
    mapping = {
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "java": "java",
        "go": "go",
        "rust": "rust",
        "cpp": "cpp",
        "c": "c",
        "html": "html",
        "css": "css",
        "json": "json",
        "yaml": "yaml",
        "sql": "sql",
        "shell": "bash",
        "markdown": "markdown",
    }
    return mapping.get(file_type, "text")


def render_project_card(project: dict):
    """渲染单个项目卡片"""
    project_id = project["id"]

    # 技术栈标签
    tech_tags = ""
    if project.get("tech_stack"):
        tech_tags = "".join([f'<span class="tech-tag">{tag}</span>' for tag in project["tech_stack"]])

    # 卡片HTML
    summary_text = project.get('summary', '') or project.get('description', '暂无描述')[:100]
    card_html = f'''
    <div class="project-card">
        <div class="card-header">
            <h3 class="card-title">{project['name']}</h3>
            <p class="card-summary">{summary_text}</p>
        </div>
        <div class="card-body">
            {f'<div class="tech-tags">{tech_tags}</div>' if tech_tags else ''}
        </div>
    </div>
    '''

    st.markdown(card_html, unsafe_allow_html=True)

    # 操作按钮
    has_github = bool(project.get("github_url"))
    has_demo = bool(project.get("demo_url"))
    has_doc = bool(project.get("doc_path"))

    btn_cols = st.columns([1, 1, 1] if has_github and has_demo and has_doc else [1] * (has_github + has_demo + has_doc))

    btn_idx = 0
    if has_github:
        with btn_cols[btn_idx]:
            st.link_button("🐙 GitHub", project["github_url"], use_container_width=True)
        btn_idx += 1

    if has_demo:
        with btn_cols[btn_idx]:
            st.link_button("🚀 演示", project["demo_url"], use_container_width=True)
        btn_idx += 1

    if has_doc:
        with btn_cols[btn_idx]:
            file_ext = Path(project.get("doc_path", "")).suffix
            icon = get_file_icon(file_ext)
            if st.button(f"{icon} 查看文档", key=f"view_doc_{project_id}", use_container_width=True):
                st.session_state.viewing_doc = project_id


def render_doc_viewer(project: dict):
    """渲染文档查看器"""
    project_id = project["id"]

    st.markdown("---")
    st.markdown(f"### 📄 {project['name']} - 项目文档")

    doc_path = project.get("doc_path", "")
    file_ext = Path(doc_path).suffix.lower()

    # 读取文件内容
    content, file_type = read_file_content(doc_path)

    if file_type == "binary":
        # 二进制文件，提供下载
        st.warning(f"此文件类型 ({file_ext}) 无法直接预览")
        base_dir = Path(__file__).parent
        filepath = base_dir / doc_path

        if filepath.exists():
            with open(filepath, "rb") as f:
                st.download_button(
                    label="📥 下载文件",
                    data=f,
                    file_name=filepath.name,
                    use_container_width=True,
                )
    elif file_type in ["markdown", "text"]:
        # Markdown 或纯文本
        if file_ext == ".md":
            st.markdown(content)
        else:
            st.text(content)
    elif file_type in ["html"]:
        # HTML 文件
        st.markdown("**HTML 预览:**")
        st.components.v1.html(content, height=400, scrolling=True)
        st.markdown("**源代码:**")
        st.code(content, language="html")
    else:
        # 代码文件
        lang = get_code_language(file_type)
        st.code(content, language=lang)

    if st.button("关闭文档", key=f"close_doc_{project_id}"):
        st.session_state.viewing_doc = None
        st.rerun()


def render_empty_state():
    """渲染空状态"""
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📭</div>
        <h3>还没有任何项目</h3>
        <p>前往「项目管理」页面添加你的第一个项目吧！</p>
    </div>
    """, unsafe_allow_html=True)

    if not is_deployed():
        st.info("💡 点击左侧边栏的「项目管理」开始添加项目")


def main():
    # 初始化session state
    if "viewing_doc" not in st.session_state:
        st.session_state.viewing_doc = None

    # 页面头部
    st.markdown("""
    <div class="page-header">
        <h1>🎯 项目作品集</h1>
        <p>展示我的创意与代码</p>
    </div>
    """, unsafe_allow_html=True)

    # 获取所有项目
    projects = get_all_projects()

    if not projects:
        render_empty_state()
        return

    # 统计信息
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-number">{len(projects)}</div>
            <div class="stat-label">项目总数</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 检查是否正在查看文档
    viewing_project = None
    if st.session_state.viewing_doc:
        viewing_project = next((p for p in projects if p["id"] == st.session_state.viewing_doc), None)

    if viewing_project:
        # 显示文档查看器
        st.markdown(f"**← 返回项目列表**")
        render_project_card(viewing_project)
        render_doc_viewer(viewing_project)
    else:
        # 显示项目卡片网格
        cols_per_row = 2
        for i in range(0, len(projects), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(projects):
                    with col:
                        render_project_card(projects[i + j])


if __name__ == "__main__":
    main()