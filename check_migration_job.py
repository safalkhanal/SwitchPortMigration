"""
<PYATS_JOBFILE>
"""
import pyats.easypy


def main(runtime):
    pyats.easypy.run(testscript='target_config.py', runtime=runtime)
