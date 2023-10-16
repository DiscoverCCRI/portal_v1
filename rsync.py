from subprocess import run

USER = 'portal'
HOST = 'ccrissde1.iot.nau.edu'


"""
This function will rsync over all the experimental data from the portal to the
intermediate server. Currently, this code is configured for the the Fall 2023
NSF Demo. As such, it uses a fixed username and hostname, and uses SSH to tell
the server to clone a given GitHub repo. Eventually, it will use rsync to copy
data from one location to another, and the host may change from one experiment
to the next. For this to work, the given user's ssh key must be uploaded to
the host.

Parameters
----------
github_link : str
    The link to a GitHub repo provided by the experimenter.

Returns
-------
int
    The return code from the rsync process (0 means success)

Examples
--------
>>> from rsync import rsync_experiment
>>> rsync_experiment("https://github.com/DiscoverCCRI/RoverAPI.git")

"""


def rsync_experiment(github_link: str):
    code = run(f"ssh -p 2222 {USER}@{HOST} 'cd ~/experiments && \
               git clone {github_link}'", shell=True)
    return code.returncode
