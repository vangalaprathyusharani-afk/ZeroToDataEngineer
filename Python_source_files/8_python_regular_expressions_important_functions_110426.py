# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Regular Expressions and Useful Python Functions
# MAGIC
# MAGIC This lesson demonstrates regular-expression tools for inspecting and
# MAGIC cleaning text, alongside Python functions useful in data pipelines.
# MAGIC Comments in the code explain what each operation does and call out common
# MAGIC mistakes to avoid.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Regular-expression operations
# MAGIC
# MAGIC - `re.findall(pattern, text)` returns all matches as a list.
# MAGIC - `re.search(pattern, text)` returns the first match object, or `None`.
# MAGIC   Match objects provide positions such as `.start()` and `.end()`.
# MAGIC - `re.split(pattern, text)` splits wherever the pattern matches.
# MAGIC - `re.sub(pattern, replacement, text)` replaces matches in the text.
# MAGIC - `re.compile(pattern)` Compiles the pattern once and can be executed any number of times .
# MAGIC - `re.match(pattern,text)` return true if the text matchesthe pattern else false.
# MAGIC
# MAGIC These tools are useful for extracting IDs, validating text formats, and
# MAGIC normalizing semi-structured fields. A pattern is not automatically a
# MAGIC validator.

# COMMAND ----------

# A few common pattern tokens:
# ^      beginning of the string (or line with re.MULTILINE)
# $      end of the string (or line with re.MULTILINE)
# \s     whitespace; \S is a non-whitespace character
# \d     digit; \D is a non-digit
# \w     Unicode word character; \W is a non-word character
# [A-Z]  one uppercase ASCII letter; [0-9] is one digit
# *      zero or more repetitions of the previous token
# +      one or more repetitions of the previous token
# .      any character except newline by default
# {n}    exactly n repetitions; {m,n} means between m and n repetitions
# |      alternation (OR); use parentheses to control its scope
# \      escape a special character, or introduce a sequence such as \d

# COMMAND ----------

import re

# The leading punctuation is intentional; the text also ends in a six-digit
# postal code. The pattern alternatives match either a word at the start OR
# six digits at the end. Parentheses make those two branches explicit.
text = "@$56 This is Naveen and my postal code is 500050"
pattern = r"(^\w+)|(\d{6}$)"

# search returns the first occurrence that matches either branch. Since the
# leading characters are punctuation, the six-digit postal code is the match.
match = re.search(pattern, text)
if match is not None:
    # `.end()` is exclusive: subtract one to show the final included index.
    print("Matched text:", match.group())
    print("Start index is", match.start())
    print("End index is", match.end() - 1)
else:
    # Always check for None before using match methods on arbitrary input.
    print("No match found.")

# COMMAND ----------

text = "@$56 This is Naveen and my postal code is 500050"
# The text begins with punctuation ("@$"), then digits ("56"), then words,
# and ends with a six-digit postal code. Each part of the pattern mirrors that:
# ^\W+  one or more non-word characters at the start ("@$")
# \d+   the digits right after the punctuation ("56")
# .+   everything in the middle ("This is Naveen and my postal code is")
# \d{6}$ exactly six digits at the end ("500050")
pattern = r"^\W+\d+\s.+\s\d{6}$"

match = re.search(pattern, text)
match.group() if match else None

# COMMAND ----------


text = "@$56 This is Naveen and my postal code is 500050"
pattern = r"(?P<code>@\$\d+)\s+This is\s+(?P<name>[A-Za-z]+)\s+and my postal code is\s+(?P<postal>\d{6})"

# search returns the first occurrence that matches either branch. Since the
# leading characters are punctuation, the six-digit postal code is the match.
match = re.search(pattern, text)
# matchdict=match.group() if match else None
matchdict=match.groupdict() if match else None
print(matchdict)

# COMMAND ----------

# re.sub interprets its first argument as a regex and replaces every match.
# pattern=r"^\W+"
# pattern=r"@\$"
pattern=r"This"
cleaned_text = re.sub(pattern, "*", text)

# str.replace treats its first argument as literal text, not as a regex.
# Here it replaces spaces with four slash characters.
slashes_for_spaces = text.replace(" ", "////")
print("Regex substitution:", cleaned_text)
print("Literal string replacement:", slashes_for_spaces)

# COMMAND ----------

# This example contains punctuation between words to demonstrate splitting.
text = "This is$Naveen@and%I my postal code is 500050"

# str.replace replaces the literal name; it does not interpret regex syntax.
name_hidden = text.replace("Naveen", "*")
print("Name replaced:", name_hidden)

# Split only on spaces, retaining punctuation attached to each token.
space_separated = text.split(" ")
print("Split on spaces:", space_separated)

# Regex split on one or more non-word characters. This removes punctuation
# separators, but may produce empty strings where separators occur at edges.
non_word_separator = r"\W+"
words = re.split(non_word_separator, text)
print("Split on punctuation/whitespace:", words)

# COMMAND ----------

# `+` groups consecutive characters into one match: for example, "Naveen"
# is one match, while `r"[a-z]"` would return each lowercase letter separately.
grouped_pattern = r"[a-z]+|[A-Z]+|[0-9]+"
single_character_pattern = r"[a-z]|[A-Z]|[0-9]"
grouped_matches = re.findall(grouped_pattern, text)
character_matches = re.findall(single_character_pattern, text)
print("Runs of letters/digits:", grouped_matches)
print("Individual letters/digits:", character_matches)

# COMMAND ----------

import re
text="naveen@gmail.com"
pattern=re.compile(r"[a-zA-Z0-9]+@+[a-zA-Z]+\.+[a-z]{3}")
# match=pattern.search(text)
# print(match.group())
# match returns a match object on success or None on failure,
# so compare against None to get a plain True/False result.
print(pattern.match('flmadeteam@gmail.com') is not None)
print(pattern.match(text) is not None)


# COMMAND ----------

# greedy match vs nobn-greedy match
text='123abc456abc'
# pattern=r"1.*b" # greedy match
pattern=r"3.*?b" # non-greedy match
print(re.search(pattern,text).group())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data engineering example 1: Standardize incoming column names
# MAGIC
# MAGIC Data from different vendors may use headers such as `Customer ID`,
# MAGIC `order-date`, or `Amount ($)`. Normalize them into predictable snake_case
# MAGIC before mapping data into a target schema. This transformation is
# MAGIC deterministic, so the same input header always produces the same output.
# MAGIC Review the result for collisions: for example, `Order Date` and
# MAGIC `order-date` both normalize to `order_date`.

# COMMAND ----------

raw_headers = [" Customer ID ", "order-date", "Amount ($)", "order date"]


def normalize_column_name(header):
    # Strip surrounding spaces and lowercase before replacing punctuation/spaces.
    normalized = re.sub(r"[^a-z0-9]+", "_", header.strip().lower())
    print(f"Normalized {header} to {normalized}")
    # Remove underscores introduced at the beginning or end of the header.
    return normalized.strip("_")


normalized_headers = [normalize_column_name(header) for header in raw_headers]
duplicate_headers = sorted(
    {
        header
        for header in normalized_headers
        if normalized_headers.count(header) > 1 # count of a specific element in a list
    }
)
print(sorted({
        header
        for header in normalized_headers
        if normalized_headers.count(header) > 1 # count of a specific element in a list
    }))

print("Normalized headers:", normalized_headers)
print("Colliding headers:", duplicate_headers)
print("unique headers:" ,list(set(normalized_headers)))

# COMMAND ----------

header="Amount ($)"
print(header.strip().lower())
normalized = re.sub(r"[^a-z0-9]+", "_", header.strip().lower())
print(normalized)

# COMMAND ----------

raw_headers = [1,2,1,5,2,7,3,6,1]
raw_headers.count(5)


# COMMAND ----------

# MAGIC %md
# MAGIC ## Data engineering example 2: Extract emailId
# MAGIC

# COMMAND ----------

import re

email_pattern = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

text = "Contact me at flmadeteam@gmail.org"

match = email_pattern.search(text)

print(match.group())


# COMMAND ----------

x= int(input("enter a value:"))
numbers = list(range(1,11))
for i in numbers:
    multlipication = i* x
    print(multlipication)
# print(x,numbers)


# COMMAND ----------

# MAGIC %md
# MAGIC ## Data engineering example 3: File Pattern Match
# MAGIC

# COMMAND ----------

dbutils.fs.cp('/Volumes/workspace/default/mydefaultvolume/sales_04112026.txt','/Volumes/workspace/default/mydefaultvolume/salesorders_04112026.txt')

# COMMAND ----------

import os
import re

pattern = re.compile(r"^sales_\d{8}\.txt$")

files = [
    f
    for f in os.listdir("/Volumes/workspace/default/mydefaultvolume/")
    if pattern.match(f)
]

print(files)

# COMMAND ----------

# enumerate pairs each item with its zero-based position.
values = [0, 1, 2, 3, 4, 54, "hello"]
reversed_values = list(reversed(values))

# Store each position/value pair as a tuple. A set is unordered and is not
# the right structure when the pair's order is meaningful.
indexed_values = [
    (index, element) for index, element in enumerate(reversed_values)
]
for index, element in indexed_values:
    print(f"Index is {index} and element is {element}")
print("Indexed rows:", indexed_values)

# COMMAND ----------

# isinstance checks whether a value has a particular type. bool is a subclass
# of int in Python, so test bool before int when distinguishing the two.
value = "100"
print("Is string:", isinstance(value, str))
print("Is integer:", isinstance(value, int))
print("Is boolean:", isinstance(False, bool))
print("Is set:", isinstance({6}, set))
print("Is dictionary:", isinstance({"name": 8}, dict))
print("Is tuple:", isinstance((5, 6), tuple))
print("Is list:", isinstance([8, 6], list))

# COMMAND ----------

# random provides pseudorandom utilities for simulations and sample data.
# Avoid `from random import *`: explicit imports make function origins clear.
import random

shuffled_values = list(range(20))
random.shuffle(shuffled_values)  # Shuffles this list in place.
print("Shuffled values:", shuffled_values)

# randint includes both endpoints: 0 and 1_000 are possible here.
sample_id = random.randint(0, 1000)
print("Sample integer:", sample_id)

# COMMAND ----------

# String methods return new strings; strings themselves are immutable.
sample_text = "This is Naveen"
print("Uppercase:", sample_text.upper())
print("Lowercase:", sample_text.lower())
print("Capitalized:", sample_text.capitalize())

# replace substitutes every occurrence of the specified literal substring.
print("Spaces replaced:", sample_text.replace(" ", "//"))

# strip removes whitespace from both ends; lstrip/rstrip affect one side only.
# These methods do not remove whitespace between words.
name = "  Python  "
print("Both sides:", name.strip())
print("Left side:", name.lstrip())
print("Right side:", name.rstrip())

# COMMAND ----------

# filter calls its predicate for each value and keeps values whose result is
# True. Return a boolean condition so that zero is correctly kept as even.
def is_even(number):
    return number % 2 == 0


numbers = list(range(20))
even_numbers = list(filter(is_even, numbers))
print("Even numbers, including zero:", even_numbers)

# reduce combines values cumulatively: (((1 + 1) + 3) + 4) + ...
from functools import reduce

values_to_sum = [1, 1, 3, 4, 5, 6]
total = reduce(lambda left, right: left + right, values_to_sum)
print("Reduced sum:", total)

# For simple numeric totals, built-in sum is usually more readable than reduce.
print("Sum using built-in sum:", sum(values_to_sum))

# COMMAND ----------

# assert is useful for developer checks during testing, not for validating
# untrusted production data: Python may disable assertions with optimization.
expected_columns = {"order_id", "amount"}
actual_columns = {"order_id", "amount", "order_date"}

# This assertion passes because all expected columns are present.
assert expected_columns.issubset(actual_columns), "Required columns are missing"
print("Required columns are present.")

# For pipeline validation, use an explicit condition and raise an exception
# instead of relying on assert, so the check remains active in production.
if not expected_columns.issubset(actual_columns):
    raise ValueError("Required columns are missing")

# COMMAND ----------

# type reports the runtime type. In data pipelines, validation with isinstance
# is often more flexible when subclasses should also be accepted.
print("Runtime type of actual_columns:", type(actual_columns).__name__)