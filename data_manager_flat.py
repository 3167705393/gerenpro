"""数据管理模块 - 处理项目数据的增删改查"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# 数据文件路径（扁平结构）
BASE_DIR = Path(__file__).parent
PROJECTS_FILE = BASE_DIR / "projects.json"
SCREENSHOTS_DIR = BASE_DIR / "assets" / "screenshots"
DOCS_DIR = BASE_DIR / "assets" / "docs"
FILES_DIR = BASE_DIR / "assets" / "files"


def _ensure_data_file():
    """确保数据文件存在"""
    if not PROJECTS_FILE.exists():
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        _save_data({"projects": []})


def _load_data() -> dict:
    """加载项目数据"""
    _ensure_data_file()
    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_data(data: dict):
    """保存项目数据"""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_projects() -> list[dict]:
    """获取所有项目"""
    data = _load_data()
    return data.get("projects", [])


def get_project_by_id(project_id: str) -> Optional[dict]:
    """根据ID获取项目"""
    projects = get_all_projects()
    for project in projects:
        if project["id"] == project_id:
            return project
    return None


def add_project(
    name: str,
    description: str = "",
    summary: str = "",
    tech_stack: list[str] = None,
    screenshot_path: str = "",
    screenshot_url: str = "",
    github_url: str = "",
    demo_url: str = "",
    doc_path: str = "",
    files: list[str] = None,
) -> dict:
    """添加新项目"""
    if tech_stack is None:
        tech_stack = []
    if files is None:
        files = []

    project = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "summary": summary,
        "tech_stack": tech_stack,
        "screenshot_path": screenshot_path,
        "screenshot_url": screenshot_url,
        "github_url": github_url,
        "demo_url": demo_url,
        "doc_path": doc_path,
        "files": files,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }

    data = _load_data()
    data["projects"].append(project)
    _save_data(data)

    return project


def update_project(
    project_id: str,
    name: str = None,
    description: str = None,
    summary: str = None,
    tech_stack: list[str] = None,
    screenshot_path: str = None,
    screenshot_url: str = None,
    github_url: str = None,
    demo_url: str = None,
    doc_path: str = None,
    files: list[str] = None,
) -> Optional[dict]:
    """更新项目"""
    data = _load_data()
    projects = data["projects"]

    for i, project in enumerate(projects):
        if project["id"] == project_id:
            if name is not None:
                project["name"] = name
            if description is not None:
                project["description"] = description
            if summary is not None:
                project["summary"] = summary
            if tech_stack is not None:
                project["tech_stack"] = tech_stack
            if screenshot_path is not None:
                project["screenshot_path"] = screenshot_path
            if screenshot_url is not None:
                project["screenshot_url"] = screenshot_url
            if github_url is not None:
                project["github_url"] = github_url
            if demo_url is not None:
                project["demo_url"] = demo_url
            if doc_path is not None:
                project["doc_path"] = doc_path
            if files is not None:
                project["files"] = files
            project["updated_at"] = datetime.now().strftime("%Y-%m-%d")

            data["projects"][i] = project
            _save_data(data)
            return project

    return None


def delete_project(project_id: str) -> bool:
    """删除项目"""
    data = _load_data()
    projects = data["projects"]

    for i, project in enumerate(projects):
        if project["id"] == project_id:
            # 删除关联的截图文件
            if project.get("screenshot_path"):
                screenshot_file = SCREENSHOTS_DIR / Path(project["screenshot_path"]).name
                if screenshot_file.exists():
                    screenshot_file.unlink()

            data["projects"].pop(i)
            _save_data(data)
            return True

    return False


def save_screenshot(uploaded_file, project_id: str) -> str:
    """保存上传的截图"""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    file_ext = Path(uploaded_file.name).suffix or ".png"
    filename = f"{project_id}{file_ext}"
    filepath = SCREENSHOTS_DIR / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return f"assets/screenshots/{filename}"


def is_deployed() -> bool:
    """检测是否为部署模式"""
    import os
    # Streamlit Cloud 会设置这些环境变量
    return os.environ.get("STREAMLIT_SERVER_HEADLESS", "").lower() == "true"


def save_document(uploaded_file, project_id: str) -> str:
    """保存上传的文档"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    file_ext = Path(uploaded_file.name).suffix
    filename = f"{project_id}{file_ext}"
    filepath = DOCS_DIR / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return f"assets/docs/{filename}"


def save_file(uploaded_file, project_id: str) -> str:
    """保存上传的任意文件"""
    FILES_DIR.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    file_ext = Path(uploaded_file.name).suffix
    original_name = Path(uploaded_file.name).stem
    filename = f"{project_id}_{original_name}{file_ext}"
    filepath = FILES_DIR / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return f"assets/files/{filename}"


def read_file_content(file_path: str) -> tuple[str, str]:
    """读取文件内容，返回 (内容, 文件类型)"""
    if not file_path:
        return "", ""

    filepath = BASE_DIR / file_path

    if not filepath.exists():
        return "", ""

    file_ext = Path(file_path).suffix.lower()

    # 判断文件类型
    text_extensions = {
        ".md": "markdown", ".txt": "text", ".json": "json",
        ".html": "html", ".htm": "html", ".css": "css",
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".java": "java", ".go": "go", ".rs": "rust",
        ".cpp": "cpp", ".c": "c", ".h": "header",
        ".xml": "xml", ".yaml": "yaml", ".yml": "yaml",
        ".sql": "sql", ".sh": "shell", ".bat": "batch",
    }

    file_type = text_extensions.get(file_ext, "binary")

    # 尝试读取文本文件
    if file_type != "binary":
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read(), file_type
        except UnicodeDecodeError:
            try:
                with open(filepath, "r", encoding="gbk") as f:
                    return f.read(), file_type
            except:
                pass

    # 二进制文件返回提示
    return f"[二进制文件: {Path(file_path).name}]", "binary"


def get_file_icon(file_ext: str) -> str:
    """根据文件扩展名返回图标"""
    icons = {
        ".md": "📝", ".txt": "📄", ".json": "📋",
        ".html": "🌐", ".htm": "🌐", ".css": "🎨",
        ".py": "🐍", ".js": "⚡", ".ts": "📘",
        ".java": "☕", ".go": "🐹", ".rs": "🦀",
        ".doc": "📘", ".docx": "📘",
        ".xls": "📊", ".xlsx": "📊",
        ".ppt": "📽️", ".pptx": "📽️",
        ".pdf": "📕", ".zip": "📦", ".rar": "📦",
    }
    return icons.get(file_ext.lower(), "📁")