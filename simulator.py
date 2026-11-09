import json
import random

NUM_CELLS = 3  # a real pack has dozens of cells; a few is enough to show the idea


def drift(value, step, low, high):
    """Move value by a small random amount, keeping it within [low, high]."""
    return max(low, min(high, value + random.uniform(-step, step)))


def simulate():
    """Yield one dict of readings per tick, forever. Values carry over between ticks."""
    # Starting values
    speed = 40.0          # km/h
    accel_pos = 30.0      # %
    rpm = 380.0           # rpm
    motor_temp = 35.0     # deg C
    soc = 95.0            # % state of charge
    pack_voltage = 145.0  # V
    pack_current = 15.0   # A (negative = charging)
    solar_power = 600.0   # W
    odometer = 0          # m
    lat, lon = -33.9173, 151.2313  # UNSW Kensington
    drive_mode = "DRIVE"
    cell_voltages = [random.uniform(4.0, 4.15) for _ in range(NUM_CELLS)]
    cell_resistances = [random.uniform(0.0035, 0.0045) for _ in range(NUM_CELLS)]

    while True:
        speed = drift(speed, 3, 0, 110)
        accel_pos = drift(accel_pos, 5, 0, 100)
        rpm = drift(rpm, 25, 0, 1100)
        motor_temp = drift(motor_temp, 0.5, 25, 90)
        pack_voltage = drift(pack_voltage, 0.5, 110, 150)
        pack_current = drift(pack_current, 2, -10, 40)
        solar_power = drift(solar_power, 30, 0, 1000)
        soc = max(0.0, soc - random.uniform(0, 0.02))  # only ever goes down
        odometer += random.randint(5, 30)              # only ever goes up
        lat += random.uniform(-0.0001, 0.0001)
        lon += random.uniform(-0.0001, 0.0001)

        # States that should change rarely, not every tick
        if random.random() < 0.02:
            drive_mode = random.choice(["DRIVE", "NEUTRAL", "REVERSE"])

        data = {
            "/car/speed/gps": round(speed, 2),
            "/car/accel_pos/actual": round(accel_pos, 3),
            "/car/brake/pressed": random.random() < 0.1,
            "/car/drive_mode": drive_mode,
            "/car/odometer": odometer,
            "/car/motors/rpm/left": round(rpm, 3),
            "/car/motors/rpm/right": round(rpm * random.uniform(0.98, 1.02), 3),
            "/car/motors/temperature": round(motor_temp, 2),
            "/car/bms/soc": round(soc, 3),
            "/car/bms/pack/voltage": round(pack_voltage, 2),
            "/car/bms/pack/current": round(pack_current, 3),
            "/car/solar/power": round(solar_power, 1),
            "/car/gps/latitude": round(lat, 6),
            "/car/gps/longitude": round(lon, 6),
        }

        for i in range(NUM_CELLS):
            cell_voltages[i] = drift(cell_voltages[i], 0.01, 3.0, 4.2)
            n = i + 1  # cells are numbered from 1
            data[f"/car/bms/cell/{n}/voltage"] = round(cell_voltages[i], 3)
            data[f"/car/bms/cell/{n}/internal_resistance"] = round(cell_resistances[i], 4)
            # The BMS bleeds charge off a cell that's above the balancing threshold
            data[f"/car/bms/cell/{n}/current_shunting"] = cell_voltages[i] > 4.1

        # Hand this tick's readings to the caller and pause here until it asks for the next
        yield data

