import os
import json
import zipfile
import re

from analysis import ParsedProject

REMOVE_PATTERN = r"^(Author:.*<.*@.*>$|\s*See merge request .*\![0-9]+$)"


def anonymize_commits(project: ParsedProject) -> None:
    commits_logs = project.commits_logs
    cleaned_text = re.sub(REMOVE_PATTERN, "", commits_logs, flags=re.MULTILINE)
    anonymized_logs = "\n".join(line for line in cleaned_text.split("\n") if line.strip())
    project.commits_logs = anonymized_logs


def pack_parsed_project(project: ParsedProject) -> None:
    json_name = f"projects/{project.id}.json"
    arc_name = f"projects/{project.id}.zip"
    anonymize_commits(project)
    with open(json_name, "w") as file:
        json.dump(project.to_dict(), file, indent=4)
    with zipfile.ZipFile(arc_name, "a") as zipf:
        zipf.write(json_name, arcname=os.path.basename(json_name))


def pack_folder() -> None:
    SOURCE_DIR = "projects/"
    with zipfile.ZipFile("result.zip", "w") as zipf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, start=SOURCE_DIR)
                zipf.write(file_path, arc_path)
    os.system("rm -r projects/")
