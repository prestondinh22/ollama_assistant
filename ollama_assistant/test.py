import sounddevice as sd
from builtins import print
print(sd.query_devices())
print("Default input device:", sd.default.device[0])
