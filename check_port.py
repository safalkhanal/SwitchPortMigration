__author__ = "Safal Khanal"
__copyright__ = "Copyright 2021"
__credits__ = ["Safal Khanal"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Safal Khanal"
__email__ = "skhanal@respiro.com.au"
__status__ = "In Development"

import os
from os import path
from csv import writer
import csv
import logging
import time
from pyats import aetest
from pyats.topology import loader
import pandas as pd

DIR_PATH_NAME = time.strftime("%Y-%m-%d")

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
                device1.connect(init_config_commands=[])

            for device in target_testbed.devices:
                device1 = target_testbed.devices[device]
                device1.connect(init_config_commands=[])
            log.info("Connection established")
        except ConnectionError:
            log.info("Connection rejected")
            exit()

    @aetest.subsection
    def createlogdir(self):
        current_dir = os.getcwd()
        if not path.exists(current_dir + '/log'):
            os.system('mkdir ' + current_dir + '/log')
        if not path.exists(current_dir + '/log/' + DIR_PATH_NAME):
            os.system('mkdir ' + current_dir + '/log/' + DIR_PATH_NAME)


class SourceInterface(aetest.Testcase):
    @aetest.test
    def source_interface(self):
        # opening a file to write the log data
        f = open("log/" + DIR_PATH_NAME + "/source_log.txt", "w")
        open("log/" + DIR_PATH_NAME + "/source_up.csv", "w")
        f.write("==========Source port information==========")
        for device in source_testbed.devices:
            device1 = source_testbed.devices[device]
            # Show all the ports of a switch and write in the file
            sourcedevice1 = device1.execute("sh ip int br")
            f = open("log/" + DIR_PATH_NAME + "/source_log.txt", "a")
            f.write('\n' + "==========" + device + "==========" + '\n')
            f.write(sourcedevice1)
            log.info("device summery:" + '\n' + "%s" % sourcedevice1)
            f.close()
            # to check up ports for every switch we save log file for every switch to a file
            temp = open("log/" + DIR_PATH_NAME + "/onesource.txt", "w")
            temp.write("====This is the switch interface log fro the last switch in the provided excel list===\n")
            temp.write("====This file is used to check the interface status of each switch and select the connected "
                       "interface===\n")
            temp.write(sourcedevice1)
            temp.close()
            with open("log/" + DIR_PATH_NAME + "/onesource.txt") as file:
                for line in file:
                    line = line.rstrip()
                    # check if the line contains 'up'
                    if "up" in line and line.find('Vlan') == -1 and line.find("Gig") == -1 and line.find(
                            "Null") == -1:
                        word = line.split(' ')[0]
                        show_vlan = device1.execute("sh interface " + word + " switchport")
                        temp = open("log/" + DIR_PATH_NAME + "/vlan.txt", "w")
                        temp.write(show_vlan)
                        temp.close()
                        with open("log/" + DIR_PATH_NAME + "/vlan.txt") as vlan_file:
                            for each in vlan_file:
                                each = each.rstrip()
                                if "Access Mode VLAN:" in each:
                                    vlan_array = each.split(" ")
                                    vlan_value = vlan_array[len(vlan_array) - 2]
                                    break
                                else:
                                    vlan_value = " "
                        show_mac = device1.execute("show mac interface " + word)
                        mac_file = open("log/" + DIR_PATH_NAME + "/mac_log.txt", "w")
                        mac_file.write(show_mac + '\n')
                        mac_file.close()
                        mac_address = ''
                        with open("log/" + DIR_PATH_NAME + "/mac_log.txt", 'r') as tac:
                            for lines in tac:
                                if word in lines:
                                    mac_address = lines.split(' ')[0]

                        row_contents = [device, word, 'up', vlan_value, mac_address]
                        # append all the port data that has status up by calling a class method
                        self.append_list('log/' + DIR_PATH_NAME + '/source_up.csv', row_contents)
        f.close()
        try:
            df = pd.read_csv('log/' + DIR_PATH_NAME + '/source_up.csv', header=None)
            df.rename(columns={0: 'Switch', 1: 'Port', 2: 'Status', 3: 'VLAN', 4: 'ConnectedMAC'}, inplace=True)
            df.to_csv('log/' + DIR_PATH_NAME + '/source_up.csv', index=False)  # save to new csv file
        except pd.errors.EmptyDataError:
            print("Error!! No data received from switch")

    def append_list(self, file, data):
        with open(file, 'a', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(data)


class TargetInterface(aetest.Testcase):
    @aetest.test
    def target_interface(self):
        open('log/' + DIR_PATH_NAME + '/target_down.csv', 'w', newline='')
        log.info("Retrieving unused interface information...")
        f = open("log/" + DIR_PATH_NAME + "/target_log.txt", "w")
        f.write("==========Target port information==========" + '\n')
        for device in target_testbed.devices:
            device1 = target_testbed.devices[device]
            targetdevice1 = device1.execute("sh ip int br")
            unused_interface = targetdevice1.find("down")
            f = open("log/" + DIR_PATH_NAME + "/target_log.txt", "a")
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
            temp = open("log/" + DIR_PATH_NAME + "/onetarget.txt", "w")
            temp.write("====This is the switch interface log fro the last switch in the provided excel list===\n")
            temp.write("====This file is used to check the interface status of each switch and select the unused "
                       "interface===\n")
            temp.write(targetdevice1)
            temp.close()
            with open("log/" + DIR_PATH_NAME + "/onetarget.txt") as file:
                for line in file:
                    line = line.rstrip()
                    if "down" in line and line.find('Vlan') == -1 and line.find("Gig") == -1 and line.find(
                            "Null") == -1:
                        word = line.split(' ')[0]
                        show_vlan = device1.execute("sh interface " + word + " switchport")
                        temp = open("log/" + DIR_PATH_NAME + "/target_vlan.txt", "w")
                        temp.write(show_vlan)
                        temp.close()
                        with open("log/" + DIR_PATH_NAME + "/target_vlan.txt") as vlan_file:
                            for each in vlan_file:
                                each = each.rstrip()
                                if "Access Mode VLAN:" in each:
                                    vlan_array = each.split(" ")
                                    vlan_value = vlan_array[len(vlan_array) - 2]
                                    break
                                else:
                                    vlan_value = " "
                        row_contents = [device, word, 'down', vlan_value, '0']
                        self.append_list('log/' + DIR_PATH_NAME + '/target_down.csv', row_contents)
        f.close()
        df = pd.read_csv('log/' + DIR_PATH_NAME + '/target_down.csv', header=None)
        df.rename(columns={0: 'Switch', 1: 'Port', 2: 'Status', 3: 'VLAN', 4: 'PortMatchFlag'}, inplace=True)
        df.to_csv('log/' + DIR_PATH_NAME + '/target_down.csv', index=False)  # save to new csv file

    def append_list(self, file, data):
        with open(file, 'a', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(data)


class MatchPort(aetest.Testcase):
    # @aetest.test
    # def match_port(self):
    #     report = open("log/"+DIR_PATH_NAME+"/report.txt", "w")
    #     open("log/"+DIR_PATH_NAME+"/report_log.csv", "w", newline='')
    #     port = {'source_port': [], 'target_port': [], 'source_switch': [], 'target_switch': []}
    #
    #     length = 0
    #     with open("log/"+DIR_PATH_NAME+"/source_up.csv", 'r') as s:
    #         data = csv.DictReader(s, delimiter=',')
    #         for values in data:
    #             port["source_switch"].append(values['Switch'])
    #             port["source_port"].append(values['Port'])
    #             length = length + 1
    #     with open("log/"+DIR_PATH_NAME+"/target_down.csv", 'r') as t:
    #         data = csv.DictReader(t, delimiter=',')
    #         for values in data:
    #             port["target_switch"].append(values['Switch'])
    #             port["target_port"].append(values['Port'])
    #     report.write("=======================Source and target matching===================")
    #     report.write('\n')
    #     a = 0
    #     while a < length:
    #         log.info("%s ------> %s" % (port['source_port'][a], port['target_port'][a]))
    #         report.write('(' + port["source_switch"][a] + ') ' + port["source_port"][a] + '  ----->  ' + '(' +
    #                      port["target_switch"][a] + ') ' + port['target_port'][a] + '\n')
    #         # Write in csv file
    #         row_contents = [port["source_switch"][a], port["source_port"][a], port["target_switch"][a],
    #                         port['target_port'][a]]
    #         self.append_list('log/'+DIR_PATH_NAME+'/report_log.csv', row_contents)
    #         a = a + 1
    #     df = pd.read_csv('log/'+DIR_PATH_NAME+'/report_log.csv', header=None)
    #     df.rename(columns={0: 'SourceSwitch', 1: 'SourcePort', 2: 'TargetSwitch', 3: 'TargetPort'}, inplace=True)
    #     df.to_csv('log/'+DIR_PATH_NAME+'/report_log.csv', index=False)  # save to new csv file

    @aetest.test
    def migrate_port(self):
        # Open a new file to write the source and target switch matching ports
        report = open("log/" + DIR_PATH_NAME + "/report.txt", "w")
        # Open a csv file to write source and target switch port matching values
        open("log/" + DIR_PATH_NAME + "/report_log.csv", "w", newline='')
        # list that contains the information to write in a file
        port = {'source_port': [], 'target_port': [], 'source_switch': [], 'target_switch': [], 'source_vlan': [],
                'target_vlan': []}
        temp = []
        # count the total items in a list
        length = 0
        # open the source switch file containing all the interface that are connected/up
        with open("log/" + DIR_PATH_NAME + "/source_up.csv", 'r') as s:
            source_data = csv.DictReader(s, delimiter=',')
            for source_values in source_data:
                # open target switch file that contains interface that are down
                with open("log/" + DIR_PATH_NAME + "/target_down.csv", 'r') as t:
                    target_data = csv.DictReader(t, delimiter=',')
                    for target_values in target_data:
                        exists = 0
                        # Concat switch and port to check if it has already been matched
                        source_concat_value = source_values['Switch'] + source_values['Port']
                        target_concat_value = target_values['Switch'] + target_values['Port']
                        # check the temporary matched list of switch + port with current value of target switch and port
                        for items in temp:
                            if source_concat_value == items or target_concat_value == items:
                                exists = 1
                        # If the port is unmatched and has same vlan as source, it is matched and append to a new list
                        if exists == 0 and source_values['VLAN'] == target_values['VLAN']:
                            temp.append(source_values['Switch'] + source_values['Port'])
                            temp.append(target_values['Switch'] + target_values['Port'])
                            port["source_switch"].append(source_values['Switch'])
                            port["source_port"].append(source_values['Port'])
                            port["target_switch"].append(target_values['Switch'])
                            port["target_port"].append(target_values['Port'])
                            port["source_vlan"].append(source_values['VLAN'])
                            port["target_vlan"].append(target_values['VLAN'])
                            length = length + 1
                            break
                with open("log/" + DIR_PATH_NAME + "/target_down.csv", 'r') as t:
                    target_data = csv.DictReader(t, delimiter=',')
                    # Loop to match ports if vlan does not match
                    for target_values in target_data:
                        exists = 0
                        # Concat switch and port to check if it has already been matched
                        source_concat_value = source_values['Switch'] + source_values['Port']
                        target_concat_value = target_values['Switch'] + target_values['Port']
                        # check the temporary matched list of switch + port with current value of target switch and port
                        for items in temp:
                            if source_concat_value == items or target_concat_value == items:
                                exists = 1
                        # Here we only check is the current target switch and port is in the temp list of matched ports
                        if exists == 0:
                            temp.append(source_values['Switch'] + source_values['Port'])
                            temp.append(target_values['Switch'] + target_values['Port'])
                            port["source_switch"].append(source_values['Switch'])
                            port["source_port"].append(source_values['Port'])
                            port["target_switch"].append(target_values['Switch'])
                            port["target_port"].append(target_values['Port'])
                            port["source_vlan"].append(source_values['VLAN'])
                            port["target_vlan"].append(target_values['VLAN'])
                            length = length + 1
                            break
        report.write("=======================Source and target matching===================")
        report.write('\n')
        a = 0
        # Iterate over the length of the list and add the values in the list to the files
        while a < length:
            log.info("(%s)%s ------> (%s)%s" % (port['source_switch'][a], port['source_port'][a],
                                                port['target_switch'][a], port['target_port'][a]))
            report.write('(' + port["source_switch"][a] + ') ' + port["source_port"][a] + '(' + port["source_vlan"][a]
                         + ')  ----->  (' + port["target_switch"][a] + ') ' + port['target_port'][a] + '('
                         + port["target_vlan"][a] + ') \n')
            # Write in csv file
            row_contents = [port["source_switch"][a], port["source_port"][a], port["source_vlan"][a],
                            port["target_switch"][a], port['target_port'][a], port["target_vlan"][a]]
            self.append_list('log/' + DIR_PATH_NAME + '/report_log.csv', row_contents)
            a = a + 1
        df = pd.read_csv('log/' + DIR_PATH_NAME + '/report_log.csv', header=None)
        df.rename(columns={0: 'SourceSwitch', 1: 'SourcePort', 2: 'SourceVLAN', 3: 'TargetSwitch', 4: 'TargetPort',
                           5: 'TargetVLAN'}, inplace=True)
        df.to_csv('log/' + DIR_PATH_NAME + '/report_log.csv', index=False)  # save to new csv file

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
