import getopt
import json
import sys

import requests as req

CMD_HELP = 'ensure_project.py -p <project.json>'


def project_exists_in_cdb(project_data, projects):
    exists = False
    for project in projects:
        if project["name"] == project_data["name"]:
            exists = True
    return exists


def get_project_list_from_cdb(projects_url):
    resp = req.get(projects_url)
    # If the response was successful, no Exception will be raised
    resp.raise_for_status()
    print(resp.text)
    projects = resp.json()
    return projects


def get_project_from_cdb(project_url):
    resp = req.get(project_url)
    # If the response was successful, no Exception will be raised
    resp.raise_for_status()
    print(resp.text)
    project = resp.json()
    return project


def load_project_configuration(json_data_file):
    project_data = json.load(json_data_file)
    return project_data


def create_artifact(host, project_config_file, sha256, filename, description, git_commit, commit_url, build_url,
                    is_compliant):
    project_data = load_project_configuration(project_config_file)

    '''
    curl -H 'Content-Type: application/json' \
     -X PUT \
     -d '{"sha256": "'"$3"'", "filename": "'"$4"'", "description": "'"$5"'", "git_commit": "'"$6"'", "commit_url": "'"$7"'", "build_url": "'"$8"'", "is_compliant": "true"}' \
    http://server:8001/api/v1/projects/$1/$2/artifacts/
    '''

    create_artifact_payload = {
        "sha256": sha256,
        "filename": filename,
        "description": description,
        "git_commit": git_commit,
        "commit_url": commit_url,
        "build_url": build_url,
        "is_compliant": is_compliant
    }
    url = url_for_artifacts(host, project_data)
    put_payload(create_artifact_payload, url)


def put_payload(payload, url):
    headers = {"Content-Type": "application/json"}
    print("Putting this payload:")
    print(json.dumps(payload, sort_keys=True, indent=4))
    print("To url: " + url)
    resp = req.put(url, data=json.dumps(payload), headers=headers)
    print(resp.text)


def url_for_artifacts(host, project_data):
    return url_for_project(host, project_data) + project_data["name"] + '/artifacts/'


def add_evidence(host, project_file_contents, sha256_digest, evidence):
    project_data = load_project_configuration(project_file_contents)
    url_for_artifact = url_for_artifacts(host, project_data) + sha256_digest

    put_payload(evidence, url_for_artifact)


def url_for_project(host, project_data):
    return host + '/api/v1/projects/' + project_data["owner"] + '/'


def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring


def parse_cmd_line():
    project_file = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:", ["project="])
    except getopt.GetoptError:
        print(CMD_HELP)
        sys.exit(2)
    for opt, arg in opts:
        print(opt + ": " + arg)
        if opt == '-h':
            print(CMD_HELP)
            sys.exit()
        elif opt in ("-p", "--project"):
            project_file = arg
    return project_file