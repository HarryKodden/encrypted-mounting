#!/usr/bin/python2

# Workaround for CVE-2019-16729
# https://sourceforge.net/p/pam-python/tickets/8/
import site
site.main()

import syslog
import traceback
import sys

sys.path.append('/usr/local/lib/python2.7/dist-packages')

import requests

DEFAULT_USER  = "nobody"
DEBUGGING = True

DEBUG_FILE = "/tmp/debug.pam"

def debug(message):
    with open(DEBUG_FILE, "w+") as f:
        f.write("Python version: {}\n".format(sys.version))
        f.write("Python path: {}\n".format(sys.path))
        f.write("{}\n".format(message))

def logging(facility, message):
    debug(message)

    if (facility != syslog.LOG_DEBUG) or DEBUGGING:
        syslog.openlog(facility=facility)
        syslog.syslog(facility, message)
        syslog.closelog()


def get_config(argv):
    """
    Read the parameters from the arguments. If the argument can be split with a
    "=", the parameter will get the given value.
    :param argv:
    :return: dictionary with the parameters
    """
    config = {}
    for arg in argv:
        argument = arg.split("=")
        if len(argument) == 1:
            config[argument[0]] = True
        elif len(argument) == 2:
            config[argument[0]] = argument[1]
    
    debug(config)
    return config

def pam_sm_authenticate(pamh, flags, argv):

    config = get_config(argv)
    
    global DEBUGGING
    DEBUGGING = (config.get("debug", None) != None)

    logging(syslog.LOG_DEBUG, "Starting PAM authentication...{}".format(config))

    prompt = config.get("prompt", "Vault Secret Password")
    if prompt[-1] != ":":
        prompt += ":"

    url = "{}/validate/{}/{}".format(
        config.get("url", "http://localhost:8080"),
        config.get("service", "default"),
        pamh.get_user(None) or DEFAULT_USER
    )

    sslverify = not config.get("nosslverify", False)
    cacerts = config.get("cacerts")
    if sslverify and cacerts:
        sslverify = cacerts
    
    logging(syslog.LOG_DEBUG, "URL: {}".format(url))

    rval = pamh.PAM_AUTH_ERR

    try:
        if pamh.authtok is None:
            message = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "%s " % prompt)
            response = pamh.conversation(message)
            pamh.authtok = response.resp

        payload = { 
            "secret_name": "password",
            "secret_value": pamh.authtok
        }
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, json=payload, headers=headers, verify=sslverify)

        logging(syslog.LOG_DEBUG, response.text)

        if (response.status_code == 200):
            rval = pamh.PAM_SUCCESS

    except Exception as e:
        logging(syslog.LOG_ERR, traceback.format_exc())
        logging(syslog.LOG_ERR, "%s: %s" % (__name__, e))

    except requests.exceptions.SSLError:
        logging(syslog.LOG_CRIT, "%s: SSL Validation error. Get a valid "
                                 "SSL certificate, For testing you can use the "
                                 "options 'nosslverify'." % __name__)

    return rval

def pam_sm_setcred(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
  return pamh.PAM_SUCCESS
