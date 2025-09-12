# AbilityStage

## 创建AbilityStage文件

DevEco Studio默认工程中未自动生成AbilityStage，如需要使用AbilityStage的能力，可以手动新建一个AbilityStage文件，具体步骤如下。

1. 在工程Module对应的ets目录下，右键选择“New > Directory”，新建一个目录并命名为myabilitystage。

2. 在myabilitystage目录，右键选择“New > ArkTS File”，新建一个文件并命名为MyAbilityStage.ets。

3. 打开MyAbilityStage.ets文件，导入AbilityStage的依赖包，自定义类继承AbilityStage并加上需要的生命周期回调，示例中增加了一个[onCreate()](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-app-ability-abilitystage#oncreate)生命周期回调。

   ```typescript
   import { AbilityStage, Want } from '@kit.AbilityKit';
   
   export default class MyAbilityStage extends AbilityStage {
     onCreate(): void {
       // 应用HAP首次加载时触发，可以在此执行该Module的初始化操作（例如资源预加载、线程创建等）。
     }
   
     onAcceptWant(want: Want): string {
       // 仅specified模式下触发
       return 'MyAbilityStage';
     }
   }
   ```

4. 在[module.json5配置文件](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/module-configuration-file)中，通过配置 srcEntry 参数来指定模块对应的代码路径，以作为HAP加载的入口。

   ```json
   {
     "module": {
       "name": "entry",
       "type": "entry",
       "srcEntry": "./ets/myabilitystage/MyAbilityStage.ets",
       // ...
     }
   }
   ```