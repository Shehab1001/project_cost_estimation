# Project Cost Estimation — Odoo 17 Module

A custom Odoo 17 module that manages **Project Cost Estimations** with a full approval workflow, role-based access control, and rich UI integration into the Project app.

---

## Features

- **Cost Estimates** linked to projects, with itemised breakdown lines
- **Computed total** automatically summed from breakdown subtotals (qty × unit price)
- **Approval workflow**: Draft → Submitted → Approved / Rejected
- **Smart button** on the project form showing how many estimates exist
- **Kanban view** for cost estimates (grouped by state by default)
- **Project kanban card** shows the latest estimate total and status
- **Chatter / activity tracking** on every estimate record

---

## Module Structure

```
project_cost_estimate/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── cost_estimate.py       # project.cost.estimate model
│   ├── cost_breakdown.py      # project.cost.breakdown model
│   └── project_project.py     # project.project extension (smart button fields)
├── views/
│   ├── cost_estimate_views.xml     # Form, List, Kanban, Search, Actions
│   ├── cost_breakdown_views.xml    # Standalone breakdown views
│   ├── project_views_inherit.xml   # Smart button + kanban card injection
│   └── menus.xml                   # Menu entries under Project app
└── security/
    ├── groups.xml              # Cost Approver group definition
    ├── ir.model.access.csv     # CRUD permissions per group
    └── record_rules.xml        # Row-level access rules
```

---

## Models

### `project.cost.estimate`
| Field | Type | Description |
|---|---|---|
| `name` | Char | Estimate title |
| `project_id` | Many2one | Linked project |
| `state` | Selection | draft / submitted / approved / rejected |
| `breakdown_ids` | One2many | Cost breakdown lines |
| `estimated_total_cost` | Float (computed) | Sum of all line subtotals |
| `currency_id` | Many2one | Company currency |
| `created_by` | Many2one | Creator (auto-set) |
| `submission_date` | Datetime | When submitted |
| `approval_date` | Datetime | When approved/rejected |
| `approved_by` | Many2one | Who approved/rejected |

### `project.cost.breakdown`
| Field | Type | Description |
|---|---|---|
| `estimate_id` | Many2one | Parent estimate |
| `name` | Char | Line description |
| `category` | Selection | Labor / Material / Service / Overhead / Other |
| `quantity` | Float | Quantity |
| `unit` | Char | Unit label (e.g. hrs, pcs) |
| `unit_price` | Float | Price per unit |
| `subtotal` | Float (computed) | quantity × unit_price |

---

## Workflow & Permissions

```
[draft] ──(Admin submits)──► [submitted] ──(Approver approves)──► [approved]
                                    └──(Approver rejects)──► [rejected]
                                                                   │
                                          (Admin resets) ◄─────────┘
```

| Group | Can Create | Can Submit | Can Approve/Reject | Visible Records |
|---|---|---|---|---|
| Project User | ✅ (draft only) | ❌ | ❌ | Own records only |
| Project Admin | ✅ | ✅ | ❌ | All records |
| Cost Approver | ❌ | ❌ | ✅ | Submitted/Approved/Rejected |

**Once submitted**: all fields become read-only (enforced in the form view via `readonly="state != 'draft'"`).

---

## Installation

1. Copy the `project_cost_estimate` folder into your Odoo 17 `addons` directory.
2. Restart the Odoo server.
3. Go to **Settings → Apps**, search for "Project Cost Estimation", and click **Install**.
4. To assign the approver group: **Settings → Users → [user] → Cost Estimate Approver**.

---

## Dependencies

- `project` (Odoo built-in Project app)
- `mail` (messaging/chatter — included transitively via `project`)

---

## License

LGPL-3
