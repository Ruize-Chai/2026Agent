# FOR DEVELOPER
# 后端开发说明

# Oriflow Agent BETA 1.0

## 后端提供的服务:
## HTTP SERVICE PROVIDE WITH BY BACKEND
### GET PLUGINLISTS
非流式GET 获取插件表
REQUIRE:NONE
RETURN:`PLUGIN LIST PAYLAOD`/"ERROR MESSAGE"




### FOR WORKFLOW MANAGEMENT:
关于工作流的注册和删除:
非流式POST 创建/(保存)工作流 CREATE A WORKFLOW WITH ID
REQUIRE:`WORKFLOW PAYLOAD`(设定好CONTEXT和PARAM)
RETURN:"OK"/"ERROR MESSAGE"

非流式POST 修改/(保存)工作流 ALTER A WORKFLOW WITH ID
REQUIRE:`WORKFLOW PAYLOAD`(设定好CONTEXT和PARAM)

非流式GET 获取工作流 GET A WORKFLOW WITH ID
REQUIRE:WORKFLOW ID
RETURN:`WORKFLOW PAYLOAD`(预设CONTXET和PARAM)/"ERROR MESSAGE"

非流式POST 删除工作流 DELETE A WORKFLOW WITH ID
REQUIRE:WORKFLOW ID
RETURN:"OK"/"ERROR MESSAGE"

非流式GET 获取工作流列表
REQUIRE:NONE
RETURN:`WORKFLOW LISTS PAYLOAD`/"ERROR MESSAGE"

### FOR WORKFLOW RUN-TIME MANAGEMENT:
关于工作流的运行控制:

*流式*POST RUN THE WORKFLOW
TIP:RUN AFTER ALTER
REQUIRE:WORKFLOW ID(*CURRENT WITHIN FRONT*)
RETURN:`NODE STATE LISTS PAYLOAD`/"ERROR MESSAGE"

#### RUN-TIME HUMAN INTERVENE
非流式POST HUMAN TEXT INPUT
TIP:WITH `TEXT INPUT` STATE ID
REQUIRE:`TEXT PAYLOAD` (WITH `NODE ID`)
RETURN:"OK"/"ERROR MESSAGE"

非流式POST HUMAN NUMBER INPUT
TIP:WITH `NUMBER INPUT` STATE ID
REQUIRE:`NUMBER PAYLOAD`(WITH `NODE ID`)
RETURN:"OK"/"ERROR MESSAGE"


非流式GET HUMAN CHECKBOX
TIP:WITH `CHECKBOX` STATE ID
REQUIRE:`NODE ID`
RETURN:`CHECKBOX SELECTIONS PAYLOAD`
+
非流式POST HUMAN CHECK
TIP:AFTER GET CHECKBOX
REQUIRE:`CHECK PAYLOAD` WITH `NODE ID`
RETURN:"OK"/"ERROR MESSAGE"

#### RUN TIME CHATBOX OUTPUT
非流式GET CHATBOX OUTPUT
TIP:NODE STATE:`OUTPUT`
REQUIRE:NODE ID
RETURN:`CHATBOX OUTPUT MESSAGE PAYLOAD`/"ERROR MESSAGE"

## RUN TIME INTERRUPT
非流式POST CHATBOX INTERRUPT
REQUIRE:NONE
RETURN:"ok"/"ERROR MESSAGE"

### LLM API MANAGE
非流式GET GET LLM API
REQUIRE:NONE
RETURN:`OPENAI SDK PAYLOAD`/"ERROR MESSAGE"

非流式POST SAVE LLM API
REQUIRE:`OPENAI SDK PAYLOAD`
RETURN:"OK"/"ERROR MESSAGE"

### FOR FILEBASE
非流式GET GET FILEBASELISTS
REQUIRE:NONE
RETURN:`FILEBASE LISTS PAYLOAD`/"ERROR MESSAGE"

# COMMUNICATE HUB
#### IN-COUMMUNICATE HUB 向内转发中枢
所有节点向HUB订阅一个通信窗口(MSG WINDOW).
HUB可以解析外来PAYLOAD并转发给占有它的NODE.
节点应当AWAIT 来自窗口的消息.
暴露的接口：外部转发要求.`in_commuHUB.send(nodeid:int,msg:Dict[Any])`


#### EX-COUMMUNICATE HUB 向外寄存中枢
所有节点向HUB订阅一个通信窗口(MSG WINDOW).
节点可以把信息寄存在此，等待前端的GET请求.
节点本身放置不必等待，放置后请提示前端GET。
暴露的接口:内部寄存要求，外部读取要求
`ex_commuHUB.cache(nodeid:int,msg:Dict[Any])`
`ex_commuHUB.fetch(nodeid:int)`

# NODE
包含以下核心数据:
1.节点类型`type`
2.监听引脚列表`listen`
3.激活引脚列表`output`
4.参数列表`params`:包括上下文调用依据`context_slot`和运行配置参数`param_config`
5.上下文资源管理`context`(Dict[str,Any])
其中`params`决定了节点的配置性参数`param_config`，也决定了节点可以调用哪些上下文`context_slot`。
根据节点任务，其管理（也即产出的上下文种类）和使用的上下文种类是固定的(未来允许拓展)
包含一个核心业务执行方法:`execute()`
绑定一个监视器，用于向外界反馈状态。(当然代码上可以绑定监听总线).
绑定一个引脚管理表，可以接收和管理引脚状态(代码上必须绑定特定引脚).
绑定两个I/O转发中枢.
绑定一个中断触发器，当中断触发时,不再点亮后续output节点.
包含一个实际调用的封装方法:`serve()`,是一个异步函数
`serve()`的逻辑；
1.所有前置引脚(ASYNCIO.EVENTS)触发
2.更新监视器
3.执行execute()(期间可能有监视器的变化)
5.更新监视器
4.执行完毕后，出发后置引脚(ASYNCIO.EVENTS)
`serve()`的逻辑可以直接由Node实现
`execute()`的逻辑由各个节点实现
节点若向前端提供服务，有其专属的通信`Pydantic PAYLOAD`格式与PyDict参数包解析.

# FLOW_LISTENER
状态监视器(本身不实现,直接实现总线).和节点是一对一的关系。节点列表和状态监视总线互相进行双射绑定.
它含有一个`ENUM`，分类不同的状态`STATE`。
它还含有一个`STATE`列表,可以流式反馈给前端
暴露接口:`flow_listener.read()`

# PIN_MANAGER
引脚管理器（包含各种EVENT），管理NODE的异步触发。
和NODE事先实现了绑定（通过它们的listen字段）
所有被节点listen的引脚触发后，节点开始运作。
在前端工作图中，每一个连线都有一个编号，它们意味着一对节点间的激活引脚
暴露接口:`pin_manager.activate(id:int)`

# INTERRUPT
中断触发器,所有节点绑定到此.管理一个布尔值.

# WORKFLOW
存放在WorkflowBase文件夹中.这个文件夹里，你可以通过workflowlists.json获取workflow数据文件表格，也可以根据workflow_id.json找到独属于这个workflow的文件架子。`LLM_GenerateWorkflow`节点生成并可以存储workflow到特定文件.(由于大模型的文件生成模式性能更好，于是我们采用了这一类设计)

workflow创建时完成各模块的绑定.
workflow启动所有节点的serve(),再激活entry:0号节点,实现对`START`节点的启动.
`END`节点后不允许接output,终结流程.

# PLUGINS
这里是关于各个plugins的实现建议:
(output无特殊说明均为全部激活)
## 1.START
一个输入节点接其他几个输出节点，无特性
input:0（ENTRY）
output:全部激活

## 2.END
特点：无输出节点
output:None

## 3.TEXT INPUT
特点：调用前端的人工输入服务，结果放置在context中.
state:`TEXT INPUT`
payload:`TEXT PAYLOAD`
output:全部激活

## 4.NUMBER INPUT
特点：调用前端的数字输入服务，结果放置在context中.
state:`TEXT INPUT`
payload:`TEXT PAYLOAD`
output:全部激活

## 5.CHATBOX
特点：调用前端的CHATBOX输出服务,需要context_slot索取一个context
state:`OUTPUT`
payload:`CHATBOX OUTPUT MESSAGE PAYLOAD`
output:全部激活

## 6.CHECKBOX
特点:调用前端的CHECKBOX输出服务,需要context_slot索取多个context,数目由params_config决定
前端会显示一个决策框.
output依然全部激活。context中存入用户的选择.
state:`CHECKBOX`
payloads:`CHECKBOX SELECTIONS PAYLOAD` & `CHECK PAYLOAD`

## 7.DELAYTIMER
特点:一个延时工具，没有特性.

## 8.IFCONDITION
特点:它允许基于context.slot所指定的上文bool变量，实现对节点的操控。
它最多允许两个引脚.

output:所读boolean:如果为真：启动IF引脚;如果为假:启动ELSE引脚;

## 9.LLM_ANSWER
特点:它在context_slot里寻找上文.个数不限，打包输入，只要是str.
param_config 设定好所用的model和模型生成参数.
调用大模型能力:Answer.
结果放在context.

## 10.
"LLM_Answer",
"LLM_Summarize",
"LLM_QA",
“LLM_Translate",
"LLM_CodeGeneration",
"LLM_Conversation",
同上.
基本上就是主Prompt不同。
实现的时候，可以把这六个类的节点类都继承一个节点类

## 11.LLM_FileProduction
下文存储在FileBase文件夹中
名字由param_config确定.
更新filebaselists.json.

## 12.LLM_GenerateWorkflow
校验workflow.
下文存储在WorkflowBase文件夹中
名字由workflowid决定
更新workflowlists.json.

# ABOUT OPENAI SDK API SKEY
# 关于大模型OPENAI SDK:
现在是把api key和endpoint存储在了运行时全局变量里，后期开发会做鉴权管理系统。

# ABOUT ERROR EXCEPTIONS:
# 关于后端错误处理
捕获后全部做三件事:1.转发给前端（假如在业务流程中）,也就是每个服务中做一个异常捕获。, 2.控制台彩色输出 , 3.记录日志到log文件
程序开始后第一件事是划分日志文件，写入日志启动头.
所有错误捕获后抛出编码了的自定义错误.捕获基类:OriflowError.


# CODE:
先约定Payload啊，然后是实现引脚表，监听器和中断器还有通信中枢，再写节点类，再写workflow，再写节点类多态插件，最后写网络服务





