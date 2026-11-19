# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC DataTypes

# COMMAND ----------

#data types
# str
# int
# float
# complex
# range
# list
# tuple
# set
# dict
# frozenset
# bytes
# bytearray
#datetime
# bool

# COMMAND ----------

v_float=100.56
type(v_float)

# COMMAND ----------

#complex data type
complex_data=5+10j
type(complex_data)
print("Real part is:",complex_data.real)
print("imaginary part is:",complex_data.imag)
String='Sample String'
#range(sequence type)(start_num,end_num-1,increment)
rangevariable=range(11)
print(rangevariable)
vRange2=range(1,len(String)+1,3)
print(vRange2)
set_var=set(vRange2)
list_var=list(rangevariable)
print(set_var, list_var)

# COMMAND ----------

# MAGIC %md
# MAGIC Data Structures/Collections(list,set,dict,tuple,frozenset)

# COMMAND ----------

#list[] ordered,indexed and mutable

list1=[1,2,3,4,4,5,6,'string']
list2=[8,9,10]
print(list1)
print(list1[4],list1[-3],list1[3:5]) #index referencing and slicing
list_variable=list1[5] #variable assignment
print(list_variable)
type(list_variable)
list1.append(1000)
list1.append(['Naveen','Rajesh'])
# list1.append('New value') # to insert any element at the end of the list
list1.insert(5,True) #to insert any element into the list for a given index
print(list1)
list1[5]=False # to update the list for a given index position
list1.remove('string') #to remove a element with element value given
print(list1)
list1[9].remove('Naveen')

list1.pop() # to remove the last element from the list
list1.pop(2) # to remove the element using a given index
del list1[7] #to remove the element using a given index
del list1 # delete the list variable
list1.extend(list2) # to merge two lists
list2.extend(list1)
# list3=list1+list2
print(list2)

# COMMAND ----------

print(list1)

# COMMAND ----------

sample_list=[1,'Today is Monday',True,5+6j]

# COMMAND ----------

# type(sample_list)
print(sample_list)

# COMMAND ----------

# list sort,reverse,index,copy,clear
list1=[7,2,100,1,2,3,4,4,5,6]
list2=['apple','Xmas','Bulb','orange']
# list2=['apple','Xmas','Bulb','orange',True,50]
list1.sort()
print(list1)
list2.sort()
print(list2)
list2.sort(key=len)
# list2.sort()
list1.sort(reverse=True)
print(list1)
print(list2)
list3=list1+list2 #merging
print(list3)

#reverse
list3.reverse()
print(list3)
print('index of apple is: ', list3.index('apple'))
print('index of apple is: ', list3.index(4))
list3[:list3.index('apple')+1]
print(list3.index(2,8,10))
list4=list3
print(list4)
print(list3)
list4=list3.copy()
list3.append('NewValue')
list4.append('NewValue2')
print(list4)
print(list3)

list4.clear()
list4


# COMMAND ----------

num1=5
num2=num1
print(num1,num2)
num1=6
print(num1,num2)

# COMMAND ----------

#tuple ordered,indexed and immutable,concat
tuple1=(1,23,4,4,5)
tuple2=('A','B','C')
type(tuple1)
print(tuple1[1],tuple1[2:])
tuple3=tuple1+tuple2
print(tuple3)
# tuple2=tuple1.copy()
tuple2
# tuple1.reverse()
tuple1


# COMMAND ----------

#set unordered,unindexed , mutable,unique
set1={100,5,1,2,3,4,5,5,5,6}
print(set1)
set1.add(7)
set1.add(8)
print(set1)
set1.discard(7)
set1.remove(5)
print(set1)
set1.pop()
print(set1)
set1
set2={}
type(set2)

# COMMAND ----------

list_sample=[]
tuple_sample=()
set_sample={}
print(type(list_sample))
print(type(tuple_sample))
print(type(set_sample))

# COMMAND ----------

#set clear,copy,remove,add,discard,pop,union,intersection,difference,

set1={1,10,15,26,28}
set1.clear()
type(set1)
print(set1)
set2={56,100,10,1,0}
set3=set2.copy()
print(set3)
set2.add(1000)
print(set3)
print(set2)
set3.clear()
# set2.remove(-99)
set2.discard(-99)
set2
set2.pop()
print(set1)
print(set2)
set4=set1.union(set2)
print(set4)
set5=set1.intersection(set2)
print(set5)
set6=set1.difference(set2)
print(set6)
set7=set2.difference(set1)
print(set6,set7)


# COMMAND ----------

set123={1,1,1,1,1}
print(set123)
list123=list(set123)
print(list123)
tuple123=(1,1,1,1)
list2=set(tuple123)
set123
print(list2)

# COMMAND ----------

#dict key value pairs,ordered,doent allow duplicate keys,copy,clear
dict1={'name':'Naveen','profession':'engineer','location':'India'}
print(dict1)
print(dict1['profession'])
dict_profession=dict1['profession']
print(dict_profession)
dictionary_items=dict1.items()
print(dictionary_items)

# COMMAND ----------

nested_json={
  "employee": {
    "id": 101,
    "name": "John Doe",
    "department": {
      "id": "D001",
      "name": "Engineering"
    }
  }
}
type(nested_json)

# COMMAND ----------

dict1['location']='USA'
print(dict1)
del dict1['location']
print(dict1)
dict1['city']='Newyork'
print(dict1)
dict1.pop('city')
print(dict1)
dict1.popitem()
print(dict1)
dict2=dict1.copy()
print(dict2)
dict1.clear()
print(dict2)
print(dict1)
nested_json['employee']['department']['id']='D002'
print(nested_json)


# COMMAND ----------

# del dict1
print(dict1)

# COMMAND ----------

#frozen set unordered,unidexed,immutable
set2=frozenset({1,2,3,4,5,5})
type(set2)
# print(set2)

# COMMAND ----------

#bytes encoded datatype(utf-8,utf-16,utf-32...),immutable
a=b'apple'
b=bytes(10)
c=bytes('Orange','utf-16')
print(a,b,c)
type(c)

# COMMAND ----------

#bytearray indexed,mutable
a=bytearray(10)
b=bytearray('apple','utf-32')
print(a)
a[2]=3
print(a,b)

# COMMAND ----------

decoded_b = b.decode('utf-32')
print(decoded_b)

# COMMAND ----------

#datetime functions
from datetime import datetime 
today_date=datetime.now()
print(today_date)
type(today_date)
print(today_date.year)
print(today_date.month)
today_day=today_date.day
print(today_day)
print(today_date.strftime("%a"))
print(today_date.strftime("%B"))

# COMMAND ----------

from datetime import datetime 
import pytz 
  
# get the standard UTC time 
UTC = pytz.utc 
type(UTC)
# it will get the time zone 
# of the specified location 
IST = pytz.timezone('Asia/Kolkata') 
type(IST)

CST=pytz.timezone('US/Central') 
type(CST)
  
# print the date and time in 
# standard format 
print("CST in Default Format : ", 
      datetime.now(CST)) 
  
print("IST in Default Format : ", 
      datetime.now(IST)) 
  
# print the date and time in 
# specified format 
datetime_utc = datetime.now(UTC) 
 
print("Date & Time in UTC : ", 
      datetime_utc.strftime('%Y:%m:%d %H:%M:%S %Z %z')) 
  
datetime_ist = datetime.now(IST) 
print("Date & Time in IST : ", 
      datetime_ist.strftime('%Y-%m-%d %H:%M:%S %Z %z')) 

# COMMAND ----------

type(datetime_ist)

# COMMAND ----------

# V_bool=True
V_bool=False
type(V_bool)


# COMMAND ----------

