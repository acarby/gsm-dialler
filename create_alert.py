#!/usr/bin/env python3
import wave
import struct
import math

# Create a simple beep tone
sample_rate = 8000  # 8kHz sample rate (common for phone audio)
duration = 3  # 3 seconds
frequency = 440  # A4 note (440 Hz)

# Create WAV file
w = wave.open('/var/www/gsmdialler-data/alert.wav', 'w')
w.setnchannels(1)  # Mono
w.setsampwidth(2)  # 16-bit
w.setframerate(sample_rate)

# Generate sine wave
for i in range(int(sample_rate * duration)):
    value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
    w.writeframes(struct.pack('<h', value))

w.close()
print("Created alert.wav - 3 second beep at 440Hz")

