import boto3
from decimal import Decimal


table = boto3.resource("dynamodb").Table("sr8-telemetry")


def value_type(val):
    if isinstance(val, bool):
        return "boolean"
    if isinstance(val, int):
        return "bigint"
    if isinstance(val, float):
        return "double"
    return "varchar"


def lambda_handler(event, context):
    if "data" not in event:
        raise ValueError("data field not in event")

    data = event["data"]

    print(data)


    with table.batch_writer() as batch:
        for key, val in data.items():
            batch.put_item(Item={
                "measure_name": key,
                "time": event["timestamp"],
                "value": Decimal(str(val)) if isinstance(val, float) else val,
                "value_type": value_type(val),
                "source": event["source"],
                "vehicle": event["vehicle"],
                "sequence_id": event["sequence_id"],
            })

    return {"written": len(data)}




