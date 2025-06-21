# 站点维护（给开发人员使用）

先维护单个站点的json，再运行generate_dat.py生成dat文件

```
cd nas-tools-sites/
python app/generate_dat.py
```

生成的dat文件在build/bin目录下，需要移动到config文件夹下替换sites.dat文件
