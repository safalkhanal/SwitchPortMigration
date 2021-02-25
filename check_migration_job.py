__author__ = "Safal Khanal"
__copyright__ = "Copyright 2021"
__credits__ = ["Safal Khanal"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Safal Khanal"
__email__ = "skhanal@respiro.com.au"
__status__ = "In Development"
"""
<PYATS_JOBFILE>
"""
import pyats.easypy


def main(runtime):
    pyats.easypy.run(testscript='target_config.py', runtime=runtime)
