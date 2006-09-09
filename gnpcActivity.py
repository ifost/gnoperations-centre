import sys
import time

try:
    import syslog
    EMERGENCY = syslog.LOG_EMERG
    ALERT = syslog.LOG_ALERT
    CRITICAL = syslog.LOG_CRIT
    ERROR = syslog.LOG_ERR
    WARNING = syslog.LOG_WARNING
    NOTICE = syslog.LOG_NOTICE
    INFO = syslog.LOG_INFO
    DEBUG = syslog.LOG_DEBUG
    syslog.openlog('gnpc',0,syslog.LOG_DAEMON)
    using_syslog = 1
except:
    # maybe I should check for evt_log and use it also???
    EMERGENCY = '[emergency]'
    ALERT = '[alert]'
    CRITICAL = '[critical]'
    ERROR = '[error]'
    WARNING = '[warning]'
    NOTICE = '[notice]'
    INFO = '[info]'
    DEBUG = '[debug]'
    using_syslog = 0

def record(priority,message):
    """record(priority,message)
         priority should be one of the constants defined in this module"""
    sys.stderr.write(time.asctime(time.localtime(time.time())))
    sys.stderr.write(' ')
    if using_syslog:
        syslog.syslog(priority,message)
    else:
        sys.stderr.write(priority + ' ')
    sys.stderr.write(message)
        
