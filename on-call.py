import json
import datetime
import time


# can't be on same team for primary and backup
# can't be on primary within the past 3 months
# can't be on backup within the past 1.5 months
# 4 people per month
# rotate every 2 weeks
# track current count of week, compare with team member count


def loadEmployees():
    with open('employees.json', 'r') as em:
        return json.load(em)


def getCurrentDay():
    return datetime.date.today()

def getDates(WEEK):
    if WEEK > 52:
        print("ISSUE")
    startdate = time.asctime(time.strptime('2022 %d 0' % WEEK, '%Y %W %w'))
    startdate = datetime.datetime.strptime(startdate, '%a %b %d %H:%M:%S %Y')
    dates = [startdate.strftime('%Y-%m-%d')]
    for i in range(1, 14):
        day = startdate + datetime.timedelta(days=i)
        dates.append(day.strftime('%Y-%m-%d'))
    weekStart = dates[0]
    weekEnd = dates[-1]
    print(f"{weekStart} - {weekEnd}")


def getNextweekDate():
    return datetime.datetime.today() + datetime.timedelta(days=14)


def getCurrentDayStat(todayDate):
    year, week_num, day_of_week = todayDate.isocalendar()
    return week_num


def updateStatus(primary, backup, curWeek):
    employees = loadEmployees()
    for e in employees:
        if e not in employees[primary] or employees[backup]:
            employees[e]['active'] = False
    employees[primary]['main'] = curWeek
    employees[backup]['backup'] = curWeek
    employees[primary]['active'] = True
    employees[backup]['active'] = True
    try:
        with open('employees.json', 'w') as jsonFile:
            json.dump(employees, jsonFile)
            # log this
            # print(f"successfuly updated {primary} to week {curWeek}")
            # print(f"successfuly updated {backup} to week {curWeek}")
    except Exception as e:
        print(e)


def teamConflict(primary, backup, employees):
    primaryTeam = None
    backupTeam = None
    developers = [tup[1] for tup in employees]
    for dev in developers:
        if primary in dev['name']:
            primaryTeam = dev['team']
        elif backup in dev['name']:
            backupTeam = dev['team']

    if primaryTeam == backupTeam:
        # print(f"==== Conflict with {primary.capitalize()} and {backup.capitalize()} ===")
        return True
    else:
        # print(f"\n\nPrimary: {primary.capitalize()} - Backup: {backup.capitalize()}")
        return False


def checkLastRotation(k, v, option, curWeek, addWeek):
    if not v['active']:
        if v[option] + addWeek <= curWeek:
            return True


def checkConflict(availableMain, availableBackup, primaryDev, backupDev, employees, curWeek,
                  removeConflictingBackup=False):
    if removeConflictingBackup:
        try:
            removeBackupDev = availableBackup['dev'].pop(backupDev)
            backupDev = min(availableBackup['dev'], key=availableBackup['dev'].get)
        except ValueError:
            print(f"Insufficient Backup List. Issue with list of employees (conflict with team)")
            exit()
    else:
        try:
            primaryDev = min(availableMain['dev'], key=availableMain['dev'].get)
        except KeyError:
            print("No Primary Devs Available")
            exit()

        if primaryDev in availableBackup['dev']:
            removePrimary = availableBackup['dev'].pop(primaryDev)
            backupDev = min(availableBackup['dev'], key=availableBackup['dev'].get)
        else:
            backupDev = min(availableBackup['dev'], key=availableBackup['dev'].get)

    hasConflict = teamConflict(primaryDev, backupDev, list(employees))
    if hasConflict:
        checkConflict(availableMain, availableBackup, primaryDev, backupDev, employees, curWeek, backupDev)
    else:
        if curWeek > 52:
            curWeek = curWeek - 52
            getDates(curWeek)
            print(f"{primaryDev.capitalize()} & {backupDev.capitalize()}")
        else:
            getDates(curWeek)
            print(f"{primaryDev.capitalize()} & {backupDev.capitalize()}")
        updateStatus(primaryDev, backupDev, curWeek)


def getPrimaryandBackup(availableMain, availableBackup, employees, curWeek):
    primaryDev = None
    backupDev = None
    checkConflict(availableMain, availableBackup, primaryDev, backupDev, employees, curWeek, )


def findMain(employees, curWeek):
    global mainDelay
    global backupDelay
    availableMain = {}
    availableBackup = {}

    # check if dev has been on support within a month and a half (5 cycles)
    for k, v in employees:
        if checkLastRotation(k, v, 'main', curWeek, mainDelay):
            # print(f"Available for main support {k}: Week {v['main']}")
            try:
                availableMain['dev'].update({k: v['main']})
            except KeyError:
                availableMain.setdefault('dev', {k: v['main']})
        if checkLastRotation(k, v, 'backup', curWeek, backupDelay):
            # print(f"Available for backup support {k}: Week {v['backup']}")
            try:
                availableBackup['dev'].update({k: v['main']})
            except KeyError:
                availableBackup.setdefault('dev', {k: v['main']})
    getPrimaryandBackup(availableMain, availableBackup, employees, curWeek)


def main():
    global isBegin
    weeksToYear = 52
    for i in range(weeksToYear):
        if isBegin:
            curWeek = getCurrentDayStat(getCurrentDay())
        else:
            curWeek = curWeek + 2
        employees = loadEmployees().items()
        if not len(employees) <= 1:
            findMain(employees, curWeek)
        else:
            print("NOT ENOUGH EMPLOYEES")
            break
        isBegin = False


if __name__ == '__main__':
    isBegin = True
    mainDelay = 6
    backupDelay = 6
    main()
