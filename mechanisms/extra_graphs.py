from figures import *
import json,math

def nice(v):
 if isinstance(v,bool):return 'true（是）' if v else 'false（否）'
 if v is None:return 'null（空值）'
 if isinstance(v,float):return str(round(v,6)) if math.isfinite(v) else str(v)
 if isinstance(v,(list,dict)):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
 return str(v)
LABELS={
'correct':'正确路径','wrong':'错误对照','before':'变更前形状/状态','after':'变更后形状/状态','new_row_trainable':'新增行可训练',
'finite_fill_result':'用大负有限数填充后的份额','manual_minus_inf_nan':'手写全负无穷softmax出现NaN','torch_all_masked':'当前实现全遮蔽结果',
'once':'旋转一次','twice':'重复旋转','indices':'选取的有效位置','correct_gradient':'有效Token归一化梯度','mean_of_means_gradient':'错误批均值的梯度',
'token_counts':'各小批有效Token数','policy_gap':'当前策略对数概率差','reference_gap':'参考策略对数概率差','margin':'相对差异','loss':'目标损失',
'A_gradient':'低秩参数A的梯度','B_gradient':'低秩参数B的梯度','first_page':'只读取第一页','all':'完整读取所有页','audience':'令牌受众','resource':'访问资源','accepted':'是否接受',
'registered':'注册集合','visible':'模型可见集合','omitted':'字段省略的情景','empty':'显式空集合的情景','unknown':'不能推断的情景',
'canonical_types':'规范压缩结果的项目类型','lossy_types':'被错误删减后的类型','stale_revision':'过期快照版本','changed_rows':'条件更新影响行数','preserved':'保留下来的版本/状态',
'old_space_result':'同一空间的检索结果','mixed_space_result':'混用空间的检索结果','dimension':'向量维度','authorized_returned':'返回的授权候选数',
'position_of_b_codepoints':'b之前的Unicode码点数','utf16_units':'b之前的UTF-16单元数','utf8_bytes':'b之前的UTF-8字节数','text':'源文本','same_head':'HEAD是否相同',
'at_day6_known_day6':'在第6天、只用第6天前知识查询','at_day6_known_day9':'在第6天、用截至第9天知识查询','invalidated':'撤回后需失效的对象',
'exists':'文件存在','discovered':'描述被发现','selected':'被选中','body_loaded':'正文进入请求','cheap_cost':'首段成本','fallback_cost':'回退新增成本','rate':'回退比例','expected_cost':'期望总成本',
'producer_key':'生产者返回字段','consumer_key':'消费者读取字段','text_overlap':'文件文本重叠','compatible':'接口兼容','observed_joint':'同题共同错误比例','independence_guess':'未经验证的独立性估算',
'unsafe_effects':'无稳定键的副作用次数','keyed_effects':'有稳定键的副作用次数','crash_exit':'注入崩溃的退出码','per_layer_attempts':'每层最大尝试次数','max_leaf_calls':'底层最多调用次数',
'no_tests_exit':'没有收集到测试的退出码','all_skip_exit':'全部跳过的退出码','mutant_survives':'错误变体是否仍通过','weak_inputs':'不充分样本','strong_inputs':'补充反例',
'planned_version':'计划依据版本','current_version':'执行时版本','execute':'是否执行','screenshot':'截图像素尺寸','css_viewport':'CSS视口尺寸','overall_accuracy':'全部样本准确率',
'selective_accuracy':'选择回答部分的准确率','coverage':'回答覆盖率','weights':'注意力份额','values':'对应Value','weighted_terms':'加权后的各项贡献','output':'最终加权输出',
'capacity_positions':'缓存容量位置数','requests':'请求数','target':'目标分布','draft':'草稿分布','correct_distribution':'补偿后的分布','wrong_distribution':'错误重抽后的分布',
'changed':'是否发生改变','value':'值','result':'结果','success':'是否成功','done':'项目是否完成','status':'状态','id':'标识','call_id':'调用标识','arguments':'完整参数',
'input':'输入','label':'标签','observed':'实际观察','expected':'数学期望','retries':'重试次数','wall_clock':'墙钟时间','sum_spans':'跨度时长之和',
}

def flatten_result(obj,prefix=''):
 out=[]
 if isinstance(obj,dict):
  for k,v in obj.items():
   path=prefix+'.'+k if prefix else k
   if k in ['scope','source','notes','note','environment','synthetic','synthetic_only','diff','all_skip_output','stdout','stderr']:continue
   if isinstance(v,dict):out.extend(flatten_result(v,path))
   else:out.append((path,v))
 else:out.append((prefix,obj))
 return out

def result_graph(data,title,mobile=False):
 w=390 if mobile else 940;s=Canvas(w,title);y=30
 fields=flatten_result(data)
 # Priority to concrete paired results, keep short arrays/matrices and state booleans.
 kept=[]
 for key,v in fields:
  if len(nice(v))>420:continue
  kept.append((key,v))
  if len(kept)>=8:break
 for key,v in kept:
  leaf=key.split('.')[-1];lab=LABELS.get(leaf,leaf)
  s.text(22,y,lab,16,w-44,bold=True,color=BLUE);y=s.maxy+8
  s.text(22,y+14,key,12,w-44,color=MUTED);y=s.maxy+16
  # Strip leading singleton axes for display, still report original nested value for provenance.
  vv=v
  while isinstance(vv,list) and len(vv)==1 and isinstance(vv[0],list):vv=vv[0]
  if isinstance(vv,list) and vv and all(isinstance(a,(int,float,bool)) for a in vv) and len(vv)<=8:
   cw=(w-48)/len(vv);y=s.matrix(24,y,[vv],cw=cw,ch=48,formatter=lambda a:('真' if a else '假') if isinstance(a,bool) else nice(a))+28
  elif isinstance(vv,list) and vv and all(isinstance(a,list) for a in vv) and len(vv)<=5 and all(len(a)==len(vv[0]) for a in vv) and 0<len(vv[0])<=6 and all(isinstance(a,(int,float,bool)) for row in vv for a in row):
   y=s.matrix(24,y,vv,cw=(w-48)/len(vv[0]),ch=48,formatter=lambda a:('真' if a else '假') if isinstance(a,bool) else nice(a))+28
  else:
   txt=nice(v);h=len(wrap(txt,w-72,17))*25.5+30;s.rect(22,y,w-44,h,PALE);s.text(36,y+28,txt,17,w-72);y+=h+32
 return s.finish('数据来自本节原始JSON；布尔格中真=true、假=false。字段名为定位路径，只省略长日志，未改写数值。')

ENG_READ={
'E01':'把两条编号序列逐个对齐，关注开头和末尾的特殊标记是否重复；重复一项会改变模型实际收到的位置与前缀，不只是显示多一个符号。',
'E02':'先比较词表行数与每行宽度，再看新增行是否确实参与求导；查表不越界只验证“能访问”，没有验证输出头同步和优化器引用。',
'E03':'本节各子记录分别固定输入，单独改变投影、缩放或dropout。不要把不同子记录当成一条连续前向；同名接口接收的可能是原表示，也可能已是Q/K/V。',
'E04':'份额[0.5,0.5]看起来合法，却可能让两个本应禁止的位置都参与计算。NaN与零输出是不同实现的边界结果，应核对具体接口和版本，不用一条通用口诀替代测试。',
'E05':'先看每格“允许还是禁止”，再看输出数值。布尔True的语义反转与非方阵因果对齐，是两种不同错误；这里保留各自的独立输入和结果。',
'E06':'同一向量旋转一次与两次，其长度可能都没变，方向却变了。错误发生在位置信息被施加的次数或位置，而不是缓存数组长度。',
'E07':'mask控制读取关系，但最终从哪个位置取logits是另一步。索引记录指出每条样本最后一个真实位置，不能统一取被PAD占据的数组末尾。',
'E08':'各概率向量共享原始logits，但温度或筛选顺序不同。先核对被改动的条件，再比较保留候选集合；相同参数名并不能保证相同算法顺序。',
'E09':'有效Token数不同的微批，必须按目标规定的总分母归一化。不同梯度结果表示优化的目标已经改变，并非仅是浮点误差。',
'E10':'先把梯度还原到真实尺度，再讨论裁剪阈值。重计算还必须保持需要复现的状态一致；这些是训练顺序与副作用问题，不能只检查最后loss是不是有限数。',
'E11':'当前策略和参考策略的差值若相同，相减后的margin就是零；即使优选回答的绝对概率很高，偏好目标也没有获得相对改善。',
'E12':'初始化时低秩乘积的一侧为零，会让另一侧首步梯度为零。应同时检查另一参数的梯度和下一步更新，不把单个零数组立即判为反向断路。',
'E13':'先找到本记录的批量、层数、KV头、长度、宽度和每数位数，再相乘。总Query头与KV头不能互换，缓存逻辑容量也不等于物理已分配容量。',
'E14':'要同时观察共享引用与写入分支。两个请求读同一前缀可以共享，但其中一条扩展或改写时，不能无条件修改另一条仍在读取的共享对象。',
'E15':'把请求追加后的总位置需求与容量比较。装不下后发生的抢占和重算会消耗算力，所以GPU忙不意味着所有工作都在推进有效输出。',
'E16':'分别看目标分布、草稿分布和拒绝后的补偿质量。这里的输入只属于E16，不沿用其他推测解码小例子；补偿分布必须补回缺失质量，而不是再次无条件抽目标分布。',
'E17':'会话引用保存了哪些项目，与本轮重新提供了哪些规则，是两个清单。应该核对实际请求边界，不能由一个会话ID推断所有指令永久继承。',
'E18':'工具项、模型响应与业务任务分别有自己的完成条件。某个done=true只证明其所属对象结束，不能跨层升级成任务成功。',
'E19':'字符缓冲、事件缓冲与参数对象各自闭合。看到可解析的参数，还要核对调用/响应状态和权限；半个网络片段更不能触发写入。',
'E20':'缺字段、字段为null、路径未经授权是三个不同判断。Schema能限定结构和类型，业务授权仍由执行器核验。',
'E21':'比较第一页工具与完整工具集合。初始化成功并不说明分页已读完；找不到工具时先定位发现链路，而不是直接指责模型选错。',
'E22':'令牌标明的受众与目标资源必须匹配。会话ID用来关联会话，不是允许访问任意资源的授权令牌。',
'E23':'注册清单、模型可见清单和运行授权清单分别追踪。工具有实现，不等于这轮模型能选择它；模型能选择，也不等于每次动作获准。',
'E24':'省略字段与显式传空集合是否等价，取决于具体产品版本和配置语义。本记录是隔离的教学探针，不把一个宿主的行为推广到所有产品。',
'E25':'证据依赖要一起核对，而不是只挑最相关片段。一个阈值离开所属环境、单位和版本后，可能完全反转结论。',
'E26':'读时间与可用版本必须绑定。旧结果还在缓存里可以解释它为什么被返回，但不能证明它适合本轮问题。',
'E27':'比较规范返回项目类型与删减后的类型。压缩状态可能包含非普通摘要文本的协议项目；擅自只留下某个“最像摘要”的项目会破坏继续调用所需信息。',
'E28':'过期版本更新影响0行是保护成功，不是数据库失灵。原始事件从版本10前进到11后，基于10生成的摘要不能无条件覆盖11。',
'E29':'两套向量同为二维仍可能采用不同坐标体系。若查询和文档不再来自兼容模型，距离计算照常运行，排名含义却已失效。',
'E30':'先数授权后还剩几个候选。取很小的全局Top-k后才过滤，可能返回空集，即便稍后的位置确实有合法且相关的资料。',
'E31':'同一来源复制一遍会在RRF中多投一票。与真实独立检索源相比，它改变的是权重而不是新增证据，不能把重复结果当成独立支持。',
'E32':'把结论的主体、版本、套餐或时间条件与证据逐格配对。相关段落只说明主题相似；条件不一致时不能直接据此回答当前用户。',
'E33':'同一字符串“a😀b”，b前的码点、UTF-16单元、UTF-8字节数不同。位置里的整数必须带单位；版本也必须对应被编辑的实际文本。',
'E34':'HEAD相同只证明提交指针未移动。工作树或IDE缓冲区可以已经不同，验证结果需要绑定文件内容，而不只绑定commit字符串。',
'E35':'两次查询问的都是第6天，但允许使用的知识截止时间不同。不要把事后得知的规则偷偷带回当时的决策，除非明确做事后纠正。',
'E36':'从原始文档沿来源依赖向外看：分块、摘要、记忆、回答缓存都可能继承错误。删除文档文件本身不能保证派生结论消失。',
'E37':'逐项读exists、discovered、selected、body_loaded。第一处从真变假的边界，通常比反复改技能正文更值得先修。',
'E38':'期望成本必须把回退概率与新增成本相乘。但只有能识别首段失败，才会触发正确回退；廉价模型的漏检错误不能靠成本公式自动发现。',
'E39':'生产者和消费者的字段名称、单位才是语义接口。修改不同文件不会产生文本冲突，仍可能造成毫秒与秒的协议错配。',
'E40':'实际共同错误率与独立乘积估算是两列不同证据。相同模型、上下文、测试盲点会使错误相关；两份同意意见不自动构成独立验证。',
'E41':'崩溃退出码只标识故障注入点，关键是恢复后副作用次数。下游已提交而上游未记账时，无稳定幂等键重做会重复产生效果。',
'E42':'先分清“尝试总次数”与“额外重试次数”。各层上限相乘可以把一次顶层任务扩成大量底层调用，应统一预算而不是每层各自积极重试。',
'E43':'退出码0可能与“全部跳过”同时成立。验收要读取收集数、实际执行数、跳过原因和工件版本，不用一个绿色状态代替证据。',
'E44':'弱样本全通过时，错误变体也可能活下来。加入能区分正确与错误实现的反例后，再看测试是否拒绝该变体，才能证明测试真的覆盖了缺陷。',
'E45':'任务配对要按同一任务ID连接，不把不同题目的均值直接相减。新增成功与新增失败必须分别保留，才能定位退化。',
'E46':'重采样单位应与独立观察单位一致。多次运行同一题不是多道独立题；置信区间也不能代替实际收益与风险判断。',
'E47':'裁判若总选择左侧，互换候选位置后结论会改变。通过顺序对照可识别位置偏差；不应只把某次评分当成真值。',
'E48':'批准必须绑定具体参数和目标版本。批准后换路径、扩大金额或目标变化，都要重新校验，不能复用一个脱离动作的“同意”。',
'E49':'分位数描述分布尾部，不满足普通平均的合并规则。要合并原始样本或兼容的直方图桶，再求整体p95。',
'E50':'Trace里的并行跨度会重叠；相加是工作量，不是用户等待时间。关键路径和排队时间才解释哪一步真正影响响应。',
'E51':'计划版本7与执行时版本8不同，意味着计划依据可能过期。重新读取状态并检验额度/权限比直接执行旧计划更重要。',
'E52':'截图像素与CSS坐标先按视口尺度转换；页面布局变化后还要重新定位。比例算对不代表按钮仍在旧位置。',
'E53':'覆盖率下降可能让回答部分准确率上升。应该同时报告整体、已回答部分和拒答比例，不能用选择性准确率掩盖未服务的请求。',
'E54':'注意力份额最大的项，其Value可能为零；较小份额乘很大Value仍可能主导输出。热图亮度不是完整因果解释。',
'E55':'比较模型方案时固定任务、预算和输出约束。若运行配置同时改变，观测差异不能只归因于模型架构。',
'E56':'回滚代码并不自动回滚索引、记忆、缓存和任务Schema。状态版本兼容性必须验证，否则旧代码可能读不懂新状态。',
}
ENG_READ.update({
'E13':'首先核对缓存键是否包含模型、适配器、前缀及位置等身份，再检查两个请求是否意外共享可变对象。键相同不该复用、对象别名导致串写，是两类独立的缓存错误。',
'E14':'不同块的指数可能使用不同最大值作为基准。合并前要把旧的分母和加权和一起换到新基准；直接平均块答案会忽略每块实际概率质量。',
'E25':'前缀缓存比较的是实现规定的精确前缀身份，不是人感觉语义一样。时间戳、工具说明顺序等早段变化，会截断后续可复用的连续前段。',
'E26':'输入预算除了当前文件，还要为工具结果、生成输出和安全余量留位置。证据被压到只剩一个数字时，即使Token总数合规，也可能丢掉单位和适用环境。',
'E45':'先在同一组任务上逐题配对，再计算改善与退化。重采样还要按独立任务组织；若同题重复运行被当作独立新题，置信度会被夸大。',
'E46':'裁判若总选择左侧，互换候选位置后结论会改变。通过顺序对照可识别位置偏差；不应只把某次评分当成真值。',
'E47':'路径字符串落在允许目录里，不证明解析后的实际目标仍在该目录。符号链接和检查后替换可能改变目标；应把检查、打开和使用的对象绑定起来。',
'E49':'同一个表里有成本与耗时，但它们的分母和合并规则不同。并行Span相加不是墙钟；p95不能直接平均；失败费用也不能从每成功任务成本中删除。',
'E50':'版本是一组模型、Prompt、工具、索引、记忆Schema与代码的组合。只替换模型名却读取新Schema状态，可能让回滚产生新的兼容性错误。',
'E55':'训练一次的支出与上线后每次推理的支出要一起计算。预计请求量越大，长期推理差额越可能超过训练节省；最优结论依赖这个工作负载。',
'E56':'错误变体分别破坏一个不变量，再看验证能否准确指出它。单次成功不是证据链完整；能稳定拦住这类反例，才说明修复针对了已知故障边界。'
})
LABELS.update({
'A':'项目A','B':'项目B','a':'项目a','b':'项目b','accepted_mass':'直接接受的概率质量','aliased_b':'共享可变引用后的B','authorized':'已授权集合','break_even_calls':'收支相抵的调用数量','byte_count':'字节数','byte_identical':'字节是否完全一致','cache_slots':'缓存槽位','calls':'调用次数','changed_accepted':'改动参数后是否获准','commit_allowed':'是否允许提交','contributions':'各项加权贡献','copy_on_write_b':'写时复制保护下的B','correct_unscaled_clipping':'先还原梯度再裁剪','cost_per_success':'每个成功任务的总成本','counts':'样本计数','css_point':'CSS坐标','current':'当前值/版本','delta_initial':'初始参数增量','eligible_top2':'授权集合中的前两项','epoch':'迭代轮次','eval_without_dropout':'关闭dropout的推理输出','evidence_budget':'可用证据预算','extra_training_cost':'额外训练成本','full_gradient':'完整批梯度','gradient':'梯度','head':'提交指针HEAD','improvements':'新增成功题数','index':'索引版本','inference_saving':'每次推理节省','integration_fails':'集成是否失败','interaction':'交互对象','invariant':'被检查的不变量','inverted':'语义反转的对照','keep_after_temperature':'先温度调整后筛选保留项','keep_before_temperature':'温度调整前筛选保留项','keys_differ':'键身份是否不同','killed':'错误变体是否被检出','last_column':'直接取最后一列的结果','lexical_inside':'路径字符串位于允许范围','limit':'限制值','loss_sums':'各批损失总和','lossy_text_items':'丢失类型后的纯文本项','mask':'允许/禁止表','mean':'均值','mean_delta':'配对差异均值','mean_group_p95':'错误地平均各组p95','missing_field_valid':'缺少字段是否结构合法','model':'模型标识','mutant_killed':'错误实现是否被测试拦住','native_sdpa_observed':'本环境SDPA的观察结果','new':'新方案','new_hash':'新内容哈希','new_id':'新增编号','new_new':'新—新组合','new_old':'新—旧组合','null_field_valid':'显式null是否结构合法','old':'旧方案','old_hash':'旧内容哈希','old_new':'旧—新组合','old_old':'旧—旧组合','original_order_winner':'原顺序的裁判胜者','outputs_with_p_half':'dropout=0.5的多次输出','p_temperature1':'温度1的概率','p_temperature2':'温度2的概率','paired_task_delta':'逐任务配对差异','pending':'尚未确认状态','percentile_interval':'百分位区间','pixel_point':'截图像素坐标','pooled_p95':'合并样本后的整体p95','post_filter_top2':'先取前两项再过滤的结果','rank_sum_gradients':'各rank贡献的梯度和','read_observed':'实际读取内容','regressions':'新增失败题数','rejection_mass':'被拒绝的概率质量','required_pair':'需要一起保留的证据','reserved_generation':'预留生成预算','reserved_tool':'预留工具结果预算','residual':'拒绝补偿分布','resolved_inside':'解析后的目标位于允许范围','response_status':'整体响应状态','reuse_allowed':'是否可复用','same_model':'模型标识相同','same_system':'系统规则相同','seed':'随机种子','semantically_equal':'语义相同的设定','snapshot':'快照版本','static':'固定部分','successes_only_wrong':'仅统计成功费用的错误口径','sum_normalized_gradient':'按总分母归一化梯度','supports':'是否足以支持结论','swapped_order_winner':'交换顺序后的裁判胜者','synthetic_judge':'教学裁判规则','template':'模板标识','tier':'套餐/级别','tools':'工具标识','top_p':'累计筛选阈值','total':'总量','trials':'重复试验数','typed_items':'有类型的项目列表','unauthorized_path_executable':'未授权路径是否可执行','unchanged_accepted':'参数不变时是否获准','unicode_length':'Unicode码点长度','unknown_version_rejected':'未知版本是否被拒绝','upper_left':'局部左上三角对照','used':'已使用量','v1_ms':'版本1耗时（毫秒）','v2_ms':'版本2耗时（毫秒）','valid_positions':'有效位置','version':'版本号','wall':'墙钟时间','wrong_block_average':'错误地平均块结果','wrong_clip_then_unscale':'先裁剪再还原的错误顺序','wrong_redraw_p':'拒绝后直接重抽p的错误分布'})
