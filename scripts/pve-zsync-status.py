# Get Information about PVE-zsync Replication Tasks

# Author: Sebastian Plocek
# https://github.com/sebastian13/zabbix-template-pve-zsync

# Forked from
# https://github.com/Cacohh/Template-PVE-Zsync/blob/master/scripts/pvezsync.py

# Function to access crontab file
def accessCrontab(filePath):
    from crontab import CronTab
    fileCron = CronTab(tabfile=filePath)
    return fileCron


# Function to obtain replication state for specific job
def pvezsyncJobState(job):
    import subprocess
    command = str("pve-zsync list | grep " + str(job) + " | tr -s ' ' ',' | cut -d, -f 3")
    data = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = data.communicate()
    return stdout.decode('utf-8')


# Function that return the date of the next run from a job in crontab file
def pvezsyncNextRun(crontabSystem, commandoJob):
    import re
    import datetime
    for job in crontabSystem:
        x = re.findall(commandoJob, str(job))
        if x:
            sch = job.schedule(date_from=datetime.datetime.now())
            return sch.get_next()


# Function that return the date of the previous run from a job in crontab file
def pvezsyncLastSync(name, source):
    import subprocess
    import re
    from datetime import datetime
    import time
    s = subprocess.check_output("pve-zsync list | grep '" + str(source) + " .* " + str(name) + "' | awk '{print $4}' | tr -d '\n'", shell=True)
    d = datetime.strptime(s.decode('utf-8'), "%Y-%m-%d_%H:%M:%S")
    return time.mktime(d.timetuple())

def pvezsyncDescriptor(crontabSystem, commandoJob):
    import re
    for job in crontabSystem:
        x = re.findall(commandoJob, str(job))
        if x:
            return job.description(use_24hour_time_format=True)


def pvezsyncMaxSnap(crontabSystem, commandoJob):
    import re
    for job in crontabSystem:
        jobStr = str(job)
        x = re.findall(commandoJob, jobStr)
        if x:
            jobList = jobStr.split()
            index = jobList.index("--maxsnap")
            return jobList[index + 1]


if __name__ == '__main__':
    # Imports
    import sys
    # Define location of crontab file of PVE-Zsync (Default: '/etc/cron.d/pve-zsync')
    file = '/etc/cron.d/pve-zsync'
    # Decide which function to use and pass arguments from cli
    if sys.argv[1] == "pvezsyncJobState":
        print(pvezsyncJobState(sys.argv[2]))
    elif sys.argv[1] == "pvezsyncNextRun":
        print(pvezsyncNextRun(accessCrontab(file), sys.argv[2]))
    elif sys.argv[1] == "pvezsyncLastSync":
        print(pvezsyncLastSync(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "pvezsyncDescriptor":
        print(pvezsyncDescriptor(accessCrontab(file), sys.argv[2]))
    elif sys.argv[1] == "pvezsyncMaxSnap":
        print(pvezsyncMaxSnap(accessCrontab(file), sys.argv[2]))
    else:
        print("Wrong arguments!!! Check your configuration and documentation if necessary!!!")
