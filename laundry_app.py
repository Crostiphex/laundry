from Tkinter import *
from numpy import *
import tkMessageBox
import sys
import serial
import threading
import os

# Initialization
master = Tk()
# make it cover the entire screen
w, h = master.winfo_screenwidth(), master.winfo_screenheight()
port = serial.Serial('COM3', 9600)
master.overrideredirect(1)
master.geometry("%dx%d+0+0" % (w, h))
master.focus_set()  # <-- move focus to this widget
master.bind("<Escape>", lambda e: e.widget.quit())
font_opt = "Helvetica 40 bold"
f = Frame(master, height=h, width=w)
f.pack_propagate(0)  # don't shrink
f.pack()
phone_book = {}
people = ['John', 'Kevin', 'Aisha', 'Chris']
phone_number = ["+19174327085", "+6466260297", "+19177055148", "+19177055168"]
colors = ['light blue', 'light green', '#feff7f', None]
exit_flag = threading.Event()


def restart_program():
    python = sys.executable
    active.close()
    os.execl(python, python, *sys.argv)


w = Button(f, text="Touch your name after starting the machine.", command=restart_program, font="Helvetica 20 bold")
w.pack()


def monitor_machine(person):
    tkMessageBox.showinfo("Message",
                          person + ", you're all set, just wait for the message on your phone. (And push OK)")

    w["text"] = "In use by " + person + ", touch here to quit."

    # change status of who is using the laundry on the server:
    laundry_user_update(person)

    # wait for your laundry with monitoring program which is basically a while loop
    global count_average
    global count
    count = 0
    count_average = zeros(150)

    def callback():
        # text the user back who is using the laundry that it's done
        laundry_finished_send_txt(person)

        # change status of who is using the laundry on the server
        laundry_user_update()
        w["text"] = "Touch your name after starting the machine."

    def wash_status():
        global count_average
        global count
        status = port.read()
        active = open('active.txt', 'a')
        if count < 149:
            if status == "A":
                active.write("in use" + '\n')
                count_average[count] = 1
                count += 1
                master.after(2000, wash_status)
            elif status == "F":
                active.write("not in use" + '\n')
                count_average[count] = 0
                count += 1
                master.after(2000, wash_status)
            else:
                print "ShIT"
        else:
            if average(count_average) < .09:
                print average(count_average)
                active.close()
                callback()

            else:
                print average(count_average)
                count = 0
                count_average = zeros(150)
                master.after(2000, wash_status)

    wash_status()


def laundry_user_update(person=None):
    from twilio.rest import TwilioRestClient
    # Find these values at https://twilio.com/user/account
    account_sid = "ACa2c60a7edd652f75cdc21ac18aa73224"
    auth_token = "9c16781b8d01416645a26c0a24b0c727"
    client = TwilioRestClient(account_sid, auth_token)
    if person is None:
        client.phone_numbers.update("PNaf257815e539329eaad82b6c21160c0d",
                                    voice_url="http://demo.twilio.com/docs/voice.xml",
                                    sms_url="http://twimlets.com/echo?Twiml=%3CResponse%3E%3CMessage%3E" +
                                            "No+one" +
                                            "+is+using+the+laundry+now.%3C%2FMessage%3E%3C%2FResponse%3E")
    else:
        client.phone_numbers.update("PNaf257815e539329eaad82b6c21160c0d",
                                    voice_url="http://demo.twilio.com/docs/voice.xml",
                                    sms_url="http://twimlets.com/echo?Twiml=%3CResponse%3E%3CMessage%3E" +
                                            person +
                                            "+is+using+the+laundry+now.%3C%2FMessage%3E%3C%2FResponse%3E")


def laundry_finished_send_txt(person):
    from twilio.rest import TwilioRestClient
    # Find these values at https://twilio.com/user/account
    account_sid = "ACa2c60a7edd652f75cdc21ac18aa73224"
    auth_token = "9c16781b8d01416645a26c0a24b0c727"
    client = TwilioRestClient(account_sid, auth_token)
    client.messages.create(to=phone_book[person], from_="+13473219745",
                           body=person + ", your laundry has finished.")


for names in enumerate(people):
    button = Button(f,
                    text=names[1],
                    command=lambda name=names[1]: monitor_machine(name),
                    font=font_opt,
                    bg=colors[names[0]])
    button.pack(fill=BOTH, expand=1)
    phone_book[names[1]] = phone_number[names[0]]
laundry_user_update()
mainloop()
