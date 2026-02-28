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
