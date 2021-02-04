import os
import smtplib
import sys
import subprocess
import tkinter as tk
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import messagebox
import tkinter.scrolledtext as st
import tkinter.ttk as ttk
import pandas as pd
import csv
import time
from os import path

DIR_PATH_NAME = time.strftime("%Y-%m-%d")


def generatesourcetestbed():
    filepath = askopenfilename(initialdir=os.getcwd(), filetypes=[("Excel file", "*.xls")])
    if not filepath:
        return
    if len(pd.read_excel(filepath)) == 0:
        txt_edit.config(state=tk.NORMAL)
        txt_edit.delete("1.0", tk.END)
        txt_edit.insert(tk.END, "Source switch testbed file is empty.\n")
        txt_edit.config(state=tk.DISABLED)
    else:
        try:
            os.system('pyats create testbed file --path ' + filepath + ' --output sourcetestbed.yml')
            txt_edit.config(state=tk.NORMAL)
            txt_edit.delete("1.0", tk.END)
            txt_edit.insert(tk.END, "Source switch testbed file created.\n")
            txt_edit.config(state=tk.DISABLED)
            btn_load_target["state"] = "active"
        except:
            txt_edit.insert(tk.END, "Testbed file format is wrong\n")


def generatetargettestbed():
    filepath = askopenfilename(initialdir=os.getcwd(), filetypes=[("Excel file", "*.xls")])
    if not filepath:
        return
    if len(pd.read_excel(filepath)) == 0:
        txt_edit.config(state=tk.NORMAL)
        txt_edit.delete("1.0", tk.END)
        txt_edit.insert(tk.END, "Target switch testbed file is empty.\n")
        txt_edit.config(state=tk.DISABLED)
        return
    else:
        try:
            os.system('pyats create testbed file --path ' + filepath + ' --output targettestbed.yml')
            txt_edit.config(state=tk.NORMAL)
            txt_edit.delete("1.0", tk.END)
            txt_edit.insert(tk.END, "Target switch testbed file created.\n")
            txt_edit.config(state=tk.DISABLED)
            btn_script1["state"] = "active"
        except:
            txt_edit.insert(tk.END, "Testbed file format is wrong\n")


# Run pyats job and display the output
def run_script1():
    txt_edit.insert(tk.END, "Script to check switch port is running")
    txt_edit.config(state=tk.NORMAL)
    txt_edit.delete("1.0", tk.END)
    value = messagebox.askokcancel("askokcancel", "This action takes few minutes to execute. Do you want to continue?")
    if value:
        try:
            txt_edit.insert(tk.END, "Script to check switch port is running")
            # invoke_process_popen_poll_live('pyats run job job.py --html-logs /logs')
            os.system('pyats run job job.py --html-logs log/' + DIR_PATH_NAME)
            filepath = "log/" + DIR_PATH_NAME + "/source_up.csv"
            report_filepath = "log/" + DIR_PATH_NAME + "/report.txt"
            with open(filepath, "r") as input_file:
                text = input_file.read()
                txt_edit.insert(tk.END, text)
            txt_edit.insert(tk.END, '\n')
            with open(report_filepath, "r") as input_file:
                text = input_file.read()
                txt_edit.insert(tk.END, text)
                txt_edit.config(state=tk.DISABLED)
            btn_save["state"] = "active"
            btn_email["state"] = "active"
            btn_report["state"] = "active"
            btn_script3["state"] = "active"
        except:
            txt_edit.insert(tk.END, "Error occurred while running the script")


# Display console output live in tkinter text box (Currently not in use)
def invoke_process_popen_poll_live(cmd, timeout=None):
    txt_edit.config(state=tk.NORMAL)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''
    try:
        txt_edit.insert(tk.END, "Success!!" + '\n')
        for line in p.stdout:
            line = line.decode(encoding=sys.stdout.encoding,
                               errors='replace' if sys.version_info < (3, 5)
                               else 'backslashreplace').rstrip()
            txt_edit.insert(tk.END, line + '\n')
            output += line
        retval = p.wait(timeout)
        return retval, output
    except:
        txt_edit.insert(tk.END, "Failed!!" + '\n')
        txt_edit.insert(tk.END, "There was some error while running the script" + '\n')


def view_report():
    value = messagebox.askokcancel("askokcancel", "This action takes few minutes to execute. Do you want to continue?")
    if value:
        txt_edit.config(state=tk.NORMAL)
        txt_edit.delete("1.0", tk.END)
        filepath = "log/" + DIR_PATH_NAME + "/report_log.csv"
        # generate_csvtable(filepath)
        with open(filepath, "r") as input_file:
            text = input_file.read()
            txt_edit.insert(tk.END, text)
            window.title(f"Switch port Consolidation - {filepath}")
            txt_edit.config(state=tk.DISABLED)
        txt_edit.insert(tk.END, '\n')


# Display CSV file content in a tabular format (In development)
def generate_csvtable(filepath):
    header = pd.read_csv(filepath, index_col=0, nrows=0).columns.tolist()
    txt_edit.pack(side=tk.TOP)
    tree = ''
    for items in header:
        tree = ttk.Treeview(txt_edit, columns=items, selectmode="extended")

    with open(filepath) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ss = row[0]
            sp = row[1]
            ts = row[2]
            tp = row[3]
            tree.insert("", 0, values=(ss, sp, ts, tp))
    tree.pack()


def run_targetconfig():
    value = messagebox.askokcancel("askokcancel", "This action takes few minutes to execute. Do you want to continue?")
    if value:
        txt_edit.config(state=tk.NORMAL)
        txt_edit.delete("1.0", tk.END)
        os.system('python target_config.py')
        filepath = "log/" + DIR_PATH_NAME + "/switch_migration_status.csv"
        with open(filepath, "r") as input_file:
            text = input_file.read()
            txt_edit.insert(tk.END, text)
            txt_edit.config(state=tk.DISABLED)


def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension="txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = txt_edit.get("1.0", tk.END)
        output_file.write(text)
    window.title(f"Switch port Consolidation - {filepath}")


def openNewWindow():
    newWindow = tk.Toplevel(window)
    newWindow.rowconfigure(0, minsize=100, weight=1)
    newWindow.columnconfigure(1, minsize=100, weight=1)
    newWindow.configure(bg='#ededed')
    newWindow.title("Send email")
    l1 = tk.Label(newWindow, text="Email address: ", bg='#ededed')
    l1.grid(row=0, column=0, padx=(10, 10))
    e1 = tk.Entry(newWindow, bg='white')
    e1.grid(row=0, column=1, columnspan=10)
    btn_send_email = tk.Button(newWindow, text="Send email", command=lambda: send_email(e1, newWindow), fg='green',
                               bg='light green')
    btn_send_email.grid(row=1, column=1)


def send_email(e1, newWindow):
    subject = "Switch log file"
    body = "Hi, \n\nSome of the log files generated during switch port migration are attached in the mail. \n\nThank " \
           "you, \nRespiro team. "
    sender_email = "respirotest0@gmail.com"
    receiver_email = e1.get()
    password = "respiroemail"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = e1.get()
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)

    message.attach(MIMEText(body, "plain"))
    current_dir = os.getcwd()
    if path.exists(current_dir + '/log/' + DIR_PATH_NAME + '/switch_migration_status.csv'):
        filename = {"log/" + DIR_PATH_NAME + "/source_up.csv", "log/" + DIR_PATH_NAME + "/TaskLog.job.html",
                    "log/" + DIR_PATH_NAME + "/target_down.csv", "log/" + DIR_PATH_NAME + "/report_log.csv",
                    "log/" + DIR_PATH_NAME + "/switch_migration_status.csv"}
    else:
        filename = {"log/" + DIR_PATH_NAME + "/source_up.csv", "log/" + DIR_PATH_NAME + "/TaskLog.job.html",
                    "log/" + DIR_PATH_NAME + "/target_down.csv", "log/" + DIR_PATH_NAME + "/report_log.csv"}
    for items in filename:
        try:
            with open(items, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(items)
                )
                # After the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(items)
                message.attach(part)
        except:
            messagebox.showerror("Error", "There was an error while sending attachments. Run the script to generate "
                                          "the attachments")

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        newWindow.destroy()
    except:
        messagebox.showerror("Error", "There was an error while sending email")


def viewlog():
    txt_edit.config(state=tk.NORMAL)
    filepath = askopenfilename(initialdir=os.getcwd() + "/log",
                               filetypes=[("Text Files", "*.txt"), ("CSV files", "*.csv")])
    if not filepath:
        return
    txt_edit.delete("1.0", tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        print(text)
        txt_edit.insert(tk.END, text)
    window.title(f"Simple Text Editor - {filepath}")


window = tk.Tk()
window.title("Respiro | Switch port Consolidation")

window.rowconfigure(0, minsize=500, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

txt_edit = st.ScrolledText(window, bg='white')
fr_buttons = tk.Frame(window, bg='#7db1c9')
txt_edit.config(state=tk.DISABLED)
btn_load_source = tk.Button(fr_buttons, text="Upload source switch testbed excel file(*.xls)",
                            command=generatesourcetestbed, activebackground="#717982")

btn_load_target = tk.Button(fr_buttons, text="Upload target switch testbed excel file(*.xls)",
                            command=generatetargettestbed, activebackground="#717982")

btn_script1 = tk.Button(fr_buttons, text="Run script to check port status on switches", command=run_script1)

btn_report = tk.Button(fr_buttons, text="View recommended port migration log", command=view_report)

btn_script3 = tk.Button(fr_buttons, text="Run script to verify the port migration", command=run_targetconfig)

btn_save = tk.Button(fr_buttons, text="Save As...", command=save_file)

btn_email = tk.Button(fr_buttons, text="Send log files as email", command=openNewWindow)

btn_logs = tk.Button(fr_buttons, text="View all logs", command=viewlog)

btn_load_source.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_load_target.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_script1.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
btn_report.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
btn_script3.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
btn_email.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
btn_logs.grid(row=7, column=0, sticky="ew", padx=5, pady=5)

fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")

btn_save["state"] = "disable"
btn_report["state"] = "disable"
btn_script3["state"] = "disable"
btn_script1["state"] = "disable"
btn_email["state"] = "disable"
btn_load_target["state"] = "disable"

window.mainloop()
