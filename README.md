# HITsz Network Connection Daemon<br><sub>哈尔滨工业大学（深圳）&emsp;校园网断线自动重连</sub>

### 工作方式

脚本每隔一段时间时间对互联网及校园网可达性进行检测，其中时间间隔在网络连接正常时逐渐增加（默认上限为两分钟），断网后密集尝试重连（间隔约五秒）。登陆尝试仅在校园网环境下进行，利用 `selenium` 控制 Chrome 实现登陆。

### 使用说明

首次使用需要绑定校园网用户信息。

进入主界面后，如图所示，默认展示 `网络` 选项卡。

![A](https://github.com/bugstop/hitsz-network-daemon/blob/master/img/A.png)

网络状态栏展示当前网络连通性，检测间隔显示下一次检测的时间。此页面无需人工操作。

如需修改校园网账号信息，需要切换到 `账户` 选项卡，点击已绑定的用户名，在弹窗内输入新的用户名和密码。用户信息~~随缘加密~~储存在同文件夹下，文件名 `userinfo.json` 。

![B](https://github.com/bugstop/hitsz-network-daemon/blob/master/img/B.png)

图形界面默认保持窗口在最上方。