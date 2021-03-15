#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import socket
import json
import argparse
import threading
from pathlib import Path
import uuid

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

result = '{} {} {} {} {} {}'
root = tk.Tk()
root.title("Carsharing Client")

text = tk.Text(master=root)
text.pack(expand=True, fill="both")
text.tag_config('remote', foreground="blue")
text.tag_config('notification', foreground="yellow", background='black')

entry = tk.Entry(master=root)
entry.pack(expand=True, fill="x")

frame = tk.Frame(master=root)
frame.pack()

status = tk.Button(master=frame, text='Disconnected', bg='red')
status.pack(side="left")

authStatus = tk.Button(master=frame, text='Not-authorized', bg='orange')
authStatus.pack(side="left")

def buttons():
    for i in "Connect", "Register", "Authenticate", "Send", "Clear", "Exit":
        b = tk.Button(master=frame, text=i)
        b.pack(side="left")
        yield b


b1, b2, b3, b4, b5, b6 = buttons()


def print_system_notification(message):
    data = str(message)
    now = str(datetime.now())[:-7]
    text.insert("insert", "({}) : {}\n".format(now, data), 'notification')


class Client:
    host = '127.0.0.1'
    port = 65432
    info = dict()
    #  TODO flag in clasa

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.userId = ""
        self.userAge = ""
        self.userDriverLicense = ""
        self.userEmail = ""
        self.userPhone = ""
        self.uuid = uuid.uuid1()

    def register_client(self):
        popup = tk.Toplevel()
        popup.title = "Form"
        user_id_entry = tk.Entry(master=popup)
        user_id_entry.grid(row=0, column=0)
        user_id_label = tk.Label(popup, text="user id:")
        user_id_label.grid(row=0, column=1)

        user_age_entry = tk.Entry(master=popup)
        user_age_entry.grid(row=1, column=0)
        user_age_label = tk.Label(popup, text="user age:")
        user_age_label.grid(row=1, column=1)

        user_drivers_license_entry = tk.Entry(master=popup)
        user_drivers_license_entry.grid(row=2, column=0)
        user_drivers_license_label = tk.Label(popup, text="user drivers license:")
        user_drivers_license_label.grid(row=2, column=1)

        user_email_entry = tk.Entry(master=popup)
        user_email_entry.grid(row=3, column=0)
        user_email_label = tk.Label(popup, text="user email:")
        user_email_label.grid(row=3, column=1)

        user_phone_entry = tk.Entry(master=popup)
        user_phone_entry.grid(row=4, column=0)
        user_phone_label = tk.Label(popup, text="user phone:")
        user_phone_label.grid(row=4, column=1)

        var1 = tk.IntVar()
        check = tk.Checkbutton(popup, text="Agree to terms", variable=var1).grid(row=5, column =0)

        new_button = tk.Button(master=popup, text="Enter")
        new_button.grid(row=6, column=0)

        def register_command():
            now = str(datetime.now())[:-7]
            print_system_notification(var1)

            if user_id_entry.get() == "" or user_age_entry.get() == "" or user_drivers_license_entry.get() == "" or var1.get() == 0:
                print_system_notification('Data is incomplete. Please complete all fields')
            else:
                self.admitFlag = 1
                self.userId = user_id_entry.get()
                self.userAge = user_age_entry.get()
                self.userDriverLicense = user_drivers_license_entry.get()
                self.userEmail = user_email_entry.get()
                self.userPhone = user_phone_entry.get()
                print_system_notification('Succesfully registered client data: user id:' + self.userId + ' user age:' + self.userAge + ' user drivers license:' + self.userDriverLicense
                                          + 'user email:' + self.userEmail + ' user phone:' + self.userPhone)
                popup.destroy()

        new_button.configure(command=register_command)

    def authenticate(self):
        if self.admitFlag:
            print_system_notification('authentication ongoing')
            result = "authenticate: {} {} {} {}".format(self.userId, self.userAge,self.userDriverLicense,self.userEmail ,self.userPhone)
            self.sendToServer(result)
        else:
            print_system_notification('CANT AUTHENTICATE')
    def set_address(self, host, port):
        self.host = host
        self.port = port

    def connect(self):

        if self.admitFlag:
            now = str(datetime.now())[:-7]
            try:
                self.s.connect((self.host, self.port))
                text.insert("insert", "({}) : Connected.\n".format(now))
                msg = str(self.uuid)
                self.s.sendall(bytes(msg.encode("utf-8")))
                self.receive()
            except ConnectionRefusedError:
                text.insert("insert", "({}) : The server is not online.\n".format(now))
        else:
            text.insert("insert", "INSERT AUTHENTICATE DATA FIRST.\n")

    def handle_message(self, command):
        if command == 'authorized':
            print_system_notification('authorized')
            authStatus.configure(bg='blue', text='Authorized')

        if command == 'not-authorized':
            print_system_notification('not-authorized')
            authStatus.configure(bg='orange', text='Not-authorized')

        if command.startswith('end-rental'):
            print_system_notification(command)
            authStatus.configure(bg='orange', text='Not-authorized')

    def receive(self):
        status.configure(bg='green', text='Connected')
        while True:
            data = str(self.s.recv(1024))[2:-1]
            now = str(datetime.now())[:-7]
            if len(data) == 0:
                pass
            else:
                text.insert("insert", "({}) : {}\n".format(now, data), 'remote')
                self.handle_message(data)

    def do_nothing(self):
        pass

    def send(self):
        respond = "{} {} ".format(str(self.uuid), str(entry.get()))
        self.send_bytes_to_server(respond)

    def sendToServer(self, string):
        respond = "{} {}".format(str(self.uuid), string)
        self.send_bytes_to_server(respond)

    def send_bytes_to_server(self, respond):
        now = str(datetime.now())[:-7]
        entry.delete("0", "end")
        try:
            self.s.sendall(bytes(respond.encode("utf-8")))
            text.insert("insert", "({}) : sent msg ({})\n".format(now, respond))
        except BrokenPipeError:
            text.insert("insert", "\nDate: {}\Server has been disconnected.\n".format(now))
            self.s.close()


c1 = Client()


def connect():
    t1 = threading.Thread(target=c1.connect)
    t1.start()


def register():
    c1.register_client()


def authenticate():
    c1.authenticate()


def send():
    t2 = threading.Thread(target=c1.send)
    t2.start()


def clear():
    text.delete("1.0", "end")


def destroy():
    root.destroy()
    status.configure(bg='red', text='Disconnected')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Carsharing Client')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    c1.set_address(args.host, args.p)
    b1.configure(command=connect)
    b2.configure(command=register)
    b3.configure(command=authenticate)
    b4.configure(command=send)
    b5.configure(command=clear)
    b6.configure(command=destroy)

    t0 = threading.Thread(target=root.mainloop)
    t0.run()
