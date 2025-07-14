from dataclasses import dataclass
import re
from base64 import b64decode
import time

import httpx

import config
from enums import ProjectType, PipelineStatus


headers = {"PRIVATE-TOKEN": config.ACCESS_TOKEN}


@dataclass
class GitProject:
    id: int
    type: ProjectType
    ssh_url: str
    created_at: str

    def __hash__(self) -> int:
        return hash((self.id, self.type, self.ssh_url, self.created_at))


@dataclass
class Pipeline:
    id: int
    status: PipelineStatus
    created_at: str
    commit_sha: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": str(self.status),
            "created_at": self.created_at,
            "commit_sha": self.commit_sha,
        }


def get_projects_by_page(per_page: int = 250, page: int = 1) -> list[dict]:
    url = config.API_BASE + "/projects"
    params = {
        "per_page": per_page,
        "page": page,
        "search_namespaces": "true",
        "search": config.PROJECT_TEMPLATE_BASE,
    }
    with httpx.Client(headers=headers) as client:
        response = client.get(url=url, params=params, timeout=20.0)
        response.raise_for_status()
    projects = response.json()
    return projects


def dict_to_git_project(project: dict, project_type: ProjectType) -> GitProject:
    return GitProject(
        id=project["id"],
        type=project_type,
        ssh_url=project["http_url_to_repo"],
        created_at=project["created_at"],
    )


def get_valid_projects(projects: list[dict]) -> list[GitProject]:
    valid_projects = []
    for proj in projects:
        path = proj["path_with_namespace"]
        m = re.fullmatch(config.PROJECTS_REGEX_BASE, path)
        if m is None:
            continue
        project_type = ProjectType(m.group(1))
        valid_projects.append(dict_to_git_project(proj, project_type))
    return valid_projects


def get_projects() -> list[GitProject]:
    page = 1
    projects = []
    temp_projects = get_projects_by_page(page=page)
    while len(temp_projects) > 0:
        projects.extend(get_valid_projects(temp_projects))
        page += 1
        temp_projects = get_projects_by_page(page=page)
    return projects


def get_forks(project: GitProject) -> list[GitProject]:
    url = config.API_BASE + "/projects/" + str(project.id) + "/forks"
    with httpx.Client(headers=headers) as client:
        response = client.get(url=url, timeout=20.0)
        response.raise_for_status()
    projects = response.json()
    projects = [dict_to_git_project(proj, project.type) for proj in projects]
    time.sleep(5)
    return projects


def dict_to_pipeline(pipeline: dict) -> Pipeline:
    return Pipeline(
        id=pipeline["id"],
        status=PipelineStatus(pipeline["status"]),
        created_at=pipeline["created_at"],
        commit_sha=pipeline["sha"],
    )


def get_pipelines(project_id: int) -> list[Pipeline]:
    url = config.API_BASE + "/projects/" + str(project_id) + "/pipelines"
    with httpx.Client(headers=headers) as client:
        response = client.get(url=url, timeout=10.0)
        response.raise_for_status()
    pipelines = response.json()
    return [dict_to_pipeline(pipeline) for pipeline in pipelines]


def find_project_id_by_path_with_namespace(projects: list[dict], path: str) -> int:
    for project in projects:
        if project["path_with_namespace"] != path:
            continue
        return project["id"]
    return projects[0]["id"]


def get_external_project_id(base: str) -> int:
    url = config.API_BASE + "/projects"
    search_param = base.rsplit("/", 1)[1]
    params = {"search": search_param, "simple": "true"}
    with httpx.Client(headers=headers) as client:
        response = client.get(url=url, params=params, timeout=10.0)
        response.raise_for_status()
    project_id = find_project_id_by_path_with_namespace(response.json(), base)
    return project_id


def get_external_readme_content(project_id: int, filepath: str) -> str:
    url = config.API_BASE + "/projects/" + str(project_id) + "/repository/files/" + filepath
    with httpx.Client(headers=headers) as client:
        response = client.get(url=url, timeout=10.0)
        response.raise_for_status()
    content_encoded = response.json()["content"]
    content = b64decode(content_encoded.encode()).decode().strip()
    return content
