# x3tb_decode

叠纸将大部分战斗相关的配置存储在Unity Asset中方便C#层调用。

这类格式的配置文件一般存储在unity asset的container路径 Assets\Build\Res\Battle\MessagePack 下

## 格式

这类配置文件均基于msgpack格式，具体有两类格式

- 标准MsgPack：将整个类中的所有property按照次序依次存储，形成数组
    - 对应的类会带有 [MessagePackObject(False)] 标记，形如
    ```
    [MessagePackObject(False)]
    public class PointConfig : ActorPointBase // TypeDefIndex: 16865
    {
        // Fields
        [Key(7)]
        public int GroupID; // 0x44
        [Key(8)]
        public PointType PointType; // 0x48
        [Key(9)]
        public RoleType RoleType; // 0x4C

        // Methods

        // RVA: 0x3392478 Offset: 0x3392478 VA: 0x3392478
        public void .ctor() { }
    }
    ```

- X3 MsgPack：和Lua中的TableGen类似和abconfig中的类似，将类结构和内容分开存储从而压缩空间
    - 对应的类带有 [X3MessagePackObject(null)] 或 [X3MessagePackObject("CutSceneAsset")]
    - 存储时，会依次封装三个msgpack，第一个object为字符串“1”，第二个obj为各个类型的字段映射，第三个obj为具体数据
    - 类结构部分如下，包含各个类型property到对应具体数据的下标
    ```
    {
        "ActorCfgs": {
            "girlCfgs": 0,
            "boyCfgs": 1,
            "monsterCfgs": 2,
            "machineCfgs": 3,
            "<girlCfgs>k__BackingField": 4,
            "<boyCfgs>k__BackingField": 5,
            "<monsterCfgs>k__BackingField": 6,
            "<machineCfgs>k__BackingField": 7
        },
        "HurtCfg": {
            "Toughness": 0,
            "HurtTypeID": 1,
            "HurtShakeName": 2,
            "DisableHurtScar": 3,
            "HurtMaterial": 4,
            "<Toughness>k__BackingField": 5,
            "<HurtTypeID>k__BackingField": 6,
            "<HurtShakeName>k__BackingField": 7,
            "<DisableHurtScar>k__BackingField": 8,
            "<HurtMaterial>k__BackingField": 9
        },
    }
    ```

整体上，编码时对于
```
{
    "prop1": value1,
    "prop2": value2,
}
```
这样的数据，会被flatten变成这样的两部分
```
{
    "prop1": 0,
    "prop2": 1,
}
[value1, value2]
```

解析时，均需要从dump.cs中寻找相应类，并按照property类型找相应类型的定义，递归完成解析。

同时，也需要找到每个文件对应的顶级类型，叠纸并没有在msgpack中留下对应信息，因此只能人工推测。例如ActorCfg.bytes实际上存储的是ActorCfgs类型。

## 用法

msgpack_decode.py 实现了常规MsgPack格式的解析。

x3msgpack_decode.py 实现了X3 MsgPack格式的解析。

do_decode.py 整理了大部分MsgPack的顶级类型和存储位置，实现批量解析所有msgpack。

使用时，将整个解密后的bundles目录加载，随后使用菜单Filter Type -> TextAsset筛选文本asset，然后Export -> Filtered assets导出文本asset，最后在脚本中配置好目录运行。