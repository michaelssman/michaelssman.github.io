# 快速排序

最流行的排序算法，速度最快的排序算法
2个要点：

1. pivot：枢轴 枢纽
2. 递归  使用递归

小于枢轴的放左边  大于枢轴大放右边
左边小的 继续选枢轴 递归  右边的同理

算法：
1. 在左边找比枢轴大的  left
2. 在右边找比枢轴小的  right
3. 交换
4. 一直递归  直到    left不小于right
5. 枢轴和right 交换 （left的比枢轴小 right的不比枢轴小）

一次之后 再对枢轴的左边（和右边）如上操作  使用递归

>未排数组：421	240	035	532	305	430	124

```c++
template<class T>
void QuickSort(T *a, const int left, const int right)
{
    if (left < right) {
        //选枢轴 进行划分
        int i = left;
        int j = right + 1;//为什么要加1
        int pivot = a[left];
        
        //划分算法
        do {
            do i++; while(a[i] < pivot);
            do j--; while(a[j] > pivot);//多加一个数，这个条件 简单一些
            if (i < j) {
                swap(a[i], a[j]);
            }
        } while (i < j);
        swap(a[left], a[j]);
        
        //递归
        QuickSort(a, left, j - 1);
        QuickSort(a, j + 1, right);
    }
}
```

加多一个数  比前面任意数都大即可 这个数不是要排序的
加多一个数   条件简单一些  算法快一些 速度快一点

不用的话 会使循环条件复杂一些 多一些比较 时间复杂度就会大一点
浪费空间 节省时间