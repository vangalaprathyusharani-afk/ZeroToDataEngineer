# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Logging for Data Engineering
# MAGIC
# MAGIC Logging records what a pipeline is doing while it runs: which batch was
# MAGIC processed, how many records were accepted, where failures occurred, and
# MAGIC whether an operation can be retried. Unlike `print`, logging supports
# MAGIC severity levels, timestamps, reusable configuration, and output to files
# MAGIC or centralized log systems.
# MAGIC
# MAGIC The examples use Python's standard library and deterministic sample data.
# MAGIC They run outside Databricks; an optional section explains how to direct
# MAGIC logs to a Databricks-accessible storage location.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configure a logger once
# MAGIC
# MAGIC A log record has a severity:
# MAGIC
# MAGIC - `DEBUG`: diagnostic details, usually disabled in normal production runs.
# MAGIC - `INFO`: normal progress, such as a batch starting or completing.
# MAGIC - `WARNING`: unexpected but recoverable conditions, such as rejected rows.
# MAGIC - `ERROR`: an operation failed and needs attention.
# MAGIC - `CRITICAL`: a severe failure that may stop the whole service or pipeline.
# MAGIC
# MAGIC Configure a named logger and handler explicitly. `basicConfig` only takes
# MAGIC effect when the root logger has no handlers, which can be confusing in
# MAGIC notebooks and managed environments. This setup also avoids adding a
# MAGIC duplicate handler when the cell is run more than once.

# COMMAND ----------

import logging

logger = logging.getLogger("data_engineering_lesson")
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Add one console handler if it has not already been set up in this notebook.
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(console_handler)

logger.debug("Debug details are available for troubleshooting.")
logger.info("Pipeline logging is configured.")
logger.warning("This is an example of a recoverable warning.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Log useful pipeline context
# MAGIC
# MAGIC A message such as "job started" is not very useful when many jobs run at
# MAGIC once. Include operational context such as pipeline name, run ID, source,
# MAGIC and batch ID. Prefer parameterized logging (`logger.info("...%s", value)`)
# MAGIC over f-strings: the logging system can skip formatting when the level is
# MAGIC disabled, and the message template stays consistent.
# MAGIC
# MAGIC Never log passwords, access tokens, full payment-card data, or unnecessary
# MAGIC personally identifiable information. A run or batch identifier is usually
# MAGIC enough to connect logs to protected records stored elsewhere.

# COMMAND ----------

pipeline_name = "orders_ingestion"
run_id = "run-20261104-001"
source_name = "landing/orders"
batch_id = "batch-0007"

logger.info(
    "Pipeline started | pipeline=%s | run_id=%s | source=%s | batch_id=%s",
    pipeline_name,
    run_id,
    source_name,
    batch_id,
)

# Do not include customer email or other sensitive values in routine log lines.
logger.info(
    "Reading batch | run_id=%s | batch_id=%s | input_format=%s",
    run_id,
    batch_id,
    "csv",
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Record data quality outcomes
# MAGIC
# MAGIC Data engineering jobs need both observability and a clear disposition for
# MAGIC bad data. Log a warning with the source position and a safe reason, then
# MAGIC quarantine the original row separately. Avoid putting the entire raw row
# MAGIC into logs because it may contain sensitive fields and can create very large
# MAGIC log volumes.

# COMMAND ----------

from decimal import Decimal, InvalidOperation

raw_orders = [
    {"order_id": "O-1001", "amount": "25.50"},
    {"order_id": "O-1002", "amount": "not-a-number"},
    {"order_id": "O-1003", "amount": "-8.00"},
]


def parse_order_amount(raw_amount):
    """Parse an order amount and reject values outside the data contract."""
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation as error:
        raise ValueError("amount is not a valid decimal") from error

    if not amount.is_finite() or amount < 0:
        raise ValueError("amount must be finite and non-negative")
    return amount


accepted_orders = []
quarantined_orders = []

for row_number, raw_order in enumerate(raw_orders, start=1):
    try:
        # Parse into a new output record; keep the source row untouched.
        accepted_orders.append(
            {
                "order_id": raw_order["order_id"],
                "amount": parse_order_amount(raw_order["amount"]),
            }
        )
    except ValueError as error:
        # Log safe identifiers and the validation reason, not the full raw row.
        logger.warning(
            "Rejected input row | run_id=%s | row_number=%d | order_id=%s | reason=%s",
            run_id,
            row_number,
            raw_order.get("order_id", "unknown"),
            error,
        )
        quarantined_orders.append(
            {"row_number": row_number, "record": raw_order, "reason": str(error)}
        )

logger.info(
    "Validation completed | run_id=%s | accepted=%d | quarantined=%d",
    run_id,
    len(accepted_orders),
    len(quarantined_orders),
)
print("Accepted records:", accepted_orders)
print("Quarantined records:", quarantined_orders)

# COMMAND ----------

import logging
from io import StringIO

log_stream = StringIO()

handler = logging.StreamHandler(log_stream)

handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
)

logger = logging.getLogger("etl")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("Pipeline started")

print(log_stream.getvalue())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Log failures with their traceback
# MAGIC
# MAGIC Catch an exception only when you can add context, recover, or report it.
# MAGIC `logger.exception` belongs inside an `except` block; it records the message
# MAGIC and the active traceback. After logging, re-raise if the pipeline cannot
# MAGIC safely continue. Do not log an error and then return a success-shaped value.

# COMMAND ----------

def load_required_configuration(configuration):
    """Return a required endpoint or fail with a clear configuration error."""
    try:
        return configuration["endpoint"]
    except KeyError:
        # Raise a more actionable message while retaining the original cause.
        raise ValueError("Required configuration key 'endpoint' is missing") from None


configuration = {"timeout_seconds": 30}
try:
    endpoint = load_required_configuration(configuration)
except ValueError:
    # `logger.exception` includes the stack trace for diagnosing this failure.
    logger.exception(
        "Pipeline configuration is invalid | run_id=%s | pipeline=%s",
        run_id,
        pipeline_name,
    )
    # This demo continues so later notebook cells can run. A real job should
    # generally re-raise here so the orchestrator marks the run as failed.
else:
    logger.info("Using configured endpoint: %s", endpoint)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Log a bounded retry for a transient source error
# MAGIC
# MAGIC A timeout may be temporary, so a pipeline can retry it a limited number
# MAGIC of times. Log each retry with its attempt and delay. Do not retry every
# MAGIC exception: malformed input, missing permissions, or a broken schema usually
# MAGIC need a fix rather than another identical request.
# MAGIC
# MAGIC The operation below receives its attempt number as an argument and does
# MAGIC not depend on global mutable state, making the demonstration predictable.

# COMMAND ----------

import time


def retry_read(operation, max_attempts=3, base_delay_seconds=0.1):
    """Retry a timeout with bounded exponential backoff; propagate other errors."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):
        try:
            result = operation(attempt)
        except TimeoutError:
            if attempt == max_attempts:
                # The final failure is logged with traceback and re-raised.
                logger.exception(
                    "Source read exhausted retries | run_id=%s | attempts=%d",
                    run_id,
                    max_attempts,
                )
                raise

            delay_seconds = base_delay_seconds * (2 ** (attempt - 1))
            logger.warning(
                "Transient timeout; retrying | run_id=%s | attempt=%d/%d | delay_seconds=%.2f",
                run_id,
                attempt,
                max_attempts,
                delay_seconds,
            )
            time.sleep(delay_seconds)
        else:
            logger.info(
                "Source read succeeded | run_id=%s | attempt=%d",
                run_id,
                attempt,
            )
            return result


def simulated_source_read(attempt):
    """Simulate a source that times out twice and succeeds on the third try."""
    if attempt < 3:
        raise TimeoutError("simulated source timeout")
    return ["record-1", "record-2"]


source_records = retry_read(simulated_source_read)
logger.info(
    "Read completed | run_id=%s | records=%d",
    run_id,
    len(source_records),
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Write logs to a file for later inspection
# MAGIC
# MAGIC A file handler is useful for a local script or a single-node job. In a
# MAGIC distributed environment, local executor files may be temporary or spread
# MAGIC across machines; production deployments commonly ship logs to a centralized
# MAGIC platform instead. This example uses a temporary directory, writes several
# MAGIC records, and prints the file so it is self-contained.

# COMMAND ----------

from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as log_directory:
    log_path = Path(log_directory) / "orders_pipeline.log"

    # A separate logger keeps this file example independent of console setup.
    file_logger = logging.getLogger("data_engineering_file_demo")
    file_logger.setLevel(logging.INFO)
    file_logger.propagate = False

    # Close any prior demo handler so rerunning this notebook cell is safe.
    for handler in file_logger.handlers[:]:
        file_logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    file_logger.addHandler(file_handler)

    file_logger.info(
        "Batch completed | run_id=%s | read=%d | accepted=%d | quarantined=%d",
        run_id,
        len(raw_orders),
        len(accepted_orders),
        len(quarantined_orders),
    )

    # Flush pending messages before reading the file.
    file_handler.flush()
    print(log_path.read_text(encoding="utf-8"))

    # Close the handler before the temporary directory removes its files.
    file_logger.removeHandler(file_handler)
    file_handler.close()

# COMMAND ----------

# DBTITLE 1,Cell 15
import logging
from pathlib import Path
from datetime import datetime

# Volume path
log_dir = Path("/Volumes/workspace/default/mydefaultvolume/logs")

# Create directory if it doesn't exist
log_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

log_path = log_dir / f"orders_pipeline_{timestamp}.log"

file_logger = logging.getLogger("orders_pipeline")
file_logger.setLevel(logging.INFO)
file_logger.propagate = False

# Clean up existing handlers (important in notebooks)
for handler in file_logger.handlers[:]:
    file_logger.removeHandler(handler)
    handler.close()

file_handler = logging.FileHandler(
    log_path,
    encoding="utf-8"
)

file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
)

file_logger.addHandler(file_handler)

file_logger.info(
    "Batch completed | run_id=%s | read=%d | accepted=%d | quarantined=%d",
    run_id,
    len(raw_orders),
    len(accepted_orders),
    len(quarantined_orders),
)

file_handler.flush()

# Close the handler before reading the file back: while the write handle is
# still open, the volume filesystem cannot open the same file for reading.
file_logger.removeHandler(file_handler)
file_handler.close()

print(log_path.read_text(encoding="utf-8"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Log data engineering metrics and completion
# MAGIC
# MAGIC Useful batch metrics include input, accepted, rejected, and output counts,
# MAGIC plus elapsed time. These make it easier to notice sudden drops, spikes, or
# MAGIC quality regressions. Logs are not a replacement for durable metrics and
# MAGIC lineage systems, but consistent key-value fields make them easier to query.

# COMMAND ----------

from time import perf_counter

batch_started = perf_counter()

# A placeholder transformation demonstrates where pipeline work would occur.
output_orders = accepted_orders
elapsed_seconds = perf_counter() - batch_started

logger.info(
    "Batch completed | pipeline=%s | run_id=%s | batch_id=%s | input=%d | "
    "output=%d | quarantined=%d | elapsed_seconds=%.4f",
    pipeline_name,
    run_id,
    batch_id,
    len(raw_orders),
    len(output_orders),
    len(quarantined_orders),
    elapsed_seconds,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Databricks logging considerations
# MAGIC
# MAGIC Databricks captures notebook and driver output, but a path such as `/` or
# MAGIC a DBFS/Volume path is not automatically writable in every runtime. Confirm
# MAGIC the destination and permissions before configuring a file handler.
# MAGIC
# MAGIC For a small driver-side demo, a Unity Catalog Volume may be used if the
# MAGIC compute has permission. Avoid writing one shared log file from many Spark
# MAGIC executors: concurrent writes can interleave or overwrite data. Prefer
# MAGIC platform driver/executor logs or a centralized logging destination for
# MAGIC distributed workloads. Do not log full records if they may contain PII.

# COMMAND ----------

# Example only: configure this after confirming the Volume exists and is writable.
# volume_log_path = "/Volumes/mycatalog/myschema/myvolume/orders_pipeline.log"
# volume_handler = logging.FileHandler(volume_log_path, encoding="utf-8")
# volume_handler.setFormatter(
#     logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
# )
# logger.addHandler(volume_handler)
# try:
#     logger.info("Writing driver log to configured Volume | run_id=%s", run_id)
# finally:
#     logger.removeHandler(volume_handler)
#     volume_handler.close()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key takeaways
# MAGIC
# MAGIC 1. Configure named loggers with useful severity levels and consistent fields.
# MAGIC 2. Include run, batch, and source context so operators can find the right job.
# MAGIC 3. Log safe identifiers and aggregate quality metrics, not sensitive raw data.
# MAGIC 4. Use `logger.exception` inside an exception handler to preserve tracebacks.
# MAGIC 5. Retry only transient failures, cap attempts, and log each retry.
# MAGIC 6. Treat local files as a demo; use centralized logs for distributed jobs.