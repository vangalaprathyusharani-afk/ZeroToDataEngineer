# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Magic commands
# MAGIC ## sub heading
# MAGIC * filesystem -%fs (commands to manage the databricks file system(dbfs) and spark cluster filesystem)
# MAGIC * sql - %sql (SQL is to write/execute sql queries from dbfs tables)
# MAGIC * markdown -%md (to wtrie down headings/comments and to skip code block execution)
# MAGIC * run - %run ( used to run a notebook from another notebook)
# MAGIC * dbutils - databricks utility commands
# MAGIC * sh - shell commands to interact with cluster
# MAGIC
# MAGIC ##paragraph 2

# COMMAND ----------

# MAGIC %md
# MAGIC #Change Directory Commands
# MAGIC * . - current directory
# MAGIC * .. - previous directory
# MAGIC * / - root directory

# COMMAND ----------

# MAGIC %sql
# MAGIC -- select 1+1 as sum_num;
# MAGIC -- select current_timestamp();
# MAGIC -- create table mydemotable
# MAGIC -- (
# MAGIC --     id int,
# MAGIC --     name string
# MAGIC -- );
# MAGIC insert into mydemotable values (1, 'John'), (2, 'Mary');

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from mydemotable;

# COMMAND ----------

# MAGIC %run "/Users/flmadeteam@gmail.com/Python Training/utils"

# COMMAND ----------

# MAGIC %run ./utils

# COMMAND ----------

audit_func()

# COMMAND ----------

help(dbutils)

# COMMAND ----------

print('Hello')
notebook_name='/Workspace/Users/flmadeteam@gmail.com/Python Training/utils.ipynb'
dbutils.notebook.run(notebook_name,60)

# COMMAND ----------

dbutils.fs.ls('/databricks-datasets/credit-card-fraud/data/')

# COMMAND ----------

help(dbutils.notebook.run)

# COMMAND ----------

# MAGIC %fs
# MAGIC ls /Workspace/Users/flmadeteam@gmail.com/

# COMMAND ----------

#ls - list the files or directories
#mkdirs - to create a directory
#rm - remove any files or directories
#cp - copy any files from one directory to the other
#mv - move any files between the directories or rename the file in the same directory

# COMMAND ----------

# MAGIC %fs ls dbfs:/FileStore/

# COMMAND ----------

# MAGIC %fs mkdirs dbfs:/FileStore/test_directory/

# COMMAND ----------

# MAGIC %fs mkdirs /Workspace/Ade_training_2026

# COMMAND ----------

# MAGIC %fs mkdirs /Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/

# COMMAND ----------

# MAGIC %fs
# MAGIC ls /Volumes/workspace/default/mydefaultvolume/mtchildfolder/

# COMMAND ----------

# MAGIC %fs
# MAGIC cp /Volumes/workspace/default/mydefaultvolume/mtchildfolder/5_functions.py /Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/

# COMMAND ----------

# MAGIC %fs
# MAGIC rm /Volumes/workspace/default/mydefaultvolume/mtchildfolder/5_functions.py

# COMMAND ----------

# MAGIC %fs
# MAGIC mv /Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/5_functions.py /Volumes/workspace/default/mydefaultvolume/mtchildfolder/

# COMMAND ----------

# MAGIC %fs mv dbfs:/FileStore/abc.txt dbfs:/FileStore/test_directory/

# COMMAND ----------

# MAGIC %fs rm dbfs:/FileStore/test_directory/abc.txt

# COMMAND ----------

# file: is used to acces compute filesystem
#dbfs: is used to access databricks file system
# dbutils.fs.ls('file:/') 
dbutils.fs.ls('dbfs:/')
# dbutils.fs.mv('/FileStore/tables/WordCount_Sample.txt','/FileStore/tables/wordcount.txt')
# dbutils.fs.cp('/FileStore/WordCount_Sample.txt','/FileStore/tables/WordCount_Sample.txt')
# dbutils.fs.rm('/FileStore/tables/WordCount_Sample.txt')
# dbutils.fs.mkdirs('/New_dir/')



# COMMAND ----------

# MAGIC %sql
# MAGIC  select 1*2  as multiplication

# COMMAND ----------

# MAGIC %fs ls file:/tmp/abc.txt

# COMMAND ----------

# MAGIC %fs head /Volumes/workspace/default/mydefaultvolume/mtchildfolder/5_functions.py

# COMMAND ----------

# MAGIC %sh
# MAGIC head /Volumes/workspace/default/mydefaultvolume/mtchildfolder/5_functions.py

# COMMAND ----------

# MAGIC %sh
# MAGIC ls /Volumes/workspace/default/mydefaultvolume/mtchildfolder/

# COMMAND ----------

filepath='/Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/mytextfile.txt'
# dbutils.fs.rm('/Volumes/workspace/default/mydefaultvolume/mtchildfolder/mytextfile.txt')

# COMMAND ----------

# file handling (r,a,x,w)
#r - to open a file in readonly mode
#a - to open a file in append mode
#x - to open a file and create the file if not exits
#w - to overwrite a file
with open(filepath,'w') as write_new_file:
    write_new_file.write("""Hi , I have created a file \nHi, This is second line""")
    write_new_file.write("\n Hi , This is third line")
    write_new_file.close()



# COMMAND ----------

with open(filepath,'w') as write_new_file:
    # write_new_file.writelines("""Hi , I have created a file \nHi, This is second line""")
    write_new_file.writelines("\n Hi , This is new line")
    write_new_file.close()

# COMMAND ----------

# MAGIC %fs head /Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/mytextfile.txt

# COMMAND ----------

filepath='/Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/mysecondtextfile.txt'
# with open(filepath,'x') as w:    
#     w.writelines('Hi , This is the fourth line')
#     w.close()
with open(filepath,'a') as append:    
    append.writelines('\nHi , This is the sixth line')
    append.close()

# COMMAND ----------

# lines = ["Hello\n", "World\n"]
lines="""this is first line\n
this is second line\n
this is third line\n"""
with open(filepath, "w") as f:
    # f.writelines(lines)
    f.write(lines)
    f.close()

# COMMAND ----------

#read() - is to read the entire file data as a string
#readline()- is to read the first line
#readlines() - is used to read all the lines from the file into  a list
#write()- to write the entire data into the file
#writelines() - to write data in a seperate line
#close() - to close the file once read/write operation completes else the file will not have updated info when opened in a seperate command or notebook
with open(filepath,'r') as read_new_file:
    # rom=read_new_file.read()
    rom_list=read_new_file.readlines()
    # read_new_file.write('This is a sample string')
    # print(rom)
    # print(rom_list)
    read_new_file.close()


with open(filepath, "r") as f:
    line1 = f.readline()
    line2 = f.readline()
    print("Line 1:", line1.strip())
    print("Line 2:", line2.strip())


# COMMAND ----------

with open("/tmp/abc.txt", "r") as f:
    lines = f.readlines()    
    print(lines)

# COMMAND ----------

with open('/tmp/abc.txt','a') as write_append_file:
    write_append_file.write("""\n Hi ,This is a third line""")
    # write_new_file.write('Hi , This is second line')
    write_append_file.close()

# COMMAND ----------

with open('/tmp/xyz.txt','x') as write_exists_file:
    write_exists_file.write("""\n Hi ,This is a third line""")
    # write_new_file.write('Hi , This is second line')
    write_exists_file.close()

# COMMAND ----------

# shord hand notation of handling the files
filepath='/Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/myshorttextfile.txt'
t= open(filepath,'w')
t.writelines('\n Hello')
t.close()

# COMMAND ----------

filepath='/Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/mytextfile.txt'
t= open(filepath,'r')
list_read=t.readlines()
for i in list_read:
    print(i)
t.close()

# COMMAND ----------

# MAGIC %fs head /Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/mytextfile.txt

# COMMAND ----------

dbutils.fs.cp('/Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/myshorttextfile.txt','/Volumes/workspace/default/mydefaultvolume/mychildfolder/myshorttextfile23.txt')

# COMMAND ----------

# MAGIC %fs
# MAGIC cp '/Volumes/workspace/default/mydefaultvolume/mysecondchildfolder/myshorttextfile.txt' '/Volumes/workspace/default/mydefaultvolume/mychildfolder/myshorttextfile23.txt'

# COMMAND ----------

# MAGIC %sh
# MAGIC ls /

# COMMAND ----------

