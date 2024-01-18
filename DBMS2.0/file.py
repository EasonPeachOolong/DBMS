import os
import valid
import shutil
from fulltext import full_text_search
#文件特殊字符一览：mydb文件中，#表示首行节点，列举用户权限；##表示表定义节点，*表示外码节点，table文件中~表示值为NULL
#本文件中大部分内容仅实现确定功能，不涉及验证格式及名称查重，在其他函数中验证后调用下方函数 
def createdb(dbname,user):
    os.mkdir(dbname)
    filename = str(dbname)+".mydb"
    with open(dbname+'/'+filename, "w") as file:
        file.write("#"+ user + "\n")   #首行为用户列表
    with open(dbname+'/'+str(dbname)+".privilege", "w") as file:
        file.write(user + " 1 1 1 1 1 1 1 1 1 1 1 1 1 1\n")
        #权限：建表、修改表、删表、插入、修改、删除、select、创建视图、删除视图、创建索引、删除索引、grant（首先自己要有某项权限）、revoke

def createTable(tableName,contents,fks,dbname):
    path = dbname +'/' + dbname + '.mydb'
    if os.path.exists(path):
        #contents = [[column_name, type, null, primary_key, foreign_key],[...]] 表基础
        lines = []
        lines.append("##" + tableName + '\n')
        for row in contents:
            string = row[0] +' '+ row[1].upper() +' '+ str(row[2]) +' '+ str(row[3]) +' '+ str(row[4]) + '\n'
            lines.append(string)
        # fks = [[fk_name, local_name, referTable, refer_name],[...]]  外码
        for fk in fks:
            string = "*" + fk[0] + " " + fk[1] + " " + fk[2] + " " + fk[3] + '\n'
            lines.append(string)
        #print(lines)
        with open(path, "a") as file:
            file.writelines(lines)
    path = dbname + '/' + tableName + '.table' 
    with open(path, "w") as file:  #创建空表
        pass

def alterTable(tableName,contents,dbname): #大体同createTable
    path = dbname +'/' + dbname + '.mydb'
    if os.path.exists(path):
        pass#未完成

def insert(dbname,tableName, contents): #contents[][0]:columnName, contents[][1:]:value
    path = dbname + '/' + tableName + '.table'
    if os.path.exists(path):
        dbpath = dbname +'/' + dbname + '.mydb'
        with open(dbpath, "r") as file:
            start = False
            columnOrder = []  #将mydb文件中该表的定义信息取出
            for line in file:
                if line[0:2] == '##' and line[2:len(line)-1] == tableName:
                    start = True
                    continue
                if start:
                    if line[0] == '#' or line[0] == '*':
                        break
                    columnOrder.append(line.split())
            #按照表设计的字段顺序填入
            column_order = {column[0]: index for index, column in enumerate(columnOrder)}
            sorted_contents = sorted(contents, key=lambda x: column_order.get(x[0]))
            #有一整列为NULL，补null列（特殊符号~）
            if len(sorted_contents) < len(columnOrder): 
                for i in range(len(columnOrder)):
                    if i>=len(sorted_contents):
                        sorted_contents.append([columnOrder[i][0]])
                        for j in range(1,len(contents[0])):
                            sorted_contents[i].append('~')
                    elif sorted_contents[i][0] != columnOrder[i][0]:
                        sorted_contents.insert(i,[columnOrder[i][0]])
                        for j in range(1,len(contents[0])):
                            sorted_contents[i].append('~')
            #print(sorted_contents) 
        #检验数据类型、是否可空、外码约束、主键约束
        flag = 1
        for i in range(len(sorted_contents)):
            if flag == 1:
                for j in range(1,len(sorted_contents[i])):
                    type_check = valid.validType(columnOrder[i][1].upper(),sorted_contents[i][j])
                    null_check = valid.validNull(columnOrder[i][2],sorted_contents[i][j])
                    if type_check[0] == 0 or null_check[0] == 0:
                        flag = 0
                        break
        if type_check[0] == 0:
            return type_check[1] #信息可传入ui
            
        if null_check[0] == 0:
            return null_check[1] #信息可传入ui
            
        fks = valid.findFK(dbname,tableName)
        fk_check = valid.validFK(dbname,fks,sorted_contents)
        if fk_check[0] == 0:
            return fk_check[1] #信息可传入ui
            
        pks = valid.findPK(dbname,tableName)
        pk_check = valid.validPK(dbname,tableName,pks,sorted_contents)
        if pk_check[0] == 0:
            return pk_check[1] #信息可传入ui
             
        #写入table文件
        with open(path, "a") as file:
            lines = []
            for i in range(1, len(sorted_contents[0])):
                string = ""
                length = len(sorted_contents)
                for j in range(length):
                    if j != length - 1 :
                        string = string + str(sorted_contents[j][i]) + ' ' #要考虑到NULL，用特殊字符~表示，在本函数前完成
                    else:
                        string = string + str(sorted_contents[j][i]) + '\n'
                lines.append(string)
            file.writelines(lines)
        return "数据插入成功！"  #信息可传入ui

def select(dbname,select_part,from_part,where_part):
    #先取出对应表的数据
    all_contents = [] #全部的数据，包含表名.属性名与属于该属性的所有值
    table_len = [] #储存各个表的记录数量
    attr_num = [] #储存各个表的属性数量
    attr_name = [] #储存表名.属性名
    for tableName in from_part:
        if os.path.exists(dbname+'/'+dbname+'.mydb'):
            with open (dbname+'/'+dbname+'.mydb','r') as file:
                contents_part = []
                start = False
                for line in file:
                    if line[0:2] == '##' and line[2:len(line)-1] == tableName:
                        start = True
                        continue
                    if start:
                        if line[0:2] == '##' or line[0] == '*':
                            break
                        contents_part.append([tableName + '.' + line.split()[0]])
                        attr_name.append(tableName + '.' + line.split()[0])
                    
        if os.path.exists(dbname+'/'+tableName+'.table'):
            with open (dbname+'/'+tableName+'.table','r') as filet:
                record = ""
                for record in filet:
                    record = record.split()
                    for i in range(len(record)):
                        contents_part[i].append(record[i])
                attr_num.append(len(record))
        else: return [0,"不存在该表"]   #不存在该表
        for content in contents_part:
            all_contents.append(content)
        table_len.append(len(all_contents[-1])-1)
    #print(all_contents)
    #print(table_len)
    #print(attr_num)
    #print(attr_name)
    #对没有声明来源表的属性进行判断和补充
    select_all = False
    for i in range(len(select_part)):
        select_part[i] = select_part[i].split('.')
        if len(select_part[i]) == 1:
            if select_part[i][0] == '*': #全部
                select_all = True
                break
            else:
                found = False #只允许找到一次
                for name in attr_name:
                    if name.split('.')[1] == select_part[i][0]: 
                        if not found:  #表名相同且首次找到
                            found = True
                            select_part[i].insert(0,name.split('.')[0])
                        else:  #表名相同且再次找到，说明select语句含义不明
                            return [0,"select对象指代不明"]
                if not found:
                    return [0,"该表中没有此属性！"]
        else:
            found = False
            for name in attr_name:
                if name == select_part[i][0] + '.' +select_part[i][1]:
                    found = True
            if not found:
                return [0,"该表中没有此属性！"]
    #开始链接
    contents = []
    tackle_result = tackle_where_part(where_part,attr_name)
    if tackle_result[0] == 0:
        return tackle_result
    condi = tackle_result[0]#值比较 example:  [[">",0,"a",2],["=",0,"v",3]] #a表示为属性、v表示为值,均用于定义操作符后的部分的类型
    other_condi = tackle_result[1] #IN 与 NOT IN
    match_condi = tackle_result[2] #match

    #dfs链接，判断是否符合条件
    result = dfs_select(table_len, attr_num, [], 0, all_contents,condi,other_condi)
    result = [result[i:i+len(all_contents)] for i in range(0, len(result), len(all_contents))]
    #判断match条件
    documents = []
    for condi in match_condi:
        for res in result:
            documents.append({'content':res[condi[0]]})
        matched = full_text_search(condi[1],documents)
        new_result = []
        for sub,res in enumerate(result):
            if sub in matched:
                new_result.append(res)
        result = new_result
    #print(result)
    #执行select选取合适列
    contents = []
    if select_all:
        select_part = attr_name
    for attr in select_part:
        for sub, name in enumerate(attr_name):
            #print(sub,name,attr[0]+attr[1])
            if (not select_all and name == attr[0]+'.'+attr[1]) or (select_all and name == attr):
                temp = [name]
                for res in result:
                    temp.append(res[sub])
                contents.append(temp)
    #print(contents)
    return contents

def dfs_select(table_len, attr_num, current_dfs, current_table, all_contents,condi,other_condi):
    #各个table的记录数列表、各个table的属性个数、当前的记录、当前表的下标、全部内容、约束、其他约束 
    if current_table == len(table_len):
        return current_dfs  # 将当前的current_dfs作为一个列表返回
    else:
        result = []  # 用于保存正确的结果
        for i in range(1, table_len[current_table] + 1):
            for _ in range(attr_num[current_table]):
                current_dfs.append(all_contents[len(current_dfs)][i])
            #检查是否符合等值约束
            if judgeCondition(current_dfs,condi,other_condi): #到目前为止还符合约束，进入下一张表的链接
                current_len = len(current_dfs)
                # 递归调用，并将返回的多个current_dfs列表添加到结果中
                result.extend(dfs_select(table_len, attr_num, current_dfs, current_table + 1, all_contents,condi,other_condi))
                for _ in range(current_len, len(current_dfs)):
                    current_dfs.pop()
            for _ in range(attr_num[current_table]):
                current_dfs.pop()
        return result

def tackle_where_part(where_part,attr_name):
    condi = []
    other_condi = []
    match_condi = []
    for condition in where_part: 
        pro = "" #暂存操作符
        condition = condition.split('=')
        if (len(condition) > 1): #此时可能为等值连接，或是值比较
            if (condition[0][-1] not in ['>','<','!']) :
                pro = "="
            else: #此时为值比较，分为属性与值（int、char）、属性与属性
                if condition[0][-1] == '>': # >= 
                    pro = ">="
                elif condition[0][-1] == '<': # <=
                    pro = "<="
                elif condition[0][-1] == '!': # !=
                    pro = "!="
            condition = condition[0] + '=' + condition[1] #还原为字符串
        else:  #此时为IN 与 NOT IN、> 、< MATCH
            condition = condition[0] #还原回字符串
            if len(condition.split('>')) > 1: # >
                pro = ">"
            elif len(condition.split('<')) > 1: # <
                pro = "<"
            elif len(condition.split('IN')) > 1: #IN /NOT IN
                if 'NOT' in condition.split(' '): # NOT IN
                    pro = " NOT IN "
                else: pro = " IN " # IN
                condition = condition.split(pro)
                condition[0] = condition[0].replace(' ','')
                condition[1] = condition[1].replace(' ','')[1:-1].split(',')
                #print(condition)
                if len(condition[0].split('.')) == 1: #补齐表名
                    found = False #只允许找到一次
                    for name in attr_name:
                        if name.split('.')[1] == condition[0]: 
                            if not found:  #表名相同且首次找到
                                found = True
                                condition[0]= name.split('.')[0] + "." +condition[0]
                            else:  #表名相同且再次找到，说明where语句含义不明
                                return [0,"where对象指代不明。"]
                    if not found:
                        return [0,"表中不存在where中指代的对象！"]
                for index,name in enumerate(attr_name):
                    if name == condition[0]:
                        break
                if index == len(attr_name)-1 and attr_name[index] != condition[0]:
                    return [0,"表中不存在where中指代的对象！"]
                if pro == " NOT IN ":
                    other_condi.append(['NOTIN',index,condition[1]])
                else: other_condi.append(['IN',index,condition[1]])
            else: # MATCH
                condition = condition.split()
                if len(condition[1].split('.')) == 1: #补齐表名
                    found = False #只允许找到一次
                    for name in attr_name:
                        if name.split('.')[1] == condition[1]: 
                            if not found:  #表名相同且首次找到
                                found = True
                                condition[1]= name.split('.')[0] + "." +condition[1]
                            else:  #表名相同且再次找到，说明where语句含义不明
                                return [0,"where对象指代不明。"]
                    if not found:
                        return [0,"表中不存在where中指代的对象！"]
                for index,name in enumerate(attr_name):
                    if name == condition[1]:
                        break
                if index == len(attr_name)-1 and attr_name[index] != condition[1]:
                    return [0,"表中不存在where中指代的对象！"]
                match_condi.append([index,condition[3]])
                #print(match_condi)

        if pro in [">","<","!=",">=","<=","="]:  #集中处理，节省空间
            condition = condition.split(pro)
            #print(condition)
            pair = [pro]
            if len(condition[0].split('.')) == 1: #去找到列号
                found = False #只允许找到一次
                for sub,name in enumerate(attr_name):
                    if name.split('.')[1] == condition[0]: 
                        if not found:  #表名相同且首次找到
                            found = True
                            pair.append(sub)
                        else:  #表名相同且再次找到，说明where语句含义不明
                            return [0,"where对象指代不明。"]
            else:
                found = False #只允许找到一次
                for sub,name in enumerate(attr_name):
                    if name == condition[0]: 
                        if not found:  #表名相同且首次找到
                            found = True
                            pair.append(sub)
                        else:  #表名相同且再次找到，说明where语句含义不明
                            return [0,"where对象指代不明。"]               
            if not found:
                return [0,"表中不存在where中指代的对象！"]

            if len(condition[1].split(".")) == 1: #此时可能后方为值、或者为不齐的列名
                if condition[1][0] == condition[1][-1] == "'":
                    pair.append("v")
                    pair.append(condition[1][1:-1])
                else:
                    found = False #只允许找到一次
                    for index,name in enumerate(attr_name):
                        if name.split('.')[1] == condition[1]: 
                            if not found:  #表名相同且首次找到
                                found = True
                                pair.append("a")
                                pair.append(index)
                            else:  #表名相同且再次找到，默认为值
                                pair[2] = "v"
                                pair[3] = condition[1]
                                break
                    if not found:
                        pair.append("v")
                        if condition[1].upper() != "NULL":
                            pair.append(condition[1])
                        else: pair.append("~")
                condi.append(pair)
            else: #此时后方一定为完整表+列名
                found = False #只允许找到一次
                for index,name in enumerate(attr_name):
                    if name == condition[1]: 
                        if not found:  #表名相同且首次找到
                            found = True
                            pair.append("a")
                            pair.append(index)
                        else:  #表名相同且再次找到，默认为值
                            pair[2] = "v"
                            pair[3] = condition[1]
                            break
                if not found:
                    pair.append("v")
                    pair.append(condition[1])
                condi.append(pair)
    return [condi,other_condi,match_condi]

def judgeCondition(content,condi,other_condi):
    flag = True
    for con in condi:  #condi = [[">",0,"a",2],["=",0,"v",3]]
        if con[1] >= len(content) or (con[2] == "a" and con[3] >= len(content)):
            continue
        if con[0] == ">":
            if con[2] == "a":
                if content[con[1]] <= content[con[3]]:
                    flag = False
            else:
                if content[con[1]] <= int(con[3]):
                    flag = False
        elif con[0] == "<":
            if con[2] == "a":
                if content[con[1]] >= content[con[3]]:
                    flag = False
            else:
                if content[con[1]] >= int(con[3]):
                    flag = False
        elif con[0] == "=":
            if con[2] == "a":
                if content[con[1]] != content[con[3]]:
                    flag = False
            else:
                if content[con[1]] != con[3]:
                    flag = False
        elif con[0] == "!=":
            if con[2] == "a":
                if content[con[1]] == content[con[3]]:
                    flag = False
            else:
                if content[con[1]] == con[3]:
                    flag = False
        elif con[0] == ">=":
            if con[2] == "a":
                if content[con[1]] < content[con[3]]:
                    flag = False
            else:
                if content[con[1]] < int(con[3]):
                    flag = False
        if con[0] == "<=":
            if con[2] == "a":
                if content[con[1]] > content[con[3]]:
                    flag = False
            else:
                if content[con[1]] > int(con[3]):
                    flag = False
    for con in other_condi: #other_condi = [["NOTIN",2,[value1,value2,value3]],["IN",1,[value1,value2,value3]]]
        if con[0] == "NOTIN":
            if content[con[1]] in con[2]:
                flag = False
        else:
            if content[con[1]] not in con[2]:
                flag = False
    return flag

def update(dbname,tableName,values,where_part):
    if os.path.exists(dbname+'/'+dbname+'.mydb'): #取出外码约束，表结构
        with open (dbname+'/'+dbname+'.mydb','r') as file:
            start = False
            columnOrder = []  #将mydb文件中该表的定义信息取出
            fks = [] #外码
            attr_name = [] #储存表名.属性名
            for line in file:
                if line[0:2] == '##' and line[2:len(line)-1] == tableName:
                    start = True
                    continue
                if start:
                    if line[0] == '#':
                        break
                    elif line[0] == '*':
                        line = line.split()
                        fks.append([line[1],line[2],line[3]])
                    else:
                        columnOrder.append(line.split())
                        attr_name.append(tableName + '.' + line.split()[0])
           
        for sub,value in enumerate(values):
            for index, col in enumerate(columnOrder):
                if index == len(columnOrder)-1 and col[0] != value[0]:
                    return "表中不存在set中指代的对象！"
                if col[0] == value[0]:
                    if value[1].upper() == "NULL":
                        values[sub][1] = '~'
                    #检查数据类型
                    if not(valid.validType(col[1],value[1])[0] == 1 or value[1].upper() == "~"):
                        return "set赋值数据类型错误！"
                    #检查是否可为空
                    if valid.validNull(col[2],value[1])[0] == 0:
                        return "set赋值数据部分不可为空！"
                    values[sub][0] = index
                    break

        tackle_result = tackle_where_part(where_part,attr_name)
        if tackle_result[0] == 0:
            return tackle_result[1]
        #print(tackle_result)
        condi = tackle_result[0]#值比较 example:  [[">",0,"a",2],["=",0,"v",3]] #a表示为属性、v表示为值,均用于定义操作符后的部分的类型
        other_condi = tackle_result[1] #IN 与 NOT IN
        match_condi = tackle_result[2] #match

    if os.path.exists(dbname+'/'+tableName+'.table'): #取出数据
        with open (dbname+'/'+tableName+'.table','r') as file:
            contents = file.readlines()
        for index,content in enumerate(contents):
            contents[index] = content.split()
        #通过match条件挑出要修改的行号
        documents = []
        for condi in match_condi:
            for content in contents:
                documents.append({'content':content[condi[0]]})
            matched = full_text_search(condi[1],documents)
        #通过值判断与in/not in得出要修改的行   
        matched2 = []    
        for sub, content in enumerate(contents):
            if judgeCondition(content,condi,other_condi):
                matched2.append(sub)
        #print(len(condi) + len(other_condi))
        if (len(condi) + len(other_condi) > 0) and (len(match_condi) > 0):
            adjusted = list(set(matched) & set(matched2))
        elif (len(condi) + len(other_condi) > 0):
            adjusted = matched2
        else: adjusted = matched
        #print(adjusted)
        #尝试修改
        for sub, content in enumerate(contents):
            if sub in adjusted:
                for value in values:
                    contents[sub][value[0]] = value[1]
        #验证主键、外码约束
        temp_contents = [[name.split('.')[1]] for name in attr_name]
        for i in range(len(attr_name)):
            for j in range(len(contents)):
                temp_contents[i].append(contents[j][i])
        #print(temp_contents)
        pks = valid.findPK(dbname,tableName)
        records = [] #组成只有主码的记录集合
        for content in contents:
            pair = []
            for pk in pks:
                pair.append(str(content[pk[1]]))
            records.append(pair)
        unique = []
        for record in records:
            if record not in unique:
                unique.append(record)
        if len(unique) != len(records):
            return "修改后结果不符合主码约束！"
        if valid.validFK(dbname,fks,temp_contents)[0] == 0:
            return "修改后结果不符合外码约束！"
        #验证其他表的外码参照是否会出错（即外码为restrict类型）
        other_fks = []  #被参照的属性（当前update的表）、参照的表名、参照的属性名
        index = []
        with open (dbname+'/'+dbname+'.mydb','r') as file:
            for line in file:
                if line[0:2] == "##":
                    index = []
                    referTableName = line[2:len(line)-1]
                elif line[0] == '*':
                    line = line.split()
                    if line[2] == tableName:
                        for ind in index:
                            if line[1] == ind[0]:
                                other_fks.append([line[3],referTableName,ind[1]])
                else: index.append([line.split()[0],len(index)])
        #print(other_fks)
        for fk in other_fks:
            with open (dbname+'/'+fk[1]+'.table','r') as file:
                for line in file:
                    found = False
                    line = line.split()
                    for index, name in enumerate(attr_name): #找到本Table中的列号index（被参照属性）
                        if name.split('.')[1] == fk[0]:
                            break
                    for content in contents:
                        if line[fk[2]] == content[index]:
                            found = True
                    if found == False:
                        return "此修改受其他表外码的约束，无法进行。"

        for i in range(len(contents)):
            contents[i] = ' '.join(contents[i]) + '\n'
        #print(contents)
        with open (dbname+'/'+tableName+'.table','w') as file:
            for content in contents:
                file.write(content)
        return f"{len(adjusted)}行数据已修改。"

def delete(dbname,tableName,where_part):
    if os.path.exists(dbname+'/'+dbname+'.mydb'): #取出外码约束，表结构
        with open (dbname+'/'+dbname+'.mydb','r') as file:
            start = False
            columnOrder = []  #将mydb文件中该表的定义信息取出
            fks = [] #外码
            attr_name = [] #储存表名.属性名
            for line in file:
                if line[0:2] == '##' and line[2:len(line)-1] == tableName:
                    start = True
                    continue
                if start:
                    if line[0] == '#':
                        break
                    elif line[0] == '*':
                        line = line.split()
                        fks.append([line[1],line[2],line[3]])
                    else:
                        columnOrder.append(line.split())
                        attr_name.append(tableName + '.' + line.split()[0])

        tackle_result = tackle_where_part(where_part,attr_name)
        if tackle_result[0] == 0:
            return tackle_result[1]
        #print(tackle_result)
        condi = tackle_result[0]#值比较 example:  [[">",0,"a",2],["=",0,"v",3]] #a表示为属性、v表示为值,均用于定义操作符后的部分的类型
        other_condi = tackle_result[1] #IN 与 NOT IN
        match_condi = tackle_result[2] #match

    if os.path.exists(dbname+'/'+tableName+'.table'): #取出数据
        with open (dbname+'/'+tableName+'.table','r') as file:
            contents = file.readlines()
        for index,content in enumerate(contents):
            contents[index] = content.split()
        #通过match条件挑出要修改的行号
        documents = []
        for condi in match_condi:
            for content in contents:
                documents.append({'content':content[condi[0]]})
            matched = full_text_search(condi[1],documents)
        #通过值判断与in/not in得出要修改的行   
        matched2 = []    
        for sub, content in enumerate(contents):
            if judgeCondition(content,condi,other_condi):
                matched2.append(sub)
        #print(len(condi) + len(other_condi))
        if (len(condi) + len(other_condi) > 0) and (len(match_condi) > 0):
            adjusted = list(set(matched) & set(matched2))
        elif (len(condi) + len(other_condi) > 0):
            adjusted = matched2
        else: adjusted = matched
        #print(adjusted)
        #尝试修改
        for sub, content in enumerate(contents):
            if sub in adjusted:
                contents[sub] = []
        for sub, content in enumerate(contents):
            if content == []:
                del contents[sub]
        #验证其他表的外码参照是否会出错（即外码为restrict类型）
        other_fks = []  #被参照的属性（当前update的表）、参照的表名、参照的属性名
        index = []
        with open (dbname+'/'+dbname+'.mydb','r') as file:
            for line in file:
                if line[0:2] == "##":
                    index = []
                    referTableName = line[2:len(line)-1]
                elif line[0] == '*':
                    line = line.split()
                    if line[2] == tableName:
                        for ind in index:
                            if line[1] == ind[0]:
                                other_fks.append([line[3],referTableName,ind[1]])
                else: index.append([line.split()[0],len(index)])
        #print(other_fks)
        for fk in other_fks:
            with open (dbname+'/'+fk[1]+'.table','r') as file:
                for line in file:
                    found = False
                    line = line.split()
                    for index, name in enumerate(attr_name): #找到本Table中的列号index（被参照属性）
                        if name.split('.')[1] == fk[0]:
                            break
                    for content in contents:
                        if line[fk[2]] == content[index]:
                            found = True
                    if found == False:
                        return "此删除受其他表外码的约束，无法进行。"

        for i in range(len(contents)):
            contents[i] = ' '.join(contents[i]) + '\n'
        #print(contents)
        with open (dbname+'/'+tableName+'.table','w') as file:
            for content in contents:
                file.write(content)
        return f"{len(adjusted)}行数据已删除。"

# FOR DROP DATABASE
def drop_db(dbname):
    if os.path.exists(dbname):
        shutil.rmtree(dbname, ignore_errors=True)

    if not os.path.exists(dbname):
        return 1

# FOR DROP TABLE
def drop_table(tableName, dbname):
    drop_table_valid = 1
    if os.path.exists(dbname+'/'+tableName+'.table'):
        with open(dbname + '/' + dbname + '.mydb', 'r') as file:
            lines = file.readlines()
        start_index = end_index = None
        for i, line in enumerate(lines):
            if line[0:2] == '##' and line[2:len(line) - 1] == tableName and start_index is None:
                start_index = i
            elif line[0:3] == '*fk' and tableName in line:
                drop_table_valid = 0
            elif line[0:2] == '##' and start_index is not None and i > start_index:
                end_index = i
                break
        if drop_table_valid == 1:
            # 删除.table文件
            os.remove(dbname + '/' + tableName + '.table')

        # 确保找到了开始和结束标记
        if start_index is not None and end_index is not None and drop_table_valid == 1:
            # 删除从 ##table 到 下一个 ## 之间的行
            del lines[start_index:end_index]

            # 重写文件
            with open(dbname + '/' + dbname + '.mydb', 'w') as file:
                file.writelines(lines)

        if not os.path.exists(dbname+'/'+tableName+'.table'):
            return 1


def get_users_password():
    with open('system.users', 'r') as file:
        # 读取所有行
        lines = file.readlines()
        result_dict = {}
        # 从第二行开始遍历
        for line in lines[1:]:
            split_result = line.split()
            result_dict[split_result[0]] = split_result[1]
    return result_dict
#注册界面用，往system.user里面添加用户名和密码
def add_user_password(username,password):
    with open('system.users', 'a') as file:
        new_data =  '\n' + username + ' ' + password + ' 0 0 0 0'
        file.write(new_data)
#获得制定数据库里的所有表的属性，用列表返回
#[['table1', ['a', 'INT', '0', '1', '0'], ['b', 'CHAR', '0', '1', '0'], ['c', 'INT', '1', '0', '0']]]
def get_all_table_attribute(database_name):
    database_folder_path = os.path.dirname(os.path.abspath(__file__))
    all_atrrtibute_path = os.path.join(database_folder_path, database_name,database_name + '.mydb')
    with open(all_atrrtibute_path,'r')as file:
        file_content = file.read()
    result = []
    current_table = None
    current_columns = []

    lines = file_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#admin') or not line:
            continue
        elif line.startswith('##'):
            if current_table is not None:
                result.append([current_table] + current_columns)
            current_table = line[2:]
            current_columns = []
        elif line.startswith('*fk'):
            continue
            # foreign_key_parts = line.split()
            # current_columns.append(foreign_key_parts)
        else:
            column_parts = line.split()
            current_columns.append(column_parts)

    if current_table is not None:
        result.append([current_table] + current_columns)

    all_table_attribute = []
    for table_info in result:
        table_name = table_info[0]
        columns = [table_name]
        for column_info in table_info[1:]:
            if len(column_info) > 1:
                columns.append(column_info)
            else:
                columns.extend(column_info)
        all_table_attribute.append(columns)
    return all_table_attribute
    
def get_all_fk(db_name):
    database_folder_path = os.path.dirname(os.path.abspath(__file__))
    all_fk_path = os.path.join(database_folder_path, db_name,db_name + '.mydb')
    result_list = []
    with open(all_fk_path, 'r') as file:
        for line in file:
            temp_list = []
            # 去除行末尾的换行符
            line = line.strip()
            if line.startswith("##"):
                # 如果是以 '##' 开头，则将其内容插入到下一个以 '*' 开头的行前
                table_name = line[2:]
            elif line.startswith('*'):
                # 如果是以 '*' 开头，则将当前行添加到结果列表，并重置当前行
                temp_list.append(table_name)
                temp_list.append(line)
                result_list.append(temp_list)
                temp_list = []
            else:
                continue
    return result_list    

def drop_column(dbname,tableName,column_name):
    if os.path.exists(dbname+'/'+dbname+'.mydb'): #取出外码约束，表结构
        all_fk = []
        for i in get_all_fk(dbname):
            print(i)
            used_table_list = []
            used_table_list.append(i[1].split()[2])
        print(used_table_list)
        
        

        #从所有属性中获得待删除一行
        # all_attributre = get_all_table_attribute(dbname)
        # for i in all_attributre:
        #     if i[0] == tableName:
        #         table_attribute = i[1:]
        #         for j in table_attribute:
        #             if j[0] == column_name:
        #                 to_drop_line = ' '.join(j)
        #                 to_drop_line = to_drop_line + '\n'#获得要删除一行
        #                 # print(to_drop_line)
                        
        # flag = False#设置标志位，若遇到当前的表，就准备开始删除
        # with open (dbname+'/'+dbname+'.mydb','r') as file:        
        #     line = file.readlines()
        # for index,each_line in enumerate(line):  
        #     if each_line == "##" + tableName + "\n":
        #         flag = True
        #     if flag and each_line == to_drop_line:
        #         del line[index]
        #         break
        # with open(dbname+'/'+dbname+'.mydb', 'w') as file:
        #     file.writelines(line)                 
                    
            
"""
#admin
##table1
a INT 0 1 0
b CHAR 0 1 0
c INT 1 0 0
##table2
a INT 0 1 1
b CHAR 0 1 0
*fk a table1 a
##table3
a INT 0 1 1
b CHAR 1 0 0
*fk a table1 a
"""


#createdb("nihao","admin")
#createTable("table1",[['a','int',0,0,1,0],['b','char',0,0,1,0]],[],"nihao")
#createTable("table2",[['a','int',0,0,1,0],['b','char',0,0,1,0]],[['fk','a','table1','a']],"nihao")
#insert("nihao","table1",[['a',100,20,8,1],['b','x','x','c','w']])
#insert("nihao","table2",[['a',8],['b','x']])

