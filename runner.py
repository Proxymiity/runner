import json
import os
from pathlib import Path
import shutil
import ctypes
import platform
import time
import subprocess

try:
    __version__ = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
except subprocess.CalledProcessError:
    __version__ = "Unknown - LKC f5f72d"

print("Proxymiity/runner - Version " + __version__)
print("Licensed under the Apache 2 License")

try:
    perms = os.getuid() == 0
except AttributeError:
    perms = ctypes.windll.shell32.IsUserAnAdmin() != 0

print("Opening project.json file")
with open("project.json", encoding="utf-8", mode="r") as f:
    project = json.load(f)

print("Project: " + project["project"]["name"])
print("         " + project["project"]["desc"])

if perms is False:
    if project["runner"]["ignore_root_errors"] is True:
        print("Not using root privileges. Proceed carefully.")
    else:
        print("Error: You are not using root/admin privileges. Please consider running this as administrator to avoid"
              " an issue while deleting files. If you are AWARE of this and want to continue, please set"
              " ignore_root_errors to true in the project.json.")
        exit(-99)

p_base = Path(os.getcwd())
p_folder = Path(str(p_base) + "/" + project["runner"]["project_folder"])
p_runner = Path(str(p_folder) + project["python"]["folder"])
p_executable = Path(str(p_runner) + "/" + project["python"]["target"])
p_url = "https://github.com/" + project["git"]["user"] + "/" + project["git"]["repo"]


def event(name: str):
    print("Processing event " + name)
    ev_cwd = os.getcwd()
    if p_runner.exists() and p_runner.is_dir():
        os.chdir(str(p_folder))
    for y in project["events"][name]:
        print(y)
        os.system(y)
    os.chdir(ev_cwd)


while True:
    if project["runner"]["delete_before_each_run"] is True:
        if p_folder.exists():
            print("Removing and cloning project...")
            shutil.rmtree(project["runner"]["project_folder"])
        event("before_clone")
        os.system("git clone " + p_url + " " + project["runner"]["project_folder"] + " " +
                  project["git"]["arguments"])
        event("after_clone")
    else:
        if not p_folder.exists():
            print("Cloning project...")
            event("before_clone")
            os.system("git clone " + p_url + " " + project["runner"]["project_folder"] + " " +
                      project["git"]["arguments"])
            event("after_clone")

    event("before_pull")
    os.system("cd " + project["runner"]["project_folder"] + " && git stash && git checkout " +
              project["git"]["branch"] + " && git pull")
    event("after_pull")

    if project["python"]["virtualenv"]["active"] is True:
        os.system("cd " + project["runner"]["project_folder"] + " && " + project["python"]["executable"] + " -m venv " +
                  project["python"]["virtualenv"]["name"])
        if platform.system() == "Windows":
            p_vp = project["runner"]["project_folder"] + "\\" + \
                   project["python"]["virtualenv"]["name"] + "\\Scripts\\python.exe"
            p_ep = project["python"]["virtualenv"]["name"] + "\\Scripts\\python.exe"
            os.system(p_vp + " -m pip install pip setuptools --upgrade")
        else:
            p_vp = project["runner"]["project_folder"] + "/" + project["python"]["virtualenv"]["name"] + "/bin/python"
            p_ep = project["python"]["virtualenv"]["name"] + "/bin/python"
            os.system(p_vp + " -m pip install pip setuptools --upgrade")
    else:
        p_vp = project["python"]["executable"]
        p_ep = project["python"]["executable"]

    for x in project["python"]["pip_packages"]:
        os.system(p_vp + " -m pip install " + x + " --upgrade")

    if project["runner"]["just_update"]:
        print("Done. 'Just' updated the repository.")
        exit(0)

    event("before_run")

    os.chdir(p_runner)
    print("Running " + str(p_executable))
    print("")
    target_run = os.system(p_ep + " " + str(p_executable))
    print("")
    print("Process exit code is {}".format(target_run))
    os.chdir(p_folder)

    event("after_run")

    if project["runner"]["run_indefinitely"] is False:
        print("Done. Program ran one time.")
        exit(0)

    if project["runner"]["run_indefinitely_on_nonzeroEC"] is False and target_run != 0:
        print("Done with errors.")
        exit(-1)

    time.sleep(project["runner"]["sleep_secs_between_runs"])
