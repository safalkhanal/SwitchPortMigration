import csv
import logging
from pyats import aetest
from pyats.topology import loader
from csv import writer
import pandas as pd
import time

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
            device1.connect()


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
                device.connect()

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

                # Check for the mac address of target interface
                data = device.execute("show mac interface " + values["TargetPort"])
                mac_file = open("log/"+DIR_PATH_NAME+"/targetmac_after_config.txt", "w")
                mac_file.write(data + '\n')
                mac_file.close()
                mac_address = ''
                with open("log/"+DIR_PATH_NAME+"/targetmac_after_config.txt", 'r') as tac:
                    for lines in tac:
                        if values["TargetPort"] in lines:
                            mac_address = lines.split(' ')[0]

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
