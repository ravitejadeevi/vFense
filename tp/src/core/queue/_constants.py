class BaseURIs():
    LISTENER = '/rvl/v1/'
    API = '/api/v1/'


class ListenerURIs():
    INSTALL_OS_APPS = '/rv/results/install/apps/os?'
    INSTALL_CUSTOM_APPS = '/rv/results/install/apps/custom?'
    INSTALL_SUPPORTED_APPS = '/rv/results/install/apps/supported?'
    INSTALL_AGENT_APPS = '/rv/results/install/apps/agent?'
    UNINSTALL = '/rv/results/uninstall?'
    REBOOT =  '/core/results/reboot/?'
    SHUTDOWN =  '/core/results/shutdown/?'
    APPS_REFRESH = '/core/results/updatesapplications/?'
    START_UP = '/core/results/startup/?'
    CHECKIN = '/core/results/checkin/?'
    NEWAGENT = '/core/newagent/?'
    RA = '/ra/rd/results/?'
    MONIOR_DATA = '/monitoring/monitordata/?'

class ValidOperations():
    NEWAGENT = 'newagent'
    APPS_REFRESH = 'updatesapplications'
    CHECKIN = 'checkin'
    STARTUP = 'startup'
    INSTALL_OS_APPS = 'install_os_apps'
    INSTALL_CUSTOM_APPS = 'install_custom_apps'
    INSTALL_SUPPORTED_APPS = 'install_agent_apps'
    INSTALL_AGENT_APPS = 'install_agent_apps'
    UNINSTALL  = 'uninstall'
    UNINSTALL_AGENT = 'uninstall_agent'
    REBOOT = 'reboot'
    SHUTDOWN = 'shutdown'
    RA = 'ra'
    OPERATIONS = (
        NEWAGENT, APPS_REFRESH, CHECKIN,
        STARTUP, INSTALL_OS_APPS, INSTALL_CUSTOM_APPS,
        INSTALL_SUPPORTED_APPS, INSTALL_AGENT_APPS,
        UNINSTALL, UNINSTALL_AGENT,
        REBOOT, SHUTDOWN, RA
    )


