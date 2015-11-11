#! /usr/bin/env python
"""
This script is designed to trigger jobs through Release Engineering's
buildapi self-serve service.

The API documentation is in here (behind LDAP):
https://secure.pub.build.mozilla.org/buildapi/self-serve

The docs can be found in here:
http://moz-releng-buildapi.readthedocs.org
"""
from __future__ import absolute_import
import json
import logging
import os

import requests

HOST_ROOT = 'https://secure.pub.build.mozilla.org/buildapi/self-serve'
LOG = logging.getLogger("buildapi_client")


class BuildapiAuthError(Exception):
    pass


def trigger_arbitrary_job(repo_name, builder, revision, auth, files=[], dry_run=False,
                          extra_properties=None):
    """
    Request buildapi to trigger a job for us.

    We return the request or None if dry_run is True.

    Raises BuildapiAuthError if credentials are invalid.
    """
    url = _builders_api_url(repo_name, builder, revision)
    payload = _payload(repo_name, revision, files, extra_properties)

    if dry_run:
        LOG.info("Dry-run: We were going to request a job for '%s'" % builder)
        LOG.info("         with this payload: %s" % str(payload))
        return None

    # NOTE: A good response returns json with request_id as one of the keys
    req = requests.post(
        url,
        headers={'Accept': 'application/json'},
        data=payload,
        auth=auth
    )
    if req.status_code == 401:
        raise BuildapiAuthError("Your credentials were invalid. Please try again.")

    try:
        content = req.json()
        LOG.debug("Status of the request: %s" % _jobs_api_url(content["request_id"]))
        return req

    except ValueError:
        LOG.warning("We did not get info from %s (status code: %s)" % (url, req.status_code))
        return None


def make_retrigger_request(repo_name, request_id, auth, count=1, priority=0, dry_run=True):
    """
    Retrigger a request using buildapi self-serve. Returns a request.

    Buildapi documentation:
    POST  /self-serve/{branch}/request
    Rebuild `request_id`, which must be passed in as a POST parameter.
    `priority` and `count` are also accepted as optional
    parameters. `count` defaults to 1, and represents the number
    of times this build  will be rebuilt.
    """
    url = '{}/{}/request'.format(HOST_ROOT, repo_name)
    payload = {'request_id': request_id}

    if count != 1 or priority != 0:
        payload.update({'count': count,
                        'priority': priority})

    if dry_run:
        LOG.info('We would make a POST request to %s with the payload: %s' % (url, str(payload)))
        return None

    LOG.info("We're going to re-trigger an existing completed job with request_id: %s %i time(s)."
             % (request_id, count))
    req = requests.post(
        url,
        headers={'Accept': 'application/json'},
        data=payload,
        auth=auth
    )
    # TODO: add debug message with job_id URL.
    return req


def make_cancel_request(repo_name, request_id, auth, dry_run=True):
    """
    Cancel a request using buildapi self-serve. Returns a request.

    Buildapi documentation:
    DELETE /self-serve/{branch}/request/{request_id} Cancel the given request
    """
    url = '{}/{}/request/{}'.format(HOST_ROOT, repo_name, request_id)
    if dry_run:
        LOG.info('We would make a DELETE request to %s.' % url)
        return None

    LOG.info("We're going to cancel the job at %s" % url)
    req = requests.delete(url, auth=auth)
    # TODO: add debug message with the canceled job_id URL. Find a way
    # to do that without doing an additional request.
    return req


def _builders_api_url(repo_name, builder, revision):
    return r'''%s/%s/builders/%s/%s''' % (
        HOST_ROOT,
        repo_name,
        builder,
        revision
    )


def _jobs_api_url(job_id):
    """This is the URL to a self-serve job request (scheduling, canceling, etc)."""
    return r'''%s/jobs/%s''' % (HOST_ROOT, job_id)


def _payload(repo_name, revision, files=[], extra_properties=None):

    # These properties are needed for Treeherder to display running jobs.
    # Additional properties may be specified by a user.
    props = {
        "branch": repo_name,
        "revision": revision,
    }
    props.update(extra_properties or {})

    payload = {
        'properties': json.dumps(props, sort_keys=True)
    }

    if files:
        payload['files'] = json.dumps(files)

    return payload
	
def make_query_repositories_request(auth):
    url = "%s/branches?format=json" % HOST_ROOT
    LOG.debug("About to fetch %s" % url)
    req = requests.get(url, auth=auth)
    if req.status_code == 401:
        raise BuildapiAuthError("Your credentials were invalid. Please try again.")
    return req
