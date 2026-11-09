import json
import os
import time
import sys

from awscrt import mqtt
from awsiot import mqtt_connection_builder
from dotenv import load_dotenv
from datetime import datetime, timezone
from simulator import simulate

load_dotenv()

IOT_ENDPOINT = os.getenv("IOT_ENDPOINT")
CLIENT_ID = "sr8-simulator"
TOPIC = "sr8/telemetry/test"



def main():
    if len(sys.argv) != 2:
        print("usage: publish.py <num_packets>")
        sys.exit(1)

    num_packets = int(sys.argv[1])


    conn = mqtt_connection_builder.mtls_from_path(
        endpoint=IOT_ENDPOINT,
        cert_filepath="certs/device.pem.crt",
        pri_key_filepath="certs/private.pem.key",
        ca_filepath="certs/AmazonRootCA1.pem",
        client_id=CLIENT_ID
    )

    conn.connect().result()
    print("connected")

    ticks = simulate()
    seq = 1

    for n in range(1, num_packets + 1):
        data = next(ticks)
        packet = {
            # "packet_no": commented out since same as sequence_id, was only there for demo purposes
            "source": "SR8-Telemetry",
            "vehicle": "SR8 Tribrid",
            "sequence_id": seq,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "data": data
        }


        print(f"Publishing packet {n}: {json.dumps(packet, indent=2)}")

        publish_future, packet_id = conn.publish(
            topic=TOPIC,
            payload=json.dumps(packet),
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

        publish_future.result()

        print(f"Sent packet {n} to {TOPIC}")

        seq += 1

        time.sleep(1)

    conn.disconnect().result()
    print("Disconnected")



if __name__ == "__main__":
    main()