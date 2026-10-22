import time
from smbus2 import SMBus, i2c_msg
import subprocess
import os
import csv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import Flask, request, send_from_directory, send_file, jsonify

import threading

print("=== BASE CONTROLLER LOADED ===", flush=True)

# =========================================================
# CONFIGURATION
# =========================================================
app = Flask(__name__, static_folder="www", static_url_path="")

CSV_DIR = "data"

BEEHIVES = ["D1", "D2", "D3"]

I2C_ADDR = {
    "D1": 101,
    "D2": 102,
    "D3": 103,
}

rtc_beehive = "D1"
have_real_time = threading.Event()
have_real_time.clear()
state_lock = threading.Lock()

LOCAL_TZ = ZoneInfo("Europe/Ljubljana") # TODO set device timezone
current_local_date = None
have_csv_file = {
    "D1": False,
    "D2": False,
    "D3": False,
}
MAX_CSV_FILES = 365 * 10

# =========================================================
# COMMANDS
# =========================================================
CMD_SYSTEM_RESET = 1

CMD_LED_RED_ON = 4
CMD_LED_RED_OFF = 5
CMD_LED_YELLOW_ON = 6
CMD_LED_YELLOW_OFF = 7
CMD_LED_GREEN_ON = 8
CMD_LED_GREEN_OFF = 9

CMD_HBRIDGE_BRAKE_OFF = 10
CMD_HBRIDGE_A_BRAKE = 11
CMD_HBRIDGE_A_FWD = 12
CMD_HBRIDGE_A_REV = 13
CMD_HBRIDGE_B_BRAKE = 14
CMD_HBRIDGE_B_FWD = 15
CMD_HBRIDGE_B_REV = 16

CMD_PUMP_STOP = 20
CMD_PUMP_RUN = 21

CMD_LOADCELL_OFF = 30
CMD_LOADCELL_ON_CH1 = 31
CMD_LOADCELL_ON_CH2 = 32
CMD_LOADCELL_READ = 33

CMD_RTC_READ_DATE = 40
CMD_RTC_READ_TIME = 41
CMD_RTC_SET_YEAR = 44
CMD_RTC_SET_MONTH = 45
CMD_RTC_SET_DAY = 46
CMD_RTC_SET_HOUR = 47
CMD_RTC_SET_MINUTE = 48
CMD_RTC_COMMIT_TIME = 49

CMD_TEMP_READ = 50
CMD_HUMIDITY_READ = 51
CMD_PRESSURE_READ = 52
CMD_ALTITUDE_READ = 53

CMD_POWER_READ = 60
CMD_ENERGY_READ = 61
CMD_BUS_VOLTAGE_READ = 62
CMD_CURRENT_READ = 63
CMD_SHUNT_VOLTAGE = 64
CMD_CHARGE_READ = 68
CMD_DIE_TEMP_READ = 69


# =========================================================
# I2C
# =========================================================
I2C_BUS = 1
i2c_lock = threading.Lock()
i2c_delay = 0.1


def i2c_send(addr, data):
    with i2c_lock:
        try:
            with SMBus(I2C_BUS) as bus:
                time.sleep(i2c_delay)
                msg = i2c_msg.write(addr, data)
                bus.i2c_rdwr(msg)
        except Exception as e:
            print(f"I2C SEND FAIL addr=0x{addr:02X} cmd={data[0]} payload={data[1]}: {e}")


def i2c_read(addr, cmd, delay=0.5):
    value = None
    with i2c_lock:
        try:
            with SMBus(I2C_BUS) as bus:
                time.sleep(i2c_delay)
                msg = i2c_msg.write(addr, [cmd, 0])
                bus.i2c_rdwr(msg)
                time.sleep(delay)
                read = i2c_msg.read(addr, 3)
                bus.i2c_rdwr(read)
                data = list(read)
                value = data[0] | (data[1] << 8) | (data[2] << 16)
                if value & 0x800000:
                    value -= 0x1000000
        except Exception as e:
            print(f"I2C READ FAIL addr=0x{addr:02X} cmd={cmd}: {e}")
    return value


# =========================================================
# LEDs
# =========================================================
def red_on(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LED_RED_ON, 0])


def red_off(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LED_RED_OFF, 0])


def yellow_on(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LED_YELLOW_ON, 0])


def yellow_off(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LED_YELLOW_OFF, 0])


def green_on(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LED_GREEN_ON, 0])


def green_off(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LED_GREEN_OFF, 0])


# =========================================================
# H-Bridge
# =========================================================
def hbridge_a_fwd(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_HBRIDGE_A_FWD, value])


def hbridge_a_rev(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_HBRIDGE_A_REV, value])


def hbridge_a_brake(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_HBRIDGE_A_BRAKE, 0])


def hbridge_b_fwd(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_HBRIDGE_B_FWD, value])


def hbridge_b_rev(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_HBRIDGE_B_REV, value])


def hbridge_b_brake(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_HBRIDGE_B_BRAKE, 0])


# =========================================================
# Pump
# =========================================================
def pump_on(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_PUMP_RUN, 0])
    set_pump_state(beehive, 1)


def pump_off(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_PUMP_STOP, 0])
    set_pump_state(beehive, 0)


# =========================================================
# Load cells
# =========================================================
# TODO
# Set correct load cell coefficient K
loadcell_on_ch1_K = 1.0/71099.0
loadcell_on_ch2_K = 1.0/2644544.0
loadcell_on_delay = 2


def loadcell_on_ch1(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LOADCELL_ON_CH1, 0])


def loadcell_on_ch2(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LOADCELL_ON_CH2, 0])


def loadcell_off(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_LOADCELL_OFF, 0])


def loadcell_read(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_LOADCELL_READ, 5)


def read_loadcell_on_ch1(beehive):
    loadcell_on_ch1(beehive)
    time.sleep(loadcell_on_delay)
    value = loadcell_read(beehive) * loadcell_on_ch1_K  # kg
    loadcell_off(beehive)
    return value


def read_loadcell_on_ch2(beehive):
    loadcell_on_ch2(beehive)
    time.sleep(loadcell_on_delay)
    value = loadcell_read(beehive) * loadcell_on_ch2_K  # kg
    loadcell_off(beehive)
    return value


# =========================================================
# Environment
# =========================================================
def read_temp(beehive):
    return (i2c_read(I2C_ADDR.get(beehive), CMD_TEMP_READ)/10) - 128  # °C


def read_humidity(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_HUMIDITY_READ)  # %


def read_pressure(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_PRESSURE_READ)  # Pa


def read_altitude(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_ALTITUDE_READ)  # m


# =========================================================
# Power
# =========================================================
def read_power(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_POWER_READ)/1000  # W


def read_energy(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_ENERGY_READ)  # J


def read_bus_voltage(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_BUS_VOLTAGE_READ)/1000  # V


def read_current(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_CURRENT_READ)/10000  # A


def read_shunt_voltage(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_SHUNT_VOLTAGE)/100000  # V


def read_charge(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_CHARGE_READ)  # C


def read_IC_temperature(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_DIE_TEMP_READ)  # °C


# =========================================================
# RTC
# =========================================================
def rtc_read_date(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_RTC_READ_DATE, 0.1)


def rtc_read_time(beehive):
    return i2c_read(I2C_ADDR.get(beehive), CMD_RTC_READ_TIME, 0.1)


def rtc_set_year(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_RTC_SET_YEAR, value % 100])


def rtc_set_month(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_RTC_SET_MONTH, value])


def rtc_set_day(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_RTC_SET_DAY, value])


def rtc_set_hour(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_RTC_SET_HOUR, value])


def rtc_set_minute(beehive, value):
    i2c_send(I2C_ADDR.get(beehive), [CMD_RTC_SET_MINUTE, value])


def rtc_commit(beehive):
    i2c_send(I2C_ADDR.get(beehive), [CMD_RTC_COMMIT_TIME, 0])


# =========================================================
# TIME
# =========================================================
def get_os_time():
    now = datetime.now(timezone.utc)
    return now.year, now.month, now.day, now.hour, now.minute, now.second


def get_rtc_time(beehive):
    date_raw = rtc_read_date(beehive)
    time_raw = rtc_read_time(beehive)

    year = 2000 + (date_raw & 0xFF)
    month = (date_raw >> 8) & 0xFF
    day = (date_raw >> 16) & 0xFF
    hour = time_raw & 0xFF
    minute = (time_raw >> 8) & 0xFF
    second = (time_raw >> 16) & 0xFF

    return year, month, day, hour, minute, second


def set_os_time(year, month, day, hour, minute, second):
    dt = datetime(
        year, month, day,
        hour, minute, second,
        tzinfo=timezone.utc
    )

    ts = dt.strftime("%Y-%m-%d %H:%M:%S")

    subprocess.run(
        ["sudo", "/usr/bin/date", "-u", "-s", ts],
        check=True
    )


def set_rtc_time(beehive, year, month, day, hour, minute, second):
    rtc_set_year(beehive, year)
    rtc_set_month(beehive, month)
    rtc_set_day(beehive, day)
    rtc_set_hour(beehive, hour)
    rtc_set_minute(beehive, minute)
    rtc_commit(beehive)


def match_os_rtc_time(beehive):
    try:
        t_rtc = datetime(*get_rtc_time(beehive), tzinfo=timezone.utc)
    except Exception:
        return False
    t_os = datetime.now(timezone.utc)
    dt_seconds = (t_os - t_rtc).total_seconds()
    return abs(dt_seconds) <= 30


def get_ntp_status():
    result = subprocess.run(
        ["timedatectl", "show", "-p", "NTP", "-p", "NTPSynchronized"],
        capture_output=True,
        text=True,
        check=True
    )

    status = {}
    for line in result.stdout.splitlines():
        key, value = line.split("=", 1)
        status[key] = value == "yes"

    return status


def init_time():
    ntp = get_ntp_status()

    if ntp["NTPSynchronized"]:
        have_real_time.set()
    else:
        try:
            time.sleep(1)
            set_os_time(*get_rtc_time(rtc_beehive))
            print(f"::: Time set - OS: {get_os_time()}, RTC: {get_rtc_time(rtc_beehive)}", flush=True)
            have_real_time.set()
        except Exception:
            print("Waiting for time...", flush=True)


# =========================================================
# STATE
# =========================================================
def create_state():
    return {
        "Epoch_time_ms": 0,
        "Loadcell_ch1_kg": 0,
        "Loadcell_ch2_kg": 0,
        "Temperature_C": 0,
        "Humidity_%": 0,
        "Pressure_Pa": 0,
        "Pump": 0,
        "Voltage_V": 0,
        "Current_A": 0
    }


states = {h: create_state() for h in BEEHIVES}


def set_pump_state(beehive, value):
    with state_lock:
        states[beehive]["Pump"] = value


def update_beehive_state(beehive):
    s = create_state()

    s["Epoch_time_ms"] = int(time.time() * 1000)

    s["Loadcell_ch1_kg"] = round(read_loadcell_on_ch1(beehive), 3)
    s["Loadcell_ch2_kg"] = round(read_loadcell_on_ch2(beehive), 3)

    s["Temperature_C"] = round(read_temp(beehive), 1)
    s["Humidity_%"] = round(read_humidity(beehive), 0)
    s["Pressure_Pa"] = round(read_pressure(beehive), 0)

    s["Voltage_V"] = round(read_bus_voltage(beehive), 3)
    s["Current_A"] = round(read_current(beehive), 3)

    with state_lock:
        s["Pump"] = states[beehive]["Pump"]
        states[beehive] = s


# =========================================================
# CSV
# =========================================================
def csv_write_state(beehive):
    global current_local_date, have_csv_file

    new_csv_file = False

    os.makedirs(CSV_DIR, exist_ok=True)

    now_local = datetime.now(LOCAL_TZ)
    now_utc = now_local.astimezone(timezone.utc)
    local_date = now_local.date()

    filename = (
        f"{beehive}_BBC_"
        f"{now_utc.year:04d}_{now_utc.month:02d}_{now_utc.day:02d}.csv"
    )

    path = os.path.join(CSV_DIR, filename)
    file_exists = os.path.exists(path)

    # First call, or local day has changed
    if not have_csv_file.get(beehive) or current_local_date != local_date:
        current_local_date = local_date

        if not file_exists:
            new_csv_file = True
            have_csv_file[beehive] = True

    with open(path, "a", newline="") as f:
        writer = csv.writer(f)

        if new_csv_file:
            writer.writerow([
                "Epoch_time_ms",
                "Loadcell_ch1_kg",
                "Loadcell_ch2_kg",
                "Temperature_C",
                "Humidity_%",
                "Pressure_Pa",
                "Pump",
                "Voltage_V",
                "Current_A"
            ])

        writer.writerow(state_to_csv_row(beehive))
        f.flush()
        os.fsync(f.fileno())

    if new_csv_file:
        manage_csv_files(beehive, MAX_CSV_FILES)


def manage_csv_files(beehive, max_files: int):
    if max_files < 1:
        raise ValueError("max_files must be at least 1")

    os.makedirs(CSV_DIR, exist_ok=True)

    prefix = f"{beehive}_BBC_"

    files = sorted(
        filename
        for filename in os.listdir(CSV_DIR)
        if filename.startswith(prefix)
        and filename.endswith(".csv")
    )

    for filename in files[:-max_files]:
        path = os.path.join(CSV_DIR, filename)

        try:
            os.remove(path)
            print(f"Deleted old CSV file: {filename}")
        except OSError as e:
            print(f"Failed to delete {filename}: {e}")


def state_to_csv_row(beehive):
    with state_lock:
        s = states[beehive].copy()

    return [
        s["Epoch_time_ms"],
        s["Loadcell_ch1_kg"],
        s["Loadcell_ch2_kg"],
        s["Temperature_C"],
        s["Humidity_%"],
        s["Pressure_Pa"],
        s["Pump"],
        s["Voltage_V"],
        s["Current_A"]
    ]


# =========================================================
# JSON
# =========================================================
def json_ok(data=None):
    payload = {
        "status": "ok"
    }

    if isinstance(data, dict):
        payload.update(data)
    else:
        payload["data"] = data

    return jsonify(payload), 200


def json_error(msg, code=400):
    return jsonify({
        "status": "error",
        "message": str(msg)
    }), code


def get_beehive(request):
    beehive = request.args.get("beehive", BEEHIVES[0])
    if beehive not in BEEHIVES:
        raise ValueError("invalid beehive")
    return beehive


# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def index():
    return send_from_directory("www", "index.html")


@app.route("/setTime", methods=["GET"])
def set_time():
    try:
        beehive = get_beehive(request)

        if beehive != rtc_beehive:
            raise ValueError("This beehive doesn't have RTC.")

        y = int(request.args["year"])
        m = int(request.args["month"])
        d = int(request.args["day"])
        h = int(request.args["hour"])
        mi = int(request.args["minute"])
        s = int(request.args["second"])

        ntp = get_ntp_status()

        if not ntp["NTPSynchronized"]:
            set_os_time(y, m, d, h, mi, s)
            if not match_os_rtc_time(beehive):
                set_rtc_time(beehive, y, m, d, h, mi, s)
        else:
            if not match_os_rtc_time(beehive):
                set_rtc_time(beehive, *get_os_time())

        print(f"::: Time set - OS: {get_os_time()}, RTC: {get_rtc_time(rtc_beehive)}", flush=True)

        have_real_time.set()

        return json_ok({"beehive": beehive})

    except Exception as e:
        return json_error(str(e))


@app.route("/getTime", methods=["GET"])
def get_time():
    try:
        beehive = get_beehive(request)
        y, m, d, h, mi, s = get_os_time()

        return json_ok({
            "beehive": beehive,
            "year": y,
            "month": m,
            "day": d,
            "hour": h,
            "minute": mi,
            "second": s
        })

    except Exception as e:
        return json_error(str(e))


@app.route("/getSnapshot", methods=["GET"])
def get_snapshot():
    try:
        beehive = get_beehive(request)
        with state_lock:
            snapshot = states[beehive].copy()
        return json_ok(snapshot)

    except Exception as e:
        return json_error(str(e))


@app.route("/setPump", methods=["GET"])
def set_pump():
    try:
        beehive = get_beehive(request)
        value = int(request.args.get("value", "0"))

        if value > 0:
            pump_on(beehive)
        else:
            pump_off(beehive)

        return json_ok({"beehive": beehive, "pump": value})

    except Exception as e:
        return json_error(str(e))


@app.route("/getFileList", methods=["GET"])
def get_file_list():
    try:
        if not os.path.isdir(CSV_DIR):
            return json_ok([])

        beehive = get_beehive(request)
        prefix = f"{beehive}_BBC_"

        files = [
            f for f in os.listdir(CSV_DIR)
            if f.endswith(".csv")
            and f.startswith(prefix)
            and os.path.isfile(os.path.join(CSV_DIR, f))
        ]

        return json_ok(files)

    except Exception as e:
        return json_error(str(e))


def safe_file_path(name):
    name = os.path.basename(name)

    if not name.endswith(".csv"):
        raise ValueError("invalid file type")

    path = os.path.join(CSV_DIR, name)

    if not os.path.realpath(path).startswith(os.path.realpath(CSV_DIR)):
        raise ValueError("invalid path")

    return path


@app.route("/getFile", methods=["GET"])
def get_file():
    try:
        file_name = request.args.get("file_name")
        if not file_name:
            return json_error("missing file_name")

        path = safe_file_path(file_name)

        if not os.path.exists(path):
            return json_error("file not found")

        return send_file(
            path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=os.path.basename(path)
        )

    except Exception as e:
        return json_error(str(e))


# =========================================================
# LOGGER
# =========================================================
def log_all_beehives():
    if not have_real_time.is_set():
        return

    print("Tick:", datetime.now(timezone.utc))

    for beehive in BEEHIVES:
        try:
            update_beehive_state(beehive)
            csv_write_state(beehive)
            print(f"{beehive} OK")

        except Exception as e:
            print(f"{beehive} FAIL: {e}")


def logger_thread():
    print("Logger thread started")

    while True:
        try:
            log_all_beehives()
            next_run = (int(time.time() / 60) + 1) * 60
            time.sleep(max(0, next_run - time.time()))

        except Exception as e:
            print(f"Logger thread error: {e}")
            time.sleep(5)


def init_logger():
    thread = threading.Thread(target=logger_thread, daemon=True)
    thread.start()


# =========================================================
# MAIN
# =========================================================
def main():
    init_time()
    init_logger()
    app.run(
        host="0.0.0.0", port=8998, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
