import os
import sys
from PyQt5.QtWidgets import QApplication,QTableWidgetItem, QTableWidget,QTextEdit, QWidget, QMessageBox, QPushButton, \
    QLabel, QLineEdit, QDesktopWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
import sql
import file
import valid
from file import get_all_table_attribute
current_user = "admin"
current_dbname = ""
current_table = ""
class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.username_password = file.get_users_password()
        global current_user
        self.init()
        self.init_ui()

    def init(self):
        self.setWindowTitle("ECUST HOYO-DBMS登录界面")
        self.resize(650,365)
        self.setWindowIcon(QIcon(QPixmap('OIP.png')))
        # dark_stylesheet = """
        # QWidget {
        #     background-color: #aec7e3;
        #     color: #005D97;
        # }
        # """
        # self.setStyleSheet(dark_stylesheet)
        center_pointer = QDesktopWidget().availableGeometry().center()
        x = center_pointer.x()
        y = center_pointer.y()
        old_x, old_y, width, height = self.frameGeometry().getRect()
        self.move(int(x - width / 2), int(y - height / 2))
        self.setFixedSize(width, height)


    def init_ui(self):
        container = QVBoxLayout()
        picture_layout = QHBoxLayout()
        picture1 = QLabel()
        picture1.setPixmap(QPixmap('pic.png').scaled(100, 100))
        picture1.setText("")
        picture1.setObjectName("label")

        picture2 = QLabel()
        picture2.setPixmap(QPixmap('name.png').scaled(500, 100))
        picture2.setText("")
        picture2.setObjectName("label")

        picture_layout.addWidget(picture1)
        picture_layout.addWidget(picture2)

        label_entry_box = QGroupBox("")
        label_entry_layout = QHBoxLayout()
        label_box = QGroupBox()
        label_layout = QVBoxLayout()
        label1 = QLabel("账号")
        label2 = QLabel("密码")
        
        font=QFont()
        font.setBold(True)
        label1.setFont(font)
        label2.setFont(font)
        
        label_layout.addWidget(label1)
        label_layout.addWidget(label2)
        label_box.setLayout(label_layout)

        entry_box = QGroupBox()
        entry_layout = QVBoxLayout()
        self.entry1 = QLineEdit()
        self.entry1.setPlaceholderText("请输入用户名")
        self.entry2 = QLineEdit()
        self.entry2.setPlaceholderText("请输入密码")
        self.entry2.setEchoMode(QLineEdit.Password)
        entry_layout.addWidget(self.entry1)
        entry_layout.addWidget(self.entry2)
        entry_box.setLayout(entry_layout)

        label_entry_layout.addWidget(label_box)
        label_entry_layout.addWidget(entry_box)
        label_entry_box.setLayout(label_entry_layout)

        check_box = QGroupBox("")
        btn_layout = QHBoxLayout()
        btn1 = QPushButton("登录")
        btn2 = QPushButton("注册")
        btn3 = QPushButton("忘记密码")
        btn4 = QPushButton("退出")
        btn1.setFont(font)
        btn2.setFont(font)
        btn3.setFont(font)
        btn4.setFont(font)
        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)
        btn_layout.addWidget(btn3)
        btn_layout.addWidget(btn4)
        check_box.setLayout(btn_layout)

        btn1.clicked.connect(self.check_login)
        btn2.clicked.connect(self.goto_Register)
        btn3.clicked.connect(self.find_password)
        btn4.clicked.connect(QApplication.instance().quit)

        information = QLabel("成员信息：竺泽宇，王涵，吴林浩，杨亿")
        information.setFont(font)
        information.setAlignment(Qt.AlignRight)

        container.addLayout(picture_layout)
        container.addWidget(label_entry_box)
        container.addWidget(check_box)
        container.addWidget(information)

        self.setLayout(container)

    #第一个按钮：登录函数设计
    def check_login(self):
        username = self.entry1.text()
        password = self.entry2.text()
        global current_user
        current_user = username
        if not username or not password:
            QMessageBox.warning(self, "出错啦！", "用户名或密码不能为空，请重新输入")
        else:
            if username not in self.username_password.keys():
                QMessageBox.warning(self, "出错啦！", "用户名不存在！\n请输入正确的用户名或注册！")
            else:
                try:
                    if password != self.username_password[username]:
                        QMessageBox.warning(self, "出错啦！", "密码错误！\n请输入正确的密码！")
                except Exception as e:
                    QMessageBox.critical(self, "异常", f"发生异常：{e}")

                if password == self.username_password[username]:
                    try:
                        QMessageBox.information(self, '成功', '登录成功!')
                        self.close()
                        self.dbms = DBMS()
                        self.dbms.show()
                    except Exception as e:
                        QMessageBox.critical(self, "异常", f"发生异常：{e}")
    #第二个按钮：前往登录界面
    def goto_Register(self):
        self.close()
        self.register = Register()
        self.register.show()


    #第三个按钮：找回密码设计
    def find_password(self):
        QMessageBox.information(self,'很抱歉','请联系管理员！')

class Register(QWidget):
    def __init__(self):
        super().__init__()
        self.username_password = file.get_users_password()
        self.init()
        self.init_ui()

    def init(self):
        self.setWindowTitle("ECUST HOYO-DBMS Created BY 竺泽宇 吴林浩 王涵 杨亿")
        self.resize(400,200)

        center_pointer = QDesktopWidget().availableGeometry().center()
        x = center_pointer.x()
        y = center_pointer.y()
        old_x, old_y, width, height = self.frameGeometry().getRect()
        self.move(int(x - width / 2), int(y - height / 2))
        self.setWindowIcon(QIcon(QPixmap('./OIP.png')))
    
    def init_ui(self):
        container = QVBoxLayout()
        #上方输入区
        input_box = QGroupBox("")
        input_box_layout = QHBoxLayout()
        ##输入区-左侧标签区
        label_box = QGroupBox()
        label_layout = QVBoxLayout()
        label1 = QLabel("新的账号")
        label2 = QLabel("新的密码")
        label3 = QLabel("重复密码")
        label_layout.addWidget(label1)
        label_layout.addWidget(label2)
        label_layout.addWidget(label3)
        label_box.setLayout(label_layout)
        ##输入区-右侧输入框
        entry_box = QGroupBox()
        entry_layout = QVBoxLayout()
        self.entry1 = QLineEdit()
        self.entry1.setPlaceholderText("请输入新的用户名")
        self.entry2 = QLineEdit()
        self.entry2.setPlaceholderText("请输入新的密码")
        self.entry2.setEchoMode(QLineEdit.Password)
        self.entry3 = QLineEdit()        
        self.entry3.setPlaceholderText("请确认新的密码")
        self.entry3.setEchoMode(QLineEdit.Password)
        entry_layout.addWidget(self.entry1)
        entry_layout.addWidget(self.entry2)
        entry_layout.addWidget(self.entry3)        
        entry_box.setLayout(entry_layout)
        #设置输入区布局
        input_box_layout.addWidget(label_box)
        input_box_layout.addWidget(entry_box)
        input_box.setLayout(input_box_layout)
        
        #下侧按钮区
        btn_box = QGroupBox()
        btn_box_layout = QHBoxLayout()
        self.btn1 = QPushButton("注册")
        self.btn2 = QPushButton("返回")
                
        ##设置按钮功能
        self.btn1.clicked.connect(self.check_add)
        self.btn2.clicked.connect(self.goback)
        
        btn_box_layout.addWidget(self.btn1)
        btn_box_layout.addWidget(self.btn2)
        
        btn_box.setLayout(btn_box_layout)
        
        container.addWidget(input_box)
        container.addWidget(btn_box)
        self.setLayout(container)
    
    #第一个按钮：注册——弹窗、插入新用户——检查有效性
    def check_add(self):
        new_user = self.entry1.text()
        new_password = self.entry2.text()
        new_check_password = self.entry3.text()
        if not new_user or not new_password:
            QMessageBox.warning(self,"出错啦","新的用户名和密码不能为空！")
        elif new_user in self.username_password.keys():
            QMessageBox.warning(self,"出错啦","该用户名已存在！")
        elif len(new_password) < 6:
            QMessageBox.warning(self,"出错啦","密码需至少6位")  
        elif new_password != new_check_password:
            QMessageBox.warning(self,"出错啦！","请输入相同的密码！")           
        else:
            QMessageBox.information(self,"成功注册！","请回到登录界面登录")
            file.add_user_password(new_user,new_password)
            self.close()
            self.login=Login()
            self.login.show()
            
        
    
    #第二个按钮：返回登录界面
    def goback(self):
        self.close()
        self.login = Login()
        self.login.show()        
    
class DBMS(QWidget):
    def __init__(self):
        super().__init__()
        self.init()
        self.init_ui()
        global current_user
        global current_dbname
        self.input_text = ""
    def init(self):
        self.setWindowTitle("ECUST HOYO-DBMS Created BY 竺泽宇 吴林浩 王涵 杨亿")
        self.resize(1000,800)
        self.setWindowIcon(QIcon(QPixmap('OIP.png')))
        center_pointer = QDesktopWidget().availableGeometry().center()
        x = center_pointer.x()
        y = center_pointer.y()
        old_x, old_y, width, height = self.frameGeometry().getRect()
        self.move(int(x - width / 2), int(y - height / 2))
        self.setWindowIcon(QIcon(QPixmap('./OIP.png')))

    def init_ui(self):
        container = QVBoxLayout()
        
        #上方展示区
        up_area = QHBoxLayout()
        up_area_layout = QHBoxLayout()
        ##上左侧数据库列表
        left_area = QGroupBox("数据库列表")
        left_area_layout = QVBoxLayout()
        ###左上方显示当前用户
        global current_user
        current_user_show = QLabel()
        current_user_show.setText("当前用户为：" + current_user)
        
        ###左下方显示数据库列表
        self.db_tree = QTreeWidget()
        self.db_tree.setHeaderLabel("Databases")
        ####获取文件路径
        self.database_folder_path = os.path.dirname(os.path.abspath(__file__))  # 替换为实际的数据库文件夹路径

        self.refresh_db_tree()
        self.db_tree.itemClicked.connect(self.on_item_clicked)
        ###设置左侧布局器
        left_area_layout.addWidget(current_user_show)
        left_area_layout.addWidget(self.db_tree)
        left_area.setLayout(left_area_layout)
        
        ##上右侧工具及代码展示栏
        right_area = QVBoxLayout()
        right_area_layout = QVBoxLayout()
        
        ###右上方按钮栏
        btn_block = QGroupBox("功能区")
        btn_block_layout = QHBoxLayout()
        btn1 = QPushButton("展示属性")
        btn2 = QPushButton("展示外码")
        btn3 = QPushButton("刷新")
        btn4 = QPushButton("注销")
        btn5 = QPushButton("退出")
        btn_block_layout.addWidget(btn1)
        btn_block_layout.addWidget(btn2)
        btn_block_layout.addWidget(btn3)
        btn_block_layout.addWidget(btn4)
        btn_block_layout.addWidget(btn5)
        btn_block.setLayout(btn_block_layout)
        btn1.clicked.connect(self.table_show)
        btn2.clicked.connect(self.table_fk_init)
        btn3.clicked.connect(self.refresh_db_tree)  # 连接刷新按钮
        btn3.clicked.connect(self.table_hide)
        btn3.clicked.connect(self.output_clear)
        btn4.clicked.connect(self.log_off)
        btn5.clicked.connect(QApplication.instance().quit)
        ###右侧代码展示栏
        show_area = QGroupBox("展示区")
        show_area_layout = QVBoxLayout()


        ####输出栏
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        show_area_layout.addWidget(self.output)
        show_area.setLayout(show_area_layout)
        ##完成右侧输出区布局器
        right_area_layout.addWidget(btn_block)
        right_area_layout.addWidget(show_area)
        right_area.addLayout(right_area_layout)
        
        #完成上侧展示区布置
        up_area_layout.addWidget(left_area)
        up_area_layout.addLayout(right_area)
        up_area.addLayout(up_area_layout)
        
        #下方输入区
        down_area = QGroupBox()
        down_area_layout = QVBoxLayout()

        ###输入栏
        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入指令")
        ###表格展示栏
        self.table = QTableWidget()
        self.table.hide()
        ####上传按钮
        self.btn3 = QPushButton("确定")
        # self.btn3.clicked.connect(self.show_text)
        self.btn3.clicked.connect(self.show_text)
        self.input.returnPressed.connect(self.submit_sql)
        
        show_area_layout_layout = QHBoxLayout()
        show_area_layout_layout.addWidget(self.input)
        show_area_layout_layout.addWidget(self.btn3)
        down_area_layout.addWidget(self.table)
        down_area_layout.addLayout(show_area_layout_layout)
        
        
        down_area.setLayout(down_area_layout)
        
        container.addLayout(up_area)
        container.addWidget(down_area)
        self.setLayout(container)
    #刷新数据库列表
    def refresh_db_tree(self):
        # 清空数据库列表,实现数据库刷新功能
        self.db_tree.clear()
        # 读取数据库文件夹名称并添加到数据库列表
        database_folders = [folder_name for folder_name in os.listdir(self.database_folder_path)
                            if os.path.isdir(os.path.join(self.database_folder_path, folder_name))]
        for folder_name in database_folders:
            # 添加数据库项
            if (folder_name == '__pycache__' or folder_name == '.vscode' or folder_name == 'back' or folder_name == 'index'):
                continue
            db_item = QTreeWidgetItem(self.db_tree)
            db_item.setText(0, folder_name)

            # # 获取该数据库下的表名称
            tables_folder_path = os.path.join(self.database_folder_path, folder_name)  # 替换为实际的数据库文件夹路径
            table_names = [table_name for table_name in os.listdir(tables_folder_path)
                           if os.path.isfile(os.path.join(tables_folder_path, table_name))]

            # # 添加表项
            for table_name in table_names:
                if '.mydb' in table_name or '.privilege' in table_name:
                    continue
                table_item = QTreeWidgetItem(db_item)
                table_item.setText(0, table_name)
                table_item.setHidden(True)

    # 当项目被点击时执行的槽函数    
    def on_item_clicked(self, item):
        global current_user
        global current_dbname
        global current_table
        print("Clicked item:", item.text(0))  # 添加这行调试输出
        # 获取点击的项目的文本
        selected_item_text = item.text(0)  # Use column 0 for text

        # 如果点击的是数据库名称（是文件夹）
        if os.path.isdir(os.path.join(self.database_folder_path, selected_item_text)):
            use_sql = "use database " + selected_item_text
            statement = sql.parse_sql(use_sql)
            for i in statement:
                if str(i[0]) == 'USE' and str(i[2]) == 'DATABASE':
                    message = sql.analyse(selected_item_text,i,current_user)
                if message[0] == 1:
                    current_dbname = message[2]#获得当前使用的数据库名称
                    self.output.append(f"{message[1]}")
                else:
                    self.output.append(f"{message[1]}")
                    return 0
            #检查是否能查询
            message =valid.validPrivilege(7,current_user,current_dbname)
            if message[0] != 1: 
                self.output.append(f"{message[1]}")
                return 0
            
            for i in range(item.childCount()):
                child_item = item.child(i)
                child_item.setHidden(False)
        # 判断是否为文件项
        else:
            # 获取当前表名
            current_table = selected_item_text
            # 获取数据库名称 
            # database_name = self.db_tree.currentItem().parent().text(0)
            # database_name = current_dbname
            #获得该数据库下所有表的属性
            attribute_list = get_all_table_attribute(current_dbname)
            for i in attribute_list:
                if selected_item_text == i[0]+'.table':
                    select_sql = "select * from " + selected_item_text.split('.')[0]
                    sql_codes = sql.parse_sql(select_sql)
                    for j in sql_codes:
                        data_list = sql.analyse(current_dbname,j,current_user)
                        if data_list[0] == 0:
                            self.output.append(f"{data_list[1]}")
                        else:
                            self.table.show()   
                            self.table_data_init([sub_list for sub_list in data_list])
                    break
            
    #展开表格
    def table_show(self):
        self.table_attribute_init()
    #关闭表格
    def table_hide(self):
        self.table.hide()
    #输出表格属性初始化
    def table_attribute_init(self):
        global current_table
        attribute_list = get_all_table_attribute(current_dbname)
        for i in attribute_list:
            if current_table == i[0]+'.table':
                current_table_attribute = i[1:]
                self.table.setColumnCount(len(current_table_attribute[0]))
                self.table.setRowCount(len(current_table_attribute))
                self.table.setHorizontalHeaderLabels(['属性名','属性类型','是否可为NULL','是否为主码','是否为外码'])
                for i, row in enumerate(current_table_attribute):
                    for j, item in enumerate(row):
                        self.table.setItem(i, j, QTableWidgetItem(str(item)))
    #输出表格数据初始化
    def table_data_init(self,data_list):  
        
        self.table.setRowCount(len(data_list[0])-1)  # 设置行数
        self.table.setColumnCount(len(data_list))  # 设置列数
        final_data_list = list(map(list, zip(*data_list)))
        attributre = final_data_list[0]
        data = final_data_list[1:]
        self.table.setHorizontalHeaderLabels(attributre)
        for row_index, row_data in enumerate(data):
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.table.setItem(row_index, col_index, item)
    #输出当前表格外键设置
    def table_fk_init(self):
        all_fk = file.get_all_fk(current_dbname)       
        for i in all_fk:
            if current_table == i[0]+".table":
                fk_data = i[1:]
                final_fk_data = [[item.strip('*;') for item in fk_data[0].split()]]
                self.table.setColumnCount(len(final_fk_data[0]))
                self.table.setRowCount(len(final_fk_data))
                self.table.setHorizontalHeaderLabels(['外码名称','本表参照属性','参照表名','连接表的属性'])
                for i, row in enumerate(final_fk_data):
                    for j, item in enumerate(row):
                        self.table.setItem(i, j, QTableWidgetItem(str(item)))
                self.table.show()
                break
        else:
            self.output.append("当前表未设置外码！")
                
    def submit_sql(self):
        input_text = self.input.text()
        self.show_text()
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        self.output.setTextCursor(cursor)
        
    def output_clear(self):
        self.output.clear()
    #注销函数  
    def log_off(self):
        self.close()
        self.login = Login()
        self.login.show()
        
    #右侧展示框输出设置
    def show_text(self):
        self.input_text = self.input.text()
        global current_dbname
        self.sql_codes = sql.parse_sql(self.input_text)
        self.output.append(f"{self.input_text}")

        for sql_code in self.sql_codes:
            #如果是USE命令
            if str(sql_code[0]) == 'USE' and str(sql_code[2]) == 'DATABASE':
                message = sql.analyse('test',sql_code,current_user)
                if message[0] == 1:
                    current_dbname = message[2]#获得当前使用的数据库名称
                self.output.append(f"{message[1]}")
                continue
                #如果是CREATE命令
            elif str(sql_code[0]) == 'CREATE' and str(sql_code[2]) == 'DATABASE':
                message = sql.analyse('test',sql_code,current_user)
                if message[0] == 1:
                    current_dbname = message[2]#获得当前使用的数据库名称
                self.output.append(f"{message[1]}")
                continue   
                #如果是SELECT命令
            elif sql_code.get_type() == 'SELECT':
                data_list = sql.analyse(current_dbname,sql_code,current_user)
                if data_list[0] == 0:
                    self.output.append(f"{data_list[1]}")
                else:
                    self.table.show()   
                    self.table_data_init([sub_list for sub_list in data_list])
            elif str(sql_code[0]) == 'DROP' and (str(sql_code[2]) == 'TABLE' or str(sql_code[2]) == 'DATABASE'):
                data_list = sql.analyse(current_dbname,sql_code,current_user)
                if data_list[0] == 1:
                    current_dbname = ''
                    self.output.append(f"{data_list[1]}")
                    
            else:
                result = sql.analyse(current_dbname,sql_code,current_user)
                self.output.append(f"{result}")
        self.refresh_db_tree()
        self.input.clear()  # 清空输入框内容
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # w = DBMS()
    w = Login()
    # w = Register()
    w.setWindowIcon(QIcon(QPixmap('OIP.png')))
    w.show()

    sys.exit(app.exec_())
