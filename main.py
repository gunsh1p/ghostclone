import logging
import sys
import time

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
        time.sleep(10)
    del projects
    total_forks_count = sum(len(v) for v in forks.values())
    logging.info(f"Recieved {total_forks_count} forks")

    parsed_projects = []

    for task_proj, proj_forks in forks.items():
        tech_task = get_tech_task(task_proj)
        temp_parsed_projects: list[ParsedProject] = [
            get_parsed_project(proj_fork, tech_task) for proj_fork in proj_forks
        ]
        parsed_projects.extend(temp_parsed_projects)
    for parsed_proj in parsed_projects:
        pack_parsed_project(parsed_proj)
    pack_folder()


if __name__ == "__main__":
    main()
