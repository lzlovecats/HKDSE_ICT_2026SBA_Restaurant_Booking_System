# Instruction to markers:
# Please ensure all the text files are saved under the same folder before running.
# Please fully extract all the files from the zip file.
# ** You are strongly advised to use VS Code to run this program for better experience.
# ** https://code.visualstudio.com/
# Please ONLY open the folder storing this program in the IDE,
# DO NOT open the folder as a sub-folder in another folder, or run-time errors might occur.

# Admin UserID: LoveWaiWai, PW: iWANT5**

import os.path
import time
import math
import string
import random
from random import randrange
from datetime import date, datetime, timedelta
from random import randrange

G9_12 = 30  # Default Table Number
G5_8 = 20
G1_4 = 10
ubid_gen_list = string.ascii_letters + string.digits  # UBID stands for Unique Booking Identification Code

R = '\033[91m'  # Error Message: Red
G = '\033[92m'  # Success Message: Green
Y = '\033[33m'  # Warning Message: Yellow
C = '\033[36m'  # Menu options: Cyan
E = '\033[0m'  # END
B = '\033[1m'  # BOLD


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


def start_screen():  # Program starts form here
    while True:
        if not check_files_exist():
            print("\n")
            exit()
        read_table_num()
        delete_old_bookings()
        update_waiting_list()
        login_system()


def check_files_exist():  # Check all the required files exist to prevent run-time errors
    files = {
        "Account.txt": os.path.isfile("Account.txt"),
        "BookingSy.txt": os.path.isfile("BookingSy.txt"),
        "MaxDate.txt": os.path.isfile("MaxDate.txt"),
        "WaitingList.txt": os.path.isfile("WaitingList.txt"),
        "Tables.txt": os.path.isfile("Tables.txt"),
        "PushMsg.txt": os.path.isfile("PushMsg.txt")
    }
    if not all(files.values()):
        print(f"\n{R}Error: Missing program files. Please ensure all the files are extracted under the same "
              f"folder.\nYou may continue to use the program, missing files will be automatically created, "
              f"but run-time error might occur.{E}")
        choice = input("\nType 'yes' to continue your work or press enter to exit program:").strip().lower()
        if choice in ["yes", "y"]:
            for f_name, status in files.items():
                if not status:
                    try:
                        open(f_name, "x").close()  # Only create missing files
                    except FileExistsError:
                        pass
                    except OSError as infor:
                        print(f"{R}災難性的失敗！{E}")
                        print(f"{R}Error information: {infor}{E}")
                        return False
            return True  # When missing files are created, allow user to continue their work
        else:
            return False  # If the user don't want to generate missing files, run-time error may occur, thus return False
    else:
        return True  # All files are there, good


def delete_old_bookings():  # Delete useless bookings to maximise the efficiency
    delete_old_booking = []
    with open("BookingSy.txt", "r") as f:
        bookings = f.readlines()
        for booking in bookings:
            parts = booking.strip().split(", ")
            if len(parts) != 5:
                continue
            ubid, userid, booking_date, booking_num, booking_time = parts
            try:
                booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()  # Only handle booking date
            except ValueError:
                continue  # If format error, means the booking will not be considerd valid, skip it
            if booking_date >= date.today():  # Check the booking date, if less than today, skip it
                delete_old_booking.append(
                    f"{ubid}, {userid}, {booking_date.strftime('%Y-%m-%d')}, {booking_num}, {booking_time}\n")
            else:
                continue
    with open("BookingSy.txt", "w") as f:
        f.writelines(delete_old_booking)


def update_waiting_list():  # Update waiting list
    with open("WaitingList.txt", "r") as f:
        waiting_list = f.readlines()

    updated_waiting_list = []
    for wait_booking in waiting_list:
        parts = wait_booking.strip().split(", ")
        if len(parts) != 5:
            continue

        ubid, userid, booking_date_str, group_size, booking_time_str = parts
        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            booking_time = datetime.strptime(booking_time_str, "%H:%M:%S").time()
            group_size = int(group_size)
        except ValueError:
            continue

        if check_availability(group_size, booking_date, booking_time) and not check_duplicated_booking(userid,
                                                                                                       booking_date,
                                                                                                       booking_time):
            # To ensure booking is valid
            write_booking(ubid, userid, booking_date, booking_time, group_size)
            write_push_msg(f"{userid}", f"{G}Your booking on {booking_date} has been confirmed. "
                                        f"Check details on Booking Menu Option 2.{E}")
        else:
            updated_waiting_list.append(wait_booking)

    with open("WaitingList.txt", "w") as f:
        f.writelines(updated_waiting_list)


def read_table_num():  # Update the table numbers, if error exist, use default settings
    global G9_12  # Numbers of tables for group num 9-12
    global G5_8  # Numbers of tables for group num 5-8
    global G1_4  # Numbers of tables for group num 1-4
    with open("Tables.txt", "r") as f:
        numbers = f.read().strip().split(", ")
        if len(numbers) != 3:
            G9_12 = 30
            G5_8 = 20
            G1_4 = 10
        else:
            G9_12, G5_8, G1_4 = numbers
            try:
                G9_12 = int(G9_12)
                G5_8 = int(G5_8)
                G1_4 = int(G1_4)
            except ValueError:  # If the file content is invalid
                G9_12 = 30
                G5_8 = 20
                G1_4 = 10
    with open("Tables.txt", "w") as f:
        f.write(f"{G9_12}, {G5_8}, {G1_4}")


def check_availability(book_num, user_date, user_time):  # To ensure the booking is valid
    book_num = int(book_num)
    available_tables = {
        range(1, 5): G1_4,  # tables for 1-4 people
        range(5, 9): G5_8,  # tables for 5-8 people
        range(9, 13): G9_12  # tables for 9-12 people
    }

    max_tables = 0
    check_size = 0
    for group_size, tables in available_tables.items():
        if int(book_num) in group_size:
            check_size = group_size
            max_tables = tables
            break

    if max_tables == 0 or check_size == 0:  # If for some reasons, max_tables or check_size didn't change
        print(f"\n{R}Unexpected Error occurred, please restart the program.")
        print(f"If the problem persists, contact our IT support.{E}")
        input("Press enter to exit:")
        exit(1)

    with open("BookingSy.txt", "r") as f:
        bookings = f.readlines()

    booked_count = 0
    for booking in bookings:
        parts = booking.strip().split(", ")
        if len(parts) != 5:
            continue

        check_ubid, check_id1, booking_date_str, group_size_str, booking_time_str = parts
        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            booking_time = datetime.strptime(booking_time_str, "%H:%M:%S").time()
            group_size = int(group_size_str)
        except ValueError:
            continue

        if booking_date == user_date and booking_time == user_time and group_size in check_size:
            booked_count += 1

    return booked_count < max_tables


def check_duplicated_booking(userid, user_date, user_time):  # To ensure booking is not repeated
    with open("BookingSy.txt", "r") as f:
        bookings = f.readlines()

    for k in bookings:
        parts = k.strip().split(", ")
        if len(parts) != 5:
            continue

        ubid, booking_id, booking_date_str, _, booking_time_str = parts
        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            booking_time = datetime.strptime(booking_time_str, "%H:%M:%S").time()
        except ValueError:
            continue

        if booking_id == userid and booking_date == user_date and booking_time == user_time:
            return True
    return False


def cal_max_day():  # Define the last available date for booking
    max_day = date.today() + timedelta(days=30)

    with open("MaxDate.txt", "w") as f:
        f.write(max_day.strftime("%Y-%m-%d"))

    return max_day.strftime("%Y-%m-%d")


def count_line():  # Calculate how many accounts was created
    with open("Account.txt", "r") as f:
        lines = f.readlines()
        count = len(lines)
        return count  # Will be used in create_account()


def create_account():  # Create a new acc and add it to "Account.txt"
    input(
        "\nWelcome to WaiWai's Restaurant Online Booking System, Press enter to start creating an account.")
    while True:
        userid = input("Input your new UserID:")
        if len(userid) == 0:
            empty = True
        else:
            empty = False
        check_space = userid.find(" ")  # No space is allowed
        check_comma = userid.find(",")  # No "," is allowed
        if check_space != -1 or check_comma != -1:
            print(f"{Y}Warning! No space or comma (,) is allowed!\n{E}")
            input("Press enter to try again.")
            continue
        elif empty:
            print(f"{Y}Warning! You have inputted nothing!\n{E}")
            input("Press enter to try again.")
            continue
        exist = False
        with open("Account.txt", "r") as f:
            for i in range(count_line()):
                line = f.readline().strip()
                line = line.split(", ")
                if len(line) != 3:
                    continue
                if userid == line[0]:
                    exist = True
                    break
                else:
                    exist = False
        if exist:
            print(f"{Y}Warning! This UserID is already in use! Please try another one!{E}")
            print("")
            continue
        else:
            break
    while True:
        pw = input("Create a password for your account: ")
        check_pw_space = pw.find(" ")  # To prevent error since I use ", " to split in other sub-programs
        check_pw_comma = pw.find(",")
        if check_pw_space != -1 or check_pw_comma != -1:
            print(f"{Y}Warning! No space or comma (,) is allowed!\n{E}")
            input("Press enter to try again.")
            continue
        check_pw = input("Please type your password again: ")
        if check_pw != pw:
            print(f"{Y}Passwords do not match, please try again.\n{E}")
            input("Press enter to try again.")
            continue
        else:
            break
    while True:
        phone = input("\nPlease input your phone number: ")
        if len(phone) != 8 or not phone.isdigit():
            print(f"{Y}Error! You have to input an 8-digit valid HK phone number!{E}")
            continue
        if phone[0] in ['4', '5', '6', '7', '8', '9']:
            break
        else:
            print(f"{Y}Error! Your phone number should start with [4, 5, 6, 7, 8, 9]!{E}")
            continue
    with open("Account.txt", "a") as f:
        f.write(f"{userid}, {pw}, {phone}\n")
    print(f"\n{G}Account creation complete! you may now use your new UserID and password to login.{E}")
    input(f"Press enter to proceed.")
    return


def login_system():
    delete_old_bookings()
    update_waiting_list()
    print("\n***WaiWai's Restaurant Login Page***")
    while True:
        userid_matched = False
        userid = input("Input your User ID: ('-1' to create an account)('-2' to exit the program)")
        if userid == '-2':
            print("")
            for i in range(randrange(8)):
                print("Exit Program...")
                time.sleep(1)
            exit()
        elif userid == '-1':
            create_account()
            return

        if userid == "LoveWaiWai":
            userid_matched = True
        else:
            with open("Account.txt", "r") as f:
                for line in f:
                    try:
                        stored_user, stored_pw, _ = line.strip().split(", ")
                    except ValueError:
                        continue
                    if userid == stored_user:
                        userid_matched = True
                        break

        if not userid_matched:
            print(f"{Y}The UserID does not exist, please try again.{E}")
            continue

        pw = input("Input your password: ")
        if userid == 'LoveWaiWai' and pw == 'iWANT5**':  # Admin Mode
            management_system()
            return

        login_success = False
        with open("Account.txt", "r") as f:
            for line in f:
                try:
                    stored_user, stored_pw, _ = line.strip().split(", ")
                except ValueError:
                    continue
                if userid == stored_user and pw == stored_pw:
                    login_success = True
                    break

        if login_success:
            print_msg(userid)
            return
        else:
            print(f"{Y}Login Failed! Please double-check your UserID and Password!\n{E}")


def management_system():
    global G9_12
    global G5_8
    global G1_4
    print("\n\nWelcome to WaiWai's Restaurant Management System")
    while True:
        print(f"\n{C}Management Menu:")
        print("1. Change the number of tables")
        print("2. View All Registered Accounts")
        print("3. Backup all the bookings")
        print("4. Recover all the bookings from last backed up")
        print("5. View all bookings")
        print("6. Exit Management System")
        print("7. Delete booking with UBID")
        print(f"8. Find booking details with UBID")
        print(f"9. Push msg to customer{E}")
        choice = input("Please enter your choice: ")
        if choice not in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            print(f"{Y}Invalid input! Please try again!{E}")
            continue
        else:
            if choice == '1':
                print(f"\nNumber of tables now: \nGroup 9-12: {G9_12}\nGroup 5-8: {G5_8}\nGroup 1-4: {G1_4}")
                ask = input("Input '-1' if you want to edit: ")
                if ask != '-1':
                    continue
                else:
                    while True:
                        new_G9_12 = input("Input new numbers of table for group 9-12: ")
                        new_G5_8 = input("Input new numbers of table for group 5-8: ")
                        new_G1_4 = input("Input new numbers of table for group 1-4: ")
                        try:
                            new_G9_12 = int(new_G9_12)
                            new_G5_8 = int(new_G5_8)
                            new_G1_4 = int(new_G1_4)
                            break
                        except ValueError:
                            print(f"{R}\nError! You should input integers!{E}")
                            input("Press enter to try again:")
                            print("")
                            continue
                    if new_G9_12 < G9_12 or new_G5_8 < G5_8 or new_G1_4 < G1_4:
                        print(f"\n{Y}Warning! new number(s) are smaller than the original one!")
                        print("Existing bookings will not be affected, "
                              f"if you want to delete them, choose option 7 in the menu.{E}")
                        really = input("Press '-4' to abort the change:")
                        if really == '-4':
                            input("Process aborted, press enter to continue:")
                            continue
                    with open("Tables.txt", "w") as f:
                        f.write(f"{new_G9_12}, {new_G5_8}, {new_G1_4}")
                    read_table_num()
                    input(f"{G}New number saved. Press enter to return to menu.{E}")
                    continue
            elif choice == '2':
                with open("Account.txt", "r") as f:
                    account = f.readlines()
                print("\nRegistered Accounts:")
                for k in account:
                    parts = k.strip().split(", ")
                    if len(parts) != 3:
                        continue
                    else:
                        userid, password, phone = parts
                        print(f"UserID: '{userid}', Phone: {phone}")
                input("Press enter to continue:")
                continue
            elif choice == '3':
                with open("BookingSy.txt", "r") as f:
                    backup = f.read()
                with open("Backup_BookingSy.txt", "w") as f:
                    f.write(backup)
                print(f"\n{G}Backup completed, the backup files is stored in 'Backup_BookingSy.txt'.{E}")
                input("Press enter to continue.")
                continue
            elif choice == '4':
                try:
                    with open("Backup_BookingSy.txt", "r") as f:
                        backup = f.read()
                except FileNotFoundError:
                    print(f"{R}No back up file found, you should do a backup first.{E}")
                    input("Press enter to continue")
                    continue
                with open("BookingSy.txt", "w") as f:
                    f.write(backup)
                print(f"\n{G}Recover completed.{E}")
                input("Press enter to continue:")
                continue
            elif choice == '5':
                with open("BookingSy.txt", "r") as f:
                    bookings = f.readlines()

                existing_bookings = []
                for booking in bookings:
                    parts = booking.strip().split(", ")
                    if len(parts) != 5:
                        continue

                    b_ubid, booking_id, booking_date_str, group_size, booking_time_str = parts
                    try:
                        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
                        booking_time = datetime.strptime(booking_time_str, "%H:%M:%S").time()
                        group_size = int(group_size)
                    except ValueError:
                        continue

                    months = {
                        1: "January",
                        2: "February",
                        3: "March",
                        4: "April",
                        5: "May",
                        6: "June",
                        7: "July",
                        8: "August",
                        9: "September",
                        10: "October",
                        11: "November",
                        12: "December"
                    }

                    month_final = booking_date.month

                    for book_month, month_str in months.items():
                        if booking_date.month == book_month:
                            month_final = month_str
                            break

                    existing_bookings.append(f"{b_ubid}:  "
                                             f"Reservation for {group_size} people at {booking_time} on"
                                             f" {booking_date.day} {month_final} {booking_date.year}"
                                             f" under the name '{booking_id}'.")

                if len(existing_bookings) > 0:
                    print("\nAll the bookings:")
                    for booking in existing_bookings:
                        print(booking)
                    input("Press enter to continue:")
                    continue
                else:
                    print("\nNo bookings found.")
                    input("Press enter to continue:")
                    continue
            elif choice == '6':
                print("")
                for i in range(randrange(8)):
                    print("Saving data...")
                    time.sleep(1)
                return
            elif choice == '7':
                m_new_bookings = []
                to_ubid = input("\nInput the ubid of the booking you want to cancel:")
                deleted = False
                with open("BookingSy.txt", "r") as f:
                    all_exist_bookings = f.readlines()
                for book in all_exist_bookings:
                    m_parts = book.strip().split(", ")
                    if len(m_parts) != 5:
                        continue
                    m_ubid, m_uid, m_date, m_num, m_time = m_parts
                    if m_ubid == to_ubid:
                        deleted = True
                        continue
                    else:
                        m_new_bookings.append(book)
                with open("BookingSy.txt", "w") as f:
                    f.writelines(m_new_bookings)
                if deleted:
                    input(f"{G}Deletion complete, press enter to return to the menu{E}")
                else:
                    print(f"\n{R}No booking with inputted UBID found{E}")
                    input("Press enter to proceed")
                continue
            elif choice == '8':
                search_for_ubid = input("Input the UBID of the booking:")
                found = False
                with open("BookingSy.txt", "r") as f:
                    op8_exist_bookings = f.readlines()
                for book in op8_exist_bookings:
                    m8_parts = book.strip().split(", ")
                    if len(m8_parts) != 5:
                        continue
                    m8_ubid, m8_uid, m8_date, m8_num, m8_time = m8_parts
                    if m8_ubid == search_for_ubid:
                        found = True
                        print("\nBooking Details:")
                        print(f"UBID: {m8_ubid}")
                        print(f"UserID: {m8_uid}")
                        print(f"Booking Date: {m8_date}")
                        print(f"Group Num: {m8_num}")
                        print(f"Booking Time: {m8_time}")
                        input("Press enter to proceed")
                        break
                if found:
                    continue
                else:
                    print(f"\n{R}No booking with inputted UBID found{E}")
                    input("Press enter to proceed")
                    continue
            elif choice == '9':
                while True:
                    Found = False
                    send_id = input("Input receiver's User ID:")
                    with open("Account.txt", "r") as f:
                        all_acc = f.readlines()
                    for acc in all_acc:
                        parts = acc.strip().split(", ")
                        if len(parts) != 3:
                            continue
                        acc_id, _, _ = parts
                        if acc_id == send_id:
                            Found = True
                            break
                    if not Found:
                        print(f"\n{R}UserID not found, please try again.{E}")
                        continue
                    else:
                        break
                send_content = input("Write message here: ")
                write_push_msg(send_id, send_content)
                input(f"{G}Finished, press enter to return to menu.{E}")


def booking_system(userid):
    while True:
        delete_old_bookings()
        update_waiting_list()
        read_table_num()
        print(f"{C}\nWelcome to WaiWai's Restaurant Booking System!")
        print("Booking Menu:")
        print("1. Book a table")
        print("2. View Existing Booking")
        print("3. Modify a Reservation")
        print("4. Cancel a booking")
        print("5. Exit Booking System")
        print(f"6. Account Settings{E}")
        while True:
            choice = input("Please enter your choice: ")
            if choice not in ['1', '2', '3', '4', '5', '6']:
                print(f"{R}Invalid input! Please try again!\n{E}")
                continue
            else:
                break
        if choice == '1':
            book_table(userid)
        elif choice == '2':
            view_booking(userid)
        elif choice == '3':
            modify_booking(userid)
        elif choice == '4':
            cancel_booking(userid)
        elif choice == '5':
            print("")
            for i in range(2):
                print("Exiting program...")
                time.sleep(1)
            return
        elif choice == '6':
            acc_settings(userid)


def book_table(userid):  # User Menu Choice 1
    today = datetime.today().date()
    max_date_str = cal_max_day()
    max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
    next_day = date.today() + timedelta(days=1)
    user_date = ""
    user_time = ""

    print(f"\nToday is {date.today()}, Last available date for making reservation: {cal_max_day()}.")
    while True:  # Get Date
        book_date = input("When do you want to make a reservation? (yyyy-mm-dd)")
        try:
            user_date = datetime.strptime(book_date, "%Y-%m-%d").date()
            if not (today < user_date <= max_date):
                if user_date == date.today():
                    print(f"{Y}Sorry! We do not accept same day reservation.{E}")
                    print("")
                    continue
                else:
                    print(f"{R}Invalid Input! The booking date must be between {next_day} and {cal_max_day()}\n{E}")
                    continue
        except ValueError:
            print(f"{R}Invalid Input! The format should be (yyyy-mm-dd) and must be a valid date!{E}")
            print("")
            continue
        break

    while True:  # Get Time
        print("What time would you like to make a reservation for?")
        book_time = input("You may book a table during 07:00-20:30")
        try:
            user_time = datetime.strptime(book_time, "%H:%M").time()
            open_time = datetime.strptime("07:00", "%H:%M").time()
            close_time = datetime.strptime("20:30", "%H:%M").time()
            if not (open_time <= user_time <= close_time):  # WaiWai's Restaurant open 07:00 and close at 21:00
                print(f"{R}\nError! Out of business time! We only accept reservation between 07:00 - 20:30!{E}")
                continue
            if user_time.minute not in [0, 30]:
                print(f"{R}\nError! You can only book at 30-minute intervals (e.g., 12:00, 12:30, 13:00).{E}")
                continue
        except ValueError:
            print(f"{R}Invalid Input! The format should be (HH:MM) and must be a valid time (in 24h format)!{E}")
            print("")
            continue
        break

    if user_date == "" or user_time == "":
        print(f"\n{R}Unexpected Error occurred, please restart the program and try again.")
        print(f"If the problem persists, contact our IT support.{E}")
        input("Press enter to exit:")
        exit(1)

    if check_duplicated_booking(userid, user_date, user_time):  # Check if user duplicated booking
        print(
            f"\n{Y}Sorry, you can't make a reservation on {user_date} at {book_time} since you already have a "
            f"reservation at that time.{E}")
        input("Press enter to return to menu.")
        return
    else:
        pass

    while True:  # Get group size
        book_num = input("How many people are the reservation for?")
        try:
            user_num = int(book_num)
        except ValueError:
            print(f"{R}Error! You have to input an integer!\n{E}")
            continue

        if user_num < 1 or user_num > 12:
            print(f"{R}Invalid group size. We only accept reservations for 1-12 people.\n{E}")
            continue

        if not check_availability(user_num, user_date, user_time):
            print(f"\n{Y}Sorry, there are no available tables for {book_num} people on {user_date}.{E}")
            ask = input(f"Would you like to wait for available table? (Y/N)")
            if ask not in ['Y', 'N', 'y', 'n']:
                input(f"{R}Invalid choice, your booking has been canceled{E}\nPress enter to return to menu:")
                return
            elif ask in ['N', 'n']:
                print("Thank you for using our service, press enter to return to the menu.")
                return
            elif ask in ['Y', 'y']:
                write_waiting_list(gen_unique_ubid(), user_num, user_date, userid, user_time)
                input("Press enter to proceed.")
                return
        else:
            print("\nFinal Confirm: Please check the following details carefully:")
            print(f"Booking date: {user_date}")
            print(f"Booking Time: {user_time}")
            print(f"Group size: {user_num} people")
            confirm = input("Press enter to confirm, '-2' for correction:")
            if confirm != '-2':
                write_booking(gen_unique_ubid(), userid, user_date, user_time, user_num)
                print(
                    f"\nReservation for {user_num} people has successfully booked for {user_date} at {user_time}. "
                    f"It's under the name {userid}.")
                input("Press Enter to return to menu: ")
                return
            else:
                correct_booking(gen_unique_ubid(), userid, user_date, user_time, user_num)
                return


def write_booking(ubid, userid, user_date, user_time, user_num):
    with open("BookingSy.txt", "a") as f:
        f.write(f"{ubid}, {userid}, {user_date}, {user_num}, {user_time}\n")


def correct_booking(ubid, userid, user_date, user_time, user_num):
    today = date.today()
    next_day = date.today() + timedelta(days=1)
    max_date_str = cal_max_day()
    max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
    new_user_date = user_date
    new_user_time = user_time
    new_user_num = user_num

    while True:
        print("\nWhat do you want to correct?")
        print("1. Date")
        print("2. Time")
        print("3. Group Size")
        dummy = input("Please type the number:")
        if dummy not in ['1', '2', '3']:
            print(f"{R}Error! Invalid input! Please try again!{E}")
            continue
        else:
            break
    if dummy == '1':
        print(f"Original Date: {user_date}")
        while True:
            new_book_date = input("\nPlease input new booking date in (yyyy-mm-dd)): ")
            try:
                new_user_date = datetime.strptime(new_book_date, "%Y-%m-%d").date()
            except ValueError:
                print(f"{R}Error! Invalid format! Please input in the format (yyyy-mm-dd)!{E}")
                continue
            if not (today < new_user_date <= max_date):
                if new_user_date == date.today():
                    print(f"{Y}Sorry! We do not accept same day reservation.\n{E}")
                    continue
                else:
                    print(f"{R}Invalid Input! The booking date must be between {next_day} and {cal_max_day()}\n{E}")
                    continue
            else:
                break

    if dummy == '2':
        print(f"Original Time: {user_time}")
        while True:
            new_book_time = input("\nPlease input new booking time in (HH:MM): ")
            try:
                new_user_time = datetime.strptime(new_book_time, "%H:%M").time()
                open_time = datetime.strptime("07:00", "%H:%M").time()
                close_time = datetime.strptime("20:30", "%H:%M").time()
                if not (open_time <= new_user_time <= close_time):  # WaiWai's Restaurant open 07:00 and close at 21:00
                    print(f"\n{R}Error! Out of business time! We only accept reservation between 07:00 - 20:30!{E}")
                    continue
                if new_user_time.minute not in [0, 30]:
                    print(f"\n{R}Error! You can only book at 30-minute intervals (e.g., 12:00, 12:30, 13:00).{E}")
                    continue
            except ValueError:
                print(f"{R}Invalid Input! The format should be (HH:MM) and must be a valid time (in 24h format)!{E}\n")
                continue
            break

    if dummy == '3':
        print(f"Original group size: {user_num}")
        while True:
            new_user_num = input("\nPlease input a number (1-12): ")
            try:
                new_user_num = int(new_user_num)
            except ValueError:
                print(f"\n{R}Error! You should enter a integer which is in the range 1-12!{E}")
                continue
            if new_user_num < 1 or new_user_num > 12:
                print(f"{R}The range of booking number is 1-12, please try again.{E}")
                continue
            break

    if (check_availability(new_user_num, new_user_date, new_user_time) and
            not check_duplicated_booking(userid, new_user_date, new_user_time)):

        corr_booking = []
        with open("BookingSy.txt", "r") as f:
            original = f.readlines()

        for book in original:
            corr_parts = book.strip().split(", ")
            if len(corr_parts) != 5:
                continue
            ori_ubid, ori_id, ori_date_str, ori_num_str, ori_time_str = corr_parts
            try:
                ori_date = datetime.strptime(ori_date_str, "%Y-%m-%d").date()
                ori_time = datetime.strptime(ori_time_str, "%H:%M:%S").time()
                ori_num = int(ori_num_str)
            except ValueError:
                continue
            if ori_id == userid and ori_date == user_date and ori_num == user_num and ori_time == user_time:
                continue
            else:
                corr_booking.append(book)

        with open("BookingSy.txt", "w") as f:
            f.writelines(corr_booking)
        write_booking(ubid, userid, new_user_date, new_user_time, new_user_num)
        print(
            f"\n{G}Reservation for {new_user_num} people has successfully"
            f" booked for {new_user_date} at {new_user_time}."
            f"It's under the name {userid}.{E}")
        input("Press Enter for menu: ")
        return
    else:
        print(f"\n{Y}Process aborted, it may because the booking on the requested date(time) was full, \n")
        print(f"or you already have a booking on the requested date(time).\n")
        print(f"If the problem persists, contact our IT support.{E}")
        input("Press enter to return to menu")
        return


def write_waiting_list(ubid, book_num, user_date, import_userid, user_time):
    try:
        book_num = int(book_num)
    except ValueError:
        print(f"\n{R}Unexpected Error occurred, please restart the program and try again.")
        print(f"If the problem persists, contact our IT support.{E}")
        input("Press enter to continue")
        return
    with open("WaitingList.txt", "r") as f:
        bookings = f.readlines()

    booked_count = 0
    max_tables = 0
    check_size = range(0)

    available_tables = {  # 30% of regular tables
        range(1, 5): max(1, math.floor(G1_4 * 0.3)),
        range(5, 9): max(1, math.floor(G5_8 * 0.3)),
        range(9, 13): max(1, math.floor(G9_12 * 0.3))
    }

    for group_size, tables in available_tables.items():
        if int(book_num) in group_size:
            check_size = group_size
            max_tables = tables
            break

    for booking in bookings:
        parts = booking.strip().split(", ")
        if len(parts) != 5:
            continue

        w_ubid, get_userid, booking_date, group_size_c, booking_time = parts
        try:
            booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            booking_time = datetime.strptime(booking_time, "%H:%M:%S").time()
            group_size_c = int(group_size_c)
        except ValueError:
            continue

        if booking_date == user_date and booking_time == user_time and group_size_c in check_size:
            booked_count += 1

    if booked_count < max_tables:
        with open("WaitingList.txt", "a") as f:
            f.write(f"{ubid}, {import_userid}, {user_date.strftime('%Y-%m-%d')}, {book_num}, {user_time}\n")
        print(
            f"{G}\nReservation for {book_num} people has successfully written into waiting list for "
            f"{user_date} at {user_time}. It's under the name {import_userid}.{E}")
        return
    else:
        print(f"{Y}Sorry, there are too much bookings at the requested date/time. Failed to add you to the waiting "
              f"list,"
              f"please try another date for your booking.{E}")
        return


def view_booking(userid):
    with open("BookingSy.txt", "r") as f:
        bookings = f.readlines()

    existing_bookings = []
    for booking in bookings:
        parts = booking.strip().split(", ")
        if len(parts) != 5:
            continue

        ubid, booking_id, booking_date, group_size, booking_time = parts
        try:
            booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            booking_time = datetime.strptime(booking_time, "%H:%M:%S").time()
            group_size = int(group_size)
        except ValueError:
            continue

        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

        month_final = booking_date.month

        for book_month, month_str in months.items():
            if booking_date.month == book_month:
                month_final = month_str
                break

        if booking_id == userid:
            existing_bookings.append(f"{booking_date.day} {month_final} {booking_date.year}: "
                                     f"Reservation for {group_size} people at {booking_time}.")

    if len(existing_bookings) > 0:
        print("\nYour existing bookings are:")
        for booking in existing_bookings:
            print(booking)
        input("Press enter to return to menu:")
        return
    else:
        print(f"\n{Y}No reservations found under your name.{E}")
        input("Press enter to return to menu:")
        return


def modify_booking(userid):
    edited_bookings = []
    while True:
        while True:
            modify_date = (
                input("\nPlease input the date(yyyy-mm-dd) of the booking that you want to modify:"))
            try:
                modify_date = datetime.strptime(modify_date, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Invalid date, please try again.\n")
                continue

        with open("BookingSy.txt", "r") as f:
            bookings = f.readlines()

        match_booking = []
        match_booking_user = []
        match_modify = 0
        for booking in bookings:
            parts = booking.strip().split(", ")
            if len(parts) != 5:
                continue
            ubid, modify_userid, modify_user_date, modify_num, modify_time = parts

            try:
                modify_user_date = datetime.strptime(modify_user_date, "%Y-%m-%d").date()
                modify_time = datetime.strptime(modify_time, "%H:%M:%S").time()
            except ValueError:
                continue

            months = {
                1: "January",
                2: "February",
                3: "March",
                4: "April",
                5: "May",
                6: "June",
                7: "July",
                8: "August",
                9: "September",
                10: "October",
                11: "November",
                12: "December"
            }
            modify_time_str = modify_time
            month_final = modify_user_date.month

            for book_month, month_str in months.items():
                if modify_user_date.month == book_month:
                    month_final = month_str
                    break

            if modify_userid == userid and modify_user_date == modify_date:
                match_modify += 1
                match_booking.append(f"{ubid}, {userid}, {modify_user_date}, {modify_num}, {modify_time}")
                match_booking_user.append(f"{modify_user_date.day} {month_final} {modify_user_date.year}: "
                                          f"Reservation for {modify_num} people at {modify_time_str}.")

        if match_modify == 0:
            print(f"{Y}No bookings found at that day, please try again.{E}")
            input("Please press enter to continue:")
            continue
        else:
            print("\nYour bookings on requested date:")
            for i in match_booking_user:
                print(i)
        break

    correct = False
    while True:
        modify_time_str = input("Enter the time of the booking that you want to modify (HH:MM) ('-2' to exit): ")
        if modify_time_str.strip() == '-2':
            return
        try:
            k_modify_time = datetime.strptime(modify_time_str, "%H:%M").time()
            for booking in match_booking:
                parts1 = booking.strip().split(", ")
                if len(parts1) != 5:
                    continue
                ubid1, _, _, _, k_time_str = parts1
                try:
                    k_time = datetime.strptime(k_time_str, "%H:%M:%S").time()
                except ValueError:
                    continue
                if k_time == k_modify_time:
                    correct = True
                    break
            if correct:
                break
            else:
                print(f"{R}Time inputted is invalid, please try again.{E}")
        except ValueError:
            print(f"{R}Invalid time format! Please try again.\n{E}")
            continue

    print("\nWhat would you like to modify?")
    print("1. Booking Date")
    print("2. Booking Time")
    print("3. Group Size")

    while True:
        choice = input("Enter your choice (1-3): ")
        if choice in ['1', '2', '3']:
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.\n")

    new_date = modify_date
    new_time = k_modify_time

    if choice == '1':
        print("")
        today = datetime.today().date()
        max_date_str = cal_max_day()
        max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
        while True:
            new_date_str = input("Enter the new date (yyyy-mm-dd): ")
            try:
                new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"{R}Invalid date format! Please try again.\n{E}")
                continue

            if not (today < new_date <= max_date):
                if new_date == date.today():
                    print(f"{Y}Sorry! We do not accept same day reservation.\n{E}")
                    continue
                else:
                    print(
                        f"{R}Invalid Input! The date must be greater than {date.today()} and less than "
                        f"{cal_max_day()}!\n{E}")
                    continue
            break

    elif choice == '2':
        print("")
        open_time = datetime.strptime("07:00", "%H:%M").time()
        close_time = datetime.strptime("20:30", "%H:%M").time()
        while True:
            new_time_str = input("Enter the new time (HH:MM): ")
            try:
                new_time = datetime.strptime(new_time_str, "%H:%M").time()
            except ValueError:
                print(f"{R}Invalid time format! Please try again.\n{E}")
                continue

            if not (open_time <= new_time <= close_time):  # WaiWai's Restaurant open 07:00 and close at 21:00
                print(f"\n{R}Error! Out of business time! We only accept reservation between 07:00 - 20:30!{E}")
                continue
            if new_time.minute not in [0, 30]:
                print(f"\n{R}Error! You can only book at 30-minute intervals (e.g., 12:00, 12:30, 13:00).{E}")
                continue
            break

    print("")
    while True:
        new_group_size = input("Enter the new group size (1-12): ")
        if new_group_size.isdigit():
            new_group_size = int(new_group_size)
            if 1 <= new_group_size <= 12:
                break
        print(f"{R}Invalid group size. Please enter a number between 1 and 12.\n{E}")

    for k in bookings:
        parts = k.strip().split(", ")
        if len(parts) != 5:
            continue

        ubid2, booking_id, booking_date_str, _, booking_time_str = parts

        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            booking_time = datetime.strptime(booking_time_str, "%H:%M:%S").time()
        except ValueError:
            continue

        if booking_id == userid and booking_date == modify_date and booking_time == k_modify_time:
            if check_duplicated_booking(userid, new_date, new_time):
                print(f"\n{Y}You already have a booking at the requested date and time, modification failed.{E}")
                input("Press enter to continue:")
                return
            if not check_availability(new_group_size, new_date, new_time):
                print(
                    f"\n{Y}Sorry, the modification requested has failed, "
                    f"we don't have enough table at the requested date and time.{E}")
                input("Press enter to continue:")
                return
            edited_bookings.append(
                f"{ubid2}, {userid}, {new_date.strftime('%Y-%m-%d')}, {new_group_size}, "
                f"{new_time.strftime('%H:%M:%S')}\n"
            )
        else:
            edited_bookings.append(k)

    with open("BookingSy.txt", "w") as f:
        f.writelines(edited_bookings)

    print(f"\n{G}Your booking has been successfully modified.{E}")
    input("Press Enter to continue.")
    return


def cancel_booking(userid):
    while True:
        edited_bookings = []
        while True:
            cancel_date = input("\nPlease input the date(yyyy-mm-dd) that you want to cancel ('-2' to exit):")
            if cancel_date == '-2':
                return
            try:
                cancel_date = datetime.strptime(cancel_date, "%Y-%m-%d").date()
                break
            except ValueError:
                print(f"{R}Invalid date format! Please enter in yyyy-mm-dd.{E}")
                continue

        with open("BookingSy.txt", "r") as f:
            original_bookings = f.readlines()

        match_booking = []
        match_booking_user = []
        match_cancel = 0
        for booking in original_bookings:
            parts = booking.strip().split(", ")
            if len(parts) != 5:
                continue
            cancel_ubid, cancel_userid, cancel_user_date, cancel_num, cancel_time = parts

            try:
                cancel_user_date = datetime.strptime(cancel_user_date, "%Y-%m-%d").date()
                cancel_time = datetime.strptime(cancel_time, "%H:%M:%S").time()
            except ValueError:
                continue

            months = {
                1: "January",
                2: "February",
                3: "March",
                4: "April",
                5: "May",
                6: "June",
                7: "July",
                8: "August",
                9: "September",
                10: "October",
                11: "November",
                12: "December"
            }
            cancel_time_str = cancel_time
            month_final = cancel_user_date.month

            for book_month, month_str in months.items():
                if cancel_user_date.month == book_month:
                    month_final = month_str
                    break

            if cancel_userid == userid and cancel_user_date == cancel_date:
                match_cancel += 1
                match_booking.append(f"{cancel_ubid}, {userid}, {cancel_user_date}, {cancel_num}, {cancel_time}")
                match_booking_user.append(f"{cancel_user_date.day} {month_final} {cancel_user_date.year}: "
                                          f"Reservation for {cancel_num} people at {cancel_time_str}.")

        if match_cancel == 0:
            print(f"{Y}No bookings found at that day, please try again.{E}")
            input("Please press enter to continue:")
            continue
        else:
            final_cancel_time = ""
            print("\nYour bookings on requested date:")
            for booking in match_booking_user:
                print(booking)
            while True:
                final_cancel_time_r = input(
                    "Please input the time of the booking which you want to cancel (HH:MM)('-2' to "
                    "exit):")
                if final_cancel_time_r == '-2':
                    return
                try:
                    final_cancel_time = datetime.strptime(final_cancel_time_r, "%H:%M").time()
                    break
                except ValueError:
                    print(f"{R}Invalid time! Please try again.{E}")
                    continue

            final_c_ubid = None
            with open("BookingSy.txt", "r") as f:
                c1_all_bookings = f.readlines()
            for c1 in c1_all_bookings:
                c1_parts = c1.strip().split(", ")
                if len(c1_parts) != 5:
                    continue
                c1_ubid, c1_userid, c1_booking_date, c1_group_num, c1_booking_time = c1_parts
                try:
                    c1_booking_date_ok = datetime.strptime(c1_booking_date, "%Y-%m-%d").date()
                    c1_booking_time_ok = datetime.strptime(c1_booking_time, "%H:%M:%S").time()
                except ValueError:
                    continue
                if (c1_booking_date_ok == cancel_date and c1_booking_time_ok == final_cancel_time
                        and c1_userid == userid):
                    final_c_ubid = c1_ubid
            if final_c_ubid is None:
                print(f"{R}Error! No booking exist at the requested time! Cancellation aborted.{E}")
                input("Press enter to return to menu")
                return

            for booking in match_booking:
                parts = booking.strip().split(", ")
                ubid, cancel_userid, cancel_user_date, cancel_num, cancel_time = parts
                try:
                    cancel_time = datetime.strptime(cancel_time, "%H:%M:%S").time()
                except ValueError:
                    continue
                if cancel_time == final_cancel_time:
                    with open("BookingSy.txt", "r") as f:
                        all_bookings = f.readlines()

                    for k in all_bookings:
                        parts = k.strip().split(", ")
                        if len(parts) != 5:
                            continue

                        book_ubid, booking_id, booking_date_str, group_size, booking_time_str = parts
                        try:
                            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
                            booking_time = datetime.strptime(booking_time_str, "%H:%M:%S").time()
                            group_size = int(group_size)
                        except ValueError:
                            continue

                        if booking_id == userid and booking_date == cancel_date and booking_time == final_cancel_time:
                            continue
                        else:
                            edited_bookings.append(
                                f"{book_ubid}, {booking_id}, {booking_date.strftime('%Y-%m-%d')}, {group_size}"
                                f", {booking_time.strftime('%H:%M:%S')}\n")

            confirm = input(
                f"Are you sure you want to cancel your booking on {cancel_date} at {final_cancel_time}? (Y/N): ")
            if confirm not in ['Y', 'y']:
                print(f"{Y}Cancellation aborted.{E}")
                input("Press enter to continue")
                return
            with open("BookingSy.txt", "w") as f:
                f.writelines(edited_bookings)
            print(f"\n{G}Booking has been successfully canceled.{E}")
            input("Press Enter to continue")
            return


def acc_settings(userid):
    star = ""
    login = False
    while True:
        pw = input("\nType your password to continue: ('-2' to exit)")
        if pw == '-2':
            return
        with open("Account.txt", "r") as f:
            for line in f:
                try:
                    stored_user, stored_pw, stored_phone = line.strip().split(", ")
                except ValueError:
                    continue
                if stored_user == userid and stored_pw == pw:
                    user_pw = stored_pw
                    user_phone = stored_phone
                    login = True
                    break
        if not login:
            print(f"{Y}Wrong password, please try again.{E}")
        else:
            break

    print("\nYour account details: ")
    print(f"UserID (unchangeable): {userid}")
    for i in range(len(user_pw)):
        star += "*"
    print(f"Password: {star}")
    print(f"Phone Number: {user_phone}")
    next_step = input("If you want to change your password/phone number, enter '-3'. "
                      "Press enter to return to the menu.")
    if next_step == '-3':
        while True:
            print("")
            print("1. Change password")
            print("2. Change phone number")
            choice = input("Enter your choice:")
            if choice not in ['1', '2']:
                print(f"{Y}Error! You should enter '1' or '2'!{E}")
                continue
            else:
                break
        new_phone = user_phone
        new_pw = user_pw
        if choice == '1':
            while True:
                new_pw = input("\nType a new password for your account: ")
                check_new_pw_space = new_pw.find(" ")
                check_new_pw_comma = new_pw.find(",")
                if check_new_pw_space != -1 or check_new_pw_comma != -1:
                    print(f"{Y}Warning! No space or comma (,) is allowed!\n{E}")
                    input("Press enter to try again.")
                    continue
                if new_pw == user_pw:
                    print(f"{Y}Error! It's same with the original password!\n{E}")
                    continue
                check_pw = input("Please type your password again: ")
                if check_pw != new_pw:
                    print(f"{Y}Passwords do not match, please try again.{E}")
                    print("")
                    continue
                else:
                    break
        elif choice == '2':
            while True:
                new_phone = input("\nPlease input your new phone number: ")
                if new_phone == user_phone:
                    print(f"{Y}Error! It's same with the original phone number!\n{E}")
                    continue
                if len(new_phone) != 8 or not new_phone.isdigit():
                    print(f"{Y}Error! You have to input an 8-digit valid HK phone number!{E}")
                    continue
                if new_phone[0] in ['4', '5', '6', '7', '8', '9']:
                    break
                else:
                    print(f"{Y}Error! Your phone number should start with [4, 5, 6, 7, 8, 9]!{E}")
                    continue

        new_acc = []
        with open("Account.txt", "r") as f:
            acc = f.readlines()
        for A in acc:
            parts = A.strip().split(", ")
            if len(parts) != 3:
                continue
            e_id, e_pw, e_num = parts
            if e_id == userid and e_pw == user_pw and e_num == user_phone:
                pass
            else:
                new_acc.append(f"{e_id}, {e_pw}, {e_num}\n")

        with open("Account.txt", "w") as f:
            f.writelines(new_acc)
            f.write(f"{userid}, {new_pw}, {new_phone}\n")
        print(f"\n{G}Account modification complete! Press enter to continue.{E}")
        return

    else:
        return


def print_msg(userid):
    with open("PushMsg.txt", "r") as f:
        total_msg = f.readlines()
    msg_to_be_sent = []
    new_push_msg = []
    for msg in total_msg:
        parts = msg.strip().split(", ")
        if len(parts) != 2:
            continue
        receiver, msg_content = parts
        if userid == receiver:
            msg_to_be_sent.append(msg_content)
        else:
            new_push_msg.append(msg)
    if len(msg_to_be_sent) > 0:
        print("\nNew message(s) received! Please Check:")
        for msg1 in msg_to_be_sent:
            print(msg1)
    else:
        print("\nNo new messages received")
    input("Press enter to proceed.")
    with open("PushMsg.txt", "w") as f:
        f.writelines(new_push_msg)
    booking_system(userid)


def write_push_msg(userid, content):
    with open("PushMsg.txt", "a") as f:
        ensure = str(content).replace("\n", " ").replace(",", "，")
        # Make sure the content will not make error
        f.write(f"{userid}, {ensure}\n")


start_screen()
