"""项目管理页面"""

import streamlit as st
from pathlib import Path
from data_manager import (
    get_all_projects, add_project, update_project,
    delete_project, save_file, save_video, is_deployed
)

st.set_page_config(page_title="项目管理", page_icon="⚙️", layout="wide")


def render_form(project=None):
    is_edit = project is not None

    with st.form("project_form"):
        name = st.text_input("项目名称 *", value=project.get("name", "") if is_edit else "")
        summary = st.text_input("项目简介", value=project.get("summary", "") if is_edit else "", placeholder="一句话介绍项目")
        description = st.text_area("项目描述", value=project.get("description", "") if is_edit else "", height=100, placeholder="详细描述项目功能、特点等")

        # 技术栈改为输入框
        tech_input = st.text_input(
            "技术栈",
            value=", ".join(project.get("tech_stack", [])) if is_edit else "",
            placeholder="例如: Python, React, MySQL（用逗号分隔）"
        )

        st.markdown("---")
        st.markdown("**项目链接**")
        col1, col2 = st.columns(2)
        with col1:
            github_url = st.text_input("GitHub链接", value=project.get("github_url", "") if is_edit else "", placeholder="https://github.com/xxx/xxx")
        with col2:
            demo_url = st.text_input("演示地址", value=project.get("demo_url", "") if is_edit else "", placeholder="https://xxx.com")

        st.markdown("---")
        st.markdown("**项目截图**")
        screenshot_url = st.text_input("截图URL", value=project.get("screenshot_url", "") if is_edit else "", placeholder="图片链接")

        st.markdown("---")
        st.markdown("**操作演示视频**")
        video_url = st.text_input(
            "视频链接（推荐）",
            value=project.get("video_url", "") if is_edit else "",
            placeholder="支持 B站/YouTube/腾讯视频 等嵌入链接或直链"
        )
        st.caption("💡 提示：推荐使用外部视频链接（如B站、对象存储），支持 mp4/webm/mov 格式直链")
        video = st.file_uploader(
            "或上传本地视频（最大 500MB）",
            type=["mp4", "webm", "mov", "avi"],
            help="支持上传大视频文件，建议使用 mp4 格式"
        )

        st.markdown("---")
        st.markdown("**项目文档**")
        doc = st.file_uploader("上传文档（支持 md/txt/py/js/html/json 等）", type=["md", "txt", "py", "js", "html", "htm", "css", "json", "yaml", "yml", "xml", "sql"])

        submitted = st.form_submit_button("✅ 保存" if is_edit else "✅ 添加", type="primary", use_container_width=True)

        # 解析技术栈
        tech_stack = [t.strip() for t in tech_input.split(",") if t.strip()]

        return {
            "submitted": submitted,
            "name": name,
            "summary": summary,
            "description": description,
            "tech_stack": tech_stack,
            "screenshot_url": screenshot_url,
            "github_url": github_url,
            "demo_url": demo_url,
            "video_url": video_url,
            "video": video,
            "doc": doc,
            "is_edit": is_edit,
            "project_id": project.get("id") if is_edit else None,
            "old_doc": project.get("doc_path") if is_edit else "",
            "old_video": project.get("video_path") if is_edit else ""
        }


def handle_submit(data):
    if not data["name"].strip():
        st.error("请输入项目名称")
        return False

    doc_path = data["old_doc"]
    if data["doc"]:
        import uuid
        pid = data["project_id"] or str(uuid.uuid4())
        doc_path = save_file(data["doc"], pid)

    # 处理视频
    video_path = data["old_video"]
    if data["video"]:
        import uuid
        pid = data["project_id"] or str(uuid.uuid4())
        video_path = save_video(data["video"], pid)

    if data["is_edit"]:
        update_project(
            data["project_id"],
            name=data["name"],
            summary=data["summary"],
            description=data["description"],
            tech_stack=data["tech_stack"],
            screenshot_url=data["screenshot_url"],
            github_url=data["github_url"],
            demo_url=data["demo_url"],
            video_url=data["video_url"],
            video_path=video_path,
            doc_path=doc_path
        )
        st.success("已更新！")
    else:
        add_project(
            name=data["name"],
            summary=data["summary"],
            description=data["description"],
            tech_stack=data["tech_stack"],
            screenshot_url=data["screenshot_url"],
            github_url=data["github_url"],
            demo_url=data["demo_url"],
            video_url=data["video_url"],
            video_path=video_path,
            doc_path=doc_path
        )
        st.success("已添加！")
    return True


def render_list():
    projects = get_all_projects()
    if not projects:
        st.info("暂无项目，使用上方表单添加")
        return

    st.subheader("📋 项目列表")
    for p in projects:
        with st.expander(f"**{p['name']}**"):
            c1, c2 = st.columns([3, 1])
            with c1:
                if p.get("summary"): st.write(f"**简介:** {p['summary']}")
                if p.get("tech_stack"): st.write(f"**技术栈:** {' | '.join(p['tech_stack'])}")
                if p.get("github_url"): st.write(f"**GitHub:** {p['github_url']}")
                # 显示视频信息
                if p.get("video_url") or p.get("video_path"):
                    st.write("🎬 **有操作视频**")
                st.caption(f"更新于: {p.get('updated_at', 'N/A')}")
            with c2:
                if st.button("✏️ 编辑", key=f"ed_{p['id']}", use_container_width=True):
                    st.session_state.editing = p
                    st.rerun()
                if st.button("🗑️ 删除", key=f"del_{p['id']}", use_container_width=True):
                    st.session_state.confirm_del = p['id']


def main():
    st.title("⚙️ 项目管理")

    if "editing" not in st.session_state:
        st.session_state.editing = None
    if "confirm_del" not in st.session_state:
        st.session_state.confirm_del = None

    # 删除确认
    if st.session_state.confirm_del:
        p = next((x for x in get_all_projects() if x["id"] == st.session_state.confirm_del), None)
        if p:
            st.warning(f"确定删除「{p['name']}」？")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("确认删除", type="primary", use_container_width=True):
                    delete_project(st.session_state.confirm_del)
                    st.session_state.confirm_del = None
                    st.success("已删除！")
                    st.rerun()
            with c2:
                if st.button("取消", use_container_width=True):
                    st.session_state.confirm_del = None
                    st.rerun()
            return

    # 编辑模式
    if st.session_state.editing:
        st.info(f"编辑: **{st.session_state.editing['name']}**")
        if st.button("← 返回添加模式"):
            st.session_state.editing = None
            st.rerun()

    # 表单
    data = render_form(st.session_state.editing)
    if data["submitted"] and handle_submit(data):
        st.session_state.editing = None
        st.rerun()

    st.markdown("---")
    render_list()


if __name__ == "__main__":
    main()