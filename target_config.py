__author__ = "Safal Khanal"
__copyright__ = "Copyright 2021"
__credits__ = ["Safal Khanal"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Safal Khanal"
__email__ = "skhanal@respiro.com.au"
__status__ = "In Development"

import csv
import logging
import os
from csv import writer
import time
from pyats import aetest
from pyats.topology import loader
import pandas as pd


log = logging.getLogger(__name__)
testbed = loader.load('targettestbed.yml')
DIR_PATH_NAME = time.strftime("%Y-%m-%d")


###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################
class common_setup(aetest.CommonSetup):
    @aetest.subsection
    def connectdevices(self):
        log.info("Connecting to  devices.....")
        for device in testbed.devices:
            device1 = testbed.devices[device]
            device1.connect(init_config_commands=[])


###################################################################
#                    TESTCASES SECTION                            #
###################################################################
class CheckTarget(aetest.Testcase):
    @aetest.test
    def check_target(self):
        open("log/"+DIR_PATH_NAME+"/switch_migration_status.csv", "w")
        with open("log/"+DIR_PATH_NAME+"/report_log.csv", 'r') as r:
            data = csv.DictReader(r, delimiter=',')
            for values in data:
                device = testbed.devices[values["TargetSwitch"]]
                device.connect(init_config_commands=[])

                # Check if the recommended target interface is up
                data = device.execute("show interface " + values["TargetPort"])
                f = open("log/"+DIR_PATH_NAME+"/targetport_after_config.txt", "w")
                f.write(data)
                f.close()
                with open("log/"+DIR_PATH_NAME+"/targetport_after_config.txt", 'r') as tac:
                    for lines in tac:
                        if values["TargetPort"] in lines:
                            # Gets the  line of command which states if the port is up or down
                            port_line = lines.split(',')[0]
                            # split the line using space to find the port status
                            port_status = port_line.split(' ')[-1]

                # get the switchport info to get the short name for port and check that port short name in mac address
                # table to get mac address
                show_vlan = device.execute("sh interface " + values["TargetPort"] + " switchport")
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

                        if "Name:" in each:
                            port_short_name_array = each.split(" ")
                            port_short_name = port_short_name_array[1]
                        else:
                            port_short_name = values["TargetPort"]

                # Check for the mac address of target interface
                data = device.execute("show mac address interface " + values["TargetPort"])
                mac_file = open("log/"+DIR_PATH_NAME+"/targetmac_after_config.txt", "w")
                mac_file.write(data + '\n')
                mac_file.close()
                mac_address = ''
                with open("log/"+DIR_PATH_NAME+"/targetmac_after_config.txt", 'r') as tac:
                    for lines in tac:
                        if values["TargetPort"] in lines or port_short_name in lines:
                            mac_address = lines.split(' ')[1]

                with open("log/"+DIR_PATH_NAME+"/source_up.csv", 'r') as su:
                    data = csv.DictReader(su, delimiter=',')
                    for list in data:
                        if list['Switch'] == values['SourceSwitch'] and list['Port'] == values['SourcePort']:
                            source_mac = list['ConnectedMAC']

                if port_status != 'down' and mac_address == source_mac:
                    status = 'Successful'
                else:
                    status = 'Failed'

                row_contents = [values["TargetSwitch"], values["TargetPort"], port_status, mac_address, source_mac,
                                status]
                self.append_list('log/'+DIR_PATH_NAME+'/switch_migration_status.csv', row_contents)

            # Add header to the csf file
            df = pd.read_csv('log/'+DIR_PATH_NAME+'/switch_migration_status.csv', header=None)
            df.rename(columns={0: 'Target Switch', 1: 'Target Port', 2: 'Target Port status',
                               3: 'Target connected MAC address', 4: 'Source connected MAC address',
                               5: 'Migration Status'}, inplace=True)
            df.to_csv('log/'+DIR_PATH_NAME+'/switch_migration_status.csv', index=False)  # save to new csv file

    def append_list(self, file, data):
        with open(file, 'a', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(data)


#####################################################################
#                       COMMON CLEANUP SECTION                      #
#####################################################################
class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def clean_everything(self):
        log.info("Aetest Common Cleanup ")
        for device in testbed.devices:
            device1 = testbed.devices[device]
            device1.disconnect()


if __name__ == '__main__':  # pragma: no cover
    logging.getLogger(__name__).setLevel(logging.ERROR)
    logging.getLogger('pyats.aetest').setLevel(logging.ERROR)
    aetest.main()
