from jnpr.junos import Device
import time
import os
from termcolor import colored
from getpass import getpass


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
        print('NEIGHBOR TABLE' + '----' * 16 + 'Trung-VDT-0988886298-----')
        for i in conf:
            if 'lo' not in i:
                if i in neighbor.keys():
                    if neighbor[i][1] == 'Up' or neighbor[i][1] == 'Full':
                        print(colored(
                            f"[+] Interface {i:14s} | {neighbor[i][0]:16s} | {neighbor[i][1]:14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}", 'blue'))
                    else:
                        print(
                            f"[*] Interface {i:14s} | {neighbor[i][0]:16s} | {neighbor[i][1]:14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}")
                else:
                    print(colored(
                        f"[-] Interface {i:14s} | {'UNKNOWN':16s} | {'UNKNOWN':14s} | {intinfo[i][0]:15s} | {intinfo[i][1]}", 'red'))

    def check_lsp(self):
        with Device(self.ip, user=self.user, password=self.password) as dev:
            while True:
                ingress, egress, transit = judev.get_lsp(
                    dev.rpc.get_mpls_lsp_information())
                lspconf = judev.get_lspconf(dev.rpc.get_configuration())
                os.system('clear')
                ingress_up = [i for i in ingress if i['name'] in lspconf]
                # print(ingress_up, egress, transit, lspconf)
                judev.print_lsp(ingress_up, egress, transit)
                time.sleep(3)

    @staticmethod
    def print_lsp(ingress_up, egress, transit):
        print('Ingress' + '----' * 14 + 'Trung-VDT-0988886298----')
        for i in ingress_up:
            if i['state'] == 'Up':
                print(colored(
                    f"[+] Name {i['name']:14s} | Source {i['source']:16s} | Destination {i['destination']:14s} | {i['state']:15s}", 'blue'))
            else:
                print(colored(
                    f"[-] Name {i['name']:14s} | Source {i['source']:16s} | Destination {i['destination']:14s} | {i['state']:15s}", 'red'))
        print('Egress ' + '----' * 20)
        for i in egress:
            if i['state'] == 'Up':
                print(colored(
                    f"[+] Name {i['name']:14s} | Source {i['source']:16s} | Destination {i['destination']:14s} | {i['state']:15s}", 'blue'))
            else:
                print(colored(
                    f"[-] Name {i['name']:14s} | Source {i['source']:16s} | Destination {i['destination']:14s} | {i['state']:15s}", 'red'))
        print('Transit' + '----' * 20)
        for i in transit:
            if i['state'] == 'Up':
                print(colored(
                    f"[+] Name {i['name']:14s} | Source {i['source']:16s} | Destination {i['destination']:14s} | {i['state']:15s}", 'blue'))
            else:
                print(colored(
                    f"[-] Name {i['name']:14s} | Source {i['source']:16s} | Destination {i['destination']:14s} | {i['state']:15s}", 'red'))

    @staticmethod
    def get_lspconf(x):
        lsp = x.findall('.//label-switched-path')
        lspconf = sorted({i.find('name').text for i in lsp})
        return lspconf

    @staticmethod
    def get_lsp(x):
        ingress = []
        egress = []
        transit = []

        ingress_xml = x.findall(
            './/rsvp-session-data[session-type="Ingress"]')
        for i in ingress_xml[0].findall('.//mpls-lsp'):
            source = i.find('source-address').text
            destination = i.find('destination-address').text
            lsp_state = i.find('lsp-state').text
            name = i.find('name').text
            value = (source, destination, lsp_state, name)
            keys = ('source', 'destination', 'state', 'name')
            ingress.append(dict(zip(keys, value)))

        egress_xml = x.findall(
            './/rsvp-session-data[session-type="Egress"]')
        for i in egress_xml[0].findall('.//rsvp-session'):
            source = i.find('source-address').text
            destination = i.find('destination-address').text
            lsp_state = i.find('lsp-state').text
            name = i.find('name').text
            value = (source, destination, lsp_state, name)
            keys = ('source', 'destination', 'state', 'name')
            egress.append(dict(zip(keys, value)))

        transit_xml = x.findall(
            './/rsvp-session-data[session-type="Transit"]')
        for i in transit_xml[0].findall('.//rsvp-session'):
            source = i.find('source-address').text
            destination = i.find('destination-address').text
            lsp_state = i.find('lsp-state').text
            name = i.find('name').text
            value = (source, destination, lsp_state, name)
            keys = ('source', 'destination', 'state', 'name')
            transit.append(dict(zip(keys, value)))

        return ingress, egress, transit


if __name__ == '__main__':
    print('-' * 15 + 'Trung-VDT-098886298' + '-' * 7)
    ip = input('Nhap dia chi IP quan tri' + ' ' * 9 + ': ')
    monitor = int(input('Lua chon 1(ospf), 2(isis), 3(lsp): '))
    username = input('Nhap username dang nhap' + ' ' * 10 + ': ')
    passwd = getpass('Nhap password dang nhap' + ' ' * 10 + ': ')

    try:
        p_router = judev(ip, username, passwd)
        if monitor == 1:
            p_router.check_ospf()
        elif monitor == 2:
            p_router.check_isis()
        elif monitor == 3:
            p_router.check_lsp()
        else:
            print('Lua chon khong co trong chuong trinh')
    except Exception as e:
        print("Lien he Trung-0988886298 de sua loi")

    # p_router = judev('172.16.1.5', 'root', 'root123')
    # p_router.check_ospf()
    # # p_router.check_lsp()
