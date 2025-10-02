# Goal

Scrape the **California Department of Education (CDE) School Directory** so that I can get **all schools’ data** into a table on my local machine.

---

## Context

- The CDE site lists schools in **pages of 500 records each**:
  - 1–500 → https://www.cde.ca.gov/SchoolDirectory/active-or-pending-schools/2/0/-11/500
  - 501–1000 → https://www.cde.ca.gov/SchoolDirectory/active-or-pending-schools/2/1/-11/500
  - 1001–1500 → https://www.cde.ca.gov/SchoolDirectory/active-or-pending-schools/2/2/-11/500
  - … and so on (7 links in total)

- Each page has a **School** column with hyperlinks that point to the **details page** for that school, e.g.:  
  https://www.cde.ca.gov/SchoolDirectory/details?cdscode=30736506143259

---

## Requirements

- Write a **Python script** to:
  1. Loop through **all 7 paginated list pages**.
  2. Extract the **summary row data** (CDS code, county, district, school, type, sector, charter, status, etc.).
  3. For each school, follow the **details hyperlink** under the “School” column.
  4. Scrape all available details on that page (administrator info, address, phone, email, website, etc.).
  5. Save everything in a structured table (one row per school, all details expanded into columns).

---

## Desired Output

- A single **table** where:
  - Each row = one school
  - Each column = one field from either the **list page** or the **details page**
- Save this locally as **CSV** (and optionally JSON).
