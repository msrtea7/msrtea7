---

title: 'wpsServer'
pubDate: 2025-03-23
description: '这是我 Astro 博客的第一篇文章。'
author: 'Walbaaco'
image:
    url: '/nun.svg'
    # 16:04:41 [WARN] [vite] Files in the public directory are served at the root path.Instead of /public/nun.svg, use /nun.svg.
    alt: 'The Astro logo on a dark background with a pink glow.'
tags: ["astro", "blogging", "learning in public"]
# layout: '../../../layouts/layout_blog_raw.astro'

---

# The Ultimate Guide For **Basic** Personal WSL DL Env Development

此刻是二零二四年三月一日凌晨一点四十分，我的心情无比沉重且轻盈，我将写下这篇文档以在将来帮助自己或有需要的人。

## 1. 配置 Windows

1. 重装电脑。

2. 主机基本配置
  
  - 删除自带的第三方防火墙/网络安全设备
  - 关闭Windows defender(防火墙)(或者在Windows defender下配置入展规则)
  - (如需开启Windows主机的ssh server)在"设置->账户->你的信息"中选择本地账户登陆
  - 在"设置->系统->电源和电池"中配置从不休眠电脑，(如果是笔记本)在控制面板中设置笔记本盒盖不采取任何操作
  - (有代理需求的自行配置好代理)

3. 主机安装NVIDIA driver
  
  - 在NVIDIA官网下载，选择，安装驱动 <https://www.nvidia.com/download/index.aspx> 
  - 执行 ```nvidia-smi``` 检查

---

## 2. 配置 WSL

1. WSL基本配置(默认宿主机win11，WSL2；其他环境自行解决)

  - 在 ```C:\Users\&Username&\``` 新建.wslconfig文件并粘贴以下内容以设置wsl网络mirror
      > 
      >[experimental]
      >autoMemoryReclaim=gradual # 开启自动回收内存，可在 gradual, dropcache, disabled 之间选择
      >networkingMode=mirrored # 开启镜像网络
      >dnsTunneling=true # 开启 DNS Tunneling
      >firewall=true # 开启 Windows 防火墙
      >autoProxy=true # 开启自动同步代理
      >sparseVhd=true # 开启自动释放 WSL2 虚拟硬盘空间
      >
  - 执行 ```wsl --install``` 安装WSL(较新版本的Windows会直接下载WSL2，注意甄别)
  - 在Microsoft Store上下载 Ubuntu 22.04.3 LTS，并install。(如下载默认的Ubuntu 18*，有可能导致代理失效)
  - 执行 ```sudo passwd root```, ```su root```, 以root用户登陆，默认的账户一直要sudo很烦且有可能碰到指令执行报错

2. WSL 配置DL开发环境，以安装tensorflow gpu版本为例
  
  - 安装miniconda <https://docs.anaconda.com/free/miniconda/index.html>
  - 安装gpu tensorflow <https://www.tensorflow.org/install/pip>

---

## 3. 杂谈

"高端"的食材往往只需要简单的配置。

忏悔，感恩。

---

## 4. ssh

apt install openssh-server
apt install build-essential

## 5. nvim

## 我且输

安装vscode <https://dev.to/abbazs/how-to-install-vscode-in-ubuntu-using-apt-get-2m8o>

1.  Download the Microsoft GPG key: Run the following command to download the Microsoft GPG key and save it as microsoft.gpg: ```curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg```

2. Install the GPG key: Run the following command to install the GPG key into the trusted keyring: ```sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/```

3. Add the VSCode and Microsoft Edge repositories: Run the following commands to add the VSCode and Microsoft Edge repositories to the system: ```sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list'
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'```

4. Remove the downloaded GPG key: Run the following command to remove the microsoft.gpg file: ```sudo rm microsoft.gpg```

5. Update package information: Run the following command to update the package information from the repositories: ```sudo apt update```

6. Install VSCode: Run the following command to install Visual Studio Code: ```sudo apt install -y code```

7. (Optional) Install with aptitude: If you use aptitude package manager, you can run the following commands instead of step 6 to install VSCode: ```sudo aptitude update
sudo aptitude install -y code```


