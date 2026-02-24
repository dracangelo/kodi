

# ✅ DASHBOARD EXTENSION (Only The Missing Parts)

These are the enhancements layered on top of the inspired design.

---

# 💰 1️⃣ Net Profit Card (Primary KPI)

### 📍 Placement:

Top KPI row (same size as Payments / Pending Bills)

### 📊 Metric:

```
Net Profit (This Month)
= Total Rent Collected
– Total Expenses
– Utility Costs
– Maintenance Costs
```

### 🟢 Display:

* Big bold number (KES)
* Small subtext:

  * ▲ +12% from last month (green)
  * ▼ -8% from last month (red)

### 🎯 Why This Matters:

This becomes the **main performance indicator**.

Landlords think:

> “How much did I actually make?”

---

# 🚨 2️⃣ Overdue & Alert Widget (Action Panel)

### 📍 Placement:

Below KPI cards OR right side column beside chart.

### 🧱 Widget Title:

**Action Required**

### 🔴 Items:

* 🔴 4 Tenants Overdue
* 🔴 2 Leases Expiring (next 30 days)
* 🟡 3 Urgent Tickets
* 🟡 1 Vacant Unit (30+ days)

Each should be clickable → redirects to filtered view.

---

### Backend Logic Needed:

* Query tenants where rent_due_date < today AND balance > 0
* Query leases where end_date <= today + 30 days
* Query tickets where priority = "High" AND status != "Closed"
* Query units where status = "Vacant" AND vacancy_days > 30

---

# 🏢 3️⃣ Occupancy Rate Card

### 📍 Placement:

Top KPI row

### 📊 Formula:

```
Occupied Units / Total Units × 100
```

### 🖥 Display:

* 87%
* Small subtext:

  * 26 / 30 Units Occupied

### 🔥 Add Visual Indicator:

* Green if > 85%
* Yellow if 70–85%
* Red if < 70%

This instantly shows property performance health.

---

# 🎯 4️⃣ Quick Actions Panel

### 📍 Placement:

Right side of dashboard (clean boxed section)
OR under KPI cards as 4 square buttons

### ⚡ Quick Buttons:

* ➕ Add Tenant
* 💰 Record Payment
* 🛠 Create Ticket
* 🧾 Add Expense
* 🏠 Add Unit

These should open modals (not full page navigation).

Speed = good UX.

---

# 🧱 5️⃣ Backend Support Requirements

To power this cleanly in Django:

### Required Aggregations:

#### Monthly Revenue:

```python
Payment.objects.filter(
    date__month=current_month
).aggregate(Sum('amount'))
```

#### Monthly Expenses:

```python
Expense.objects.filter(
    date__month=current_month
).aggregate(Sum('amount'))
```

#### Occupancy:

```python
Unit.objects.filter(status="Occupied").count()
```

#### Overdue:

```python
Tenant.objects.filter(
    rent_due_date__lt=today,
    balance__gt=0
)
```

---

### Performance Advice:

* Add indexes on:

  * rent_due_date
  * lease_end_date
  * unit_status
  * payment_date

* Use database-level aggregation

* Cache dashboard metrics (Redis later)

---

# 🎨 6️⃣ Design Adjustment Recommendation

Instead of pure dark theme:

### Recommended Strategy:

* Default: Light mode
* Toggle: Dark mode
* Store preference in user profile

### Why:

Financial clarity > aesthetics

Charts, tables, and financial reports read better in light themes.

---

# 📊 Updated Dashboard Layout (Improved Version)

### Top Row (KPIs)

* Properties
* Active Tenants
* Occupancy %
* Pending Bills
* Payments Made
* **Net Profit (NEW)**

---

### Second Row

Left:

* Financial Trend Chart

Right:

* **Action Required Panel (NEW)**

---

### Third Row

Left:

* Visitors Today
* Currently Checked In

Right:

* **Quick Actions Panel (NEW)**

---

# 🏆 Result

With these additions your dashboard becomes:

* Informative
* Action-driven
* Financially focused
* Property-performance aware
* Operationally efficient

It stops being “generic SaaS”
and becomes:

> A real property management control center.


