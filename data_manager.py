"""数据管理模块 - 支持 GitHub API 存储"""

import json
import base64
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import requests

# GitHub 配置
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "3167705393/gerenpro")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
DATA_FILE_PATH = "projects.json"

# 本地路径
BASE_DIR = Path(__file__).parent
SCREENSHOTS_DIR = BASE_DIR / "assets" / "screenshots"
FILES_DIR = BASE_DIR / "assets" / "files"


def is_deployed() -> bool:
    """检测是否为部署模式"""
    return os.environ.get("STREAMLIT_SERVER_HEADLESS", "").lower() == "true"


def _get_github_headers():
    """获取 GitHub API 请求头"""
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }


def _github_upload_file(content: bytes, file_path: str, message: str) -> str:
    """上传文件到 GitHub 仓库"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    encoded_content = base64.b64encode(content).decode()

    # 检查文件是否已存在
    try:
        resp = requests.get(url, headers=_get_github_headers(), params={"ref": GITHUB_BRANCH})
        if resp.status_code == 200:
            sha = resp.json().get("sha")
        else:
            sha = None
    except:
        sha = None

    payload = {
        "message": message,
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    try:
        resp = requests.put(url, headers=_get_github_headers(), json=payload)
        if resp.status_code in [200, 201]:
            return f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{file_path}"
    except:
        pass
    return ""


def _get_file_sha():
    """获取数据文件的 SHA"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE_PATH}"
    params = {"ref": GITHUB_BRANCH}
    try:
        resp = requests.get(url, headers=_get_github_headers(), params=params)
        if resp.status_code == 200:
            return resp.json().get("sha")
    except:
        pass
    return None


def _load_data() -> dict:
    """加载数据"""
    if is_deployed() and GITHUB_TOKEN:
        url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{DATA_FILE_PATH}"
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        return {"projects": []}
    else:
        local_file = BASE_DIR / DATA_FILE_PATH
        if local_file.exists():
            with open(local_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"projects": []}


def _save_data(data: dict):
    """保存数据"""
    if is_deployed() and GITHUB_TOKEN:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE_PATH}"
        content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode()).decode()

        sha = _get_file_sha()
        payload = {
            "message": f"更新项目数据 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": content,
            "branch": GITHUB_BRANCH
        }
        if sha:
            payload["sha"] = sha

        try:
            resp = requests.put(url, headers=_get_github_headers(), json=payload)
            return resp.status_code in [200, 201]
        except:
            return False
    else:
        local_file = BASE_DIR / DATA_FILE_PATH
        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True


def get_all_projects() -> list[dict]:
    """获取所有项目"""
    return _load_data().get("projects", [])


def get_project_by_id(project_id: str) -> Optional[dict]:
    """根据 ID 获取项目"""
    for project in get_all_projects():
        if project.get("id") == project_id:
            return project
    return None


def add_project(name: str, description: str = "", summary: str = "",
                tech_stack: list = None, screenshot_path: str = "",
                screenshot_url: str = "", github_url: str = "",
                demo_url: str = "", doc_path: str = "") -> dict:
    """添加项目"""
    if tech_stack is None:
        tech_stack = []

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
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.now().strftime("%Y-%m-%d")
    }

    data = _load_data()
    data["projects"].append(project)
    _save_data(data)
    return project


def update_project(project_id: str, **kwargs) -> Optional[dict]:
    """更新项目"""
    data = _load_data()
    for i, project in enumerate(data["projects"]):
        if project.get("id") == project_id:
            for key, value in kwargs.items():
                if value is not None:
                    project[key] = value
            project["updated_at"] = datetime.now().strftime("%Y-%m-%d")
            data["projects"][i] = project
            _save_data(data)
            return project
    return None


def delete_project(project_id: str) -> bool:
    """删除项目"""
    data = _load_data()
    for i, project in enumerate(data["projects"]):
        if project.get("id") == project_id:
            data["projects"].pop(i)
            _save_data(data)
            return True
    return False


def save_screenshot(uploaded_file, project_id: str) -> str:
    """保存截图（本地或GitHub）"""
    ext = Path(uploaded_file.name).suffix or ".png"
    content = uploaded_file.read()

    if is_deployed() and GITHUB_TOKEN:
        # 上传到 GitHub
        file_path = f"assets/screenshots/{project_id}{ext}"
        url = _github_upload_file(content, file_path, f"上传截图 {project_id}")
        return url
    else:
        # 本地保存
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{project_id}{ext}"
        filepath = SCREENSHOTS_DIR / filename
        with open(filepath, "wb") as f:
            f.write(content)
        return f"assets/screenshots/{filename}"


def save_file(uploaded_file, project_id: str) -> str:
    """保存文档文件"""
    ext = Path(uploaded_file.name).suffix
    name = Path(uploaded_file.name).stem
    content = uploaded_file.read()

    if is_deployed() and GITHUB_TOKEN:
        # 上传到 GitHub
        file_path = f"assets/files/{project_id}_{name}{ext}"
        url = _github_upload_file(content, file_path, f"上传文档 {name}")
        return url
    else:
        # 本地保存
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{project_id}_{name}{ext}"
        filepath = FILES_DIR / filename
        with open(filepath, "wb") as f:
            f.write(content)
        return f"assets/files/{filename}"


def read_file_content(file_path: str) -> tuple:
    """读取文件内容"""
    if not file_path:
        return "", ""

    # 判断是否为URL
    if file_path.startswith("http"):
        try:
            resp = requests.get(file_path)
            if resp.status_code == 200:
                content = resp.text
                ext = Path(file_path).suffix.lower()
                text_types = {
                    ".md": "markdown", ".txt": "text", ".json": "json",
                    ".html": "html", ".css": "css", ".py": "python",
                    ".js": "javascript", ".yaml": "yaml", ".yml": "yaml"
                }
                return content, text_types.get(ext, "text")
        except:
            pass
        return "", "binary"

    # 本地文件
    filepath = BASE_DIR / file_path
    if not filepath.exists():
        return "", ""

    ext = Path(file_path).suffix.lower()
    text_types = {
        ".md": "markdown", ".txt": "text", ".json": "json",
        ".html": "html", ".htm": "html", ".css": "css",
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".java": "java", ".go": "go", ".yaml": "yaml", ".yml": "yaml",
        ".sql": "sql", ".xml": "xml", ".sh": "shell"
    }

    if ext in text_types:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read(), text_types[ext]
        except:
            pass
    return f"[文件: {Path(file_path).name}]", "binary"


def get_file_icon(file_ext: str) -> str:
    """获取文件图标"""
    icons = {
        ".md": "📝", ".txt": "📄", ".json": "📋",
        ".html": "🌐", ".css": "🎨", ".py": "🐍",
        ".js": "⚡", ".ts": "📘", ".java": "☕",
        ".go": "🐹", ".pdf": "📕", ".doc": "📘",
        ".docx": "📘", ".ppt": "📽️", ".pptx": "📽️",
        ".zip": "📦", ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️"
    }
    return icons.get(file_ext.lower(), "📁")