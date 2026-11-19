# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# dependencies = [
#   "\"pandas>=2.0,<4\"",
#   "\"openpyxl>=3.1\"",
#   "\"pyarrow>=13\"",
# ]
# ///
# MAGIC %md
# MAGIC # Pandas for data engineering: from first Series to a reliable pipeline
# MAGIC
# MAGIC **Audience:** beginner through advanced Python/data engineering learners. **Format:** instructor-led, runnable top to bottom. All names, orders, and values are synthetic.
# MAGIC
# MAGIC **Learning path**
# MAGIC 1. Understand Series, DataFrames, indexes, data types, and selection.
# MAGIC 2. Create and ingest tables from Python objects, CSV, delimited text, fixed-width text, Excel, JSON, and JSON Lines.
# MAGIC 3. Profile, cleanse, validate, quarantine, transform, join, and aggregate data.
# MAGIC 4. Apply practical patterns: deduplication, event-time windows, slowly changing dimensions, incremental processing, and reconciliation.
# MAGIC
# MAGIC **Run instructions:** Import this `.py` file into a Databricks workspace as a **SOURCE** notebook, attach Python compute, and select **Run all**. Cells depend on earlier cells; rerun from the start after changing a source cell. Outputs are produced during execution, not stored in the notebook.
# MAGIC
# MAGIC Before running, upload all 12 files from the companion `sample_data` folder to `/Volumes/workspace/default/mydefaultvolume/input/pandas/`. Ensure `/Volumes/workspace/default/mydefaultvolume/output/pandas/` exists and the compute identity can read the inputs and read and write the outputs. The notebook does not generate source files. The supplied synthetic files and their contents are required for the fixture-specific assertions.
# MAGIC
# MAGIC **Dependencies:** The setup cell uses Databricks `%pip` to ensure compatible pandas, `openpyxl` (Excel), and `pyarrow` (Parquet, ORC, Feather) versions are available, installing missing packages or upgrading versions below the specified minimum. Already-suitable packages are normally left in place. The following cell restarts Python before the lesson to load the installed versions; this clears Python variables from earlier work in this notebook. Installing packages requires permission and access to a configured package source. Setup failures stop the run and must be resolved rather than ignored.
# MAGIC
# MAGIC **Teaching tip:** For each section, predict the output first, run the cell, and explain what a downstream consumer would experience if the data were wrong.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Environment setup
# MAGIC Run the next cells before importing pandas. `%pip` manages notebook-scoped packages, not source data files. The version ranges require pandas 2.x or 3.x, openpyxl 3.1 or later, and pyarrow 13 or later; pandas itself also installs its own dependencies. The Python restart applies library changes and clears existing notebook Python state. Notebook-scoped libraries may need to be reinstalled after a compute session ends.

# COMMAND ----------

# MAGIC %pip install "pandas>=2.0,<4" "openpyxl>=3.1" "pyarrow>=13"

# COMMAND ----------

# Restart before creating lesson variables so newly installed packages are loaded.
dbutils.library.restartPython()

# COMMAND ----------

# Load file-handling tools and pandas for tabular data.
import json

# Make BytesIO available to the following notebook cells.
from io import BytesIO

# Make Path available to the following notebook cells.
from pathlib import Path

# Make uuid4 available to the following notebook cells.
from uuid import uuid4

# Make pandas available to the following notebook cells.
import pandas as pd

# Widen printed tables so students can see more columns in the output.
pd.set_option("display.max_columns", 30)

# Call pd.set_option with the stated inputs.
pd.set_option("display.width", 140)

# Display pandas together with the values supplied below.
print("pandas:", pd.__version__)

# Display Sample data is synthetic; amounts are illustrative, not financial advice. together with the values supplied below.
print("Sample data is synthetic; amounts are illustrative, not financial advice.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Locate and check the source files
# MAGIC A data engineer often receives business facts through different interfaces. The provided files are *small, independent examples*, not multiple copies of one canonical dataset. The orders CSV deliberately contains duplicates and invalid values so that later quality rules have something meaningful to catch.
# MAGIC
# MAGIC `Path` joins the volume directory and each filename. Upload the companion sample files unchanged before running and create the output directory separately. The check below reports missing files or output directory; it does not create or modify them. CSV/text files use UTF-8 except the explicitly named Windows-1252 example. The Excel file has two sheets; JSON Lines has one complete JSON object per line.

# COMMAND ----------

# Point every input reader at the supplied Unity Catalog volume directory.
data_dir = Path("/Volumes/workspace/default/mydefaultvolume/input/pandas/")

# Set output_dir: construct a filesystem path without reading or writing it.
output_dir = Path("/Volumes/workspace/default/mydefaultvolume/output/pandas/")

# Set required_files: collect the explicitly listed values.
required_files = [
    "orders.csv", "customers.csv", "products_semicolon.txt", "shipments_pipe.txt",
    "inventory_tabs.tsv", "sensor_multidelimiter.txt", "employees_no_header.txt",
    "employees_windows1252.csv", "stores_fixed_width.txt", "events.jsonl",
    "web_orders.json", "sales_targets.xlsx",
]
# Fail before the lesson starts if the volume is inaccessible or files are absent.
missing_files = [name for name in required_files if not (data_dir / name).is_file()]

# Run this branch only when missing_files is true.
if missing_files:

    # Stop with the explicit error shown when this condition is met.
    raise FileNotFoundError(
        f"Missing or inaccessible input files in {data_dir}: {', '.join(missing_files)}. "
        "Upload the companion sample_data files and check volume access permissions."
    )

# Run this branch only when not output_dir.is_dir() is true.
if not output_dir.is_dir():

    # Stop with the explicit error shown when this condition is met.
    raise FileNotFoundError(
        f"Output directory does not exist or is inaccessible: {output_dir}. "
        "Create it in the volume and check access permissions."
    )

# Display Reading sample files from together with the values supplied below.
print("Reading sample files from:", data_dir)

# Display Writing lesson output to together with the values supplied below.
print("Writing lesson output to:", output_dir)

# Display the result of '\n'.join(required_files) for inspection.
print("\n".join(required_files))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. What is a Series?
# MAGIC Think of a **Series** as one labeled column of a spreadsheet: the values are the column's contents, and the index is a set of row labels. A Series has a single dtype; pandas also supports nullable dtypes such as `Int64` and `string`. Missing values are not automatically zeros.
# MAGIC
# MAGIC In data engineering, a Series might represent delivery times, customer IDs, or a quality flag. Vectorized operations express a rule across the whole column without writing a Python loop.
# MAGIC
# MAGIC **Arguments used below:** `pd.Series(data, index=..., name=...)` takes values as its first argument; `index` labels each value and `name` labels the resulting column. `mean()` computes the mean of nonmissing values. For example, `pd.Series([5, 7], index=["A", "B"], name="days")` maps A to 5 and B to 7.

# COMMAND ----------

# Associate each delivery value with an order label and give the Series a name.
delivery_days = pd.Series([2, 4, 3], index=["order-A", "order-B", "order-C"], name="delivery_days")
# delivery_days = pd.Series([2, 4, 3], name="delivery_days")
print("Series:\n", delivery_days)

# Display Labels together with the values supplied below.
print("Labels:", delivery_days.index.tolist(), "| dtype:", delivery_days.dtype)
# Add one to every value at once; mean() summarizes all nonmissing values.
print("Days with one-day delay:\n", delivery_days + 1)

# Display Average delivery days together with the values supplied below.
print("Average delivery days:", delivery_days.mean())

# Inspect the python object type.
type(delivery_days)

# Display the result of delivery_days['order-A'] for inspection.
print(delivery_days["order-A"])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create Series in several ways
# MAGIC A list or tuple gets a default integer index; a dictionary uses its keys as labels; a scalar is repeated for an explicit index. Selecting a DataFrame column and reading a file can also produce a Series. Nullable integers retain missing values as `<NA>` instead of forcing an ordinary integer column to represent a missing number.
# MAGIC
# MAGIC **Options used:** `name="units"` names the Series; `index=["A", "B", "C"]` supplies the scalar's three labels; `dtype="Int64"` selects nullable integers. In `read_csv(path, dtype={"customer_id": "string"})`, the first argument is the source path and the `dtype` mapping keeps that column as text. Use `dtype` for IDs so leading zeroes survive.

# COMMAND ----------

# Lists get a positional index; dictionary keys become labels.
from_list = pd.Series([10, 20, 30], name="units")

# Set from_dict: construct a labeled one-dimensional Series.
from_dict = pd.Series({"North": 120, "South": 80}, name="sales")
# A scalar is repeated for each supplied label; a tuple also supplies values.
from_scalar = pd.Series(0, index=["A", "B", "C"], name="initial_count")

# Set from_tuple: construct a labeled one-dimensional Series.
from_tuple = pd.Series((1.5, 2.5), name="weight")
# Nullable Int64 supports both whole numbers and a missing value.
nullable = pd.Series([1, None, 3], dtype="Int64", name="nullable_units")
# A single selected DataFrame column is a Series; preserve IDs as strings.
from_csv_column = pd.read_csv(data_dir / "customers.csv", dtype={"customer_id": "string"})["customer_id"]

# Display List together with the values supplied below.
print("List:\n", from_list, "\nDictionary:\n", from_dict)

# Display Scalar together with the values supplied below.
print("Scalar:\n", from_scalar, "\nTuple:\n", from_tuple)

# Display Nullable together with the values supplied below.
print("Nullable:\n", nullable, "\nColumn from CSV:\n", from_csv_column)

# Display the Python type of from_csv_column.
print(type(from_csv_column))

# COMMAND ----------

# Set from_csv_column: select the specified labels or positions from pd.read_csv(data_dir / 'customers.csv', dt....
from_csv_column = pd.read_csv(data_dir / "customers.csv", dtype={"customer_id": "string"})["customer_id"]
# from_csv_column = pd.read_csv(data_dir / "customers.csv", dtype={"customer_id": "string"})
# print("List:\n", from_list, "\nDictionary:\n", from_dict)
# print("Scalar:\n", from_scalar, "\nTuple:\n", from_tuple)
# print("Nullable:\n", nullable, "\nColumn from CSV:\n", from_csv_column)
type(from_csv_column)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Inspect Python object types and render small tables
# MAGIC `type` identifies whether a value is a Series, DataFrame, or string. In a Databricks notebook `display(df)` offers an interactive table; `print(df)` works in a plain Python environment too. `to_string(index=False)` creates text for a small log or report, not a structured data exchange format. Do not log sensitive fields or convert huge tables into strings.
# MAGIC
# MAGIC **Option:** `to_string(index=False)` omits row labels from the rendered text; `index=True` would include them. It does not change the original DataFrame.

# COMMAND ----------

# A selected column is a Series, its containing table is a DataFrame,
# and to_string renders text without changing either object.
type_example = pd.DataFrame({"region": ["North", "South"], "orders": [3, 5]})

# Set rendered_table: render the table as text for display.
rendered_table = type_example.to_string(index=False)
# rendered_table = type_example.to_string()
print("Column type:", type(type_example["orders"]))

# Display Table type together with the values supplied below.
print("Table type:", type(type_example), "| rendered type:", type(rendered_table))

# Display Small text report together with the values supplied below.
print("Small text report:\n", rendered_table)
# Databricks supplies display; standard Python environments may not have it.
if "display" in globals():

    # Call display with the stated inputs.
    display(type_example)

# COMMAND ----------

# Display the result of globals().keys() for inspection.
print(globals().keys())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Index alignment: labels matter
# MAGIC Imagine adding two price lists by product name. Pandas matches labels, not just row positions. A label missing on either side produces a missing result. This is helpful for business keys, but surprising if two independent columns happen to have different indexes. `loc` selects **labels**; `iloc` selects **positions**.
# MAGIC
# MAGIC **Option:** `jan.add(feb, fill_value=0)` treats a value missing on one side as zero before adding. This is a business assumption; if both sides are missing, the result remains missing.

# COMMAND ----------

# Addition matches the fruit labels, even when their positions differ.
jan = pd.Series({"apple": 10, "banana": 20})

# Set feb: construct a labeled one-dimensional Series.
feb = pd.Series({"banana": 5, "cherry": 7})

# Display Aligned addition together with the values supplied below.
print("Aligned addition:\n", jan + feb)
# fill_value=0 supplies zero for a label absent on one side of this addition.
print("Treat absent labels as zero:\n", jan.add(feb, fill_value=0))
# loc uses the label; iloc uses the zero-based position.
print("Label banana:", jan.loc["banana"], "| first position:", jan.iloc[0])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. What is a DataFrame?
# MAGIC A **DataFrame** is a labeled two-dimensional table: rows are records and columns are attributes. Think of a spreadsheet with a header. A critical engineering question is **grain**: what does one row represent? In the order example the grain is *one order line*, identified by `(order_id, line_id)`, not an entire order.
# MAGIC
# MAGIC A DataFrame's index is useful for alignment and selection, but it is not automatically a unique business key or a database primary key.
# MAGIC
# MAGIC **Arguments:** `pd.DataFrame(data, columns=["name", "orders"])` takes column-oriented or row-oriented `data`; `columns` supplies or selects column names in the specified order. For row lists, the first value maps to `name` and the second to `orders`.

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Types of Data Formats
# MAGIC * Structured - Fixed storage format schema and easily readable by human (SQl Table, excel file)
# MAGIC * Semistructured - Dynamic Schema and with limited readable flexibility ( JSon, XML)
# MAGIC * Unstructured -  No Fixed structure ( Image, Audio File, Video File)

# COMMAND ----------

from_rows=[["Asha",2],["Rame",5]]
df=pd.DataFrame(from_rows,columns=["name","orders"])
display(df)

# COMMAND ----------

# greater than 1
# 2 = 2*1
# 5= 1*5 

# COMMAND ----------

print(list(range(2,2)))

# COMMAND ----------

def func_even_odd(numbers):
    prime_list=[] 
    other_list=[]
    for i in numbers:
        if i>1:
            prime_flag=True
            for j in range(2,i):
                if i%j==0:
                    prime_flag=False
                    break
            
            if prime_flag==True:
                prime_list.append(i)
            else:
                other_list.append(i)
        else:            
            other_list.append(i)
        
    return prime_list,other_list

list_numbers = list(range(1,10))
func_even_odd(list_numbers)


# COMMAND ----------

print(list(range(2, 3)))

# COMMAND ----------

semistructured_example= {"name": ["Asha", "Ben","Naveen"], "orders": [3, 5,6],"Address": ["123 Main Street",None, "456 Oak Avenue"]}
df=pd.DataFrame(semistructured_example)
print(df)

array1=[{"name": "Asha", "orders": 3}, {"name": "Ben", "orders": 5,"address": "456, Hyderabad","Address": "500046, Hyderabad"}, {"name": "Charlie", "orders": 2,"Address": "123, Hyderabad"}]
array2=[{"name": "Asha", "orders": 3}, {"name": "Ben", "orders": 5,"Address": "456, Hyderabad"}, {"name": "Charlie", "orders": 2,"Address": "123, Hyderabad"}]
df_array1=pd.DataFrame(array1)
df_array2=pd.DataFrame(array2)
print(df_array1)
print(df_array2)
a=''



# COMMAND ----------

from_rows = pd.DataFrame([["Asha", 3], ["Ben", 5,"123, Hyderabad"]], columns=["name", "orders","Address"])
print(from_rows)

# COMMAND ----------

# Build the same table from columns, record dictionaries, or lists of row values.
from_columns = pd.DataFrame({"name": ["Asha", "Ben"], "orders": [3, 5]})

print(from_columns)

# Set from_records: construct a two-dimensional DataFrame.
from_records = pd.DataFrame([{"name": "Asha", "orders": 3}, {"name": "Ben", "orders": 5}])

# Set from_rows: construct a two-dimensional DataFrame.
from_rows = pd.DataFrame([["Asha", 3], ["Ben", 5]], columns=["name", "orders"])
# Series inputs align by their index labels, not merely by their positions.
from_series = pd.DataFrame({"orders": pd.Series({"North": 3, "South": 5}),
                            "returns": pd.Series({"North": 1, "South": 0})})

# Display Dictionary of columns together with the values supplied below.
print("Dictionary of columns:\n", from_columns)

# Display List of dictionaries together with the values supplied below.
print("List of dictionaries:\n", from_records)

# Display Rows with explicit columns together with the values supplied below.
print("Rows with explicit columns:\n", from_rows)

# Display Aligned Series together with the values supplied below.
print("Aligned Series:\n", from_series)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Ingest files: the boundary between the outside world and a table
# MAGIC ### CSV: read raw values without losing evidence
# MAGIC `read_csv` accepts a path and parsing options. Read identifiers and dirty fields as strings first: `001` is an identifier, not the number `1`; invalid numbers should remain visible for quality checks. Here `keep_default_na=False` preserves literal text including blank fields. In another source, decide explicitly which strings (for example `NULL`) should be treated as missing.
# MAGIC
# MAGIC Specifying a schema and encoding is safer than relying on inference. A DataFrame holds in-memory data on the driver; reading a huge CSV this way can exhaust driver memory.
# MAGIC
# MAGIC **`read_csv` arguments used:** the first argument is the source path; `dtype="string"` reads every field as text; `keep_default_na=False` preserves empty strings and default NA tokens as text; `encoding="utf-8"` decodes bytes. For example, `"001"` stays `"001"` rather than becoming the integer `1`. A specified encoding must match the source contract.

# COMMAND ----------

csv_df=pd.read_csv(data_dir / "orders.csv")
display(csv_df)
csv_df.info()

# COMMAND ----------

# this is to create spark DF from pandas df
spark_df=spark.createDataFrame(csv_df)

# COMMAND ----------

spark_df.show(5)

# COMMAND ----------

# Pandas Parser Engines
# C Engine - This is the fastest engine and default engine which is used to handle single delimiter with out any rgex expresssions and load data in chunks
# python engine - This is little slower Engine which is used to handle multiple delimiters with rgex expressions and load data in chunks
# pyarrow - This is the fastest engine which is used to handle single delimiter with out any rgex expresssions and load data in chunks from columnar files like parquet,avro
#openxyl - This is used to process excel files


# COMMAND ----------

raw_orders = pd.read_csv(data_dir / "orders.csv", dtype="string", keep_default_na=False, encoding="utf-8")
display(raw_orders)
raw_orders.info()

# COMMAND ----------

# Keep all incoming columns as strings and preserve empty fields for profiling.
raw_orders = pd.read_csv(data_dir / "orders.csv", dtype="string", keep_default_na=False, encoding="utf-8")

# Set customers: parse the specified delimited input into pandas objects.
customers = pd.read_csv(data_dir / "customers.csv", dtype="string", keep_default_na=False, encoding="utf-8")

# Display Rows and columns together with the values supplied below.
print("Rows and columns:", raw_orders.shape)

# Display First rows together with the values supplied below.
print("First rows:\n", raw_orders.head(3))

# Display Column types together with the values supplied below.
print("Column types:\n", raw_orders.dtypes)

# Display Customers together with the values supplied below.
print("Customers:\n", customers)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Delimited text and fixed-width records
# MAGIC A delimiter is the character between fields: `;` for the product feed, `|` for shipments, and a tab for inventory. `sep` specifies it. A **multi-character** separator such as `::` requires the Python parser and is interpreted as a regular expression. Regex separators can mishandle quoted fields containing separators; use a format-aware parser or ask the producer to supply a standard format if quoting matters.
# MAGIC
# MAGIC Fixed-width files use character positions instead of separators. `colspecs` uses zero-based, end-exclusive slices. Confirm widths and encoding with the provider before parsing.
# MAGIC
# MAGIC **Arguments:** `sep=";"`, `sep="|"`, and `sep="\t"` choose semicolon, pipe, and tab respectively; `dtype="string"` preserves the raw text. `sep="::", engine="python"` uses the Python regex parser for a multi-character separator. For `read_fwf`, `colspecs=[(0, 4), (4, 14), (14, 18)]` defines end-exclusive character ranges and `names=[...]` assigns the three columns.

# COMMAND ----------

products = pd.read_csv(data_dir / "products_semicolon.txt",sep=";")
display(products)
products.info()

# COMMAND ----------

# Specify each file's separator explicitly; \t represents one tab character.
products = pd.read_csv(data_dir / "products_semicolon.txt", sep=";", dtype="string")

# Set shipments: parse the specified delimited input into pandas objects.
shipments = pd.read_csv(data_dir / "shipments_pipe.txt", sep="|", dtype="string")

# Set inventory: parse the specified delimited input into pandas objects.
inventory = pd.read_csv(data_dir / "inventory_tabs.tsv", sep="\t", dtype="string")

# Display Semicolon together with the values supplied below.
print("Semicolon:\n", products, "\nPipe:\n", shipments, "\nTab:\n", inventory)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Multi-character separators and fixed-width records
# MAGIC `engine="python"` supports the `sep="::"` regular-expression separator. `read_fwf(..., colspecs=[...], names=[...], dtype="string")` reads fixed character positions, assigns column names, and preserves text values.

# COMMAND ----------

sensors = pd.read_csv(data_dir / "sensor_multidelimiter.txt", sep="::", engine="python",dtype="string")
display(sensors)

# COMMAND ----------

stores = pd.read_fwf(data_dir / "stores_fixed_width.txt", colspecs=[(0, 4), (4, 14), (14, 18)]
                     , dtype="string",names=["store_id", "region", "stock"])
display(stores)

print(len(stores["store_id"][0]))

# COMMAND ----------

stores = pd.read_fwf(data_dir / "stores_fixed_width.txt", colspecs=[(0, 9), (14, 18)]
                     , dtype="string",names=["store_id_region", "stock"])
display(stores)

print(len(stores["store_id_region"][0]))

# COMMAND ----------

#read csv file with no headers
df_no_header=pd.read_csv(data_dir/"customers.csv",header=None,names=["customer_id","customer_name","region","signup_date"],skiprows=1)
display(df_no_header)
df_no_header=pd.read_csv(data_dir/"customers.csv",header=None,skiprows=1)
display(df_no_header)

#read only even rows from a file
df_even_rows=pd.read_csv(data_dir/"customers.csv",header=None,names=["customer_id","customer_name","region","signup_date"],skiprows=lambda x:x%2!=0)
# display(df_even_rows)
print(df_even_rows)

# COMMAND ----------

# The multi-character separator needs the Python parser and is treated as regex.
sensors = pd.read_csv(data_dir / "sensor_multidelimiter.txt", sep="::", engine="python", dtype="string")
# Fixed-width slices are zero-based and exclude the ending character position.
stores = pd.read_fwf(data_dir / "stores_fixed_width.txt", colspecs=[(0, 4), (4, 14), (14, 18)],
                     names=["store_id", "region", "stock"], dtype="string")

# Display Multi-character together with the values supplied below.
print("Multi-character:\n", sensors, "\nFixed-width:\n", stores)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Headerless feeds and legacy encodings
# MAGIC `header=0` (the default inferred behavior here) reads the first line as column names. A supplier file with **no** header needs `header=None` and explicit `names`; otherwise its first employee disappears into the column labels. A file's encoding describes how bytes represent text. Use the encoding agreed with the producer: this example contains Windows-1252 bytes and must be read as `windows-1252`.
# MAGIC
# MAGIC `latin1` can decode any byte but may silently produce incorrect characters for Windows-1252 punctuation. Never rely on a decoder simply succeeding as proof the encoding is correct. The files are synthetic training fixtures, not real employee data.
# MAGIC
# MAGIC **Arguments:** `header=None` says the first line is a record; `names=[...]` names its fields; `sep="|"` chooses the separator. The `dtype={...}` mapping gives identifiers nullable strings and salary nullable `Int64`. `encoding="windows-1252"` selects the character decoder for the separate legacy feed.

# COMMAND ----------

legacy_employees = pd.read_csv(data_dir / "employees_windows1252.csv",encoding="windows-1252", dtype="string")
display(legacy_employees)

# COMMAND ----------

# The first record is data, not a header; assign an explicit four-column schema.
employees_feed = pd.read_csv(
    data_dir / "employees_no_header.txt", sep="|", header=None,
    names=["employee_id", "employee_name", "department_id", "salary"],
    dtype={"employee_id": "string", "employee_name": "string",
           "department_id": "string", "salary": "Int64"},
)
# Decode the supplied Windows-1252 source using its declared encoding.
legacy_employees = pd.read_csv(data_dir / "employees_windows1252.csv", encoding="windows-1252", dtype="string")

# Display Headerless employee feed together with the values supplied below.
print("Headerless employee feed:\n", employees_feed)

# Display Windows-1252 feed together with the values supplied below.
print("Windows-1252 feed:\n", legacy_employees)

# Require `len(employees_feed) == 3 and employees_feed.iloc[0]['employee_id'] == 'E001'`; stop if this invariant fails.
assert len(employees_feed) == 3 and employees_feed.iloc[0]["employee_id"] == "E001"

# Require `legacy_employees.loc[0, 'name'] == 'André'`; stop if this invariant fails.
assert legacy_employees.loc[0, "name"] == "Andr\u00e9"

# COMMAND ----------

employees_feed.info()

# COMMAND ----------

legacy_employees = pd.read_csv(data_dir / "employees_windows1252.csv", encoding="windows-1252", dtype="string",index_col=False)
print(legacy_employees)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Excel: sheets are separate tables
# MAGIC `read_excel` accepts a sheet name and dtype. Look at sheet names first: spreadsheets may contain multiple business tables. Production spreadsheets can also have merged cells, shifted headers, formulas, and formatting that does not constitute a real schema; agree on a contract with the producer.
# MAGIC
# MAGIC **Arguments:** `ExcelFile(path, engine="openpyxl")` opens the workbook using openpyxl; `read_excel(excel_file, sheet_name="Targets")` selects the named worksheet. The example reads `Calendar` separately with the same option.

# COMMAND ----------

# Inspect the workbook, then load each named worksheet as a separate DataFrame.
excel_file = pd.ExcelFile(data_dir / "sales_targets.xlsx", engine="openpyxl")

# Display Sheets together with the values supplied below.
print("Sheets:", excel_file.sheet_names)

# Set targets: read the specified Excel worksheet.
targets = pd.read_excel(excel_file, sheet_name="Targets")

# Set calendar: read the specified Excel worksheet.
calendar = pd.read_excel(excel_file, sheet_name="Calendar")

# Display Targets together with the values supplied below.
print("Targets:\n", targets, "\nCalendar:\n", calendar)

# COMMAND ----------

# MAGIC %md
# MAGIC ### JSON and JSON Lines
# MAGIC JSON can be nested: the web order has an object for the customer and a list of items. `json_normalize` flattens nested objects; `record_path` expands item arrays and repeats the parent order ID. The grain changes from **one order** to **one order item**. JSON Lines is different: each line is an independent object, so use `lines=True`.
# MAGIC
# MAGIC **Arguments:** `open(encoding="utf-8")` decodes the JSON file; `json_normalize(data, sep=".")` joins nested field names with a dot; `record_path="items"` expands the item list and `meta=["order_id"]` copies the parent key to each item. For `read_json`, `lines=True` parses one JSON object per line and `dtype` preserves the customer ID as text.

# COMMAND ----------

# Parse the JSON document into a Python dictionary.
with (data_dir / "web_orders.json").open(encoding="utf-8") as file:

    # Assign the result of `json.load(file)` to web_payload.
    web_payload = json.load(file)
# Flatten customer fields at order grain; expand items to one row per item.
web_orders = pd.json_normalize(web_payload["orders"], sep=".")

# Set web_items: flatten nested JSON into rows and columns.
web_items = pd.json_normalize(web_payload["orders"], record_path="items", meta=["order_id"])
# lines=True reads each line as an independent JSON record.
events = pd.read_json(data_dir / "events.jsonl", lines=True, dtype={"customer_id": "string"})

# Display Order-level JSON together with the values supplied below.
print("Order-level JSON:\n", web_orders)

# Display Item-level JSON together with the values supplied below.
print("Item-level JSON:\n", web_items)

# Display JSON Lines together with the values supplied below.
print("JSON Lines:\n", events)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Inspect, select, and filter
# MAGIC `shape` is `(rows, columns)`; `head`, `sample`, `info`, and `describe` help profile a new source. `isna` sees actual missing values; it does not treat the empty strings intentionally retained above as missing. For reproducible teaching, a sample uses `random_state`.
# MAGIC
# MAGIC **Arguments:** `describe(include="all")` includes nonnumeric columns; `sample(n=2, random_state=42)` selects two rows reproducibly; `tail(2)` selects the last two rows. A seed helps reproduce a sample but is not a quality guarantee.

# COMMAND ----------

# Inspect dimensions, schema, distributions, and a reproducible sample.
print("Shape:", raw_orders.shape)

# Display Columns together with the values supplied below.
print("Columns:", raw_orders.columns.tolist())

# Call raw_orders.info with the stated inputs.
raw_orders.info()

# Display Text summary together with the values supplied below.
print("Text summary:\n", raw_orders.describe(include="all"))

# Display Reproducible sample together with the values supplied below.
print("Reproducible sample:\n", raw_orders.sample(n=2, random_state=42))
# head/tail inspect the start and end; count reports nonmissing values per column.
print("Last two source rows:\n", raw_orders.tail(2))

# Display Nonmissing values per column together with the values supplied below.
print("Nonmissing values per column:\n", raw_orders.count())
# Blank strings were preserved at ingestion, so count them explicitly.
print("Empty order IDs:", raw_orders["order_id"].eq("").sum())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Select columns and rows
# MAGIC `df["column"]` returns a Series; `df[["column"]]` returns a DataFrame. Use `loc` for label-based row/column selection and `iloc` for positions. Boolean masks must be parenthesized around each condition; use `&`, `|`, and `~` instead of Python `and`, `or`, and `not`.

# COMMAND ----------

# One column in brackets returns a Series; a list of columns returns a DataFrame.
print("Series:\n", raw_orders["product"].head())

# Display Table together with the values supplied below.
print("Table:\n", raw_orders[["order_id", "product"]].head())
# iloc uses zero-based positions and excludes each slice's end.
print("First two positions:\n", raw_orders.iloc[:2, :3])
# Combine two Boolean conditions, then select matching rows and named columns.
mask = (raw_orders["status"] == "completed") & (raw_orders["customer_id"] == "C001")

# Display Completed lines for C001 together with the values supplied below.
print("Completed lines for C001:\n", raw_orders.loc[mask, ["order_id", "line_id", "product"]])

# Display Known customer IDs together with the values supplied below.
print("Known customer IDs:", customers["customer_id"].unique())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Concatenate batches versus join entities
# MAGIC `concat` stacks records from the same schema; it does not look up related records. `merge` joins matching keys horizontally. An outer merge and its indicator expose records present on just one side. A one-to-many or many-to-many join can increase row counts, so always compare counts and validate the expected relationship.
# MAGIC
# MAGIC `isin` is a convenient membership test, while `query` expresses a filter as a string. `value_counts` is a quick distribution check, not a substitute for validating allowed values.
# MAGIC
# MAGIC **Arguments:** `concat([a, b], ignore_index=True)` stacks batches and creates a new integer index. `value_counts(dropna=False)` includes missing values in the distribution. In `merge(right, on="customer_id", how="outer", indicator=True, validate="one_to_one")`, `right` is the lookup, `on` is its shared key, `how` keeps both sides, `indicator` records origin, and `validate` requires unique keys on both sides.

# COMMAND ----------

# Split the example into two batches, then stack them and reset row labels.
batch_a = customers.iloc[:2]

# Set batch_b: select the specified labels or positions from customers.iloc.
batch_b = customers.iloc[2:]

# Set combined_customers: combine the specified pandas objects.
combined_customers = pd.concat([batch_a, batch_b], ignore_index=True)

# Display Stacked customer batches together with the values supplied below.
print("Stacked customer batches:", len(combined_customers))
# Filter using query or membership, and inspect counts including missing values.
print("Northern customers:\n", combined_customers.query("region == 'North'"))

# Display Selected customers together with the values supplied below.
print("Selected customers:\n", customers.loc[customers["customer_id"].isin(["C001", "C003"])])

# Display Raw statuses together with the values supplied below.
print("Raw statuses:\n", raw_orders["status"].value_counts(dropna=False))
# An outer join keeps unmatched rows from both sides; _merge identifies their origin.
join_example = pd.DataFrame({"customer_id": ["C001", "C999"]}).merge(
    customers[["customer_id", "region"]], on="customer_id", how="outer", indicator=True, validate="one_to_one"
)

# Display Outer-join coverage together with the values supplied below.
print("Outer-join coverage:\n", join_example)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Join types: inner, left, right, full outer, and cross
# MAGIC Consider an employee feed and a department lookup. The feed has one unknown department (`D99`); the lookup has one department with no employees (`D30`). An **inner** join retains only matches. A **left** join retains every employee, a **right** join retains every department, and a **full outer** join retains both unmatched sides. `indicator` makes the unmatched rows visible. `validate="many_to_one"` checks that department IDs on the lookup side are unique.
# MAGIC
# MAGIC A **cross join** creates every combination, useful for constructing a small planning grid such as region × month. Its row count is the product of the input sizes: never cross join large datasets without estimating cost. Missing join keys can match in pandas, unlike SQL equality, so reject or handle missing keys explicitly.
# MAGIC
# MAGIC **Options:** `on="department_id"` identifies the common key, `how` selects inner/left/right/outer, `validate="many_to_one"` requires unique department keys, and `indicator=True` adds `_merge`. For `how="cross"` no key is supplied: every left row pairs with every right row.

# COMMAND ----------

# Use the headerless source as the employee fact table; create a tiny department lookup.
departments = pd.DataFrame({
    "department_id": ["D10", "D20", "D30"],
    "department_name": ["Engineering", "Operations", "Finance"],
})

# Evaluate the condition `employees_feed['department_id'].isna().any() or departments['department_id'].isna().any()` before entering this branch.
if employees_feed["department_id"].isna().any() or departments["department_id"].isna().any():

    # Stop with the explicit error shown when this condition is met.
    raise ValueError("Handle missing department keys before joining")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Compare keyed joins
# MAGIC The same `on`, `validate`, and `indicator` arguments apply to each `how` value. The assertions check expected row counts and the `_merge` labels; they are specific to these sample records.

# COMMAND ----------

# Run the four key-based joins with the same keys and inspect their match indicators.
join_results = {}

# Process each join_type from ['inner', 'left', 'right', 'outer'].
for join_type in ["inner", "left", "right", "outer"]:

    # Set joined: join related rows using the declared key and join policy.
    joined = employees_feed.merge(
        departments, on="department_id", how=join_type,
        validate="many_to_one", indicator=True,
    )

    # Set join_results[join_type]: evaluate the expression shown below.
    join_results[join_type] = joined

    # Display the result of f'\n{join_type.upper()} join ({len(joined)} rows):\n' for inspection.
    print(f"\n{join_type.upper()} join ({len(joined)} rows):\n", joined)

# Verify the example's expected unmatched and matched cardinalities.
assert {kind: len(frame) for kind, frame in join_results.items()} == {
    "inner": 2, "left": 3, "right": 3, "outer": 4,
}

# Require `join_results['outer']['_merge'].value_counts().to_dict() == {'both': 2, 'left_only': 1, 'right_only': 1}`; stop if this invariant fails.
assert join_results["outer"]["_merge"].value_counts().to_dict() == {
    "both": 2, "left_only": 1, "right_only": 1,
}

# COMMAND ----------

# MAGIC %md
# MAGIC #### Build a planning grid with a cross join
# MAGIC `how="cross"` forms all combinations without specifying `on`. Here two regions multiplied by three months gives six rows.

# COMMAND ----------

# Cross join two dimensions to generate every region/month planning combination.
planning_regions = pd.DataFrame({"region": ["North", "South"]})

# Set planning_months: construct a two-dimensional DataFrame.
planning_months = pd.DataFrame({"month": ["2025-01", "2025-02", "2025-03"]})

# Set planning_grid: join related rows using the declared key and join policy.
planning_grid = planning_regions.merge(planning_months, how="cross")

# Display Region-month planning grid together with the values supplied below.
print("\nRegion-month planning grid:\n", planning_grid)

# Require `len(planning_grid) == len(planning_regions) * len(planning_months) == 6`; stop if this invariant fails.
assert len(planning_grid) == len(planning_regions) * len(planning_months) == 6

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Clean and type the raw data without hiding problems
# MAGIC Keep a raw copy for audit and make a working copy. A blank string becomes `pd.NA`; trim whitespace and standardize names and statuses. Convert quantities and prices with `to_numeric(errors="coerce")` and dates with `to_datetime(errors="coerce", utc=True)`. **Coercion is not a fix**: it turns unparseable input into missing values, so the next section must report and quarantine them.
# MAGIC
# MAGIC This example uses integer cents for money: binary floating-point prices are not reliable for financial totals. The demo accepts nonnegative prices with at most two decimal places. For larger amounts or more demanding decimal rules, use a decimal type and a defined rounding policy.
# MAGIC
# MAGIC **Arguments:** `insert(0, "source_row", range(...))` places row numbers in column position 0. `to_numeric(..., errors="coerce")` converts invalid text to missing rather than raising; `to_datetime(..., errors="coerce", utc=True)` also produces UTC timestamps. Coerced values must be reported and rejected below.

# COMMAND ----------

# Preserve the raw input and track each record's original CSV line for audit.
work = raw_orders.copy()

# Call work.insert with the stated inputs.
work.insert(0, "source_row", range(2, len(work) + 2))

# Set text_columns: collect the explicitly listed values.
text_columns = ["order_id", "line_id", "customer_id", "order_ts", "product", "quantity", "unit_price", "status"]
# Remove surrounding spaces and convert blank text into pandas missing values.
for column in text_columns:

    # Set work[column]: replace matching values using the given mapping or values.
    work[column] = work[column].str.strip().replace("", pd.NA)
# Standardize capitalization without overwriting the original raw DataFrame.
work["product"] = work["product"].str.title()

# Set work['status']: standardize text to lowercase.
work["status"] = work["status"].str.lower()

# COMMAND ----------

# MAGIC %md
# MAGIC #### Parse numbers and timestamps
# MAGIC `errors="coerce"` converts invalid inputs to missing values for the later quality checks; it does not repair the original values. `utc=True` makes the parsed timestamp UTC-aware.

# COMMAND ----------

# Invalid numbers or dates become missing; subsequent quality rules reject them.
work["quantity_num"] = pd.to_numeric(work["quantity"], errors="coerce")

# Set work['price_num']: parse numeric values, preserving the stated error policy.
work["price_num"] = pd.to_numeric(work["unit_price"], errors="coerce")

# Set work['order_time']: parse timestamps, preserving the stated timezone and error policy.
work["order_time"] = pd.to_datetime(work["order_ts"], errors="coerce", utc=True)

# Display the result of work[['source_row', 'order_id', 'product', 'quantity_num', 'price_num', 'order_time']] for inspection.
print(work[["source_row", "order_id", "product", "quantity_num", "price_num", "order_time"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Missing values, fill, and string tools
# MAGIC Missing means *unknown*, not necessarily zero. `isna`/`notna` find missing values, `fillna` supplies a deliberate default, and `str` methods apply text operations. Only fill when a business rule justifies it: filling a missing price with zero would invent revenue. This isolated example does not alter our order pipeline.

# COMMAND ----------

# Demonstrate normalization and a deliberate fill without changing pipeline data.
example = pd.DataFrame({"email": ["  A@EXAMPLE.COM ", None, "b@example.com"], "discount": [5, None, 0]})

# Set example['email_clean']: standardize text to lowercase.
example["email_clean"] = example["email"].str.strip().str.lower()
# Record which values were missing before applying the example default.
example["discount_was_missing"] = example["discount"].isna()

# Set example['discount_for_demo']: replace missing values with the specified business default.
example["discount_for_demo"] = example["discount"].fillna(0)

# Display the current contents of example for inspection.
print(example)

# Display Missing by column together with the values supplied below.
print("Missing by column:\n", example.isna().sum())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Drop or fill missing values deliberately
# MAGIC `isnull`/`notnull` are aliases of `isna`/`notna`. `count()` counts nonmissing values **per column**, unlike `len(df)`, which counts rows. `dropna()` removes rows missing any column by default; `dropna(subset=[...])` limits the required fields. Dropping every row with an optional exit date would wrongly remove active employees.
# MAGIC
# MAGIC A default can be justified for an optional field, but do not fill unknown identifiers, dates, or salaries with invented business values. This example assigns the result of `fillna` instead of chained `df["column"].fillna(..., inplace=True)`, which does not reliably update the original DataFrame in modern pandas. Methods return a new object by default; `inplace=True` mutates the object it acts on and makes original data harder to audit.
# MAGIC
# MAGIC **Arguments:** `dropna()` removes rows missing any column; `dropna(subset=["employee_id"])` checks only the required key; `fillna(0)` replaces missing values with the specified scalar. The example keeps a missingness flag so that a filled zero remains auditable.

# COMMAND ----------

# Construct a separate HR staging example with required and optional attributes.
employee_quality = pd.DataFrame({
    "employee_id": ["E001", "E002", "E003", None],
    "department": ["Engineering", "Operations", None, "Finance"],
    "exit_date": [None, "2025-01-15", None, None],
    "bonus_cents": [10000, None, 5000, None],
})
# Inspect null and non-null flags; count excludes nulls whereas len counts all rows.
print("Exit-date missing flags:\n", employee_quality["exit_date"].isnull())

# Display Exit-date present flags together with the values supplied below.
print("Exit-date present flags:\n", employee_quality["exit_date"].notnull())

# Display Row count together with the values supplied below.
print("Row count:", len(employee_quality), "| nonmissing counts:\n", employee_quality.count())

# COMMAND ----------

# MAGIC %md
# MAGIC #### Choose required fields before dropping or filling
# MAGIC Compare `dropna()` against `dropna(subset=["employee_id"])`. `copy()` creates a separate working DataFrame; `fillna(0)` applies the explicitly stated bonus assumption.

# COMMAND ----------

# Compare strict removal with removal based only on the required employee ID.
complete_rows = employee_quality.dropna()

# Assign the result of `employee_quality.dropna(subset=['employee_id']).copy()` to keyed_rows.
keyed_rows = employee_quality.dropna(subset=["employee_id"]).copy()

# Display Rows after dropping any null together with the values supplied below.
print("Rows after dropping any null:", len(complete_rows))

# Display Rows with required ID together with the values supplied below.
print("Rows with required ID:", len(keyed_rows))

# Assume a documented demo rule: an absent optional bonus means no bonus.
# Preserve the original value and record the missingness for auditing.
keyed_rows["bonus_was_missing"] = keyed_rows["bonus_cents"].isna()

# Set keyed_rows['bonus_for_reporting']: replace missing values with the specified business default.
keyed_rows["bonus_for_reporting"] = keyed_rows["bonus_cents"].fillna(0)

# Display the current contents of keyed_rows for inspection.
print(keyed_rows)

# Require `len(complete_rows) == 0 and len(keyed_rows) == 3`; stop if this invariant fails.
assert len(complete_rows) == 0 and len(keyed_rows) == 3

# COMMAND ----------

# MAGIC %md
# MAGIC ### Update and filter safely
# MAGIC `loc[row_label, column]` updates a particular cell or all rows matching a condition. For many rows, use a Boolean mask rather than a Python loop that edits or drops rows while iterating. A filter returns the rows retained; it does not delete anything from the raw feed unless you reassign the result.
# MAGIC
# MAGIC The example is a synthetic operational classification, not a judgment about employees. Derive a reporting category from salary and keep the original salary intact.

# COMMAND ----------

# Work on a copy so the raw employee feed remains available for comparison.
employee_report = employees_feed.copy()

# Set employee_report['salary_band']: use the literal value shown.
employee_report["salary_band"] = "standard"
# Assign a label to every matching row in one operation using loc.
employee_report.loc[employee_report["salary"] >= 85000, "salary_band"] = "high"
# Correct one identified example field; the row label is 0 in this DataFrame.
employee_report.loc[0, "employee_name"] = "Mira (verified)"
# Retain standard-band rows in a new DataFrame instead of dropping during a loop.
standard_band = employee_report.loc[employee_report["salary_band"].eq("standard")].copy()

# Display Classified employees together with the values supplied below.
print("Classified employees:\n", employee_report)

# Display Standard-band employees together with the values supplied below.
print("Standard-band employees:\n", standard_band)

# Require `len(standard_band) == 1 and employees_feed.loc[0, 'employee_name'] == 'Mira'`; stop if this invariant fails.
assert len(standard_band) == 1 and employees_feed.loc[0, "employee_name"] == "Mira"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Mapping, regex extraction, and vectorization
# MAGIC `map` translates codes through a lookup; unknown codes become missing and should be investigated. `str.extract` captures structured text into columns; unmatched strings become missing. Prefer built-in vectorized operations to a row-wise `apply` when possible: they are usually clearer and faster. `apply` is still useful for custom logic, as in the small quality-reason demonstration below.

# COMMAND ----------

# Extract the letters and digits from references matching the entire pattern.
feed = pd.DataFrame({"source_ref": ["WEB-001", "APP-002", "bad-ref"], "channel": ["W", "A", "X"]})

# Assign the result of `feed['source_ref'].str.extract('^([A-Z]+)-(\\d+)$')` to feed[['source', 'reference_number']].
feed[["source", "reference_number"]] = feed["source_ref"].str.extract(r"^([A-Z]+)-(\d+)$")
# Map known codes and flag unknown codes, which map to missing values.
feed["channel_name"] = feed["channel"].map({"W": "Web", "A": "App"})

# Set feed['unmapped_channel']: identify missing values.
feed["unmapped_channel"] = feed["channel_name"].isna()

# Display the current contents of feed for inspection.
print(feed)

# Display Investigate unmapped channels together with the values supplied below.
print("Investigate unmapped channels:", int(feed["unmapped_channel"].sum()))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Data quality: explicit rules and quarantine
# MAGIC A quality check answers a business question: **completeness** (keys present), **validity** (positive whole quantity, valid timestamp and price), **uniqueness** (one row per order line), and **referential integrity** (customer exists). Checks are not all interchangeable.
# MAGIC
# MAGIC We first remove **exact duplicate business rows**. This demo keeps the first file occurrence; in production preserve the duplicate in an audit stream and choose a deterministic rule based on trustworthy ingestion metadata. Conflicting records with the same business key are **not** silently removed: all of them will be quarantined below. A source row number points back to the CSV line, including its header.
# MAGIC
# MAGIC **Options:** `duplicated(subset=business_columns, keep="first")` compares just those columns and flags later occurrences. `keep=False`, used below for conflicting keys, flags every occurrence.

# COMMAND ----------

# Compare business fields only, excluding source_row so identical input lines match.
business_columns = text_columns

# Set exact_duplicate: identify duplicate rows according to the specified keys.
exact_duplicate = work.duplicated(subset=business_columns, keep="first")
# Separate later copies for audit and keep the first occurrence for validation.
duplicate_rows = work.loc[exact_duplicate].copy()

# Assign the result of `work.loc[~exact_duplicate].copy()` to deduped.
deduped = work.loc[~exact_duplicate].copy()

# Display Input rows together with the values supplied below.
print("Input rows:", len(work), "| exact duplicates removed:", len(duplicate_rows))

# Display Duplicate source rows together with the values supplied below.
print("Duplicate source rows:\n", duplicate_rows[["source_row", "order_id", "line_id"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Build a reason per violated rule
# MAGIC Rules are evaluated for each surviving row. Missing or invalid values fail rather than passing by accident. A line ID is a nonempty string in this example. We check cents using the original text so that `12.345` cannot silently round to `12.35`. The conflict check excludes incomplete keys: missing keys are already invalid. All conflicting rows are rejected rather than arbitrarily selecting a winner.
# MAGIC
# MAGIC **Options:** `duplicated(subset=[...], keep=False)` marks all rows sharing a complete key. `str.fullmatch(pattern, na=False)` returns false for missing prices. `DataFrame(..., index=deduped.index)` aligns rule flags to source rows. `apply(..., axis=1)` builds reasons **per row**, not per column; `fillna(True)` makes unresolved rule results failures.

# COMMAND ----------

# Complete keys can be checked for conflicts; keep=False flags every occurrence.
has_key = deduped["order_id"].notna() & deduped["line_id"].notna()

# Set conflicting_key: combine the stated values or conditions using the shown operator.
conflicting_key = has_key & deduped.duplicated(subset=["order_id", "line_id"], keep=False)

# Set quantity: select the specified labels or positions from deduped.
quantity = deduped["quantity_num"]

# Set price: select the specified labels or positions from deduped.
price = deduped["price_num"]

# COMMAND ----------

# MAGIC %md
# MAGIC #### Evaluate rule flags and collect reasons
# MAGIC `DataFrame(..., index=deduped.index)` aligns the Boolean rules to source rows. `fullmatch(..., na=False)` rejects missing prices, and `apply(..., axis=1)` creates a reason string for each row.

# COMMAND ----------

# Each Boolean column is True when its rule fails for that source row.
rules = pd.DataFrame({
    "missing_order_key": ~has_key,
    "missing_customer": deduped["customer_id"].isna(),
    "missing_product": deduped["product"].isna(),
    "invalid_timestamp": deduped["order_time"].isna(),
    # Quantity must be present, positive, and a whole number.
    "invalid_quantity": quantity.isna() | (quantity <= 0) | (quantity % 1 != 0),
    # Check the original text to reject negative prices and more than two decimals.
    "invalid_price": price.isna() | (price < 0) | ~deduped["unit_price"].str.fullmatch(r"\d+(?:\.\d{1,2})?", na=False),
    "invalid_status": ~deduped["status"].isin(["completed", "cancelled"]),
    "conflicting_order_line": conflicting_key,
}, index=deduped.index).fillna(True).astype(bool)
# Combine all failed rule names into a readable reason for each rejected row.
deduped["quality_reasons"] = rules.apply(lambda row: ", ".join(row.index[row]), axis=1)

# Display Failures by rule (a row can fail multiple rules) together with the values supplied below.
print("Failures by rule (a row can fail multiple rules):\n", rules.sum())

# Display the result of deduped.loc[deduped['quality_reasons'].ne(''), ['source_row', 'order_id', 'quality_reasons']] for inspection.
print(deduped.loc[deduped["quality_reasons"].ne(""), ["source_row", "order_id", "quality_reasons"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Referential integrity and safe joins
# MAGIC Joining is like a spreadsheet lookup, but duplicate keys on the lookup side can multiply rows. `validate="many_to_one"` makes that assumption explicit and fails if the customer dimension is not unique. `indicator=True` labels matches. This check is run only after missing customer IDs are rejected: pandas can match null join keys to null keys, unlike ordinary SQL equality.
# MAGIC
# MAGIC Unknown customer IDs are quarantined. No inner join is used to silently drop them. For a real pipeline, the team must decide whether to reject, retry when the dimension arrives, or assign a clearly documented unknown-member key.
# MAGIC
# MAGIC **Options:** `on="customer_id"` is the join key; `how="left"` retains eligible orders; `validate="many_to_one"` checks the customer lookup is unique; `indicator=True` distinguishes matched and left-only rows. `drop(columns="_merge")` removes the helper column, and `concat(..., ignore_index=True)` stacks both reject sets with fresh labels.

# COMMAND ----------

# Split invalid records from records eligible for the customer lookup.
rejected_rules = deduped.loc[deduped["quality_reasons"].ne("")].copy()

# Assign the result of `deduped.loc[deduped['quality_reasons'].eq('')].copy()` to rule_passed.
rule_passed = deduped.loc[deduped["quality_reasons"].eq("")].copy()

# Evaluate the condition `customers['customer_id'].isna().any() or customers['customer_id'].eq('').any()` before entering this branch.
if customers["customer_id"].isna().any() or customers["customer_id"].eq("").any():

    # Stop with the explicit error shown when this condition is met.
    raise ValueError("Customer dimension contains an empty customer_id")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Look up customers and split matched from unmatched
# MAGIC `how="left"` preserves eligible order lines; `validate="many_to_one"` rejects duplicate customer keys; `indicator=True` supplies match labels. `concat(..., ignore_index=True)` combines both reject streams.

# COMMAND ----------

# Protect against duplicate dimension keys and keep unmatched facts visible.
enriched = rule_passed.merge(customers[["customer_id", "customer_name", "region"]],
                             on="customer_id", how="left", validate="many_to_one", indicator=True)
# Quarantine unknown customers; retain matched rows as accepted facts.
unknown_customers = enriched.loc[enriched["_merge"].eq("left_only")].copy()

# Set unknown_customers['quality_reasons']: use the literal value shown.
unknown_customers["quality_reasons"] = "unknown_customer"

# Assign the result of `enriched.loc[enriched['_merge'].eq('both')].drop(columns='_merge').copy()` to accepted.
accepted = enriched.loc[enriched["_merge"].eq("both")].drop(columns="_merge").copy()
# Combine field-rule rejects and lookup rejects for a single audit view.
rejects = pd.concat([rejected_rules, unknown_customers.drop(columns="_merge")], ignore_index=True)

# Display Unknown customers together with the values supplied below.
print("Unknown customers:\n", unknown_customers[["source_row", "customer_id", "quality_reasons"]])

# Display Rejected rows together with the values supplied below.
print("Rejected rows:\n", rejects[["source_row", "order_id", "quality_reasons"]].sort_values("source_row"))

# Display Accepted rows together with the values supplied below.
print("Accepted rows:", len(accepted))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Reconcile the accounting
# MAGIC Every original row must end in exactly one category: removed exact duplicate, rejected, or accepted. An assertion makes a failed assumption visible instead of printing a success-shaped result. Rule-failure counts cannot be added to reconcile rows because one row can fail more than one rule.

# COMMAND ----------

# Check no source rows vanished or were counted twice, then verify key integrity.
print({"input": len(work), "exact_duplicates": len(duplicate_rows), "rejected": len(rejects), "accepted": len(accepted)})

# Require `len(work) == len(duplicate_rows) + len(rejects) + len(accepted)`; stop if this invariant fails.
assert len(work) == len(duplicate_rows) + len(rejects) + len(accepted), "Row reconciliation failed"

# Require `not accepted.duplicated(['order_id', 'line_id']).any()`; stop if this invariant fails.
assert not accepted.duplicated(["order_id", "line_id"]).any(), "Accepted business key is not unique"

# Require `accepted['customer_id'].notna().all()`; stop if this invariant fails.
assert accepted["customer_id"].notna().all()
# This final assertion is specific to the supplied fixture, not a generic rule.
assert len(work) == 10 and len(duplicate_rows) == 1 and len(rejects) == 5 and len(accepted) == 4

# Display Reconciliation and expected fixture counts passed. together with the values supplied below.
print("Reconciliation and expected fixture counts passed.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Transform, derive, and classify
# MAGIC Transform the accepted rows into analysis-ready types. Exact cents are derived from the validated price string; `partition` separates dollars and cents without a floating-point rounding decision. `assign` creates columns and `loc` applies business rules to matching rows. Status is retained: cancelled lines are accepted as valid records, but they must not be counted as completed revenue.
# MAGIC
# MAGIC **Arguments:** `astype("int64")` converts validated quantities and cents to integers. `assign(line_amount_cents=..., order_date=..., order_month=...)` creates named columns; each lambda receives the DataFrame. `strftime("%Y-%m")` formats year and month, and `.loc[condition, "line_size"]` updates only matching rows.

# COMMAND ----------

# Convert a validated decimal string to exact integer cents without float rounding.
def price_to_cents(value):

    # Assign the result of `value.partition('.')` to (dollars, _, cents).
    dollars, _, cents = value.partition(".")
    # Pad the fractional part so "25", "25.5", and "25.50" work consistently.
    return int(dollars) * 100 + int((cents + "00")[:2])

# COMMAND ----------

# MAGIC %md
# MAGIC #### Derive amounts, dates, and categories
# MAGIC `map(price_to_cents)` applies the converter to each validated price; `astype("int64")` specifies integer storage. Each named `assign` argument creates a new column. `loc` uses conditions to set the categories, applying the higher threshold last.

# COMMAND ----------

# Convert cleaned values to analytical types and derive amount and date columns.
accepted["quantity"] = accepted["quantity_num"].astype("int64")

# Set accepted['unit_price_cents']: convert values to the specified dtype.
accepted["unit_price_cents"] = accepted["unit_price"].map(price_to_cents).astype("int64")

# Set accepted: derive the named output columns.
accepted = accepted.assign(
    line_amount_cents=lambda df: df["quantity"] * df["unit_price_cents"],
    order_date=lambda df: df["order_time"].dt.date,
    order_month=lambda df: df["order_time"].dt.strftime("%Y-%m"),
)
# Start with small, then overwrite matching rows from lower to higher thresholds.
# Large lines also meet the medium condition, so applying large last is essential.
accepted["line_size"] = "small"

# Set accepted.loc[accepted['line_amount_cents'] >= 10000,...: use the literal value shown.
accepted.loc[accepted["line_amount_cents"] >= 10000, "line_size"] = "medium"

# Set accepted.loc[accepted['line_amount_cents'] >= 50000,...: use the literal value shown.
accepted.loc[accepted["line_amount_cents"] >= 50000, "line_size"] = "large"

# Display the result of accepted[['order_id', 'line_id', 'product', 'quantity', 'line_amount_cents', 'status', 'line_size']] for inspection.
print(accepted[["order_id", "line_id", "product", "quantity", "line_amount_cents", "status", "line_size"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Sorting, renaming, replacing, and indexing
# MAGIC `sort_values` orders the display or determines the winner before a deliberate deduplication. `rename` clarifies a contract, `replace` maps known codes, and `set_index` creates an index for label-based lookups. Indexes are not necessarily unique; verify uniqueness if the use case requires it. This example operates on a copy.
# MAGIC
# MAGIC **Arguments:** `rename(columns={"order_id": "order_number"})` maps an old column name to a new one; `replace({...})` maps status values; `sort_values([...])` uses the listed sort keys; `set_index([...])` creates a multi-level row index.

# COMMAND ----------

# Create a separate presentation view without changing the accepted fact table.
view = accepted.rename(columns={"order_id": "order_number"}).copy()

# Set view['status_label']: replace matching values using the given mapping or values.
view["status_label"] = view["status"].replace({"completed": "Completed", "cancelled": "Cancelled"})
# Sort for readable output and use the order-line pair as a two-level index.
view = view.sort_values(["order_number", "line_id"]).set_index(["order_number", "line_id"])

# Display the result of view[['product', 'status_label', 'line_amount_cents']] for inspection.
print(view[["product", "status_label", "line_amount_cents"]])

# Display Index unique together with the values supplied below.
print("Index unique:", view.index.is_unique)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Explicit duplicate removal, multi-column sort, and casting
# MAGIC `duplicated` flags repeated rows; `drop_duplicates` returns a new DataFrame by default. Choose a subset and winner only when the business has defined a safe deduplication policy. This demo removes only identical rows; the order pipeline above separately rejects conflicting business keys.
# MAGIC
# MAGIC `sort_values` accepts one direction per column and `na_position` for missing sort keys. `astype("string")` produces pandas' nullable string dtype, preserving missing values; it does not prove a value is a valid business identifier.
# MAGIC
# MAGIC **Options:** `ignore_index=True` resets labels when stacking; `ascending=[True, False]` sorts the first key ascending and the second descending; `na_position="first"` puts missing sort keys first. `drop_duplicates()` uses all columns and keeps the first exact row by default.

# COMMAND ----------

# Set employee_copies: combine the specified pandas objects.
employee_copies = pd.concat([employees_feed, employees_feed.iloc[[0]]], ignore_index=True)
# Show the duplicate flag before removing later exact copies of entire rows.
print("Duplicate flags:\n", employee_copies.duplicated())

# Assign the result of `employee_copies.drop_duplicates().copy()` to unique_employees.
unique_employees = employee_copies.drop_duplicates().copy()
# Demonstrate different sort directions and explicitly place missing salaries first.
employee_order = unique_employees.sort_values(
    ["department_id", "salary"], ascending=[True, False], na_position="first"
)
# Cast a copy of the numeric salary for text-oriented export or comparison.
employee_order["salary_text"] = employee_order["salary"].astype("string")

# Display Sorted, deduplicated employees together with the values supplied below.
print("Sorted, deduplicated employees:\n", employee_order)

# Display String dtype together with the values supplied below.
print("String dtype:", employee_order["salary_text"].dtype)

# Require `len(employee_copies) == 4 and len(employee_order) == 3`; stop if this invariant fails.
assert len(employee_copies) == 4 and len(employee_order) == 3

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Aggregate with the right grain
# MAGIC Revenue is counted for **completed** lines only. `groupby(...).agg(...)` produces a smaller table at a new grain: one row per region and month. `sum` counts line amounts; `nunique` counts distinct orders so an order with two lines is counted once. `transform` returns a value aligned to every original row, useful for each line's share of its region's revenue.
# MAGIC
# MAGIC The examples use cents for accurate arithmetic. An order spanning multiple regions could be counted once **in each region**, so summing regional distinct-order counts would not necessarily give global distinct orders.
# MAGIC
# MAGIC **Options:** `groupby(["region", "order_month"], as_index=False, dropna=False)` makes the keys regular output columns and retains missing-key groups. `agg(revenue_cents=("line_amount_cents", "sum"), ...)` names each output and identifies its input column and aggregation. `size` counts rows; `nunique` counts distinct nonmissing order IDs; `transform("sum")` broadcasts each group total back to its original rows.

# COMMAND ----------

# Cancelled lines are valid records but do not contribute to completed revenue.
completed = accepted.loc[accepted["status"].eq("completed")].copy()
# Collapse lines into region/month groups and name each output metric.
region_month = (completed.groupby(["region", "order_month"], as_index=False, dropna=False)
                .agg(revenue_cents=("line_amount_cents", "sum"),
                     order_count=("order_id", "nunique"),
                     line_count=("line_id", "size"),
                     units=("quantity", "sum")))
# transform repeats the regional total on each line so a line share can be computed.
completed["region_total_cents"] = completed.groupby("region")["line_amount_cents"].transform("sum")

# Set completed['region_share']: combine the stated values or conditions using the shown operator.
completed["region_share"] = completed["line_amount_cents"] / completed["region_total_cents"]

# Display Region/month metrics together with the values supplied below.
print("Region/month metrics:\n", region_month)

# Display Line share together with the values supplied below.
print("Line share:\n", completed[["order_id", "line_id", "region", "region_share"]])
# Confirm the expected revenue and distinct-order count for this fixture.
assert completed["line_amount_cents"].sum() == 145000

# Require `completed['order_id'].nunique() == 2`; stop if this invariant fails.
assert completed["order_id"].nunique() == 2

# COMMAND ----------

# MAGIC %md
# MAGIC ### Pivot, crosstab, and reshape
# MAGIC A pivot turns long-form categories into columns; the result is convenient for reports but can be sparse or very wide. `pivot_table` aggregates repeated combinations; `pivot` expects unique combinations and raises on duplicates. `melt` converts wide tables back to long form. `crosstab` counts combinations.
# MAGIC
# MAGIC **Options:** `pivot_table(index="region", columns="product", values="line_amount_cents", aggfunc="sum", fill_value=0)` chooses row labels, column labels, measures, aggregation and a display fill. `melt(id_vars="region", var_name="product", value_name="revenue_cents")` keeps the region and names the new category and value columns. Filled zeroes reflect this particular report's assumption.

# COMMAND ----------

# Sum amounts for each region/product combination and display products as columns.
pivoted = pd.pivot_table(completed, index="region", columns="product", values="line_amount_cents",
                         aggfunc="sum", fill_value=0)
# Move product columns back into rows; crosstab separately counts line records.
long_again = pivoted.reset_index().melt(id_vars="region", var_name="product", value_name="revenue_cents")

# Display Pivot together with the values supplied below.
print("Pivot:\n", pivoted)

# Display Back to long together with the values supplied below.
print("Back to long:\n", long_again)

# Display Product counts by region together with the values supplied below.
print("Product counts by region:\n", pd.crosstab(completed["region"], completed["product"]))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Distribution and ranking
# MAGIC `quantile` describes a distribution and can help investigate outliers; an unusual value is not automatically wrong. `rank` gives an ordering within a group. Specify the tie policy rather than assuming a unique rank. These are **line** amounts, not order totals.
# MAGIC
# MAGIC **Arguments:** `rank(method="dense", ascending=False)` ranks largest values first, shares ranks for ties, and leaves no rank gaps. `quantile([0.25, 0.5, 0.75])` requests the 25th, 50th, and 75th percentiles.

# COMMAND ----------

# Dense ranking gives equal amounts the same rank without gaps between ranks.
ranked = completed.copy()

# Assign the result of `ranked.groupby('region')['line_amount_cents'].rank(method='dense', ascending=False)` to ranked['amount_rank_in_region'].
ranked["amount_rank_in_region"] = ranked.groupby("region")["line_amount_cents"].rank(method="dense", ascending=False)

# Display Line-amount percentiles (cents) together with the values supplied below.
print("Line-amount percentiles (cents):\n", completed["line_amount_cents"].quantile([0.25, 0.5, 0.75]))

# Display Ranked lines together with the values supplied below.
print("Ranked lines:\n", ranked[["order_id", "line_id", "line_amount_cents", "amount_rank_in_region"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Descriptive statistics and grouped summaries
# MAGIC Mean is the arithmetic average; median is the middle value; mode returns the most frequent value(s), so it is a Series and ties are possible. Sum totals values, while `min`, `max`, and `count` describe a group. These functions typically skip missing values; `count` is not the same as the number of rows when values are missing. For money, use integer cents or an appropriate decimal type and apply a defined rounding policy.
# MAGIC
# MAGIC This example groups a synthetic employee feed by department. In real HR data, use access controls and avoid publishing small groups or sensitive salary information without approval.
# MAGIC
# MAGIC **Options:** `groupby("department_id", as_index=False)` retains the department as a column. Each named `agg` argument, such as `minimum_salary=("salary", "min")`, specifies an output name, source column, and operation; `count` excludes missing values.

# COMMAND ----------

# Summarize the numeric salary column and show all modes, including ties.
salary = employees_feed["salary"]

# Display Salary mean together with the values supplied below.
print("Salary mean:", salary.mean(), "| median:", salary.median(), "| sum:", salary.sum())

# Display Department mode(s) together with the values supplied below.
print("Department mode(s):\n", employees_feed["department_id"].mode())
# Named aggregations state which input column and statistic produces each result.
department_summary = employees_feed.groupby("department_id", as_index=False).agg(
    minimum_salary=("salary", "min"),
    maximum_salary=("salary", "max"),
    total_salary=("salary", "sum"),
    known_salary_count=("salary", "count"),
    employee_count=("employee_id", "count"),
)

# Display Department summaries together with the values supplied below.
print("Department summaries:\n", department_summary)

# Require `salary.sum() == 245000 and salary.median() == 85000`; stop if this invariant fails.
assert salary.sum() == 245000 and salary.median() == 85000

# COMMAND ----------

# MAGIC %md
# MAGIC ### Join metrics to targets
# MAGIC Here the target is **monthly** at region grain, so aggregate one chosen month before joining; otherwise a region-only join would repeat the monthly target for every month. `validate="one_to_one"` protects the intended grain. Missing targets are not silently replaced by zero.
# MAGIC
# MAGIC **Options:** `merge(targets, on="region", how="left", validate="one_to_one", indicator=True)` preserves January regions, checks uniqueness on both sides, and identifies missing targets before calculating a ratio.

# COMMAND ----------

# Restrict to one month so each region matches one monthly target.
january = region_month.loc[region_month["order_month"].eq("2025-01")].copy()

# Set target_check: join related rows using the declared key and join policy.
target_check = january.merge(targets, on="region", how="left", validate="one_to_one", indicator=True)
# Stop rather than reporting misleading attainment for missing targets.
if not target_check["_merge"].eq("both").all():

    # Stop with the explicit error shown when this condition is met.
    raise ValueError("A region has no January target; investigate before reporting attainment")
# Compare actual and target in the same monetary units.
target_check["target_cents"] = target_check["monthly_target"] * 100

# Set target_check['attainment']: combine the stated values or conditions using the shown operator.
target_check["attainment"] = target_check["revenue_cents"] / target_check["target_cents"]

# Display the result of target_check[['region', 'order_month', 'revenue_cents', 'target_cents', 'attainment']] for inspection.
print(target_check[["region", "order_month", "revenue_cents", "target_cents", "attainment"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Window-style operations and time
# MAGIC A SQL window computes a value for each row without collapsing the rows. In pandas, sort deterministically and use `groupby` with `cumcount`, `cumsum`, or `shift`. Here the grouping is **per customer**, and timestamps plus keys break ties. `shift` finds the previous completed line, not necessarily the previous order.
# MAGIC
# MAGIC Timestamps were parsed as UTC earlier, which avoids ambiguous local daylight-saving times. Convert a UTC timestamp to a business timezone before deriving a local reporting date; never assume a naive timestamp is UTC without an upstream contract.
# MAGIC
# MAGIC **Options:** `sort_values([...])` supplies a deterministic order; `groupby("customer_id", sort=False)` groups customers without sorting group keys. `shift()` defaults to one preceding row within each group. `tz_convert("Asia/Kolkata")` changes the displayed timezone, not the underlying instant.

# COMMAND ----------

# Establish deterministic ordering before customer-level window calculations.
sequence = completed.sort_values(["customer_id", "order_time", "order_id", "line_id"]).copy()

# Set by_customer: group records according to the supplied business keys.
by_customer = sequence.groupby("customer_id", sort=False)
# cumcount starts at zero; add one for a human-friendly line number.
sequence["line_number_for_customer"] = by_customer.cumcount() + 1

# Set sequence['running_spend_cents']: calculate a cumulative total in the existing row order.
sequence["running_spend_cents"] = by_customer["line_amount_cents"].cumsum()
# shift retrieves the previous line within each customer, leaving the first missing.
sequence["previous_line_time"] = by_customer["order_time"].shift()

# Set sequence['hours_since_previous_line']: combine the stated values or conditions using the shown operator.
sequence["hours_since_previous_line"] = (sequence["order_time"] - sequence["previous_line_time"]).dt.total_seconds() / 3600
# Convert the same instant from UTC to a business timezone.
sequence["india_time"] = sequence["order_time"].dt.tz_convert("Asia/Kolkata")

# Display the result of sequence[['customer_id', 'order_id', 'line_number_for_customer', 'running_spend_cents', 'previous_line_time', 'hours_since_previous_line', 'india_time']] for inspection.
print(sequence[["customer_id", "order_id", "line_number_for_customer", "running_spend_cents",
                "previous_line_time", "hours_since_previous_line", "india_time"]])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Daily time series and rolling averages
# MAGIC Here we sum completed revenue per UTC calendar day, then explicitly insert zero for days with **no completed lines**. `rolling(3)` is three rows/days after daily reindexing; `min_periods=1` allows a value before three days are available. Zero is appropriate only if the input is known to be complete for that day; a missing file is not proof of zero sales.
# MAGIC
# MAGIC **Arguments:** `set_index("order_time")` provides the datetime index; `resample("D")` creates daily bins; `to_frame("revenue_cents")` names the Series as a DataFrame column. `rolling(3, min_periods=1)` requests a three-row window with at least one observation.

# COMMAND ----------

# Resample sums into UTC days, including zero-valued days between observations.
daily = completed.set_index("order_time")["line_amount_cents"].resample("D").sum()

# Assign the result of `daily.to_frame('revenue_cents')` to daily_frame.
daily_frame = daily.to_frame("revenue_cents")
# Average up to the current day and the preceding two days.
daily_frame["rolling_3_day_mean_cents"] = daily_frame["revenue_cents"].rolling(3, min_periods=1).mean()

# Display the current contents of daily_frame for inspection.
print(daily_frame)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Advanced joins: SCD type 2 and point-in-time correctness
# MAGIC A customer dimension may change over time. A type-2 dimension keeps versions with `[valid_from, valid_to)` intervals: start inclusive, end exclusive, `NaT` meaning still current. Matching an old order to today's region would rewrite history. We create all candidate matches for the small demo, then keep the interval containing the order time.
# MAGIC
# MAGIC The check below asserts exactly one historical match for **every** accepted line. Missing or overlapping intervals fail loudly. The many-to-many candidate merge can be expensive; use distributed range joins for large histories.
# MAGIC
# MAGIC **Options:** `to_datetime(..., utc=True)` parses boundaries in UTC. `merge(..., on="customer_id", how="left", validate="many_to_many")` permits repeated customer IDs on both sides; it does not prove interval correctness. `reindex(accepted["source_row"], fill_value=0)` includes source rows with no match so the subsequent check catches them.

# COMMAND ----------

# Model historical customer-region versions with inclusive start and exclusive end.
history = pd.DataFrame([
    {"customer_id": "C001", "historical_region": "West", "valid_from": "2024-01-01", "valid_to": "2025-01-05"},
    {"customer_id": "C001", "historical_region": "North", "valid_from": "2025-01-05", "valid_to": None},
    {"customer_id": "C002", "historical_region": "South", "valid_from": "2024-01-01", "valid_to": None},
    {"customer_id": "C003", "historical_region": "North", "valid_from": "2024-01-01", "valid_to": None},
])
# Parse boundaries in UTC to compare them with the UTC order timestamp.
history["valid_from"] = pd.to_datetime(history["valid_from"], utc=True)

# Set history['valid_to']: parse timestamps, preserving the stated timezone and error policy.
history["valid_to"] = pd.to_datetime(history["valid_to"], utc=True)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Match facts to the valid historical interval
# MAGIC `on`, `how`, and `validate` define the candidate join. The Boolean interval test applies an inclusive start and exclusive end. `reindex(..., fill_value=0)` ensures missing matches remain visible in the count.

# COMMAND ----------

# Generate customer-version candidates, then retain only the interval containing the order.
candidates = accepted.merge(history, on="customer_id", how="left", validate="many_to_many")

# Set valid_interval: combine the stated values or conditions using the shown operator.
valid_interval = (candidates["order_time"].ge(candidates["valid_from"]) &
                  (candidates["valid_to"].isna() | candidates["order_time"].lt(candidates["valid_to"])))

# Assign the result of `candidates.loc[valid_interval].copy()` to historical.
historical = candidates.loc[valid_interval].copy()
# Reindex against all accepted lines so even zero-match lines are checked.
match_counts = historical.groupby("source_row").size().reindex(accepted["source_row"], fill_value=0)

# Run this branch only when not match_counts.eq(1).all() is true.
if not match_counts.eq(1).all():

    # Stop with the explicit error shown when this condition is met.
    raise ValueError(f"SCD match must be exactly one per line; bad counts: {match_counts[match_counts.ne(1)].to_dict()}")

# Display the result of historical[['order_id', 'line_id', 'order_time', 'region', 'historical_region']] for inspection.
print(historical[["order_id", "line_id", "order_time", "region", "historical_region"]])

# Display C001's January 2 lines correctly use West, not today's North. together with the values supplied below.
print("C001's January 2 lines correctly use West, not today's North.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Nearest prior match with `merge_asof`
# MAGIC A sensor reading can be matched to the most recent calibration **at or before** its event time. Sort both inputs by their time keys globally, set a tolerance, and inspect unmatched results. `merge_asof` is not a substitute for validating SCD intervals: it finds a prior start but does not check an end boundary.
# MAGIC
# MAGIC **Arguments:** `merge_asof(readings, calibrations, left_on="event_time", right_on="calibration_time", by="sensor_id", direction="backward", tolerance=pd.Timedelta("3h"))` specifies the two inputs, their time keys, equality grouping key, search direction, and maximum allowed time difference. A reading outside the three-hour limit remains unmatched.

# COMMAND ----------

# Sort both inputs by time, as required by merge_asof.
readings = pd.DataFrame({"sensor_id": ["S1", "S1", "S2"],
                         "event_time": pd.to_datetime(["2025-01-02T10:00Z", "2025-01-02T12:00Z", "2025-01-02T12:00Z"], utc=True),
                         "reading": [20.0, 22.0, 18.0]}).sort_values("event_time")

# Set calibrations: order records by the specified sort keys.
calibrations = pd.DataFrame({"sensor_id": ["S1", "S2"],
                             "calibration_time": pd.to_datetime(["2025-01-02T09:00Z", "2025-01-02T08:00Z"], utc=True),
                             "offset": [0.5, -0.5]}).sort_values("calibration_time")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Match readings to a recent calibration
# MAGIC `left_on` and `right_on` select the time keys, `by` restricts matching to the same sensor, `direction="backward"` disallows future calibrations, and `tolerance` sets a three-hour limit.

# COMMAND ----------

# Match the latest calibration for the same sensor within the previous three hours.
matched = pd.merge_asof(readings, calibrations, left_on="event_time", right_on="calibration_time",
                        by="sensor_id", direction="backward", tolerance=pd.Timedelta("3h"))
# Missing matches keep a missing adjusted reading rather than inventing an offset.
matched["adjusted_reading"] = matched["reading"] + matched["offset"]

# Display the current contents of matched for inspection.
print(matched)

# Display Unmatched readings requiring investigation together with the values supplied below.
print("Unmatched readings requiring investigation:", matched["calibration_time"].isna().sum())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12. Semi-structured data and `explode`
# MAGIC A single event may contain several tags. `explode` makes one row per tag and repeats the event ID. This is a grain change: counting exploded rows as events will inflate event counts. `json_normalize` handles objects; `explode` is useful when list-valued columns have already been loaded.
# MAGIC
# MAGIC **Arguments:** `explode("tags", ignore_index=True)` expands the chosen list-valued column and generates fresh row labels. `nunique()` counts distinct nonmissing event IDs.

# COMMAND ----------

# Expand each tag list to event-tag rows; the event ID is repeated as needed.
tagged_events = pd.DataFrame({"event_id": ["E1", "E2"], "tags": [["mobile", "sale"], ["web"]]})

# Set event_tags: expand list values into separate rows.
event_tags = tagged_events.explode("tags", ignore_index=True)

# Display the current contents of event_tags for inspection.
print(event_tags)

# Display Events together with the values supplied below.
print("Events:", event_tags["event_id"].nunique(), "| event-tag rows:", len(event_tags))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 13. Incremental ingestion, late arrivals, and idempotence
# MAGIC A watermark is a progress marker, not a guarantee that every earlier event has arrived. A robust production design needs a source-defined ordering, overlap or change-data-capture strategy, persistent checkpoints, and an atomic upsert keyed by a stable event ID. Event time alone is usually unsafe as an ingestion watermark.
# MAGIC
# MAGIC This bounded example uses a **source ingestion sequence**, not event time. We deliberately replay one known event and include a late-arriving older event. Identical event-ID replays are removed; conflicting payloads for the same ID raise an error. Persisting the resulting state and checkpoint atomically is outside this in-memory demonstration.
# MAGIC
# MAGIC **Options:** `concat(..., ignore_index=True)` resets labels after stacking. `nunique(dropna=False)` treats missing as a distinct value during conflict checking. `any(axis=None)` asks whether any cell in the Boolean table is true. `drop_duplicates("event_id", keep="first")` keeps the earliest sorted identical replay after conflict validation.

# COMMAND ----------

# Existing state represents events processed before the saved checkpoint.
existing = pd.DataFrame([
    {"event_id": "E1", "event_time": "2025-01-02T10:00:00Z", "amount_cents": 1000, "ingest_seq": 1},
    {"event_id": "E2", "event_time": "2025-01-03T10:00:00Z", "amount_cents": 2000, "ingest_seq": 2},
])
# E2 is an identical replay; E3 arrives late based on its event time.
incoming = pd.DataFrame([
    {"event_id": "E2", "event_time": "2025-01-03T10:00:00Z", "amount_cents": 2000, "ingest_seq": 3},
    {"event_id": "E3", "event_time": "2025-01-01T10:00:00Z", "amount_cents": 500, "ingest_seq": 4},
])

# COMMAND ----------

# MAGIC %md
# MAGIC #### Process the incremental batch
# MAGIC `ignore_index=True` resets labels during concatenation; `nunique(dropna=False)` includes missing payload values; `any(axis=None)` checks the whole table; `drop_duplicates(..., keep="first")` retains the earliest identical event after validation.

# COMMAND ----------

# Read records after the ingestion-sequence checkpoint, not after an event-time cutoff.
checkpoint = 2

# Assign the result of `incoming.loc[incoming['ingest_seq'].gt(checkpoint)].copy()` to new_batch.
new_batch = incoming.loc[incoming["ingest_seq"].gt(checkpoint)].copy()

# Set combined: combine the specified pandas objects.
combined = pd.concat([existing, new_batch], ignore_index=True)
# Multiple payload values for one ID indicate a conflict, not a safe replay.
payload_versions = combined.groupby("event_id")[["event_time", "amount_cents"]].nunique(dropna=False)

# Run this branch only when payload_versions.gt(1).any(axis=None) is true.
if payload_versions.gt(1).any(axis=None):

    # Stop with the explicit error shown when this condition is met.
    raise ValueError("Conflicting event payloads require investigation")
# Keep the earliest identical event and propose a new in-memory checkpoint.
state = combined.sort_values("ingest_seq").drop_duplicates("event_id", keep="first")

# Set next_checkpoint: evaluate the expression shown below.
next_checkpoint = int(new_batch["ingest_seq"].max()) if not new_batch.empty else checkpoint

# Display Resulting event state together with the values supplied below.
print("Resulting event state:\n", state)

# Display Proposed checkpoint together with the values supplied below.
print("Proposed checkpoint:", next_checkpoint, "| late event E3 retained:", "E3" in state["event_id"].values)

# Require `len(state) == 3 and next_checkpoint == 4`; stop if this invariant fails.
assert len(state) == 3 and next_checkpoint == 4

# COMMAND ----------

# MAGIC %md
# MAGIC ## 14. Scale, chunking, and execution boundaries
# MAGIC Pandas processes in a single Python process, normally on the **driver** in Databricks. It is excellent for modest data, debugging, and local transformations, but loading distributed data with `toPandas()` collects it on the driver. Inspect memory (`memory_usage(deep=True)`), read only required columns, choose appropriate dtypes, and use chunks where aggregation is decomposable.
# MAGIC
# MAGIC This chunked example counts **raw source rows** per status, including bad and duplicate rows. Chunk-local deduplication alone is not globally correct when duplicates cross chunk boundaries. `category` can save memory for low-cardinality strings; always measure, as high-cardinality data may not benefit.
# MAGIC
# MAGIC **Options:** `memory_usage(index=True, deep=True)` includes index and deeper object memory estimates. `read_csv(..., usecols=["status"], dtype="string", chunksize=3)` reads one column in three-row batches; `value_counts(dropna=False)` includes missing statuses. `concat(..., axis=1)` aligns the batch counts as columns and `sum(axis=1)` sums each status across batches.

# COMMAND ----------

# deep=True includes more of the memory used by underlying object data.
print("Raw DataFrame bytes:", int(raw_orders.memory_usage(index=True, deep=True).sum()))

# Set partial_counts: collect the explicitly listed values.
partial_counts = []
# Read only the status column in small batches and count each batch.
for chunk in pd.read_csv(data_dir / "orders.csv", usecols=["status"], dtype="string", chunksize=3):

    # Call partial_counts.append with the stated inputs.
    partial_counts.append(chunk["status"].value_counts(dropna=False))
# Align counts by status label and add across batches; absent statuses count as zero.
raw_status_counts = pd.concat(partial_counts, axis=1).fillna(0).sum(axis=1).astype("int64")

# Display Chunked raw status counts together with the values supplied below.
print("Chunked raw status counts:\n", raw_status_counts)

# Require `int(raw_status_counts.sum()) == len(raw_orders)`; stop if this invariant fails.
assert int(raw_status_counts.sum()) == len(raw_orders)
# Compare memory after encoding repeated status values as categorical labels.
category_demo = raw_orders["status"].astype("category")

# Display Status bytes, string vs category together with the values supplied below.
print("Status bytes, string vs category:", raw_orders["status"].memory_usage(deep=True),
      category_demo.memory_usage(deep=True))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Pandas and Spark are not interchangeable
# MAGIC Spark DataFrames are distributed and evaluated through Spark; pandas DataFrames live in the driver process. The optional cell below uses an already available Databricks `spark` session to convert our **tiny** accepted table, with unsupported helper fields excluded. Spark is not needed for the rest of the notebook. Use Spark-native reads and transformations for large production datasets; do not `toPandas()` a large table just to run these examples.
# MAGIC
# MAGIC **Options:** `itertuples(index=False, name=None)` produces ordinary tuples without index values; `spark.createDataFrame(spark_rows, schema=spark_columns)` assigns column names while inferring types. The Spark session must already exist.

# COMMAND ----------

# Run this optional comparison only when a Spark session already exists.
if "spark" in globals():

    # Set spark_columns: collect the explicitly listed values.
    spark_columns = ["order_id", "line_id", "customer_id", "region", "line_amount_cents", "status"]
    # Convert only the tiny selected example to rows for Spark schema inference.
    spark_rows = list(accepted[spark_columns].itertuples(index=False, name=None))

    # Assign the result of `spark.createDataFrame(spark_rows, schema=spark_columns)` to spark_demo.
    spark_demo = spark.createDataFrame(spark_rows, schema=spark_columns)

    # Call spark_demo.groupby('status').count().show with the stated inputs.
    spark_demo.groupBy("status").count().show()
else:

    # Display Optional Spark demo skipped: no Spark session in this Python environment. together with the values supplied below.
    print("Optional Spark demo skipped: no Spark session in this Python environment.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 15. Write common data-engineering file formats
# MAGIC A delivery contract determines the format: **CSV and delimited text** for simple interchange, **JSON and JSON Lines** for APIs and events, **Excel** for spreadsheet users, **Parquet and ORC** for columnar analytics, and **Feather** for fast Arrow-based interchange. The same small region/month aggregate is written to each format and read back for verification. Inputs remain in the input volume; output and verification reads use the configured output volume.
# MAGIC
# MAGIC Every output gets a unique filename and is opened in exclusive-create mode; a collision fails instead of overwriting. Rerunning these cells creates additional files. These small driver-side examples are not transactional multi-file writes: if a cell fails, previous or partially written files may remain. Production pipelines need secure storage, explicit schemas, idempotency, monitoring, retention, and a suitable transactional sink.
# MAGIC
# MAGIC Run the setup cell below once before the individual format cells. The run ID groups their filenames; rerun the setup cell to create a fresh set. `reset_index(drop=True)` removes old index labels for comparison, and `assert_frame_equal(..., check_dtype=False)` compares all rows and columns while allowing format-specific dtypes; it does not prove that types were preserved.
# MAGIC
# MAGIC **Format caveats:** CSV, text, and ordinary JSON do not preserve full pandas types; Excel can alter types and has spreadsheet limits. Parquet, ORC, and Feather carry richer types, but support differs across engines; ORC does not preserve timezone metadata in pandas. Validate your own schemas and consumers. Never load untrusted pickle files: they can execute code. Database tables and Delta Lake are not ordinary pandas file-writer formats; use an appropriately configured database connector or Spark/Delta APIs for those destinations. Pandas has no built-in Avro writer.

# COMMAND ----------

# Define a run identifier for related output files. This is not a transaction ID.
export_run_id = uuid4().hex

# Give each file a unique name and keep output paths under the configured directory.
def export_path(suffix):

    # Return the computed value to the caller.
    return output_dir / f"completed_region_month_{export_run_id}.{suffix}"

# Check every value and column after a round trip, while allowing format-specific dtypes.
def verify_export(label, frame):

    # Verify the round-tripped dataframe against the expected result.
    pd.testing.assert_frame_equal(
        frame.reset_index(drop=True), region_month.reset_index(drop=True),
        check_dtype=False,
    )

    # Display the result of f"{label}: verified {len(frame)} rows, {int(frame['revenue_cents'].sum())} cents" for inspection.
    print(f"{label}: verified {len(frame)} rows, {int(frame['revenue_cents'].sum())} cents")

# COMMAND ----------

# MAGIC %md
# MAGIC ### CSV and delimited text
# MAGIC `to_csv` writes both CSV and other delimited text: `sep` selects the delimiter. `index=False` keeps the pandas index out of the file. UTF-8 is explicit, and the sample readers restore string identifiers so a field such as `001` would not become `1`. For compressed batch transfers, `.csv.gz` with `compression="gzip"` saves space. Quoting is still important when field values contain delimiters or newlines.
# MAGIC
# MAGIC #### 15.1 CSV: comma-separated output
# MAGIC `to_csv(path, index=False, mode="x", encoding="utf-8")`: `path` is the output filename, `index=False` excludes pandas row labels, `mode="x"` fails if the file exists, and `encoding` controls text bytes. `read_csv(path, dtype=text_dtypes, encoding="utf-8")` restores the two identifier columns as strings. Predict the output header before running the cell.

# COMMAND ----------

# Use exclusive creation so neither existing outputs nor source files are overwritten.
text_dtypes = {"region": "string", "order_month": "string"}

# Assign the result of `export_path('csv')` to csv_path.
csv_path = export_path("csv")

# Write delimited text using the specified destination and options.
region_month.to_csv(csv_path, index=False, mode="x", encoding="utf-8")

# Call verify_export with the stated inputs.
verify_export("CSV", pd.read_csv(csv_path, dtype=text_dtypes, encoding="utf-8"))

# Display CSV output together with the values supplied below.
print("CSV output:", csv_path)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 15.2 TSV: tab-separated output
# MAGIC `sep="\t"` changes the delimiter to a tab on both write and read. The same `index=False`, `mode="x"`, `encoding="utf-8"` and `dtype` options have the meanings described for CSV.

# COMMAND ----------

# A tab-separated file is still produced with to_csv; only the delimiter changes.
tsv_path = export_path("tsv")

# Write delimited text using the specified destination and options.
region_month.to_csv(tsv_path, sep="\t", index=False, mode="x", encoding="utf-8")

# Call verify_export with the stated inputs.
verify_export("TSV", pd.read_csv(tsv_path, sep="\t", dtype=text_dtypes, encoding="utf-8"))

# Display TSV output together with the values supplied below.
print("TSV output:", tsv_path)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 15.3 Pipe-delimited text
# MAGIC `sep="|"` uses a pipe between fields. The `.txt` extension does not determine the separator: the producer and consumer must agree on it. `mode="x"` still prevents overwrites.

# COMMAND ----------

# A pipe-delimited text feed is common when a downstream system expects a .txt file.
pipe_path = export_path("txt")

# Write delimited text using the specified destination and options.
region_month.to_csv(pipe_path, sep="|", index=False, mode="x", encoding="utf-8")

# Call verify_export with the stated inputs.
verify_export("Pipe text", pd.read_csv(pipe_path, sep="|", dtype=text_dtypes, encoding="utf-8"))

# Display Pipe output together with the values supplied below.
print("Pipe output:", pipe_path)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 15.4 Gzip-compressed CSV
# MAGIC `compression="gzip"` compresses on write and decompresses on read. The `.csv.gz` suffix signals the expected format; specifying the option explicitly makes the contract visible. `index`, `mode`, `encoding`, and `dtype` work as above.

# COMMAND ----------

# Gzip compresses the same CSV data; specify compression on both write and read.
gzip_path = export_path("csv.gz")

# Write delimited text using the specified destination and options.
region_month.to_csv(gzip_path, index=False, mode="x", encoding="utf-8", compression="gzip")

# Call verify_export with the stated inputs.
verify_export("Gzip CSV", pd.read_csv(gzip_path, dtype=text_dtypes, encoding="utf-8", compression="gzip"))

# Display Compressed CSV output together with the values supplied below.
print("Compressed CSV output:", gzip_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ### JSON and JSON Lines
# MAGIC `orient="records"` represents each row as a JSON object; without `lines=True` the output is a JSON array, suitable for a small API payload. With `lines=True`, each line is a separate object, often convenient for event and log ingestion. The corresponding reader must use the same `lines` setting. JSON number and date handling depends on the consumer; document the contract.
# MAGIC
# MAGIC #### 15.5 JSON array
# MAGIC `path.open("x", encoding="utf-8")` exclusively creates a text file. `to_json(file, orient="records", indent=2)` writes a list of row objects, pretty-printed with two-space indentation. `read_json(path, orient="records", dtype=text_dtypes)` reads that shape and restores string types.

# COMMAND ----------

# Pass an exclusively created text file handle to prevent overwriting.
json_path = export_path("json")

# Open the context shown below and release it when the block finishes.
with json_path.open("x", encoding="utf-8") as file:

    # Serialize records as json using the specified layout.
    region_month.to_json(file, orient="records", indent=2)

# Call verify_export with the stated inputs.
verify_export("JSON array", pd.read_json(json_path, orient="records", dtype=text_dtypes))

# Display JSON output together with the values supplied below.
print("JSON output:", json_path)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 15.6 JSON Lines
# MAGIC `orient="records", lines=True` writes one JSON object per line. The reader also needs `lines=True`, or it will expect a single JSON document. The file is created with `open("x", encoding="utf-8")`, and `dtype` controls the identifier columns when reading.

# COMMAND ----------

# JSON Lines has one record per line, rather than one enclosing array.
jsonl_path = export_path("jsonl")

# Open the context shown below and release it when the block finishes.
with jsonl_path.open("x", encoding="utf-8") as file:

    # Serialize records as json using the specified layout.
    region_month.to_json(file, orient="records", lines=True)

# Call verify_export with the stated inputs.
verify_export("JSON Lines", pd.read_json(jsonl_path, orient="records", lines=True, dtype=text_dtypes))

# Display JSON outputs together with the values supplied below.
print("JSON outputs:", json_path, jsonl_path, sep="\n")

# COMMAND ----------

# MAGIC %md
# MAGIC #### 15.7 Excel workbook
# MAGIC Excel is useful for sharing small reports with business users, not for large-scale distributed processing. The workbook contains two named sheets: the aggregate and the lookup targets. Unity Catalog volumes do not support the non-sequential writes needed to build an Excel ZIP archive directly. We build this **small** workbook with `ExcelWriter` and `openpyxl` in memory, then write the finished bytes sequentially to the volume. This creates no temporary directory or local source file, but memory usage grows with workbook size.
# MAGIC
# MAGIC Source: [Databricks: writing Excel files to a Unity Catalog volume](https://kb.databricks.com/unity-catalog/trying-to-write-excel-files-to-a-unity-catalog-volume-fails).
# MAGIC
# MAGIC **Arguments:** `ExcelWriter(excel_buffer, engine="openpyxl")` selects the in-memory destination and workbook engine. `to_excel(writer, sheet_name="RegionMonth", index=False)` selects the destination sheet and excludes the index. `open("xb")` creates a new binary file exclusively. `read_excel(path, sheet_name=..., dtype=text_dtypes)` selects a sheet and restores text types; `check_dtype=False` allows format-driven dtype differences in the verification.

# COMMAND ----------

# Assign the result of `export_path('xlsx')` to excel_path.
excel_path = export_path("xlsx")
# ExcelWriter closes the workbook and finalizes its bytes before the volume write.
excel_buffer = BytesIO()

# Open the context shown below and release it when the block finishes.
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:

    # Write the dataframe to the selected excel worksheet.
    region_month.to_excel(writer, sheet_name="RegionMonth", index=False)

    # Write the dataframe to the selected excel worksheet.
    targets.to_excel(writer, sheet_name="Targets", index=False)
# Exclusive binary creation protects any existing output; write finished bytes once.
with excel_path.open("xb") as file:

    # Call file.write with the stated inputs.
    file.write(excel_buffer.getvalue())

# Call excel_buffer.close with the stated inputs.
excel_buffer.close()

# Call verify_export with the stated inputs.
verify_export("Excel RegionMonth", pd.read_excel(excel_path, sheet_name="RegionMonth", dtype=text_dtypes))

# Verify the round-tripped dataframe against the expected result.
pd.testing.assert_frame_equal(pd.read_excel(excel_path, sheet_name="Targets"), targets, check_dtype=False)

# Display Excel output together with the values supplied below.
print("Excel output:", excel_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Parquet, ORC, and Feather
# MAGIC Parquet is a common columnar format for lakehouse analytics; compression and selecting only needed columns can reduce I/O. ORC is another columnar format common in Hadoop/Hive ecosystems. Feather is an Arrow-based interchange format useful for fast data exchange between compatible tools; it is not a transactional table format. These examples use pandas with the **pyarrow** engine and a simple default index.
# MAGIC
# MAGIC Formats and versions can differ in type support. Test timestamps, decimals, nullable fields, and schema evolution with your actual reader. Files written by pandas are single-driver examples; use Spark-native writes for distributed datasets. A Parquet file is not a Delta table: Delta requires its transaction log.
# MAGIC
# MAGIC #### 15.8 Parquet
# MAGIC `open("xb")` creates a binary file without overwriting. `to_parquet(file, engine="pyarrow", compression="snappy", index=False)` chooses the engine, compression codec, and excludes the index. `read_parquet(path, engine="pyarrow")` reads the saved columns back.

# COMMAND ----------

# Write columnar files to exclusive binary handles and read each one back.
parquet_path = export_path("parquet")

# Open the context shown below and release it when the block finishes.
with parquet_path.open("xb") as file:

    # Write a compressed columnar parquet file.
    region_month.to_parquet(file, engine="pyarrow", compression="snappy", index=False)

# Call verify_export with the stated inputs.
verify_export("Parquet", pd.read_parquet(parquet_path, engine="pyarrow"))

# Display Parquet output together with the values supplied below.
print("Parquet output:", parquet_path)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 15.9 ORC
# MAGIC `to_orc(file, engine="pyarrow", index=False)` writes to an exclusively created binary file using the Arrow ORC engine and excludes the index. `read_orc(path)` reads the file. ORC type support differs from Parquet, and pandas notes that timezone metadata is not preserved.

# COMMAND ----------

# Assign the result of `export_path('orc')` to orc_path.
orc_path = export_path("orc")

# Open the context shown below and release it when the block finishes.
with orc_path.open("xb") as file:

    # Write a columnar orc file.
    region_month.to_orc(file, engine="pyarrow", index=False)

# Call verify_export with the stated inputs.
verify_export("ORC", pd.read_orc(orc_path))

# Display ORC output together with the values supplied below.
print("ORC output:", orc_path)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 15.10 Feather
# MAGIC `reset_index(drop=True)` gives Feather a default index without adding the old index as a column. `to_feather(file)` writes Arrow Feather to an exclusively created binary handle; `read_feather(path)` reads it back. The default writer settings are used; no compression option is passed explicitly.

# COMMAND ----------

# Assign the result of `export_path('feather')` to feather_path.
feather_path = export_path("feather")

# Open the context shown below and release it when the block finishes.
with feather_path.open("xb") as file:

    # Write an arrow feather file.
    region_month.reset_index(drop=True).to_feather(file)

# Call verify_export with the stated inputs.
verify_export("Feather", pd.read_feather(feather_path))

# Display Feather output together with the values supplied below.
print("Feather output:", feather_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 16. Recap, exercises, and discussion
# MAGIC **Pipeline recap:** raw CSV (10 rows) → one exact duplicate → five rejected rows (four field-rule failures and one unknown customer) → four accepted lines → three completed lines, two distinct completed orders, and 145,000 cents completed revenue. One valid cancelled line is excluded from revenue. Source-row IDs make investigation possible.
# MAGIC
# MAGIC **Practice, with expected outcomes**
# MAGIC 1. Find the rejected row with an unknown customer. Add a valid C999 customer to the dimension and rerun the join onward: accepted rows should rise by one and rejects fall by one. The fixture-specific assertions and subsequent totals will need updating. Decide whether this is acceptable for your business process.
# MAGIC 2. Change the quantity for O101 to `2` in an in-memory copy of `raw_orders`, then rerun the cleansing and quality checks: its invalid-quantity failure should disappear. Do not edit the shared source file. Update the fixture-specific assertions and recalculate expected totals.
# MAGIC 3. Add a different payload with key `(O100, 1)`. Confirm both versions of that key are marked as conflicts, rather than choosing an arbitrary winner. Revisit the fixed fixture assertions when you intentionally change the input.
# MAGIC 4. Compute completed revenue by product and verify that the total equals 145,000 cents. Explain why adding order counts by product may exceed the global distinct-order count.
# MAGIC 5. Change C001's historical region boundary and observe how point-in-time attribution changes. Introduce overlapping intervals and confirm the SCD validation raises.
# MAGIC 6. Move the S2 calibration within three hours of its reading; confirm the previously unmatched row receives an offset.
# MAGIC
# MAGIC **Discussion:** When would you reject rather than repair a record? What source system owns the key? What happens if a file is missing versus an empty file? How would you make writes, quality metrics, and checkpoint advancement atomic? What PII should never appear in teaching data or logs?
# MAGIC
# MAGIC **Production next steps:** define source contracts and SLAs; store raw and reject datasets securely; record lineage, run IDs and rule counts; add unit/integration tests; design replay and late-data policies; enforce schema and access control; and use distributed processing where data size demands it.