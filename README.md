# subjsscan
在渗透项目中发现很多网站的路径都写在了js文件中，于是pua了两天openai，完成了这个脚本工具。</br>
工具的主要工作流程是先从js文件中提取关键词（由单引号、双引号、大括号，小括号、中括号包裹起来的字符串，且长度小于100个字符，由字母、数字、/、\以及.组成），再将关键词拼接到url后面，进行扫描。判断有没有未授权之类的漏洞</br>

#使用方法
python subjsscan.py  -u  http://testphp.vulnweb.com/

![图片](https://github.com/52yao/subjsscan/assets/67967304/e5b177f7-6e35-4b86-94ac-8b40b0bccffc)

1、会在当前目前下生成一个以用户输入的url命名的文件，里面是下载的一些js文件、提取出来的关键词、拼接好的路径</br>
2、会在当前目录下生成一个over.txt文档，里面是子目录、状态码，返回包大小等信息</br>
![图片](https://github.com/52yao/subjsscan/assets/67967304/1147e13b-9d84-47f1-8e30-6505ad7efcc8)
