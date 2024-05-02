#!/usr/bin/python3

import requests
import requests.auth
import argparse
from tabulate import tabulate

server_url = "http://bitbucket.orb.local:7990/rest/api/1.0"

project_name = "FIR"
repos = ["appengine","server"]
target_repo = "monorepo"

parser = argparse.ArgumentParser(description='Get bitbucket permissions')
parser.add_argument('-u', '--username', help='bitbucket username',
                    required=True)
parser.add_argument('-p', '--password', help='bitbucket password',
                    required=True)
args = parser.parse_args()

username = args.username
password = args.password


def print_privileges_matrix():
    try:
        auth = requests.auth.HTTPBasicAuth(username, password)
        for repository in repos:
            request_url = f"{server_url}/projects/{project_name}/repos/{repository}/permissions/users"
            response = requests.get(request_url, auth=auth)
            response_json = response.json()

            users_info = [(user['user']['slug'], repository, user['permission'])
                          for user in response_json['values']]
            headers = ["User", "Repository", "Permissions"]
            print(tabulate(users_info, headers=headers))
            if repos.index(repository) != len(repos) -1:
                print("====================================")

    except requests.exceptions.RequestException as error:
        print(f"Failed to retrieve Bitbucket permissions: {error}")
        exit(1)

def get_maximal_permissions():
    maximal_permissions = {}
    priorities = ["REPO_READ", "REPO_WRITE", "REPO_ADMIN"]

    try:
        auth = requests.auth.HTTPBasicAuth(username, password)

        for repo in repos:
            request_url = f"{server_url}/projects/{project_name}/repos/{repo}/permissions/users"
            response = requests.get(request_url, auth=auth)
            response_json = response.json()

            for user in response_json['values']:
                user_name = user['user']['slug']
                permission = user['permission']

                if user_name in maximal_permissions:
                    if priorities.index(maximal_permissions[user_name]) < priorities.index(permission):
                        maximal_permissions[user_name] = permission
                else:
                    maximal_permissions[user_name] = permission

        return maximal_permissions

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        exit(1)

def set_uset_permissions():
    print("====================================\n")
    print("Выставляем привилегии в новом репозитории\n")
    for user, permission in get_maximal_permissions().items():
        url = f"{server_url}/projects/{project_name}/repos/{target_repo}/permissions/users?name={user}&permission={permission}"
        response = requests.put(url, auth=requests.auth.HTTPBasicAuth(username, password))
        if response.status_code != 204:
            print(f"Невозможно выставить привилегии для {user}. {response.text}")
        else:
            print(f"Выставляем привилегию {permission} для {user}")

print("\nИсходное состояние на сервере\n+++++++++++++++++++++++++++++++++++")
print_privileges_matrix()
print("\nМаксимальные привилегии в разрезе пользователей\n++++++++++++++++++++++++++++++++++++")
print(get_maximal_permissions())
print()

set_uset_permissions()