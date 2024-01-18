import sqlparse as sp
import file
import valid
import re

def parse_sql(sql):
    sql =  sp.format(sql, reindent=False, keyword_case='upper', strip_whitespace=True)
    # 解析SQL语句
    statements = sp.parse(sql) #sql中可包含多条语句，每一句解析为一个statement，statements中包含多个独立的statement
    return statements

def analyse(dbname,statement,user):
    # print(statement[0],statement[2])
    if str(statement[0]) == 'USE' and str(statement[2]) == 'DATABASE':
        #检查用户权限
        message = valid.validPrivilege(0,user,str(statement[4]))
        if message[0] == 1:
            dbname = str(statement[4])
            message.append(dbname)
        return message   #信息可传入ui

    if statement.get_type() == 'CREATE':
        if statement.tokens[2].value.upper() == "DATABASE":   
            for token in statement.tokens:
                if isinstance(token, sp.sql.Identifier):
                    # 获取数据库名称
                    dbname = token.get_real_name()
                    message = valid.validDB(dbname, user)
                    if message[0] == 1:
                        # 调用创建数据库的函数
                        file.createdb(dbname, user)
                        message.append(dbname)
                    # return message[1]   #信息可传入ui
                    return message

        elif statement.tokens[2].value.upper() == "TABLE":  #########
            if dbname == "NULL":
                return "未选取数据库。" #信息可传入ui            
            #检查用户权限
            message = valid.validPrivilege(1,user,dbname)
            if message[0] != 1:
                return message[1]   #信息可传入ui                  
            tableName = str(statement[4])
            checkName = valid.ValidTableName(dbname,tableName) #检查是否重名
            if checkName[0] == 0:
                return checkName[1] #信息可传入ui     
            info = str(statement[6]).replace('(',' ').replace(')',' ').split(',')
            contents = []
            primary = []
            fks = []
            #print(info)
            for each in info:
                each = each.split()
                if each[0] == 'PRIMARY':
                    primary.append(each[2])
                elif len(each) == 1: #也是主码，由于前面以逗号阶段把primary字段拆开了
                    primary.append(each[0])
                elif each[0] == 'CONSTRAINT': #外码约束
                    fks.append([each[1],each[4],each[6],each[7]])
                else:  #基础信息
                    if len(each) > 2:
                        contents.append([each[0],each[1],0,0,0])
                    else: contents.append([each[0],each[1],1,0,0])
            #print(contents,primary,fks)
            for fk in fks: #验证外码参照对象为表的主键
                allpk = valid.findPK(dbname,fk[2])
                found = False
                for pk in allpk:
                    if fk[3] == pk[0]:
                        found = True
                if not found:
                    return "外码参照有误，参照字段非主码！" #信息可传入ui
            for i in range(len(contents)):
                if contents[i][0] in primary:
                    contents[i][3] = 1
                    contents[i][2] = 0 #作为主码时不可为空
                for fk in fks:
                    if contents[i][0] == fk[1]:
                        contents[i][4] = 1
            #调用file的createtable
            file.createTable(tableName,contents,fks,dbname)
            return "创建表成功！" #信息可传入ui

        
        elif statement.tokens[2].value.upper() == "INDEX":
            pass

        elif statement.tokens[2].value.upper() == "VIEW":
            pass
    
    elif statement.get_type() == 'INSERT':             
        if dbname == "NULL":
            return "未选取数据库。" #信息可传入ui    
        #检查用户权限
        message = valid.validPrivilege(4,user,dbname)
        if message[0] != 1:
            return message[1]   #信息可传入ui            
        # 获取目标表名和列名
        tableName = statement[4].get_real_name()
        column = []
        matches = re.findall(r'\((.*?)\)', statement[4].value)
        # 遍历匹配到的子字符串列表
        for match in matches:
            # 去除子字符串中的空格，并使用逗号分割得到元素列表
            elements = match.replace(' ', '').split(',')
        for element in elements:
            column.append([element])

        sub = re.findall(r'\((.*?)\)', statement[6].value)[0]
        sub_statement = sp.parse(sub)[0]

        if sub_statement.get_type().upper() == "SELECT":
            #复合select语句实现批量插入的处理
            contents = analyse(dbname,sub_statement,user)
            if len(contents) != len(column):
                return "给出的属性数量与数据属性数量不匹配！"
            for index1,content in enumerate(contents):
                for index2, value in enumerate(content):
                    if index2 > 0:
                        column[index1].append(value)

        else:   #sub(split后) = [value1, value2, ...] 为一条记录  column = [['a'], ['b']], 未来补充为contents格式
            sub = sub.replace(' ', '').replace("'",'').split(',')
            for i in range(len(sub)):
                if str(sub[i]).upper() == "NULL":
                    column[i].append('~')
                else: column[i].append(str(sub[i]))
        #调用file中insert函数
        message = file.insert(dbname,tableName, column)
        return message
    
    elif statement.get_type() == 'SELECT':
        # print(statement)  
        if dbname == "NULL":
            return [0,"未选取数据库。"] #信息可传入ui
        #检查用户权限
        message = valid.validPrivilege(7,user,dbname)
        if message[0] != 1:
            return message[1]   #信息可传入ui
        select_part = str(statement[2]).split(',')    #select
        from_part = str(statement[6]).split(',')     #from
        whereFlag = False
        for part in statement:
            if str(part)[0:5] == 'WHERE':#存在where子句
                #暂时无法处理where中有select嵌套的情况
                whereFlag = True
                where_part = []
                string = ""
                for index, token in enumerate(part):     
                    if index > 0:
                        if isinstance(token, sp.sql.Comparison): #值比较
                            where_part.append(str(token).replace(' ','')) #如果要做嵌套，就要对token的左右分别判断是否有select类型
                            if len(string) > 0:
                                where_part.append(string[0:-1])
                                string = ""
                        elif str(token) not in [' ',';',"AND"]: #in 与 not in  #要做嵌套的话道理同上
                            string = string + str(token) + ' '
                if len(string) > 0:
                    where_part.append(string[0:-1])
                #print(where_part)
        if whereFlag:
            contents = file.select(dbname,select_part,from_part,where_part)
        else:
            contents = file.select(dbname,select_part,from_part,[])
        return contents
    
    elif statement.get_type() == 'UPDATE':
        if dbname == "NULL":
            return [0,"未选取数据库。"] #信息可传入ui
        #检查用户权限
        message = valid.validPrivilege(5,user,dbname)
        if message[0] != 1:
            return message[1]   #信息可传入ui        
        tableName = str(statement[2])
        values = []
        for each in str(statement[6]).replace(' ','').replace("'",'').split(','):
            each = each.split('=')
            values.append([each[0],each[1]])
        where_part = []
        string = ""
        for index, token in enumerate(statement[8]):     
            if index > 0:
                if isinstance(token, sp.sql.Comparison): #值比较
                    where_part.append(str(token).replace(' ','')) #如果要做嵌套，就要对token的左右分别判断是否有select类型
                    if len(string) > 0:
                        where_part.append(string[0:-1])
                        string = ""
                elif str(token) not in [' ',';',"AND"]: #in 与 not in  #要做嵌套的话道理同上
                    string = string + str(token) + ' '
        if len(string) > 0:
            where_part.append(string[0:-1])
        #print(tableName)
        #print(values)
        #print(where_part)
        message = file.update(dbname,tableName,values,where_part)
        return message

    elif statement.get_type() == 'DELETE':
        if dbname == "NULL":
            return [0,"未选取数据库。"] #信息可传入ui
        #检查用户权限
        message = valid.validPrivilege(6,user,dbname)
        if message[0] != 1:
            return message[1]   #信息可传入ui
        tableName = str(statement[4])
        where_part = []
        string = ""
        for index, token in enumerate(statement[6]):
            if index > 0:
                if isinstance(token, sp.sql.Comparison): #值比较
                    where_part.append(str(token).replace(' ','')) #如果要做嵌套，就要对token的左右分别判断是否有select类型
                    if len(string) > 0:
                        where_part.append(string[0:-1])
                        string = ""
                elif str(token) not in [' ',';',"AND"]: #in 与 not in  #要做嵌套的话道理同上
                    string = string + str(token) + ' '
        if len(string) > 0:
            where_part.append(string[0:-1])
        message = file.delete(dbname,tableName,where_part)
        return message

    # 新增的DROP功能
    elif statement.get_type() == 'DROP':
        if dbname == 'NULL':
            return [0,"未选取数据库。"] #信息可传入ui
        #检查用户权限
        message = valid.validPrivilege(14,user,dbname)
        if message[0] != 1:
            return message[1]  #信息可传入ui
        # what_to_delete = str(statement[2])
        name1 = str(statement[4])

        if statement.tokens[2].value.upper() == "DATABASE":
            # file中新增的drop_db函数
            # 前端中的dbname全局变量是curent_dbname
            message = file.drop_db(name1)
            if message == 1:
                return [1,"该数据库已成功删除！"]

        elif statement.tokens[2].value.upper() == "TABLE":
            name2 = str(statement[10])
            # file中新增的drop_table函数
            # DROP TABLE table_name FROM DATABASE db_name
            #   0 1   2 3      4   5  6 7    8   9   10
            message = file.drop_table(name1,name2)
            if message == 1:
                return[1,"成功删除表格！"]
            
#alter table table1 drop column c
    elif statement.get_type() == 'ALTER':
        if dbname == "NULL":
            return [0,"未选取数据库。"]
        message = valid.validPrivilege(2,user,dbname)
        if message[0] != 1:
            return message[1]   #信息可传入ui
        tableName = str(statement[4])
        #如果要删除表中属性列
        if statement.tokens[6].value.upper() == 'DROP' and str(statement.tokens[8])[0:7].upper() == 'COLUMN':
            column_name = str(statement[10])
            message = file.drop_column(dbname,tableName,column_name)
            
            
        pass
        
#sql = " CrEate DataBase nihao"
#sql = " use database nihao"
#sql = " cReate table table1 (a int not Null, b char , c int, primary key (a,b))"
#sql = " cReate table table2 (a int not Null, b char , primary key (a,b), constraint fk foreign key(a) references table1(a))"
#sql = " cReate table table3 (a int not Null, b char , primary key (a), constraint fk foreign key(a) references table1(a))"
#sql = " insert into table1(a,b,c) values(100,'a',15)" #连输两遍可检验主码约束
#sql = " insert into table1(a,b) values(50,'b')"  #缺列补NULL
#sql = " insert into table1(b,a) values('c',20)"  #乱序示例
#sql = " insert into table1(a,b,c) values(50,'d',NulL)" #插入空
#sql = " insert into table2(a,b) values(100,'a')"  
#sql = " insert into table2(a,b) values(15,'a')"  #外码约束示例
#sql = " insert into table3(a,b) values(x,x)" #数据类型约束示例
#sql = " insert into table3(a,b) values(100,x)"
#sql = "   iNseRt   InTo    table2(a,b)   values  (select a,b from table1)"
#sql = " select * from table1 where table1.b = 'a' and table1.a  in (  100,  50  )  "
#sql = "select * from table1 where a not in (100, 20)"    
#sql = " select c,table2.b from table1,table2 where table1.a= table2.a and table1.a=100"
#sql = "select c,table2.b from table1,table2 where table1.a= table2.a" 
#sql = " select * from table1,table2 where table1.a = table2.a"  
#sql = " select * from table1"
#sql = " select a from table1"
#sql = "select c,table2.a,table3.b from table1,table2,table3 where table1.a = aa and table2.a = table1.a"
#sql = "select * from table1 where a != 50"  

#sql = "update table1 set c=111 where c=null and table1.a != 50" #正常修改
#sql = "update table1 set a=111 where b = 'a'"  #被其他表的外码参照约束不能修改
#sql =  "update table1 set b='x' where c = null"  #主键约束

#sql = " insert into table1(a,b,c) values(75,'e',NULL)"  
#sql = "delete from table1 where a= 75 and a =75"
#sql = "delete from table1 where a in (12,100,75)"  #被其他表的外码参照约束不能删除
        
#sql = " cReate table table4 (a int not Null, b char , primary key (a))"
#sql = "insert into table4(a,b) values (1,盘外招不能说没用，只能在特殊情况用。08这种老手，什么场面没见过，对盘外招他是相当熟悉了，不管别人怎么操作都有应对技巧。但如果你换个不熟悉的人来，很容易就翻车了。说白了还是针对不了解的，对付那些经验丰富的高手没什么用)"
#sql = "insert into table4(a,b) values (2,允许，一个牛你还有精力手动控制，等牛多了不手动操作的话就容易堵矿，中后期大规模坦克交战或者小规模坦克分兵，如果还敢分精力飞矿，很容易被人抓住坦克发呆的漏洞)"
#sql = "insert into table4(a,b) values (3,对面唯一有机会的一局就是3号打8号那把，一开始不应该造兵以免影响重工进度，重工出来卖基地，等出了3坦克1防空车（可偷+防飞行兵）再果断卖重工爆兵，这样还有可能打得下)"
#sql = "select * from table4 where match   b   against 老手什么盘外招没见过"
#while(True):
#    sql = input()
# #    parse_sql(sql,'admin')
# sql = "use database nihao; select c,table2.b from table1,table2 where table1.a= table2.a"  
# sql = "alter table table1 drop column c"
# statements =  parse_sql(sql)
# for statement in statements:
#     # print(analyse('nihao',statement,'admin'))    
#     analyse('nihao',statement,'admin')


