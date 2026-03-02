"""项目管理页面"""

import streamlit as st
from pathlib import Path
from data_manager import (
    get_all_projects, add_project, update_project,
    delete_project, save_file, is_deployed
)

st.set_page_config(page_title="项目管理", page_icon="⚙️", layout="wide")

# 技术栈选项
TECH_OPTIONS = [
    "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust",
    "React", "Vue", "Angular", "Next.js", "Streamlit",
    "Node.js", "Django", "Flask", "FastAPI",
    "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "Docker", "Kubernetes", "AWS", "Azure",
    "TensorFlow", "PyTorch", "OpenAI"
]


def render_form(project=None):
    is_edit = project is not None

    with st.form("project_form"):
        name = st.text_input("项目名称 *", value=project.get("name", "") if is_edit else "")
        summary = st.text_input("项目简介", value=project.get("summary", "") if is_edit else "")
        description = st.text_area("项目描述", value=project.get("description", "") if is_edit else "", height=80)

        tech = st.multiselect("技术栈", TECH_OPTIONS, default=project.get("tech_stack", []) if is_edit else [])
        custom = st.text_input("自定义技术（逗号分隔）", value="")

        st.markdown("---")
        screenshot_url = st.text_input("截图URL", value=project.get("screenshot_url", "") if is_edit else "")
        github_url = st.text_input("GitHub链接", value=project.get("github_url", "") if is_edit else "")
        demo_url = st.text_input("演示地址", value=project.get("demo_url", "") if is_edit else "")

        st.markdown("---")
        doc = st.file_uploader("上传文档", type=["md", "txt", "py", "js", "html", "json", "yaml"])

        submitted = st.form_submit_button("✅ 保存" if is_edit else "✅ 添加", type="primary", use_container_width=True)

        return {
            "submitted": submitted,
            "name": name,
            "summary": summary,
            "description": description,
            "tech_stack": tech + [t.strip() for t in custom.split(",") if t.strip()],
            "screenshot_url": screenshot_url,
            "github_url": github_url,
            "demo_url": demo_url,
            "doc": doc,
            "is_edit": is_edit,
            "project_id": project.get("id") if is_edit else None,
            "old_doc": project.get("doc_path") if is_edit else ""
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
            doc_path=doc_path
        )
        st.success("已添加！")
    return True


def render_list():
    projects = get_all_projects()
    if not projects:
        st.info("暂无项目")
        return

    for p in projects:
        with st.expander(f"**{p['name']}**"):
            c1, c2 = st.columns([3, 1])
            with c1:
                if p.get("summary"): st.write(f"简介: {p['summary']}")
                if p.get("tech_stack"): st.write(f"技术: {' | '.join(p['tech_stack'])}")
            with c2:
                if st.button("✏️ 编辑", key=f"ed_{p['id']}"):
                    st.session_state.editing = p
                    st.rerun()
                if st.button("🗑️ 删除", key=f"del_{p['id']}"):
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
                if st.button("确认删除", type="primary"):
                    delete_project(st.session_state.confirm_del)
                    st.session_state.confirm_del = None
                    st.success("已删除！")
                    st.rerun()
            with c2:
                if st.button("取消"):
                    st.session_state.confirm_del = None
                    st.rerun()
            return

    # 编辑模式
    if st.session_state.editing:
        st.info(f"编辑: **{st.session_state.editing['name']}**")
        if st.button("← 返回添加"):
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