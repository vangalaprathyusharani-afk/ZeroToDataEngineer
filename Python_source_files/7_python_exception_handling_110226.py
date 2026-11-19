# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Exception Handling for Data Engineering
# MAGIC
# MAGIC Learn to distinguish expected bad data from pipeline failures, add useful
# MAGIC context to errors, retry transient operations safely, and preserve rejected
# MAGIC records for investigation. The examples use functions, avoid custom classes,
# MAGIC and use Python's standard library, so they can run outside Databricks. The
# MAGIC final section shows an optional Databricks filesystem example.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. The `try` / `except` / `else` / `finally` structure
# MAGIC
# MAGIC - `try`: code that may fail.
# MAGIC - `except`: handle a specific error that you know how to recover from.
# MAGIC - `else`: runs only when the `try` block succeeds.
# MAGIC - `finally`: runs whether the operation succeeds or fails; use it for
# MAGIC   cleanup.
# MAGIC
# MAGIC Avoid a bare `except:`: it can hide programming errors and even interrupt
# MAGIC signals such as `KeyboardInterrupt`.

# COMMAND ----------

try:
    # Put only the operation that may raise an I/O error inside this block.
    print("Reading source data...")
    source_row_count = 3
except OSError as error:
    # Handle this known operational failure and include its diagnostic message.
    print(f"Could not read the source: {error}")
else:
    # `else` runs only if the `try` block completed without raising an error.
    print(f"Read {source_row_count} source rows.")
finally:
    # `finally` runs in either case, so it is useful for guaranteed cleanup/logging.
    print("Source-read attempt finished.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Catch expected errors and preserve their meaning
# MAGIC
# MAGIC Catch the most specific exception first. Here, division by zero and a
# MAGIC wrong input type are expected input problems. A different programming
# MAGIC error is not silently treated as the same problem.

# COMMAND ----------

def divide_values(numerator, denominator):
    try:
        # This expression can raise ZeroDivisionError or TypeError.
        result = numerator / denominator
    except ZeroDivisionError as error:
        # Return a clear failure value for the specific invalid denominator.
        print(f"Cannot divide by zero: {error}")
        return None
    except TypeError as error:
        # A string such as "2" is not automatically accepted as a number here.
        print(f"Both values must be numeric: {error}")
        return None
    else:
        # Keep the success path separate from error handling.
        print(f"Division succeeded: {result}")
        return result
    finally:
        # This still runs before a return from either the try or except branch.
        print("Division attempt finished.")


output=divide_values(denominator=10, numerator=2)
print(output)
output=divide_values(10, 0)
print(output)
divide_values(10, "2")
# type(output)

# COMMAND ----------

result=10/"2"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validate records before loading them
# MAGIC
# MAGIC A production ETL job should not let one malformed row erase every good
# MAGIC row. This example parses a small CSV batch, validates each record, loads
# MAGIC valid rows into a list, and sends invalid rows to a quarantine list with
# MAGIC their original values and a reason.
# MAGIC
# MAGIC In a Spark pipeline, the same idea can be implemented with a validation
# MAGIC column and separate accepted/rejected DataFrames. This example uses
# MAGIC Python's built-in `ValueError` for invalid input.

# COMMAND ----------

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from io import StringIO


def parse_order(row):
    # Require values before parsing so errors identify missing input clearly.
    required_fields = ("order_id", "order_date", "amount")
    missing_fields = [field for field in required_fields if not row.get(field)]
    if missing_fields:
        raise ValueError(
            f"Missing required field(s): {', '.join(missing_fields)}"
        )

    try:
        # Parse into useful types instead of leaving dates and amounts as strings.
        order_date = date.fromisoformat(row["order_date"])
        amount = Decimal(row["amount"])
    except (ValueError, InvalidOperation) as error:
        # Preserve the low-level parsing error as the cause for debugging.
        raise ValueError(f"Invalid date or amount: {error}") from error

    # Decimal supports exact monetary arithmetic; reject NaN, infinity, and negatives.
    if not amount.is_finite() or amount < 0:
        raise ValueError("amount must be a finite, non-negative number")

    # Return a new normalized row; the original CSV dictionary is not modified.
    return {
        "order_id": row["order_id"],
        "order_date": order_date,
        "amount": amount,
    }


csv_text = """order_id,order_date,amount
1001,2026-10-01,49.95
1002,not-a-date,12.00
1003,2026-10-03,-4.50
1004,2026-10-04,8.25
1005,2026-10-05,
1006,2026-10-06,Infinity
"""

# Keep successful rows and rejected rows separate so bad data does not disappear.
accepted_orders = []
quarantined_orders = []

# DictReader converts each CSV line into a dictionary keyed by the header fields.
for raw_order in csv.DictReader(StringIO(csv_text)):
    try:
        # Append only after the complete validation and parsing succeeds.
        accepted_orders.append(parse_order(raw_order))
    except ValueError as error:
        # Retain both the original row and the reason for later remediation.
        quarantined_orders.append(
            {"record": raw_order, "reason": str(error)}
        )

print(f"Accepted {len(accepted_orders)} orders:")
for order in accepted_orders:
    print(order)

print(f"\nQuarantined {len(quarantined_orders)} orders:")
for rejected in quarantined_orders:
    print(rejected)

# COMMAND ----------

from decimal import Decimal
# print(Decimal('Naveen'))
print(Decimal('Infinity')) # Infinity value representation

integer=1_00_00_000

# COMMAND ----------

csv_text = """order_id,order_date,amount
1001,2026-10-01,49.95
1002,not-a-date,12.00
1003,2026-10-03,-4.50
1004,2026-10-04,8.25
1005,2026-10-05,
"""
data=StringIO(csv_text)
dict_date=csv.DictReader(data)
print(data)
for i in dict_date:
  print(i)

# COMMAND ----------

positive_inf = float('inf')
negative_inf = float('-inf')

print(positive_inf)
print(negative_inf)

x = float('inf')

print(x > 1000000000)
print(x > 999999999999999999999)

print(Decimal('Infinity'))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Handle malformed JSON and add pipeline context
# MAGIC
# MAGIC A parser exception explains what went wrong with one value. A pipeline-
# MAGIC level exception can add which source or task failed. Use `raise ... from`
# MAGIC to keep the original exception available in the traceback. This uses the
# MAGIC built-in `RuntimeError` to add source context.

# COMMAND ----------

import json


def parse_json_payload(source_name, payload):
    try:
        # json.loads returns Python data, or raises JSONDecodeError for malformed text.
        return json.loads(payload)
    except json.JSONDecodeError as error:
        # Add source context while chaining the original parser exception.
        raise RuntimeError(
            f"Could not parse JSON from {source_name}"
        ) from error


print(parse_json_payload("orders.json", '{"order_id": 1001}'))

try:
    parse_json_payload("broken_orders.json", '{"order_id": ')
except RuntimeError as error:
    print(f"Load failed: {error}")
    # `__cause__` is populated because parse_json_payload used `raise ... from error`.
    print(f"Original cause: {type(error.__cause__).__name__}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Retry transient errors, not bad input
# MAGIC
# MAGIC Network timeouts and temporary service errors may succeed on a later
# MAGIC attempt. Invalid schemas and malformed records will not; retrying those
# MAGIC wastes time. Always cap retries, and make the delay grow between attempts
# MAGIC (exponential backoff) to avoid overwhelming a recovering service.
# MAGIC
# MAGIC This demonstration simulates two timeouts and then a successful read.

# COMMAND ----------

import time


def retry_with_backoff(operation, max_attempts=3, base_delay_seconds=0.1):
    # Reject invalid configuration before invoking the external operation.
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    # Pass the attempt number into the operation; this also makes the demo stateless.
    for attempt in range(1, max_attempts + 1):
        try:
            # Return immediately on success; other exception types are not retried.
            return operation(attempt)
        except TimeoutError:
            # Re-raise on the final attempt instead of hiding a persistent outage.
            if attempt == max_attempts:
                raise
            # Delays double: base, 2x base, 4x base, and so on.
            delay = base_delay_seconds * (2 ** (attempt - 1))
            print(
                f"Temporary timeout on attempt {attempt}; "
                f"retrying in {delay:.1f}s"
            )
            time.sleep(delay)


def simulated_source_read(attempt):
    # Pretend the source is temporarily unavailable on the first two attempts.
    if attempt < 3:
        raise TimeoutError("source service did not respond in time")
    # The third attempt succeeds, demonstrating the retry success path.
    return ["row-1", "row-2"]


source_rows = retry_with_backoff(simulated_source_read, max_attempts=3)
print(f"Loaded {len(source_rows)} rows on attempt 3.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Fail the pipeline when a batch-level contract is broken
# MAGIC
# MAGIC Row-level quality problems can be quarantined, but a missing required
# MAGIC column often means the whole source schema changed. Fail clearly rather
# MAGIC than producing a misleadingly successful, incomplete load.

# COMMAND ----------

def validate_columns(actual_columns, required_columns):
    # Set difference finds required names absent from the source schema.
    missing = sorted(set(required_columns) - set(actual_columns))
    if missing:
        # A missing column can invalidate a whole batch, so fail visibly.
        raise ValueError(
            f"Source is missing required columns: {', '.join(missing)}"
        )


# First demonstrate a schema that meets the contract.
validate_columns(
    actual_columns=("order_id", "order_date", "amount"),
    required_columns=("order_id", "order_date", "amount"),
)
print("Source schema is valid.")

# Then show how an incomplete schema is reported to the pipeline operator.
try:
    validate_columns(
        actual_columns=("order_id", "amount"),
        required_columns=("order_id", "order_date", "amount"),
    )
except ValueError as error:
    print(f"Batch rejected: {error}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Optional: Databricks file listing
# MAGIC
# MAGIC `dbutils` and `display` are Databricks-provided objects, so this cell is
# MAGIC intentionally commented out and is not run in a plain Python environment.
# MAGIC In a Databricks notebook, replace the example Volume path with a location
# MAGIC that exists and that your identity is permitted to read.
# MAGIC
# MAGIC Handle expected path/permission errors explicitly. Do not convert a failed
# MAGIC listing into an empty file list, because that can make a broken ingestion
# MAGIC look like a successful run with zero input files.

# COMMAND ----------

# source_path = "/Volumes/mycatalog/myschema/myvolume"
# try:
#     # List files at a configured Unity Catalog Volume location.
#     source_files = dbutils.fs.ls(source_path)
# except Exception as error:
#     # Add the failed path as context, while retaining the platform error as cause.
#     raise RuntimeError(f"Could not list input path {source_path}") from error
#
# # Exclude empty files, which commonly appear as placeholders in landing zones.
# non_empty_file_paths = [
#     file_info.path for file_info in source_files if file_info.size > 0
# ]
# display(non_empty_file_paths)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key takeaways
# MAGIC
# MAGIC 1. Catch specific exceptions and handle only failures you understand.
# MAGIC 2. Validate and quarantine bad records so useful rows can still flow.
# MAGIC 3. Preserve the original cause when adding pipeline-level error context.
# MAGIC 4. Retry only transient failures, with a maximum attempt count.
# MAGIC 5. Use context managers for reliable resource cleanup.
# MAGIC 6. Treat a broken batch-level schema as a visible pipeline failure.

# COMMAND ----------

#list comprehension (short hand/dynamic list creation)

list1=[]
print(list1)
range_variable=range(10)
print(list(range_variable))
list2=[a*a for a in range(10)]
print(list2)

list2 = [b for b in range(50) if b%2==0]
print(list2)

list3=[c.path for c in dbutils.fs.ls('/databricks-datasets/credit-card-fraud') if c.size>0]
print(list3)

# COMMAND ----------

display(dbutils.fs.ls('/databricks-datasets/credit-card-fraud'))

# COMMAND ----------

dbutils.fs.ls('/databricks-datasets/credit-card-fraud')

# COMMAND ----------

