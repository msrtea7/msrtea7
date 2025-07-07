---
title: '7DB - PostgreSQL - content'
pubDate: 2025-07-06
author: 'Walbaaco'
tags: ["DB"]
---

# **7DB - PostgreSQL - content**

> Corresponding code [here](https://msrtea7.com/posts/academic/7db_pg_code/)

## **Day 1**

### **Content**

Intro to basic RDBS operations and concepts like CRUD --- create, read, update, delete.

Intro to indexing which helps in accelerating DB operations.

The following table is about the covered terms

| Term | Definition |
|------|------------|
| Column | A domain of values of a certain type, sometimes called an *attribute* |
| Row | An object comprised of a set of column values, sometimes called a *tuple* |
| Table | A set of rows with the same columns, sometimes called a *relation* |
| Primary key | The unique value that pinpoints a specific row |
| Foreign key | A data constraint that ensures that each entry in a column in one table uniquely corresponds to a row in another table (or even the same table) |
| CRUD | Create, Read, Update, Delete |
| SQL | Structured Query Language, the *lingua franca* of a relational database |
| Join | Combining two tables into one by some matching columns |
| Left join | Combining two tables into one by some matching columns or NULL if nothing matches the left table |
| Index | A data structure to optimize selection of a specific set of columns |
| B-tree index | A good standard index; values are stored as a balanced tree data structure; very flexible; B-tree indexes are the default in Postgres |
| Hash index | Another good standard index in which each index value is unique; hash indexes tend to offer better performance for comparison operations than B-tree indexes but are less flexible and don't allow for things like range queries |


## **Day 2**

### **Architecture and basics**

#### **1. Window Functions** - Advanced Analytics Made Simple

```sql
SELECT employee, amount, 
       SUM(amount) OVER (PARTITION BY department) as dept_total,
       ROW_NUMBER() OVER (ORDER BY amount DESC) as ranking
FROM sales;
```

**What makes them special**: Window functions perform calculations across sets of rows that are related to the current row, similar to aggregate functions, but unlike regular aggregate functions, they don't cause rows to become grouped into a single output row. (Source: https://www.postgresql.org/docs/current/tutorial-window.html)

**Real-world impact**: Perfect for creating rankings, running totals, moving averages, and comparative analysis without losing individual row details. They're essentially your Swiss Army knife for data analytics.

**Common use cases**: Sales leaderboards, year-over-year comparisons, cumulative statistics, and percentile calculations.



#### **2. Transactions**

Transactions are the bulwark of relational database consistency. PostgreSQL transactions follow ACID compliance, which stands for:
- Atomic (either all operations succeed or none do)
- Consistent (the data will always be in a good state and never in an inconsistent state)
- Isolated (transactions don’t interfere with one another)
- Durable (a committed transaction is safe, even after a server crash)”

It's critical for any operation where partial completion would be catastrophic - think financial transfers, order processing, or inventory management.



#### **3. Functions vs Stored Procedures** - Code Reusability Done Right

```sql
-- Function: Computes and returns a value
CREATE FUNCTION calc_age(birth_date DATE) RETURNS INTEGER AS $$
BEGIN
  RETURN EXTRACT(YEAR FROM AGE(birth_date));
END;
$$ LANGUAGE plpgsql;

-- Procedure: Executes operations, can control transactions (PG 11+)
CREATE PROCEDURE update_salary(emp_id INT, increase_pct DECIMAL) AS $$
BEGIN
  UPDATE employees SET salary = salary * (1 + increase_pct/100) 
  WHERE id = emp_id;
  COMMIT;
END;
$$ LANGUAGE plpgsql;
```

**The key distinction**: Functions return values and are great for calculations, while stored procedures (introduced in PostgreSQL 11) don't return values but can control transactions. (Source: https://www.postgresql.org/docs/current/xproc.html)

**Strategic advantage**: 
- **Functions**: Excel at data transformation and complex calculations that can be embedded in queries
- **Procedures**: Perfect for multi-step business processes that need transaction control

**Modern best practice**: Use functions for computations and data retrieval, procedures for complex operations requiring transaction management.


#### **4. Triggers** - Automated Business Logic

```sql
CREATE TRIGGER audit_changes
  AFTER UPDATE ON employee_salary
  FOR EACH ROW
  EXECUTE FUNCTION log_salary_change();
```

**The automation engine**: Triggers are specifications that the database should automatically execute a particular function whenever a certain type of operation is performed. (Source: https://www.postgresql.org/docs/current/trigger-definition.html)

**Why they matter**: They ensure business rules are enforced consistently, regardless of which application or user modifies the data. Think of them as your database's immune system.

**Smart applications**: Audit logging, data synchronization, cache invalidation, and automatic calculations that must happen every time data changes.



#### **5. Views** - Smart Data Interfaces

```sql
CREATE VIEW active_high_performers AS
SELECT e.name, e.department, e.salary, p.rating
FROM employees e
JOIN performance p ON e.id = p.employee_id
WHERE e.status = 'active' AND p.rating >= 4.0;
```

**The abstraction layer**: Views wrap complex queries into simple, reusable interfaces while providing security through selective data exposure.

**Business benefits**: Simplify application development, enforce data access policies, and create consistent reporting interfaces across your organization.

**Security bonus**: Grant access to views instead of raw tables to control exactly what data users can see.



#### **6. Rules System** - Query Rewriting Engine (Use with Caution)

```sql
CREATE RULE update_holidays AS 
ON UPDATE TO holidays_view 
DO INSTEAD 
  UPDATE events SET title = NEW.name WHERE title = OLD.name;
```

```
SQL String → Parser → Query Tree → Rewrite → (New) Query Tree → Planner → Execution
                                     ↑
                                   Rules
                                     ↑
                                   Views
```

> The sql compilation pipeline



**How**: The rule system is located between the parser and the planner. It takes the output of the parser, one query tree, and the user-defined rewrite rules, which are also query trees with some extra information, and creates zero or more query trees as result. Source <https://www.postgresql.org/docs/current/querytree.html>

**Important caveat**: While many things can be done using triggers can also be implemented using the PostgreSQL rule system, the trigger approach is conceptually far simpler and easier for novices to get right. (Source: https://www.postgresql.org/docs/current/rules-triggers.html)

**Modern recommendation**: For new projects, prefer INSTEAD OF triggers over rules. Rules can be powerful but are complex and can lead to unexpected behavior.


#### **7. Crosstab** - Data Pivot Tables

```sql
-- Enable the tablefunc extension first
CREATE EXTENSION IF NOT EXISTS tablefunc;

SELECT * FROM crosstab(
  'SELECT employee, quarter, amount FROM sales ORDER BY 1,2',
  'SELECT unnest(ARRAY[''Q1'',''Q2'',''Q3'',''Q4''])'
) AS ct(employee VARCHAR, Q1 INT, Q2 INT, Q3 INT, Q4 INT);
```

**The transformation tool**: The crosstab function is used to produce "pivot" displays, wherein data is listed across the page rather than down. (Source: https://www.postgresql.org/docs/current/tablefunc.html)

**Practical value**: Convert row-based data into Excel-style pivot tables for better analysis and reporting. Essential for creating comparative reports and multi-dimensional analysis.

**Setup requirement**: The crosstab function is part of the PostgreSQL extension called tablefunc, which needs to be enabled once per database. (Source: https://www.postgresql.org/docs/current/tablefunc.html)

## **Day3 & Wrap-Up**

PostgresSQL extensions are just insane.

<https://www.postgresql.org/download/products/6-postgresql-extensions/><br/>
<https://www.postgresql.org/docs/current/contrib.html><br/>
<https://github.com/topics/postgresql-extension>

> Complete this part in the future
