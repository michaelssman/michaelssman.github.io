```
#include <iostream>
using namespace std;
class List;
class Node {
    friend List;
    int data;
    Node* link;//下一个节点指针
};
class List {
    int length();
    void deleteNode(int n);
    Node *first;
};
void List::deleteNode(int n) {
    if(n > length()) return;
    Node *currentNode = first;
    Node *preNode;
    //找到需要删除的节点
    for(int i = 0; i < length() - n; i++) {
        preNode = currentNode;
        currentNode = currentNode->link;
    }
    //修改指针指向
    preNode->link = currentNode->link;
}
int main() {
    //int a;
    //cin >> a;
    cout << "Hello World!" << endl;
}
```

