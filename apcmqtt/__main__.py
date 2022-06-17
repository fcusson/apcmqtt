"""apcmqtt - apcupsd to mqtt translation layer

This modules monitors apcupsd continuously and updates an MQTT on the
changes of status

functions:
    main(): code entrypoint
"""

import apc.ups as ups

def main():
    """code entrypoint"""
    ups.get_ups_status()

if __name__ == "__main__":
    main()