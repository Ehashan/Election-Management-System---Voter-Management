# Pre-Approved Test NIC Numbers

These 50 valid Sri Lankan NIC numbers are stored in the MongoDB `temp_nic` collection for voter registration testing.

---

##  Old Format (9 Digits + 'V') — 25 NICs

| # | NIC Number | Format | Status in `temp_nic` |
|---|---|---|---|
| 01 | `781423589V` | 9-digit + V | Available |
| 02 | `792154687V` | 9-digit + V | Available |
| 03 | `803215498V` | 9-digit + V | Available |
| 04 | `811564789V` | 9-digit + V | Available |
| 05 | `822453698V` | 9-digit + V | Available |
| 06 | `833125478V` | 9-digit + V | Available |
| 07 | `841789654V` | 9-digit + V | Available |
| 08 | `852468135V` | 9-digit + V | Available |
| 09 | `863579246V` | 9-digit + V | Available |
| 10 | `871357924V` | 9-digit + V | Available |
| 11 | `882468013V` | 9-digit + V | Available |
| 12 | `893579124V` | 9-digit + V | Available |
| 13 | `901452369V` | 9-digit + V | Available |
| 14 | `912563478V` | 9-digit + V | Available |
| 15 | `923674589V` | 9-digit + V | Available |
| 16 | `931478523V` | 9-digit + V | Available |
| 17 | `942589631V` | 9-digit + V | Available |
| 18 | `953691472V` | 9-digit + V | Available |
| 19 | `961472583V` | 9-digit + V | Available |
| 20 | `972583691V` | 9-digit + V | Available |
| 21 | `983694715V` | 9-digit + V | Available |
| 22 | `991592634V` | 9-digit + V | Available |
| 23 | `876543210V` | 9-digit + V | Available |
| 24 | `915432167V` | 9-digit + V | Available |
| 25 | `948765432V` | 9-digit + V | Available |

---

##  New Format (12 Digits) — 25 NICs

| # | NIC Number | Format | Status in `temp_nic` |
|---|---|---|---|
| 26 | `198512304561` | 12-digit | Available |
| 27 | `198623405672` | 12-digit | Available |
| 28 | `198734506783` | 12-digit | Available |
| 29 | `198845607894` | 12-digit | Available |
| 30 | `198956708905` | 12-digit | Available |
| 31 | `199012304567` | 12-digit | Available |
| 32 | `199123405678` | 12-digit | Available |
| 33 | `199234506789` | 12-digit | Available |
| 34 | `199345607890` | 12-digit | Available |
| 35 | `199456708901` | 12-digit | Available |
| 36 | `199512307892` | 12-digit | Available |
| 37 | `199623408903` | 12-digit | Available |
| 38 | `199734509014` | 12-digit | Available |
| 39 | `199845601235` | 12-digit | Available |
| 40 | `199956702346` | 12-digit | Available |
| 41 | `200012303457` | 12-digit | Available |
| 42 | `200123404568` | 12-digit | Available |
| 43 | `200234505679` | 12-digit | Available |
| 44 | `200345606780` | 12-digit | Available |
| 45 | `200456707891` | 12-digit | Available |
| 46 | `200512308902` | 12-digit | Available |
| 47 | `199467801234` | 12-digit | Available |
| 48 | `199678902345` | 12-digit | Available |
| 49 | `199889003456` | 12-digit | Available |
| 50 | `200190104567` | 12-digit | Available |

---

### 💡 Validation Rules
- **Valid & Unused**: Allowed to register. Once registered, marked as `is_used: true`.
- **Duplicate Registration**: Attempting to reuse an already registered NIC displays: `"NIC already used. This NIC has already been registered."`
- **Any Other NIC**: Entering an NIC not in this list displays: `"Invalid NIC. This NIC does not exist in the official records."`
