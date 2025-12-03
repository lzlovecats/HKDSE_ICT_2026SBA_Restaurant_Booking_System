from datetime import datetime, date
import random
import string
ubid_gen_list = string.ascii_letters + string.digits
def gen_unique_ubid():  # Generate unique booking identification code
    check_unique_set = set()  # Use set instead of list for better efficiency
    with open("BookingSy.txt", "r") as f:
        all_bookings = f.readlines()
    for book in all_bookings:
        parts = book.strip().split(", ")
        if len(parts) != 5:
            continue
        ubid, userid, book_date, group_num, book_time = parts
        check_unique_set.add(str(ubid))  # Add existing ubid to the set
    with open("WaitingList.txt", "r") as f:
        wait_bookings = f.readlines()
    for book_wait in wait_bookings:
        parts = book_wait.strip().split(", ")
        if len(parts) != 5:
            continue
        w_ubid, w_userid, w_book_date, w_group_num, w_book_time = parts
        check_unique_set.add(str(w_ubid))  # Add existing ubid in waiting list to the set
    while True:
        ran_ubid = ""
        for i in range(6):
            ran_ubid += random.choice(ubid_gen_list)
        if ran_ubid not in check_unique_set:  # If generated ubid repeated, try again
            check_unique_set.add(ran_ubid)
            uni_ubid = str(ran_ubid)
            return uni_ubid

print("")
check_id = ["hknZxk", "CRARAz"]  # UBID of the existing bookings  
no_bug = True      
for i in range(0, 2000000):
    print(f"\nChecking for {i+1} times...\n")
    a = gen_unique_ubid()
    if a in check_id:
        no_bug = False
        break
print(no_bug)