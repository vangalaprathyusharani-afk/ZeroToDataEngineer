# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
#type casting(implicit,explicit)
a='15'
b=16
# c=a+b
# c=int(a)+b
c=a+str(b)
print(c)
type(c)
type(b)

# COMMAND ----------

# This is comments
b+c

# COMMAND ----------

#multiline statements
# print("This is Naveen \n and i am an engineer \n I am good")
sample_quote="This is Naveen \nand i am an engineer \nI am good"
print(sample_quote)
# print("Second statement, This is Naveen
# and I am engineer
# and i am good")
print("""Second statement, This is Naveen
and I am engineer
and i am good""")
string='hello'
sample_quote='''Second statement, This is Naveen
and I am engineer
and i am good'''
print(sample_quote,string)

# COMMAND ----------

#format strings
name='Naveen'
age=30
location='Chennai'
# print("my name is :{n} and my age is :{a} and  i am from :{l}".format(a=age,n=name,l=location))
print("my name is: ",name," and my age is :",age, "and  i am from :" ,location)
print("my name is :{1} and my age is :{0} and  i am from :{2}".format(age,name,location))

sample_string="""my name is :{1} 
and my age is :{0}""".format(age,name)
print(sample_string)

# COMMAND ----------

#f strings
country='India'
city='Hyd'
# statement='my country is :{country} and I am from :{city}'
statement=f'my country is :{country} and I am from :{city}'
# print(f'my name is :{name} and my age is :{age}')
print(statement)

# COMMAND ----------

# real time example
franchiseid=3000038
df=spark.sql(f"""
select * from samples.bakehouse.media_customer_reviews
where franchiseid={franchiseid}""")
display(df)

# COMMAND ----------

#type casting %s,%d,%f ...
num1=156
num2=15.8568
char1='String'
print("num1=%f , num2=%s"%(num1,num2))
num3="%s"%(num2)
print(num3)
type(num3)
num4=float(num1)
print(num4)
type(num4)

# COMMAND ----------

name = "Sita"
age = 22
print("Using %s ")
print ("%s's age is %d."%(name,age))
# print ("%d's age is %s."%(name,age))

# COMMAND ----------

type(char1)

# COMMAND ----------

#Arithmetic operators
add=1+1
mult=2*2
print(add)
print(mult)
print(4/2) #float output from division
print(4//2) #integer output from dvivison
print(7%2) #modulus operator to get the reminder from a division

# COMMAND ----------

#string operations
#indexing
str1='This is a training session ' #index=0,1,2,3,4... , reverse_index=....,-3,-2,-1
print(str1[-2])
print(str1[24])

#length of the string
print(len(str1))

#slicing(substring)(starting_index:end_index-1) and from lower number to higher number but not viceversa
str2=str1[5:20]
print(str2)
str22=str1[20:5]
print(str22)
str3= str1[5:] # starting from 5 until end
print(str3)
str33= str1[:5]
print(str33)
str4=str1[6:len(str1)-2]
print(str4)
str5=str1[-6:-1]
print(str5)
print("str2=",str2,"str22=",str22,"str33=",str33, "str3=",str3, "str4=",str4,"str5=",str5)
# print("str3=",str3, "str33=",str33)

# COMMAND ----------

sample_string='my name is Naveen'
len(sample_string)
# reverse_string=sample_string[-5:-3]
reverse_string=sample_string[::-1]
print(reverse_string)

# COMMAND ----------

