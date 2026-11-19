# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# print("welcome to Python's Training")
# statement="There are hundred's of people"
# statement="There are hundreds of people"
# statement: str="There are hundreds of people"
statement: int="There are hundreds of people"
val=5
print(statement)
type(statement)


# COMMAND ----------

print(statement)
statement = True
print(statement)
type(statement)


# COMMAND ----------

print(val)
type(val)

# COMMAND ----------

#variables (which can be overriden any number of times)
# comments(ctrl+/)
var1 = 'sample_string'
print(var1,' , this is the first assignment','   "   This is the thid statement')
var1=10
print(var1,', this is the second assignment')


# COMMAND ----------

# multi variable assignment
# to run a cell - shift+enter
# to run selected text - ctrl+shift+enter
number_var= number_var2=num_var3='100'
print(number_var,number_var2,num_var3)

number_var,number_var2,num_var3=100,'string',500
print(number_var,number_var2,num_var3)

print(number_var2)
print(num_var3)
print(number_var)
var2='Good Morning'
# type(number_var2)

# COMMAND ----------

print(var1,', this is the first assignment')

# COMMAND ----------

type(var1)

# COMMAND ----------

numberf='True'

# COMMAND ----------

number_var='Hello'

# COMMAND ----------

print("The number variable is:",number_var2," and The character Variable is :",var2)

# COMMAND ----------

# print("The number variable is:",number_var2," and The character Variable is :",var2)
print(1+1)
print(7+7)

# COMMAND ----------

if 100>=50:
    print('100>50')
    if 100==100:        
       print("100 is equal to 100")            
print("hello")

# COMMAND ----------

if 1==1:(print('Hello'))

# COMMAND ----------

name: int='Naveen'

# COMMAND ----------

print(name)

# COMMAND ----------

type(name)

# COMMAND ----------

# Multi-line comments in Python:
# Shortcut: select the lines and press Ctrl + / (Cmd + / on Mac) to toggle comments

# 1. Multiple single-line comments (the standard way)
# This is line one of the comment
# This is line two of the comment
print("using # on each line")

# 2. Triple-quoted string used as a multi-line comment/block (not a real comment,
#    but often used to 'comment out' code or write docstrings)
"""
This is a multi-line string.
It can span several lines and is often used
to quickly comment out a block of code.
"""
print("using triple quotes")

# Tip: to comment out existing code fast, highlight it and press Ctrl + /
# print("this line is commented out")
# print("this one too")

# COMMAND ----------

# 
print('multi line comments \nsecond line')

# COMMAND ----------

print("Hello\nWorld")


# COMMAND ----------

