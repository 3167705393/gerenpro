"""项目展示网站首页"""

import streamlit as st
from pathlib import Path
from data_manager import (
    get_all_projects, read_file_content, get_file_icon, is_deployed
)


def get_video_url(project: dict) -> str:
    """获取视频URL（优先外部链接，其次本地路径）"""
    if project.get("video_url"):
        return project["video_url"]
    if project.get("video_path"):
        # 本地视频
        if project["video_path"].startswith("http"):
            return project["video_path"]
        # 本地文件路径
        from data_manager import BASE_DIR
        local_path = BASE_DIR / project["video_path"]
        if local_path.exists():
            return str(local_path)
    return ""


def has_video(project: dict) -> bool:
    """检查项目是否有视频"""
    return bool(project.get("video_url") or project.get("video_path"))

st.set_page_config(
    page_title="项目作品集",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
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
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 1rem;
        border: 1px solid rgba(0,0,0,0.05); cursor: pointer;
        transition: all 0.3s ease;
    }
    .project-card:hover {transform: translateY(-5px); box-shadow: 0 12px 40px rgba(102,126,234,0.25);}
    .card-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem; color: white;
    }
    .card-title {font-size: 1.2rem; font-weight: 600; margin: 0 0 0.3rem 0;}
    .card-summary {font-size: 0.85rem; opacity: 0.9; margin: 0;}
    .card-body {padding: 1rem;}
    .tech-tag {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        color: #667eea; padding: 0.2rem 0.6rem; border-radius: 12px;
        font-size: 0.75rem; margin-right: 0.3rem; display: inline-block; margin-bottom: 0.2rem;
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

    /* 弹窗样式 */
    .modal-overlay {
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.5); z-index: 1000;
        display: flex; align-items: center; justify-content: center;
    }
    .modal-content {
        background: white; border-radius: 16px; padding: 2rem;
        max-width: 800px; width: 90%; max-height: 80vh;
        overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .modal-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -2rem -2rem 1.5rem -2rem; padding: 1.5rem 2rem;
        border-radius: 16px 16px 0 0; color: white;
    }
    .modal-title {font-size: 1.5rem; font-weight: 600; margin: 0;}
    .modal-summary {opacity: 0.9; margin-top: 0.5rem;}
</style>
""", unsafe_allow_html=True)


def render_project_card(project: dict):
    """渲染项目卡片"""
    pid = project["id"]
    tech_tags = "".join([f'<span class="tech-tag">{t}</span>' for t in project.get("tech_stack", [])])
    summary = project.get("summary") or project.get("description", "")[:80] or "暂无描述"

    # 视频标记
    video_badge = '<span style="background:#ff6b6b;color:white;padding:2px 8px;border-radius:10px;font-size:0.7rem;margin-left:8px;">🎬 有视频</span>' if has_video(project) else ''

    st.markdown(f'''
    <div class="project-card">
        <div class="card-header">
            <h3 class="card-title">{project['name']}{video_badge}</h3>
            <p class="card-summary">{summary}</p>
        </div>
        <div class="card-body">{tech_tags}</div>
    </div>
    ''', unsafe_allow_html=True)

    # 点击查看详情按钮
    if st.button("📖 查看详情", key=f"view_{pid}", use_container_width=True):
        st.session_state.view_project = pid


def render_project_detail(project: dict):
    """渲染项目详情弹窗"""
    st.markdown("----")

    # 标题区域
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
        <h2 style="margin:0; color:white;">{project['name']}</h2>
        <p style="margin:0.5rem 0 0 0; opacity:0.9;">{project.get('summary', '') or project.get('description', '')[:100]}</p>
    </div>
    """, unsafe_allow_html=True)

    # 关闭按钮
    if st.button("← 返回列表", key="close_detail"):
        st.session_state.view_project = None
        st.rerun()

    # 操作演示视频（优先显示）
    video_url = get_video_url(project)
    if video_url:
        st.markdown("**🎬 操作演示视频**")
        # 判断是否为本地文件
        if video_url.startswith("http"):
            # 外部链接 - 尝试直接播放或显示链接
            video_ext = Path(video_url).suffix.lower()
            if video_ext in [".mp4", ".webm", ".mov", ".avi"]:
                st.video(video_url)
            else:
                # 非直链视频，显示链接按钮
                st.info("📺 此视频需要外部播放器")
                st.link_button("▶️ 打开视频", video_url, use_container_width=True)
        else:
            # 本地文件
            st.video(video_url)
        st.markdown("")

    # 截图
    if project.get("screenshot_url"):
        st.markdown("**📷 项目截图**")
        st.image(project["screenshot_url"], use_container_width=True)
        st.markdown("")

    # 基本信息
    col1, col2 = st.columns(2)
    with col1:
        if project.get("tech_stack"):
            st.markdown("**🛠️ 技术栈**")
            tags = " ".join([f"`{t}`" for t in project["tech_stack"]])
            st.markdown(tags)
    with col2:
        st.markdown("**📅 时间**")
        st.write(f"创建: {project.get('created_at', 'N/A')}")
        st.write(f"更新: {project.get('updated_at', 'N/A')}")

    # 描述
    if project.get("description"):
        st.markdown("**📝 项目描述**")
        st.write(project["description"])

    # 链接
    if project.get("github_url") or project.get("demo_url"):
        st.markdown("**🔗 相关链接**")
        cols = st.columns([1, 1])
        if project.get("github_url"):
            with cols[0]:
                st.link_button("🐙 GitHub 仓库", project["github_url"], use_container_width=True)
        if project.get("demo_url"):
            with cols[1]:
                st.link_button("🚀 在线演示", project["demo_url"], use_container_width=True)

    # 文档
    if project.get("doc_path"):
        st.markdown("---")
        st.markdown("**📄 项目文档**")
        content, ftype = read_file_content(project.get("doc_path", ""))
        ext = Path(project.get("doc_path", "")).suffix.lower()

        if ext == ".md":
            st.markdown(content)
        elif ftype == "html":
            st.components.v1.html(content, height=400, scrolling=True)
        elif ftype != "binary":
            st.code(content, language=ftype)
        else:
            st.info(f"文档: {project.get('doc_path')}")


def main():
    if "view_project" not in st.session_state:
        st.session_state.view_project = None

    # 页面头部
    st.markdown('<div class="page-header"><h1>🎯 项目作品集</h1><p>展示我的创意与代码</p></div>', unsafe_allow_html=True)

    # 项目管理入口
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("⚙️ 项目管理", type="primary", use_container_width=True):
            st.switch_page("pages/1_项目管理.py")

    projects = get_all_projects()

    if not projects:
        st.markdown('<div class="empty-state"><h3>📭 还没有项目</h3><p>前往「项目管理」添加项目</p></div>', unsafe_allow_html=True)
        return

    # 统计
    st.markdown(f'<div class="stats-bar"><span class="stat-number">{len(projects)}</span> 个项目</div>', unsafe_allow_html=True)

    # 查看详情模式
    if st.session_state.view_project:
        viewing = next((p for p in projects if p["id"] == st.session_state.view_project), None)
        if viewing:
            render_project_detail(viewing)
            return

    # 项目卡片列表
    for i in range(0, len(projects), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(projects):
                with col:
                    render_project_card(projects[i + j])


if __name__ == "__main__":
    main()