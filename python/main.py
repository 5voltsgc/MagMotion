"""
MagMotion - Python Communication & UI
Real-time sensor monitoring from Teensy 4.1
"""

import sys
import re
import serial
import serial.tools.list_ports

# Regex to extract numbers (positive/negative integers)
num_re = re.compile(r"-?\d+")

def parse_header_tokens(line: str):
    """Parse CSV header row. Return list of column names if found."""
    if not any(c.isalpha() for c in line):
        return None
    toks = [t.strip() for t in line.split(",") if t.strip()]
    return toks if toks else None

class SerialReader:
    """Non-blocking serial reader for Teensy 4.1 data."""
    
    def __init__(self, port: str, baud: int = 115200, timeout: float = 0.05):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        self.labels = None
        self._saw_header = False
    
    def read_latest(self):
        """
        Drain serial buffer, return latest valid data row.
        Returns: (channel_names, values) or (None, None) if no data.
        """
        newest_vals = None
        newest_labels = None
        
        while self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
            except Exception as e:
                print(f"Read error: {e}")
                return None, None
            
            if not line:
                continue
            
            # Detect header row
            if not self._saw_header:
                hdr = parse_header_tokens(line)
                if hdr:
                    newest_labels = hdr
                    self._saw_header = True
                    continue
                else:
                    self._saw_header = True
            
            # Parse numeric row
            nums = num_re.findall(line)
            if nums:
                newest_vals = [int(v) for v in nums]
        
        if newest_vals is not None and newest_labels is None:
            newest_labels = self.labels
        
        if newest_labels:
            self.labels = newest_labels
        
        return newest_labels, newest_vals
    
    def close(self):
        if self.ser.is_open:
            self.ser.close()

def list_serial_ports():
    """List available serial ports."""
    ports = serial.tools.list_ports.comports()
    return [p.device for p in ports]

def main():
    """Example: connect and print data."""
    print("MagMotion - Python UI (Placeholder)")
    print()
    
    # List ports
    ports = list_serial_ports()
    if not ports:
        print("No serial ports found!")
        return
    
    print("Available ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port}")
    
    # For now, just show placeholder
    print()
    print("Next steps:")
    print("  1. Implement Qt GUI (e.g., with pyqtgraph for live plotting)")
    print("  2. Create real-time chart for sensor values")
    print("  3. Add controls to adjust Teensy settings")
    print()

if __name__ == "__main__":
    main()
