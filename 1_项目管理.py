"""项目管理页面 - 添加/编辑/删除项目"""

import streamlit as st
from services.data_manager import (
    get_all_projects,
    add_project,
    update_project,
    delete_project,
    save_screenshot,
    save_file,
    is_deployed,
)

# 页面配置
st.set_page_config(
    page_title="项目管理",
    page_icon="⚙️",
    layout="wide",
)

# 部署模式下隐藏此页面
if is_deployed():
    st.warning("⚠️ 此页面在部署模式下不可用")
    st.stop()


# 常用技术栈选项
TECH_STACK_OPTIONS = [
    "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust",
    "React", "Vue", "Angular", "Next.js", "Streamlit",
    "Node.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "TensorFlow", "PyTorch", "OpenAI", "LangChain",
]

# 支持的文件类型
SUPPORTED_FILE_TYPES = [
    "md", "txt", "json", "html", "htm", "css",
    "py", "js", "ts", "java", "go", "rs", "c", "cpp", "h",
    "xml", "yaml", "yml", "sql", "sh", "bat",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf",
    "zip", "rar", "7z",
]


def render_project_form(project: dict = None):
    """渲染项目表单"""
    is_edit = project is not None

    with st.form("project_form", clear_on_submit=not is_edit):
        # === 基本信息 ===
        st.markdown("### 📋 基本信息")

        # 项目名称
        name = st.text_input(
            "项目名称 *",
            value=project.get("name", "") if is_edit else "",
            placeholder="输入项目名称",
        )

        # 项目简介（新增）
        summary = st.text_area(
            "项目简介",
            value=project.get("summary", "") if is_edit else "",
            placeholder="一句话介绍你的项目（可选）",
            height=60,
            max_chars=200,
        )

        # 项目描述
        description = st.text_area(
            "项目描述",
            value=project.get("description", "") if is_edit else "",
            placeholder="详细描述你的项目功能、特点等",
            height=100,
        )

        # === 技术栈 ===
        st.markdown("---")
        st.markdown("### 🛠️ 技术栈")

        # 预设技术栈选择
        existing_tech = project.get("tech_stack", []) if is_edit else []
        tech_stack = st.multiselect(
            "选择常用技术",
            options=TECH_STACK_OPTIONS,
            default=existing_tech,
            help="从列表中选择技术栈",
        )

        # 自定义技术栈输入
        custom_tech = st.text_input(
            "自定义技术栈（用逗号分隔）",
            value=", ".join([t for t in existing_tech if t not in TECH_STACK_OPTIONS]) if is_edit else "",
            placeholder="例如: Solidity, Web3, TailwindCSS",
            help="输入列表中没有的技术，用逗号分隔",
        )

        # === 项目截图 ===
        st.markdown("---")
        st.markdown("### 🖼️ 项目截图")

        # 初始化默认值
        default_screenshot_index = 0
        if is_edit:
            if project.get("screenshot_url"):
                default_screenshot_index = 2
            elif project.get("screenshot_path"):
                default_screenshot_index = 1

        screenshot_mode = st.radio(
            "截图来源",
            options=["不上传", "上传图片", "图片URL"],
            index=default_screenshot_index,
            horizontal=True,
        )

        screenshot_path = ""
        screenshot_url = project.get("screenshot_url", "") if is_edit else ""

        if screenshot_mode == "上传图片":
            st.info("👇 点击下方区域选择图片文件")
            uploaded_screenshot = st.file_uploader(
                "选择截图文件",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                help="支持 PNG, JPG, GIF, WEBP 格式",
            )
        elif screenshot_mode == "图片URL":
            uploaded_screenshot = None
            screenshot_url = st.text_input(
                "输入图片URL",
                value=screenshot_url,
                placeholder="https://example.com/screenshot.png",
            )
        else:
            uploaded_screenshot = None

        # === 项目文档/文件 ===
        st.markdown("---")
        st.markdown("### 📎 项目文件")
        st.caption("支持多种格式：代码文件(.py/.js等)、文档(.md/.txt/.docx等)、演示(.pptx)等")

        # 初始化默认值
        default_doc_index = 0
        if is_edit and project.get("doc_path"):
            default_doc_index = 1

        doc_mode = st.radio(
            "文档来源",
            options=["不上传", "上传文件"],
            index=default_doc_index,
            horizontal=True,
        )

        uploaded_doc = None
        if doc_mode == "上传文件":
            st.info("👇 点击下方区域选择文件")
            uploaded_doc = st.file_uploader(
                "选择文档文件",
                type=SUPPORTED_FILE_TYPES,
                help="支持代码、文档、演示等多种格式",
            )

        # 已有文件显示
        if is_edit and project.get("doc_path"):
            st.success(f"已上传: {project['doc_path']}")

        # === 项目链接 ===
        st.markdown("---")
        st.markdown("### 🔗 项目链接（可选）")

        col1, col2 = st.columns(2)
        with col1:
            github_url = st.text_input(
                "GitHub 链接",
                value=project.get("github_url", "") if is_edit else "",
                placeholder="https://github.com/username/repo",
            )
        with col2:
            demo_url = st.text_input(
                "演示地址",
                value=project.get("demo_url", "") if is_edit else "",
                placeholder="https://your-demo.com",
            )

        # === 提交按钮 ===
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            submit_label = "✅ 更新项目" if is_edit else "✅ 添加项目"
            submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)
        with col2:
            if is_edit:
                if st.form_submit_button("取消", use_container_width=True):
                    st.session_state.editing_project = None
                    st.rerun()

        return {
            "submitted": submitted,
            "name": name,
            "description": description,
            "summary": summary,
            "tech_stack": tech_stack,
            "custom_tech": custom_tech,
            "screenshot_mode": screenshot_mode,
            "uploaded_screenshot": uploaded_screenshot if screenshot_mode == "上传图片" else None,
            "screenshot_url": screenshot_url,
            "doc_mode": doc_mode,
            "uploaded_doc": uploaded_doc,
            "github_url": github_url,
            "demo_url": demo_url,
            "is_edit": is_edit,
            "project_id": project.get("id") if is_edit else None,
            "existing_doc_path": project.get("doc_path", "") if is_edit else "",
        }


def handle_form_submit(form_data: dict):
    """处理表单提交"""
    if not form_data["name"].strip():
        st.error("请输入项目名称")
        return False

    # 合并技术栈
    tech_stack = form_data["tech_stack"].copy()
    if form_data["custom_tech"]:
        custom_tags = [t.strip() for t in form_data["custom_tech"].split(",") if t.strip()]
        tech_stack.extend(custom_tags)
    # 去重
    tech_stack = list(dict.fromkeys(tech_stack))

    # 处理截图
    screenshot_path = ""
    screenshot_url = form_data["screenshot_url"]

    if form_data["uploaded_screenshot"]:
        import uuid
        temp_id = form_data["project_id"] or str(uuid.uuid4())
        screenshot_path = save_screenshot(form_data["uploaded_screenshot"], temp_id)

    # 处理文档
    doc_path = form_data["existing_doc_path"]
    if form_data["uploaded_doc"]:
        import uuid
        temp_id = form_data["project_id"] or str(uuid.uuid4())
        doc_path = save_file(form_data["uploaded_doc"], temp_id)

    if form_data["is_edit"]:
        update_project(
            form_data["project_id"],
            name=form_data["name"],
            description=form_data["description"],
            summary=form_data["summary"],
            tech_stack=tech_stack,
            screenshot_path=screenshot_path if screenshot_path else None,
            screenshot_url=screenshot_url if screenshot_url else None,
            github_url=form_data["github_url"],
            demo_url=form_data["demo_url"],
            doc_path=doc_path if doc_path else None,
        )
        st.success("项目已更新！")
    else:
        add_project(
            name=form_data["name"],
            description=form_data["description"],
            summary=form_data["summary"],
            tech_stack=tech_stack,
            screenshot_path=screenshot_path,
            screenshot_url=screenshot_url,
            github_url=form_data["github_url"],
            demo_url=form_data["demo_url"],
            doc_path=doc_path,
        )
        st.success("项目已添加！")

    return True


def render_project_list():
    """渲染项目列表"""
    projects = get_all_projects()

    if not projects:
        st.info("还没有任何项目，使用上方表单添加第一个项目吧！")
        return

    st.subheader("📋 已有项目")

    for project in projects:
        with st.expander(f"**{project['name']}**", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                if project.get("summary"):
                    st.markdown(f"**简介:** {project['summary']}")
                if project.get("description"):
                    st.markdown(f"**描述:** {project['description'][:100]}..." if len(project.get('description', '')) > 100 else f"**描述:** {project['description']}")
                if project.get("tech_stack"):
                    st.markdown(f"**技术栈:** {' | '.join(project['tech_stack'])}")
                if project.get("doc_path"):
                    st.markdown(f"**文档:** {project['doc_path']}")
                if project.get("github_url"):
                    st.markdown(f"**GitHub:** [{project['github_url']}]({project['github_url']})")
                if project.get("demo_url"):
                    st.markdown(f"**演示:** [{project['demo_url']}]({project['demo_url']})")
                st.caption(f"创建于: {project.get('created_at', 'N/A')} | 更新于: {project.get('updated_at', 'N/A')}")

            with col2:
                if st.button("✏️ 编辑", key=f"edit_{project['id']}", use_container_width=True):
                    st.session_state.editing_project = project
                    st.rerun()
                if st.button("🗑️ 删除", key=f"delete_{project['id']}", use_container_width=True):
                    st.session_state.confirm_delete = project['id']


def confirm_delete_dialog():
    """删除确认对话框"""
    if "confirm_delete" in st.session_state and st.session_state.confirm_delete:
        project_id = st.session_state.confirm_delete
        project = next((p for p in get_all_projects() if p["id"] == project_id), None)

        if project:
            st.warning(f"确定要删除项目「{project['name']}」吗？此操作不可撤销。")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("确认删除", type="primary", use_container_width=True):
                    delete_project(project_id)
                    st.session_state.confirm_delete = None
                    st.success("项目已删除！")
                    st.rerun()
            with col2:
                if st.button("取消", use_container_width=True):
                    st.session_state.confirm_delete = None
                    st.rerun()


def main():
    st.title("⚙️ 项目管理")

    # 初始化session state
    if "editing_project" not in st.session_state:
        st.session_state.editing_project = None
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = None

    # 显示正在编辑的项目
    if st.session_state.editing_project:
        st.info(f"正在编辑: **{st.session_state.editing_project['name']}**")
        if st.button("← 返回添加模式"):
            st.session_state.editing_project = None
            st.rerun()

    # 表单区域
    st.subheader("📝 " + ("编辑项目" if st.session_state.editing_project else "添加项目"))
    form_data = render_project_form(st.session_state.editing_project)

    if form_data["submitted"]:
        if handle_form_submit(form_data):
            st.session_state.editing_project = None
            st.rerun()

    st.markdown("---")
    render_project_list()
    confirm_delete_dialog()


if __name__ == "__main__":
    main()