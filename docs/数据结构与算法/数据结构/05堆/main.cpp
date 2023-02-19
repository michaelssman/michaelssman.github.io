//
//  main.cpp
//  CPPDemo00
//
//  Created by 崔辉辉 on 2019/10/31.
//  Copyright © 2019 huihui. All rights reserved.
//

#include <iostream>
#include <string>
#include <cstdlib>
#include <cassert>
#include <fstream>
#include <vector>
#include <list>//C++ STL中的链表
#include <queue>

#include <set>
#include <map>
using namespace std;
#define SWAP(x,y,t) ((t) = (x),(x) = (y),(y) = (t))
int main(int argc, const char * argv[]) {
    // insert code here...
    std::cout << "Hello, World!\n";
    return 0;
}

#pragma mark - 做一个大顶堆
//做在头文件里，用模版。
//大顶堆
template <class T>
class MaxHeap
{
public:
    MaxHeap(int mx = 10);//构造函数。堆的大小 默认是10个
    virtual ~MaxHeap();//析构函数
    
    bool IsEmpty();//判断堆是否是空堆
    void Push(const T&);//push 往堆里增加数据
    void Pop();//pop 把根删除
    const T& Top() const;//top 获取根里的数据 并不删除 和pop不一样
private:
    T* heapArray;//数组
    int maxSize;//数组最大是多少，最多放多少数据
    int currentSize;//数组当前的大小，有多少数据
    
    void trickleUp(int index);
    void trickleDown(int index);//向下冒泡
};

//构造函数
template <class T>
MaxHeap<T>::MaxHeap(int mx)
{
    if (mx < 1) {
        throw "max size must be >= 1";
    }
    
    maxSize = mx;
    currentSize = 0;//新创建的堆 里面没有数据
    heapArray = new T[maxSize];//用new创建出来数组
}

//析构函数
template <class T>
MaxHeap<T>::~MaxHeap()
{
    delete [] heapArray;//与new对应
}

//是否是空的
template <class T>
bool MaxHeap<T>::IsEmpty()
{
    return currentSize == 0;//currentsize是用来计数的 每push一个就加1
}

//push 插入新的节点到堆里
template <class T>
void MaxHeap<T>::Push(const T &e)
{
    //先检查堆是不是已经满了
    if (currentSize == maxSize) {
        //利用动态数组 放大 就不需要抛出异常了
        throw "MaxHeap is full";
    }
    
    //新插入到节点都放入到最后 currentSize是最后一个空位 不是最后一个节点 是最后一个节点的下一个
    heapArray[currentSize] = e;
    //向上渗透
    trickleUp(currentSize++);
}

template <class T>
void MaxHeap<T>::trickleUp(int index)
{
    //子节点序号是11 则父节点序号是5. 子节点序号是10 父节点序号是4
    int parent = (index - 1) / 2;//父节点的序号
    T bottom = heapArray[index];//最后的节点临时保存起来 因为要交换 否则一交换就没了。
    //一层一层不断的向上 index==0时就到根了 到顶了。 如果父节点小于bottom则就结束了。
    while (index > 0 && heapArray[parent] < bottom) {
        heapArray[index] = heapArray[parent];//交换 和小的父节点交换
        index = parent;
        parent = (parent - 1) / 2;
    }
    heapArray[index] = bottom;
}

//top 查看堆的根节点
template <class T>
const T& MaxHeap<T>::Top() const
{
    return heapArray[0];//根的数据是最大的 下标是0
}

//pop 把堆顶（根）删除
template <class T>
void MaxHeap<T>::Pop()
{
    //先把最后的数据放到根位置。currentSize是最后一个空位，最后一个节点的下一个。所以要减减。
    heapArray[0] = heapArray[--currentSize];
    //向下渗透
    trickleDown(0);//从根（0）开始 向下渗透
}

template <class T>
void MaxHeap<T>::trickleDown(int index)
{
    //每个节点有一个左儿子 一个右儿子 要找最大的。
    int largerChild;
    //根 临时保存起来
    T top = heapArray[index];
    //用循环向下渗透 每渗透一次都会减半
    while (index < currentSize / 2) {
        //左儿子序号（下标）
        int leftChild = 2 * index + 1;
        //右儿子下标
        int rightChild = leftChild + 1;
        //先检查是否有右儿子 有的节点没有右儿子。并且左儿子小于右儿子。则右儿子做最大的。否则就是左儿子大。
        if (rightChild < currentSize && heapArray[leftChild] < heapArray[rightChild]) {
            largerChild = rightChild;
        } else {
            largerChild = leftChild;
        }
        //如果top比大的子节点大则停止循环，否则就继续交换。
        if (top >= heapArray[largerChild]) {
            break;
        }
        heapArray[index] = heapArray[largerChild];
        index = largerChild;
    }
    heapArray[index] = top;
}

//测试
void test()
{
    MaxHeap<int> h(100);//最大是100个
    cout << h.IsEmpty() << endl;
    
    h.Push(20);
    h.Push(30);
    h.Push(15);
    cout << h.Top() << endl;//最大的 根

    h.Pop();
    cout << h.Top() << endl;//最大的 根

}

//测试堆排序
void test1()
{
    MaxHeap<int> h(100);//最大是100个
    
    int arr[] = {62,3,90,27,33,8,12,9,43,66};
    
    for (int i = 0; i < 10; i++) {
        h.Push(arr[i]);
    }
    
    for (int i = 0; i < 10; i++) {
        arr[i] = h.Top();
        h.Pop();
    }
    
    for (int i = 0; i < 10; i++) {
        cout << arr[i] << endl;
    }

}
