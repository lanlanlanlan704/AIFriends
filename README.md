一个伟大的开始！！！
2026.1.24


先创建 Django 项目（自带 manage.py 命令入口），项目内建 APP（自带 models.py 写数据格式），通过 manage.py 依次执行 makemigrations 和 migrate 命令，Django 读取 models.py 的定义，自动生成 db.sqlite3 数据库文件及对应数据表。

github上传
1. 添加所有修改的文件
git add .
2. 提交并写备注
git commit -m "备注信息"
3. 推送到GitHub
git push


github克隆
1.定位路径：终端输入 cd D:\ai_voice_project\另一台电脑 切换到目标文件夹
2.克隆代码：执行 git clone -b master git@github.com:lanlanlanlan704/AIFriends.git（一键建仓库 + 下载 master 分支代码）
3.推送改动：git add . && git commit -m "备注" && git push
4.拉取最新：git pull origin master

vue的格式
<template> → 写 HTML（页面结构、内容、标签）
<script> → 写 JS（逻辑、数据、方法、生命周期）
<style> → 写 CSS（样式、布局、外观）

后端总结
项目后端基于 Django 框架搭建，根目录下的.venv 为 Python 虚拟环境，用于隔离项目依赖避免冲突，backend 作为 Django 主项目目录存放全局配置相关内容，web 是核心子应用（APP），通过 web 目录下的 models.py 定义数据库表结构，借助根目录的 manage.py 命令行工具执行 makemigrations 和 migrate 命令，自动生成 db.sqlite3 数据库文件及对应数据表，web 目录下的 views.py 处理业务逻辑和接口请求，urls.py 配置子应用路由映射请求到对应视图，migrations 目录存储数据库迁移文件记录 models.py 的变更历史，admin.py 则用于配置 Django 后台管理界面方便数据管理，整体为前端提供稳定的数据接口和业务逻辑支撑。
前端总结
项目前端基于 Vue + Vite 构建，核心代码集中在 frontend 目录下，其中 node_modules 存放通过 npm install 安装的前端依赖包，public 目录用于存储无需编译的静态资源（如图标、基础 HTML 模板），src 目录包含页面组件、业务逻辑、样式等前端核心源码，vite.config.js 配置 Vite 的开发服务和打包规则，package.json 与 package-lock.json 管理前端依赖版本和脚本命令，可通过 npm run dev 启动本地调试服务进行开发调试，开发完成后执行 npm run build 打包生成可直接部署的静态文件，整体负责用户界面展示和交互逻辑处理，与后端接口配合实现完整的用户操作流程。
总结
后端以 Django 为核心，通过 manage.py 完成数据库迁移、服务启动等操作，web 子应用承载核心业务逻辑与数据模型定义；
前端基于 Vue+Vite 构建，依托 npm 命令完成依赖安装、开发调试和打包部署，核心源码集中在 src 目录。

话筒svg图标
  <svg width="32" height="32" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <!-- 话筒头 -->
    <rect x="22" y="6" width="20" height="28" rx="10" fill="black"/>

    <!-- 话筒柄 -->
    <rect x="30" y="34" width="4" height="14" rx="2" fill="black"/>

    <!-- U 型支架 -->
    <path d="M18 30v4c0 8 6.5 14 14 14s14-6 14-14v-4"
          fill="none"
          stroke="black"
          stroke-width="4"
          stroke-linecap="round"/>

    <!-- 底座 -->
    <rect x="22" y="52" width="20" height="4" rx="2" fill="black"/>
  </svg>

2026/1/28
配置了 RouterView 和 RouterLink 后，点击页面按钮时，RouterLink 会自动修改地址栏域名 / 路径，而将该域名 / 路径对应的 vue 文件内容加载到页面指定位置的工作，由 RouterView 来完成。