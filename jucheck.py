from jnpr.junos import Device
import time
import os
from getpass import getpass
from prettytable import PrettyTable

R = "\033[0;31;40m"  # RED
G = "\033[0;32;40m"  # GREEN
Y = "\033[0;33;40m"  # Yellow
B = "\033[0;34;40m"  # Blue
N = "\033[0m"  # Reset


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
                try:
                    os.system('clear')
                    isadj = judev.get_isadj(
                        dev.rpc.get_isis_adjacency_information())
                    isconf = judev.get_isconf(dev.rpc.get_configuration())
                    intinfo = judev.get_intinfo(dev.rpc.get_configuration())
                    judev.print_nei(isconf, isadj, intinfo)
                    print('\n\nCtrl-C to quit')
                    time.sleep(3)
                except KeyboardInterrupt:
                    break

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
                try:
                    os.system('clear')
                    osnei = judev.get_osnei(
                        dev.rpc.get_ospf_neighbor_information())
                    osconf = judev.get_osconf(dev.rpc.get_configuration())
                    intinfo = judev.get_intinfo(dev.rpc.get_configuration())
                    judev.print_nei(osconf, osnei, intinfo)
                    print('\n\nCtrl-C to quit')
                    time.sleep(3)
                except KeyboardInterrupt:
                    break

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
        print('Contact Trung-VDT-0988886298 if error')
        print('--' * 19 + '\n')
        print('Adjacency Table')
        t = PrettyTable(['Status', 'Interface', 'Neighbor-ID',
                         'State', 'Description', 'InterfaceIP'])
        for i in conf:
            if 'lo' not in i:
                if i in neighbor.keys():
                    if neighbor[i][1] == 'Up' or neighbor[i][1] == 'Full':
                        state = '[+]'
                        t.add_row([B + state + N, B + i + N, B +
                                   neighbor[i][0] + N, B + neighbor[i][1] + N, B + intinfo[i][0] + N, B + intinfo[i][1] + N])
                    else:
                        state = '[*]'
                        t.add_row([Y + state + N, Y + i + N, Y +
                                   neighbor[i][0] + N, Y + neighbor[i][1] + N, Y + intinfo[i][0] + N, Y + intinfo[i][1] + N])
                else:
                    state = '[-]'
                    t.add_row([R + state + N, R + i + N, R +
                               'UNKNOWN' + N, R + 'UNKNOWN' + N, R + intinfo[i][0] + N, R + intinfo[i][1] + N])
        print(t)

    def check_lsp(self):
        with Device(self.ip, user=self.user, password=self.password) as dev:
            while True:
                try:
                    ingress, egress, transit = judev.get_lsp(
                        dev.rpc.get_mpls_lsp_information())
                    lspconf = judev.get_lspconf(dev.rpc.get_configuration())
                    os.system('clear')
                    ingress_up = [i for i in ingress if i['name'] in lspconf]
                    judev.print_lsp(ingress_up, egress, transit)
                    print('\n\nCtrl-C to quit')
                    time.sleep(3)
                except KeyboardInterrupt:
                    break

    @staticmethod
    def print_lsp(ingress_up, egress, transit):
        print('Contact Trung-VDT-0988886298 if error')
        print('--' * 19 + '\n')
        ingress_table = PrettyTable(
            ['Status', 'Name', 'Souce', 'Destination', 'State'])
        print('Ingress Table')
        for i in ingress_up:
            if i['state'] == 'Up':
                status1 = '[+]'
                ingress_table.add_row([B + status1 + N, B + i['name'] + N, B +
                                       i['source'] + N, B + i['destination'] + N, B + i['state'] + N])
            else:
                status1 = '[-]'
                ingress_table.add_row([R + status1 + N, R + i['name'] + N, R +
                                       i['source'] + N, R + i['destination'] + N, R + i['state'] + N])
        print(ingress_table)
        print('\nEgress Table')
        egress_table = PrettyTable(
            ['Status', 'Name', 'Souce', 'Destination', 'State'])

        for i in egress:
            if i['state'] == 'Up':
                status2 = '[+]'
                egress_table.add_row([B + status2 + N, B + i['name'] + N, B +
                                      i['source'] + N, B + i['destination'] + N, B + i['state'] + N])
            else:
                status2 = '[-]'
                egress_table.add_row([R + status2 + N, R + i['name'] + N, R +
                                      i['source'] + N, R + i['destination'] + N, R + i['state'] + N])
        print(egress_table)

        print('\nTransit Table')
        transit_table = PrettyTable(
            ['Status', 'Name', 'Souce', 'Destination', 'State'])
        for i in transit:
            if i['state'] == 'Up':
                status3 = '[+]'
                transit_table.add_row([B + status3 + N, B + i['name'] + N, B +
                                       i['source'] + N, B + i['destination'] + N, B + i['state'] + N])
            else:
                status2 = '[-]'
                transit_table.add_row([R + status3 + N, R + i['name'] + N, R +
                                       i['source'] + N, R + i['destination'] + N, R + i['state'] + N])
        print(transit_table)

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
    try:
        print('-' * 15 + 'Trung-VDT-098886298' + '-' * 7)
        ip = input('Nhap dia chi IP quan tri' + ' ' * 9 + ': ')
        monitor = int(input('Lua chon 1(ospf), 2(isis), 3(lsp): '))
        username = input('Nhap username dang nhap' + ' ' * 10 + ': ')
        passwd = getpass('Nhap password dang nhap' + ' ' * 10 + ': ')
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

    # p_router = judev('172.16.1.1', 'root', 'root123')
    # # p_router.check_ospf()
    # p_router.check_lsp()
