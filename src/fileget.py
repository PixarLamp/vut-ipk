#!/usr/bin/env python3
import sys
import socket
import re
import os

#checks correctness of the nameserver agr.
def nameserver_check(nameserv):
    if re.match('^(\d{1,3}.){3}\d{1,3}:\d{1,5}$', nameserv):
        nameserver = sys.argv[2]
        return nameserv
    else:
        sys.stderr.write("Wrong NAMESERVER arg\n")
        exit()
#checks correctness of the given surl agr.
def surl_check(surl):
    if re.match('^(fsp:\/\/)([.\w-]+\/)+([.\w-]+|\*)$', surl):
        return surl
    else:
        sys.stderr.write("Wrong SURL arg\n")
        exit()
#checks validity of the port from the args.
def port_check(pt):
    if pt > 65535 or pt == 0:
        sys.stderr.write("Wrong port\n")
        exit()
    return
#creates udp socket, returns the desired port if udp request does not succeed the program ends
def nsp(domain, ip_addr, port_no):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto((("WHEREIS " + domain + "\r\n").encode('utf-8')), (ip_addr, port_no))
    msgFromServer = udp_socket.recv(2048)
    message = (msgFromServer).decode('utf-8')
    udp_socket.close()
    if message == "ERR Syntax":
        sys.stderr.write("NSP ERR Syntax\n")
        exit()
    if message == "ERR Not Found":
        sys.stderr.write("NSP ERR Not found\n")
        exit()
    return message
#gets one line of a fsp rely on request and returns it
def get_answer():
    char = ""
    msg = ""
    while char != "\n":
        char = (fsp_socket.recv(1)).decode('utf-8')
        msg = msg + char
    return msg

#creates and coppies the desired file
def copy_file(length, f_name, tmpindex):
    if tmpindex == True:
        f_name = "indextmp"
    length_split = length.split(":")
    bit_size = int(length_split[1].strip())
    fsp_socket.recv(2)  
    buffer = 10
    no_of_cycles = (bit_size // buffer) + (bit_size % buffer > 0)
    f = open(f_name, "wb")
    for i in range(no_of_cycles):
        f.write(fsp_socket.recv(buffer))
    f.close()
    return

#requests the given file
def fsp_request(path, domain):
    fsp_socket.send(("GET " + path + " FSP/1.0\r\n").encode('utf-8'))
    fsp_socket.send(("Hostname: " + domain + "\r\n").encode('utf-8'))
    fsp_socket.send(("Agent: xhrklo00\r\n").encode('utf-8'))
    fsp_socket.send(("\r\n").encode('utf-8'))
    return

#checks whether the fsp request succeeded, if not program ends
def state_check(state):
    if state == "FSP/1.0 Bad Request" or state == "FSP/1.0 Not Found" or state == "FSP/1.0 Server Error":
        sys.stderr.write(state + "\n")
        length = get_answer()
        length_split = length.split(":")
        bit_size = int(length_split[1].strip())
        fsp_socket.recv(2)  
        buffer = 10
        no_of_cycles = (bit_size // buffer) + (bit_size % buffer > 0)
        msg = ""
        for i in range(no_of_cycles):
            msg = msg + (fsp_socket.recv(buffer).decode('utf-8'))
        sys.stderr.write(msg + "\n")
        exit()
    return

nameserver = ""
surl = ""
got_nameserver = False
got_surl = False
if len(sys.argv) != 5:
    sys.stderr.write("Wrong number of arguments\n")
    exit()
if sys.argv[1] == "-n":
    nameserver = nameserver_check(sys.argv[2])
    got_nameserver = True
elif  sys.argv[1] == "-f":
    surl = surl_check(sys.argv[2])
    got_surl = True
else:
    sys.stderr.write("Wrong agrument\n")
    exit()
if sys.argv[3] == "-n" and got_nameserver == False:
    nameserver = nameserver_check(sys.argv[4])
elif  sys.argv[3] == "-f" and got_surl == False:
    surl = surl_check(sys.argv[4])
else:
    sys.stderr.write("Wrong agrument\n")
    exit()

tmp_index = False
x = nameserver.split(":")
ip = x[0]
port = int(x[1])
port_check(port)
y = surl.split("/")
domain_name = y[2]
filename = y[-1]
path = '/'.join(y[3:])
msg = nsp(domain_name, ip, port)
a = msg.split(":")
port_rec = int(a[1])
addr = (ip, port_rec)
fsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fsp_socket.connect(addr)
if path == "*":
    tmp_index = True
    filename = "index" 
    fsp_request(filename, domain_name)
    state = get_answer()
    state_check(state)
    length = get_answer()
    copy_file(length, filename, tmp_index)
    fsp_socket.close()
    #got index file
    f = open("indextmp", "r")
    for x in f: #going through lines of index file
        tmp_index = False
        fsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fsp_socket.connect(addr)
        line = x.strip()
        path = line
        filename = (path.split("/"))[-1]
        fsp_request(path, domain_name)
        state = get_answer()
        state_check(state)
        length = get_answer()
        copy_file(length, filename, tmp_index)
        fsp_socket.close()
    f.close()
    os.remove("indextmp") 
else:
    fsp_request(path, domain_name)
    state = get_answer().strip()
    state_check(state)
    length = get_answer()
    copy_file(length, filename, tmp_index)
fsp_socket.close()