# Evol Deepspace Scripts

关注果冻喵，关注果冻谢谢喵 -> [恋与深空Evol攻略组](https://weibo.com/u/7559183971)

## updater

- updater.py：从入口服务器拿到更新地址和最新版本信息，存在catalogs/1.0.XXXX.json里面
- update_downloader.py：根据上面得到的json下载整包

## res_decrypt

（这一部分需要把调试用的ipynb转为独立python脚本）
- Lua相关：
  1. XLuaDecrypt: 把lua资源包解压
  2. 用修改版unluac反编译变种Lua字节码
  3. RestructureLua：恢复叠纸CRC32 hash后的路径
- 图片资源相关：
  其他Unity AssetBundle里面的资源需要用ABDecrypt解密一下才能用AssetStudio打开

## frida_debug

（用于debug和研究的脚本）

## abconfig_parser

解析内部存asset bundle依赖关系的工具，但我们不关心依赖关系，不需要这个工具，直接遍历所有的*.ab文件就行了