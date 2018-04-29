# -*- coding: utf-8 -*-
"""
force_rekey.py forces a VSD keyserver to reissue Seed, SEKs, and other primitives.

--- Author ---
Roman Dodin <dodin.roman@gmail.com>

--- Usage ---
python force_rekey.py

--- Documentation ---
https://github.com/nuagenetworks/vspk-examples/blob/master/python/force_rekey.md
"""

import time

from vspk import v5_0 as vspk

# Login variables
n_username = 'csproot'
n_password = 'csproot'
n_org = 'csp'
api_url = 'https://10.167.60.21:8443'

# script variables
org_name = '521_CATS_FIXED'
job_timeout = 600  # in seconds

def is_job_ready(job, timeout=600):
    """
    Waits for job to succeed and returns job.result
    """

    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        job.fetch()
        if job.status == 'SUCCESS':
            print('SUCCESS :: Re-keying Job succeeded!')
            return True
        if job.status == 'FAILED':
            return False
        time.sleep(1)
    print('ERROR :: Job {} failed to return its status in {}sec interval'.format(
        job.command, timeout))

nuage_session = vspk.NUVSDSession(
    username=n_username,
    password=n_password,
    enterprise=n_org,
    api_url=api_url)

me = nuage_session.start().user

# get parent for the re-key job object
org = me.enterprises.get_first(filter='name == "{}"'.format(org_name))

# create job object
job = vspk.NUJob(command='FORCE_KEYSERVER_UPDATE')

print('Starting {} job for the {} Organization'.format(
    'FORCE_KEYSERVER_UPDATE',
    org.name))

# run job object under its parent
org.create_child(job)

# wait for object to finish
is_job_ready(job, timeout=job_timeout)
