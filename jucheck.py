from jnpr.junos import Device
import time
import os
from termcolor import colored


class judev:
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password

    @staticmethod
    def get_intinfo(x):
        focus = x.findall('.//interfaces/interface')
        intinfo = dict()
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
                intinfo[subinterface] = (description, ip)
        return intinfo

    def check_isis(self):
        with Device(self.ip, user=self.user, password=self.password) as dev:
            while True:
                os.system('clear')
                isadj = judev.get_isadj(
                    dev.rpc.get_isis_adjacency_information())
                isconf = judev.get_isconf(dev.rpc.get_configuration())
                intinfo = judev.get_intinfo(dev.rpc.get_configuration())
                judev.print_nei(isconf, isadj, intinfo)
                time.sleep(3)

    @staticmethod
    def get_isadj(x):
        adj = x.findall('.//isis-adjacency')
        isadj = dict()
        for i in adj:
            interface = i.find('interface-name').text
            neighbor = i.find('system-name').text
            state = i.find('adjacency-state').text
            isadj[interface] = (neighbor, state)
        return isadj

    @staticmethod
    def get_isconf(x):
        interface = x.findall('.//isis/interface')
        isconf = sorted({i.find('name').text for i in interface})
        return isconf

    def check_ospf(self):
        with Device(self.ip, user=self.user, password=self.password) as dev:
            while True:
                os.system('clear')
                osnei = judev.get_osnei(
                    dev.rpc.get_ospf_neighbor_information())
                osconf = judev.get_osconf(dev.rpc.get_configuration())
                intinfo = judev.get_intinfo(dev.rpc.get_configuration())
                judev.print_nei(osconf, osnei, intinfo)
                time.sleep(3)

    @staticmethod
    def get_osnei(x):
        adj = x.findall('.//ospf-neighbor')
        osnei = dict()
        for i in adj:
            interface = i.find('interface-name').text
            neighbor = i.find('neighbor-id').text
            state = i.find('ospf-neighbor-state').text
            osnei[interface] = (neighbor, state)
        return osnei

    @staticmethod
    def get_osconf(x):
        interface = x.findall('.//area/interface')
        osconf = sorted({i.find('name').text for i in interface})
        return osconf

    @staticmethod
    def print_nei(conf, neighbor, intinfo):
        for i in conf:
            if 'lo' not in i:
                if i in neighbor.keys():
                    if neighbor[i][1] == 'Up':
                        print(colored(
                            f"[+] Interface {i:14s} | {neighbor[i][0]:16s} | {neighbor[i][1]:14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}", 'blue'))
                    else:
                        print(
                            f"[*] Interface {i:14s} | {neighbor[i][0]:16s} | {neighbor[i][1]:14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}")
                else:
                    print(colored(
                        f"[-] Interface {i:14s} | {'UNKNOWN':16s} | {'UNKNOWN':14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}", 'red'))


if __name__ == '__main__':
    r5 = judev('172.16.1.5', 'root', 'root123')
    r5.check_ospf()
