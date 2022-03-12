from jnpr.junos import Device
import time
import os
from termcolor import colored


class judev:
    def __init__(self,ip,user,password):
        self.ip = ip
        self.user = user
        self.password = password

    def getrpc(self,rpc):
        rpc = rpc.replace('-','_')
        with Device(host=self.ip,user=self.user,password=self.password) as dev:
            return eval(f'dev.rpc.get_{rpc}()')

    def get_intinfo(self):
        x = self.getrpc('configuration')
        focus = x.findall('.//interfaces/interface')
        self.intinfo = dict()
        for i in focus:
            interface = i.find('name').text
            if i.find('description') is not None:
                descriptor0 = i.find('description').text
            else:
                descriptor0 = 'None'
            for j in i.findall('.//unit'):
                subinterface = f"{interface}.{j.find('name').text}"
                if i.find('.//description') is not None:
                    description = i.find('.//description').text
                else:
                    description = descriptor0
                ip = i.find('.//address/name').text
                self.intinfo[subinterface] = (description, ip)
        return self.intinfo

    def check_isis(self):
        while True:
            self.get_isadj()
            self.get_isconf()
            self.get_intinfo()
            judev.print_nei(self.isconf,self.isadj,self.intinfo)
            time.sleep(1)
            # os.system('clear')

    def check_ospf(self):
        while True:
            os.system('clear')
            self.get_osnei()
            self.get_osconf()
            self.get_intinfo()
            judev.print_nei(self.osconf,self.osnei,self.intinfo)
            time.sleep(1)

    def get_isadj(self):
        x = self.getrpc('isis-adjacency-information')
        adj = x.findall('.//isis-adjacency')
        self.isadj = dict()
        for i in adj:
            interface = i.find('interface-name').text
            neighbor = i.find('system-name').text
            state = i.find('adjacency-state').text
            self.isadj[interface] = (neighbor, state)
        return self.isadj

    def get_isconf(self):
        x = self.getrpc('configuration')
        interface = x.findall('.//isis/interface')
        self.isconf = sorted({i.find('name').text for i in interface})
        return self.isconf

    def get_osnei(self):
        x = self.getrpc('ospf-neighbor-information')
        adj = x.findall('.//ospf-neighbor')
        self.osnei = dict()
        for i in adj:
            interface = i.find('interface-name').text
            neighbor = i.find('neighbor-id').text
            state = i.find('ospf-neighbor-state').text
            self.osnei[interface] = (neighbor, state)
        return self.osnei

    def get_osconf(self):
        x = self.getrpc('configuration')
        interface = x.findall('.//area/interface')
        self.osconf = sorted({i.find('name').text for i in interface})
        return self.osconf



    @staticmethod
    def print_nei(conf,neighbor,intinfo):
        for i in conf:
            if 'lo' not in i:
                if i in neighbor.keys():
                    if neighbor[i][1] == 'Up':
                        print(colored(f"[+] Interface {i:14s} | {neighbor[i][0]:16s} | {neighbor[i][1]:14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}",'blue'))
                    else:
                        print(f"[*] Interface {i:14s} | {neighbor[i][0]:16s} | {neighbor[i][1]:14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}")
                else:
                    print(colored(f"[-] Interface {i:14s} | {'UNKNOWN':16s} | {'UNKNOWN':14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}",'red'))
