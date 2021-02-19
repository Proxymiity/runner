[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Proxymiity_runner&metric=alert_status)](https://sonarcloud.io/dashboard?id=Proxymiity_runner)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a72e5751e4aa456a906179d0cb66b02f)](https://www.codacy.com/gh/Proxymiity/runner/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Proxymiity/runner&amp;utm_campaign=Badge_Grade)
# Runner
A simple utility to run GitHub projects locally. Designed for server-use.

What does this do?  
1. Runner reads the `project.json` file. It contains everything it needs to clone and run your code.
2. Runner either clones your project if it does not exist locally, or just refreshes the code in it via a git pull.
3. If `just_update` is enabled, it will 'Just update'. If not, Runner will setup your Python venv if enabled.
4. It will then install any required dependency you specified in the `pip_packages` array.
5. Runner will next run your code. It will display in the console.
6. After running your code, your exit code will be displayed and Runner will close (or repeat if your config file says to).  

Runner can also run programs before cloning, after cloning, before running your code, and after running your code.

Here's a project example:
<!--
    I know that comments in JSON are NOT permitted. But this is an example config.
    Please remove them if you copy that one.
-->
```py
{
  "project": {                      # Simple project description
    "name": "Sample project",
    "desc": "This is a sample project using runner."
  },
  "git": {
    "user": "Proxymiity",           # This builds a GitHub URL:
    "repo": "Alter",                # github.com/Proxymiity/Alter
    "branch": "plugins.moderation", # on the 'plugins.moderation' branch
    "arguments": "--recursive"      # and passes the '--recusrive' flag to git
  },
  "python": {
    "virtualenv": {
      "active": true,               # Enables a virtual environment named 'dvenv'
      "name": "dvenv"
    },
    "pip_packages": ["discord.py"], # Runs 'pip install discord.py --upgrade'
    "executable": "python",         # Specifies the python binary. Leave to 'python' if using venv. Must be in PATH.
    "folder" : "/",                 # This specifies the location of the file to run:
    "target": "alter.py"            # /alter.py
  },                                # (This is relative to your branch. e.g. main/file.py)
  "events": {
    "before_clone": [],             # These events are relative to the parent directory of your repo
    "after_clone" : [],             # This runs '/setup.py' with 'python' and args 'owner 278230133176008704'
    "before_run": ["cd alter && python setup.py owner 278230133176008704"],
    "after_run": []                 # Tip! In this case, the parent directory only have the project.json, runner.py
  },                                # and your project's folder.
  "events": {
    "before_clone": [],             # These events are relative to your branch, too.
    "after_clone" : [],
    "before_pull": [],
    "after_pull" : [],              # For example, this runs /setup.py with python and arg 'owner 278230133176008704'
    "before_run": ["python setup.py owner 278230133176008704"],
    "after_run": []
  },
  "runner": {
    "ignore_root_errors": false,    # Ignores the fact that you are using a non-root user (which can lead to errors)
    "run_indefinitely": true,       # Runs in a loop. Not recommended though
    "run_indefinitely_on_nonzeroEC": false, # Continue looping even if there is a non-zero exit code.
    "sleep_secs_between_runs": 1,   # Number of seconds to wait before restarting your loop. Minimum is 1.
    "delete_before_each_run": false,        # Wipes your repo (in this case '/alter') then clone it again.
    "just_update": false,           # Just updates the repository locally. This will not run any of your code
    "project_folder": "alter"       # The project directory. e.g, in this case, '*/runner/alter'
  }
}
```
Please keep in mind that you *can* enter sensitive information in the `events` section. But you will need to secure your `project.json` file so that no app, no code, or nobody can access it.
