#######################  SETUP  #######################
import Pyro4
from libpurecoollink.dyson import DysonAccount
from libpurecoollink.const import FanSpeed, FanMode, NightMode, Oscillation, FanState, StandbyMonitoring, QualityTarget, HeatTarget, FocusMode, HeatMode
# to disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys
#######################  SETUP  #######################

def writeToFile(string):
    with open('pyro_uri', 'w') as f:
        f.write(str(string))

def main():
    daemon = Pyro4.Daemon()
    fan = DysonFan(daemon)
    uri = daemon.register(fan, objectId='DysonFan')

    # write uri to disk
    writeToFile(uri)
    print(uri)

    # wait till the login procedure finishes
    # (this is when daemon able to response to request)
    # Pyro4.Proxy(uri).ready() # indicate the proxy is ready
    print('logging in...')
    fan.login()
    print('logged in & proxy created. Waiting for calls from client now.')
    # register for others to connect to
    daemon.requestLoop()
    print('exited requestLoop')
    daemon.close()
    print('daemon closed')


@Pyro4.expose
class DysonFan:
    fan = None

    def turnOff(self):
        self.fan.set_configuration(fan_mode=FanMode.OFF)

    def __init__(self, daemon):
        self.daemon = daemon

    @Pyro4.oneway # in case call returns much later than daemon.shutdown
    def shutdown(self):
        print('stopping daemon')
        self.fan.disconnect()
        self.daemon.shutdown()

    def login(self):
        # Log to Dyson account
        # Language is a two characters code (eg: FR)
        dyson_account = DysonAccount("USERNAME","PASSWD","XX")
        logged = dyson_account.login()

        if not logged:
            print('Unable to login to Dyson account')
            exit(1)

        # List devices available on the Dyson account
        devices = dyson_account.devices()

        # Connect using discovery to the first device
        connected = devices[0].connect()

        if not connected:
            print("Unable to find any device!")
            exit(1)

        self.fan = devices[0]
        #####################################################

        # connected == device available, state values are available, sensor values are available
        # devices[0].set_configuration(fan_mode=FanMode.FAN, fan_speed=FanSpeed.FAN_SPEED_3, heat_target=HeatTarget.CELSIUS(20))

        # devices[0].disconnect()

    def set_configuration(self, args):
        # print("======================")
        # print(args)
        commands = commandParser(args)
        # print(commands)
        self.fan.set_fan_configuration(*commands)








def commandParser(kwargs):
    args = []

    # if anything ele that involes controlling fan speed or heat was set, ignore auto mode
    if kwargs['FanMode'] == 'off':
        args.append(FanMode.OFF)
    if kwargs['FanSpeed'] or kwargs['FanMode'] == 'on':
        args.append(FanMode.FAN)
    elif kwargs['FanMode'] == 'auto':
        args.append(FanMode.AUTO)
    else:
        args.append(None)

    if kwargs['Oscillation'] == 'on':
        args.append(Oscillation.OSCILLATION_ON)
    elif kwargs['Oscillation'] == 'off':
        args.append(Oscillation.OSCILLATION_OFF)
    else:
        args.append(None)

    if kwargs['FanMode'] == 'auto':
        args.append(FanSpeed.FAN_SPEED_AUTO)
    else:
        if kwargs['FanSpeed']:
            args.append(fanSpeedtoConst(kwargs['FanSpeed']))
        else:
            args.append(None)

    if kwargs['NightMode'] == 'on':
        args.append(NightMode.NIGHT_MODE_ON)
    elif kwargs['NightMode'] == 'off':
        args.append(NightMode.NIGHT_MODE_OFF)
    else:
        args.append(None)

    if kwargs['QualityTarget'] == 'normal':
        args.append(QualityTarget.QUALITY_NORMAL)
    elif kwargs['QualityTarget'] == 'high':
        args.append(QualityTarget.QUALITY_HIGH)
    elif kwargs['QualityTarget'] == 'better':
        args.append(QualityTarget.QUALITY_BETTER)
    else:
        args.append(None)

    if kwargs['StandbyMonitoring'] == 'on':
        args.append(StandbyMonitoring.STANDBY_MONITORING_ON)
    elif kwargs['StandbyMonitoring'] == 'off':
        args.append(StandbyMonitoring.STANDBY_MONITORING_OFF)
    else:
        args.append(None)

    if kwargs['SleepTimer']:
        args.append(int(kwargs['SleepTimer']))
    else:
        args.append(None)

    if kwargs['HeatMode'] == 'on':
        args.append(HeatMode.HEAT_ON)
    elif kwargs['HeatMode'] == 'off':
        args.append(HeatMode.HEAT_OFF)
    else:
        args.append(None)

    if kwargs['HeatTarget']:
        args.append(HeatTarget.CELSIUS(kwargs['HeatTarget']))
    else:
        args.append(None)

    if kwargs['FocusMode'] == 'on':
        args.append(FocusMode.FOCUS_ON)
    elif kwargs['FocusMode'] == 'off':
        args.append(FocusMode.FOCUS_OFF)
    else:
        args.append(None)

    return args


def fanSpeedtoConst(speed):
    if speed == 'AUTO':
        return FanSpeed.FAN_SPEED_AUTO
    elif speed == 1:
        return FanSpeed.FAN_SPEED_1
    elif speed == 2:
        return FanSpeed.FAN_SPEED_2
    elif speed == 3:
        return FanSpeed.FAN_SPEED_3
    elif speed == 4:
        return FanSpeed.FAN_SPEED_4
    elif speed == 5:
        return FanSpeed.FAN_SPEED_5
    elif speed == 6:
        return FanSpeed.FAN_SPEED_6
    elif speed == 7:
        return FanSpeed.FAN_SPEED_7
    elif speed == 8:
        return FanSpeed.FAN_SPEED_8
    elif speed == 9:
        return FanSpeed.FAN_SPEED_9
    elif speed == 10:
        return FanSpeed.FAN_SPEED_10
    else:
        raise "Error while parsing fan speed."


if __name__ == '__main__':
    main()
