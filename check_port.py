from csv import writer
import csv
import logging
from pyats import aetest
from pyats.topology import loader
import pandas as pd

log = logging.getLogger(__name__)
source_testbed = loader.load('sourcetestbed.yml')
target_testbed = loader.load('targettestbed.yml')


###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################
class common_setup(aetest.CommonSetup):
    @aetest.subsection
    def connectdevices(self):
        log.info("Connecting to  devices.....")
        try:
            for device in source_testbed.devices:
                device1 = source_testbed.devices[device]
                device1.connect()

            for device in target_testbed.devices:
                device1 = target_testbed.devices[device]
                device1.connect()
            log.info("Connection established")
        except():
            log.info("Connection rejected")
            exit()


class SourceInterface(aetest.Testcase):
    @aetest.test
    def source_interface(self):
        # opening a file to write the log data
        f = open("log/source_log.txt", "w")
        open("log/source_up.csv", "w")
        f.write("==========Source port information==========")
        for device in source_testbed.devices:
            device1 = source_testbed.devices[device]
            # Show all the ports of a switch and write in the file
            sourcedevice1 = device1.execute("sh ip int br")
            f = open("log/source_log.txt", "a")
            f.write('\n' + "==========" + device + "==========" + '\n')
            f.write(sourcedevice1)
            log.info("device summery:" + '\n' + "%s" % sourcedevice1)
            f.close()
            # to check up ports for every switch we save log file for every switch to a file
            temp = open("log/onesource.txt", "w")
            temp.write(sourcedevice1)
            temp.close()
            with open("log/onesource.txt") as file:
                for line in file:
                    line = line.rstrip()
                    # check if the line contains 'up'
                    if "up" in line and line.find('Vlan') == -1 and line.find("Gig") == -1 and line.find(
                            "Null") == -1:
                        word = line.split(' ')[0]
                        show_vlan = device1.execute("sh interface " + word + " switchport")
                        temp = open("log/vlan.txt", "w")
                        temp.write(show_vlan)
                        temp.close()
                        with open("log/vlan.txt") as vlan_file:
                            for each in vlan_file:
                                each = each.rstrip()
                                if "Access Mode VLAN:" in each:
                                    vlan_array = each.split(" ")
                                    vlan_value = vlan_array[len(vlan_array)-2]
                                    print(vlan_value)
                                    break
                                else:
                                    vlan_value = " "
                        show_mac = device1.execute("show mac interface " + word)
                        mac_file = open("log/mac_log.txt", "w")
                        mac_file.write(show_mac + '\n')
                        mac_file.close()
                        mac_address = ''
                        with open("log/mac_log.txt", 'r') as tac:
                            for lines in tac:
                                if word in lines:
                                    mac_address = lines.split(' ')[0]

                        row_contents = [device, word, 'up', vlan_value, mac_address]
                        # append all the port data that has status up by calling a class method
                        self.append_list('log/source_up.csv', row_contents)
        f.close()
        try:
            df = pd.read_csv('log/source_up.csv', header=None)
            df.rename(columns={0: 'Switch', 1: 'Port', 2: 'Status', 3: 'VLAN', 4: 'Connected MAC'}, inplace=True)
            df.to_csv('log/source_up.csv', index=False)  # save to new csv file
        except pd.errors.EmptyDataError:
            print("Error!! No data received from switch")

    def append_list(self, file, data):
        with open(file, 'a', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(data)


class TargetInterface(aetest.Testcase):
    @aetest.test
    def target_interface(self):
        open('log/target_down.csv', 'w', newline='')
        log.info("Retrieving unused interface information...")
        f = open("log/target_log.txt", "w")
        f.write("==========Target port information==========" + '\n')
        for device in target_testbed.devices:
            device1 = target_testbed.devices[device]
            targetdevice1 = device1.execute("sh ip int br")
            unused_interface = targetdevice1.find("down")
            f = open("log/target_log.txt", "a")
            f.write('\n' + "==========" + device + "==========" + '\n')
            f.write(targetdevice1)
            if unused_interface == -1:
                log.info("no unused ports")
                f.write('\n' + "no unused ports" + '\n')
                num = 0
            else:
                num = targetdevice1[(unused_interface - 2)]
            log.info("number of unused ports are %s" % num)
            log.info("device summery:" + '\n' + "%s" % targetdevice1)
            f.write('\n' + "===========================================")
            f.close()
            temp = open("log/onetarget.txt", "w")
            temp.write(targetdevice1)
            temp.close()
            with open("log/onetarget.txt") as file:
                for line in file:
                    line = line.rstrip()
                    if "down" in line and line.find('Vlan') == -1 and line.find("Gig") == -1 and line.find(
                            "Null") == -1:
                        word = line.split(' ')[0]
                        row_contents = [device, word, 'down']
                        self.append_list('log/target_down.csv', row_contents)
        f.close()
        df = pd.read_csv('log/target_down.csv', header=None)
        df.rename(columns={0: 'Switch', 1: 'Port', 2: 'Status'}, inplace=True)
        df.to_csv('log/target_down.csv', index=False)  # save to new csv file

    def append_list(self, file, data):
        with open(file, 'a', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(data)


class MatchPort(aetest.Testcase):
    @aetest.test
    def match_port(self):
        report = open("log/report.txt", "w")
        open("log/report_log.csv", "w", newline='')
        port = {'source_port': [], 'target_port': [], 'source_switch': [], 'target_switch': []}

        length = 0
        with open("log/source_up.csv", 'r') as s:
            data = csv.DictReader(s, delimiter=',')
            for values in data:
                port["source_switch"].append(values['Switch'])
                port["source_port"].append(values['Port'])
                length = length + 1
        with open("log/target_down.csv", 'r') as t:
            data = csv.DictReader(t, delimiter=',')
            for values in data:
                port["target_switch"].append(values['Switch'])
                port["target_port"].append(values['Port'])
        report.write("=======================Source and target matching===================")
        report.write('\n')
        a = 0
        while a < length:
            log.info("%s ------> %s" % (port['source_port'][a], port['target_port'][a]))
            report.write('(' + port["source_switch"][a] + ') ' + port["source_port"][a] + '  ----->  ' + '(' +
                         port["target_switch"][a] + ') ' + port['target_port'][a] + '\n')
            # Write in csv file
            row_contents = [port["source_switch"][a], port["source_port"][a], port["target_switch"][a],
                            port['target_port'][a]]
            self.append_list('log/report_log.csv', row_contents)
            a = a + 1
        df = pd.read_csv('log/report_log.csv', header=None)
        df.rename(columns={0: 'Source Switch', 1: 'Source Port', 2: 'Target Switch', 3: 'Target Port'}, inplace=True)
        df.to_csv('log/report_log.csv', index=False)  # save to new csv file

    def append_list(self, file, data):
        with open(file, 'a', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(data)


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def clean_everything(self):
        log.info("Aetest Common Cleanup ")
        for device in source_testbed.devices:
            device1 = source_testbed.devices[device]
            device1.disconnect()

        for device in target_testbed.devices:
            device1 = target_testbed.devices[device]
            device1.disconnect()


if __name__ == '__main__':  # pragma: no cover
    logging.getLogger(__name__).setLevel(logging.ERROR)
    logging.getLogger('pyats.aetest').setLevel(logging.ERROR)
    aetest.main()
