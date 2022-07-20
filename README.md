# ApcMQTT

A monitoring tool for apcups that sends data over MQTT messages to a broker at a regular interval.

## Description

ApcMQTT takes the information provided by apcaccess and fowards it to an mqtt broker. The server setup can work with a local or network device for both the mqtt broker and the apcaccess. Which means the service can be used either from the device with the apcupsd setup, the mqtt broker or a standalone server that communicates with both of them.

It is possible to setup multiple ups in the service, by adding a new ups in the config file. There is no limit to the number of ups to monitor.

The service will foward all the available data points to the mqtt broker. A developper topic is also available to validate the keys being activily sent.

## Installation

To install the package, make the install script executable and then run it:

```bash
chmod +x ./install.sh
sudo ./install.sh
```

The script will take care to:

1. install dependencies
2. create the service file for use by systemd
3. copy the module inside the /lib folder of the server
4. create a basic config file in /etc

## Usage

The project can be run either as a standalone script or a systemd service.

### Systemd service

simply start the service calling it in systemctl:

```bash
sudo systemctl start apcmqtt.service
systemctl status apcmqtt.service
```

To make the service start on boot, type the following command:

```bash
sudo systemctl enable apcmqtt.serivce
```

### standalone

To run as standalone, make sure you are the library folder first (work in progress, won't be required in future update) and then run the module from python

```bash
cd /lib/apcmqtt
python -m apcmqtt
```

from there, the script will start to run and can be stopped with a keyboard interupt.

### arguments

The following arguments can be appended to the module call to modify the behavior of the software

|  argument   | description                   | exemple                                    |
| :---------: | ----------------------------- | ------------------------------------------ |
| -v --debug  | sets the script to debug mode | python -m apcmqtt -v                       |
| -c --config | location of the config file   | python -m apcmqtt -c ./config/apcmqtt.yaml |

### config file

The config file hold the information to connect to the different component of the service as well as the options to run the service. A configuration example would look like:

```yaml
mqtt:
  host: 127.0.0.1
  port: 1883
  user: username
  password: password
  root_topic: ups
ups:
  local:
    is_local: true
  server:
    is_local: false
    host: 192.168.0.50
    port: 3551
script:
  delay: 10
```

- **mqtt**: groups all the configuration linked to the mqtt broker
- **ups**: groups all the configuration for the ups. Multiple ups can be provided
- **script**: configuration element linked to the way the module works

#### mqtt

- **mqtt.host**: the ip address or hostname of the matt broker
- **mqtt.port**: the port to communicate to the mqtt broker on
- **mqtt.user**: the username to connect to the mqtt broker
- **mqtt.password**: the password linked to the user mentioned above
- **root_topic**: the root of the topics that will be used to publish the ups informations

#### ups

The ups config can list multiple ups. Each ups must have a key to identify itself and follow two (2) potential structures

##### local ups

```yaml
name_of_the_ups:
    is_local: true
```

##### network ups

```yaml
name_of_the_ups:
    is_local: false
    host: <ip address or hostname>
    port: <default apcups port is 3551>
```

#### script

- **delay**: number of second before republishing new data

### Publishing structure

the topic on the mqtt broker server will this structure

```txt
<root_topic>/<ups_name>/<key>
```

The following key are always transmited:

| key            | description                                                                                                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------- |
| name           | the name of the server as stated in the configuration file                                                            |
| status         | the current status reported by apcupsd. `ONLINE` means all fine                                                       |
| time_left      | the estimated time left before the battery dies                                                                       |
| battery_charge | the percentage of charge left on the battery                                                                          |
| keys           | list of all the topic that apcmqtt is publishing currently. Lists additionnal key that depend on the model of the ups |

## Contributions

<!--TODO-->

## Suport

<!--TODO-->

## Licence

This project is licenced under the MIT licence. You can find the licence [here](./LICENCE)
