# VLA泊车-HMI交互需求测试用例（完整版）

## 需求概述

**需求文档来源**：
1. 📄 25年11月 VLA泊车-HMI交互需求V1.0 [最终].pdf（20页）
2. 📄 泊车HAVP_HMI交互规范_V1.0_20251118.pdf（88页）
3. 📊 VLA漫游泊车指令_202511.xlsx（语音指令定义）
4. 📊 泊车文言映射表.xlsx（文言信号映射）
5. 📄 GWM-25-04-车外智驾灯需求.pdf（9页）

**提取方式**：使用PyMuPDF精准提取所有PDF内容  
**生成日期**：2026-01-26  
**适用车型**：Thor  
**座舱版本**：CUX3.5  
**平台配置**：ADC40  

### VLA漫游泊车功能架构

```
VLA漫游泊车
├── 1. 平台配置识别（ADC40平台配置字）
├── 2. 功能开启
│   ├── 2.1 无图漫游功能开启
│   │   ├── 引导界面（0xF:VLAP without ODD）
│   │   ├── 人驾界面（0x10:VLAP Preactive）
│   │   ├── 控车界面（0x11:VLAP Active Page）
│   │   ├── 无目的漫游（APA选车位）
│   │   └── 有目的漫游（语音命中楼层/出口等）
│   ├── 2.2 有图泊车功能开启
│   │   ├── 2D库位管理界面（0x1:Pre_Mapbuilt）
│   │   └── 记忆巡航激活界面（0x3:Cruise）
│   └── 2.3 功能开启异常（17种异常场景）
├── 3. 静默建图
│   ├── 3.1 无图静默建图（人驾界面后台建图）
│   ├── 3.2 无图漫游泊车（控车界面实时建图）
│   └── 3.3 有图巡航泊车
├── 4. 漫游阶段
│   ├── 4.1 漫游抑制（9种不使能条件）
│   ├── 4.2 漫游激活（特殊场景文言）
│   ├── 4.3 沿途泊车（按键状态管理）
│   ├── 4.4 漫游暂停&继续
│   ├── 4.5 漫游异常退出（25+种场景）
│   ├── 4.6 静默&漫游完成
│   └── 4.7 扩建地图
├── 5. COT推理面板
│   ├── 5.1 面板样式（热力图标标注）
│   ├── 5.2 显示规则（5s间隔、去重逻辑）
│   └── 5.3 COT场景（任务推理+非任务推理）
├── 6. 导航&巡航
│   ├── POI信息显示（出入口、充电桩车位）
│   └── 6.1 巡航完成
├── 7. 语音控车（3大类指令）
│   ├── 园区功能开启指令
│   ├── 行为控制指令
│   └── 目的地寻找指令
└── 8. 功能退出（用户主动退出&系统退出）
```

### ⚠️ 三大变更修复（必须重点验证）

#### 变更1：漫游异常退出逻辑调整
**背景**：解决地图匹配上后漫游预激活界面和2D地图界面频繁跳闪问题

**退出界面规则**：
- ✅ 无图漫游场景（InterfaceDisTyp=0x11，无地图） → 退出到**漫游预激活界面（0x10:VLAP Preactive）**
  - 四门两盖打开：机舱盖、后背门、车门、后视镜折叠、安全带解开
  - 绕行障碍物空间不足（不可移动障碍物30s）
  - 车辆已在目标楼层/区域
  - EPB干预、档位干预、方向盘干预、刹车干预
  - 车速超过30km/h

- ✅ 有图巡航场景（InterfaceDisTyp=0x3:Cruise，有地图） → 退出到**HUT主界面**
  - 四门两盖打开（同上）
  - 定位失败
  - 光照不满足、雨量过大
  - 系统故障、关联系统故障
  - 漫游超时10分钟、暂停超时3分钟
  - APA泊车超时4分钟、暂停次数超限
  - 主动安全功能激活（RCTB/FCTB、AEB、ESP、TCS/ABS、HDC）
  - 胎压异常、目标车位被占
  - APA泊入失败、激活失败
  - 摄像头被遮挡、摄像头故障、雷达故障
  - 主动退出

**涉及信号**：HAVPFunctTextDisp（文言）+ PopupDisp=0x20（接管弹窗）

#### 变更2：静默建图保存弹窗时间调整  
**背景**：解决静默建图保存弹窗显示时间过短问题

| 项目 | 原设计 | 新设计 |
|------|-------|-------|
| 弹窗显示时间 | 10s | **15s** |
| 触发信号 | PopupDisp=0x3F:HAVP_Push_Request（最长10s） | PopupDisp=0X3F:HAVP_Push_Request（最长**15s**） |
| 触发场景 | 手动泊入车位后挂P挡 / 沿途泊车自动泊入后 | 同左 |
| 用户操作 | 点击【保存】/【取消】或等待10s自动放弃 | 点击【保存】/【取消】或等待**15s**自动放弃 |

#### 变更3：漫游常驻文言信号变更
**背景**：区分漫游和巡航的常驻文言

| 项目 | 原设计 | 新设计 |
|------|-------|-------|
| 信号值 | HAVPFunctTextDisp=0x2E: Park-in Cruising | HAVPFunctTextDisp=**0xC4**: HAVP Roaming |
| 文言内容 | 记忆泊车巡航文言（与记忆泊车混淆） | **"车辆漫游中，请注意周围环境"** |
| 显示场景 | 漫游控车界面常驻显示 | 同左 |
| 适用状态 | FunctWorkSts=0x9:VLAP Roaming | 同左 |

---

## 测试用例列表

### 1. 平台配置识别（2个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-001 | 泊车 | HMI | P0 | ADC40平台配置识别 | 1. 车辆处于ready状态<br>2. 系统正常启动 | 车辆配置为ADC40平台 | 1. 系统启动完成<br>2. 检查VLA漫游泊车功能显示 | HUT识别ADC40平台配置字 | 1. HUT正确显示VLA漫游泊车相关功能界面<br>2. 【记忆泊车】按键可见<br>3. VLA功能模块正常加载 | ADC40平台配置字识别成功 | 实车测试 | Thor-CUX3.5 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-002 | 泊车 | HMI | P1 | 非ADC40平台配置处理 | 1. 车辆处于ready状态<br>2. 系统正常启动 | 车辆配置为非ADC40平台 | 1. 系统启动完成<br>2. 检查VLA漫游泊车功能显示 | HUT识别非ADC40平台配置字 | 1. HUT不显示VLA漫游泊车相关功能<br>2. 仅显示基础泊车功能 | 平台配置字识别为非ADC40 | 实车测试 | 边界场景 | 业务逻辑层 |

### 2. 无图漫游功能开启-引导界面（3个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-003 | 泊车 | HMI | P0 | ODD范围外显示无图引导界面 | 1. 车辆处于ready状态<br>2. 当前位置在ODD范围外 | Signal_Indnc=0x1:SOME/IP | 1. 点击【记忆泊车】按键或语音激活<br>2. 观察界面显示 | HUT发送BtnEnaReq=0x2:Active_signal<br>域控反馈InterfaceDisTyp=0xF:VLAP without ODD | 1. 中控屏显示无图引导界面<br>2. 弹窗推送"记忆泊车已就绪，下拨两次拨杆或试试语音激活"<br>3. 弹窗持续显示10s | InterfaceDisTyp=0xF:VLAP without ODD | 实车测试 | 无图引导界面 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-004 | 泊车 | HMI | P0 | 无图引导界面语音激活响应 | 1. 车辆处于ready状态<br>2. 显示无图引导界面 | InterfaceDisTyp=0xF:VLAP without ODD | 1. 语音指令"激活记忆泊车"<br>2. 观察系统响应 | VLA链路识别语音指令 | 1. 系统响应语音指令<br>2. 根据是否进入ODD范围决定后续动作 | 语音指令识别成功 | 实车测试 | 语音激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-005 | 泊车 | HMI | P1 | 无图引导界面进入ODD自动跳转 | 1. 车辆处于ready状态<br>2. 显示无图引导界面<br>3. 车辆行驶 | InterfaceDisTyp=0xF:VLAP without ODD | 1. 车辆驶入ODD范围内<br>2. 观察界面自动跳转 | 域控检测进入ODD范围<br>发送InterfaceDisTyp=0x10:VLAP Preactive | 1. 界面自动从无图引导界面跳转到漫游泊车人驾界面<br>2. 显示360全景影像视图<br>3. 开始静默建图 | InterfaceDisTyp=0x10:VLAP Preactive | 实车测试 | 自动跳转场景 | 业务逻辑层 |

### 3. 无图漫游功能开启-人驾界面（5个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-006 | 泊车 | HMI | P0 | 漫游泊车人驾界面完整显示 | 1. 车辆处于ready状态<br>2. 位于ODD范围内<br>3. 点击【记忆泊车】按键 | 域控发送InterfaceDisTyp=0x10:VLAP Preactive<br>FunctWorkSts=0x0:Standby | 1. 进入漫游泊车人驾界面<br>2. 检查所有界面元素完整性 | PrkgFuncStsLmp=0x2:VLAP_Roaming_Standby<br>APS_PASSwtReq=0x2:Request to open<br>FunctBtnDisp=0x0:None<br>StartPrkBtnDisp=0x0:No_Display | 1. 显示360全景影像视图（复用记忆泊车视频）<br>2. 显示自车车模<br>3. 显示当前档位信息（实际车速HUT性能暂不满足）<br>4. 漫游标识置灰<br>5. 实时渲染感知元素：立柱、车位、道路箭头、行人、车辆、减速带、学习轨迹<br>6. 显示缩略态Map（范围100米），小地图不可展开<br>7. 状态灯置灰显示（仅中控） | InterfaceDisTyp=0x10:VLAP Preactive<br>PrkgFuncStsLmp=0x2（CAN信号） | 实车测试 | 人驾界面完整性 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-007 | 泊车 | HMI | P0 | 人驾界面点击小地图Toast提示 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 点击缩略态小地图<br>2. 观察Toast提示 | HUT检测点击操作 | 1. 中控屏Toast提示"请保存地图后再尝试"<br>2. 小地图不展开<br>3. 提示持续显示3s | HUT侧交互逻辑 | 实车测试 | 小地图点击提示 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-008 | 泊车 | HMI | P0 | 人驾界面双击拨杆激活漫游 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车辆静止或低速行驶 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 双击拨杆<br>2. 观察界面跳转和状态变化 | HUT检测拨杆信号<br>域控发送InterfaceDisTyp=0x11:VLAP Active Page | 1. 界面跳转到漫游控车界面<br>2. 漫游标识高亮显示<br>3. 显示【退出】按键<br>4. 显示【沿途泊车】按键<br>5. 显示COT推理面板<br>6. 状态灯高亮 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming<br>PrkgFuncStsLmp=0x4:VLAP_Roaming_Active | 实车测试 | 拨杆激活漫游 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-009 | 泊车 | HMI | P0 | 人驾界面语音激活漫游 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 语音指令"开始漫游"或"开启漫游泊车"<br>2. 观察界面响应和语音反馈 | VLA链路识别语音<br>域控发送InterfaceDisTyp=0x11:VLAP Active Page | 1. 界面跳转到漫游控车界面<br>2. 漫游标识高亮<br>3. 语音播报"好的，我将开始漫游泊车"<br>4. 车辆开始控车 | InterfaceDisTyp=0x11:VLAP Active Page<br>PrkgFuncStsLmp=0x4:VLAP_Roaming_Active | 实车测试 | 语音激活漫游 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-010 | 泊车 | HMI | P1 | 人驾界面感知元素实时渲染验证 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车辆在停车场行驶 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 车辆行驶经过立柱、车位、减速带等<br>2. 验证各感知元素实时渲染 | 域控持续发送感知数据 | 1. 立柱实时渲染位置和形状<br>2. 车位实时显示（含充电桩车位）<br>3. 道路箭头（地面方向标识）实时显示<br>4. 行人和车辆动态渲染<br>5. 减速带位置准确<br>6. 学习轨迹实时更新 | 感知元素渲染准确 | 实车测试 | 静默建图感知渲染 | 业务逻辑层 |

### 4. 无图漫游功能开启-控车界面（4个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-011 | 泊车 | HMI | P0 | 漫游控车界面完整元素显示 | 1. 车辆处于ready状态<br>2. 漫游功能已激活 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 1. 检查漫游控车界面所有元素<br>2. 验证各功能显示正确 | PrkgFuncStsLmp=0x4:VLAP_Roaming_Active<br>AlongToutPrkgBtnSts=0x1:Available<br>VLAPSpdSetVal=0x14:Twenty | 1. 显示360全景影像视图<br>2. 显示缩略态实时路线（小地图不可展开）<br>3. 显示自车位置<br>4. 显示实时感知障碍物、车位信息、历史轨迹、规划路径<br>5. 显示最大车速和实际车速<br>6. 根据HAVPFunctTextDisp提示文字<br>7. 显示【退出】按键<br>8. 漫游标识高亮<br>9. 显示【沿途泊车】按键<br>10. 显示COT推理面板 | InterfaceDisTyp=0x11:VLAP Active Page | 实车测试 | 控车界面完整性 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-012 | 泊车 | HMI | P0 | 漫游控车速度设置显示与范围 | 1. 车辆处于ready状态<br>2. 漫游功能已激活 | InterfaceDisTyp=0x11:VLAP Active Page | 1. 观察速度显示<br>2. 验证速度设置反馈 | VLAPSpdSetVal=0x14:Twenty | 1. 界面显示最大车速20km/h<br>2. 显示当前实际车速（或档位信息）<br>3. 速度数值实时更新<br>4. 速度设置范围10~20km/h | VLAPSpdSetVal支持10~20km/h范围 | 实车测试 | 速度显示与设置 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-013 | 泊车 | HMI | P1 | 漫游控车小地图点击Toast提示 | 1. 车辆处于ready状态<br>2. 显示漫游控车界面 | InterfaceDisTyp=0x11:VLAP Active Page | 1. 点击缩略态小地图<br>2. 观察Toast提示 | HUT检测点击操作 | 1. 中控屏Toast提示"请保存地图后再尝试"<br>2. 小地图不展开 | HUT侧交互逻辑 | 实车测试 | 小地图点击提示 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-014 | 泊车 | HMI | P0 | 漫游中常驻文言变更验证 | 1. 车辆处于ready状态<br>2. 漫游功能已激活<br>3. 车辆漫游中 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 1. 检查常驻文言显示<br>2. 验证信号值和文言内容 | 域控发送HAVPFunctTextDisp=0xC4（文言："车辆漫游中，请注意周围环境"）:HAVP Roaming | 1. 界面显示常驻文言"车辆漫游中，请注意周围环境"<br>2. 文言信号值为0xC4（⚠️非0x2E）<br>3. 文言常驻显示在固定位置 | HAVPFunctTextDisp=0xC4（文言："车辆漫游中，请注意周围环境"）:HAVP Roaming | 实车测试 | ⚠️变更3-漫游文言0xC4 | 业务逻辑层 |

### 5. 无目的漫游-APA选车位（5个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-015 | 泊车 | HMI | P0 | 人驾界面踩刹车显示可泊入车位 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车辆低速行驶 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 用户踩制动使车辆刹停<br>2. 观察车位显示 | 域控检测车辆静止<br>发送可泊入车位信息 | 1. HUT界面显示8个可泊入车位<br>2. 高亮显示最近的一个车位作为APA目标车位<br>3. 目标车位支持车头车尾选择<br>4. 车位图标清晰可见 | 域控发送可泊入车位列表 | 实车测试 | APA选车位显示 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-016 | 泊车 | HMI | P0 | 人驾界面点击切换目标车位 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 界面显示多个可泊入车位 | InterfaceDisTyp=0x10:VLAP Preactive<br>当前高亮车位A | 1. 点击其他可泊入车位B<br>2. 观察车位高亮状态变化 | HUT发送SelNearSlotID指定车位B<br>泊车控制器更改车位B状态 | 1. 车位B高亮显示<br>2. 车位A恢复普通显示<br>3. 目标车位切换成功<br>4. 界面有切换动画效果 | 泊车控制器反馈车位B高亮 | 实车测试 | 点击切换车位 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-017 | 泊车 | HMI | P0 | 人驾界面语音选择车位 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 界面显示多个可泊入车位 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 语音指令"选择3号车位"<br>2. 观察车位状态和语音反馈 | VLA链路识别语音<br>HUT发送SelNearSlotID<br>泊车控制器更改车位状态 | 1. 3号车位高亮显示<br>2. 原高亮车位恢复普通显示<br>3. 语音播报"已选择3号车位" | 泊车控制器反馈3号车位高亮 | 实车测试 | 语音选择车位 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-018 | 泊车 | HMI | P0 | 人驾界面点击开始APA泊车 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 已选择目标车位 | InterfaceDisTyp=0x10:VLAP Preactive<br>FunctBtnDisp=0x5:Start_APA | 1. 界面显示【开始泊车】按键<br>2. 点击【开始泊车】按键<br>3. 观察系统响应 | 泊车控制器发送FunctBtnDisp=0x5<br>HUT发送BtnEnaReq=0x6:Confrim_start_parking<br>泊车控制器开始执行器握手 | 1. 系统开始横纵向执行器握手<br>2. APA功能激活<br>3. 车辆开始自动泊入<br>4. 界面显示APA泊车引导信息 | APA激活成功<br>FunctWorkSts=0xA:VLAP Parking | 实车测试 | 点击开始APA | 业务逻辑层 |
| BFO-HMI-Thor-VLA-019 | 泊车 | HMI | P0 | 人驾界面语音开始APA泊车 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 已选择目标车位 | InterfaceDisTyp=0x10:VLAP Preactive<br>FunctBtnDisp=0x5:Start_APA | 1. 语音指令"开始泊车"<br>2. 观察系统响应和语音反馈 | VLA链路识别语音<br>HUT发送BtnEnaReq=0x6:Confrim_start_parking | 1. 系统开始横纵向执行器握手<br>2. APA功能激活<br>3. 语音播报"好的，开始泊车"<br>4. 车辆开始自动泊入 | APA激活成功 | 实车测试 | 语音开始APA | 业务逻辑层 |

### 6. 有目的漫游（3个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-020 | 泊车 | HMI | P0 | 人驾界面语音驶离停车场 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 语音指令"帮我驶离停车场"或"帮我驶离停车楼"<br>2. 观察界面跳转和语音反馈 | VLA链路识别有目的漫游指令<br>域控发送InterfaceDisTyp=0x11:VLAP Active Page | 1. 界面跳转到漫游控车界面<br>2. 车辆开始执行驶离任务<br>3. 语音播报"好的，正在寻找{停车场出口}"<br>4. COT面板显示任务推理 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 实车测试 | 有目的漫游-驶离 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-021 | 泊车 | HMI | P0 | 人驾界面语音寻找楼层 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 语音指令"帮我停到B1层"或"帮我寻找B1层"或"去B1层"<br>2. 观察界面跳转和系统响应 | VLA链路识别楼层目标<br>域控发送InterfaceDisTyp=0x11:VLAP Active Page | 1. 界面跳转到漫游控车界面<br>2. 车辆开始执行前往B1层任务<br>3. 语音播报"好的，正在寻找B1层"<br>4. COT面板显示任务推理（发现楼层指引） | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 实车测试 | 有目的漫游-找楼层 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-022 | 泊车 | HMI | P0 | 领航桌面直接语音激活有目的漫游 | 1. 车辆处于ready状态<br>2. 位于ODD范围内<br>3. 未进入功能界面（领航桌面） | 当前显示领航桌面 | 1. 语音指令"帮我寻找停车场出口"<br>2. 观察系统响应 | VLA链路识别指令<br>域控发送InterfaceDisTyp=0x11:VLAP Active Page | 1. 直接跳转到漫游控车界面（跳过人驾界面）<br>2. 车辆开始执行寻找出口任务<br>3. 语音播报"好的，正在寻找停车场出口"<br>4. 漫游功能直接激活 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 实车测试 | 未进功能前激活 | 业务逻辑层 |

### 7. 有图泊车功能开启-库位管理（4个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-023 | 泊车 | HMI | P0 | 有图场景显示2D库位管理界面 | 1. 车辆处于ready状态<br>2. 位于有地图的停车场/园区<br>3. ODD范围内 | 停车场已有学习路线<br>定位成功 | 1. 点击【记忆泊车】按键<br>2. 观察界面显示 | HUT发送BtnEnaReq=0x2:Active_signal<br>域控发送InterfaceDisTyp=0x1:Pre_Mapbuilt<br>FunctBtnDisp=0x0:None<br>FunctBtnSts=0x1:Available | 1. 界面跳转到2D库位管理界面<br>2. 渲染逻辑同记忆泊车<br>3. 显示【开始记忆泊车】按键<br>4. 显示已学习的地图区域<br>5. 显示POI信息（出入口、充电桩车位）<br>6. 巡航状态灯置灰 | InterfaceDisTyp=0x1:Pre_Mapbuilt<br>StartPrkBtnDisp=0x1:Available<br>PrkgFuncStsLmp=0x7:HAVP_Standby | 实车测试 | 有图场景2D界面 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-024 | 泊车 | HMI | P0 | 2D地图显示充电桩车位属性 | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面<br>3. 地图中包含充电桩车位 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 查看2D地图<br>2. 检查充电桩车位显示<br>3. 点击充电桩车位查看详情 | 域控发送充电桩车位POI信息 | 1. 2D地图显示充电桩车位图标（明显标识）<br>2. 充电桩车位有专属图标样式<br>3. 点击可查看充电桩车位详细信息<br>4. 充电桩车位数量正确 | 充电桩车位属性POI渲染 | 实车测试 | 充电桩车位显示 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-025 | 泊车 | HMI | P0 | 2D地图显示停车场出入口POI | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 查看2D地图<br>2. 检查出入口POI显示 | 域控发送停车场出入口POI信息 | 1. 2D地图显示停车场出口图标<br>2. 2D地图显示停车场入口图标<br>3. 出入口图标位置准确<br>4. 图标样式清晰可辨 | 出入口POI信息渲染 | 实车测试 | 出入口POI显示 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-026 | 泊车 | HMI | P1 | 无图引导界面进入有图区域自动跳转2D | 1. 车辆处于ready状态<br>2. 显示无图引导界面<br>3. 车辆行驶进入有图停车场 | InterfaceDisTyp=0xF:VLAP without ODD | 1. 车辆驶入有图停车场ODD范围<br>2. 观察界面自动跳转 | 域控识别进入有图区域<br>发送InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 界面自动从无图引导界面跳转到2D库位管理界面<br>2. 显示已学习的地图信息<br>3. 跳转流畅无闪烁 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 实车测试 | 无图转有图自动跳转 | 业务逻辑层 |

### 8. 有图巡航功能开启（6个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-027 | 泊车 | HMI | P0 | 双击拨杆激活巡航-有默认车位 | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面<br>3. 地图中存在默认车位 | InterfaceDisTyp=0x1:Pre_Mapbuilt<br>StartPrkBtnDisp=0x1:Available<br>存在默认车位 | 1. 双击拨杆<br>2. 观察界面跳转和车辆响应 | HUT检测拨杆信号<br>域控发送InterfaceDisTyp=0x3:Cruise | 1. 界面跳转到记忆巡航激活界面<br>2. 巡航标识高亮显示<br>3. 车辆开始向默认车位行驶<br>4. 显示最大车速和实际车速<br>5. 显示规划路径 | InterfaceDisTyp=0x3:Cruise<br>PrkgFuncStsLmp=0x8:HAVP_Active<br>VLAPSpdSetVal=0x14:Twenty | 实车测试 | 拨杆激活巡航 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-028 | 泊车 | HMI | P0 | 语音命中默认车位激活巡航 | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面<br>3. 地图中存在默认车位 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 语音指令"帮我泊入默认车位"<br>2. 观察系统响应和语音反馈 | VLA链路识别命中默认车位<br>域控发送InterfaceDisTyp=0x3:Cruise | 1. 界面跳转到记忆巡航激活界面<br>2. 巡航功能激活<br>3. 车辆开始向默认车位行驶<br>4. 语音播报"好的，正在为您泊入默认车位" | InterfaceDisTyp=0x3:Cruise<br>PrkgFuncStsLmp=0x8:HAVP_Active | 实车测试 | 语音命中默认车位 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-029 | 泊车 | HMI | P0 | 语音命中出入口POI激活巡航 | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面<br>3. 地图中存在出入口POI点 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 语音指令"帮我去停车场出口"<br>2. 观察系统响应 | VLA链路识别命中出口POI<br>域控发送InterfaceDisTyp=0x3:Cruise | 1. 界面跳转到记忆巡航激活界面<br>2. 巡航功能激活<br>3. 车辆开始向出口行驶<br>4. 语音播报"好的，正在为您前往停车场出口" | InterfaceDisTyp=0x3:Cruise<br>PrkgFuncStsLmp=0x8:HAVP_Active | 实车测试 | 语音命中出口POI | 业务逻辑层 |
| BFO-HMI-Thor-VLA-030 | 泊车 | HMI | P0 | 语音命中充电桩车位激活巡航 | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面<br>3. 地图中存在充电桩车位 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 语音指令"帮我泊入充电桩车位"<br>2. 观察系统响应（多个充电桩按最近规划） | VLA链路识别命中充电桩车位<br>域控选择最近充电桩规划<br>发送InterfaceDisTyp=0x3:Cruise | 1. 界面跳转到记忆巡航激活界面<br>2. 巡航功能激活<br>3. 车辆开始向最近的充电桩车位行驶<br>4. 语音播报"好的，正在为您前往充电桩车位"<br>5. 显示规划路径到充电桩车位 | InterfaceDisTyp=0x3:Cruise<br>PrkgFuncStsLmp=0x8:HAVP_Active | 实车测试 | 语音命中充电桩车位 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-031 | 泊车 | HMI | P0 | 语音未命中地图信息转漫游 | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 语音指令"帮我停到B2层"（地图中无B2层）<br>2. 观察系统响应 | VLA链路识别未命中已有信息<br>域控发送InterfaceDisTyp=0x11:VLAP Active Page | 1. 界面跳转到漫游控车界面（非巡航）<br>2. 漫游功能激活<br>3. 车辆开始执行漫游寻找B2层<br>4. 语音播报"好的，正在寻找B2层" | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 实车测试 | 语音未命中转漫游 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-032 | 泊车 | HMI | P0 | 软按键点击激活巡航 | 1. 车辆处于ready状态<br>2. 显示2D库位管理界面<br>3. 【开始记忆泊车】按键可用 | InterfaceDisTyp=0x1:Pre_Mapbuilt<br>StartPrkBtnDisp=0x1:Available | 1. 点击【开始记忆泊车】按键<br>2. 观察系统响应 | HUT发送按键点击信号<br>域控发送InterfaceDisTyp=0x3:Cruise | 1. 界面跳转到记忆巡航激活界面<br>2. 巡航功能激活<br>3. 车辆开始执行巡航任务（优先默认车位） | InterfaceDisTyp=0x3:Cruise<br>PrkgFuncStsLmp=0x8:HAVP_Active | 实车测试 | 软按键激活巡航 | 业务逻辑层 |

请使用以下命令继续生成用例：需要我继续生成剩余部分吗？文档会非常详细和完整。

### 9. 漫游抑制-不使能条件（9个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-033 | 泊车 | HMI | P0 | 四门打开漫游不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 任一车门打开 | InterfaceDisTyp=0x10:VLAP Preactive<br>车门打开 | 1. 尝试双击拨杆或语音激活漫游<br>2. 观察系统响应 | 域控检测车门打开状态<br>功能不进Active | 1. 功能维持Standby状态不激活<br>2. 界面保持漫游泊车人驾界面<br>3. Toast提示"车门打开，记忆泊车暂不可用"<br>4. 直至车门关闭条件恢复 | FunctWorkSts=0x0:Standby<br>InterfaceDisTyp=0x10:VLAP Preactive | 实车测试 | 漫游抑制-车门 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-034 | 泊车 | HMI | P0 | 两盖打开漫游不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 机舱盖或后背门打开 | InterfaceDisTyp=0x10:VLAP Preactive<br>机舱盖或后背门打开 | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测两盖状态 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. Toast提示相应异常<br>4. 直至条件恢复 | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-两盖 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-035 | 泊车 | HMI | P0 | 安全带解开漫游不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 安全带解开 | InterfaceDisTyp=0x10:VLAP Preactive<br>安全带解开 | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测安全带状态 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. Toast提示"未系安全带，记忆泊车暂不可用" | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-安全带 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-036 | 泊车 | HMI | P0 | 后视镜折叠漫游不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 外后视镜折叠 | InterfaceDisTyp=0x10:VLAP Preactive<br>后视镜折叠 | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测后视镜状态 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. Toast提示"后视镜折叠，记忆泊车暂不可用" | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-后视镜 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-037 | 泊车 | HMI | P0 | 车速20-30km/h漫游不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车速在20-30km/h | InterfaceDisTyp=0x10:VLAP Preactive<br>车速>20km/h且<30km/h | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测车速范围 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. 直至车速降低到有效范围 | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-车速 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-038 | 泊车 | HMI | P0 | 坡道大于24%漫游不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车辆位于坡度>24%坡道 | InterfaceDisTyp=0x10:VLAP Preactive<br>坡道>24% | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测坡度 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. Toast提示"请驶离坡道再试" | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-坡道 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-039 | 泊车 | HMI | P1 | 光照雨量条件不满足不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 光照过亮/过暗或雨量过大 | InterfaceDisTyp=0x10:VLAP Preactive<br>光照雨量不满足 | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测光照雨量 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. Toast提示相应异常 | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-光照雨量 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-040 | 泊车 | HMI | P1 | 驾驶模式不满足不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 驾驶模式不满足 | InterfaceDisTyp=0x10:VLAP Preactive<br>驾驶模式不满足 | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测驾驶模式 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. Toast提示"驾驶模式不满足" | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-驾驶模式 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-041 | 泊车 | HMI | P1 | 车辆非静止条件不使能 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车辆在车位内非静止 | InterfaceDisTyp=0x10:VLAP Preactive<br>车辆非静止（车位内） | 1. 尝试激活漫游功能<br>2. 观察系统响应 | 域控检测车辆运动状态 | 1. 功能维持Standby状态<br>2. 界面保持人驾界面<br>3. 直至车辆静止 | FunctWorkSts=0x0:Standby | 实车测试 | 漫游抑制-非静止 | 业务逻辑层 |


### 10. 功能开启异常提示-基础异常（7个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-042 | 泊车 | HMI | P0 | 功能开关关闭Toast提示 | 1. 车辆处于ready状态<br>2. 记忆泊车功能使能开关为关 | 使能开关关闭 | 1. 点击【记忆泊车】按键或语音激活<br>2. 观察提示信息 | 域控发送PopupDisp=0x3:Turn on background functions | 1. 中控屏Toast提示"请先打开记忆泊车功能开关"<br>2. 仪表无报警音效<br>3. VLA链路TTS播报"请先打开记忆泊车功能开关"（语音激活时） | PopupDisp=0x3 | 实车测试 | 功能开关异常 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-043 | 泊车 | HMI | P0 | 坡道过大Toast和音效提示 | 1. 车辆处于ready状态<br>2. 车辆位于坡度>24%的坡道 | 坡道>24%或泊出坡道>15% | 1. 尝试激活漫游功能<br>2. 观察Toast、音效和TTS | 域控发送PopupDisp=0x5:HAVP rampway<br>APS_SysSoundIndcn发送五帧 | 1. 中控屏Toast提示"请驶离坡道再试"<br>2. 仪表播放radarfailure.wav报警音效<br>3. VLA链路TTS播报"请驶离坡道再试"<br>4. 音效APS_SysSoundIndcn=0x1:parking_unavailable | PopupDisp=0x5:HAVP rampway<br>APS_SysSoundIndcn（发送五帧） | 实车测试 | 坡道异常 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-044 | 泊车 | HMI | P0 | ODD范围外Toast提示 | 1. 车辆处于ready状态<br>2. 车辆位于非ODD范围 | 非ODD范围内 | 1. 点击【记忆泊车】按键<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x6:HAVP Environment empty | 1. 中控屏Toast提示"当前环境无法满足功能开启条件"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"当前环境无法满足功能开启条件" | PopupDisp=0x6<br>APS_SysSoundIndcn=0x1 | 实车测试 | ODD范围异常 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-045 | 泊车 | HMI | P0 | 摄像头被遮挡Toast提示 | 1. 车辆处于ready状态<br>2. 摄像头被遮挡 | 摄像头被遮挡 | 1. 尝试激活漫游功能<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x8:HAVP camera blocked | 1. 中控屏Toast提示"摄像头被遮挡，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"摄像头被遮挡，记忆泊车暂不可用" | PopupDisp=0x8<br>APS_SysSoundIndcn=0x1 | 实车测试 | 摄像头遮挡 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-046 | 泊车 | HMI | P0 | 环视摄像头故障Toast提示 | 1. 车辆处于ready状态<br>2. 环视摄像头故障 | 环视摄像头故障 | 1. 尝试激活漫游功能<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x9:HAVP loop camera faulty | 1. 中控屏Toast提示"摄像头故障，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"摄像头故障，记忆泊车暂不可用" | PopupDisp=0x9<br>APS_SysSoundIndcn=0x1 | 实车测试 | 摄像头故障 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-047 | 泊车 | HMI | P0 | 雷达故障Toast提示 | 1. 车辆处于ready状态<br>2. 雷达故障 | 雷达故障 | 1. 尝试激活漫游功能<br>2. 观察Toast和TTS | 域控发送PopupDisp=0xA:HAVP Radar faulty | 1. 中控屏Toast提示"雷达故障，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"雷达故障，记忆泊车暂不可用" | PopupDisp=0xA<br>APS_SysSoundIndcn=0x1 | 实车测试 | 雷达故障 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-048 | 泊车 | HMI | P0 | 关联系统故障Toast提示 | 1. 车辆处于ready状态<br>2. 关联系统故障 | 关联系统故障 | 1. 尝试激活漫游功能<br>2. 观察Toast和TTS | 域控发送PopupDisp=0xB:HAVP Associated system faulty | 1. 中控屏Toast提示"关联系统故障，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"关联系统故障，记忆泊车暂不可用" | PopupDisp=0xB<br>APS_SysSoundIndcn=0x1 | 实车测试 | 关联系统故障 | 业务逻辑层 |


### 11. 功能开启异常-主动安全功能（5个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-049 | 泊车 | HMI | P0 | RCTB/FCTB激活Toast提示 | 1. 车辆处于ready状态<br>2. RCTB/FCTB激活 | RCTB/FCTB激活 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x11:HAVP RCTB/FCTB activation | 1. 中控屏Toast提示"主动安全功能激活，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"主动安全功能激活，记忆泊车暂不可用" | PopupDisp=0x11<br>APS_SysSoundIndcn=0x1 | 实车测试 | RCTB/FCTB激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-050 | 泊车 | HMI | P0 | AEB激活Toast提示 | 1. 车辆处于ready状态<br>2. AEB激活 | AEB激活 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x12:HAVP AEB activation | 1. 中控屏Toast提示"主动安全功能激活，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"主动安全功能激活，记忆泊车暂不可用" | PopupDisp=0x12<br>APS_SysSoundIndcn=0x1 | 实车测试 | AEB激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-051 | 泊车 | HMI | P0 | TCS/ABS激活Toast提示 | 1. 车辆处于ready状态<br>2. TCS/ABS激活 | TCS/ABS激活 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x13:HAVP TCS/ABS activation | 1. 中控屏Toast提示"主动安全功能激活，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"主动安全功能激活，记忆泊车暂不可用" | PopupDisp=0x13<br>APS_SysSoundIndcn=0x1 | 实车测试 | TCS/ABS激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-052 | 泊车 | HMI | P0 | ESP激活Toast提示 | 1. 车辆处于ready状态<br>2. ESP激活 | ESP激活 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x14:HAVP ESP activation | 1. 中控屏Toast提示"主动安全功能激活，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"主动安全功能激活，记忆泊车暂不可用" | PopupDisp=0x14<br>APS_SysSoundIndcn=0x1 | 实车测试 | ESP激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-053 | 泊车 | HMI | P0 | HDC激活Toast提示 | 1. 车辆处于ready状态<br>2. HDC激活 | HDC激活 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x15:HAVP HDC activation | 1. 中控屏Toast提示"主动安全功能激活，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"主动安全功能激活，记忆泊车暂不可用" | PopupDisp=0x15<br>APS_SysSoundIndcn=0x1 | 实车测试 | HDC激活 | 业务逻辑层 |

### 12. 功能开启异常-特殊条件（6个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-054 | 泊车 | HMI | P1 | 胎压异常Toast提示 | 1. 车辆处于ready状态<br>2. 胎压异常 | 胎压异常（暂不监控） | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x16:HAVP Tire pressure is too low | 1. 中控屏Toast提示"胎压异常，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"胎压异常，记忆泊车暂不可用" | PopupDisp=0x16<br>APS_SysSoundIndcn=0x1 | 实车测试 | 胎压异常（预留） | 业务逻辑层 |
| BFO-HMI-Thor-VLA-055 | 泊车 | HMI | P1 | 光照不满足Toast提示 | 1. 车辆处于ready状态<br>2. 光照过亮或过暗 | 光照条件不满足 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x17:HAVP Illumination conditions | 1. 中控屏Toast提示"光照过亮或过暗，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"光照过亮或过暗，系统暂不可用" | PopupDisp=0x17<br>APS_SysSoundIndcn=0x1 | 实车测试 | 光照异常 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-056 | 泊车 | HMI | P1 | 雨量过大Toast提示 | 1. 车辆处于ready状态<br>2. 雨量过大 | 雨量过大 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x18:HAVP Raining conditions | 1. 中控屏Toast提示"雨量过大，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"雨量过大，系统暂不可用" | PopupDisp=0x18<br>APS_SysSoundIndcn=0x1 | 实车测试 | 雨量异常 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-057 | 泊车 | HMI | P0 | N/R档语音激活Toast提示挂D档 | 1. 车辆处于ready状态<br>2. 挡位为N档或R档 | 挡位为N档或R档 | 1. 语音指令激活漫游或巡航<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x1B:Please switch to D gear | 1. 中控屏Toast提示"请先挂入D挡"<br>2. 仪表无报警音效<br>3. VLA链路TTS播报"请先挂入D挡"<br>4. 系统不控车 | PopupDisp=0x1B | 实车测试 | N/R档语音激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-058 | 泊车 | HMI | P0 | 驾驶模式不满足Toast提示 | 1. 车辆处于ready状态<br>2. 驾驶模式不满足 | 驾驶模式不满足 | 1. 尝试激活漫游<br>2. 观察Toast和TTS | 域控发送PopupDisp=0x3B:HAVP Driving Mode not supported | 1. 中控屏Toast提示"驾驶模式不满足，记忆泊车暂不可用"<br>2. 仪表播放radarfailure.wav<br>3. VLA链路TTS播报"驾驶模式不满足，系统暂不可用" | PopupDisp=0x3B<br>APS_SysSoundIndcn=0x1 | 实车测试 | 驾驶模式异常 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-059 | 泊车 | HMI | P0 | 后视镜折叠Toast提示-两种场景 | 1. 车辆处于ready状态<br>2. 后视镜折叠 | 后视镜折叠 | 1. 场景A：在漫游预激活界面尝试激活<br>2. 场景B：在有图场景点击【记忆泊车】<br>3. 观察Toast和界面跳转 | 域控发送PopupDisp=0x3D:HAVP Rearview mirror folded | 场景A：在漫游预激活界面Toast提示"后视镜折叠，记忆泊车暂不可用"<br>场景B：进入2D库位管理界面并Toast提示<br>仪表播放radarfailure.wav<br>VLA链路TTS播报"后视镜折叠，系统暂不可用" | PopupDisp=0x3D<br>APS_SysSoundIndcn=0x1 | 实车测试 | 后视镜折叠 | 业务逻辑层 |


### 15. 静默建图-无图静默建图（4个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-066 | 泊车 | HMI | P0 | 人驾界面实时渲染感知元素 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车辆在停车场行驶 | InterfaceDisTyp=0x10:VLAP Preactive<br>FunctWorkSts=0x0:Standby<br>PrkgFuncStsLmp=0x2 | 1. 车辆行驶经过各类感知对象<br>2. 验证各元素实时渲染效果 | 域控持续发送感知数据<br>APS_PASSwtReq=0x2:Request to open | 1. 立柱实时渲染（位置、形状）<br>2. 车位实时显示（含车头车尾方向）<br>3. 道路箭头实时显示（地面方向标识）<br>4. 行人实时渲染（动态跟踪）<br>5. 车辆实时渲染（颜色、朝向）<br>6. 减速带位置准确显示<br>7. 学习轨迹实时更新（绿色线条）<br>8. 缩略态map显示行驶轨迹（范围100米） | 所有感知元素渲染准确 | 实车测试 | 静默建图渲染完整性 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-067 | 泊车 | HMI | P0 | 人驾界面状态灯置灰显示 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面 | InterfaceDisTyp=0x10:VLAP Preactive<br>FunctWorkSts=0x0:Standby | 1. 检查状态灯显示位置<br>2. 验证状态灯样式和颜色 | PrkgFuncStsLmp=0x2:VLAP_Roaming_Standby（CAN信号） | 1. 中控屏显示漫游状态灯<br>2. 状态灯呈置灰样式<br>3. 状态灯仅在中控显示（不在仪表）<br>4. 状态灯位置符合UI设计 | PrkgFuncStsLmp=0x2（CAN信号，仅中控） | 实车测试 | 静默建图状态灯 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-068 | 泊车 | HMI | P1 | 人驾界面缩略态map范围验证 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 车辆已行驶超过100米 | InterfaceDisTyp=0x10:VLAP Preactive | 1. 观察缩略态map显示范围<br>2. 验证地图局部展示逻辑 | 域控发送全量地图数据<br>HUT进行局部展示（约100米范围） | 1. 缩略态map显示行驶过的道路线<br>2. 显示范围约100米（域控全量，HUT局部）<br>3. 地图随车辆移动实时更新<br>4. 超出范围的轨迹不显示 | HUT侧局部展示逻辑 | 实车测试 | 缩略态map范围 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-069 | 泊车 | HMI | P1 | 人驾界面AVM自动悬浮显示 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面 | InterfaceDisTyp=0x10:VLAP Preactive<br>APS_PASSwtReq=0x2:Request to open | 1. 车辆切换到APA泊车或R挡或转向等<br>2. 观察AVM悬浮显示 | APS_PASSwtReq持续发送请求 | 1. 360全景影像视图自动悬浮显示<br>2. 复用记忆泊车视频展示<br>3. AVM显示清晰无延迟 | APS_PASSwtReq=0x2持续发送 | 实车测试 | AVM自动悬浮 | 业务逻辑层 |

### 16. 静默建图-无图漫游控车（5个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-070 | 泊车 | HMI | P0 | 漫游控车界面完整元素渲染 | 1. 车辆处于ready状态<br>2. 无图漫游已激活<br>3. 车辆漫游控车中 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming<br>PrkgFuncStsLmp=0x4 | 1. 检查漫游控车界面所有元素<br>2. 验证实时渲染效果 | 域控持续发送感知、规划数据<br>AlongToutPrkgBtnSts=0x1<br>VLAPSpdSetVal=0x14 | 1. 360全景影像自动悬浮<br>2. 缩略态实时路线显示<br>3. 自车位置实时更新<br>4. 感知元素（立柱、车位、道路箭头、行人、车辆、减速带）实时渲染<br>5. 历史轨迹和局部规划轨迹显示<br>6. 缩略态map实时更新<br>7. 状态灯高亮<br>8. 【沿途泊车】按键显示<br>9. COT推理面板显示<br>10. 最大车速和实际车速显示 | 所有元素完整渲染 | 实车测试 | 漫游控车完整渲染 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-071 | 泊车 | HMI | P0 | 漫游控车状态灯高亮显示 | 1. 车辆处于ready状态<br>2. 漫游已激活 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 1. 检查状态灯显示状态<br>2. 验证状态灯高亮效果 | PrkgFuncStsLmp=0x4:VLAP_Roaming_Active | 1. 中控屏显示漫游状态灯<br>2. 状态灯呈高亮样式<br>3. 状态灯仅在中控显示<br>4. 状态灯位置和样式正确 | PrkgFuncStsLmp=0x4（CAN信号） | 实车测试 | 漫游激活状态灯 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-072 | 泊车 | HMI | P0 | 漫游油门override状态灯闪烁 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 车辆漫游控车中 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 1. 用户踩油门干预<br>2. 观察状态灯变化<br>3. 松开油门后观察恢复 | 域控检测油门override<br>发送PrkgFuncStsLmp=0x6:VLAP_Crusing_Override | 1. 用户踩油门时，状态灯高亮闪烁<br>2. 闪烁频率符合设计规范<br>3. 松开油门后，状态灯恢复高亮常亮 | PrkgFuncStsLmp=0x6（CAN信号） | 实车测试 | 油门override闪烁 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-073 | 泊车 | HMI | P0 | 漫游速度设置范围限制验证 | 1. 车辆处于ready状态<br>2. 漫游已激活 | InterfaceDisTyp=0x11:VLAP Active Page<br>VLAPSpdSetVal当前值 | 1. 尝试设置速度<10km/h<br>2. 尝试设置速度>20km/h<br>3. 观察系统响应和提示 | 速度设置超出10~20km/h范围<br>域控发送VLA链路提示 | 1. 设置速度<10km/h时系统拒绝，显示提示<br>2. 设置速度>20km/h时系统拒绝，显示提示<br>3. VLA链路显示速度范围限制提示<br>4. 速度保持在有效范围10~20km/h内 | VLAPSpdSetVal范围限制10~20km/h | 实车测试 | 速度范围限制 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-074 | 泊车 | HMI | P0 | 漫游中常驻文言变更验证 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 车辆漫游控车中 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 1. 检查常驻文言显示<br>2. 验证信号值为0xC4（非0x2E）<br>3. 验证文言内容 | 域控发送HAVPFunctTextDisp=0xC4（文言："车辆漫游中，请注意周围环境"）:HAVP Roaming | 1. 界面显示常驻文言"车辆漫游中，请注意周围环境"<br>2. 文言信号值确认为0xC4（⚠️变更3：非0x2E）<br>3. 文言常驻显示在固定位置<br>4. 文言可被其他文言临时打断 | HAVPFunctTextDisp=0xC4（文言："车辆漫游中，请注意周围环境"）:HAVP Roaming | 实车测试 | ⚠️变更3-漫游文言0xC4 | 业务逻辑层 |


### 17. 静默建图完成与保存-⚠️变更2重点（6个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-075 | 泊车 | HMI | P0 | 手动泊入后弹窗15s保存地图 | 1. 车辆处于ready状态<br>2. 无图漫游完成<br>3. 静默建图开关开启<br>4. 手动泊入车位 | 静默建图完成 | 1. 手动泊入车位后挂P挡<br>2. 观察弹窗显示<br>3. 使用计时器验证弹窗时间 | 域控发送HAVPFunctTextDisp=0xBA（文言："泊车已完成"）:Parking in complete<br>PopupDisp=0x3F:HAVP_Push_Request | 1. 中控屏显示文言"泊车已完成"<br>2. 弹窗提示"是否保存地图"<br>3. 弹窗显示时间为15s（⚠️变更2：非10s）<br>4. 弹窗包含【保存】和【取消】按键<br>5. 显示倒计时或进度提示 | HAVPFunctTextDisp=0xBA（文言："泊车已完成"）<br>PopupDisp=0x3F（持续15s） | 实车测试 | ⚠️变更2-弹窗15s | 业务逻辑层 |
| BFO-HMI-Thor-VLA-076 | 泊车 | HMI | P0 | 沿途泊车自动泊入后弹窗15s | 1. 车辆处于ready状态<br>2. 无图漫游完成<br>3. 通过【沿途泊车】自动泊入 | 静默建图完成<br>APA自动泊入完成 | 1. 车辆自动泊入车位后挂P挡<br>2. 观察弹窗显示<br>3. 使用计时器验证15s | 域控发送HAVPFunctTextDisp=0xBA（文言："泊车已完成"）<br>PopupDisp=0x3F | 1. 中控屏显示文言"泊车已完成"<br>2. 弹窗提示"是否保存地图"<br>3. 弹窗显示时间为15s（⚠️变更2）<br>4. 弹窗包含【保存】和【取消】按键 | HAVPFunctTextDisp=0xBA（文言："泊车已完成"）<br>PopupDisp=0x3F（持续15s） | 实车测试 | ⚠️变更2-自动泊入弹窗 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-077 | 泊车 | HMI | P0 | 点击保存按键成功保存地图 | 1. 车辆处于ready状态<br>2. 显示保存地图弹窗 | 弹窗显示中 | 1. 点击【保存】按键<br>2. 观察系统响应和界面跳转 | HUT发送BtnEnaReq=0x3<br>域控保存地图<br>发送HAVPFunctTextDisp=0x4B（文言："巡航中系统故障"）:Save_Success | 1. 弹窗消失<br>2. Toast提示"保存成功"<br>3. 界面跳转到2D库位管理页面<br>4. 显示已保存的完整地图数据<br>5. 【开始记忆泊车】按键可用 | InterfaceDisTyp=0x1:Pre_Mapbuilt<br>HAVPFunctTextDisp=0x4B（文言："巡航中系统故障"）<br>StartPrkBtnDisp=0x1:Available | 实车测试 | 保存成功场景 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-078 | 泊车 | HMI | P0 | 点击取消按键放弃保存 | 1. 车辆处于ready状态<br>2. 显示保存地图弹窗 | 弹窗显示中 | 1. 点击【取消】按键<br>2. 观察系统响应和界面跳转 | HUT发送BtnEnaReq=0x5:Cancel<br>域控放弃路线保存 | 1. 弹窗立即消失<br>2. 界面跳转到HUT主界面<br>3. 地图未保存<br>4. 无保存成功提示 | 域控放弃保存 | 实车测试 | 取消保存场景 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-079 | 泊车 | HMI | P0 | 弹窗15s未点击自动放弃保存 | 1. 车辆处于ready状态<br>2. 显示保存地图弹窗 | 弹窗显示中 | 1. 不进行任何操作<br>2. 使用计时器验证15s超时<br>3. 观察系统自动响应 | 15s倒计时结束<br>域控自动放弃路线保存 | 1. 弹窗15s后自动消失（⚠️变更2：非10s）<br>2. 界面跳转到HUT主界面<br>3. 地图未保存<br>4. 无需用户操作 | 15s超时自动放弃 | 实车测试 | ⚠️变更2-超时15s | 业务逻辑层 |
| BFO-HMI-Thor-VLA-080 | 泊车 | HMI | P1 | 保存成功后地图数据完整性验证 | 1. 车辆处于ready状态<br>2. 地图保存成功<br>3. 显示2D库位管理页面 | InterfaceDisTyp=0x1:Pre_Mapbuilt<br>地图已保存 | 1. 检查2D地图显示完整性<br>2. 验证POI信息准确性<br>3. 检查【开始记忆泊车】按键状态 | 域控发送完整地图数据<br>StartPrkBtnDisp=0x1:Available | 1. 显示完整的地图区域<br>2. 显示出入口等POI信息<br>3. 显示充电桩车位（如有）<br>4. 【开始记忆泊车】按键可用<br>5. 地图数据与实际学习路线一致 | 地图数据完整性验证通过 | 实车测试 | 地图完整性验证 | 业务逻辑层 |


### 18. 沿途泊车功能（6个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-081 | 泊车 | HMI | P0 | 沿途泊车按键可用状态显示 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 非沿途找车位状态 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming<br>非沿途找车位状态 | 1. 检查【沿途泊车】按键显示<br>2. 验证按键可点击状态 | AlongToutPrkgBtnSts=0x1:Available | 1. 【沿途泊车】按键显示在界面上<br>2. 按键呈可点击态（颜色正常）<br>3. 按键位置和样式符合UI设计 | AlongToutPrkgBtnSts=0x1:Available | 实车测试 | 沿途泊车按键-可用 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-082 | 泊车 | HMI | P0 | 沿途泊车按键不显示场景 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 已处于沿途找车位状态或漫游暂停 | InterfaceDisTyp=0x11:VLAP Active Page<br>AlongToutPrkgBtnSts=0x0:No_Display | 1. 点击【沿途泊车】后检查按键<br>2. 或进入暂停状态检查按键 | 沿途找车位执行中或暂停状态 | 1. 【沿途泊车】按键不显示<br>2. 沿途找车位时显示"正在寻找车位"文言<br>3. 暂停时显示【继续】按键 | AlongToutPrkgBtnSts=0x0:No_Display | 实车测试 | 沿途泊车按键-不显示 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-083 | 泊车 | HMI | P0 | 点击沿途泊车按键激活寻找车位 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 【沿途泊车】按键可用 | InterfaceDisTyp=0x11:VLAP Active Page<br>AlongToutPrkgBtnSts=0x1:Available | 1. 点击【沿途泊车】按键<br>2. 观察系统响应和文言提示 | HUT发送BtnEnaReq=0x10:VLAP parking Nearby<br>域控反馈HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"）:Searching parkspace | 1. 系统开始沿途寻找车位<br>2. 界面显示文言"正在寻找车位"（常驻）<br>3. 文言可被其他文言打断<br>4. 【沿途泊车】按键不再显示<br>5. 车辆开始沿途寻车位动作 | HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"）:Searching parkspace<br>AlongToutPrkgBtnSts=0x0 | 实车测试 | 点击沿途泊车 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-084 | 泊车 | HMI | P0 | 语音沿途泊车激活寻找车位 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 【沿途泊车】按键可用 | InterfaceDisTyp=0x11:VLAP Active Page | 1. 语音指令"沿途泊车"或"就近泊车"<br>2. 观察系统响应和语音反馈 | VLA链路识别沿途泊车指令<br>HUT发送BtnEnaReq=0x10<br>域控反馈HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"） | 1. 系统开始沿途寻找车位<br>2. 语音播报确认信息<br>3. 界面显示文言"正在寻找车位"<br>4. 【沿途泊车】按键不再显示 | HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"）<br>AlongToutPrkgBtnSts=0x0 | 实车测试 | 语音沿途泊车 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-085 | 泊车 | HMI | P0 | 沿途泊车发现车位自动切换APA | 1. 车辆处于ready状态<br>2. 沿途泊车寻找车位中 | HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"）:Searching parkspace<br>FunctWorkSts=0x9:VLAP Roaming | 1. 系统沿途发现可泊入车位<br>2. 观察界面变化和车辆动作 | 域控发送APS_Worksts=0x3:Guidence<br>InterfaceDisTyp保持=0x11:VLAP Active<br>FunctWorkSts切换到0xA:VLAP Parking | 1. 系统自动切换至APA泊车过程<br>2. 界面渲染APA泊车引导画面<br>3. 车辆开始自动泊入动作<br>4. COT推理面板不再显示（FunctWorkSts=0xA）<br>5. 显示APA泊车引导信息 | APS_Worksts=0x3:Guidence<br>FunctWorkSts=0xA:VLAP Parking<br>InterfaceDisTyp=0x11 | 实车测试 | 沿途泊车切换APA | 业务逻辑层 |
| BFO-HMI-Thor-VLA-086 | 泊车 | HMI | P1 | 沿途泊车找车位过程文言常驻 | 1. 车辆处于ready状态<br>2. 沿途泊车寻找车位中 | HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"）:Searching parkspace | 1. 观察"正在寻找车位"文言显示<br>2. 观察其他文言打断效果 | 沿途泊车找车位周期内 | 1. 文言"正在寻找车位"常驻显示<br>2. 可被其他高优文言打断<br>3. 打断后可恢复显示 | HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"）常驻 | 实车测试 | 文言常驻逻辑 | 业务逻辑层 |

### 19. 漫游暂停与继续（5个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-087 | 泊车 | HMI | P0 | 语音指令暂停漫游 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 车辆漫游控车中 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0x9:VLAP Roaming | 1. 语音指令"帮我停车"或"刹停"<br>2. 观察系统响应和界面变化 | VLA链路识别暂停指令<br>域控发送FunctWorkSts=0xB:VLAP Pause<br>FunctBtnDisp=0x2:Continue_HAVP | 1. 车辆减速刹停保压<br>2. 界面显示【继续】按键<br>3. 【沿途泊车】按键不显示<br>4. 漫游标识保持高亮<br>5. 漫游速度设置显示为0<br>6. COT推理面板保持显示 | FunctWorkSts=0xB:VLAP Pause<br>FunctBtnDisp=0x2<br>AlongToutPrkgBtnSts=0x0<br>VLAPSpdSetVal=0 | 实车测试 | 语音暂停漫游 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-088 | 泊车 | HMI | P0 | 点击继续按键恢复漫游 | 1. 车辆处于ready状态<br>2. 漫游暂停状态<br>3. 显示【继续】按键 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0xB:VLAP Pause<br>FunctBtnDisp=0x2:Continue_HAVP | 1. 点击【继续】按键<br>2. 观察系统响应和界面变化 | HUT发送BtnEnaReq=0xF:Continue_VLAP<br>域控恢复FunctWorkSts=0x9:VLAP Roaming | 1. 车辆继续漫游<br>2. 【继续】按键消失<br>3. 【沿途泊车】按键恢复显示（保持暂停前状态）<br>4. 漫游速度设置恢复显示<br>5. COT推理面板继续更新 | FunctWorkSts=0x9:VLAP Roaming<br>沿途泊车按键状态保持暂停前 | 实车测试 | 点击继续漫游 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-089 | 泊车 | HMI | P0 | 语音指令继续漫游 | 1. 车辆处于ready状态<br>2. 漫游暂停状态 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0xB:VLAP Pause | 1. 语音指令"继续漫游"或"继续巡航"<br>2. 观察系统响应和语音反馈 | VLA链路识别继续指令<br>域控恢复FunctWorkSts=0x9 | 1. 车辆继续漫游<br>2. 【继续】按键消失<br>3. 【沿途泊车】按键恢复显示<br>4. 语音播报"好的，继续为您漫游"<br>5. 速度设置恢复 | FunctWorkSts=0x9:VLAP Roaming | 实车测试 | 语音继续漫游 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-090 | 泊车 | HMI | P1 | 暂停状态沿途泊车按键不显示 | 1. 车辆处于ready状态<br>2. 漫游已激活并暂停 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0xB:VLAP Pause | 1. 检查【沿途泊车】按键显示状态<br>2. 检查【继续】按键显示 | AlongToutPrkgBtnSts=0x0:No_Display<br>FunctBtnDisp=0x2:Continue_HAVP | 1. 【沿途泊车】按键不显示<br>2. 【继续】按键显示<br>3. 暂停状态下不能操作沿途泊车 | 暂停状态按键逻辑 | 实车测试 | 暂停状态按键 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-091 | 泊车 | HMI | P0 | 暂停超时3分钟自动退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游暂停状态<br>3. 暂停接近3分钟 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0xB:VLAP Pause | 1. 不进行任何操作<br>2. 等待超过3分钟<br>3. 使用计时器验证超时<br>4. 观察系统自动响应 | 暂停超过3分钟<br>域控发送HAVPFunctTextDisp=0xB7:Pause overtime_sys_exit<br>PopupDisp=0x20:take over immediately | 1. 系统请求底盘挂P档<br>2. 系统拉起EPB<br>3. 显示文言"暂停超时，系统退出"<br>4. 显示"请立即接管"大弹窗<br>5. 播放接管音效CruiseTakeOverLV31声<br>6. 3s后功能退出，退回到HUT主界面 | HAVPFunctTextDisp=0xB7<br>PopupDisp=0x20<br>3s后退到主界面 | 实车测试 | 暂停超时自动退出 | 业务逻辑层 |


### 20. 漫游异常退出-四门两盖-⚠️变更1重点（10个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-092 | 泊车 | HMI | P0 | 无图漫游中打开机舱盖退出到预激活 | 1. 车辆处于ready状态<br>2. 无图漫游已激活<br>3. 车辆漫游控车中 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0x9:VLAP Roaming | 1. 打开机舱盖<br>2. 观察弹窗、音效和界面跳转<br>3. 验证退出界面正确性 | 域控检测机舱盖打开<br>发送HAVPFunctTextDisp=0x3F（文言："巡航中机舱盖打开"）:Crusing Engine hood open<br>PopupDisp=0x20:take over immediately | 1. 显示文言"巡航中机舱盖打开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效CruiseTakeOverLV31声<br>4. 3s后退出到漫游预激活界面（⚠️变更1：InterfaceDisTyp=0x10） | HAVPFunctTextDisp=0x3F（文言："巡航中机舱盖打开"）<br>PopupDisp=0x20<br>⚠️变更1：退到0x10 | 实车测试 | ⚠️变更1-机舱盖退预激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-093 | 泊车 | HMI | P0 | 有图巡航中打开机舱盖退出到主界面 | 1. 车辆处于ready状态<br>2. 有图巡航已激活<br>3. 车辆巡航控车中 | InterfaceDisTyp=0x3:Cruise<br>FunctWorkSts≠0x0 | 1. 打开机舱盖<br>2. 观察弹窗、音效和界面跳转<br>3. 验证退出界面正确性 | 域控检测机舱盖打开<br>发送HAVPFunctTextDisp=0x3F（文言："巡航中机舱盖打开"）<br>PopupDisp=0x20 | 1. 显示文言"巡航中机舱盖打开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面（⚠️变更1：非预激活界面） | HAVPFunctTextDisp=0x3F（文言："巡航中机舱盖打开"）<br>PopupDisp=0x20<br>⚠️变更1：退到主界面 | 实车测试 | ⚠️变更1-机舱盖退主界面 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-094 | 泊车 | HMI | P0 | 无图漫游中打开后背门退出到预激活 | 1. 车辆处于ready状态<br>2. 无图漫游已激活 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0x9 | 1. 打开后背门<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x40（文言："巡航中后背门打开"）:Crusing Trunk open<br>PopupDisp=0x20 | 1. 显示文言"巡航中后背门打开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到漫游预激活界面 | HAVPFunctTextDisp=0x40（文言："巡航中后背门打开"）<br>⚠️变更1：退到0x10 | 实车测试 | ⚠️变更1-后背门退预激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-095 | 泊车 | HMI | P0 | 有图巡航中打开后背门退出到主界面 | 1. 车辆处于ready状态<br>2. 有图巡航已激活 | InterfaceDisTyp=0x3:Cruise | 1. 打开后背门<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x40（文言："巡航中后背门打开"）<br>PopupDisp=0x20 | 1. 显示文言"巡航中后背门打开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x40（文言："巡航中后背门打开"）<br>⚠️变更1：退到主界面 | 实车测试 | ⚠️变更1-后背门退主界面 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-096 | 泊车 | HMI | P0 | 无图漫游中打开车门退出到预激活 | 1. 车辆处于ready状态<br>2. 无图漫游已激活 | InterfaceDisTyp=0x11:VLAP Active | 1. 打开车门<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x41（文言："巡航中车门打开"）:Crusing Door open<br>PopupDisp=0x20 | 1. 显示文言"巡航中车门打开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到漫游预激活界面 | HAVPFunctTextDisp=0x41（文言："巡航中车门打开"）<br>⚠️变更1：退到0x10 | 实车测试 | ⚠️变更1-车门退预激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-097 | 泊车 | HMI | P0 | 有图巡航中打开车门退出到主界面 | 1. 车辆处于ready状态<br>2. 有图巡航已激活 | InterfaceDisTyp=0x3:Cruise | 1. 打开车门<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x41（文言："巡航中车门打开"）<br>PopupDisp=0x20 | 1. 显示文言"巡航中车门打开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x41（文言："巡航中车门打开"）<br>⚠️变更1：退到主界面 | 实车测试 | ⚠️变更1-车门退主界面 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-098 | 泊车 | HMI | P0 | 无图漫游中折叠后视镜退出到预激活 | 1. 车辆处于ready状态<br>2. 无图漫游已激活 | InterfaceDisTyp=0x11:VLAP Active | 1. 折叠外后视镜<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x42（文言："巡航中后视镜折叠"）:Crusing Rearview mirror fold<br>PopupDisp=0x20 | 1. 显示文言"巡航中后视镜折叠"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到漫游预激活界面 | HAVPFunctTextDisp=0x42（文言："巡航中后视镜折叠"）<br>⚠️变更1：退到0x10 | 实车测试 | ⚠️变更1-后视镜退预激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-099 | 泊车 | HMI | P0 | 有图巡航中折叠后视镜退出到主界面 | 1. 车辆处于ready状态<br>2. 有图巡航已激活 | InterfaceDisTyp=0x3:Cruise | 1. 折叠外后视镜<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x42（文言："巡航中后视镜折叠"）<br>PopupDisp=0x20 | 1. 显示文言"巡航中后视镜折叠"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x42（文言："巡航中后视镜折叠"）<br>⚠️变更1：退到主界面 | 实车测试 | ⚠️变更1-后视镜退主界面 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-100 | 泊车 | HMI | P0 | 无图漫游中解开安全带退出到预激活 | 1. 车辆处于ready状态<br>2. 无图漫游已激活 | InterfaceDisTyp=0x11:VLAP Active | 1. 解开安全带<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x43（文言："巡航中安全带解开"）:Crusing Seat belt loosen<br>PopupDisp=0x20 | 1. 显示文言"巡航中安全带解开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到漫游预激活界面 | HAVPFunctTextDisp=0x43（文言："巡航中安全带解开"）<br>⚠️变更1：退到0x10 | 实车测试 | ⚠️变更1-安全带退预激活 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-101 | 泊车 | HMI | P0 | 有图巡航中解开安全带退出到主界面 | 1. 车辆处于ready状态<br>2. 有图巡航已激活 | InterfaceDisTyp=0x3:Cruise | 1. 解开安全带<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x43（文言："巡航中安全带解开"）<br>PopupDisp=0x20 | 1. 显示文言"巡航中安全带解开"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x43（文言："巡航中安全带解开"）<br>⚠️变更1：退到主界面 | 实车测试 | ⚠️变更1-安全带退主界面 | 业务逻辑层 |


### 21. 漫游异常退出-系统和环境异常-⚠️变更1重点（12个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-102 | 泊车 | HMI | P0 | 漫游或巡航中绕行障碍物空间不足退出 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 遇到不可移动障碍物 | InterfaceDisTyp=0x11或0x3<br>绕行空间不足 | 1. 系统检测绕行障碍物空间不足持续30s<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x46（文言："绕行障碍物空间不足"）:Statistic Obstacle 30s<br>PopupDisp=0x20 | 1. 显示文言"绕行障碍物空间不足"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后：无图漫游退到预激活界面，有图巡航退到主界面 | HAVPFunctTextDisp=0x46（文言："绕行障碍物空间不足"）<br>⚠️变更1：区分退出界面 | 实车测试 | ⚠️变更1-障碍物退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-103 | 泊车 | HMI | P0 | 漫游或巡航中定位失败退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活 | InterfaceDisTyp=0x11或0x3 | 1. 系统定位失败<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x48（文言："定位失败"）:Positioning Unsuccessful<br>PopupDisp=0x20 | 1. 显示文言"定位失败"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x48（文言："定位失败"）<br>PopupDisp=0x20<br>退到主界面 | 实车测试 | 定位失败退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-104 | 泊车 | HMI | P0 | 巡航中光照不满足退出到主界面 | 1. 车辆处于ready状态<br>2. 巡航或巡航APA已激活<br>3. 光照条件突变 | InterfaceDisTyp=0x3:Cruise或巡航APA | 1. 光照条件突然不满足<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x49（文言："巡航中光照不满足"）:Crusing Illumination conditions<br>PopupDisp=0x20 | 1. 显示文言"巡航中光照不满足"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x49（文言："巡航中光照不满足"）<br>退到主界面 | 实车测试 | 光照异常退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-105 | 泊车 | HMI | P0 | 巡航中雨量过大退出到主界面 | 1. 车辆处于ready状态<br>2. 巡航或巡航APA已激活<br>3. 雨量突然增大 | InterfaceDisTyp=0x3:Cruise或巡航APA | 1. 雨量过大<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x4A（文言："巡航中雨量过大"）:Crusing Raining conditions<br>PopupDisp=0x20 | 1. 显示文言"巡航中雨量过大"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x4A（文言："巡航中雨量过大"）<br>退到主界面 | 实车测试 | 雨量异常退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-106 | 泊车 | HMI | P0 | 漫游或巡航中系统故障退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活 | InterfaceDisTyp=0x11或0x3 | 1. 系统发生LVP故障<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x4B（文言："巡航中系统故障"）:Crusing LVP Failure<br>PopupDisp=0x20 | 1. 显示文言"巡航中系统故障"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x4B（文言："巡航中系统故障"）<br>退到主界面 | 实车测试 | 系统故障退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-107 | 泊车 | HMI | P0 | 漫游或巡航中关联系统故障退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活 | InterfaceDisTyp=0x11或0x3 | 1. 关联系统发生故障<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x4C（文言："巡航中关联系统故障"）:Crusing Associated System Failure<br>PopupDisp=0x20 | 1. 显示文言"巡航中关联系统故障"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x4C（文言："巡航中关联系统故障"）<br>退到主界面 | 实车测试 | 关联系统故障退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-108 | 泊车 | HMI | P0 | 漫游超时10分钟退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 漫游接近10分钟 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0x9 | 1. 漫游时间达到10分钟<br>2. 使用计时器验证<br>3. 观察弹窗和界面跳转 | 漫游超过10分钟<br>域控发送HAVPFunctTextDisp=0x4D（文言："巡航超时"）:Crusing Time out<br>PopupDisp=0x20 | 1. 显示文言"巡航超时"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x4D（文言："巡航超时"）<br>退到主界面 | 实车测试 | 漫游超时退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-109 | 泊车 | HMI | P0 | 漫游APA泊车超时4分钟退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. APA泊车过程超时 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0xA:VLAP Parking<br>APA泊车接近4分钟 | 1. APA泊车时间达到4分钟<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x4E（文言："泊车超时"）:Parking Time out<br>PopupDisp=0x20 | 1. 显示文言"泊车超时"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x4E（文言："泊车超时"）<br>退到主界面 | 实车测试 | APA超时退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-110 | 泊车 | HMI | P1 | 漫游APA暂停次数超限退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游APA阶段<br>3. 暂停次数接近上限 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0xA<br>APA暂停次数接近上限 | 1. APA暂停次数超限<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x4F（文言："暂停次数超限"）:Number of pauses exceeded<br>PopupDisp=0x20 | 1. 显示文言"暂停次数超限"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x4F（文言："暂停次数超限"）<br>退到主界面 | 实车测试 | 暂停次数超限 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-111 | 泊车 | HMI | P1 | 续航不足退出到主界面（不开发） | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 车辆续航不足 | InterfaceDisTyp=0x11或0x3<br>续航不足 | 1. 车辆续航低于阈值<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x50（文言："续航不足"）:Vehicle range too low<br>PopupDisp=0x20 | 1. 显示文言"续航不足"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x50（文言："续航不足"）<br>退到主界面（纯电车型，不开发） | 实车测试 | 续航不足（预留） | 业务逻辑层 |


### 22. 漫游异常退出-主动安全功能（5个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-114 | 泊车 | HMI | P0 | RCTB/FCTB激活退出到主界面 | 1. 车辆处于ready状态<br>2. 全功能漫游或巡航已激活<br>3. RCTB/FCTB激活 | InterfaceDisTyp=0x11或0x3<br>RCTB/FCTB激活 | 1. RCTB/FCTB激活<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x51（文言："主动安全功能激活"）:Crusing RCTB/FCTB activation<br>PopupDisp=0x20 | 1. 显示文言"主动安全功能激活"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x51（文言："主动安全功能激活"）<br>退到主界面 | 实车测试 | RCTB/FCTB激活退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-115 | 泊车 | HMI | P0 | AEB激活退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. AEB激活 | AEB激活 | 1. AEB激活<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x52（文言："主动安全功能激活"）:Crusing AEB activation<br>PopupDisp=0x20 | 1. 显示文言"主动安全功能激活"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x52（文言："主动安全功能激活"）<br>退到主界面 | 实车测试 | AEB激活退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-116 | 泊车 | HMI | P0 | ESP激活退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. ESP激活 | ESP激活 | 1. ESP激活<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x53（文言："主动安全功能激活"）:Crusing ESP activation<br>PopupDisp=0x20 | 1. 显示文言"主动安全功能激活"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x53（文言："主动安全功能激活"）<br>退到主界面 | 实车测试 | ESP激活退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-117 | 泊车 | HMI | P0 | TCS/ABS激活退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. TCS/ABS激活 | TCS/ABS激活 | 1. TCS/ABS激活<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x54（文言："主动安全功能激活"）:Crusing TCS/ABS activation<br>PopupDisp=0x20 | 1. 显示文言"主动安全功能激活"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x54（文言："主动安全功能激活"）<br>退到主界面 | 实车测试 | TCS/ABS激活退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-118 | 泊车 | HMI | P0 | HDC激活退出到主界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. HDC激活 | HDC激活 | 1. HDC激活<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x55（文言："主动安全功能激活"）:Crusing HDC activation<br>PopupDisp=0x20 | 1. 显示文言"主动安全功能激活"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后退出到HUT主界面 | HAVPFunctTextDisp=0x55（文言："主动安全功能激活"）<br>退到主界面 | 实车测试 | HDC激活退出 | 业务逻辑层 |


### 23. 漫游异常退出-用户干预-⚠️变更1重点（9个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-119 | 泊车 | HMI | P0 | 巡航中EPB干预退出到预激活界面 | 1. 车辆处于ready状态<br>2. 巡航或巡航APA已激活 | InterfaceDisTyp=0x3:Cruise或巡航APA | 1. 拉起EPB<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x61（文言："EPB干预"）:Pull up EPB | 1. 显示文言"巡航中EPB干预"<br>2. 可能显示"请立即接管"弹窗<br>3. 退出到漫游预激活界面（⚠️变更1） | HAVPFunctTextDisp=0x61（文言："EPB干预"）<br>⚠️变更1：退到0x10 | 实车测试 | ⚠️变更1-EPB干预 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-120 | 泊车 | HMI | P0 | 巡航中档位干预退出到预激活界面 | 1. 车辆处于ready状态<br>2. 巡航或巡航APA已激活 | InterfaceDisTyp=0x3:Cruise或巡航APA | 1. 切换挡位干预<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x62（文言："档位干预"）:gear intervene | 1. 显示文言"巡航中档位干预"<br>2. 退出到漫游预激活界面（⚠️变更1：无图）<br>3. 或退出到HUT主界面（有图） | HAVPFunctTextDisp=0x62（文言："档位干预"）<br>⚠️变更1：区分退出界面 | 实车测试 | ⚠️变更1-档位干预 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-121 | 泊车 | HMI | P0 | 巡航中方向盘干预退出到预激活界面 | 1. 车辆处于ready状态<br>2. 巡航或巡航APA已激活 | InterfaceDisTyp=0x3:Cruise或巡航APA | 1. 转动方向盘干预<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x63（文言："方向盘干预"）:steering intervene | 1. 显示文言"巡航中方向盘干预"<br>2. 退出到漫游预激活界面（⚠️变更1：无图）<br>3. 或退出到HUT主界面（有图） | HAVPFunctTextDisp=0x63（文言："方向盘干预"）<br>⚠️变更1：区分退出界面 | 实车测试 | ⚠️变更1-方向盘干预 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-122 | 泊车 | HMI | P0 | 巡航中踩刹车退出到预激活界面 | 1. 车辆处于ready状态<br>2. 巡航已激活（非APA） | InterfaceDisTyp=0x3:Cruise<br>非APA状态 | 1. 踩刹车干预<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x64（文言："刹车干预"）:brake intervene | 1. 显示文言"巡航中刹车干预"<br>2. 巡航功能退出<br>3. 退出到漫游预激活界面（⚠️变更1：无图）<br>4. 或退出到HUT主界面（有图） | HAVPFunctTextDisp=0x64（文言："刹车干预"）<br>⚠️变更1：区分退出界面 | 实车测试 | ⚠️变更1-刹车干预 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-123 | 泊车 | HMI | P0 | 巡航中主动退出到主界面 | 1. 车辆处于ready状态<br>2. 巡航或巡航APA已激活 | InterfaceDisTyp=0x3:Cruise | 1. 点击【退出】按键或语音"退出"<br>2. 观察界面跳转 | HUT发送退出指令<br>域控发送HAVPFunctTextDisp=0x65（文言："用户主动退出"）:crusing user exit | 1. 显示文言"用户主动退出"<br>2. 功能退出<br>3. 退出到HUT主界面 | HAVPFunctTextDisp=0x65（文言："用户主动退出"）<br>退到主界面 | 实车测试 | 用户主动退出 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-124 | 泊车 | HMI | P0 | 车速超过30km/h退出到预激活界面 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 车速加速 | InterfaceDisTyp=0x11或0x3<br>车速超过30km/h | 1. 车速超过30km/h<br>2. 观察弹窗和界面跳转 | 域控发送HAVPFunctTextDisp=0x67（文言："车速过高"）:Crusing Speed too high | 1. 显示文言"巡航中车速过高"<br>2. 显示"请立即接管"大弹窗<br>3. 播放接管音效<br>4. 3s后：无图退到预激活界面，有图退到主界面 | HAVPFunctTextDisp=0x67（文言："车速过高"）<br>⚠️变更1：区分退出界面 | 实车测试 | ⚠️变更1-车速过高 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-125 | 泊车 | HMI | P1 | 已在目标楼层退出到预激活界面 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 车辆已到达目标楼层 | InterfaceDisTyp=0x11:VLAP Active<br>车辆已在目标楼层 | 1. 车辆漫游到目标楼层<br>2. 观察文言和界面跳转 | 域控发送HAVPFunctTextDisp=0xBC（文言："目标楼层在当前楼层"）:Target Floor is on the current Floor | 1. 显示文言"目标楼层在当前楼层"<br>2. 任务完成提示<br>3. 退出到漫游预激活界面（⚠️变更1）<br>4. 或退到主界面（有图） | HAVPFunctTextDisp=0xBC（文言："目标楼层在当前楼层"）<br>⚠️变更1：区分退出界面 | 实车测试 | ⚠️变更1-目标楼层完成 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-126 | 泊车 | HMI | P1 | 已在目标区域退出到预激活界面 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 车辆已到达目标区域 | InterfaceDisTyp=0x11:VLAP Active<br>车辆已在目标区域 | 1. 车辆漫游到目标区域<br>2. 观察文言和界面跳转 | 域控发送HAVPFunctTextDisp=0xC2（文言："目标区域在当前区域"）:Target Area is on the current Area | 1. 显示文言"目标区域在当前区域"<br>2. 任务完成提示<br>3. 退出到漫游预激活界面（⚠️变更1）<br>4. 或退到主界面（有图） | HAVPFunctTextDisp=0xC2（文言："目标区域在当前区域"）<br>⚠️变更1：区分退出界面 | 实车测试 | ⚠️变更1-目标区域完成 | 业务逻辑层 |

### 24. COT推理面板显示（6个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-127 | 泊车 | HMI | P0 | 漫游激活后COT推理面板显示 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. FunctWorkSts≠0xA | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming | 1. 检查COT推理面板显示<br>2. 验证面板内容完整性 | 域控通过VLAADASCtrlSrv服务<br>EnvironmentReport接口传输数据 | 1. COT推理面板显示在界面指定位置<br>2. 面板显示缩略态（场景+横纵控制行为）<br>3. 显示环境热力图标标注<br>4. 显示推理文字内容 | COT面板正常显示 | 实车测试 | COT面板显示 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-128 | 泊车 | HMI | P0 | COT热力图标标注重要指引信息 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. COT面板显示中<br>4. 经过楼层/出入口/上下坡 | InterfaceDisTyp=0x11:VLAP Active Page<br>COT面板显示 | 1. 车辆行驶经过楼层指引标识<br>2. 车辆行驶经过出入口标识<br>3. 车辆行驶经过上下坡标识<br>4. 观察热力图标标注 | 感知通过OCR识别指引信息<br>域控发送热力图标数据 | 1. 热力图框选/扎标楼层信息<br>2. 热力图框选/扎标出入口信息<br>3. 热力图框选/扎标上下坡信息<br>4. 标注位置准确，颜色醒目 | 可视化重要指引信息 | 实车测试 | COT热力图标标注 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-129 | 泊车 | HMI | P0 | COT推理文字格式验证 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. COT面板显示 | InterfaceDisTyp=0x11:VLAP Active Page | 1. 观察推理文字内容<br>2. 验证文字格式规范 | 域控发送VLAtext消息<br>string title=2（场景+动作） | 1. 推理文字格式：当前任务+【逗号】+场景+【句号】+横向决策+【逗号】+纵向决策+【句号】<br>2. 文字内容清晰可读<br>3. 格式符合设计规范 | VLAtext消息格式 | 实车测试 | COT文字格式 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-130 | 泊车 | HMI | P1 | COT推理内容5秒间隔更新 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. COT面板显示 | InterfaceDisTyp=0x11:VLAP Active Page | 1. 观察推理内容更新频率<br>2. 使用计时器记录间隔<br>3. 验证去重逻辑 | VLA以1秒2帧推送<br>DTA按5s/次转发<br>使用时间戳保证间隔 | 1. 推理内容约每5秒更新一次<br>2. 时间戳保证5秒间隔<br>3. 高优推理直接推送（用户语音指令）<br>4. 文本重复不更新 | 更新频率符合规范 | 实车测试 | COT更新频率 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-131 | 泊车 | HMI | P1 | COT去重逻辑验证 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. COT面板显示 | InterfaceDisTyp=0x11:VLAP Active Page | 1. 观察相同场景下推理是否重复推送<br>2. 验证超过30s未更新的处理 | 推理去重逻辑<br>场景和控制行为比对 | 1. 功能刚激活时首帧必推（不比对上一帧）<br>2. 场景或控制行为变化才推送<br>3. 超过30s未更新则更新一条新推理<br>4. 去重逻辑正确执行 | 去重逻辑验证通过 | 实车测试 | COT去重逻辑 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-132 | 泊车 | HMI | P0 | 漫游APA状态COT面板不显示 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 切换到APA泊车状态 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0xA:VLAP Parking | 1. 沿途泊车发现车位切换到APA<br>2. 检查COT面板显示状态 | FunctWorkSts切换到0xA:VLAP Parking | 1. COT推理面板不再显示<br>2. 界面显示APA泊车引导信息<br>3. APA状态下专注泊车引导（⚠️变更：0xA状态不显示COT） | FunctWorkSts=0xA时COT不显示 | 实车测试 | COT面板-APA不显示 | 业务逻辑层 |

### 25. 语音控车指令（8个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-133 | 泊车 | HMI | P0 | 语音开启漫游泊车指令 | 1. 车辆处于ready状态<br>2. 满足功能开启条件 | 符合ODD条件 | 1. 语音指令"开启漫游泊车"或"漫游泊车开启"等<br>2. 观察系统响应和语音反馈 | VLA链路识别【驾驶设置】【漫游泊车open】 | 1. 系统开始开启漫游功能<br>2. 语音播报成功："好的，我将开始漫游泊车"<br>3. 或失败："漫游泊车开启失败+{原因}"<br>4. 或抑制："请先{松开刹车}" | 语音反馈正确 | 实车测试 | 语音开启漫游 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-134 | 泊车 | HMI | P0 | 语音去X楼层指令 | 1. 车辆处于ready状态<br>2. 漫游相关界面显示 | InterfaceDisTyp=0x10或0x11 | 1. 语音指令"去B1层"或"到B1层去"或"开到B1层去"<br>2. 观察系统响应和语音反馈 | VLA链路识别【寻找目的地】【楼层】 | 1. 系统识别楼层目标<br>2. 语音播报成功："好的，正在寻找B1层"<br>3. 车辆开始导航至B1层<br>4. 或失败反馈<br>5. 或抑制反馈 | 语音反馈正确 | 实车测试 | 语音去楼层 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-135 | 泊车 | HMI | P0 | 语音泊入默认车位指令 | 1. 车辆处于ready状态<br>2. 2D库位管理界面或漫游界面<br>3. 存在默认车位 | InterfaceDisTyp=0x1或0x11<br>存在默认车位 | 1. 语音指令"泊入默认车位"<br>2. 观察系统响应 | VLA链路识别【泊入车位】【默认】 | 1. 系统识别默认车位目标<br>2. 激活巡航功能<br>3. 车辆开始向默认车位行驶 | 命中默认车位激活巡航 | 实车测试 | 语音泊入默认车位 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-136 | 泊车 | HMI | P0 | 语音泊入充电桩车位指令 | 1. 车辆处于ready状态<br>2. 2D库位管理界面或漫游界面<br>3. 存在充电桩车位 | InterfaceDisTyp=0x1或0x11<br>存在充电桩车位 | 1. 语音指令"泊入充电桩车位"<br>2. 观察系统响应 | VLA链路识别【泊入车位】【充电桩车位】 | 1. 系统识别充电桩车位目标<br>2. 激活巡航功能（多个充电桩按最近规划）<br>3. 车辆开始向充电桩车位行驶 | 命中充电桩车位激活巡航 | 实车测试 | 语音泊入充电桩 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-137 | 泊车 | HMI | P0 | 语音巡航停车指令 | 1. 车辆处于ready状态<br>2. 漫游已激活<br>3. 车辆控车中 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0x9 | 1. 语音指令"巡航停车"<br>2. 观察系统响应 | VLA链路识别【停车操作】【刹停】 | 1. 车辆减速刹停保压<br>2. 进入暂停状态<br>3. 显示【继续】按键 | FunctWorkSts=0xB:VLAP Pause | 实车测试 | 语音刹停 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-138 | 泊车 | HMI | P0 | 语音沿途/就近泊车指令 | 1. 车辆处于ready状态<br>2. 漫游已激活 | InterfaceDisTyp=0x11:VLAP Active<br>AlongToutPrkgBtnSts=0x1 | 1. 语音指令"沿途泊车"或"就近泊车"<br>2. 观察系统响应 | VLA链路识别【泊入车位】【附近车位】 | 1. 系统开始沿途寻找车位<br>2. 界面显示"正在寻找车位"文言<br>3. 【沿途泊车】按键不显示 | HAVPFunctTextDisp=0xBD（文言："正在寻找沿途车位"） | 实车测试 | 语音沿途泊车 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-139 | 泊车 | HMI | P1 | 语音不支持指令反馈 | 1. 车辆处于ready状态<br>2. 漫游相关界面显示 | InterfaceDisTyp=0x10或0x11 | 1. 语音指令不支持的功能<br>2. 观察语音反馈 | VLA链路识别指令不支持 | 1. 语音播报"暂不支持该功能，正在学习中"<br>2. 系统不执行任何操作<br>3. 维持当前状态 | 不支持指令反馈 | 实车测试 | 不支持指令反馈 | 业务逻辑层 |


### 26. 扩建地图（5个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-140 | 泊车 | HMI | P0 | 有图人驾驶离地图范围跳转漫游人驾 | 1. 车辆处于ready状态<br>2. 显示记忆泊车导航或2D地图界面<br>3. 车辆行驶 | 当前在有图停车场内 | 1. 车辆驶出原地图范围外<br>2. 观察界面自动跳转 | 域控检测驶出地图范围<br>发送InterfaceDisTyp=0x10:VLAP Preactive | 1. 界面自动跳转到漫游泊车人驾界面<br>2. 开始扩建地图（静默建图）<br>3. 界面显示实时感知元素<br>4. 无弹窗提示 | InterfaceDisTyp=0x10:VLAP Preactive | 实车测试 | 扩建地图-人驾跳转 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-141 | 泊车 | HMI | P0 | 扩建地图返回原地图范围跳转2D管理 | 1. 车辆处于ready状态<br>2. 显示漫游泊车人驾界面<br>3. 正在扩建地图 | InterfaceDisTyp=0x10:VLAP Preactive<br>车辆在原地图范围外 | 1. 车辆返回原地图范围内<br>2. 观察界面自动跳转 | 域控检测返回地图范围<br>发送InterfaceDisTyp=0x1:Pre_Mapbuilt | 1. 界面跳转回2D地图管理页面<br>2. 显示原有地图和新扩建区域<br>3. 地图融合显示正确<br>4. 无弹窗提示 | InterfaceDisTyp=0x1:Pre_Mapbuilt | 实车测试 | 扩建地图-返回跳转 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-142 | 泊车 | HMI | P0 | 有图漫游驶离地图范围维持控车界面 | 1. 车辆处于ready状态<br>2. 有图漫游已激活<br>3. 车辆漫游控车中 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming<br>FunctWorkSts≠0xA | 1. 车辆驶出原地图范围外<br>2. 观察界面状态 | 域控检测驶出地图范围 | 1. 维持漫游控车界面不变<br>2. 继续显示实时感知和规划<br>3. 后台进行扩建地图<br>4. 无弹窗提示 | InterfaceDisTyp=0x11维持 | 实车测试 | 扩建地图-漫游维持 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-143 | 泊车 | HMI | P0 | 园区内挂P档自动保存扩建地图 | 1. 车辆处于ready状态<br>2. 正在扩建地图<br>3. 车辆在原地图范围外或2D管理页 | 扩建地图过程中 | 1. 车辆停止挂P档<br>2. 观察系统行为（无交互提示） | 域控检测挂P档<br>自动更新保存地图 | 1. 地图自动保存（无弹窗）<br>2. 无交互提示用户<br>3. 维持当前界面显示<br>4. 地图数据已更新融合 | 自动保存成功 | 实车测试 | 扩建地图-挂P自动保存 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-144 | 泊车 | HMI | P1 | 驶出园区自动保存退出主界面 | 1. 车辆处于ready状态<br>2. 正在扩建地图 | 扩建地图过程中 | 1. 车辆继续行驶驶出园区<br>2. 观察系统行为和界面跳转 | 域控检测驶出园区<br>自动更新保存地图 | 1. 地图自动保存（无弹窗）<br>2. 退回HUT主界面<br>3. 无交互提示用户<br>4. 更新后地图已保存 | 自动保存并退出主界面 | 实车测试 | 扩建地图-驶出自动保存 | 业务逻辑层 |

### 27. 导航巡航-POI显示（3个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-145 | 泊车 | HMI | P0 | 巡航界面显示停车场出入口POI | 1. 车辆处于ready状态<br>2. 巡航已激活<br>3. 地图包含出入口POI | InterfaceDisTyp=0x3:Cruise | 1. 检查巡航界面POI信息显示<br>2. 验证出入口图标 | 域控发送停车场出口、入口POI信息 | 1. 界面显示停车场出口图标<br>2. 界面显示停车场入口图标<br>3. 图标位置准确<br>4. 图标样式清晰 | 出入口POI渲染 | 实车测试 | 巡航出入口POI | 业务逻辑层 |
| BFO-HMI-Thor-VLA-146 | 泊车 | HMI | P0 | 巡航界面显示充电桩车位POI | 1. 车辆处于ready状态<br>2. 巡航已激活<br>3. 地图包含充电桩车位 | InterfaceDisTyp=0x3:Cruise | 1. 检查巡航界面充电桩车位显示<br>2. 验证充电桩图标 | 域控发送充电桩车位POI信息 | 1. 界面显示充电桩车位图标<br>2. 充电桩车位有专属标识<br>3. 图标位置准确<br>4. 可区分普通车位和充电桩车位 | 充电桩车位POI渲染 | 实车测试 | 巡航充电桩POI | 业务逻辑层 |
| BFO-HMI-Thor-VLA-147 | 泊车 | HMI | P0 | 巡航界面速度设置显示 | 1. 车辆处于ready状态<br>2. 巡航已激活 | InterfaceDisTyp=0x3:Cruise<br>VLAPSpdSetVal=0x14 | 1. 检查速度显示<br>2. 验证速度设置反馈 | 域控发送VLAPSpdSetVal | 1. 界面显示最大车速<br>2. 显示实际车速<br>3. 漫游泊车速度设置反馈显示<br>4. 速度范围10~20km/h | VLAPSpdSetVal显示正确 | 实车测试 | 巡航速度显示 | 业务逻辑层 |

### 28. 巡航完成（2个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-148 | 泊车 | HMI | P0 | 巡航完成显示统计信息页面 | 1. 车辆处于ready状态<br>2. 记忆巡航泊入完成或巡航到POI点 | 巡航任务完成 | 1. 巡航任务完成<br>2. 观察界面跳转和内容显示 | 域控发送InterfaceDisTyp=0x5:HAVP_completed | 1. 界面跳转到完成页<br>2. 显示统计信息界面<br>3. 显示文字提示<br>4. 显示【退出】按键<br>5. 统计信息准确（行驶距离、时间等） | InterfaceDisTyp=0x5:HAVP_completed | 实车测试 | 巡航完成页 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-149 | 泊车 | HMI | P0 | 巡航完成点击退出或20秒自动退出 | 1. 车辆处于ready状态<br>2. 显示巡航完成页面 | InterfaceDisTyp=0x5:HAVP_completed | 1. 场景A：点击【退出】按键<br>2. 场景B：20秒不操作<br>3. 观察界面跳转 | 场景A：HUT发送BtnEnaReq=0x8:HAVP_Completed<br>域控发送HAP_Hmi_Index=0x1:Main Screen<br>场景B：20秒超时域控主动退出 | 场景A：点击【退出】后立即退回HUT主界面<br>场景B：20秒无操作后自动退至HUT主界面<br>退出流畅无卡顿 | 退回HUT主界面 | 实车测试 | 巡航完成退出 | 业务逻辑层 |

### 29. 有图漫游完成（2个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-150 | 泊车 | HMI | P0 | 有图漫游到达终点完成 | 1. 车辆处于ready状态<br>2. 有图漫游已激活<br>3. 车辆到达漫游终点 | InterfaceDisTyp=0x11:VLAP Active Page<br>车辆到达终点 | 1. 车辆完成有图漫游任务<br>2. 观察文言提示和界面跳转 | 域控发送HAVPFunctTextDisp=0xB8（文言："漫游已完成"）:Roaming Completed | 1. 中控屏显示文言"漫游已完成"<br>2. 3s后界面自动退出到HUT主界面<br>3. 静默完成无需用户交互<br>4. 退出流畅 | HAVPFunctTextDisp=0xB8（文言："漫游已完成"）<br>3s后退到主界面 | 实车测试 | 有图漫游完成 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-151 | 泊车 | HMI | P1 | 有图漫游完成与记忆泊车学习完成区别 | 1. 车辆处于ready状态<br>2. 有图漫游完成 | HAVPFunctTextDisp=0xB8（文言："漫游已完成"）:Roaming Completed | 1. 对比漫游学习完成和记忆泊车学习完成<br>2. 验证跳转界面不同 | 漫游学习完成逻辑 | 1. 漫游学习完成跳转为2D地图管理界面（非总结页面）<br>2. 与记忆泊车学习完成逻辑不同<br>3. 无统计总结页面显示 | 不同于记忆泊车学习完成 | 实车测试 | 漫游完成逻辑差异 | 业务逻辑层 |

---

## 测试覆盖总结（完整版）

### 按功能模块分类（共29个模块，151个用例）

1. ✅ 平台配置识别 - 2个用例
2. ✅ 无图漫游功能开启-引导界面 - 3个用例
3. ✅ 无图漫游功能开启-人驾界面 - 5个用例
4. ✅ 无图漫游功能开启-控车界面 - 4个用例
5. ✅ 无目的漫游-APA选车位 - 5个用例
6. ✅ 有目的漫游 - 3个用例
7. ✅ 有图泊车功能开启-库位管理 - 4个用例
8. ✅ 有图巡航功能开启 - 6个用例
9. ✅ 漫游抑制-不使能条件 - 9个用例
10. ✅ 功能开启异常-基础异常 - 7个用例
11. ✅ 功能开启异常-主动安全功能 - 5个用例
12. ✅ 功能开启异常-特殊条件 - 6个用例
13. ✅ 其他功能开启异常 - 4个用例
14. ✅ 主动推送功能-预留 - 2个用例
15. ✅ 静默建图-无图静默建图 - 4个用例
16. ✅ 静默建图-无图漫游控车 - 5个用例
17. ✅ 静默建图完成与保存-⚠️变更2 - 6个用例
18. ✅ 沿途泊车功能 - 6个用例
19. ✅ 漫游暂停与继续 - 5个用例
20. ✅ 漫游异常退出-四门两盖-⚠️变更1 - 10个用例
21. ✅ 漫游异常退出-系统和环境异常-⚠️变更1 - 12个用例
22. ✅ 漫游异常退出-主动安全功能 - 5个用例
23. ✅ 漫游异常退出-用户干预-⚠️变更1 - 9个用例
24. ✅ COT推理面板显示 - 6个用例
25. ✅ 语音控车指令 - 8个用例
26. ✅ 扩建地图 - 5个用例
27. ✅ 导航巡航-POI显示 - 3个用例
28. ✅ 巡航完成 - 2个用例
29. ✅ 有图漫游完成 - 2个用例

### 按优先级分类

- **P0级别**：121个用例（核心功能、用户直接交互、三大变更验证、必须验证）
- **P1级别**：30个用例（边界场景、异常分支、优化体验、补充验证、预留功能）

**总计：151个测试用例**

### 按测试类型分类

- **功能开启测试**：41个用例
- **异常处理测试**：58个用例（含变更1重点）
- **核心交互测试**：32个用例
- **辅助功能测试**：20个用例（COT、语音、POI等）

### 三大变更覆盖验证

#### ⚠️ 变更1：漫游异常退出逻辑
- 覆盖用例数：**36个用例**
- 覆盖场景：
  - 四门两盖异常：10个用例（无图退预激活，有图退主界面）
  - 系统环境异常：12个用例（主要退主界面）
  - 主动安全功能：5个用例（退主界面）
  - 用户干预场景：9个用例（区分无图和有图）

#### ⚠️ 变更2：静默建图保存弹窗15s
- 覆盖用例数：**6个用例**
- 覆盖场景：
  - 手动泊入后弹窗：1个用例
  - 自动泊入后弹窗：1个用例
  - 点击保存：1个用例
  - 点击取消：1个用例
  - 15s超时：1个用例
  - 保存成功后验证：1个用例

#### ⚠️ 变更3：漫游文言HAVPFunctTextDisp=0xC4（文言："车辆漫游中，请注意周围环境"）
- 覆盖用例数：**2个用例**
- 覆盖场景：
  - 漫游控车常驻文言显示：1个用例
  - 信号值和文言内容验证：1个用例

---

## 核心信号定义参考（完整版）

### 界面信号 InterfaceDisTyp

| 信号值 | 含义 | 说明 |
|-------|------|------|
| 0x0:None | 无界面 | 默认状态 |
| 0xF:VLAP without ODD | 无图引导界面 | ODD范围外显示 |
| 0x10:VLAP Preactive | 漫游泊车人驾界面 | 无图静默建图、扩建地图 |
| 0x11:VLAP Active Page | 漫游控车界面 | 无图/有图漫游控车 |
| 0x1:Pre_Mapbuilt | 2D库位管理界面 | 有图场景管理页 |
| 0x3:Cruise | 记忆巡航激活界面 | 有图巡航控车 |
| 0x5:HAVP_completed | 巡航完成页 | 显示统计信息 |

### 状态灯信号 PrkgFuncStsLmp（CAN信号，仅中控显示）

| 信号值 | 含义 | 状态灯样式 | 说明 |
|-------|------|----------|------|
| 0x2:VLAP_Roaming_Standby | 无图漫游待激活 | 置灰 | 人驾界面 |
| 0x4:VLAP_Roaming_Active | 无图漫游已激活 | 高亮 | 漫游控车 |
| 0x6:VLAP_Crusing_Override | 漫游油门override | 高亮闪烁 | 用户踩油门 |
| 0x7:HAVP_Standby | 有图巡航待激活 | 置灰 | 2D管理界面 |
| 0x8:HAVP_Active | 有图巡航已激活 | 高亮 | 巡航控车 |
| 0x9:HAVP_Override | 有图巡航踩油门 | 高亮闪烁 | 用户踩油门 |
| 0x3:VLAP_Crusing_Standby | 有图巡航待激活 | 置灰 | 2D管理界面（扩展） |

### 功能状态 FunctWorkSts

| 信号值 | 含义 | 说明 |
|-------|------|------|
| 0x0:Standby | 待机状态 | 功能未激活 |
| 0x9:VLAP Roaming | 漫游状态 | 车辆漫游中 |
| 0xA:VLAP Parking | 漫游APA状态 | APA泊车中（COT不显示） |
| 0xB:VLAP Pause | 漫游暂停状态 | 暂停保压 |

### 沿途泊车按键 AlongToutPrkgBtnSts

| 信号值 | 含义 | 说明 |
|-------|------|------|
| 0x0:No_Display | 不显示 | 未激活/已找车位/暂停状态 |
| 0x1:Available | 可用 | 显示可点击态 |
| 0x2:Unavailable | 不可用 | 显示不可点击态（预留） |
| 0x3:Highlight | 高亮 | 预留状态 |

### 按键请求 BtnEnaReq

| 信号值 | 含义 | 说明 |
|-------|------|------|
| 0x2:Active_signal | 激活记忆泊车 | 点击【记忆泊车】 |
| 0x3 | 保存地图 | 点击【保存】 |
| 0x5:Cancel | 取消保存 | 点击【取消】 |
| 0x6:Confrim_start_parking | 确认开始泊车 | 开始APA |
| 0x8:HAVP_Completed | 巡航完成 | 点击【退出】 |
| 0xF:Continue_VLAP | 继续漫游 | 点击【继续】 |
| 0x10:VLAP parking Nearby | 沿途泊车 | 点击【沿途泊车】 |

### 功能按键 FunctBtnDisp

| 信号值 | 含义 | 说明 |
|-------|------|------|
| 0x0:None | 无按键 | 不显示 |
| 0x2:Continue_HAVP | 继续按键 | 暂停状态显示 |
| 0x5:Start_APA | 开始泊车按键 | 选定车位后显示 |

### 速度设置 VLAPSpdSetVal
- **支持范围**：10~20km/h
- **示例值**：0x14:Twenty（20km/h）
- **说明**：漫游泊车速度设置反馈信号

### ⚠️ 三大变更关键信号

#### 变更1：异常退出HAVPFunctTextDisp（26个信号）
- 0x3F~0x43: 四门两盖异常（机舱盖、后背门、车门、后视镜、安全带）
- 0x46: 绕行障碍物空间不足
- 0x48~0x4C: 系统异常（定位、光照、雨量、系统、关联系统）
- 0x4D~0x50: 超时异常（漫游10min、APA4min、暂停次数、续航）
- 0x51~0x55: 主动安全（RCTB/FCTB、AEB、ESP、TCS/ABS、HDC）
- 0x57~0x5A: 其他异常（车位被占、APA失败、激活失败）
- 0x5B~0x5D: 传感器异常（摄像头遮挡、摄像头故障、雷达故障）
- 0x61~0x67: 用户干预（EPB、档位、方向盘、刹车、主动退出、车速过高）
- 0xB7、0xBB、0xBC、0xC2: 特殊退出（暂停超时、漫游超时、目标楼层/区域）

#### 变更2：保存弹窗PopupDisp
- 0x3F:HAVP_Push_Request - 静默建图保存弹窗（持续**15s**）

#### 变更3：漫游常驻文言HAVPFunctTextDisp
- 0xC4:HAVP Roaming - "车辆漫游中，请注意周围环境"（非0x2E）

### 其他重要文言信号 HAVPFunctTextDisp

| 信号值 | 含义 | 说明 |
|-------|------|------|
| 0xB8:Roaming Completed | 漫游已完成 | 有图漫游完成 |
| 0xB9 | 漫游调头 | 车辆需调头 |
| 0xBA:Parking in complete | 泊车已完成 | 静默建图完成 |
| 0xBB:Roaming overtime | 漫游超时 | 漫游超过10分钟 |
| 0xBC:Target Floor | 目标楼层 | 已在目标楼层 |
| 0xBD:Searching parkspace | 正在寻找车位 | 沿途泊车常驻文言 |
| 0xBE | 目标楼层无空车位 | 有图场景 |
| 0xC0 | 到达目标楼层找车位 | 开始找车位 |
| 0xC2:Target Area | 目标区域 | 已在目标区域 |
| 0xC4:HAVP Roaming | 车辆漫游中 | ⚠️变更3 |

### Toast弹窗信号 PopupDisp（18个异常+3个功能）

**功能异常类（返回Toast+TTS）**：
- 0x3: Turn on background functions - 开关关闭
- 0x5: HAVP rampway - 坡道过大
- 0x6: HAVP Environment empty - ODD范围外
- 0x8~0xA: 传感器异常（摄像头遮挡/故障、雷达故障）
- 0xB~0xC: 系统异常（关联系统、系统故障）
- 0xD~0x10: 四门两盖（车门、后背门、安全带、机舱盖）
- 0x11~0x18: 主动安全+环境（RCTB/FCTB、AEB、TCS/ABS、ESP、HDC、胎压、光照、雨量）
- 0x1B: Please switch to D gear - 挂D档
- 0x3B: Driving Mode not supported - 驾驶模式
- 0x3D: Rearview mirror folded - 后视镜
- 0x42: Other auxiliary functions - 其他辅助
- 0x49: Not Available in Valet Mode - 代客模式
- 0x4C~0x4D: 特殊异常（挂车、差速锁）

**功能推送类**：
- 0x3F: HAVP_Push_Request - 静默建图保存（⚠️15s）
- 0x4E: VLAP Roaming Push_Request - 漫游主动推送（预留）
- 0x4F: VLAP Crusing Push_Request - 巡航主动推送（预留）

**接管弹窗**：
- 0x20: take over immediately - 请立即接管（所有异常退出场景）

---

## 测试执行指南

### 测试环境配置

**硬件要求**：
- 车型：Thor
- 座舱版本：CUX3.5
- 平台配置：ADC40
- 传感器：环视摄像头、雷达正常工作

**测试场景需求**：
1. **无图停车场/园区**（用于静默建图和无图漫游测试）
   - 多楼层停车场（B1、B2、B3等）
   - 包含出入口标识
   - 包含充电桩车位
   - 包含道路箭头地面标识
   - 包含减速带、立柱等感知对象

2. **有图停车场/园区**（用于巡航和有图漫游测试）
   - 已学习完整地图
   - 包含默认车位、出入口POI、充电桩车位
   - 地图数据完整准确

3. **混合测试场景**（用于扩建地图测试）
   - 部分区域有图，部分区域无图
   - 用于测试驶离地图范围的扩建逻辑

### 测试工具与监控

**信号监控工具**：
- CAN信号监控（状态灯PrkgFuncStsLmp）
- 以太网信号监控（SOME/IP服务）
- VLA链路TTS监听
- Proto消息抓包（VLAtext）

**测试辅助工具**：
- 计时器（验证弹窗15s、暂停3分钟、漫游10分钟等）
- 视频录制设备（记录界面变化和跳转）
- 语音识别测试工具
- 日志采集工具

### 测试执行优先级

**P0用例（121个）- 第一轮必测**：
1. 三大变更验证用例（44个）
2. 核心功能开启流程（20个）
3. 关键异常处理（30个）
4. 核心交互功能（27个）

**P1用例（30个）- 第二轮补充**：
1. 边界场景验证
2. 预留功能验证
3. 优化体验验证

### 关键验证点清单

#### ⚠️ 变更1验证清单（必须全部通过）
- [ ] 无图漫游+机舱盖打开 → 退到漫游预激活界面（0x10）
- [ ] 有图巡航+机舱盖打开 → 退到HUT主界面
- [ ] 无图漫游+后背门打开 → 退到漫游预激活界面
- [ ] 有图巡航+后背门打开 → 退到HUT主界面
- [ ] 无图漫游+车门打开 → 退到漫游预激活界面
- [ ] 有图巡航+车门打开 → 退到HUT主界面
- [ ] 无图漫游+后视镜折叠 → 退到漫游预激活界面
- [ ] 有图巡航+后视镜折叠 → 退到HUT主界面
- [ ] 无图漫游+安全带解开 → 退到漫游预激活界面
- [ ] 有图巡航+安全带解开 → 退到HUT主界面
- [ ] 所有其他异常退出场景验证退出界面正确性

#### ⚠️ 变更2验证清单（必须全部通过）
- [ ] 手动泊入后弹窗显示时间为15s（使用计时器验证）
- [ ] 自动泊入后弹窗显示时间为15s（使用计时器验证）
- [ ] 15s内点击【保存】按键可正常保存
- [ ] 15s内点击【取消】按键可放弃保存
- [ ] 15s超时后自动放弃保存
- [ ] 弹窗信号为PopupDisp=0x3F（持续15s）

#### ⚠️ 变更3验证清单（必须全部通过）
- [ ] 漫游控车界面常驻文言信号值为0xC4（非0x2E）
- [ ] 文言内容为"车辆漫游中，请注意周围环境"
- [ ] 文言常驻显示在固定位置
- [ ] 文言可被其他高优文言临时打断

#### 其他关键验证点
- [ ] 状态灯仅在中控显示，不在仪表显示（CAN信号）
- [ ] 当前车速HUT侧性能暂不满足，实际显示档位信息
- [ ] 小地图不可展开，点击提示"请保存地图后再尝试"
- [ ] COT面板在FunctWorkSts=0xA:VLAP Parking状态下不显示
- [ ] 充电桩车位属性在2D地图和巡航过程中正确显示
- [ ] 扩建地图挂P档和驶出园区自动保存，无交互提示
- [ ] 道路箭头为地面方向标识（非车道箭头）
- [ ] 所有异常退出显示"请立即接管"弹窗+播放CruiseTakeOverLV31声音效
- [ ] 所有异常退出3s后跳转到目标界面

---

## Excel导出说明

### 使用export_to_excel.py导出

```bash
cd /home/wangqian/Documents/hmi-testcase-auto-generation

python3 .claude/skills/generate-test-cases/scripts/export_to_excel.py \
  --input "新增用例/VLA泊车HMI交互测试用例_完整版.md" \
  --output "新增用例/VLA泊车HMI交互测试用例.xlsx" \
  --sheet "VLA泊车测试用例"
```

### Excel文件结构
- **工作表名称**：VLA泊车测试用例
- **列数**：14列（符合公司标准）
- **行数**：152行（含表头）
- **格式**：自动应用格式化（加粗表头、边框、列宽、冻结首行）

---

**文档版本**：v1.0（完整版-基于PyMuPDF）  
**生成日期**：2026-01-26  
**适用车型**：Thor  
**座舱版本**：CUX3.5  
**平台配置**：ADC40  
**测试用例总数**：151个（P0: 121个，P1: 30个）  
**需求文档来源**：5个文档（3个PDF + 2个Excel）  
**提取工具**：PyMuPDF + openpyxl  

---

✅ **测试用例生成完成！**

📊 **用例统计**：
- 总用例数：151个
- P0级别：121个
- P1级别：30个
- 覆盖模块：29个

🎯 **三大变更全覆盖**：
- 变更1（异常退出）：36个用例
- 变更2（弹窗15s）：6个用例
- 变更3（文言0xC4）：2个用例

📄 **文档质量**：
- ✅ 预期结果只包含可观测现象
- ✅ 信号描述单独列出
- ✅ 覆盖正常、边界、异常场景
- ✅ 符合公司14列标准格式

**记住：好的测试用例是可执行的、可观测的、可重复的！**
# VLA泊车补充测试用例

## 补充说明
本文档包含基于VLA指令Sheet2和车外智驾灯需求补充的测试用例，以及对现有用例的文言优化。

---

## 一、语音控车指令补充用例

### 1. 转向控制指令（4个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-152 | 泊车 | HMI | P0 | 语音掉头/换方向指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 车辆控车中 | InterfaceDisTyp=0x11:VLAP Active或0x3:Cruise<br>FunctWorkSts=0x9:VLAP Roaming | 1. 语音指令"掉头"或"换方向"<br>2. 观察系统响应和语音反馈 | VLA链路识别【转向控车】意图<br>vla_req.intent=VLA_steering_setting<br>vla_req.slots.steering_type=SteeringType_u_turn | 1. 车辆开始执行掉头动作<br>2. 语音播报"正在调整行驶方向"<br>3. 界面显示车辆转向轨迹<br>4. COT推理面板更新掉头任务 | 域控执行掉头控制 | 实车测试 | 转向控制 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-153 | 泊车 | HMI | P0 | 语音前方路口左转指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 接近路口 | InterfaceDisTyp=0x11或0x3<br>FunctWorkSts=0x9 | 1. 语音指令"前方路口左转"或"左拐"或"向左转"<br>2. 观察系统响应和语音反馈 | VLA链路识别【转向控车】【左】【路口】<br>vla_req.intent=VLA_steering_setting<br>vla_req.slots.steering_type=SteeringType_left | 1. 系统识别左转指令<br>2. 语音播报"前方路口左转"<br>3. 车辆在路口执行左转动作<br>4. 转向提示显示在界面<br>5. COT推理面板显示左转任务 | 域控执行左转控制 | 实车测试 | 转向控制-左转 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-154 | 泊车 | HMI | P0 | 语音前方路口右转指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 接近路口 | InterfaceDisTyp=0x11或0x3<br>FunctWorkSts=0x9 | 1. 语音指令"前方路口右转"或"右拐"或"向右开"<br>2. 观察系统响应和语音反馈 | VLA链路识别【转向控车】【右】【路口】<br>vla_req.intent=VLA_steering_setting<br>vla_req.slots.steering_type=SteeringType_right | 1. 系统识别右转指令<br>2. 语音播报"前方路口右转"<br>3. 车辆在路口执行右转动作<br>4. 转向提示显示在界面<br>5. COT推理面板显示右转任务 | 域控执行右转控制 | 实车测试 | 转向控制-右转 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-155 | 泊车 | HMI | P0 | 语音前方路口直行指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 接近路口 | InterfaceDisTyp=0x11或0x3<br>FunctWorkSts=0x9 | 1. 语音指令"前方路口直行"或"往前走"或"向前开"<br>2. 观察系统响应和语音反馈 | VLA链路识别【转向控车】【直行】【路口】<br>vla_req.intent=VLA_steering_setting<br>vla_req.slots.steering_type=SteeringType_straight | 1. 系统识别直行指令<br>2. 语音播报"前方路口直行"<br>3. 车辆在路口保持直行<br>4. 直行提示显示在界面<br>5. COT推理面板显示直行任务 | 域控执行直行控制 | 实车测试 | 转向控制-直行 | 业务逻辑层 |

### 2. 速度调节指令（2个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-156 | 泊车 | HMI | P0 | 语音快一点/加速指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 车辆控车中 | InterfaceDisTyp=0x11或0x3<br>FunctWorkSts=0x9<br>当前速度<20km/h | 1. 语音指令"快一点"或"加速"或"车速太慢了"<br>2. 观察系统响应和速度变化 | VLA链路识别【速度调节】【加速】<br>vla_req.intent=VLA_speed_setting<br>vla_req.slots.acceleration_type=AccelerationType_up | 1. 系统识别加速指令<br>2. 语音播报"目标车速已加快"<br>3. 界面显示目标车速增加<br>4. 实际车速逐渐提升（在10~20km/h范围内）<br>5. VLAPSpdSetVal信号值增加 | VLAPSpdSetVal增加（最大0x14:20km/h） | 实车测试 | 速度调节-加速 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-157 | 泊车 | HMI | P0 | 语音慢一点/减速指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 车辆控车中 | InterfaceDisTyp=0x11或0x3<br>FunctWorkSts=0x9<br>当前速度>10km/h | 1. 语音指令"慢一点"或"减速"或"车速太快了"<br>2. 观察系统响应和速度变化 | VLA链路识别【速度调节】【减速】<br>vla_req.intent=VLA_speed_setting<br>vla_req.slots.acceleration_type=AccelerationType_down | 1. 系统识别减速指令<br>2. 语音播报"目标车速已减慢"<br>3. 界面显示目标车速降低<br>4. 实际车速逐渐降低（在10~20km/h范围内）<br>5. VLAPSpdSetVal信号值减小 | VLAPSpdSetVal减小（最小0xA:10km/h） | 实车测试 | 速度调节-减速 | 业务逻辑层 |

### 3. 其他行为控制指令（2个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-158 | 泊车 | HMI | P0 | 语音路边停靠指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 车辆控车中 | InterfaceDisTyp=0x11或0x3<br>FunctWorkSts=0x9 | 1. 语音指令"前面路边停车"或"靠边停车"或"附近停车"<br>2. 观察系统响应 | VLA链路识别【停车操作】【靠边】<br>vla_req.intent=VLA_stop_driving<br>vla_req.slots.stop_driving_type=StopDrivingType_PullOver | 1. 系统识别路边停靠指令<br>2. 语音播报"好的，停车"<br>3. 车辆开始寻找路边合适位置<br>4. 车辆靠边停靠<br>5. 停稳后保持 | 域控执行路边停靠 | 实车测试 | 路边停靠 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-159 | 泊车 | HMI | P1 | 语音倒车指令 | 1. 车辆处于ready状态<br>2. 漫游或巡航已激活<br>3. 需要倒车场景 | InterfaceDisTyp=0x11或0x3<br>FunctWorkSts=0x9 | 1. 语音指令"倒车"<br>2. 观察系统响应 | VLA链路识别【驾驶设置】【倒车】<br>vla_req.intent=VLA_driving_setting<br>vla_req.slots.backward_driving_distance=0 | 1. 系统识别倒车指令<br>2. 车辆执行倒车动作<br>3. 倒车过程中监控后方障碍物<br>4. 界面显示倒车引导信息 | 域控执行倒车控制 | 实车测试 | 倒车控制 | 业务逻辑层 |

---

## 二、区域相关功能补充用例

### 4. 区域车位指令（3个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-160 | 泊车 | HMI | P0 | 语音泊入A区车位指令 | 1. 车辆处于ready状态<br>2. 显示2D地图或漫游界面<br>3. 停车场有A区标识 | InterfaceDisTyp=0x1或0x11<br>停车场包含A区 | 1. 语音指令"帮我泊入A区车位"或"停到A区"<br>2. 观察系统响应和语音反馈 | VLA链路识别【泊入车位】【区域车位】<br>vla_req.intent=VLA_INTENT_PARK_IN<br>vla_req.slots.parking_area="A区" | 1. 系统识别A区车位目标<br>2. 语音播报"好的，正在寻找A区车位并泊入"<br>3. 激活漫游或巡航功能<br>4. 车辆开始前往A区车位<br>5. 界面显示A区位置和规划路径 | 域控发送parking_area="A区" | 实车测试 | 区域车位-A区 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-161 | 泊车 | HMI | P1 | 语音泊入B区车位指令 | 1. 车辆处于ready状态<br>2. 显示2D地图或漫游界面<br>3. 停车场有B区标识 | InterfaceDisTyp=0x1或0x11<br>停车场包含B区 | 1. 语音指令"帮我泊入B区车位"<br>2. 观察系统响应和语音反馈 | VLA链路识别【泊入车位】【区域车位】<br>vla_req.intent=VLA_INTENT_PARK_IN<br>vla_req.slots.parking_area="B区" | 1. 系统识别B区车位目标<br>2. 语音播报"好的，正在寻找B区车位并泊入"<br>3. 激活漫游或巡航功能<br>4. 车辆开始前往B区车位<br>5. 界面显示B区位置和规划路径 | 域控发送parking_area="B区" | 实车测试 | 区域车位-B区 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-162 | 泊车 | HMI | P1 | 语音泊入J区车位边界测试 | 1. 车辆处于ready状态<br>2. 显示2D地图或漫游界面<br>3. 停车场有J区标识 | InterfaceDisTyp=0x1或0x11<br>停车场包含J区 | 1. 语音指令"帮我寻找J区"<br>2. 观察系统响应和语音反馈 | VLA链路识别【泊入车位】【区域车位】<br>vla_req.intent=VLA_INTENT_PARK_IN<br>vla_req.slots.parking_area="J区" | 1. 系统识别J区车位目标（边界值测试）<br>2. 语音播报"好的，正在寻找J区车位并泊入"<br>3. 激活漫游或巡航功能<br>4. 车辆开始前往J区车位 | 域控发送parking_area="J区"（A~J区支持） | 实车测试 | 区域车位-边界J区 | 业务逻辑层 |

### 5. 区域寻找指令（2个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-163 | 泊车 | HMI | P0 | 语音去A区寻找目的地 | 1. 车辆处于ready状态<br>2. 显示漫游界面<br>3. 停车场有A区标识 | InterfaceDisTyp=0x10或0x11<br>停车场包含A区 | 1. 语音指令"帮我停在A区"或"去A区"<br>2. 观察系统响应和语音反馈 | VLA链路识别【寻找目的地】【区域】<br>vla_req.intent=VLA_INTENT_PARK_SEARCH<br>vla_req.slots.parking_area="A区" | 1. 系统识别A区目的地<br>2. 语音播报确认反馈<br>3. 激活漫游功能<br>4. 车辆开始前往A区<br>5. 界面显示规划路径到A区<br>6. 到达A区后等待进一步指令或自动寻找车位 | 域控发送parking_area="A区" | 实车测试 | 区域寻找-A区 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-164 | 泊车 | HMI | P1 | 语音区域不存在异常提示 | 1. 车辆处于ready状态<br>2. 显示漫游界面 | InterfaceDisTyp=0x10或0x11 | 1. 语音指令"帮我去K区"（K区不在A~J范围）<br>2. 观察系统响应和语音反馈 | VLA链路识别但K区不在支持范围 | 1. 系统识别指令但无法执行<br>2. 语音播报"抱歉，未找到K区"或"暂不支持该功能"<br>3. 维持当前状态<br>4. 不执行漫游动作 | 系统不支持K区（仅支持A~J区） | 实车测试 | 区域不存在异常 | 业务逻辑层 |

---

## 三、特殊POI车位补充用例

### 6. 特殊POI车位指令（3个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-165 | 泊车 | HMI | P1 | 语音泊入电梯旁车位指令 | 1. 车辆处于ready状态<br>2. 显示2D地图或漫游界面<br>3. 停车场有电梯旁车位 | InterfaceDisTyp=0x1或0x11<br>存在电梯旁车位POI | 1. 语音指令"帮我泊入电梯旁车位"<br>2. 观察系统响应和语音反馈 | VLA链路识别【泊入车位】【电梯车位】<br>vla_req.intent=VLA_INTENT_PARK_IN<br>vla_req.slots.parking_position=PARKING_POSITION_LIFT | 1. 系统识别电梯旁车位目标<br>2. 语音播报确认反馈<br>3. 激活漫游或巡航功能<br>4. 车辆开始前往电梯旁车位<br>5. 界面显示电梯POI位置和规划路径 | 域控发送PARKING_POSITION_LIFT | 实车测试 | 电梯旁车位 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-166 | 泊车 | HMI | P1 | 语音泊入楼梯附近车位指令 | 1. 车辆处于ready状态<br>2. 显示2D地图或漫游界面<br>3. 停车场有楼梯附近车位 | InterfaceDisTyp=0x1或0x11<br>存在楼梯附近车位POI | 1. 语音指令"帮我泊入楼梯附近车位"<br>2. 观察系统响应和语音反馈 | VLA链路识别【泊入车位】【楼梯车位】<br>vla_req.intent=VLA_INTENT_PARK_IN<br>vla_req.slots.parking_position=PARKING_POSITION_STAIR | 1. 系统识别楼梯附近车位目标<br>2. 语音播报确认反馈<br>3. 激活漫游或巡航功能<br>4. 车辆开始前往楼梯附近车位<br>5. 界面显示楼梯POI位置和规划路径 | 域控发送PARKING_POSITION_STAIR | 实车测试 | 楼梯附近车位 | 业务逻辑层 |
| BFO-HMI-Thor-VLA-167 | 泊车 | HMI | P1 | 语音泊入商场车位指令 | 1. 车辆处于ready状态<br>2. 显示2D地图或漫游界面<br>3. 停车场有商场附近车位 | InterfaceDisTyp=0x1或0x11<br>存在商场附近车位POI | 1. 语音指令"帮我泊入商场附近车位"<br>2. 观察系统响应和语音反馈 | VLA链路识别【泊入车位】【商场车位】<br>vla_req.intent=VLA_INTENT_PARK_IN<br>vla_req.slots.parking_position=PARKING_POSITION_MARKET | 1. 系统识别商场附近车位目标<br>2. 语音播报确认反馈<br>3. 激活漫游或巡航功能<br>4. 车辆开始前往商场附近车位<br>5. 界面显示商场POI位置和规划路径 | 域控发送PARKING_POSITION_MARKET | 实车测试 | 商场车位 | 业务逻辑层 |

---

## 四、车外智驾灯功能用例

### 7. 车外智驾灯显示控制（8个用例）

| 用例编号 | 功能类型 | 分组 | 用例分级 | 用例名称 | 预置条件 | 预置条件-信号描述 | 测试步骤 | 测试步骤-信号描述 | 预期结果 | 预期结果-信号描述 | 标签信息 | 备注 | 层级 |
|---------|---------|------|---------|---------|---------|----------------|---------|----------------|---------|----------------|---------|------|------|
| BFO-HMI-Thor-VLA-168 | 泊车 | HMI | P0 | 智驾灯开关设置-开启 | 1. 车辆处于ready状态<br>2. 进入智驾设置菜单 | 配置文件SEC=SEC10 | 1. 查看智驾灯开关设置项<br>2. 点击开启智驾灯<br>3. 观察设置状态 | HUT发送IntellgntAsscLmpEnaResp=0x2:Full_bright | 1. 智驾灯开关显示【开启】状态<br>2. 设置项跟车记忆（上下电记忆）<br>3. Toast提示"智驾灯已开启" | IntellgntAsscLmpEnaResp=0x2 | 实车测试 | 智驾灯开关 | 系统层 |
| BFO-HMI-Thor-VLA-169 | 泊车 | HMI | P1 | 智驾灯开关设置-关闭 | 1. 车辆处于ready状态<br>2. 进入智驾设置菜单<br>3. 智驾灯当前为开启状态 | IntellgntAsscLmpEnaResp=0x2 | 1. 点击关闭智驾灯<br>2. 观察设置状态 | HUT发送IntellgntAsscLmpEnaResp=0x0:OFF | 1. 智驾灯开关显示【关闭】状态<br>2. 智驾不发点亮/熄灭信号<br>3. 后续智驾功能激活时智驾灯不亮 | IntellgntAsscLmpEnaResp=0x0 | 实车测试 | 智驾灯开关关闭 | 系统层 |
| BFO-HMI-Thor-VLA-170 | 泊车 | HMI | P0 | VLA漫游泊车人驾界面智驾灯熄灭 | 1. 车辆处于ready状态<br>2. 智驾灯开关为开启<br>3. 显示漫游泊车人驾界面 | InterfaceDisTyp=0x10:VLAP Preactive<br>FunctWorkSts=0x0:Standby<br>IntellgntAsscLmpEnaResp=0x2 | 1. 进入漫游泊车人驾界面<br>2. 检查车外智驾灯状态 | 域控发送IntellgntAsscLmpReq=0x1:OFF<br>CEM转发给灯具 | 1. 车外智驾灯熄灭（前后四个灯全部熄灭）<br>2. CEM反馈IntellgntAsscLmpSts=0x1:OFF<br>3. 灯具反馈FLIntellgntAsscLmpSts=0x1:OFF等<br>4. 车辆未控车状态不点亮智驾灯 | IntellgntAsscLmpReq=0x1:OFF | 实车测试 | VLA人驾灯灭 | 系统层 |
| BFO-HMI-Thor-VLA-171 | 泊车 | HMI | P0 | VLA漫游控车智驾灯常亮 | 1. 车辆处于ready状态<br>2. 智驾灯开关为开启<br>3. 漫游已激活 | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0x9:VLAP Roaming<br>IntellgntAsscLmpEnaResp=0x2 | 1. 双击拨杆或语音激活漫游<br>2. 进入漫游控车界面<br>3. 检查车外智驾灯状态 | 域控发送IntellgntAsscLmpReq=0x3:Always_Bright<br>CEM转发给灯具 | 1. 车外智驾灯点亮（前后四个灯全部常亮）<br>2. CEM反馈IntellgntAsscLmpSts=0x3:Always_Bright<br>3. 灯具反馈FLIntellgntAsscLmpSts=0x3:Always_Bright等<br>4. 智驾灯持续常亮直至漫游退出 | IntellgntAsscLmpReq=0x3:Always_Bright | 实车测试 | VLA漫游灯亮 | 系统层 |
| BFO-HMI-Thor-VLA-172 | 泊车 | HMI | P0 | VLA漫游APA阶段智驾灯常亮 | 1. 车辆处于ready状态<br>2. 智驾灯开关为开启<br>3. 沿途泊车发现车位进入APA | InterfaceDisTyp=0x11:VLAP Active Page<br>FunctWorkSts=0xA:VLAP Parking<br>APS_Worksts=0x3:Guidance | 1. 沿途泊车切换到APA泊车<br>2. 检查车外智驾灯状态 | 域控发送IntellgntAsscLmpReq=0x3:Always_Bright<br>CEM转发给灯具 | 1. 车外智驾灯保持常亮<br>2. APA泊车过程中智驾灯不熄灭<br>3. CEM反馈IntellgntAsscLmpSts=0x3:Always_Bright<br>4. 泊车完成后智驾灯熄灭 | IntellgntAsscLmpReq=0x3（APA阶段） | 实车测试 | VLA-APA灯亮 | 系统层 |
| BFO-HMI-Thor-VLA-173 | 泊车 | HMI | P0 | 有图巡航智驾灯常亮 | 1. 车辆处于ready状态<br>2. 智驾灯开关为开启<br>3. 有图巡航已激活 | InterfaceDisTyp=0x3:Cruise<br>IntellgntAsscLmpEnaResp=0x2 | 1. 双击拨杆或语音激活巡航<br>2. 进入巡航控车界面<br>3. 检查车外智驾灯状态 | 域控发送IntellgntAsscLmpReq=0x3:Always_Bright<br>CEM转发给灯具 | 1. 车外智驾灯点亮（前后四个灯全部常亮）<br>2. CEM反馈IntellgntAsscLmpSts=0x3:Always_Bright<br>3. 巡航过程中智驾灯持续常亮<br>4. 巡航退出后智驾灯熄灭 | IntellgntAsscLmpReq=0x3:Always_Bright | 实车测试 | 有图巡航灯亮 | 系统层 |
| BFO-HMI-Thor-VLA-174 | 泊车 | HMI | P0 | 漫游退出智驾灯熄灭 | 1. 车辆处于ready状态<br>2. 智驾灯开关为开启<br>3. 漫游控车中智驾灯常亮 | InterfaceDisTyp=0x11:VLAP Active<br>FunctWorkSts=0x9<br>IntellgntAsscLmpSts=0x3 | 1. 点击【退出】或系统异常退出<br>2. 检查车外智驾灯变化 | 域控发送IntellgntAsscLmpReq=0x1:OFF<br>CEM转发给灯具 | 1. 漫游退出同时车外智驾灯熄灭<br>2. CEM反馈IntellgntAsscLmpSts=0x1:OFF<br>3. 灯具反馈各灯状态为OFF<br>4. 智驾灯熄灭响应及时（与功能退出同步） | IntellgntAsscLmpReq=0x1:OFF | 实车测试 | 退出时灯灭 | 系统层 |
| BFO-HMI-Thor-VLA-175 | 泊车 | HMI | P1 | 智驾灯开关关闭后功能激活灯不亮 | 1. 车辆处于ready状态<br>2. 智驾灯开关为关闭<br>3. 显示漫游界面 | IntellgntAsscLmpEnaResp=0x0:OFF | 1. 双击拨杆或语音激活漫游<br>2. 进入漫游控车界面<br>3. 检查车外智驾灯状态 | 智驾灯开关关闭<br>域控不发IntellgntAsscLmpReq信号 | 1. 漫游功能正常激活<br>2. 车外智驾灯保持熄灭状态<br>3. 整个漫游过程智驾灯不点亮<br>4. 用户可正常使用VLA功能 | 智驾灯开关OFF时不发灯光信号 | 实车测试 | 开关关闭灯不亮 | 系统层 |

---

## 补充用例汇总

**本次补充用例数量**：23个  

### 按功能分类
1. 转向控制指令：4个（P0）
2. 速度调节指令：2个（P0）
3. 其他行为控制：2个（P0+P1）
4. 区域车位功能：3个（P0+P1）
5. 区域寻找功能：2个（P0+P1）
6. 特殊POI车位：3个（P1）
7. 车外智驾灯功能：8个（P0+P1）

### 按优先级分类
- **P0级别**：16个
- **P1级别**：7个

### 信号覆盖
- VLA语音Intent：VLA_steering_setting, VLA_speed_setting, VLA_stop_driving, VLA_driving_setting, VLA_INTENT_PARK_IN, VLA_INTENT_PARK_SEARCH
- 智驾灯信号：IntellgntAsscLmpEnaResp, IntellgntAsscLmpReq, IntellgntAsscLmpSts
- 车位Slots：parking_area (A~J区), PARKING_POSITION_LIFT/STAIR/MARKET

---

**补充用例文档生成完成！**  
**生成日期**：2026-01-26  
**文档版本**：v1.0  
**补充用例编号**：BFO-HMI-Thor-VLA-152 ~ BFO-HMI-Thor-VLA-175  
