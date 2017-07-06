#!/bin/python3
#######################  SETUP  #######################
import sys, os
import Pyro4
import click
from time import sleep
from subprocess import Popen, PIPE, STDOUT
from libpurecoollink.const import FanSpeed, FanMode, NightMode, Oscillation, FanState, StandbyMonitoring, QualityTarget, HeatTarget, HeatMode, FocusMode
import connectiondaemon
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
#######################################################
pyro_uri_session_file = 'pyro_uri' # for storing uri for connecting back to daemon

#######################  COMMANDS  #######################

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def run():
    pass


@run.command(short_help='turn on the fan')
@click.option('-m','--mode', type=click.Choice(['auto','manual']), prompt='Mode operates in',default='auto', help='operational mode tha the fan operates in')
def on(**kwargs):
    myFan = connectDevice()
    commands = getTemplateCommands()
    if kwargs['mode'] == 'auto':
        commands['FanMode'] = 'auto'
    else:
        commands['FanMode'] = 'on'
    myFan.set_configuration(commands)
    print('sent')


@run.command(short_help='turn off the fan')
def off(**kwargs):
    myFan = connectDevice()
    myFan.turnOff()
    print('sent')


@run.command(short_help='control each aspect of the fan settings')
@click.option('-a/-m', '--auto/--manual', is_flag=True,default=None, help='auto or manual mode where should the fan manage the fanspeed itself or not')
@click.option('-s', '--speed', type=click.IntRange(1,10,clamp=True), help='change the speed of fan', metavar='<1-10>')
@click.option('-hm', '--heat-mode', type=click.Choice(['on','off']), help='enable the fan as heat mode')
@click.option('-n', '--night-mode', type=click.Choice(['on','off']), help='enable it as night mode')
@click.option('-f', '--focus', type=click.Choice(['on','off']), help='focus the stream of fan or spread')
@click.option('-q', '--quality-target', type=click.Choice(['normal','high','better']), help='set air quality target')
@click.option('-t', '--temperature-target', type=click.IntRange(1, 37), help='set the temperature for heat mode', metavar='<1-37>')
@click.option('-o', '--oscillation', type=click.Choice(['on','off']), help='turn osillation mode')
@click.option('--sleep-timer', type=click.INT, help='Sleep timer in minutes, 0 to cancel',metavar='<minutes>')
@click.option('--standby-monitoring', type=click.Choice(['on','off']), help='monitor air quality when on standby')
def set(**kwargs):
    myFan = connectDevice()

    if all(v is None for v in kwargs.values()): # none of the options were given. promopt user of the help command
        print('No operations given. Use --help to see list of available actions.')
        sys.exit()

    # print(kwargs)
    commands = getTemplateCommands()

    if kwargs['auto'] != None:
        commands['FanMode'] = 'auto' if kwargs['auto'] else 'on'
    if kwargs['oscillation']:
        commands['Oscillation'] = kwargs['oscillation']
    if kwargs['heat_mode']:
        commands['HeatMode'] = kwargs['heat_mode']
    if kwargs['night_mode']:
        commands['NightMode'] = kwargs['night_mode']
    if kwargs['focus']:
        commands['FocusMode'] = kwargs['focus']
    if kwargs['quality_target']:
        commands['QualityTarget'] = kwargs['quality_target']
    if kwargs['speed']:
        commands['FanSpeed'] = kwargs['speed']
    if kwargs['temperature_target']:
        commands['HeatTarget'] = kwargs['temperature_target']
    if kwargs['sleep_timer']:
        commands['SleepTimer'] = kwargs['sleep_timer']
    if kwargs['standby_monitoring']:
        commands['StandbyMonitoring'] = kwargs['standby_monitoring']

    myFan.set_configuration(commands)
    print('sent')


@run.command(short_help='quickly turn on the fan in heating mode')
@click.option('-a', '--auto', is_flag=True, help='auto mode where the fan manage the fanspeed itself')
@click.option('-n', '--night-mode', is_flag=True, help='enable it as night mode')
@click.option('-f', '--focus', is_flag=True, help='focus the stream of fan or spread')
@click.option('-o', '--oscillation', is_flag=True, help='turn osillation mode')
@click.option('-s', '--speed', type=click.IntRange(1,10,clamp=True), help='change the speed of fan', metavar='<1-10>')
@click.option('-t', '--temperature-target', type=click.IntRange(1, 37), help='set the temperature for heat mode', metavar='<1-37>')
def heat(**kwargs):
    myFan = connectDevice()
    commands = getTemplateCommands()
    # default options
    commands['FanMode'] = 'on'
    commands['HeatMode'] = 'on'
    commands['Oscillation'] = 'off'
    commands['NightMode'] = 'off'
    commands['FocusMode'] = 'off'
    # get options from user
    if kwargs['auto']:
        commands['FanMode'] = 'auto'
    if kwargs['oscillation']:
        commands['Oscillation'] = 'on'
    if kwargs['night_mode']:
        commands['NightMode'] = 'on'
    if kwargs['focus']:
        commands['FocusMode'] = 'on'
    if kwargs['speed']:
        commands['FanSpeed'] = kwargs['speed']
    if kwargs['temperature_target']:
        commands['HeatTarget'] = kwargs['temperature_target']

    myFan.set_configuration(commands)
    print('sent')


@run.command(short_help='quickly turn on the fan in cooling mode')
@click.option('-a', '--auto', is_flag=True, help='auto mode where the fan manage the fanspeed itself')
@click.option('-n', '--night-mode', is_flag=True, help='enable it as night mode')
@click.option('-f', '--focus', is_flag=True, help='focus the stream of fan or spread')
@click.option('-o', '--oscillation', is_flag=True, help='turn osillation mode')
@click.option('-s', '--speed', type=click.IntRange(1,10,clamp=True), help='change the speed of fan', metavar='<1-10>')
def fan(**kwargs):
    myFan = connectDevice()
    commands = getTemplateCommands()
    # default options
    commands['FanMode'] = 'on'
    commands['HeatMode'] = 'off'
    commands['Oscillation'] = 'off'
    commands['NightMode'] = 'off'
    commands['FocusMode'] = 'off'
    # get options from user
    if kwargs['auto']:
        commands['FanMode'] = 'auto'
    if kwargs['oscillation']:
        commands['Oscillation'] = 'on'
    if kwargs['night_mode']:
        commands['NightMode'] = 'on'
    if kwargs['focus']:
        commands['FocusMode'] = 'on'
    if kwargs['speed']:
        commands['FanSpeed'] = kwargs['speed']

    myFan.set_configuration(commands)
    print('sent')


@run.command(short_help='control the network token daemon')
@click.argument('daemon', type=click.Choice(['start','stop']), metavar='<start/stop>')
@click.option('-v', '--verbose', is_flag=True, help='be verbosive of the commands', default=False)
def daemon(**kwargs):
    if kwargs['daemon'] == 'start':
        print("spawning daemon now...")
        if spawnDaemon(verbose=kwargs['verbose']):
            print("successful!")
            sys.exit(0)
        else:
            print("failed..")
            sys.exit(1)
    else:
        print("killing daemon now...")
        myFan = getDaemon(verbose=kwargs['verbose'])
        if myFan:
            myFan.shutdown()
            myFan._pyroRelease()
            print("successful!")
            sys.exit()
        else:
            print("no daemon exists.")
        sys.exit(0)


#######################  HELPERS  #######################

def getTemplateCommands():
    command = {}
    command['FanMode'] = None
    command['Oscillation'] = None
    command['FanSpeed'] = None
    command['NightMode'] = None
    command['QualityTarget'] = None
    command['StandbyMonitoring'] = None
    command['SleepTimer'] = None
    command['HeatMode'] = None
    command['HeatTarget'] = None
    command['FocusMode'] = None
    return command

def connectDevice():
    myFan = getDaemon()
    if not myFan:
        print('Daemon does not exists. Spawning one automatically now...')
        spawnDaemon()
        myFan = getDaemon()
        if not myFan:
            print('still not working... exiting now...')
            sys.exit(1)
    return myFan

def getDaemon(verbose=False):
    # load daemon from file
    if not os.path.exists(pyro_uri_session_file): # test for existance
        return None
    with open(pyro_uri_session_file, 'r') as f:
        uri = f.readline()
    # spawn a new daemon now
    with Pyro4.Proxy(uri) as DysonFan:
        try:
            DysonFan._pyroBind()
            return DysonFan
        except Pyro4.errors.CommunicationError: # no daemon exists
            return None

def spawnDaemon(verbose=False):
    # try to get a daemon to see if it exists first.
    DysonFan = getDaemon()
    if DysonFan:
        print('Daemon already exists. Ignoring...')
        sys.exit(0)
    # start a new session as daemon by subprocess
    daemonScriptPath = os.path.dirname(os.path.abspath(__file__)) + '/connectiondaemon.py'
    if verbose:
        Popen(['python', daemonScriptPath], start_new_session=True)
    else:
        Popen(['python', daemonScriptPath], stdout=PIPE, stdin=PIPE,stderr=STDOUT, start_new_session=True)
    sleep(1) # wait for a while for daemon to run, then try to retrieve daemon again
    return getDaemon()

#########################################################

if __name__ == '__main__':
    run()
