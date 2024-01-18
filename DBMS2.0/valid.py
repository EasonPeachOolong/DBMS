import os
import re

def validDB(dbname,username):
    if os.path.exists(dbname):
        return [0,"数据库已存在，请更换数据库名称。"]
    else:
        if username == 'admin':
            return [1,"数据库创建成功！"]
        with open("system.users", "r") as file:
            for line in file:
                line = line.split()
                if line[0] == username:
                    if int(line[2]) == 1:
                        return [1,"数据库创建成功！"]
                    else:
                        return [0,"您没有创建数据库的权限！"]

def validType(targetType,context):
    context = str(context)
    if targetType == 'INT':
        pattern = r'[^-\d~]'  # 匹配除了负号、~和数字字符以外的任意字符
        if re.search(pattern, context):
            return [0,"数据类型不匹配！"]
    return [1]

def validNull(isNull,context):#context='a'
    if str(isNull) == '0':
        if context == '~':
            return [0,"部分字段不得为空！"]
    return [1]

def findFK(dbname,tableName): #找到该表的所有外码
    if os.path.exists(dbname+'/'+dbname+'.mydb'):
        with open (dbname+'/'+dbname+'.mydb','r') as file:
            start = False
            fks = []
            for line in file:
                if line[0:2] == '##' and line[2:len(line)-1] == tableName:
                    start = True
                    continue
                if start:
                    if line[0:2] == '##':
                        break
                    if line[0] == '*':
                        line = line.split()
                        fks.append([line[1],line[2],line[3]])
    return fks

#验证所有数据是否满足外码约束
def validFK(dbname,fks,contents): #fks=[[local_name,refer_table,refer_name],[..]]  contents=[[local_name,value1,value2,..],[..]]
    for content in contents:   #只能单列绑定单列外码
        for fk in fks:
            if content[0] == fk[0]:
                with open (dbname+'/'+dbname+'.mydb','r') as file:
                    start = False
                    num = 0
                    for line in file:
                        if line[0:2] == '##' and line[2:len(line)-1] == fk[1]:
                            start = True
                            continue
                        if start:
                            if line[0:2] == '##' or line[0] == '*':
                                break
                            elif line.split()[0] == fk[2]:
                                break
                            num = num + 1
                with open (dbname+'/'+fk[1]+'.table','r') as file:
                    exist = []
                    for line in file:
                        exist.append(line.split()[num])
                    for i in range(1,len(content)):
                        if str(content[i]) not in exist and content[i] != '~':
                            return [0,"部分值不符合外码约束"]
    return [1] 

def findPK(dbname,tableName):  #找到所有主码
    if os.path.exists(dbname+'/'+dbname+'.mydb'):
        with open (dbname+'/'+dbname+'.mydb','r') as file:
            start = -1
            pks = []
            for line in file:
                if line[0:2] == '##' and line[2:len(line)-1] == tableName:
                    start = start + 1
                    continue
                if start >= 0:
                    if line[0:2] == '##' or line[0] == '*':
                        break
                    line = line.split()
                    if line[3] == '1':
                        pks.append([line[0],start])
                    start = start + 1
    return pks

#验证数据是否符合主码约束
def validPK(dbname,tableName,pks,contents):   #pks = [[column_name, order],[...]]  contents=[[local_name,value1,value2,..],[..]]  
    records = [] #组成记录集合
    for i in range(1,len(contents[0])):
        pair = []
        for pk in pks:
           pair.append(str(contents[pk[1]][i])) #############
        records.append(pair)
    unique = []
    for record in records:
        if record not in unique:
            unique.append(record)
    if len(unique) != len(records):
        return [0,"部分值不符合主码约束"]
    if os.path.exists(dbname+'/'+tableName+'.table'):
        with open (dbname+'/'+tableName+'.table','r') as file:
            for line in file:
                pair = []
                line = line.split()
                for pk in pks:
                    pair.append(line[pk[1]])        
                if pair in records:
                    return [0,"部分值不符合主码约束"]
    return [1]

def ValidTableName(dbname,tableName):
    if os.path.exists(dbname+'/'+dbname+'.mydb'):
        with open (dbname+'/'+dbname+'.mydb','r') as file:
            namelist = []
            for line in file:
                if line[0:2] == '##' :
                    namelist.append(line[2:len(line)-1])
        if tableName in namelist:
            return [0,"该表名已存在"]
        return [1]

def validPrivilege(type,user,dbname):
    if os.path.exists(dbname+'/'+dbname+'.privilege'):
        if user == 'admin':
            if type == 0:   
                return [1,"正在使用"+dbname+"数据库"]
            return [1]
        privilege = []
        with open (dbname+'/'+dbname+'.privilege','r') as file:
            for line in file:
                line = line.split()
                if line[0] == user:
                    privilege = line
                    break
        if type == 0:#访问数据库
            if len(privilege) > 1 and int(privilege[15]) == 1:
                return [1,"正在使用"+dbname+"数据库"]
            else: return [0,"您没有访问该数据库的权限"]

        if len(privilege) > 1 and int(privilege[type]) == 1:
            return [1]
        else:
            if type == 1: #建表
                return [0,"您没有建立关系表的权限"]
            elif type == 2: #修改表
                return [0,"您没有修改关系表的权限"]
            elif type == 3: #删表
                return [0,"您没有删除关系表的权限"]
            elif type == 4: #插入
                return [0,"您没有INSERT的权限"]
            elif type == 5: #修改
                return [0,"您没有UPDATE的权限"]
            elif type == 6: #删除
                return [0,"您没有DELETE的权限"]
            elif type == 7: #select
                return [0,"您没有SELECT的权限"]
            elif type == 8: #创建视图
                return [0,"您没有建立视图的权限"]
            elif type == 9: #删除视图
                return [0,"您没有删除视图的权限"]
            elif type == 10: #创建索引
                return [0,"您没有创建索引的权限"]
            elif type == 11: #删除索引
                return [0,"您没有删除索引的权限"]
            elif type == 12: #grant（首先自己要有某项权限）
                return [0,"您没有grant的权限"]
            elif type == 13: #revoke
                return [0,"您没有revoke的权限"]
            elif type == 14: #drop
                return [0,"您没有drop的权限"]
                