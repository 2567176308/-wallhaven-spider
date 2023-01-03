'''练手小项目，仅供学习参考'''
'''通过使用asyncio协程实现异步爬虫，下载wallhaven上面的热榜高清图片壁纸'''
'''由于request模块不支持异步编程，故有些部分用aiohppt代替'''
'''项目还有很大优化空间'''

import aiohttp
import asyncio
from lxml import etree
import requests
import re
import os
# 创建文件夹在本目录
if not os.path.exists('./异步爬取'):
    os.mkdir('./异步爬取')
#     设置头文件进行UA伪装
headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    }
# hot榜地址url
url_hot ='https://wallhaven.cc/hot'
# 由于页数是通过添加荷载page参数实现，故可通过添加至params，拼接发送get请求，达到分页目的
for page in range(1,11):
    # 页数可通过range里面参数修改，我这里是从1到10页
    params = {
        'page': page
    }
    print('正在爬取第', page, '页...')
    # 获取hot页面信息
    page_text = requests.get(url=url_hot,headers=headers,params=params).text

    # 解析hot页面
    tree = etree.HTML(page_text)
    # 通过xpath定位解析标签
    li_list = tree.xpath('//div[@id="thumbs"]/section/ul/li')
    src_list = []
    t = 1
    # 遍历每个li标签获取图片详细地址
    for li in li_list:

        url_src = li.xpath('.//a/@href')[0]
        # print(url_src)
        detail_text = requests.get(url=url_src, headers=headers).text
        # 通过正则表达式匹配图片详情页地址
        ex = '<img id="wallpaper" src="(.*?)"'
        # 由于匹配结果有的为空字符，运行会有错误，故用了这个治标不治本的方法暂时跑起来
        try:
            src= re.findall(ex,detail_text,re.S)[0]
            src_list.append(src)
            # 同样也可以用xpath定位
            # detail_tree = etree.HTML(detail_text)
            # src = detail_tree.xpath('//div[@class="scrollbox"]/img[@id="wallpaper"]/@src')
        except IndexError as e:
            pass

    # print(src_list,len(src_list))
# 利用aiohttp异步爬虫获取图片
# 异步存储
    async def write_data(data,path):
        with open(path, 'wb') as f:
            f.write(data)


    # 异步爬取
    async def get_img(url):
        async with aiohttp.ClientSession() as session:
            print('正在爬取',url)
            async with await session.get(url) as response:
                content = await response.read()
                src_path = './异步爬取/' +url.split('/')[-1]
                await write_data(content,src_path)
                # async with open(src_path,'wb') as fp:
                #    await fp.write(content)
                print('爬取完毕',url)
                # print(content)
    tasks = []

    for url in src_list:
        c = get_img(url)
        task = asyncio.ensure_future(c)
        tasks.append(task)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))