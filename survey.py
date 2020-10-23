from gm10_radiation_sensor import GM10Sensor
from time import sleep
import progressbar
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("seconds", metavar='seconds', nargs=1 ,default=10, type=int,
                    help="Time in seconds to take a reading for")
parser.add_argument("--device", default="ttyUSB0", type=str, help="Device name under /dev")
parser.add_argument("--maxcps", default=1000, type=int,
    help="Maximum counts per second before initiating a new read from the serial port")
parser.add_argument("--calibration", default=1080, type=int,
    help="mR/hr calibration value for sensor based on isotope. Default is for Cs-137")
parser.add_argument("--maxsample", default=900, type=int,
    help="Maximum amount of time to average reading over in seconds.")
parser.add_argument("--alert", default=5, type=int,
    help="Alert radiation threshold in counts per second. Defaults to 5")
options = parser.parse_args()

sensor = GM10Sensor(
  "/dev/"+options.device,
  options.maxcps,
  options.calibration,
  options.maxsample,
  options.alert
)
sensor.StartSurvey()
print("Beginning radiation survey for {} minutes".format(options.seconds[0]/60))
for i in progressbar.progressbar(range(options.seconds[0]), redirect_stdout=True):
    sleep(1)
    print(sensor.GetCurrentReading())
print("Final reading:\n",sensor.GetCurrentReading())
sensor.StopSurvey()
