import csv
import logging
from pyats import aetest
from pyats.topology import loader
from csv import writer
import pandas as pd

log = logging.getLogger(__name__)
testbed = loader.load('targettestbed.yml')


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
        open("log/target_after_configlog.csv", "w")
        with open("log/report_log.csv", 'r') as r:
            data = csv.DictReader(r, delimiter=',')
            for values in data:
                device = testbed.devices[values["Target Switch"]]
                device.connect()

                # Check if the recommended target interface is up
                data = device.execute("show interface " + values["Target Port"])
                f = open("log/targetport_after_config.txt", "w")
                f.write(data)
                f.close()
                with open("log/targetport_after_config.txt", 'r') as tac:
                    for lines in tac:
                        if values["Target Port"] in lines:
                            # Gets the  line of command which states if the port is up or down
                            port_line = lines.split(',')[0]
                            # split the line using space to find the port status
                            port_status = port_line.split(' ')[-1]

                # Check for the mac address of target interface
                data = device.execute("show mac interface " + values["Target Port"])
                mac_file = open("log/targetmac_after_config.txt", "w")
                mac_file.write(data + '\n')
                mac_file.close()
                mac_address = ''
                with open("log/targetmac_after_config.txt", 'r') as tac:
                    for lines in tac:
                        if values["Target Port"] in lines:
                            mac_address = lines.split(' ')[0]

                with open("log/source_up.csv", 'r') as su:
                    data = csv.DictReader(su, delimiter=',')
                    for list in data:
                        if list['Switch'] == values['Source Switch'] and list['Port'] == values['Source Port']:
                            source_mac = list['Connected MAC']

                if port_status != 'down' and mac_address == source_mac:
                    status = 'Successful'
                else:
                    status = 'Failed'

                row_contents = [values["Target Switch"], values["Target Port"], port_status, mac_address, source_mac,
                                status]
                self.append_list('log/target_after_configlog.csv', row_contents)

            # Add header to the csf file
            df = pd.read_csv('log/target_after_configlog.csv', header=None)
            df.rename(columns={0: 'Target Switch', 1: 'Target Port', 2: 'Target Port status',
                               3: 'Target connected MAC address', 4: 'Source connected MAC address',
                               5: 'Migration Status'}, inplace=True)
            df.to_csv('log/target_after_configlog.csv', index=False)  # save to new csv file

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
