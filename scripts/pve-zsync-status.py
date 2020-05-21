# Get Information about PVE-zsync Replication Tasks

# Author: Sebastian Plocek
# https://github.com/sebastian13/zabbix-template-pve-zsync

# Forked from
# https://github.com/Cacohh/Template-PVE-Zsync/blob/master/scripts/pvezsync.py

# How to Use
def help():
    print("""
            PVE-zsync Monitoring
            https://github.com/sebastian13/zabbix-template-pve-zsync

            Usage:
                python3 pve-zsync-status [function] [name] [source]

            Available [functions]:
                - pvezsyncDescriptor
                - pvezsyncDest
                - pvezsyncFuzzytime
                - pvezsyncJobState
                - pvezsyncLastSync
                - pvezsyncMaxSnap
                - pvezsyncNextRun
            """)


# Function to access crontab file
def accessCrontab(filePath):
    from crontab import CronTab
    fileCron = CronTab(tabfile=filePath)
    return fileCron


# Function to obtain replication state for specific job
def pvezsyncJobState(name, source):
    import subprocess
    command = str("pve-zsync list | grep '" + str(source) + " .* " + str(name) + "' | tr -s ' ' ',' | cut -d, -f 3")
    data = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = data.communicate()
    return stdout.decode('utf-8')


# Function that return the date of the next run from a job in crontab file
def pvezsyncNextRun(cron, name, source):
    import re
    import datetime
    iter = cron.find_command(re.compile("--source\s" + source + ".*--name\s" + name)) 
    for job in iter:
        schedule = job.schedule(date_from=datetime.datetime.now())
        return (schedule.get_next())


# Return the Last Sync Timestamp according to `pve-zsync list`
def pvezsyncLastSync(name, source):
    import subprocess
    import re
    from datetime import datetime
    import time
    s = subprocess.check_output("pve-zsync list | grep '" + str(source) + " .* " + str(name) + "' | awk '{print $4}' | tr -d '\n'", shell=True)
    d = datetime.strptime(s.decode('utf-8'), "%Y-%m-%d_%H:%M:%S")
    return time.mktime(d.timetuple())


# Return the job frequency
def pvezsyncDescriptor(cron, name, source):
    import re
    import datetime
    iter = cron.find_command(re.compile("--source\s" + source + ".*--name\s" + name)) 
    for job in iter:
        return job.description(use_24hour_time_format=True)


# Return the fuzzytime - i.e. the time between each cron run, incl. a 5-minutes tolerance
def pvezsyncFuzzytime(cron, name, source):
    import re
    import datetime
    iter = cron.find_command(re.compile("--source\s" + source + ".*--name\s" + name))
    for job in iter:
        # Calculate seconds between each execution
        # A default tolerance of 300 seconds will be added via preprocessing on Zabbix Server.
        # This can be customized by overwriting the inherited macro {$FUZZYTOLERANCE}.
        fuzzytime = ( 86400 // job.frequency_per_day() )
        return fuzzytime


# Return the number of snapshots which should be kept
def pvezsyncMaxSnap(cron, name, source):
    import re
    iter = cron.find_command(re.compile("--source\s" + source + ".*--name\s" + name))
    for job in iter:
        jobStr = str(job)
        jobList = jobStr.split()
        index = jobList.index("--maxsnap")
        return jobList[index + 1]


# Return the destination
def pvezsyncDest(cron, name, source):
    import re
    iter = cron.find_command(re.compile("--source\s" + source + ".*--name\s" + name))
    for job in iter:
        jobStr = str(job)
        jobList = jobStr.split()
        index = jobList.index("--dest")
        return jobList[index + 1]


if __name__ == '__main__':
    # Imports
    import sys
    # Define location of crontab file of PVE-Zsync (Default: '/etc/cron.d/pve-zsync')
    file = '/etc/cron.d/pve-zsync'

    if len(sys.argv) != 4:
        help()
        sys.exit(1)

    # Decide which function to use and pass arguments from cli
    if sys.argv[1] == "pvezsyncJobState":
        print(pvezsyncJobState(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "pvezsyncNextRun":
        print(pvezsyncNextRun(accessCrontab(file), sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "pvezsyncLastSync":
        print(pvezsyncLastSync(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "pvezsyncDescriptor":
        print(pvezsyncDescriptor(accessCrontab(file), sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "pvezsyncFuzzytime":
        print(pvezsyncFuzzytime(accessCrontab(file), sys.argv[2], sys.argv[3]), end='')
    elif sys.argv[1] == "pvezsyncMaxSnap":
        print(pvezsyncMaxSnap(accessCrontab(file), sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "pvezsyncDest":
        print(pvezsyncDest(accessCrontab(file), sys.argv[2], sys.argv[3]))
    else:
        print("""
            [ERROR] Function >>>  """ + sys.argv[1] + "  <<< is unknown.")
        help()
