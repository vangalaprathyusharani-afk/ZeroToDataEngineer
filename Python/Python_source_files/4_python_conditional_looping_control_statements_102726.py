# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
list1=[1,2,3]
# list1.clear()

# COMMAND ----------

#synatax
if False:
    print('This is true statement')
else:#optional block to excute when if condition is evaluated to false
    print('This is false statement')

if list1:# the condotion will be evaluated to True in case of non-empty list else False
    print('This is a full list ')
else:
    print('This is an empty list')

# COMMAND ----------

a=1000
b=500
print(a,b)


# COMMAND ----------

if b>a:
    print('b>a')
else:
    print('b<a')

# COMMAND ----------

d=1000
c=1000
print(c,d)

# COMMAND ----------

#multiple conditions
if c==d:
    print(f'{c} equals to {d}')
elif c>d:
    print(f'{c} greater than {d}')
elif c<d:
    print(f'{c} less than {d}')
else:
    print('Nothing')

# COMMAND ----------

if c!=d:
    if c>d:
        print(f'{c} greater than {d}')
    # else:
    #     print(f'{c} less than {d}')
else:
    print(f'{c} equals to {d}')


# COMMAND ----------

#nested conditions
if c!=d:
    if c>d:
      print(f'{c} greater than {d}')
    elif c<d:
        print(f'{c} less than {d}')  
    else:
        print('Nothing')
else:
    print(f'{c} equals to {d}')


# COMMAND ----------

a=3
if a in list1:
    print(f'{a} is present in the {list1}')
else:
    print(f'{a} is not part of {list1}')

# COMMAND ----------

if a in list1:
    print (f'{a} is present in the {list1}')
else:
    print(f'{a} is not part of {list1}')

# COMMAND ----------

a=10

# COMMAND ----------

list2=[1,2,3,4,5,6,7,8,9]
if a in list2:
    print(f'{a} is present in the {list2}')
else:
    print(f'{a} is not part of {list2}')


# COMMAND ----------

country='India'
State=['Telangana','AP','Tamilnadu','Delhi']
TG_City =['Hyderabad','Warangal']
TN_City=['Chennai','Coimbatore']
AP_City=['Vizag','Vijayawada']
Delhi_city=['Delhi']

# COMMAND ----------

i_state='AP'
i_city='Vizag'
if country=='India':
    if i_state in State:
        if i_state=='Telangana':
            if i_city in TG_City:
                print('Candidate can be considered for hiring process')
            else:
                print("Candidate is from Telangana but not from listed cities and can't be considered for hiring process")
        elif i_state=='AP':
            if i_city in AP_City:
                print(f'Candidate  from AP and from {i_city}  can be considered for hiring process')
            else:
                print("Candidate is from AP but not from listed cities and can't be considered for hiring process")
    else:
        print("the candiate is from other states")
else:
    print("Candidate is from outside of india and can't be considered")


# COMMAND ----------

#shorhand if
c=100
d=1000
# if c!=d: print('True')

print('c not equals to d') if c!=d else print('false block,c equals to d') 

#every shorthandif should follow with else block in nested conditions
print('c equals to d') if c==d  else print('c greater than d') if c>d else print('c less than d')

# COMMAND ----------

#looping statements (for ,while)4
# for loop is used to iterate over a sequence of data/records
# while loop is used until the condition becomes false
import datetime
list_sample=[1,2,'Naveen','xyz']
v_range= range(10)
#for loop
for element in list_sample:
    print(element)
    print(datetime.datetime.now())

print(v_range)
range_data=list(v_range)
print(range_data)

for i in v_range:
    print(i)

# COMMAND ----------

# to calculate the sqaure root values
v_range=range(11)
for i in v_range:
    print(f'current iteration value is {i}')
    i_square=i*i
    print(f'square value of {i} is {i_square}')
else:#Optional block to execute whne no iterations left
    print('Iterations completed')
# print('Iterations completed')

# COMMAND ----------

# while True: # infinite loop
    # print('This is true')

# COMMAND ----------

#while loop
#synatax is while <condition>:
i=0
while i<=10:
    print(i,'This is true')
    i+=1
else: # optional block if while evaluates to false
    print(i,'is no more greater than 10')

# COMMAND ----------

#looping control statements (break(stop the loop),pass(do nothing), continue(skip the iteration))

tuple1=('New York','Chicago','Hyderabad','Bangalore','Mexico')
for i in tuple1:
    if i != 'Hyderabad':
        print(i)
    else:        
        pass
        print('This is my favourite city')
        
        


for i in tuple1:
    if i != 'Hyderabad':
        print(i)
    else:
        continue
        print('This is skipped')
        print('This is my favourite city')


for i in tuple1:
    if i != 'Hyderabad':
        print(i)
    else:
        break
        # pass

print('all loops got executed')

# COMMAND ----------

# nested loop
list1=['Telangana','AP','Tamilnadu','Delhi']
list2=['Hyderabad','Warangal','Chennai','Coimbatore','Vizag','Vijayawada']
list_output=[]
for i in list1:
    for j in list2:
        list_output.append((i,j))
print(list_output)
       

# COMMAND ----------

#iterating over dictionaries
dict1={'name':'Naveen','profession':'engineer','location':'India'}
for i in dict1:
    print('key is :',i)
    print('value is :',dict1[i])
    if i=='location':
        dict1[i]='USA'
print(dict1)
if 'name' in dict1:
    print('value of name key is:', dict1['name'])
else:
    print(f'there is no such key present in the dictionary')

print(dict1.items())

for k,v in dict1.items():
    print(f'key is {k} and value is {v}')



# COMMAND ----------

a=input()
print(a)

# COMMAND ----------

string='abc'
if string:
    print('non empty')
else:
    print('empty')


# COMMAND ----------

a=10
b=2
print(a%b)

# COMMAND ----------

list1=[1,2,2,2,3,4,5,6]
list1.remove(2)
print(list1)

# COMMAND ----------

list_input=[1,2,3,4,4,2,5,3,6]
list_output=[]
for i in list_input:
    if i not in list_output:
        list_output.append(i)
print(list_output)
print(set(list_input))

# COMMAND ----------

