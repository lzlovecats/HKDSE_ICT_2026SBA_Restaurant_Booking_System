# Instruction to markers:
# Please ensure all the text files are saved under the same folder before running.
# Please fully extract all the files from the zip file.
# ** You are strongly advised to use VS Code to run this program for better experience.
# ** https://code.visualstudio.com/
# Please ONLY open the folder storing this program in the IDE,
# DO NOT open the folder as a sub-folder in another folder, or run-time errors might occur.

# Admin UserID: LoveWaiWai, PW: iWANT5**

import os.path
import sys
import tkinter as tk
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import ttk, messagebox, scrolledtext
import random
import string
import math

G9_12 = 30  # Default Table Number
G5_8 = 20
G1_4 = 10
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
            except ValueError:  # If format error, means the booking will not be considerd valid, skip it
                continue
            if booking_date >= date.today():  # Check the booking date, if less than today, skip it
                delete_old_booking.append(
                    f"{ubid}, {userid}, {booking_date.strftime('%Y-%m-%d')}, {booking_num}, {booking_time}\n")
            else:
                continue
    with open("BookingSy.txt", "w") as f:
        f.writelines(delete_old_booking)


def check_environment():  # Check if the program can run successfully
    if sys.version_info < (3, 10):  # Should have Python 3.10 or above
        try:
            messagebox.showerror("Environment Incompatible",
                                 "This program requires Python 3.10 or above.\nPlease update your Python version or "
                                 "use CLI mode.")
        finally:
            sys.exit(1)

    try:
        check_tk = tk.Tk()
        tk_patchlevel = check_tk.call("info", "patchlevel")  # Check if tk available
        check_tk.destroy()
    except Exception as err:  # When tk.Tk can't be created, or can't get the info of tk.Tk
        try:
            messagebox.showerror("Tk not available", f"Tkinter could not start.\nError Details: {err}")  # Try if graphical window can be shown
        except Exception:  # If tk.Tk really can't run
            sys.stderr.write(f"Tk not available: {err}\n")  # using sys to ensure the error msg is printed in the Terminal
        finally:
            sys.exit(1)  # Whatever GUI shown or not, use sys to exit the program, prevent the user destory

    try:
        # Get the first two info of tk_patchlevel, for each data, int() it and write into major and minor
        major, minor, *_ = [int(x) for x in tk_patchlevel.split(".")]  
        if (major, minor) < (8, 6):  # Minimum requirement of Tk Version >= 8.6
            sure = messagebox.askyesno("Environment Incompatible",
                                       f"Detected Tk Version: {tk_patchlevel}. Required Tk 8.6 or above.\nYou may "
                                       f"still to continue, however unexpected errors may occurred.\nContinue?")
            if sure:
                pass
            else:
                sys.exit(1)
    except Exception:
        pass  # It is okay that cannot get the version details


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
            write_push_msg(f"{userid}", f"Your booking on {booking_date} has been confirmed. "
                                        f"Check details on Booking Menu Option 2.")
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
            except ValueError:
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

    if max_tables == 0 or check_size == 0:
        messagebox.showerror("Unexpected Error occurred.",
                             "Unexpected Error occurred, please restart the program."
                             "\n\nIf the problem persists, contact our IT support.") ; return False

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


def write_booking(ubid, userid, user_date, user_time, user_num):
    with open("BookingSy.txt", "a") as f:
        f.write(f"{ubid}, {userid}, {user_date}, {user_num}, {user_time}\n")


def write_waiting_list(ubid, book_num, user_date, import_userid, user_time):
    try:
        book_num = int(book_num)
    except ValueError:
        messagebox.showerror("Unexpected Error occurred.",
                             "Unexpected Error occurred, please restart the program and try again."
                             "\nIf the problem persists, contact our IT support.")
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
        messagebox.showinfo("Added to waiting list.",
                            f"Reservation for {book_num} people has successfully written into waiting list for "
                            f"{user_date} at {user_time}.\nIt's under the name {import_userid}.")
        return
    else:
        messagebox.showerror("No table.", "Sorry! There are too much bookings at the requested date/time."
                                          "\nFailed to add you to the waiting list,\n"
                                          "please try another date for your booking.")
        return


def write_push_msg(userid, content):
    with open("PushMsg.txt", "a") as f:
        ensure = str(content).replace("\n", " ").replace(",", "，")
        # Make sure the content will not make error
        f.write(f"{userid}, {ensure}\n")


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WaiWai's Restaurant Booking System GUI Version")
        self.resizable(False, False)
        self.geometry("900x556")  # Window size ratio = 1:phi
        base_path = Path(__file__).resolve().parent
        self.current_user = None
        os.chdir(base_path)  # Set the default path as same as the folder storing this program

        self.pages = {"LoginPage": LoginPage(self, controller=self),
                      "ManagementPage": ManagementPage(self, controller=self),
                      "BookingPage": BookingPage(self, controller=self),
                      "CreateAccount": CreateAccount(self, controller=self)}

        files = {  # check_files_exist()
            "Account.txt": os.path.isfile("Account.txt"),
            "BookingSy.txt": os.path.isfile("BookingSy.txt"),
            "MaxDate.txt": os.path.isfile("MaxDate.txt"),
            "WaitingList.txt": os.path.isfile("WaitingList.txt"),
            "Tables.txt": os.path.isfile("Tables.txt"),
            "PushMsg.txt": os.path.isfile("PushMsg.txt")
        }
        if not all(files.values()):
            choice = messagebox.askyesno(
                "Missing program files",
                "Some required files are missing.\n\nCreate the missing files now and continue?"
            )
            if choice:
                for f_name, status in files.items():
                    if not status:
                        try:
                            open(f_name, "x").close()  # Only create missing files
                        except FileExistsError:
                            pass
                        except OSError as infor:
                            messagebox.showerror("災難性的失敗！", f"Error information: {infor}")
                            exit(444)
            else:
                exit(404)

        read_table_num()
        delete_old_bookings()
        update_waiting_list()

        self.show_page("LoginPage")
        self.after(150, self.activate_window)  # Get focus
        self.bind("<Map>", lambda e: self.after(50, self.activate_window))  # When cursor move or keyboard click

    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        p = self.pages[page_name]
        p.pack(fill="both", expand=True)
        self.focus_force()
        try:
            p.refresh_data()
        except AttributeError:
            pass
        try:
            p.focus_first()
        except AttributeError:
            pass

    def activate_window(self):
        self.lift()
        self.focus_force()

    def reload_page(self, page_name):  # For ManagementPage/CreateAccount to re-build itself
        old = self.pages.get(page_name)
        if old is not None:
            try:
                old.destroy()
            except Exception:
                pass

        if page_name == "ManagementPage":
            self.pages["ManagementPage"] = ManagementPage(self, controller=self)
        elif page_name == "CreateAccount":
            self.pages["CreateAccount"] = CreateAccount(self, controller=self)

        self.show_page(page_name)


class LoginPage(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        login_page_label = ttk.Label(form, text="WaiWai's Restaurant Login Page", font=("Times New Roman", 20))
        userid_label = ttk.Label(form, text="UserID", font=("Arial", 16, "bold"))
        user_pw_label = ttk.Label(form, text="Password", font=("Arial", 16, "bold"))
        cre_acc_label = ttk.Label(form, text="Don't have a account?", font=("Arial", 14))

        self.userid = tk.StringVar()
        self.user_pw = tk.StringVar()

        self.userid_entry = ttk.Entry(form, textvariable=self.userid)
        self.userid_entry.focus_set()  # Cursor default at UserID box
        self.password_entry = ttk.Entry(form, textvariable=self.user_pw, show="*")
        self.submit_btn = ttk.Button(form, text="Login", command=self.get_id_pw, width=35)
        self.cre_acc_btn = ttk.Button(form, text="Create Account", command=self.go_to_cre_acc)

        login_page_label.grid(row=0, columnspan=2, pady=36)
        userid_label.grid(row=1, column=0)
        user_pw_label.grid(row=2, column=0)
        self.userid_entry.grid(row=1, column=1)
        self.password_entry.grid(row=2, column=1)
        self.submit_btn.grid(row=4, columnspan=2, pady=6)
        cre_acc_label.grid(row=5, column=0, pady=10)
        self.cre_acc_btn.grid(row=5, column=1, pady=10)

        self.userid_entry.bind("<Return>", self.focus_at_pw)
        self.password_entry.bind("<Return>", self.get_id_pw)

    def go_to_cre_acc(self):
        self.controller.show_page("CreateAccount")
        self.controller.pages["CreateAccount"].refresh_data()

    def focus_at_pw(self, event=None):
        self.password_entry.focus_set()

    def get_id_pw(self, event=None):
        self.submit_btn.state(["disabled"])

        userid = self.userid_entry.get()
        user_pw = self.password_entry.get()
        if not userid or not user_pw:
            messagebox.showwarning("Missing Info", "UserID or Password is missing, please try again.")
            self.submit_btn.state(["!disabled"])
            return

        userid_matched = False
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
            messagebox.showwarning("User Not Found", "Inputted UserID does not exist, please try again.")
            self.submit_btn.state(["!disabled"])
            return

        if userid == 'LoveWaiWai' and user_pw == 'iWANT5**':  # Admin Mode
            self.controller.show_page("ManagementPage")
            self.submit_btn.state(["!disabled"])
            return

        login_success = False
        with open("Account.txt", "r") as f:
            for line in f:
                try:
                    stored_user, stored_pw, _ = line.strip().split(", ")
                except ValueError:
                    continue
                if userid == stored_user and user_pw == stored_pw:
                    login_success = True
                    break
        if not login_success:
            messagebox.showwarning("Login Failed", "UserID or Password is not correct, please try again.")
            self.submit_btn.state(["!disabled"])
            return

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
        if msg_to_be_sent:
            all_msgs = "\n\n".join(msg_to_be_sent)
            messagebox.showinfo("New message(s) received", f"Please check the following message(s):\n\n{all_msgs}")
        else:
            pass
        with open("PushMsg.txt", "w") as f:
            f.writelines(new_push_msg)

        self.submit_btn.state(["!disabled"])
        self.controller.current_user = userid
        self.controller.show_page("BookingPage")

    def clear_fields(self):
        try:
            self.userid.set("")
            self.user_pw.set("")
        except Exception:
            pass
        try:
            self.userid_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        except Exception:
            pass
        try:
            self.submit_btn.state(["!disabled"])  # ensure clickable
        except Exception:
            pass
        try:
            self.userid_entry.focus_set()
        except Exception:
            pass

    def focus_first(self):
        try:
            self.userid_entry.focus_set()
        except Exception:
            pass


class ManagementPage(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.form = ttk.Frame(self)
        self.form.grid(row=0, column=0)
        self.G9_12_var = tk.StringVar(value=str(G9_12))
        self.G5_8_var = tk.StringVar(value=str(G5_8))
        self.G1_4_var = tk.StringVar(value=str(G1_4))

        self.title_label = ttk.Label(self.form, text="WaiWai's Restaurant Booking System",
                                font=("Times New Roman", 22))
        self.sub_title_label = ttk.Label(self.form, text="Restaurant Keeper Management Page", font=("Times New Roman", 22))
        self.op1_btn = ttk.Button(self.form, text="1. Change the number of tables", width=35, command=self.op1)
        self.op2_btn = ttk.Button(self.form, text="2. View All Registered Accounts", width=35, command=self.op2)
        self.op3_btn = ttk.Button(self.form, text="3. Backup all the bookings", width=35, command=self.op3)
        self.op4_btn = ttk.Button(self.form, text="4. Recover all the bookings", width=35, command=self.op4)
        self.op5_btn = ttk.Button(self.form, text="5. View all the bookings", width=35, command=self.op5)
        self.op6_btn = ttk.Button(self.form, text="6. Delete booking with UBID", width=35, command=self.op6)
        self.op7_btn = ttk.Button(self.form, text="7. Find booking details with UBID", width=35, command=self.op7)
        self.op8_btn = ttk.Button(self.form, text="8. Push msg to customer", width=35, command=self.op8)
        self.op9_btn = ttk.Button(self.form, text="9. Find bookings for a specific day", width=35, command=self.op9)
        self.op10_btn = ttk.Button(self.form, text="10. Show recent statistics", width=35, command=self.op10)
        self.return_btn = ttk.Button(self.form, text=" ← Exit Management System", width=35, command=self.logout)

        self.title_label.grid(row=0, columnspan=2)
        self.sub_title_label.grid(row=1, columnspan=2, pady=(0, 10))
        self.op1_btn.grid(row=2, column=0)
        self.op2_btn.grid(row=2, column=1)
        self.op3_btn.grid(row=3, column=0)
        self.op4_btn.grid(row=3, column=1)
        self.op5_btn.grid(row=4, column=0)
        self.op6_btn.grid(row=4, column=1)
        self.op7_btn.grid(row=5, column=0)
        self.op8_btn.grid(row=5, column=1)
        self.op9_btn.grid(row=6, column=0)
        self.op10_btn.grid(row=6, column=1)
        self.return_btn.grid(row=7, columnspan=2, pady=5)

    def op1(self):
        read_table_num()
        self.G9_12_var.set(str(G9_12))
        self.G5_8_var.set(str(G5_8))
        self.G1_4_var.set(str(G1_4))

        instruction_label = ttk.Label(self.form, text="Number of Tables: (Not recommended to change)", font=("Times New Roman", 22))
        G9_12_label = ttk.Label(self.form, text="Group Size 9-12", font=("Arial", 16, "bold"))
        G5_8_label = ttk.Label(self.form, text="Group Size 5-8", font=("Arial", 16, "bold"))
        G1_4_label = ttk.Label(self.form, text="Group Size 1-4", font=("Arial", 16, "bold"))
        self.G9_12_entry = ttk.Entry(self.form, textvariable=self.G9_12_var)
        self.G5_8_entry = ttk.Entry(self.form, textvariable=self.G5_8_var)
        self.G1_4_entry = ttk.Entry(self.form, textvariable=self.G1_4_var)
        edit_btn = ttk.Button(self.form, text="Edit", command=self.op1_1)
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)

        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()

        instruction_label.grid(row=0, columnspan=2, pady=(0, 10))
        G9_12_label.grid(row=1, column=0)
        self.G9_12_entry.grid(row=1, column=1)
        G5_8_label.grid(row=2, column=0)
        self.G5_8_entry.grid(row=2, column=1)
        G1_4_label.grid(row=3, column=0)
        self.G1_4_entry.grid(row=3, column=1)
        return_btn.grid(row=4, column=0, pady=(5, 0))
        edit_btn.grid(row=4, column=1, pady=(5, 0))

        self.G9_12_entry.bind("<Return>", self.op1_f1)
        self.G5_8_entry.bind("<Return>", self.op1_f2)
        self.G1_4_entry.bind("<Return>", self.op1_1)

    def op2(self):
        acc_list = []

        with open("Account.txt", "r") as f:
            for line in f:
                parts = line.strip().split(", ")
                if len(parts) != 3:
                    continue
                else:
                    userid, password, phone = parts
                    acc_list.append(f"UserID: '{userid}', Phone: {phone}")
        acc_text_str = "\n".join(acc_list)  # .join is a very useful function

        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()

        try:  # Only for management op2
            self.form.rowconfigure(1, weight=1)
            self.form.columnconfigure(0, weight=1)
        except Exception:
            pass

        acc_text = scrolledtext.ScrolledText(self.form, wrap="word", font=("Arial", 15), height=12)
        acc_text.insert("1.0", acc_text_str if acc_text_str else "<Accounts not found>")
        acc_text.configure(state="disabled")  # To make it read-only

        op2_label = ttk.Label(self.form, text="Account Details:", font=("Times New Roman", 22))
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)

        op2_label.grid(row=0, column=0, pady=(0, 10))
        acc_text.grid(row=1, column=0)
        return_btn.grid(row=2, column=0)

        return

    def op3(self):
        with open("BookingSy.txt", "r") as f:
            backup = f.read()
        with open("Backup_BookingSy.txt", "w") as f:
            f.write(backup)
        messagebox.showinfo("Backup completed.", "Backup completed, the backup files is stored in 'Backup_BookingSy.txt'.")
        return

    def op4(self):
        try:
            with open("Backup_BookingSy.txt", "r") as f:
                backup = f.read()
        except FileNotFoundError:
            messagebox.showerror("No back up file found.", "No back up file found, you should do a backup first.")
            return
        with open("BookingSy.txt", "w") as f:
            f.write(backup)
        messagebox.showinfo("Recover completed.", "Recover completed.")
        return

    def op5(self):
        book_list = []

        with open("BookingSy.txt", "r") as f:
            for line in f:
                parts = line.strip().split(", ")
                if len(parts) != 5:
                    continue
                else:
                    ubid, b_userid, book_date, book_size, book_time = parts
                    try:
                        book_date = datetime.strptime(book_date, "%Y-%m-%d").date()
                        book_time = datetime.strptime(book_time, "%H:%M:%S").time()
                        book_size = int(book_size)
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
                    month_final = book_date.month
                    for book_month, month_str in months.items():
                        if book_date.month == book_month:
                            month_final = month_str
                            break
                    book_list.append(f"{ubid}:  "
                                             f"Reservation for {book_size} people at {book_time} on"
                                             f" {book_date.day} {month_final} {book_date.year}"
                                             f" under the name '{b_userid}'.")

        if len(book_list) > 0:
            book_text_str = "\n".join(book_list)
        else:
            book_text_str = "<No bookings found.>"

        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()

        try:  # Only for management op5
            self.form.rowconfigure(1, weight=1)
            self.form.columnconfigure(0, weight=1)
        except Exception:
            pass

        book_text = scrolledtext.ScrolledText(self.form, wrap="word", font=("Arial", 15), height=12)
        book_text.insert("1.0", book_text_str)
        book_text.configure(state="disabled")  # To make it read-only

        op5_label = ttk.Label(self.form, text="Bookings Details:", font=("Times New Roman", 22))
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)

        op5_label.grid(row=0, column=0, pady=(0, 10))
        book_text.grid(row=1, column=0)
        return_btn.grid(row=2, column=0)

    def op6(self):
        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()

        self.tbd_ubid = tk.StringVar()  # tbd means to be deleted
        instruction_label = ttk.Label(self.form, text="Input the ubid of the booking you would like to cancel",
                                      font=("Times New Roman", 22))
        ubid_label = ttk.Label(self.form, text="UBID", font=("Arial", 16, "bold"))
        ubid_entry = ttk.Entry(self.form, textvariable=self.tbd_ubid)
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)
        delete_btn = ttk.Button(self.form, text="Delete", command=self.op6_1)

        instruction_label.grid(row=0, columnspan=2, pady=(0, 10))
        ubid_label.grid(row=1, column=0)
        ubid_entry.grid(row=1, column=1)
        return_btn.grid(row=2, column=0, pady=(5,0))
        delete_btn.grid(row=2, column=1, pady=(5,0))

    def op7(self):
        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()

        self.tbf_ubid = tk.StringVar()  # tbf means to be found
        instruction_label = ttk.Label(self.form, text="Input the ubid of the booking you would like to find",
                                      font=("Times New Roman", 22))
        ubid_label = ttk.Label(self.form, text="UBID", font=("Arial", 16, "bold"))
        ubid_entry = ttk.Entry(self.form, textvariable=self.tbf_ubid)
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)
        find_btn = ttk.Button(self.form, text="Find", command=self.op7_1)

        instruction_label.grid(row=0, columnspan=2, pady=(0, 10))
        ubid_label.grid(row=1, column=0)
        ubid_entry.grid(row=1, column=1)
        return_btn.grid(row=2, column=0, pady=(5, 0))
        find_btn.grid(row=2, column=1, pady=(5, 0))

    def op8(self):
        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()

        self.msg_uid = tk.StringVar()
        self.msg_contect = tk.StringVar()
        instruction_label = ttk.Label(self.form, text="Send message to customer",
                                      font=("Times New Roman", 22))
        uid_label = ttk.Label(self.form, text="UserID", font=("Arial", 16, "bold"))
        self.uid_entry = ttk.Entry(self.form, textvariable=self.msg_uid)
        msg_label = ttk.Label(self.form, text="Message", font=("Arial", 16, "bold"))
        self.msg_entry = ttk.Entry(self.form, textvariable=self.msg_contect)
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)
        send_btn = ttk.Button(self.form, text="Send", command=self.op8_1)

        instruction_label.grid(row=0, columnspan=2, pady=(0, 10))
        uid_label.grid(row=1, column=0)
        self.uid_entry.grid(row=1, column=1)
        msg_label.grid(row=2, column=0)
        self.msg_entry.grid(row=2, column=1)
        return_btn.grid(row=3, column=0, pady=(5, 0))
        send_btn.grid(row=3, column=1, pady=(5, 0))

        self.uid_entry.bind("<Return>", self.op8_f1)
        self.msg_entry.bind("<Return>", self.op8_1)

    def op1_1(self, event=None):
        new_G9_12 = self.G9_12_entry.get()
        new_G5_8 = self.G5_8_entry.get()
        new_G1_4 = self.G1_4_entry.get()

        try:
            new_G9_12 = int(new_G9_12)
            new_G5_8 = int(new_G5_8)
            new_G1_4 = int(new_G1_4)
        except ValueError:
            messagebox.showerror("Invalid input.", "Error! You should input integers!")
            return

        if new_G9_12 < G9_12 or new_G5_8 < G5_8 or new_G1_4 < G1_4:
            really = messagebox.askyesno("Smaller then original one.",
                                "Warning! new number(s) are smaller than the original one!"
                                "\nExisting bookings will not be affected,"
                                "\nif you want to delete them,\nchoose option 7 in the menu."
                                "\n\nAre you sure to continue?")
            if not really:
                messagebox.showinfo("Process end.", "Process aborted, press OK to continue:")
                return

        if new_G9_12 == G9_12 and new_G5_8 == G5_8 and new_G1_4 == G1_4:
            messagebox.showerror("Same numbers.", "You have not edited anything yet!")
            return

        with open("Tables.txt", "w") as f:
            f.write(f"{new_G9_12}, {new_G5_8}, {new_G1_4}")
        read_table_num()
        messagebox.showinfo("Edit success.", "New number saved. Press OK to return to menu.")
        update_waiting_list()
        self.G9_12_var.set(str(G9_12))
        self.G5_8_var.set(str(G5_8))
        self.G1_4_var.set(str(G1_4))
        self.return_menu()

    def op8_1(self, event=None):
        tbs_uid = self.msg_uid.get()
        tbs_msg = self.msg_contect.get()
        Found = False
        with open("Account.txt", "r") as f:
            all_acc = f.readlines()
        for acc in all_acc:
            parts = acc.strip().split(", ")
            if len(parts) != 3:
                continue
            acc_id, _, _ = parts
            if acc_id == tbs_uid:
                Found = True
                break
        if not Found:
            messagebox.showerror("UserID not found.", "UserID not found, please try again.")
            return
        else:
            write_push_msg(tbs_uid, tbs_msg)
            messagebox.showinfo("Msg sent.", "Message sent, press OK to return to menu.")
            self.return_menu()

    def op8_f1(self, event=None):
        self.msg_entry.focus_set()

    def return_menu(self):
        self.controller.reload_page("ManagementPage")

    def logout(self):
        self.controller.current_user=None
        login_page = self.controller.pages["LoginPage"]
        login_page.clear_fields()
        self.controller.show_page("LoginPage")

    def op6_1(self):
        m_new_bookings = []
        deleted = False
        d_ubid = self.tbd_ubid.get().strip()
        with open("BookingSy.txt", "r") as f:
            all_exist_bookings = f.readlines()
        for book in all_exist_bookings:
            m_parts = book.strip().split(", ")
            if len(m_parts) != 5:
                continue
            m_ubid, m_uid, m_date, m_num, m_time = m_parts
            if m_ubid == d_ubid:
                deleted = True
                continue
            else:
                m_new_bookings.append(book)
        with open("BookingSy.txt", "w") as f:
            f.writelines(m_new_bookings)
        if deleted:
            messagebox.showinfo("Deletion complete.", "Deletion complete, press OK to return to the menu.")
            update_waiting_list()
            self.return_menu()
        else:
            messagebox.showerror("Booking not found.", "No booking with inputted UBID found.")
            update_waiting_list()
        return

    def op7_1(self):
        found = False
        f_ubid = self.tbf_ubid.get().strip()
        with open("BookingSy.txt", "r") as f:
            op7_exist_bookings = f.readlines()
        for book in op7_exist_bookings:
            m7_parts = book.strip().split(", ")
            if len(m7_parts) != 5:
                continue
            m7_ubid, m7_uid, m7_date, m7_num, m7_time = m7_parts
            if m7_ubid == f_ubid:
                found = True
                messagebox.showinfo("Booking Details:",
                                    f"UBID: {m7_ubid}\n"
                                    f"UserID: {m7_uid}\n"
                                    f"Booking Date: {m7_date}\n"
                                    f"Group Num: {m7_num}\n"
                                    f"Booking Time: {m7_time}\n\n"
                                    f"Press OK to return to the menu.")
                self.return_menu()
                return
        if not found:
            messagebox.showerror("No booking found.", "No booking with inputted UBID found.")
            return

    def op1_f1(self, event=None):
        self.G5_8_entry.focus_set()

    def op1_f2(self, event=None):
        self.G1_4_entry.focus_set()

    def op9(self):
        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()

        op9_date = tk.StringVar()
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)
        self.instruction_label = ttk.Label(self.form, text="Input a date to find bookings:", font=("Times New Roman", 22))
        self.date_label = ttk.Label(self.form, text="Date (yyyy-mm-dd)", font=("Arial", 16, "bold"))
        self.op9_date_entry = ttk.Entry(self.form, textvariable=op9_date)
        self.find_btn = ttk.Button(self.form, text="Find", command=self.op9_1)
        self.instruction_label.grid(row=0, columnspan=2)
        self.date_label.grid(row=1, column=0)
        self.op9_date_entry.grid(row=1, column=1)
        return_btn.grid(row=2, column=0)
        self.find_btn.grid(row=2, column=1)

        self.op9_date_entry.bind("<Return>", self.op9_1)

    def op9_1(self, event=None):
        get_date = self.op9_date_entry.get()
        try:
            get_date = datetime.strptime(get_date, "%Y-%m-%d").date()
        except ValueError:
                messagebox.showerror("Invalid Input.", "Invalid date format! Please try again!")
                return
        book_list = []

        with open("BookingSy.txt", "r") as f:
            for line in f:
                parts = line.strip().split(", ")
                if len(parts) != 5:
                    continue
                else:
                    ubid, b_userid, book_date, book_size, book_time = parts
                    try:
                        book_date = datetime.strptime(book_date, "%Y-%m-%d").date()
                        book_time = datetime.strptime(book_time, "%H:%M:%S").time()
                        book_size = int(book_size)
                    except ValueError:
                        continue
                    if not book_date == get_date:
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
                    month_final = book_date.month
                    for book_month, month_str in months.items():
                        if book_date.month == book_month:
                            month_final = month_str
                            break
                    book_list.append(f"{ubid}:  "
                                             f"Reservation for {book_size} people at {book_time} on"
                                             f" {book_date.day} {month_final} {book_date.year}"
                                             f" under the name '{b_userid}'.")

        if len(book_list) > 0:
            book_text_str = "\n".join(book_list)
        else:
            book_text_str = "<No bookings found.>"

        self.title_label.grid_forget()
        self.sub_title_label.grid_forget()
        self.op1_btn.grid_forget()
        self.op2_btn.grid_forget()
        self.op3_btn.grid_forget()
        self.op4_btn.grid_forget()
        self.op5_btn.grid_forget()
        self.op6_btn.grid_forget()
        self.op7_btn.grid_forget()
        self.op8_btn.grid_forget()
        self.op9_btn.grid_forget()
        self.op10_btn.grid_forget()
        self.return_btn.grid_forget()
        self.instruction_label.grid_forget()
        self.date_label.grid_forget()
        self.op9_date_entry.grid_forget()
        self.return_btn.grid_forget()
        self.find_btn.grid_forget()

        try:
            self.form.rowconfigure(1, weight=1)
            self.form.columnconfigure(0, weight=1)
        except Exception:
            pass

        book_text = scrolledtext.ScrolledText(self.form, wrap="word", font=("Arial", 15), height=12)
        book_text.insert("1.0", book_text_str)
        book_text.configure(state="disabled")  # To make it read-only

        op5_label = ttk.Label(self.form, text="Bookings Details:", font=("Times New Roman", 22))
        return_btn = ttk.Button(self.form, text=" ← Return to Management Menu", command=self.return_menu)

        op5_label.grid(row=0, column=0, pady=(0, 10))
        book_text.grid(row=1, column=0)
        return_btn.grid(row=2, column=0)

    def op10(self):
        max_date_str = cal_max_day()
        max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
        book_list = []
        total_count = 0
        count_14 = 0
        count_58 = 0
        count_912 = 0

        with open("BookingSy.txt", "r") as f:
            for line in f:
                parts = line.strip().split(", ")
                if len(parts) != 5:
                    continue
                else:
                    ubid, b_userid, book_date, book_size, book_time = parts
                    try:
                        book_date = datetime.strptime(book_date, "%Y-%m-%d").date()
                        book_time = datetime.strptime(book_time, "%H:%M:%S").time()
                        book_size = int(book_size)
                    except ValueError:
                        continue
                    if not (date.today() < book_date <= max_date):
                        continue
                    else:
                        total_count += 1
                        if book_size in range(1, 5):
                            count_14 += 1
                        elif book_size in range(5, 9):
                            count_58 += 1
                        elif book_size in range(9, 13):
                            count_912 += 1
                        else:
                            continue
        
        messagebox.showinfo("Statistics:", f"Total Bookings in next 30 Days:\n {total_count}\n\n"
                            f"1-4 ppl:\n {count_14}\n\n5-8 ppl:\n{count_58}\n\n9-12 ppl:\n{count_912}")
        return


class BookingPage(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        self.userid_var = tk.StringVar(self, value="Logged in as: <NULL>")
        self.current_userid_label = ttk.Label(form, textvariable=self.userid_var)

        title_label = ttk.Label(form, text="WaiWai's Restaurant Booking System",
                                font=("Times New Roman", 22))
        sub_title_label = ttk.Label(form, text="User Booking Page", font=("Times New Roman", 22))
        self.op1_btn = ttk.Button(form, text="1. Book a table", width=35, command=self.op1)
        op2_btn = ttk.Button(form, text="2. View Existing Booking", width=35, command=self.op2)
        op3_btn = ttk.Button(form, text="3. Modify a Reservation", width=35, command=self.op3)
        op4_btn = ttk.Button(form, text="4. Cancel a booking", width=35, command=self.op4)
        op5_btn = ttk.Button(form, text=" ← Logout", width=35, command=self.call_login)
        op6_btn = ttk.Button(form, text="Account Settings", width=35, command=self.go_settings)
        op7_btn = ttk.Button(form, text="5. Check Table Availability", width=35, command=self.op7)
        op8_btn = ttk.Button(form, text="6. View Bookings in Waiting List", width=35, command=self.op8)

        title_label.grid(row=0, columnspan=2)
        sub_title_label.grid(row=1, columnspan=2, pady=(0, 10))
        self.current_userid_label.grid(row=7, columnspan=2, pady=(5, 0))
        self.op1_btn.grid(row=3, column=0)
        op2_btn.grid(row=3, column=1)
        op3_btn.grid(row=4, column=0, pady=(10, 0))
        op4_btn.grid(row=4, column=1, pady=(10, 0))
        op7_btn.grid(row=5, column=0, pady=(10, 0))
        op8_btn.grid(row=5, column=1, pady=(10, 0))
        op5_btn.grid(row=6, column=0, pady=(10, 0))
        op6_btn.grid(row=6, column=1, pady=(10, 0))

    def call_login(self):
        self.controller.current_user = None
        login_page = self.controller.pages["LoginPage"]
        login_page.clear_fields()
        self.controller.show_page("LoginPage")

    def refresh_data(self):
        uid = self.controller.current_user or "<NULL>"
        self.userid_var.set(f"Logged in as: {uid}")

    def focus_first(self):
        try:
            self.op1_btn.focus_set()
        except Exception:
            pass

    def op1(self):
        self.op1_page = BookingPage_op1(self.master, controller=self.controller)
        self.pack_forget()
        self.op1_page.pack(fill="both", expand=True)

    def op2(self):
        op2_page = BookingPage_op2(self.master, controller=self.controller)
        if not op2_page.winfo_exists():
            return  # Check if the page exists
        self.pack_forget()
        self.op2_page = op2_page
        self.op2_page.pack(fill="both", expand=True)

    def op3(self):
        self.op3_page = BookingPage_op3(self.master, controller=self.controller)
        self.pack_forget()
        self.op3_page.pack(fill="both", expand=True)

    def op4(self):
        self.op4_page = BookingPage_op4(self.master, controller=self.controller)
        self.pack_forget()
        self.op4_page.pack(fill="both", expand=True)

    def go_settings(self):
        self.acc_set = AccSettings(self.master, controller=self.controller)
        self.pack_forget()
        self.acc_set.pack(fill="both", expand=True)

    def op7(self):
        self.op7_page = BookingPage_op7(self.master, controller=self.controller)
        self.pack_forget()
        self.op7_page.pack(fill="both", expand=True)

    def op8(self):
        self.op8_page = BookingPage_op8(self.master, controller=self.controller)
        self.pack_forget()
        self.op8_page.pack(fill="both", expand=True)


class BookingPage_op1(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        next_day = date.today() + timedelta(days=1)
        uid = self.controller.current_user if self.controller else "<NULL>"
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        self.year_var = tk.StringVar(self)
        self.month_var = tk.StringVar(self)
        self.day_var = tk.StringVar(self)
        self.time_var = tk.StringVar(self)
        self.size_var = tk.StringVar(self)

        self.userid_var = tk.StringVar()
        self.userid_var.set(f"Logged in as: {uid}")
        self.current_userid_label = ttk.Label(form, textvariable=self.userid_var)
        today_label = ttk.Label(form, text=f"Today is {date.today()}.\n"
                                           f"Last available date for making reservation: {cal_max_day()}.",
                                font=("Times New Roman", 22))
        when_label = ttk.Label(form, text="Input the date you would like to make a reservation:", font=("Arial", 16))
        year_label = ttk.Label(form, text="Year", font=("Arial", 16, "bold"))
        month_label = ttk.Label(form, text="Month", font=("Arial", 16, "bold"))
        day_label = ttk.Label(form, text="Day", font=("Arial", 16, "bold"))
        time_label = ttk.Label(form, text="Time (HH:MM)", font=("Arial", 16, "bold"))
        size_label = ttk.Label(form, text="Group Size", font=("Arial", 16, "bold"))
        self.year_entry = ttk.Entry(form, textvariable=self.year_var)
        self.month_entry = ttk.Entry(form, textvariable=self.month_var)
        self.day_entry = ttk.Entry(form, textvariable=self.day_var)
        self.time_entry = ttk.Entry(form, textvariable=self.time_var)
        self.size_entry = ttk.Entry(form, textvariable=self.size_var)
        return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
        submit_btn = ttk.Button(form, text="Submit", command=self.get_data)

        self.year_entry.bind("<Return>", self.focus_1)
        self.month_entry.bind("<Return>", self.focus_2)
        self.day_entry.bind("<Return>", self.focus_3)
        self.time_entry.bind("<Return>", self.focus_4)
        self.size_entry.bind("<Return>", self.get_data)

        today_label.grid(row=0, columnspan=2)
        when_label.grid(row=1, columnspan=2, pady=10)
        year_label.grid(row=2, column=0)
        self.year_entry.grid(row=2, column=1)
        month_label.grid(row=3, column=0)
        self.month_entry.grid(row=3, column=1)
        day_label.grid(row=4, column=0)
        self.day_entry.grid(row=4, column=1)
        time_label.grid(row=5, column=0)
        self.time_entry.grid(row=5, column=1)
        size_label.grid(row=6, column=0)
        self.size_entry.grid(row=6, column=1)
        return_btn.grid(row=7, column=0)
        submit_btn.grid(row=7, column=1)

    def return_booking(self):
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")

    def get_data(self, event=None):
        today = datetime.today().date()
        next_day = date.today() + timedelta(days=1)
        max_date_str = cal_max_day()
        max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
        year_input = self.year_entry.get()
        month_input = self.month_entry.get()
        day_input = self.day_entry.get()
        time_input = self.time_entry.get()
        userid = self.controller.current_user
        size = self.size_entry.get()
        user_date = ""
        user_time = ""

        mix_date = f"{year_input}-{month_input}-{day_input}"
        try:
            user_date = datetime.strptime(mix_date, "%Y-%m-%d").date()
            if not (today < user_date <= max_date):
                if user_date == date.today():
                    messagebox.showerror("Invalid Input.",
                                         "Sorry! We do not accept same day reservation.")
                    return
                else:
                    messagebox.showerror("Invalid Input.",
                                         f"The booking date must be between {next_day} and {cal_max_day()}.")
                    return
            user_time = datetime.strptime(time_input, "%H:%M").time()
            open_time = datetime.strptime("07:00", "%H:%M").time()
            close_time = datetime.strptime("20:30", "%H:%M").time()
            if not (open_time <= user_time <= close_time):  # WaiWai's Restaurant open 07:00 and close at 21:00
                messagebox.showerror("Invalid input.",
                                     "Out of business time!\nWe only accept reservation between 07:00 - 20:30!")
                return
            if user_time.minute not in [0, 30]:
                messagebox.showerror("Invalid input.",
                                     "Error!\nYou can only book at 30-minute intervals (e.g., 12:00, 12:30, 13:00).")
                return
            user_num = int(size)
        except ValueError:
            messagebox.showerror("Invalid Input.",
                                 "The value in Year/Month/Day/Group Size should be an integer,"
                                 "\nwhile the value in Time should be in format (HH:MM)!")
            return

        if check_duplicated_booking(userid, user_date, user_time):  # Check if user duplicated booking
            messagebox.showerror("Duplicated Booking.",
                                 f"Sorry! You can't make a reservation on {user_date} at {user_time} "
                                 f"since you already have a reservation at that time.")
            return
        else:
            pass

        if user_num < 1 or user_num > 12:
            messagebox.showerror("Invalid group size.",
                                 "Invalid group size. We only accept reservations for 1-12 people.")
            return

        if not check_availability(user_num, user_date, user_time):
            messagebox.showerror("Not available.",
                                 f"Sorry, there are no available tables for {user_num} people on {user_date}.")
            ask = messagebox.askyesno(
                "No table available",
                "Would you like to be added to the waiting list for that time?")
            if not ask:
                messagebox.showinfo("Process end.",
                                    "Thank you for using our service, press OK to return to the menu.")
                BookingPage_op1.return_booking(self)
            elif ask:
                write_waiting_list(gen_unique_ubid(), user_num, user_date, userid, user_time)
                waited = messagebox.askyesno("Process end.",
                                             "Your booking is successfully been added to the waiting list."
                                             "\n\nReturn to Booking Menu now?")
                if waited:
                    BookingPage_op1.return_booking(self)
                else:
                    return
                return
        else:
            write_booking(gen_unique_ubid(), userid, user_date, user_time, user_num)
            booked = messagebox.askyesno("Booking confirmed.",
                                         f"Reservation for {user_num} people has successfully booked for {user_date} at "
                                         f"{user_time}.\nIt's under the name {userid}.\n\nReturn to Booking Menu now?")
            if booked:
                self.return_booking()
            else:
                return

    def focus_1(self, event=None):
        self.month_entry.focus_set()

    def focus_2(self, event=None):
        self.day_entry.focus_set()

    def focus_3(self, event=None):
        self.time_entry.focus_set()

    def focus_4(self, event=None):
        self.size_entry.focus_set()


class BookingPage_op2(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        userid = self.controller.current_user if self.controller else "<NULL>"
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

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
            self.bookings_var = tk.StringVar(self)
            dummy = ""
            for booking in existing_bookings:
                dummy += f"{booking}\n"
                self.bookings_var.set(dummy)
            book_value_label = ttk.Label(form, textvariable=self.bookings_var, font=("Arial", 15))
            book_value_label.grid(row=1, column=0, pady=10)
            info_label = ttk.Label(form, text="Your bookings details:", font=("Times New Roman", 22))
            info_label.grid(row=0, column=0)
            return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
            return_btn.grid(row=2, column=0)
        else:
            messagebox.showinfo("No bookings found.",
                                "No reservations found under your name.\nPress OK to return to the menu:")
            self.destroy()
            self.controller.show_page("BookingPage")

    def return_booking(self):
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")


class BookingPage_op3(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        self.userid = self.controller.current_user if self.controller else "<NULL>"
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        # tbm means "To be modified"
        instruction = ttk.Label(form, text="Input the details of the booking that you would like to modify:",
                                font=("Times New Roman", 22))
        self.tbm_date = tk.StringVar()
        self.tbm_time = tk.StringVar()
        self.tbm_size = tk.StringVar()
        date_label = ttk.Label(form, text="Date (yyyy-mm-dd)", font=("Arial", 16, "bold"))
        time_label = ttk.Label(form, text="Time (HH:MM)", font=("Arial", 16, "bold"))
        size_label = ttk.Label(form, text="Group Size", font=("Arial", 16, "bold"))
        self.date_entry = ttk.Entry(form, textvariable=self.tbm_date)
        self.time_entry = ttk.Entry(form, textvariable=self.tbm_time)
        self.size_entry = ttk.Entry(form, textvariable=self.tbm_size)
        return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
        enter_btn = ttk.Button(form, text="Enter", command=self.get_data)

        self.date_entry.bind("<Return>", self.focus_1)
        self.time_entry.bind("<Return>", self.focus_2)
        self.size_entry.bind("<Return>", self.get_data)

        instruction.grid(row=0, columnspan=2, pady=10)
        date_label.grid(row=1, column=0)
        time_label.grid(row=2, column=0)
        size_label.grid(row=3, column=0)
        self.date_entry.grid(row=1, column=1)
        self.time_entry.grid(row=2, column=1)
        self.size_entry.grid(row=3, column=1)
        return_btn.grid(row=4, column=0)
        enter_btn.grid(row=4, column=1)

    def return_booking(self):
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")

    def get_data(self, event=None):
        book_date = self.date_entry.get()
        self.book_time = self.time_entry.get()
        book_size = self.size_entry.get()

        try:
            modify_date = datetime.strptime(book_date, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid input.", "Invalid date, please try again.")
            return

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

            if modify_userid == self.userid and modify_user_date == modify_date:
                match_modify += 1
                match_booking.append(f"{ubid}, {self.userid}, {modify_user_date}, {modify_num}, {modify_time}")
                match_booking_user.append(f"{modify_user_date.day} {month_final} {modify_user_date.year}: "
                                          f"Reservation for {modify_num} people at {modify_time_str}.")

        if match_modify == 0:
            messagebox.showerror("Invalid input.",
                                 "No bookings found at that day/time, please try again.")
            return

        correct = False
        try:
            k_modify_time = datetime.strptime(self.book_time, "%H:%M").time()
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
                pass
            else:
                messagebox.showerror("Invalid input.",
                                     "No bookings found at that day/time, please try again.")
                return
        except ValueError:
            messagebox.showerror("Invalid input.", "Invalid time format! Please try again.")
            return

        if not book_size.isdigit() or not (1 <= int(book_size) <= 12):
            messagebox.showerror("Invalid input.", "Invalid group size format! Please try again.")
            return

        self.tbm_date.set(book_date)
        self.tbm_time.set(self.book_time)
        self.tbm_size.set(book_size)
        self.modify_page = BookingPage_op3_1(self.master, controller=self.controller,
                                             tbm_date=self.tbm_date.get(),
                                             tbm_time=self.tbm_time.get(),
                                             tbm_size=self.tbm_size.get())
        self.pack_forget()
        self.modify_page.pack(fill="both", expand=True)

    def focus_1(self, event=None):
        self.time_entry.focus_set()

    def focus_2(self, event=None):
        self.size_entry.focus_set()


class BookingPage_op3_1(ttk.Frame):
    def __init__(self, parent, controller=None, tbm_date="", tbm_time="", tbm_size=""):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        self.userid = self.controller.current_user if self.controller else "<NULL>"
        self.tbm_date = tbm_date
        self.tbm_time = tbm_time
        self.tbm_size = tbm_size
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        instruction = ttk.Label(form, text="Input new date/time/group size:", font=("Times New Roman", 22))
        enter_btn = ttk.Button(form, text="Enter", command=self.modify_book)
        return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
        self.new_date = tk.StringVar(value=tbm_date)
        self.new_time = tk.StringVar(value=tbm_time)
        self.new_size = tk.StringVar(value=tbm_size)
        new_date_label = ttk.Label(form, text="New Date", font=("Arial", 16, "bold"))
        new_time_label = ttk.Label(form, text="New Time", font=("Arial", 16, "bold"))
        new_size_label = ttk.Label(form, text="New Group Size", font=("Arial", 16, "bold"))
        self.new_date_entry = ttk.Entry(form, textvariable=self.new_date)
        self.new_time_entry = ttk.Entry(form, textvariable=self.new_time)
        self.new_size_entry = ttk.Entry(form, textvariable=self.new_size)

        instruction.grid(row=0, columnspan=2, pady=10)
        new_date_label.grid(row=1, column=0)
        new_time_label.grid(row=2, column=0)
        new_size_label.grid(row=3, column=0)
        self.new_date_entry.grid(row=1, column=1)
        self.new_time_entry.grid(row=2, column=1)
        self.new_size_entry.grid(row=3, column=1)
        return_btn.grid(row=4, column=0)
        enter_btn.grid(row=4, column=1)

        self.new_date_entry.bind("<Return>", self.focus_1)
        self.new_time_entry.bind("<Return>", self.focus_2)
        self.new_size_entry.bind("<Return>", self.modify_book)

    def return_booking(self):
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")

    def modify_book(self, event=None):
        today = datetime.today().date()
        max_date_str = cal_max_day()
        max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
        edited_bookings = []
        old_date = self.new_date_entry.get()
        old_time = self.new_time_entry.get()
        old_size = self.new_size_entry.get()
        try:
            old_date = datetime.strptime(self.tbm_date, "%Y-%m-%d").date()
            old_time = datetime.strptime(self.tbm_time, "%H:%M").time()
            old_size = int(old_size)
        except ValueError:
            messagebox.showerror("Invalid input.", "The format of date/time/group size is not correct!\n"
                                                   "Please try again!")
            return

        with open("BookingSy.txt", "r") as f:
            bookings = f.readlines()

        try:
            new_date = datetime.strptime(self.new_date_entry.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid input.", "Invalid date format! Please try again.")
            return

        if not (today < new_date <= max_date):
            if new_date == date.today():
                messagebox.showerror("Invalid input.", f"Sorry! We do not accept same day reservation.")
                return
            else:
                messagebox.showerror("Invalid input.",
                                     f"The date must be greater than {date.today()} and less than "
                                     f"{cal_max_day()}!")
                return

        open_time = datetime.strptime("07:00", "%H:%M").time()
        close_time = datetime.strptime("20:30", "%H:%M").time()
        try:
            new_time = datetime.strptime(self.new_time_entry.get(), "%H:%M").time()
        except ValueError:
            messagebox.showerror("Invalid input.", "Invalid time format! Please try again.")
            return

        if not (open_time <= new_time <= close_time):  # WaiWai's Restaurant open 07:00 and close at 21:00
            messagebox.showerror(
                "Invalid input.", "Error! Out of business time! We only accept reservation between 07:00 - 20:30!")
            return
        if new_time.minute not in [0, 30]:
            messagebox.showerror("Invalid format.",
                                 "Error! You can only book at 30-minute intervals (e.g., 12:00, 12:30, 13:00).")
            return

        if self.new_size_entry.get().isdigit():
            new_size = int(self.new_size_entry.get())
            if 1 <= new_size <= 12:
                pass
            else:
                messagebox.showerror("Invalid input.", "Invalid group size. Please enter a number between 1 and 12.")
                return
        else:
            messagebox.showerror("Invalid input.", "Invalid group size. The format of group size should be an integer!")
            return

        modified = False
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

            if booking_id == self.userid and booking_date == old_date and booking_time == old_time:
                if check_duplicated_booking(self.userid, new_date, new_time):
                    messagebox.showerror("Duplicated booking.",
                                         "You already have a booking at the requested date and time, modification "
                                         "failed.")
                    return
                if not check_availability(new_size, new_date, new_time):
                    messagebox.showerror("Not available", "We don't have enough tables at that time.")
                    return
                edited_bookings.append(
                    f"{ubid2}, {self.userid}, {new_date.strftime('%Y-%m-%d')}, {new_size}, "
                    f"{new_time.strftime('%H:%M:%S')}\n"
                )
                modified = True
            else:
                edited_bookings.append(k)

        with open("BookingSy.txt", "w") as f:
            f.writelines(edited_bookings)

        if modified:
            messagebox.showinfo("Modification success.", "Your booking has been successfully modified.")
            self.return_booking()
        else:
            messagebox.showerror("Modification failed", "Unable to find the original booking to modify.")
            return

    def focus_1(self, event=None):
        self.new_time_entry.focus_set()

    def focus_2(self, event=None):
        self.new_size_entry.focus_set()


class BookingPage_op4(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        self.userid = self.controller.current_user if self.controller else "<NULL>"
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        # tbc means "To be cancelled"
        instruction = ttk.Label(form, text="Input the details of the booking that you would like to cancel:",
                                font=("Times New Roman", 22))
        self.tbc_date = tk.StringVar()
        self.tbc_time = tk.StringVar()
        self.tbc_size = tk.StringVar()
        date_label = ttk.Label(form, text="Date (yyyy-mm-dd)", font=("Arial", 16, "bold"))
        time_label = ttk.Label(form, text="Time (HH:MM)", font=("Arial", 16, "bold"))
        self.date_entry = ttk.Entry(form, textvariable=self.tbc_date)
        self.time_entry = ttk.Entry(form, textvariable=self.tbc_time)
        return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
        enter_btn = ttk.Button(form, text="Enter", command=self.get_data)

        instruction.grid(row=0, columnspan=2, pady=10)
        date_label.grid(row=1, column=0)
        time_label.grid(row=2, column=0)
        self.date_entry.grid(row=1, column=1)
        self.time_entry.grid(row=2, column=1)
        return_btn.grid(row=4, column=0)
        enter_btn.grid(row=4, column=1)

        self.date_entry.bind("<Return>", self.focus_1)
        self.time_entry.bind("<Return>", self.get_data)

    def return_booking(self):
        update_waiting_list()
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")

    def get_data(self, event=None):
        edited_bookings = []
        cancel_date = self.date_entry.get()
        i_cancel_time = self.time_entry.get()

        try:
            cancel_date = datetime.strptime(cancel_date, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid input.", "Invalid date format! Please enter in yyyy-mm-dd.")
            return

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

            if cancel_userid == self.userid and cancel_user_date == cancel_date:
                match_cancel += 1
                match_booking.append(f"{cancel_ubid}, {self.userid}, {cancel_user_date}, {cancel_num}, {cancel_time}")
                match_booking_user.append(f"{cancel_user_date.day} {month_final} {cancel_user_date.year}: "
                                          f"Reservation for {cancel_num} people at {cancel_time_str}.")

        if match_cancel == 0:
            messagebox.showerror("Invalid input.", "No bookings found at that day/time, please try again.")
            return
        else:
            try:
                final_cancel_time = datetime.strptime(i_cancel_time, "%H:%M").time()
            except ValueError:
                messagebox.showerror("Invalid input.", "Time format is not correct, please try again.")
                return
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
                        and c1_userid == self.userid):
                    final_c_ubid = c1_ubid
            if final_c_ubid is None:
                messagebox.showerror("Invalid input.", "No bookings found at that day/time, please try again.")
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

                        if booking_id == self.userid and booking_date == cancel_date and booking_time == final_cancel_time:
                            continue
                        else:
                            edited_bookings.append(
                                f"{book_ubid}, {booking_id}, {booking_date.strftime('%Y-%m-%d')}, {group_size}"
                                f", {booking_time.strftime('%H:%M:%S')}\n")
                    break
            confirm = messagebox.askyesno(
                "Confirmation",
                f"Are you sure you want to cancel your booking on {cancel_date} at {final_cancel_time}?")
            if not confirm:
                messagebox.showinfo("Process ended.", "Cancellation aborted.")
                update_waiting_list()
                self.return_booking()
            else:
                with open("BookingSy.txt", "w") as f:
                    f.writelines(edited_bookings)
                messagebox.showinfo("Cancelled.", "Booking has been successfully cancelled.")
                update_waiting_list()
                self.return_booking()

    def focus_1(self, event=None):
        self.time_entry.focus_set()


class BookingPage_op7(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        self.userid = self.controller.current_user if self.controller else "<NULL>"
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        self.search_year_var = tk.StringVar(self)
        self.search_month_var = tk.StringVar(self)
        self.search_day_var = tk.StringVar(self)
        self.search_time_var = tk.StringVar(self)

        title_label = ttk.Label(form, text=f"Today is {date.today()}.\n"
                                           f"Last available date for making reservation: {cal_max_day()}.",
                                font=("Times New Roman", 22))
        subtitle_label = ttk.Label(form, text="Input a date to check availability", font=("Times New Roman", 22))
        search_year_label = ttk.Label(form, text="Year", font=("Arial", 16, "bold"))
        search_month_label = ttk.Label(form, text="Month", font=("Arial", 16, "bold"))
        search_day_label = ttk.Label(form, text="Day", font=("Arial", 16, "bold"))
        search_time_label = ttk.Label(form, text="Time (HH:MM)", font=("Arial", 16, "bold"))
        self.search_year_entry = ttk.Entry(form, textvariable=self.search_year_var)
        self.search_month_entry = ttk.Entry(form, textvariable=self.search_month_var)
        self.search_day_entry = ttk.Entry(form, textvariable=self.search_day_var)
        self.search_time_entry = ttk.Entry(form, textvariable=self.search_time_var)
        return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
        search_btn = ttk.Button(form, text="Submit", command=self.search)

        self.search_year_entry.bind("<Return>", self.focus_1)
        self.search_month_entry.bind("<Return>", self.focus_2)
        self.search_day_entry.bind("<Return>", self.focus_3)
        self.search_time_entry.bind("<Return>", self.search)

        title_label.grid(row=0, columnspan=2)
        subtitle_label.grid(row=1, columnspan=2)
        search_year_label.grid(row=2, column=0)
        self.search_year_entry.grid(row=2, column=1)
        search_month_label.grid(row=3, column=0)
        self.search_month_entry.grid(row=3, column=1)
        search_day_label.grid(row=4, column=0)
        self.search_day_entry.grid(row=4, column=1)
        search_time_label.grid(row=5, column=0)
        self.search_time_entry.grid(row=5, column=1)
        return_btn.grid(row=6, column=0)
        search_btn.grid(row=6, column=1)

    def return_booking(self):
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")

    def search(self, event=None):
        read_table_num()
        num1_4 = G1_4
        num5_8 = G5_8
        num9_12 = G9_12
        today = datetime.today().date()
        next_day = date.today() + timedelta(days=1)
        max_date_str = cal_max_day()
        max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
        year_input = self.search_year_entry.get()
        month_input = self.search_month_entry.get()
        day_input = self.search_day_entry.get()
        mix_date = f"{year_input}-{month_input}-{day_input}"
        mix_time = self.search_time_entry.get()

        try:
            check_date = datetime.strptime(mix_date, "%Y-%m-%d").date()
            check_time = datetime.strptime(mix_time, "%H:%M").time()
        except ValueError:
            messagebox.showerror(
    "Invalid Input.",
    "The values in Year / Month / Day should form a valid date,\n"
    "and the time should be in format HH:MM."
)
            return
        
        if not (today < check_date <= max_date):
                if check_date == date.today():
                    messagebox.showerror("Invalid Input.",
                                         "Sorry! Same day checking is not allowed.")
                    return
                else:
                    messagebox.showerror("Invalid Input.",
                                         f"The checking date must be between {next_day} and {cal_max_day()}.")
                    return
        
        open_time = datetime.strptime("07:00", "%H:%M").time()
        close_time = datetime.strptime("20:30", "%H:%M").time()
        if not (open_time <= check_time <= close_time):
            messagebox.showerror("Invalid Input.",
                                "Out of business time!\nWe only accept checking between 07:00 - 20:30!")
            return
        if check_time.minute not in [0, 30]:
            messagebox.showerror("Invalid Input.",
                         "You can only check in 30-minute intervals (e.g., 12:00, 12:30, 13:00).")
            return

        with open("BookingSy.txt", "r") as f:
            bookings = f.readlines()

        for book in bookings:
            parts = book.strip().split(", ")

            if len(parts) != 5:
                continue
            _, _, book_date, book_size, book_time = parts

            try:
                book_date = datetime.strptime(book_date, "%Y-%m-%d").date()
                book_time = datetime.strptime(book_time, "%H:%M:%S").time()
                book_size = int(book_size)
            except ValueError:
                continue
            
            if book_date != check_date:
                continue
            if book_date == check_date and book_time == check_time:
                if book_size in range(1, 5):
                    num1_4 -= 1
                elif book_size in range(5, 9):
                    num5_8 -= 1
                elif book_size in range(9, 13):
                    num9_12 -= 1
                else:
                    continue

        if num1_4 < 0:  # Admin may reduce the number of tables when bookings are made, its for preventing negative numbers
            num1_4 = 0
        if num5_8 < 0:
            num5_8 = 0
        if num9_12 < 0:
            num9_12 = 0

        messagebox.showinfo("Availiability Details:", f"1–4 ppl tables available:\n {num1_4} / {G1_4}\n\n"
                            f"5-8 ppl tables available:\n {num5_8} / {G5_8}\n\n"
                            f"9-12 ppl tables available:\n {num9_12} / {G9_12}")
        return

    def focus_1(self, event=None):
        self.search_month_entry.focus_set()

    def focus_2(self, event=None):
        self.search_day_entry.focus_set()

    def focus_3(self, event=None):
        self.search_time_entry.focus_set()
    

class BookingPage_op8(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        userid = self.controller.current_user if self.controller else "<NULL>"
        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        with open("WaitingList.txt", "r") as f:
            wait_file = f.readlines()

        wait_bookings = []
        for wait_book in wait_file:
            parts = wait_book.strip().split(", ")
            if len(parts) != 5:
                continue

            wait_ubid, wait_userid, wait_date, wait_size, wait_time = parts
            try:
                wait_date = datetime.strptime(wait_date, "%Y-%m-%d").date()
                wait_time = datetime.strptime(wait_time, "%H:%M:%S").time()
                wait_size = int(wait_size)
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

            month_final = wait_date.month

            for book_month, month_str in months.items():
                if wait_date.month == book_month:
                    month_final = month_str
                    break

            if wait_userid == userid:
                wait_bookings.append(f"{wait_date.day} {month_final} {wait_date.year}: "
                                         f"Waiting Booking for {wait_size} people at {wait_time}.")

        self.empty = False
        if len(wait_bookings) > 0:
            self.wait_bookings_var = tk.StringVar(self)
            dummy = ""
            for booking in wait_bookings:
                dummy += f"{booking}\n"
                self.wait_bookings_var.set(dummy)
            book_value_label = ttk.Label(form, textvariable=self.wait_bookings_var, font=("Arial", 15))
            book_value_label.grid(row=1, column=0, pady=10)
            info_label = ttk.Label(form, text="All your bookings in Waiting List:", font=("Times New Roman", 22))
            info_label.grid(row=0, column=0)
            return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
            return_btn.grid(row=2, column=0)
        else:
            self.empty = True
            messagebox.showinfo("No bookings found.",
                                "No waiting bookings found under your name.\nPress OK to return to the menu:")
            return_btn = ttk.Button(form, text=" ← Return to Booking Menu", command=self.return_booking)
            return_btn.grid(row=2, column=0)

    def return_booking(self):
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")


class CreateAccount(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller

        form = ttk.Frame(self)
        form.grid(row=0, column=0)

        welcome_new_user_label = ttk.Label(form, text="WaiWai's Restaurant Booking System",
                                           font=("Times New Roman", 22))
        creation_label = ttk.Label(form, text="Account Creation Page", font=("Times New Roman", 22))
        title_label = ttk.Label(form, text="Welcome! Please input the following details to create a account:",
                                font=("Arial", 14))

        self.new_userid = tk.StringVar()
        self.new_user_pw = tk.StringVar()
        self.double_pw = tk.StringVar()
        self.phone = tk.StringVar()
        new_userid_label = ttk.Label(form, text="Your UserID", font=("Arial", 16, "bold"))
        new_user_pw_label = ttk.Label(form, text="Your Password", font=("Arial", 16, "bold"))
        double_pw_check = ttk.Label(form, text="Input Your Password Again", font=("Arial", 16, "bold"))
        phone_label = ttk.Label(form, text="Phone Number", font=("Arial", 16, "bold"))
        self.new_userid_entry = ttk.Entry(form, textvariable=self.new_userid)
        self.new_user_pw_entry = ttk.Entry(form, textvariable=self.new_user_pw, show="*")
        self.double_pw_entry = ttk.Entry(form, textvariable=self.double_pw, show="*")
        self.create_btn = ttk.Button(form, text="Create Account", command=self.get_details)
        self.phone_entry = ttk.Entry(form, textvariable=self.phone)
        go_back_btn = ttk.Button(form, text=" ← Return to Login Page", command=self.call_login_page)

        welcome_new_user_label.grid(row=1, columnspan=2)
        creation_label.grid(row=2, columnspan=2)
        title_label.grid(row=3, column=0, pady=(36, 10), columnspan=2)
        new_userid_label.grid(row=4, column=0)
        new_user_pw_label.grid(row=5, column=0)
        double_pw_check.grid(row=6, column=0)
        self.new_userid_entry.grid(row=4, column=1)
        self.new_user_pw_entry.grid(row=5, column=1)
        self.double_pw_entry.grid(row=6, column=1)
        phone_label.grid(row=7, column=0)
        self.phone_entry.grid(row=7, column=1)
        go_back_btn.grid(row=8, column=0, pady=10)
        self.create_btn.grid(row=8, column=1, pady=10)

        self.new_user_pw_entry.bind("<Return>", self.focus_next1)
        self.new_userid_entry.bind("<Return>", self.focus_next)
        self.double_pw_entry.bind("<Return>", self.focus_next2)
        self.phone_entry.bind("<Return>", self.get_details)

    def call_login_page(self):
        self.controller.show_page("LoginPage")

    def focus_next(self, event=None):
        self.new_user_pw_entry.focus_set()

    def focus_next1(self, event=None):
        self.double_pw_entry.focus_set()

    def get_details(self, event=None):
        self.create_btn.state(["disabled"])
        new_userid = self.new_userid_entry.get()
        new_user_pw = self.new_user_pw_entry.get()
        double_pw = self.double_pw_entry.get()
        phone = self.phone_entry.get()
        if new_user_pw != double_pw:
            messagebox.showerror("Unmatched Password.", "Your passwords are not match, please try again.")
            self.create_btn.state(["!disabled"])
            return
        if len(new_userid) == 0:
            empty = True
        else:
            empty = False
        check_space = new_userid.find(" ")  # No space is allowed
        check_comma = new_userid.find(",")  # No "," is allowed
        if check_space != -1 or check_comma != -1:
            messagebox.showerror("Invalid username.", "Warning! \nNo space or comma (,) is allowed!")
            self.create_btn.state(["!disabled"])
            return
        elif empty:
            messagebox.showerror("Invalid username.", "Warning! \nYou have inputted nothing!")
            self.create_btn.state(["!disabled"])
            return
        exist = False
        with open("Account.txt", "r") as f:
            for i in range(count_line()):
                line = f.readline().strip()
                line = line.split(", ")
                if len(line) != 3:
                    continue
                if new_userid == line[0]:
                    exist = True
                    break
                else:
                    exist = False
        if exist:
            messagebox.showerror("Invalid username.",
                                 "Warning! \nThis UserID is already in use! Please try another one!")
            self.create_btn.state(["!disabled"])
            return
        check_pw_space = new_user_pw.find(" ")  # To prevent error since I use ", " to split in other sub-programs
        check_pw_comma = new_user_pw.find(",")
        if check_pw_space != -1 or check_pw_comma != -1:
            messagebox.showerror("Invalid password.", "Warning! \nNo space or comma (,) is allowed!")
            self.create_btn.state(["!disabled"])
            return
        if len(phone) != 8 or not phone.isdigit():
            messagebox.showerror("Invalid phone number.", "Error! You have to input an 8-digit valid HK phone number!")
            self.create_btn.state(["!disabled"])
            return
        if phone[0] not in ['4', '5', '6', '7', '8', '9']:
            messagebox.showerror("Invalid phone number.",
                                 "Error! Your phone number should start with [4, 5, 6, 7, 8, 9]!")
            self.create_btn.state(["!disabled"])
            return
        with open("Account.txt", "a") as f:
            f.write(f"{new_userid}, {new_user_pw}, {phone}\n")
        login_now = messagebox.askyesno("Account created.",
                                        "Account creation complete! Login Now?")
        if login_now:
            self.create_btn.state(["!disabled"])
            self.controller.show_page("LoginPage")
        else:
            self.create_btn.state(["!disabled"])

    def focus_next2(self, event=None):
        self.phone_entry.focus_set()

    def refresh_data(self):
        try:
            self.new_userid.set("")
            self.new_user_pw.set("")
            self.double_pw.set("")
            self.phone.set("")
        except Exception:
            pass


class AccSettings(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        self.userid = self.controller.current_user if self.controller else "<NULL>"
        self.form = ttk.Frame(self)
        self.form.grid(row=0, column=0)

        self.i_user_pw = tk.StringVar()
        self.welcome = ttk.Label(self.form, text="WaiWai's Restaurant Booking System",
                                           font=("Times New Roman", 22))
        self.subtitle = ttk.Label(self.form, text="Account Settings Page", font=("Times New Roman", 22))
        self.instruction = ttk.Label(self.form, text="Your account details:", font=("Times New Roman", 22))
        self.login_label = ttk.Label(self.form, text="Input your password", font=("Arial", 16, "bold"))
        self.login_entry = ttk.Entry(self.form, textvariable=self.i_user_pw, show="*")
        self.login_btn = ttk.Button(self.form, text="Login", command=self.login)
        self.return_btn = ttk.Button(self.form, text=" ← Return to Booking Menu", command=self.return_booking)

        self.welcome.grid(row=0, columnspan=2)
        self.subtitle.grid(row=1, columnspan=2, pady=(0, 10))
        self.login_label.grid(row=3, column=0)
        self.login_entry.grid(row=3, column=1)
        self.return_btn.grid(row=5, column=0)
        self.login_btn.grid(row=5, column=1)

        self.login_entry.bind("<Return>", self.login)

    def return_booking(self):
        try:
            self.destroy()
        finally:  # Prevent unexpected error
            self.controller.show_page("BookingPage")

    def login(self, event=None):
        typed_pw = self.i_user_pw.get()
        if not typed_pw:
            messagebox.showerror("Invalid input.", "Empty password, please try again.")
            return

        self.found_pw = None
        self.found_phone = None
        login = False
        with open("Account.txt", "r") as f:
            for line in f:
                try:
                    stored_user, stored_pw, stored_phone = line.strip().split(", ")
                except ValueError:
                    continue
                if stored_user == self.userid and stored_pw == typed_pw:
                    self.found_pw = stored_pw
                    self.found_phone = stored_phone
                    login = True
                    break
        if not login:
            messagebox.showerror("Invalid input.", "Wrong password, please try again.")
            return

        self.welcome.grid_forget()
        self.subtitle.grid_forget()
        self.login_label.grid_forget()
        self.login_entry.grid_forget()
        self.login_btn.grid_forget()

        self.instruction.grid(row=0, columnspan=2, pady=(0, 10))
        self.return_btn.grid(row=5, column=0)

        id_label = ttk.Label(self.form, text="UserID (unchangeable)", font=("Arial", 16, "bold"))
        id_content = ttk.Label(self.form, text=self.userid, font=("Arial", 16))
        pw_label = ttk.Label(self.form, text="Your password", font=("Arial", 16, "bold"))
        self.pw_content = tk.StringVar(self, value=str(self.found_pw))
        self.pw_entry = ttk.Entry(self.form, textvariable=self.pw_content)
        phone_label = ttk.Label(self.form, text="Phone", font=("Arial", 16, "bold"))
        self.phone_content = tk.StringVar(self, value=str(self.found_phone))
        self.phone_entry = ttk.Entry(self.form, textvariable=self.phone_content)
        update_btn = ttk.Button(self.form, text="Update", command=self.update_acc)

        id_label.grid(row=1, column=0)
        id_content.grid(row=1, column=1)
        pw_label.grid(row=2, column=0)
        self.pw_entry.grid(row=2, column=1)
        phone_label.grid(row=3, column=0)
        self.phone_entry.grid(row=3, column=1)
        update_btn.grid(row=5, column=1)

        update_btn.bind("<Return>", self.update_acc)
        self.pw_entry.bind("<Return>", self.focus_1)

    def update_acc(self, event=None):
        new_pw = self.pw_entry.get()
        new_phone = self.phone_entry.get()
        check_new_pw_space = new_pw.find(" ")
        check_new_pw_comma = new_pw.find(",")

        if check_new_pw_space != -1 or check_new_pw_comma != -1:
            messagebox.showerror("Invalid input.", "Warning! No space or comma (,) is allowed!")
            self.destroy()
            self.controller.show_page("BookingPage")
            return

        if len(new_phone) != 8 or not new_phone.isdigit():
            messagebox.showerror("Format error.", "Error! You have to input an 8-digit valid HK phone number!")
            return
        if not new_phone[0] in ['4', '5', '6', '7', '8', '9']:
            messagebox.showerror("Format error.", "Error! Your phone number should start with [4, 5, 6, 7, 8, 9]!")
            return

        if new_pw == self.found_pw and new_phone == self.found_phone:
            messagebox.showerror("Value error.", "You have not edited anything yet!")
            return

        new_acc = []
        with open("Account.txt", "r") as f:
            acc = f.readlines()
        for A in acc:
            parts = A.strip().split(", ")
            if len(parts) != 3:
                continue
            e_id, e_pw, e_num = parts
            if e_id == self.userid and e_pw == self.found_pw and e_num == self.found_phone:
                pass
            else:
                new_acc.append(f"{e_id}, {e_pw}, {e_num}\n")

        with open("Account.txt", "w") as f:
            f.writelines(new_acc)
            f.write(f"{self.userid}, {new_pw}, {new_phone}\n")
        messagebox.showinfo("Update success.", "Account modification complete! Press OK to continue.")
        self.destroy()
        self.controller.show_page("BookingPage")

    def focus_1(self, event=None):
        self.phone_entry.focus_set()


if __name__ == "__main__":  # It should be run directly (just for safety)
    check_environment()
    root = MainApp()
    try:
        icon = tk.PhotoImage(file="icon.png")
        root.iconphoto(True, icon)
    except Exception:
        messagebox.showerror("Icon not found", "The icon image is missing.\nYou may still continue your work without problems.\n\nPress OK to continue")
        pass
    root.mainloop()
