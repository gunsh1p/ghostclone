import logging
import sys

from gitlab import get_projects, get_forks
from analysis import get_parsed_project, get_tech_task, ParsedProject
from packer import pack_parsed_project, pack_folder

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    projects = get_projects()
    logging.info(f"Recieved {len(projects)} projects")

    forks = {}

    for proj in projects:
        temp_forks = get_forks(proj)
        forks[proj] = temp_forks
    del projects
    total_forks_count = sum(len(v) for v in forks.values())
    logging.info(f"Recieved {total_forks_count} forks")

    parsed_projects: list[ParsedProject] = []

    for task_proj, proj_forks in forks.items():
        tech_task = get_tech_task(task_proj)
        for proj_fork in proj_forks:
            parsed_proj = get_parsed_project(proj_fork, tech_task)
            if parsed_proj is None:
                continue
            parsed_projects.append(parsed_proj)
    for parsed_proj in parsed_projects:
        pack_parsed_project(parsed_proj)
    pack_folder()


if __name__ == "__main__":
    main()
