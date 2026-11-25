
import json
import uuid
import boto3
from datetime import date, datetime
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("MedicineInventory")
session_table = dynamodb.Table("MedicineActiveSessions")

SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:753523293131:MedicineInventoryAlerts"
sns = boto3.client("sns")


def json_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"{type(obj).__name__} is not JSON serializable")


def response(code, body):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=json_serializer)
    }


def get_user_sub(event):
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )
    return claims.get("sub")


def get_session_id(event):
    headers = event.get("headers") or {}
    return (
        headers.get("x-session-id")
        or headers.get("X-Session-Id")
    )


def register_session(event, user_sub):
    session_id = get_session_id(event)

    if not session_id or len(session_id) > 128:
        return response(400, {
            "error": "Valid X-Session-Id header is required"
        })

    session_table.put_item(
        Item={
            "userSub": user_sub,
            "sessionId": session_id,
            "updatedAt": datetime.utcnow().isoformat()
        }
    )

    return response(200, {
        "message": "Session registered successfully"
    })


def validate_session(event, user_sub):
    session_id = get_session_id(event)

    if not session_id:
        return False

    result = session_table.get_item(
        Key={"userSub": user_sub},
        ConsistentRead=True
    )

    active_session = result.get("Item")

    return (
        active_session is not None
        and active_session.get("sessionId") == session_id
    )


def get_all():
    result = table.scan()
    items = result.get("Items", [])

    while "LastEvaluatedKey" in result:
        result = table.scan(
            ExclusiveStartKey=result["LastEvaluatedKey"]
        )
        items.extend(result.get("Items", []))

    return items


def get_one(medicine_id):
    return table.get_item(
        Key={"medicineId": medicine_id}
    ).get("Item")


def valid_quantity(value):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def send_alert(medicine, status):
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"Medicine Inventory Alert: {status}",
        Message=(
            f"Medicine: {medicine['name']}\n"
            f"Quantity: {medicine['quantity']}\n"
            f"Expiry date: {medicine['expiryDate']}\n"
            f"Alert: {status}\n\nPlease check your inventory."
        )
    )


def check_alerts(medicine):
    try:
        days_left = (
            date.fromisoformat(str(medicine["expiryDate"]))
            - date.today()
        ).days

        alerts = []

        if int(medicine["quantity"]) <= int(
            medicine.get("reorderLevel", 10)
        ):
            alerts.append("LOW STOCK")

        if days_left < 0:
            alerts.append("EXPIRED")
        elif days_left <= 30:
            alerts.append("EXPIRING SOON")

        if alerts:
            send_alert(medicine, " and ".join(alerts))

    except (KeyError, ValueError, TypeError):
        pass


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get(
        "http", {}
    ).get("method", "")

    path = event.get("rawPath", event.get("path", "/medicines"))
    parts = [p for p in path.rstrip("/").split("/") if p]

    # Cognito JWT authorizer supplies the verified user identity.
    user_sub = get_user_sub(event)

    if not user_sub:
        return response(401, {
            "error": "Unauthorized. Please log in."
        })

    # POST /session — register or replace the active device session.
    if method == "POST" and parts == ["session"]:
        return register_session(event, user_sub)

    # All medicine routes require the current active session.
    if not parts or parts[0] != "medicines":
        return response(404, {"error": "Route not found"})

    if not validate_session(event, user_sub):
        return response(401, {
            "code": "SESSION_REPLACED",
            "error": "Your account was signed in on another device. Please log in again."
        })

    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON"})

    # GET /medicines — list inventory
    if method == "GET" and parts == ["medicines"]:
        return response(200, get_all())

    # POST /medicines — add medicine, rejecting duplicate names
    if method == "POST" and parts == ["medicines"]:
        name = str(
            data.get("medicineName", data.get("name", ""))
        ).strip()

        quantity = data.get("quantity")
        expiry = data.get("expiryDate", "")
        reorder = data.get("reorderLevel", 10)

        if not name:
            return response(400, {
                "error": "Medicine name is required"
            })

        if not valid_quantity(quantity):
            return response(400, {
                "error": "Quantity must be a non-negative integer"
            })

        if not valid_quantity(reorder):
            return response(400, {
                "error": "Reorder level must be a non-negative integer"
            })

        try:
            date.fromisoformat(expiry)
        except (ValueError, TypeError):
            return response(400, {
                "error": "Expiry date must be YYYY-MM-DD"
            })

        for old in get_all():
            old_name = str(
                old.get("name", old.get("medicineName", ""))
            ).strip()

            if old_name.casefold() == name.casefold():
                return response(409, {
                    "error": "Medicine already exists. Use Edit or Stock In instead."
                })

        medicine = {
            "medicineId": str(uuid.uuid4()),
            "name": name,
            "quantity": quantity,
            "expiryDate": expiry,
            "reorderLevel": reorder,
            "createdAt": datetime.utcnow().isoformat()
        }

        table.put_item(Item=medicine)
        check_alerts(medicine)

        return response(201, {
            "message": "Medicine added",
            "medicine": medicine
        })

    # Other medicine routes must include a medicineId.
    if len(parts) < 2:
        return response(404, {"error": "Route not found"})

    medicine_id = parts[1]
    medicine = get_one(medicine_id)

    if not medicine:
        return response(404, {"error": "Medicine not found"})

    # PUT /medicines/{medicineId} — edit medicine fields.
    if method == "PUT" and len(parts) == 2:
        updates = {}

        if "medicineName" in data or "name" in data:
            name = str(
                data.get("medicineName", data.get("name", ""))
            ).strip()

            if not name:
                return response(400, {
                    "error": "Name cannot be empty"
                })

            for old in get_all():
                old_name = str(
                    old.get("name", old.get("medicineName", ""))
                ).strip()

                if (
                    old.get("medicineId") != medicine_id
                    and old_name.casefold() == name.casefold()
                ):
                    return response(409, {
                        "error": "Another record already has this name"
                    })

            updates["name"] = name

        if "quantity" in data:
            if not valid_quantity(data["quantity"]):
                return response(400, {
                    "error": "Quantity must be a non-negative integer"
                })
            updates["quantity"] = data["quantity"]

        if "expiryDate" in data:
            try:
                date.fromisoformat(data["expiryDate"])
            except (ValueError, TypeError):
                return response(400, {
                    "error": "Expiry date must be YYYY-MM-DD"
                })
            updates["expiryDate"] = data["expiryDate"]

        if "reorderLevel" in data:
            if not valid_quantity(data["reorderLevel"]):
                return response(400, {
                    "error": "Reorder level must be a non-negative integer"
                })
            updates["reorderLevel"] = data["reorderLevel"]

        if not updates:
            return response(400, {
                "error": "No fields to update"
            })

        names = {}
        values = {}
        assignments = []

        for i, (key, value) in enumerate(updates.items()):
            names[f"#f{i}"] = key
            values[f":v{i}"] = value
            assignments.append(f"#f{i} = :v{i}")

        result = table.update_item(
            Key={"medicineId": medicine_id},
            UpdateExpression="SET " + ", ".join(assignments),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ReturnValues="ALL_NEW"
        )

        updated = result["Attributes"]
        check_alerts(updated)

        return response(200, {
            "message": "Medicine updated",
            "medicine": updated
        })

    # POST /medicines/{medicineId}/stock
    if (
        method == "POST"
        and len(parts) == 3
        and parts[2] == "stock"
    ):
        change = data.get("change")

        if (
            not isinstance(change, int)
            or isinstance(change, bool)
            or change == 0
        ):
            return response(400, {
                "error": "change must be a non-zero integer"
            })

        current = int(medicine.get("quantity", 0))
        new_quantity = current + change

        if new_quantity < 0:
            return response(400, {
                "error": "Not enough stock for this stock-out"
            })

        result = table.update_item(
            Key={"medicineId": medicine_id},
            UpdateExpression="SET quantity = :q",
            ExpressionAttributeValues={":q": new_quantity},
            ReturnValues="ALL_NEW"
        )

        updated = result["Attributes"]
        check_alerts(updated)

        return response(200, {
            "message": "Stock adjusted",
            "previousQuantity": current,
            "change": change,
            "medicine": updated
        })

    # DELETE /medicines/{medicineId}
    if method == "DELETE" and len(parts) == 2:
        table.delete_item(
            Key={"medicineId": medicine_id}
        )
        return response(200, {
            "message": "Medicine deleted"
        })

    return response(405, {"error": "Method not allowed"})
