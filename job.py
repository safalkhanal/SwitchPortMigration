"""
<PYATS_JOBFILE>
"""
import pyats.easypy


def main(runtime):
    pyats.easypy.run(testscript='check_port.py', runtime=runtime)
