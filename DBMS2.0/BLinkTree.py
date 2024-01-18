import json


class BLinkTreeNode:
    def __init__(self, is_leaf=False):
        self.items = []          # 存储键值对
        self.children = []      # 存储子节点引用
        self.is_leaf = is_leaf  # 是否是叶子节点
        self.next = None        # B-link Tree特有，指向同一层级的下一个节点



class BLinkTree:
    def __init__(self, root=None, t=None):
        if root:
            self.root = root  # 使用已存在的根节点
        else:
            self.root = BLinkTreeNode(is_leaf=True)
            self.t = t  # 树的阶数


    def insert(self, key, value):
        if len(self.root.items) == 2 * self.t - 1:
            temp = BLinkTreeNode()
            self.root = temp
            temp.children.insert(0, self.root)
            self.split_child(temp, 0)
            self.insert_non_full(temp, key, value)
        else:
            self.insert_non_full(self.root, key, value)


    def insert_non_full(self, node, key, value):
        i = len(node.items) - 1
        if node.is_leaf:
            node.items.append((None, None))  # 准备插入新的键值对
            while i >= 0 and key < node.items[i][0]:  # 比较键的部分
                node.items[i + 1] = node.items[i]
                i -= 1
            node.items[i + 1] = (key, value)  # 插入新的键值对
        else:
            while i >= 0 and key < node.items[i][0]:  # 比较键的部分
                i -= 1
            i += 1
            if len(node.children[i].items) == 2 * self.t - 1:
                self.split_child(node, i)
                if key > node.items[i][0]:  # 比较键的部分
                    i += 1
            self.insert_non_full(node.children[i], key, value)  # 递归插入到子节点

    def split_child(self, parent, i):
        t = self.t
        node = parent.children[i]
        new_node = BLinkTreeNode(is_leaf=node.is_leaf)

        # 确保node中有足够的项来分裂
        if len(node.items) >= t:
            parent.items.insert(i, node.items[t - 1])  # 插入中间项到父节点
            new_node.items = node.items[t:(2 * t - 1)]  # 新节点获取一半项
            node.items = node.items[0:(t - 1)]  # 旧节点保留一半项

            if not node.is_leaf:
                new_node.children = node.children[t:(2 * t)]
                node.children = node.children[0:t]

            # 更新横向链接
            new_node.next = node.next
            node.next = new_node
        else:
            # 处理节点项不足以分裂的情况
            print("Error: Node does not have enough items to split")


    def search_and_update(self, node, key, new_value):
        """
        搜索键并更新其值。如果键不存在，则不执行任何操作。
        """
        i = 0
        while i < len(node.items) and key > node.items[i][0]:  # 比较键的部分
            i += 1
        if i < len(node.items) and node.items[i][0] == key:
            node.items[i] = (key, new_value)  # 更新键值对中的值
            return True
        elif node.is_leaf:
            return False
        else:
            return self.search_and_update(node.children[i], key, new_value)


    def search(self, node, key):
        i = 0
        while i < len(node.items) and key > node.items[i][0]:  # 比较键的部分
            i += 1
        if i < len(node.items) and node.items[i][0] == key:
            return node
        elif node.is_leaf:
            return False
        else:
            return self.search(self, node, key)


    def delete_from_leaf(self, node, key):
        """
        从叶子节点中删除键。这是一个简化的删除操作。
        """
        for item in node.items:
            if item[0] == key:  # 比较键的部分
                node.items.remove(item)
                return True
        return False

    def delete(self, key, node=None):
        """
        删除一个键值对。这是一个简化的删除操作。
        """
        if node is None:
            node = self.root
        if node.is_leaf:
            return self.delete_from_leaf(node, key)
        i = 0
        while i < len(node.items) and key > node.items[i][0]:  # 比较键的部分
            i += 1
        if i < len(node.items) and node.items[i][0] == key:
            # 简化处理：如果键在内部节点，不执行删除
            return False
        elif node.is_leaf:
            return False
        else:
            return self.delete(key, node.children[i])

    def serialize(self, node):
        if node is None:
            return None
        node_data = {
            'items': node.items,
            'is_leaf': node.is_leaf,
            'children': [self.serialize(child) for child in node.children]
        }
        return node_data

    def save_to_file(self, filename):
        tree_data = self.serialize(self.root)
        with open(filename, 'w') as file:
            json.dump(tree_data, file)

    def deserialize(self, node_data):
        if node_data is None:
            return None
        node = BLinkTreeNode(is_leaf=node_data['is_leaf'])
        node.items = node_data['items']
        node.children = [self.deserialize(child_data) for child_data in node_data['children']]
        return node

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            tree_data = json.load(file)
        self.root = self.deserialize(tree_data)



# 创建一个BLinkTree实例
tree = BLinkTree(t=3)

# 插入一些键
tree.insert(10,1)
tree.insert(20,2)
tree.insert(5,3)
tree.insert(6,4)
tree.insert(12,5)

searched_node = tree.search(tree.root, 10)
if searched_node:
    print("找到键 10，对应的值为:", [item for item in searched_node.items if item[0] == 10][0][1])
else:
    print("键 10 未找到")

if tree.search_and_update(tree.root, 10, 15):
    print("键 10 的值已更新为 'new_value'")
else:
    print("键 10 未找到，无法更新")


tree.save_to_file('tree_data.json')

# 从文件加载树
new_tree = BLinkTree(t=3)
new_tree.load_from_file('tree_data.json')