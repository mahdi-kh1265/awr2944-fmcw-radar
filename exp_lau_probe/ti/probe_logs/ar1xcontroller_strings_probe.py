from pathlib import Path
import re

dll = Path(r"C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\Clients\AR1xController\AR1xController.dll")
out = Path(r"C:\Users\khams008\Documents\awr2944-fmcw-radar\exp_lau_probe\ti\probe_logs\ar1xcontroller_strings_probe.txt")

data = dll.read_bytes()

def ascii_strings(data, minlen=5):
    pat = rb"[ -~]{%d,}" % minlen
    for m in re.finditer(pat, data):
        yield m.group().decode("ascii", errors="ignore")

def utf16le_strings(data, minlen=5):
    strings = []
    cur = bytearray()
    i = 0
    while i + 1 < len(data):
        b1, b2 = data[i], data[i + 1]
        if b2 == 0 and 32 <= b1 <= 126:
            cur.append(b1)
        else:
            if len(cur) >= minlen:
                strings.append(cur.decode("ascii", errors="ignore"))
            cur = bytearray()
        i += 2

    if len(cur) >= minlen:
        strings.append(cur.decode("ascii", errors="ignore"))

    return strings

keywords = [
    "Connect", "ConnectTarget", "Calling_ConnectTarget", "IsConnected",
    "SOP", "FullReset", "Reset", "Board Control", "Gpio Control",
    "RS232", "COM", "Baud", "deviceVariant", "frequencyBand",
    "SelectChip", "AR1642", "AWR2944", "XWR2944",
    "Button", "Click", "Set", "Port", "Disconnect",
    "ATE", "Target", "Firmware", "MSS", "BSS",
    "Gpio", "Board", "Serial", "Uart"
]

strings = set(ascii_strings(data)) | set(utf16le_strings(data))

hits = []
for s in sorted(strings):
    if any(k.lower() in s.lower() for k in keywords):
        hits.append(s)

out.write_text("\n".join(hits), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
