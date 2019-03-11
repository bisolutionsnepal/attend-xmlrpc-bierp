#!/usr/bin/python3
############################################################################
### Some Casual Imports
import xmlrpc.client
import datetime
import sys
import os
from fuzzywuzzy import fuzz
############################################################################
###Credentials Administrator or one with manager access of Attendance module.
# username = 'xmlrpc'
# password = 'foo'
# db = 'xmlrpc' #database name
# url='http://localhost:8082' #odooserver url

# Example
# username = 'xmlrpc'
# password = 'foo'
# db = 'xmlrpc'
# url='http://localhost:8082'

############################################################################
###Help Usuage Printing.
def attend_help():
    print("""
---------------------------------------------------
| attend <yourname> state/status/checkin/checkout |
---------------------------------------------------""")

if len(sys.argv)==1:
    print("""
Roses are red, Violets are blue
without any arguments master,
what am i going to do. """)
    attend_help()
    sys.exit()

############################################################################
###Help Usuage Printing.
def intro():
    print("""
--------------------------------------
|          Odoo CLI Attendance       |
-------------------------------------- """)

############################################################################
###Try-except to prevent Error raises
try:
    emp_name = sys.argv[1]
except IndexError as indexerrname:
    print("You sure that employee exists?")
    attend_help()
    sys.exit()

############################################################################
###Try-except to prevent Error raises
try:
    chkinout = sys.argv[2]
except IndexError as indexerrio:
    print("Makeup your mind. It's easy either checkin or checkout.")
    attend_help()
    sys.exit()

############################################################################
### xmlrpc objects
try:
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
except IOError as ioerror:
    print("Check Script Credentials")
    sys.exit()
############################################################################
###Get UserID of the employee authenticated with above usernmae.
uid = common.authenticate(db, username, password, {})

############################################################################
###Get all the employees name & id . Later use it to extract needed ones.
emp_list = models.execute_kw(db, uid, password,'hr.employee', 'search_read',[],{'fields': ['name']})

def stat_get():
    attend_all = models.execute_kw(db, uid, password,'hr.attendance','search_read',[],{'fields': ['employee_id','check_in','check_out']})
    for each in attend_all:
        if each['employee_id'][1] == emp_name:
            print(each['employee_id'][1])
            break
    print('-------------------------------------------')
    for each in attend_all:
        if each['employee_id'][1] == emp_name:
            checkin = datetime.datetime.strptime(each['check_in'],'%Y-%m-%d %H:%M:%S')
            checkout = datetime.datetime.strptime(each['check_out'],'%Y-%m-%d %H:%M:%S')
            print('|',checkin,' -------> ',checkout.strftime('%H:%M:%S'),'|')
            print('-------------------------------------------')
            if checkin.strftime('%Y-%m-%d') < (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d'):
                break


############################################################################
###Fuzzy Searching if the fuzzy.ratio > 50 then choose it.
for each in emp_list:
    if fuzz.partial_ratio(each['name'],emp_name) > 75:
        emp_name = each['name']

####################################
############################################################################
###Try-except to prevent Error raises if the employee index don't exist
try:
    usr_emp_id=list(filter(lambda person: person['name'] == emp_name, emp_list))[0]['id']
except IndexError as indexerrempid:
    print("You sure that employee exists?")
    attend_help()
    sys.exit()

############################################################################
### Get attendance state of the user.
attend_data=models.execute_kw(db, uid, password, 'hr.employee','search_read',[],{'fields':['attendance_state','name']})
attend_state=list(filter(lambda person: person['name'] == emp_name, attend_data))[0]['attendance_state']

############################################################################
### Noobish conditions and checking statements
if (chkinout == 'status' or chkinout == 'state'):
    print('You are',attend_state)
elif (chkinout == 'stat' or chkinout == 'history'):
    stat_get()
elif (attend_state == 'checked_out' and chkinout == 'checkin'):
    print('Checking in ...')
    result=models.execute_kw(db, uid, password, 'hr.employee','attendance_manual',[[usr_emp_id],['hr_attendance.hr_attendance_action_my_attendances']])
    check_in= result['action']['attendance']['check_in']
    check_out= result['action']['attendance']['check_out']
    print('CheckedIn')
elif (attend_state == 'checked_in' and chkinout == 'checkout'):
    print('Checking out ...')
    result = models.execute_kw(db, uid, password, 'hr.employee','attendance_manual',[[usr_emp_id],['hr_attendance.hr_attendance_action_my_attendances']])
    check_in = result['action']['attendance']['check_in']
    check_out = result['action']['attendance']['check_out']
    print('CheckedOut')
elif (attend_state == 'checked_in' and chkinout == 'checkin'):
    print('You are already Checked In.')
    print("Please Check Out first.")
    attend_help()
elif (attend_state == 'checked_out' and chkinout == 'checkout'):
    print("You have already Checked Out.")
    print("Please Check In first.")
else:
    print("Makeup your mind. It's easy either checkin or checkout.")
    attend_help()
sys.exit()
############################################################################
### End of Script Ez
