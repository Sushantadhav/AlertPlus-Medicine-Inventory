# AlertPlus – Database Structure

AlertPlus uses Amazon DynamoDB to store medicine inventory records and active user-session information.

## 1. MedicineInventory

**Purpose:** Stores medicine inventory records used by the AlertPlus dashboard and inventory operations.

| Property | Details |
|---|---|
| Table name | `MedicineInventory` |
| Partition key | `medicineId` |
| Key type | String (`S`) |

### Medicine item attributes

The following attributes are confirmed from the project details and DynamoDB records:

| Attribute | Description |
|---|---|
| `medicineId` | Unique identifier for a medicine record; partition key |
| `name` | Medicine name |
| `quantity` | Current available stock quantity |
| `expiryDate` | Medicine expiry date |
| `createdAt` | Record creation timestamp |
| `reorderLevel` | Stock threshold used to identify low-stock medicines |

Example item (illustrative):

```json
{
  "medicineId": "example-id",
  "name": "Zinc 20 mg Tablets",
  "quantity": 5,
  "expiryDate": "2026-12-07",
  "reorderLevel": 10,
  "createdAt": "2026-11-06T..."
}
```

The example is illustrative; it is not a complete export of a live database item.

## 2. MedicineActiveSessions

**Purpose:** Stores active user-session information for the application's single-active-session behavior.

| Property | Details |
|---|---|
| Table name | `MedicineActiveSessions` |
| Partition key | `userSub` |
| Key type | String (`S`) |

The screenshot confirms the partition key. Other attributes are not listed here because their exact names and types have not yet been verified.

## Data notes

- `MedicineInventory` is the medicine-data table.
- `MedicineActiveSessions` is the active-session table.
- Do not publish real customer information, session tokens, or other sensitive values in this repository.
