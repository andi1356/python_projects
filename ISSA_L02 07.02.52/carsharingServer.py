#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import socket
import json
import argparse
import threading
from pathlib import Path

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


root = tk.Tk()
root.title("Carsharing Server")

text = tk.Text(master=root)
text.pack(expand=True, fill="both")
text.tag_config('remote', foreground="blue")
text.tag_config('notification', foreground="yellow", background='black')

entry = tk.Entry(master=root)
entry.pack(expand=True, fill="x")

frame = tk.Frame(master=root)
frame.pack()

status = tk.Button(master=frame, text='Disconnected', fg='red')
status.pack(side="left")


def buttons():
    for i in "Start", "Send", "Clear", "Exit":
        b = tk.Button(master=frame, text=i)
        b.pack(side="left")
        yield b


b1, b2, b3, b4, = buttons()


def print_system_notification(message):
    data = str(message)
    now = str(datetime.now())[:-7]
    text.insert("insert", "({}) : {}\n".format(now, data), 'notification')


class Server:
    clients = []

    auth_clients = list()

    host = '127.0.0.1'
    port = 65432

    def __init__(self):
        self.rental = ['']
        self.parse_configuration_file()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def parse_configuration_file(self):
        script_location = Path(__file__).absolute().parent
        file_location = script_location / 'cars.json'
        with open(file_location, 'r') as content_file:
            content = content_file.read()
            print('content = ', content)
            self.parse_json(content)

    def parse_json(self, json_to_be_parsed):
        print_system_notification('Parsing Json File...')
        json_array_of_clients = json.loads(json_to_be_parsed)
        for key in json_array_of_clients:
            print_system_notification('key=' + key)
            print_system_notification("[" + key + "] = " + str(json_array_of_clients[key]))
            for auth_client in json_array_of_clients[key]:
                self.auth_clients.append(auth_client)

    def set_address(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen(10)
        now = str(datetime.now())[:-7]
        text.insert("insert", "({}) : Started.\n".format(now))
        self.condition()

    def accept(self):
        c, addr = self.s.accept()
        self.clients.append(c)
        data = c.recv(1024)
        status.configure(fg='green', text='Connected')
        # text.insert("insert", "({}) : {} connected.\n".format(str(datetime.now())[:-7], str(data)[1:]))

    def handle_message(self, command):
        if command.startswith('start-rental'):
            if command[-7:] in Server.auth_clients:
                print_system_notification('start-rental')
                self.send_bytes_to_client('authorized')
                self.rental.append(command[-7:])

            else:
                self.send_bytes_to_client('not authorized')


        if command.startswith('end-rental'):
            if command[-7:] in self.rental:
                print_system_notification('end-rental success')
                self.send_bytes_to_client('authorized')
            else:
                print_system_notification('end-rental error')
                self.send_bytes_to_client('not authorized')

    def receive(self):
        for i in self.clients:

            def f():
                data = str(i.recv(1024))[2:-1]
                now = str(datetime.now())[:-7]
                if len(data) == 0:
                    pass
                else:
                    text.insert("insert", "({}) : {}\n".format(now, data), 'remote')
                    self.handle_message(data)

            t1_2_1 = threading.Thread(target=f)
            t1_2_1.start()

    def condition(self):
        while True:
            t1_1 = threading.Thread(target=self.accept)
            t1_1.daemon = True
            t1_1.start()
            t1_1.join(1)
            t1_2 = threading.Thread(target=self.receive)
            t1_2.daemon = True
            t1_2.start()
            t1_2.join(1)

    def send(self):
        response = str(entry.get())
        self.send_bytes_to_client(response)

    def send_bytes_to_client(self, response):
        now = str(datetime.now())[:-7]
        entry.delete("0", "end")
        try:
            for i in self.clients:
                i.sendall(bytes(response.encode("utf-8")))
            text.insert("insert", "({}) : {}\n".format(now, response))
        except BrokenPipeError:
            text.insert("insert", "({}) : Client has been disconnected.\n".format(now))
            status.configure(fg='red', text='Disconnected')


s1 = Server()


def start():
    t1 = threading.Thread(target=s1.start)
    t1.start()


def send():
    t2 = threading.Thread(target=s1.send)
    t2.start()


def clear():
    text.delete("1.0", "end")


def destroy():
    root.destroy()
    exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Carsharing Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-port', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    s1.set_address(args.host, args.port)
    b1.configure(command=start)
    b2.configure(command=send)
    b3.configure(command=clear)
    b4.configure(command=destroy)
    t0 = threading.Thread(target=root.mainloop)
    t0.run()
