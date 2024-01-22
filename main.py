import socketserver
import os
import calendar
import re
from datetime import datetime
from dotenv import load_dotenv
from netmiko import ConnectHandler


#Your SERVER Configuration
SERVER_IP = "0.0.0.0" # your NIC IP
SERVER_PORT = "514"

#log location
dir = "path/to/backup-folder"

#loading enviroment variables
load_dotenv()


#USERNAME-TacAcs+
username = os.getenv("DEVICE_USERNAME")

#PASSWORD-TacAcs+
password = os.getenv("DEVICE_PASSWORD")

#SECRET-TacAcs+
enable_secret = os.getenv("DEVICE_ENABLE_PASSWORD")


#checks for missing months and years in backup folder
def dir_tree(dir):
    os.chdir(dir)
    year = datetime.now().strftime("%Y")
    month = calendar.month_name[int(datetime.now().strftime("%m"))]
    day = datetime.now().strftime("%Y-%m-%d")
    years = os.listdir()
    if year not in years:
        os.mkdir(f'{year}/')
        os.chdir(f'{year}/')
        months = os.listdir()
        if month not in months:
            os.mkdir(f'{month}/')
            os.chdir(f'{month}/')
            days = os.listdir()
            if day in days:
                os.chdir("./"+day+"/")
            else:
                os.mkdir("./"+day+"/")
                os.chdir("./"+day+"/")
        else:
            os.chdir(f'{month}/')
            days = os.listdir()
            if day in days:
                os.chdir("./"+day+"/")
            else:
                os.mkdir("./"+day+"/")
                os.chdir("./"+day+"/")
    else:
        os.chdir(f'{year}/')
        months = os.listdir()
        if month not in months:
            os.mkdir(f'{month}/')
            os.chdir(f'{month}/')
            days = os.listdir()
            if day in days:
                os.chdir("./"+day+"/")
            else:
                os.mkdir("./"+day+"/")
                os.chdir("./"+day+"/")
        else:
            os.chdir(f'{month}/')            
            days = os.listdir()
            if day in days:
                os.chdir("./"+day+"/")
            else:
                os.mkdir("./"+day+"/")
                os.chdir("./"+day+"/")



#detects the connecting device
def detect_hostname(device,connection,):
    prompt = connection.send_command("show version")
    if re.search("JUNOS",prompt):
        hostname = connection.find_prompt()
        connection.disconnect()
        #user = hostname.replace(device['username'],"")    
        #user = user[1:-1] 
        return hostname[:-1]
        
    else:#re.match("Cisco",version):
        hostname = connection.find_prompt()
        connection.disconnect()
        return hostname[:-1]


def Connect(username,password,enable_secret,ip):
    try:
        device = {
            'device_type': 'autodetect',
            'ip': ip,
            'username': username,
            'password': password,
            'secret':enable_secret
        }

        try:
            net_connect_try = ConnectHandler(**device)
            hostname = detect_hostname(device, net_connect_try)
            return hostname

        except Exception as err:
            #this is for further debuging if ssh or telet is operating on different port
            if re.search("Wrong TCP port",str(err)) or re.search("Login Failed:",str(err)):
                try:
                    device["device_type"] = 'cisco_ios_telnet'
                    net_connect_try = ConnectHandler(**device)
                    hostname = detect_hostname(device, net_connect_try)
                    return hostname
                except:
                    device["device_type"] = 'juniper_junos_telnet'
                    del device["secret"]
                    net_connect_try = ConnectHandler(**device)
                    hostname = detect_hostname(device, net_connect_try)
                    return hostname
            

    except Exception as err:
        print(err)
        print(device['ip'])  

    


#Handles the SYSLOG request from the clients and logs them
class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        dir_tree(dir=dir)
        ip = self.client_address[0]
        if any([True if ip == name.split("-")[1][1:-1] else False for name in os.listdir()]):
            for name in os.listdir():
                if ip == name.split("-")[1][1:-1]:
                    hostname = name.split(" ")[0]
            #timestamp
            day = datetime.now().strftime("%Y;%m;%d")
            #filename
            LOG_FILE = f"{hostname} - {ip} - {day}.txt"
            #logging.basicConfig(level=logging.DEBUG, format='%(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=LOG_FILE, filemode='a')
            data = bytes.decode(self.request[0].strip())
            with open(LOG_FILE,"a") as file:
                file.write(data+"\n")
                return 0
        else:
            hostname = Connect(username,password,enable_secret,ip)
            day = datetime.now().strftime("%Y;%m;%d")
            #filename
            LOG_FILE = f"{hostname} - {ip} - {day}.txt"
            #logging.basicConfig(level=logging.DEBUG, format='%(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=LOG_FILE, filemode='a')
            data = bytes.decode(self.request[0].strip())
            with open(LOG_FILE,"a") as file:
                file.write(data+"\n")
                return 0

if __name__ == "__main__":
    try:
        #starts the server
        with socketserver.UDPServer((SERVER_IP, int(SERVER_PORT)), MyUDPHandler) as server:
            server.serve_forever()

    #Handling the Stopin of the server
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")
