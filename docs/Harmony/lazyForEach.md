# LazyForEach

LazyForEach从提供的数据源中按需迭代数据，并在每次迭代过程中创建相应的组件。当在滚动容器中使用了LazyForEach，框架会根据滚动容器可视区域按需创建组件，当组件滑出可视区域外时，框架会进行组件销毁回收以降低内存占用。

## 接口描述

```typescript
LazyForEach(   
    dataSource: IDataSource,             // 需要进行数据迭代的数据源  
    itemGenerator: (item: any, index: number) => void,  // 子组件生成函数 
    keyGenerator?: (item: any, index: number) => string // 键值生成函数
): void
```

**参数：**

| 参数名        | 参数类型                                                     | 必填 | 参数描述                                                     |
| ------------- | ------------------------------------------------------------ | ---- | ------------------------------------------------------------ |
| dataSource    | [IDataSource](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control-lazyforeach-0000001820879609#ZH-CN_TOPIC_0000001811158850__idatasource类型说明) | 是   | LazyForEach数据源，需要开发者实现相关接口。                  |
| itemGenerator | (item: any， index:number) => void                           | 是   | 子组件生成函数，为数组中的每一个数据项创建一个子组件。**说明：**item是当前数据项，index是数据项索引值。itemGenerator的函数体必须使用大括号{...}。itemGenerator每次迭代只能并且必须生成一个子组件。itemGenerator中可以使用if语句，但是必须保证if语句每个分支都会创建一个相同类型的子组件。itemGenerator中不允许使用ForEach和LazyForEach语句。 |
| keyGenerator  | (item: any, index:number) => string                          | 否   | 键值生成函数，用于给数据源中的每一个数据项生成唯一且固定的键值。当数据项在数组中的位置更改时，其键值不得更改，当数组中的数据项被新项替换时，被替换项的键值和新项的键值必须不同。键值生成器的功能是可选的，但是，为了使开发框架能够更好地识别数组更改，提高性能，建议提供。如将数组反向时，如果没有提供键值生成器，则LazyForEach中的所有节点都将重建。**说明：**item是当前数据项，index是数据项索引值。数据源中的每一个数据项生成的键值不能重复。 |

## IDataSource类型说明

```typescript
interface IDataSource { 
    totalCount(): number; // 获得数据总数 
    getData(index: number): Object; // 获取索引值对应的数据    
    registerDataChangeListener(listener: DataChangeListener): void; // 注册数据改变的监听器    
    unregisterDataChangeListener(listener: DataChangeListener): void; // 注销数据改变的监听器
}
```

| 接口声明                                                     | 参数类型                                                     | 说明                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------------------------- |
| totalCount(): number                                         | -                                                            | 获得数据总数。                                           |
| getData(index: number): any                                  | number                                                       | 获取索引值index对应的数据。index：获取数据对应的索引值。 |
| registerDataChangeListener(listener:[DataChangeListener](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control-lazyforeach-0000001820879609#ZH-CN_TOPIC_0000001811158850__datachangelistener类型说明)): void | [DataChangeListener](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control-lazyforeach-0000001820879609#ZH-CN_TOPIC_0000001811158850__datachangelistener类型说明) | 注册数据改变的监听器。listener：数据变化监听器           |
| unregisterDataChangeListener(listener:[DataChangeListener](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control-lazyforeach-0000001820879609#ZH-CN_TOPIC_0000001811158850__datachangelistener类型说明)): void | [DataChangeListener](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control-lazyforeach-0000001820879609#ZH-CN_TOPIC_0000001811158850__datachangelistener类型说明) | 注销数据改变的监听器。listener：数据变化监听器           |

## DataChangeListener类型说明