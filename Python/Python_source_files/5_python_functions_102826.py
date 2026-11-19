# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
#Functions (lambda and user defined func)

#function is a reusable block of code to perform some operation with or without a return value
# lambda is a one liner function


# COMMAND ----------

f_lambda= lambda a: a*a
f_lambda(100)
type(f_lambda)

# COMMAND ----------

# lambda_f=lambda a,b: print('a+b is',a+b)
lambda_f=lambda a,b: a+b
var=lambda_f(5,6)
print(var)

# COMMAND ----------

type(lambda_f)

# COMMAND ----------

#function syntax

def func_square(a):
    print('the input variable is:',a)
    a_square=a*a
    return a_square

sqr_root=func_square(10)
print(sqr_root)
# print(a_square)


# COMMAND ----------

func_square(10)

# COMMAND ----------

type(func_square)

# COMMAND ----------

def invoke_function(func_name,a):
    func_name(a)

invoke_function(func_square,10)

# COMMAND ----------

#write a func to get  lists of even values and odd values
def func_even_odd(numbers):
    even_list=[] #The funtion variables cant be accessed outside of the function
    odd_list=[]
    for i in numbers:
        if i%2 ==0:
            even_list.append(i)
        else:
            odd_list.append(i)
    return even_list,odd_list



# COMMAND ----------

print(even_list)

# COMMAND ----------

list1=list(range(50))
# print(list1)
func_even_odd(list1)

# COMMAND ----------

# type(func_even_odd)
func_even_odd(list1)

# COMMAND ----------

e_list,o_list=func_even_odd(list1)
print(o_list)


# COMMAND ----------

#nested function(can call only the parent function whereas inside function will not be callable outside)
def first_func():
    print('This is first func')
    def second_func():
        print('This is inside func')
    second_func()

# first_func()
# second_func() # we cant invoke an child function from a parent function outside of the function


# COMMAND ----------

def add_num(a,b):
    return a+b
# add_num(10,20)
add_num(10,20,30)

# COMMAND ----------

#dynamic argument  functions(*args)

def calc_sum(*args):
    return sum(args)

def dynamic_args(list1,*args):
    for i in args:
        list1.append(i)
    return list1

# COMMAND ----------

list1=[1,2,3]
dynamic_args(list1,10,20,30,40,50)

# COMMAND ----------

# calc_sum(5,10,20,56,78)
# calc_sum(5,-100,500)

# COMMAND ----------

# default argument (arguments will be considered in positional order by default)
def person_details(name,profession,location='India'):
    print(f'name:{name}, profession:{profession}, location:{location}')

# person_details('naveen','engineer')
person_details('naveen','engineer','USA')

# COMMAND ----------

dict_sample={'name':'Naveen','Location':'India'}
dict_sample.items()

# COMMAND ----------

#dynamic key value pair arguments(**kvargs)

def dynamic_kv(**kvargs):
    dict_test={}
    for k,v in kvargs.items():        
        print(f'key is {k}')
        print(f'Value is {v}')
        dict_test[k]=v
    return dict_test

my_dict=dynamic_kv(name='Naveen',profession='engineer',location='Hyderabad',phone='888888888')
print(my_dict)
type(my_dict)

# COMMAND ----------

for k,v in dict_sample.items():
    print(f'key is {k}')
    print(f'value is {v}')

# COMMAND ----------

dynamic_kv(name='Naveen',profession='engineer',location='Hyderabad',phone='888888888')

# COMMAND ----------

def dynamic_kv(**kevvars):
    dict_test={}
    for k,v in kevvars.items():        
        print(f'key is {k}')
        print(f'Value is {v}')
        dict_test[k]=v
    return dict_test

my_dict=dynamic_kv(name='Naveen',profession='engineer',location='Hyderabad',phone='888888888')
print(my_dict)
type(my_dict)

# COMMAND ----------

