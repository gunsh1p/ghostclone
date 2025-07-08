import os
import subprocess
from dataclasses import dataclass
import re
from urllib.parse import quote_plus
import zipfile

from gitlab import (
    GitProject,
    Pipeline,
    get_pipelines,
    get_external_project_id,
    get_external_readme_content,
)
import config


@dataclass
class ParsedProject:
    id: int
    tech_task: str
    commits_logs: str
    pipelines: list[Pipeline]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tech_task": self.tech_task,
            "commits_logs": self.commits_logs,
            "pipelines": [pipeline.to_dict() for pipeline in self.pipelines],
        }


def clone_repo(ssh_url: str) -> None:
    cmd = f"git clone {ssh_url} tmp".split()
    subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def get_all_branches() -> list[str]:
    cmd = "git branch -a".split()
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="tmp/")
    stdout = process.stdout.decode()
    return [branch.strip() for branch in stdout.split("\n") if len(branch) != 0]


def get_remote_branches(all_branches: list[str]) -> list[str]:
    remote_branches = [
        branch
        for branch in all_branches
        if branch.startswith("remote") and "/HEAD" not in branch and "/ci" not in branch
    ]
    return [branch.rsplit("/", 1)[1] for branch in remote_branches]


def get_last_commit_date_in_branch(branch: str) -> int:
    cmd = f"git checkout {branch}".split()
    subprocess.call(cmd, cwd="tmp/", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd = "git log -1 --format=%at".split()
    date = subprocess.run(
        cmd, cwd="tmp/", stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout.decode()
    return int(date.strip())


def find_dev_repo() -> str:
    all_branches = get_all_branches()
    branches = get_remote_branches(all_branches)
    max_date, dev_branch = 0, branches[0]
    for branch in branches:
        date = get_last_commit_date_in_branch(branch)
        if date <= max_date:
            continue
        max_date, dev_branch = date, branch
    return dev_branch


def fetch_commits_logs(branch: str) -> str:
    cmd = f"git checkout {branch}".split()
    subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="tmp/")
    cmd = "git log -p".split()
    output = subprocess.run(cmd, stdout=subprocess.PIPE, cwd="tmp/").stdout.decode()
    output = output.strip()
    return output


def get_external_project_id_with_filepath(url: str) -> tuple[int, str]:
    base, filepath = url.split("/-/blob/", 1)
    base = base.replace("https://", "").replace("http://", "")
    base = base.split("/", 1)[1]
    project_id = get_external_project_id(base)
    filepath = filepath.rsplit("?", 1)[0]
    branch, filepath = filepath.split("/", 1)
    filepath = quote_plus(filepath) + "?ref=" + branch
    return (project_id, filepath)


def get_external_readme(url: str) -> str:
    project_id, filepath = get_external_project_id_with_filepath(url)
    return get_external_readme_content(project_id, filepath)


def get_final_readme(content: str) -> str:
    urls = re.findall(config.TECH_TASKS_REGEX_BASE, content)
    if len(urls) == 0:
        return content
    return get_external_readme(urls[0])


def get_readme() -> str:
    with open("tmp/README.md", "r") as file:
        content = file.read()
    readme = get_final_readme(content)
    return readme


def get_tech_task(project: GitProject) -> str:
    clone_repo(project.ssh_url)
    readme = get_readme()
    delete_repo()
    return readme


def create_zip_exclude_git(source_dir, zipf: zipfile.ZipFile) -> None:
    for root, dirs, files in os.walk(source_dir):
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            file_path = os.path.join(root, file)
            arc_path = os.path.relpath(file_path, start=source_dir)
            zipf.write(file_path, arc_path)


def zip_repisitory(project_id: int) -> None:
    arc_name = f"projects/{project_id}.zip"
    os.system("mkdir -p projects")
    with zipfile.ZipFile(arc_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        create_zip_exclude_git("tmp/", zipf)


def delete_repo() -> None:
    os.system("rm -rf tmp/")


def get_parsed_project(project: GitProject, tech_task: str) -> ParsedProject:
    clone_repo(project.ssh_url)
    branch = find_dev_repo()
    commits_logs = fetch_commits_logs(branch)
    pipelines = get_pipelines(project.id)
    zip_repisitory(project.id)
    delete_repo()
    return ParsedProject(
        id=project.id, tech_task=tech_task, commits_logs=commits_logs, pipelines=pipelines
    )
