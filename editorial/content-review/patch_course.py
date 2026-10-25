from pathlib import Path
from bs4 import BeautifulSoup, Tag
from html import escape as E
import json, hashlib, re, os, copy

WORK=Path('/mnt/data/_content_audit_20261024')
ROOT=WORK/'build/AI_Systems_Engineering_Textbook_ZH'
DATA=json.loads((ROOT/'labs/model/data/run.json').read_text())
RESULTS=json.loads((WORK/'audit/new-results.json').read_text())
P=DATA['initial_parameters']; T=DATA['initial_trace']; edits=[]; cache={}; moved={}

def get(page):
    if page not in cache: cache[page]=BeautifulSoup((ROOT/page).read_text(),'lxml')
    return cache[page]
def fragment(html):return list(BeautifulSoup(html,'html.parser').contents)
def insert_after(tag,html):
    for x in fragment(html): tag.insert_after(x);tag=x
    return tag

def table(headers,rows,caption=None):
    cap=f'<caption>{E(caption)}</caption>' if caption else ''
    return '<div class="table-wrap"><table>'+cap+'<thead><tr>'+''.join('<th scope="col">'+str(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def fmt(x,dec=6):
    if isinstance(x,bool): return '允许' if x else '禁止'
    return f'{x:.{dec}f}' if isinstance(x,(float,int)) else str(x)
def vec(a,dec=6):return '['+', '.join(fmt(x,dec) for x in a)+']'
def matrix(name,arr,labels=None):
    return table(['输入特征行 / 输出列']+[str(i) for i in range(len(arr[0]))],[[labels[i] if labels else i]+[fmt(x,3) for x in row] for i,row in enumerate(arr)],name)
def row(k):return T[k][0][2]
def note(page,ids):
    prefix=os.path.relpath(ROOT/'sources.html',(ROOT/page).parent).replace(os.sep,'/')
    return '<p class="source-note">依据与范围：'+ '；'.join(f'<a href="{prefix}#review-{i}">[{i}]</a>' for i in ids)+'。算例条件在本节给定；教学结果不代表商业模型或生产性能。</p>'
def local(page,target,label):return f'<a href="{os.path.relpath(ROOT/target,(ROOT/page).parent).replace(os.sep,"/")}">{label}</a>'
def findh(page,query):
    s=get(page);h=s.find(id=query)
    if h:return h
    hs=[x for x in s.select('article h2,article h3,article h4') if x.get_text(' ',strip=True)==query]
    if not hs: hs=[x for x in s.select('article h2,article h3,article h4') if query in x.get_text(' ',strip=True)]
    if len(hs)!=1:raise ValueError((page,query,[(x.get('id'),x.get_text()) for x in hs]))
    return hs[0]
def end_of_section(h):
    rank=int(h.name[1]);last=h
    for x in h.next_siblings:
        if isinstance(x,Tag) and re.fullmatch('h[1-6]',x.name) and int(x.name[1])<=rank: break
        # Stay before standalone block or a following question.
        if isinstance(x,Tag) and x.name=='section' and 'mechanism-question' in x.get('class',[]):break
        last=x
    return last

def record(page,action,anchor,issue,detail=''):
    edits.append(dict(page=page,action=action,anchor=anchor,issues=issue,detail=detail))
def add(page,after,title,body,ident,issues,sources=None):
    h=findh(page,after);html=f'<h3 id="review-{ident}">{title}</h3>'+body
    if sources:html+=note(page,sources)
    insert_after(end_of_section(h),html);record(page,'integrate',h.get('id'),issues,title)
def add_inside(page,anchor,html,issues,immediate=False):
    h=findh(page,anchor);insert_after(h if immediate else end_of_section(h),html)
    record(page,'restore-computation',h.get('id'),issues)
def replace_paragraph(page,contains,html,issues):
    s=get(page);ts=[x for x in s.select('article p') if contains in x.get_text(' ',strip=True)]
    if len(ts)!=1:raise ValueError(('paragraph',page,contains,len(ts)))
    tag=ts[0];before=tag.get_text(' ',strip=True)
    for new in fragment(html):tag.insert_before(new)
    tag.decompose();record(page,'replace',contains,issues,before[:100])
def replace_h_section(page,anchor,body,issues,new_title=None):
    h=findh(page,anchor);rank=int(h.name[1]);removed=[]
    for x in list(h.next_siblings):
        if isinstance(x,Tag) and re.fullmatch('h[1-6]',x.name) and int(x.name[1])<=rank:break
        # preserve anchor spans while dropping obsolete duplicate text
        if isinstance(x,Tag) and x.name=='span' and x.get('id'):continue
        removed.append(x.get_text(' ',strip=True) if isinstance(x,Tag) else str(x))
        x.extract()
    if new_title:h.string=new_title
    insert_after(h,body);record(page,'rewrite-subsection',h.get('id'),issues,'Replaced redundant or ambiguous subsection; anchors retained')

# Restore the concrete calculation chain from the unchanged model record.
p='foundations/05.html'
body=table(['同一位置的对象','第0维','第1维','第2维','第3维'],[
 ['Token参数 E[2]']+[fmt(x,3) for x in P['E'][2]],['位置参数 P[2]']+[fmt(x,3) for x in P['P'][2]],['逐格相加 X[0,2]']+[fmt(x,3) for x in row('x')]],'初始化参数θ₀；b=0表示第一句话，t=2表示加入BOS后的第三个位置')
body+='<p>逐格核对：第0维是 −0.3＋0.1＝−0.2；第1维是 0.8＋0＝0.8；第2维是 0.1−0.1＝0；第3维是 0.5−0.05＝0.45。这里Token编号和位置编号恰好都为2，只是巧合：另一个位置出现“爱”，仍取E[2]，但应取那个位置的P行。E与P都是本模型可训练的参数表，不是二进制编码。</p>'
h=findh(p,'core-parameters-3--mc-section-3');target=h.find_next_sibling('p');insert_after(target,body);record(p,'restore-computation',h.get('id'),['A01'])

p='foundations/10.html'
body=table(['特征j','Xⱼ','Xⱼ²','r＝√(均方＋ε)','g1ⱼ','N1ⱼ＝Xⱼ/r×g1ⱼ'],[[i,fmt(x),fmt(x*x),fmt(T['r1'][0][2][0],9),fmt(P['g1'][i],3),fmt(row('n1')[i],9)] for i,x in enumerate(row('x'))], '同一初始参数θ₀、同一位置；RMSNorm不减均值')
body+='<p>平方和为0.04＋0.64＋0＋0.2025＝0.8825；除以4得0.220625，再加ε＝0.00001，开方得0.469718001。最后四个结果仍对应原来的四个特征。初始g1全为1；训练后它不必仍为1。下一节投影用的是这排N1，而不是绕过归一化直接使用X。</p>'
add_inside(p,'core-normalization-2--mc-section-2',body,['A02'])

p='foundations/11.html'
body='<p>以下全部来自贯通模型的初始化参数θ₀。行对应输入的4个特征，列对应要计算的4个输出特征。计算第j个输出时，取N1这一行与参数表的第j列逐项相乘再相加；三张表并不共享数值。</p>'
for key in ['Wq','Wk','Wv']:body+=matrix(key+'：4×4',P[key])
body+=table(['同一位置b=0,t=2','运算','完整结果'],[['输入N1','F10的RMSNorm输出',vec(row('n1'),9)],['Q','N1 @ Wq',vec(row('q'),9)],['K','N1 @ Wk',vec(row('k'),9)],['V','N1 @ Wv',vec(row('v'),9)]])
body+='<p>例如Q的第0格：<code>(−0.425787387)×0.2＋1.703149547×0.1＋0×(−0.2)＋0.958021620×(−0.2)≈−0.106446847</code>。下表和后文保留的是完整精度计算后显示的结果；手算四舍五入数时可能相差末位。W是长期参数，Q/K/V是本次前向的中间量，不能交换二者的身份。</p>'
add_inside(p,'core-qkv-2--mc-section-2',body,['A03'],True)

p='foundations/14.html'
add_inside(p,'core-value-residual-4--mc-section-4',matrix('Wo：把混合结果转换回残差宽度',P['Wo'])+table(['输入mix','运算','输出attn_delta'],[[vec(row('mix'),9),'mix @ Wo',vec(row('attn_delta'),9)]]),['A04'])
add_inside(p,'core-value-residual-5--mc-section-5',table(['特征j','原输入X','注意力分支attn_delta','残差结果R＝X＋attn_delta'],[[i,fmt(row('x')[i],9),fmt(row('attn_delta')[i],9),fmt(row('residual')[i],9)] for i in range(4)]),['A04'])
add_inside(p,'core-ffn-2--mc-section-2',matrix('W1：4个输入特征到8个中间特征',P['W1'])+table(['R经第二次RMSNorm后的N2','N2 @ W1得到ff_pre'],[[vec(row('n2'),9),vec(row('ff_pre'),9)]]),['A04'])
body=table(['中间特征j','ff_preⱼ','ReLU(ff_preⱼ)','为何保留/置零'],[[i,fmt(x,9),fmt(row('ff_act')[i],9),'大于0，保留' if x>0 else '不大于0，置零'] for i,x in enumerate(row('ff_pre'))])
body+=matrix('W2：8个中间特征回到4个残差特征',P['W2'])
body+='<p>只有第2、3个中间特征非零，所以本位置的压回结果等于 <code>ff_act[2]×W2[2,:]＋ff_act[3]×W2[3,:]</code>，得到 <code>'+vec(row('ff_delta'),9)+'</code>。这是本次输入的现象，不代表可以永久删掉其他行；换输入或更新参数后，激活位置可能改变。</p>'
add_inside(p,'core-ffn-3--mc-section-3',body,['A04'])
add_inside(p,'core-ffn-4--mc-section-4',table(['特征j','主路R','FFN分支ff_delta','hidden＝R＋ff_delta'],[[i,fmt(row('residual')[i],9),fmt(row('ff_delta')[i],9),fmt(row('hidden')[i],9)] for i in range(4)])+'<p>hidden再经过最终RMSNorm，得到 <code>'+vec(row('final'),9)+'</code>。下面输出头所读的是这排final，不是N1、R或ff_act。</p>',['A04'])
body=matrix('U：4个内部特征到8个词表候选；列顺序为PAD、我、爱、学习、你、！、BOS、EOS',P['U'])
body+=table(['候选ID','Token','logit＝final·U[:,ID]','softmax概率'],[[i,E(v),fmt(row('logits')[i],9),fmt(row('probabilities')[i],9)] for i,v in enumerate(DATA['spec']['vocab'])])
body+='<p>本行的正确训练目标是“学习”，其概率约0.207640683，不是已经生成正确句子的证据。训练时还要把另外九个位置一起计分；推理时才会根据解码规则从候选中选择新Token。</p>'
add_inside(p,'core-output-head-2--mc-section-2',body,['A04'])

p='foundations/18.html'
for i,anchor in enumerate(['core-generation-2--mc-section-2','core-generation-3--mc-section-3','core-generation-4--mc-section-4']):
 step=DATA['generation_full']['steps'][i]
 body='<p>本轮使用<strong>训练完成的θ*</strong>，实际输入为<code>'+str(step['input'])+'</code>；以下logits都来自最后一个有效输入位置，不接续F14初始化θ₀的那一行。</p>'
 body+=table(['ID','词表项','本轮logit','本轮概率'],[[j,E(v),fmt(step['logits'][j],9),f"{step['probabilities'][j]:.9g}"] for j,v in enumerate(DATA['spec']['vocab'])],f'完整重算生成第{i+1}轮；贪心选择ID{step["selected"]}（{step["selected_text"]}）')
 if i==2:body+='<p>EOS结束当前生成，不作为普通字显示，也不再自动输入下一轮。它不能替代Agent对文件、测试或业务动作的验收；那是前面执行循环中的另一层完成状态。</p>'
 add_inside(p,anchor,body,['A05'])

p='foundations/19.html'
body=table(['Query绝对位置 / Key绝对位置',0,1,2,3,4],[[3,'允许','允许','允许','允许','禁止'],[4,'允许','允许','允许','允许','允许']], '已有位置0—2；本轮一起处理位置3、4；允许条件key_position≤query_position')
body+='<p>第一个新Query位于绝对位置3，可以看0、1、2、3，不能看4；第二个可以看0—4。表有2行5列，不能用普通2×5左上三角只允许第一行看Key0。构造这张表只说明因果关系；如有补齐或不同请求，还要叠加相应有效性与请求边界。</p>'
add_inside(p,'core-cache-5--mc-section-5',body,['A06'])

p='chapters/02.html'
body='<p>固定初始化θ₀、第一句话b=0、加入BOS后的“爱”t=2。每一行的输入来自上面的既有对象；数值均从同一份运行记录读取。</p>'
rows=[]
for name,key,origin in [('X','x','E[2]＋P[2]'),('N1','n1','RMSNorm(X,g1)'),('Q','q','N1@Wq'),('K','k','N1@Wk'),('V','v','N1@Wv'),('mix','mix','本Query的A行乘所有可见V'),('注意力分支','attn_delta','mix@Wo'),('R','residual','X＋注意力分支'),('N2','n2','RMSNorm(R,g2)'),('FFN中间值','ff_pre','N2@W1'),('FFN激活','ff_act','ReLU(中间值)'),('FFN分支','ff_delta','激活@W2'),('hidden','hidden','R＋FFN分支'),('final','final','RMSNorm(hidden,gf)'),('logits','logits','final@U'),('概率','probabilities','softmax(logits)')]:
 rows.append([name,origin,vec(row(key),9)])
body+=table(['对象','计算来源','本位置实际数值'],rows)
body+='<p>这份前向记录本身不改变任何参数。进入训练时，它连同标签用来计算损失和梯度；完成训练后再做推理时，结构相同而参数已是θ*，不能将两个阶段的中间量互相拼接。</p>'
add_inside(p,'core-forward-trace-3--mc-section-3',body,['A07'],True)

# Stop point; subsequent source-based prose edits are appended below.

# Local prerequisite bridges: definitions appear where the outside-in reader needs them.
add('foundations/26.html','模型不会自动看见整台电脑','此处的Token先理解为计量单位',
    '<p>本节把模型当黑盒，只需先知道：<strong>Token是分词器把文本转换成的编号单位</strong>，不固定等于一个字或一个单词。输入预算统计的是本次真实序列，包括规则、历史、工具说明和材料；输出预算限制的是模型生成。字数只能粗估，不能精确证明“装得下”。这里的预算也不是长期记忆容量。</p><p>例如两段中文各100字，代码、标点和分词规则不同，Token数可以不同。应使用实际模型配套的计数规则或服务提供的用量信息；等进入F03再拆开编码过程。当前先把它当有限的输入空间，判断哪些证据必须进入，而不是提前猜内部矩阵。</p>',
    'token-unit',['A09'],['PROMPT'])
add('foundations/29.html','资料不足时的正确动作','查询改写与HyDE：生成的是检索线索，不是证据',
    '<p><strong>查询改写</strong>是把用户问题换成更适合搜索的表达，仍要保留限定条件。例如“这笔去年差旅能不能报销”可以拆成“差旅制度、发生时间、员工类别、费用类别”，但不能悄悄删掉“去年”。</p><p><strong>HyDE</strong>是一种先生成假想回答或文档、再用其表示寻找真实资料的检索办法。假想内容只作为搜索线索，不是已核实事实。若模型先假想“最多报销500元”，实际资料却写300元，应以适用版本的真实资料为准；不能把假想回答再次检索出来便当作双重证据。改写前后应比较召回与最终任务结果，不只看措辞变得专业。</p>',
    'hyde-bridge',['A09'],['HYDE'])
add('foundations/36.html','为什么多跑几次仍不等于更多独立任务','Bootstrap到底重新抽什么',
    '<p><strong>Bootstrap（自助重采样）</strong>是在已有样本中有放回地抽取同样数量的样本，再计算指标；多次重复，用来观察结论对样本构成的敏感程度。它不是运行模型的新试验，也不会凭空补出尚未观察到的困难任务。</p><p>例如三个任务的配对结果是T1=(旧失败,新成功)、T2=(旧成功,新成功)、T3=(旧成功,新失败)。一次抽样可能得到T1、T1、T3，净增益变为1/3。关键是每次把同一任务的旧、新结果<strong>成对抽走</strong>。若每任务有多次trial，先保留任务分组；不能将同题的十次运行当作十个完全独立任务。小样本、任务相关或反复调参都会限制这种估计的解释。</p>',
    'bootstrap-bridge',['A09','A22'],['EVAL'])

add('foundations/03.html','先固定片段、编号和边界','聊天模板决定谁在说话，不能让两个步骤重复加边界',
    '<p>角色对象不是模型直接读取的Python字典。<strong>聊天模板</strong>将角色、内容和轮次边界按某个模型约定排列成序列。模板属于模型输入协议；同一段普通文字放在不同角色边界后，表示的任务可能不同。</p>'+
    table(['步骤','实际对象','需要核对'],[['准备消息','user问题＋assistant示范','训练数据是否真的含有期望回答'],['渲染模板','边界标记＋角色＋文本','标记是否来自该模型配套模板'],['分词','整数ID列表','模板若已加特殊标记，第二次分词不要重复添加'],['训练/生成','评分已有答案或开启新回答','训练通常保留完整示范，生成才按模板开启待续助手段']])+ 
    '<p>HF文档给出的特定接口约定是：先<code>apply_chat_template(tokenize=False)</code>得到字符串后，再分词应避免额外加入模板已经包含的特殊Token；直接<code>tokenize=True</code>能减少这类双重处理。不能由此推出所有模型都需要同一种BOS/EOS，也不能手工给任何聊天模型套上相同角色字符串。验收时打印一条完整ID序列及解码结果，检查边界数量和位置。</p>',
    'template-boundary',['A10'],['CHAT-TEMPLATE'])
add('foundations/04.html','从完整句子得到训练输入与目标','数学上错开一位，代码里只能由一层负责',
    '<p>本教材手写模型明确使用输入<code>[BOS,我,爱,学习,！]</code>和目标<code>[我,爱,学习,！,EOS]</code>，再对齐计算普通交叉熵。另一些框架接受整条序列与同长度labels，并在损失函数内部错开一位。两种代码表面不同，数学目标可以相同。</p><p>因此看到别人写<code>labels = input_ids.copy()</code>，既不能立即断言“错误地学复制”，也不能断言一定正确。先确认模型的损失入口是否负责移位。本书这台手写模型不负责再次移位；使用内部已移位的包装器却继续传手动移位标签，会错成预测后后一个Token。F16先沿手写模型训练，机制Q017再对照真实框架源码。</p>',
    'shift-owner',['A11'],['LOSS'])
add('foundations/12.html','合并因果与补齐限制','同一个EOS编号可以出现在有效位置和补齐位置',
    '<p>以下是<strong>独立接口例</strong>，不是改变贯通模型的PAD=0、EOS=7设定。假设某分词器用7同时表示EOS和补齐：一行ID为<code>[BOS,我,7,7]</code>，有效标记为<code>[1,1,1,0]</code>。第三个位置的7是有效结束标记，第四个位置的7才是补齐。</p>'+
    table(['物理位置','ID身份','可作为有效上下文','在未移位labels中的处理'],[[0,'BOS','是','依训练目标决定'],[1,'我','是','依训练目标决定'],[2,'7＝真实EOS','是','应保留结束目标，除非配方另有约定'],[3,'7＝补齐','否','设ignore_index，不参与评分']])+
    '<p>若直接用<code>labels[ids == 7] = -100</code>，会把真实EOS目标也删掉。应依据每条样本的实际长度或有效位置标记区分，不依据编号猜用途。还要注意：这里展示的是未移位标签，最终哪行logit为EOS负责，要按唯一的移位规则对齐。</p>',
    'eos-pad-mask',['A12'],['LOSS','SFT'])
add('chapters/04.html','用五个Token走完对齐','对照真实损失入口：两种正确移位与一种错误叠加',
    '<p>为避免接口参数名造成误判，固定完整序列<code>s=[6,1,2,3,5,7]</code>。第一种是本书的显式对齐；第二种以Transformers <code>v4.52.3</code>的<code>ForCausalLMLoss</code>为已读代码样本，其默认分支在labels末端补ignore，再取<code>labels[...,1:]</code>。这只是所引入口的约定，不代表每个模型类都自动这样做。</p>'+
    table(['调用方式','送入前向的ID','传给损失入口的labels','实际评分目标'],[['本书：直接交叉熵','[6,1,2,3,5]','[1,2,3,5,7]','五个位置预测下一个'],['所引HF包装器：内部移位','[6,1,2,3,5,7]','[6,1,2,3,5,7]','[1,2,3,5,7,ignore]'],['错误：外部和内部都移位','[6,1,2,3,5]','[1,2,3,5,7]','[2,3,5,7,ignore]，首位错成预测“爱”']])+ 
    '<p>两个正确写法是否给出相同损失，还要求有效位置、归一化分母及对应logits一致。若损失按有效Token平均，最后一个被忽略的位置不进入分母；若全部标签都被忽略，应跳过或明确报错，不让空分母产生NaN后继续更新。随包小测试核对的是标签映射与分母语义，未安装并冒充运行这份历史Transformers版本。</p>',
    'causal-label-contract',['A11','A12'],['LOSS','LOCAL'])
add('chapters/03.html','追问：两份文档拼接训练，只放一个EOS就完全隔离了吗？','真正打包时，三种边界要同时对齐',
    '<p>固定独立片段A占位置0—2，B占位置3—4。普通因果表允许B读取A；严格按样本隔离的表还要求<code>segment(q)==segment(k)</code>，因此位置3只能读3，位置4只能读3、4。EOS只是一种输入值，不会替宿主建立这条约束。</p>'+
    table(['边界','负责什么','漏掉后怎样错'],[['attention分段','禁止B的查询读取A的K/V','跨样本信息泄漏'],['loss分段','不把A末尾预测B开头作为无意目标','把独立文档拼成错误续写训练'],['position约定','为每个片段选择重置或连续编号，配合模型实现','边界与位置不匹配，训练/推理输入协议漂移']])+ 
    '<p>“packing更省padding”只描述效率动机，不自动保证上述边界。框架可能使用块掩码、长度数组或专门内核表达它们。读取实际实现并做负控制：只改A内容，若规定严格隔离，B的logits不应因此改变；同时检查B第一道评分题是否仍存在且对应正确前缀。</p>',
    'packed-contract',['A12'],['LOSS','SFT'])

add('foundations/16.html','实际训练并保存同一套模型','能生成的权重文件，不等于能无缝续训的检查点',
    '<p>本教材保存的模型结构与参数足够让推理程序重新做前向；但AdamW还保存过去梯度的统计。只恢复参数，相当于站在同一个位置、却忘了优化器的行进历史，因此下一步可以不同。</p>'+
    table(['目的','至少要恢复什么','本书对应证据'],[['部署或复算前向','结构、参数、词表/模板、位置与精度约定','已有八词表模型的参数文件与推理程序'],['接着原训练继续','再加优化器状态、全局步数和数据位置；涉及随机层/调度时还需其状态','本节标量AdamW对照'],['宣称完全可复现','还需环境、内核、随机数及数据加载顺序等一致条件','本书不保证任意硬件/分布式逐bit复现']])+ 
    f'<p>新的CPU对照只训练一个标量：连续完成四次更新得到<code>{RESULTS["checkpoint"]["uninterrupted"]:.12f}</code>；第二步后恢复参数与优化器状态，再做两步，结果相同；只恢复参数而重建AdamW，得到<code>{RESULTS["checkpoint"]["weights_only"]:.12f}</code>。例子很小，但差异真实来自运行，不是画出来的曲线。完整代码在'+local('foundations/16.html','labs/content_contracts.py','content_contracts.py')+'；原400步语言模型权重没有被这项测试改动。</p>',
    'checkpoint-purpose',['A14'],['TORCH-SAVE','LOCAL'])
add('chapters/04.html','追问：恢复训练只加载权重够不够？','恢复的是下一次更新的全部输入，而不只是θ',
    '<p>把更新写成<code>(θₖ₊₁, oₖ₊₁)=update(θₖ, oₖ, batchₖ, lrₖ)</code>，其中o是优化器状态。对带随机性的训练，还要有随机状态r；数据采样器决定batch来自哪条记录。只加载θ，却重新初始化o、r或重头读数据，已不是同一次训练的继续。</p>'+ 
    table(['状态','保存原因','典型漏项'],[['model / optimizer','参数与一阶、二阶矩共同决定更新','只存state_dict，重启后前几步跳变'],['scheduler / global_step','学习率与预热位置一致','按microbatch步数而非optimizer步数推进'],['scaler（如启用）','混合精度损失缩放与溢出跳步','恢复后缩放状态重置'],['RNG / sampler / data revision','Dropout、打乱顺序、样本版本可追溯','恢复到旧游标却读取新版数据'],['累计边界','一个优化步可能含多个microbatch','半途快照未保存累积梯度却直接继续']])+ 
    '<p>更简单且容易验证的策略是只在一次optimizer更新完成、累积梯度已清理后的边界保存；先写完整临时文件，再按存储语义完成替换，并记录成功。不是每个训练系统都需要复杂事务，但必须说明恢复粒度。验收应比较“连续N步”和“K步后恢复再N−K步”的参数、下一批样本和学习率，而不是只检查load不报错。</p>',
    'restart-state',['A14'],['TORCH-SAVE','LOCAL'])
add('chapters/04.html','一份文档的完整生命周期','用六条记录走完去重、分组与评测隔离',
    '<p>以下是独立数据工程例，不改变贯通模型的两句话。原始记录a1、a2来自同一来源A且正文完全相同；b1、b2来自B且互为副本；c1来自C，d1来自D。先为来源、版本和权利范围建立元数据，再按重复关系形成不可跨集合的组。</p>'+ 
    table(['阶段','记录/数量','此步留下的证据'],[['原始','a1,a2,b1,b2,c1,d1：6条','来源与内容指纹，不丢原始ID'],['精确去重','a1,b1,c1,d1：4条','a2→a1、b2→b1的去重映射'],['按来源组分配','训练A/B，验证C，测试D：2/1/1','集合分配清单与数据版本'],['再分块或分词','每个来源的所有块跟随所属集合','源ID→块ID→Token范围'],['训练与调参','只用训练更新，验证选择方案','配置、有效Token数、失败样本'],['最终检验','冻结方案后检查D','独立结果，不回填训练或继续调参']])+ 
    '<p>这是固定教学分配，不是建议真实数据只用四篇文档。跨来源转载、近重复、同题改写和同仓库高度相近任务也可能泄漏，需要在划分前识别为组；不能只按文件名判断。规范化要与数据类型匹配：中文空白清理可能合理，Python缩进和代码中的空格却可能有语义。每次过滤都记录“6→4”的数量及原因，否则性能变化可能只是测试分布被换了。</p><p>数据可用性还有许可、隐私与撤回边界。去重不是获得授权；删除原始文档也不自动删除已生成的块、缓存、训练检查点及参数影响。不同派生物需分别列出保留与撤销策略，不把数据清单上的删除当作模型已遗忘。</p>',
    'data-lifecycle-example',['A13','A17'],['CS336','DIVE1','LOCAL'])

add('foundations/17.html','监督微调仍是条件预测训练','学教师的文本，与拿结果奖励训练，是两条不同链',
    '<p>Dive into LLMs的数学例先取教师生成的解题文本，再用它作SFT目标。此时梯度仍来自“目标Token的负对数概率”，不是自动变成强化学习；教师来自推理模型，也不改变学生此步的监督目标。教师输出需要验证，较长的解释不天然比短答案更正确。</p><p>独立例：教师对“2＋3”输出“5”。SFT提高这串已给定答案的概率；结果奖励训练则先让学生产生候选，再用独立规则判断5是否正确，用相应优化算法改变候选分布。前者可能继承教师错误，后者可能利用验证器漏洞。两条链都要保存数据来源、训练与评测划分，不能把测试答案回收成训练示范后仍称独立测试。</p><p>实际SFT还需核对哪些位置计loss。所读数学笔记将整条input_ids复制到labels；这本身不能证明只对助手回答训练。指定版本TRL提供的助手掩码功能还依赖模板支持，最终应打印一条样本的Token、角色、labels和有效计分数，而不是只看一个布尔开关。</p>',
    'teacher-vs-reward',['A15','A16'],['DIVE4','SFT','LOSS'])
# Replace one redundant immediate DPO derivation with a useful continuation, keeping its anchor.
replace_h_section('foundations/17.html','DPO的式子先用两份答案解释',
    '<p>上式中的<code>log π(y|x)</code>不是每个Token概率的平均，也不是模型给自己的评分。若完整回答含两个Token，条件概率分别0.5和0.6，则答案概率是0.3，对数概率是<code>ln0.5＋ln0.6＝ln0.3</code>。后一个Token的概率必须以提示和前一个Token为条件，不能从两个独立请求里随便取数相乘。</p><p>标准DPO在所声明目标上比较整段回答的对数概率和；把它偷偷换成按长度平均，会改变目标，不能还称相同公式。回复结束标记、截断、只计算回答而非Prompt的mask，都应在优选与较差两边使用一致规则。下面另一个独立概率表仅检验“相对参考策略”的含义，不续接贯通模型。</p>',
    ['A15','A32'],'把DPO的整段概率还原为Token对数概率')
add('chapters/05.html','PPO、GRPO','PPO里的旧策略与参考模型不是同一角色',
    '<p>为使符号不混用，令πθ为正在更新的策略，πold为生成这批样本时的策略快照，πref为提供偏离约束的参考模型。某些初始化时它们权重相同，但经过更新后职责和生命周期不同。</p>'+ 
    table(['对象','本轮提供什么','容易混淆的地方'],[['πold','固定所采样动作的旧对数概率','PPO概率比的分母不是任意参考模型'],['πθ','可求导的新动作对数概率','这一项通过优化改变'],['πref','计算约束项所用的参考分布','不应每做一次更新就不加说明地重置'],['奖励/优势','候选好坏与相对基线的评价','奖励分高不等于事实真，也不等于概率']])+ 
    '<p>单步独立数例：πold(a|s)=0.1，πθ(a|s)=0.2，概率比r=2；优势A=1，裁剪范围[0.8,1.2]，PPO代理项<code>min(rA,clip(r)A)=1.2</code>。若A=−1，则两项为−2和−1.2，取较小的−2。不要把clip写成“所有情况下把梯度限制在±20%”；这是代理目标的裁剪结构，完整训练还有价值/熵/KL等具体配方。</p><p>若按组内奖励中心化构造GRPO类优势，一组奖励全为[1,1,1,1]，中心化优势全为0；该奖励项无法区分谁更好。仍可能存在KL或其他项，因此不能说整次更新一定为0。需要核对实际实现是否白化、如何处理零方差及长度权重，不把一个示意公式当所有GRPO实现。</p>',
    'policy-roles',['A15'],['PPO','DIVE11','GRPO'])
add('chapters/05.html','蒸馏：不仅复制最终答案','复现数学SFT前，先检查选择偏差、标签与版本',
    '<p>所读Dive数学笔记有三个适合直接转成工程检查的问题：<code>final_answer.isdigit()</code>只保留部分数字形式；<code>labels=input_ids.copy()</code>不说明助手专用loss；标为vLLM版本的打印项实际取自<code>transformers.__version__</code>。这些是对应快照中的代码观察，不代表其思想无效，也不代表所有后续版本仍有相同写法。</p>'+ 
    table(['答案文本','isdigit结果','对实验样本的影响'],[['2','True','保留非负整数字符形式'],['−2（实际负号可为-）','False','负数可能被排除'],['0.5','False','小数被排除'],['1/2','False','分数被排除']])+ 
    '<p>应先决定研究总体：仅研究非负整数题，就明确写进结论；研究全部数学答案，则需要覆盖目标表达式的受限解析与等价判断。随包示例只支持带符号整数、有限小数和a/b，使用<code>Fraction</code>进行精确比较；不把模型输出传给<code>eval</code>。这个受限解析器不支持一般符号代数，拒绝的答案必须计入覆盖率而不是删除后重算准确率。</p><p>版本清单从各自包读取实际版本，再记录模型revision、tokenizer/template、数据版本、过滤前后数量和硬件。历史笔记中的40GB显存或训练耗时只适用于其配置，不能当所有1.5B训练的最低需求。本书没有运行该外部大模型训练；新增测试验证的是上述数据与接口边界。</p>',
    'math-sft-audit',['A16','A26'],['DIVE4','LOCAL'])

add('chapters/05.html','先诊断知识缺口与行为缺口','知识编辑、RAG和记忆：先确定要改变哪个对象',
    '<p>“把答案改正确”可能指四件不同的事：本轮补入证据、跨任务保存一条事实、训练一般回答习惯，或直接编辑模型参数。它们不是同一种记忆系统。选择干预前，先问事实是否时变、是否要求来源与撤回、能否做广泛回归。</p>'+ 
    table(['机制','实际改变','可追溯/撤回方式','不能保证'],[['RAG/上下文','本轮输入及索引','版本化源文档与候选、缓存失效','检索到了就一定回答正确'],['外部长期记忆','独立存储的事实或经验','来源、时间、范围、删除派生项','删除记录就擦除了模型参数知识'],['SFT/适配器','大量任务上的参数行为','数据版本、适配器回滚、回归集','精确更新一条事实而其他行为完全不动'],['知识编辑','针对目标关联的参数或附加机制','保存修改、测目标及邻近行为','单条回答变化就是安全完整的全局知识更新']])+ 
    '<p>知识编辑的局部测试至少拆开：目标提问是否更新、改写问法能否泛化、无关事实是否保持、相关多跳问题能否正确迁移。不要把某历史例子的“某方法最好”升级为所有模型和编辑批量的普遍结论。对频繁更新且必须引用的企业制度，先比较可追踪的外部检索，而不是默认改权重。</p>',
    'knowledge-update-choice',['A17'],['DIVE3','EDIT'])
add('chapters/18.html','追问：长期记忆和模型参数知识是什么关系？' if any('追问：长期记忆和模型参数知识是什么关系？'==h.get_text(' ',strip=True) for h in get('chapters/18.html').select('h3')) else 'Q069',
    '先确认“删除记忆”删除的是哪一层',
    '<p>本章的记忆是模型外部可存取的记录。删除一条记录后，还需使它派生的摘要、索引块、检索缓存和使用者副本失效；这些都不等于对基座参数进行机器遗忘。反过来，用知识编辑改变一个模型回答，也不会替你修改外部事实库的旧记录。模型机制Q024讨论参数层，当前先把来源ID和派生关系作为跨任务记忆的边界，避免用同一个“记住/忘记”词掩盖不同对象。</p>',
    'memory-vs-weights',['A17'],['DIVE3'])

add('foundations/18.html','固定模型并核对请求条件','eval和不记录梯度，分别关闭什么',
    '<p><code>model.eval()</code>切换具有训练/评估差异的模块行为，例如Dropout；<code>no_grad()</code>或<code>inference_mode()</code>控制自动求导记录。前者不自动停止求导，后者不自动关闭Dropout。训练好的参数不更新，也不意味着随机层已关闭。</p><p>本书微型模型没有Dropout，两个模式在这条路径上容易看起来一样；换成真实模型后不能据此省略设置。还有函数式算子的独立参数：例如所引PyTorch SDPA按传入的<code>dropout_p</code>决定是否施加Dropout，不会仅因外部模块eval就自动改成0。验证时同时检查模式、函数参数、权重身份、Token和位置；仅固定随机种子不够。</p>',
    'eval-autograd',['A19'],['AUTOGRAD','SDPA'])

add('chapters/08.html','写出一条请求的时间账','先固定计时边界，再把首Token和后续间隔相加',
    '<p>以下以<strong>客户端提交请求到收到各Token</strong>为统一边界。设t₀为提交时刻，t₁…tM为M个实际输出Token的接收时刻。TTFT=t₁−t₀；相邻Token间隔ITLᵢ=tᵢ−tᵢ₋₁；当M&gt;1时，平均ITL=(tM−t₁)/(M−1)。因此到最后一个Token的时间恒等于<code>TTFT＋(M−1)×平均ITL</code>。若M=1，间隔均值无定义，不能填0伪装“极快”。</p>'+ 
    table(['时间点/阶段','本独立例数值','不能混算的边界'],[['请求提交','0ms','起点由客户端或服务端定义，二者不可拼接'],['排队','0—40ms','不是模型前向'],['Prefill前向','40—100ms','已经计算首Token所需的最后位置表示'],['首项采样、编码与发送','100—120ms','本例单列20ms，不再算一遍完整Decode'],['后续Token接收','140、160、180ms','3个20ms间隔，输出总数M=4'],['结果','TTFT120ms；平均ITL20ms；总180ms','不是120＋4×20＝200ms']])+ 
    '<p>库中的TPOT可能按不同边界统计，应读取指标定义；上述公式约束的是本例定义下的平均间隔，不是p95，也不表示每一步恒定20ms。请求最终结束、流式最后一个Token到达和Agent完成验收还可以是三个时刻。测整项任务时应继续计入后处理、工具往返和验证，而不能把首字更快直接称为任务更快。</p>',
    'ttft-contract',['A18'],['CS2680-A4','LOCAL'])
replace_paragraph('chapters/08.html','在单次生成中，可粗略写',
    '<p>在单次生成中，先按实际输出数M拆成首Token等待与其后M−1个间隔，不把首Token再次算成一次完整Decode。实际间隔随上下文长度、batch、抢占和传输变化。下面的时间账明确规定测量边界；流式传输可以改善感知等待，但不会自动减少总计算。</p>',['A18'])
# Clarify the older numerical example without changing its measured values.
for p in get('chapters/08.html').select('article p,article td'):
    text=p.get_text(' ',strip=True)
    if '首Token计算20' in text:
        p.string=text.replace('首Token计算20','首项输出处理与发送20（本例不另算完整Decode）')

add('chapters/07.html','追问：Prompt Cache与KV Cache什么关系？','前缀复用只复用满足身份约束的那一部分',
    '<p>单请求KV缓存是逐轮继续同一序列；跨请求的前缀缓存则试图复用另一个请求已经算过的相同前缀。两者都依赖模型计算身份，而不是“文字看起来差不多”。权重或adapter、分词/模板、位置方式、前缀Token和实现支持的缓存形式，都可能改变可复用性。</p><p>假设两个请求的前三个Token完全相同而第四个不同，缓存也只能在实现允许的块边界内复用相同部分；不能将第一个请求不同后缀的K/V一并带入。vLLM所引版本的APC用于避免重复的前缀Prefill，并不会免除新输出Token自身的生成计算。统计收益时分别记录冷启动、已预热匹配前缀和不匹配前缀；把预热成本藏起来，会让结论失真。</p><p>共享缓存也有数据隔离条件。服务的命中策略、用户/租户边界及内容策略要一并说明；不要仅用“hash相同”就承诺跨用户复用安全。缓存实现正确性用logits对照验证，性能用真实时钟/吞吐验证，是两份不同证据。</p>',
    'prefix-cache-boundary',['A19'],['VLLM-APC'])

add('chapters/25.html','正确的成本分母','吞吐、满足服务目标的吞吐与每成功任务成本分开算',
    '<p>原始吞吐可以统计每秒完成请求数或输出Token数；<strong>goodput</strong>在此定义为每秒完成且同时满足质量与延迟目标的任务数。快但错误的结果不进入goodput，失败请求花掉的费用却仍进入总成本。</p>'+ 
    table(['同一20秒观察窗','方案A','方案B'],[['总费用（含失败）','2.00','1.50'],['尝试任务数','4','4'],['独立验收成功数','2','1'],['成功且满足延迟目标数','1','1'],['每成功任务费用','2/2＝1.00','1.5/1＝1.50'],['主机墙钟/成功任务','20/2＝10秒','20/1＝20秒'],['goodput','1/20＝0.05任务/秒','1/20＝0.05任务/秒']])+ 
    '<p>这是口径演示，不是实际模型A/B实验。B总账单更低，却不等于更经济；没有成功任务时，单位成功成本应标为未定义或不可达，不写成0。并发请求的耗时求和也不是观察窗的墙钟长度。选择阈值前固定任务集、质量验收和服务目标，之后不能为有利结果临时改分母。</p>',
    'goodput-cost',['A18','A22'],['CS2680-A3','CS2680-A4','LOCAL'])

add('foundations/01.html','先确定训练与推理的共同部分','先认任务头：分类模型不等于续写模型',
    '<p>“都叫预训练模型”不意味着可以用同一套输入、标签和输出解释。这里先分清三类常见任务形态；之后主线只推导因果Decoder，避免把分类教程中的约定带进来。</p>'+ 
    table(['形态','输出要解决什么','训练时的关键不同'],[['编码器＋分类头','把一段文本判成类别，如正面/负面','通常使用可双向读输入的表示，再预测类别标签'],['因果Decoder＋词表头','根据前缀预测下一个Token','不能偷看未来目标，标签与位置要错开'],['编码器—解码器','读取源序列，生成另一条目标序列','源编码、目标因果解码与交叉注意力要分别定义']])+ 
    '<p>Dive into LLMs开头的BERT分类例很适合学习数据→训练→部署，但其类别标签不是本书的下一Token标签。能部署一个分类Demo也不等于已实现多轮聊天、工具协议或生产隔离。使用例子时先说明任务与输出头，再比较训练和推理中共用的前向计算。</p>',
    'task-heads',['A26'],['DIVE1','CS336'])
add('chapters/13.html','Q049','提示、示例与训练：先用最小输入定位问题',
    '<p>在黑盒阶段，先区分改变的是<strong>本轮输入</strong>还是<strong>模型参数</strong>。写清目标、允许的证据、输出字段和失败条件是在改输入。给两个同任务示例也是改输入，并不执行梯度更新。只有进入后面的训练流程，参数才会按损失被更新。</p><p>独立例：需要模型返回资料的<code>title/source_id</code>。先使用明确字段与一条可验证材料，检查缺失字段或无依据内容；若模型仍误解格式，再提供一致的少量示范。示范不得与当前规则冲突，也不得包含评测目标的答案。比较“无示例→两例→更多例”时固定任务和评分，否则上下文变长不能说明质量提高。</p><p>经典CoT、程序辅助和多路径采样可以作为实验策略，但不能变成“所有模型必须输出长篇思考”。官方推理模型指南明确提醒某些推理模型不需要显式逐步思考提示；应该要求可检查的结论、简要依据或可执行验证，不把可见解释当隐藏内部过程的完整记录。额外采样带来成本，多数答案相同也可能只是同一个错误被重复。</p>',
    'prompt-minimum',['A20'],['DIVE2','PROMPT'])
add('chapters/09.html','如何判断某次失败是模型问题还是Harness问题？','先核对工具操作的是哪一个工作区',
    '<p>一个真实系统可能同时有界面进程、Agent运行进程、任务容器和模型服务。<code>read_file("src/a.py")</code>中的路径必须相对于明确的环境解释；Agent进程所在目录不一定就是待修复仓库。</p><p>CS2680公开作业给出了一个具体隔离情形：目标仓库在任务容器中，Agent通过任务工具接口读写/执行。直接在Agent一侧打开同名路径，可能读到错误环境甚至空目录。本教材离线索引助手把环境缩小为受限临时目录，不冒充该课程的容器实现。</p>'+ 
    table(['本轮记录','为什么需要','最小反例'],[['environment_id＋cwd','确定真实目标环境','同一相对路径在两个容器内容不同'],['文件指纹或工作树版本','确定读写验证的是哪一份内容','测试在旧文件上通过'],['工具请求/结果call_id','关联动作与观察','将另一次读取结果回填'],['验收执行位置','确保验证约束同一个产物','本地小测试绿了，目标容器未改动']])+ 
    '<p>排错时先读取一个可预期的哨兵文件或仓库版本，并在结果中核对环境身份；不要立即换更强模型。边界清楚的工具比让模型猜“我在哪里”更可靠。</p>',
    'workspace-location',['A21'],['CS2680-A3','LOCAL'])
add('chapters/19.html','Q073','加载证据、实际行为与执行许可分别验收',
    '<p>一个Skill成功出现在本轮输入，只能证明“内容已提供”，不能证明模型每项都正确使用，更不能证明文件或网络操作已获授权。复盘至少区分：发现了哪个版本、路由为什么选它、载入哪些正文、工具是否可用、行动是否符合流程、最终产物是否过关。</p><p>局部例：Skill要求先读规则再改配置。日志有“已加载Skill”但模型直接写文件，说明加载链成功而执行行为未满足；执行器拒绝越界路径，则说明权限防线起作用，不是Skill文件损坏。应根据偏离层修复描述、上下文或执行约束，不能把每种失败都转化成再增加一大段Prompt。</p><p>本节引用的产品源码保持其原固定快照。运行你自己的CLI时，还要记实际版本、启用功能和配置；不同产品的技能、钩子和子Agent继承机制不能仅凭同名术语互相推断。</p>',
    'skill-evidence',['A29'],['LOCAL'])
add('chapters/23.html','Q091','调参集、验证集与最终评测集不能反复换名字',
    '<p>设有30个任务：开发用10个、选择方案用10个、最终验收用10个。反复查看某任务失败并据此改Prompt后，它已经参与开发；不能仍把该任务表现当作完全未见的测试证据。若任务来自同一问题模板、同一仓库变体或同一文档，应按这种相关组划分，避免只换名字制造“独立样本”。</p><p>一次对照应保存相同任务ID的旧、新结果，含失败和超时，并另列基础设施故障。若升级模型、改检索和提高预算同时发生，改善可以是真实的，但无法把因果贡献全归给某一个模块。做消融时一次只撤回一个主要改变；随机系统需要重复trial，但汇总时仍以任务或预定相关组为采样单位。</p><p>来源课程中的固定评分环境用于限制比较条件；本教材不拥有其隐藏测试，也不照搬其学生账户限制。自行实验应公开可复现任务、保留内部未参与调参的验收集，明确哪些结果只是脚本夹具、哪些是真实模型运行。</p>',
    'heldout-split',['A13','A22'],['CS2680-A3','CS336','EVAL'])
add('chapters/24.html','Q093','会识别风险，不代表危险动作已经被阻止',
    '<p>R-Judge这类记录判读任务检查模型能否从交互记录中识别风险；运行时安全还要求在动作发生前限制权限、在结果不明时核验状态。两类能力相关，但测量对象不同。把危险动作执行完，再回答“unsafe”，并不是成功阻断。</p>'+ 
    table(['本地无害测试','检测对象','通过后仍不能推出'],[['模拟文件含“请忽略规则”字样','外部数据是否被误升格成指令','模型不会在其他措辞下受影响'],['模拟写入只允许临时目录','执行器是否拒绝越界路径','所有网络/远程工具都已隔离'],['操作成功而确认丢失','结果未知能否被正确保留','外部系统支持完整原子回滚'],['仅回放历史记录判safe/unsafe','风险识别与解释质量','真实动作已被停止或撤销']])+ 
    '<p>安全例子应在有授权的受限环境使用虚构数据、空操作或临时文件，记录误拦和漏拦。不能照搬外部教程中涉及真实凭据、破坏性命令的样例作为默认练习。执行边界越清楚，越能用确定性测试定位，而不是只依赖模型表达“我会小心”。</p>',
    'recognition-enforcement',['A23'],['DIVE6','DIVE10'])
add('chapters/27.html','Q107','视觉输入、动作定位与执行反馈是三份不同数据',
    '<p>多模态系统可以让语言模型调用外部视觉工具，也可以把视觉编码后的表示直接作为模型输入；这两种接法不能混成“模型天生看到了所有像素”。进入模型的内容还可能经过缩放、裁剪、切块和位置编码，具体要由对应模型与服务协议确定。</p><p>独立坐标例：原截图宽1200、高800，等比例缩为600×400且无裁剪。缩图坐标(150,100)映射回原图是(300,200)。若还存在裁剪偏移、设备像素比或滚动，需要再应用对应变换；不能只乘2。动作发出前还要确认截图与当前页面状态一致，发出后重新观察业务结果。</p><p>Dive的GUI例让模型同时输出动作和1—5分。这样的自评分不是已校准概率；材料中“score=5”与成功字段仍可能不同。应收集同任务分布下的动作结果，例如给5分的20次操作只成功12次，则这一组经验成功率是60%，不能直接把5/5解释为100%。在覆盖率与风险之间选人工接管阈值，还需单独的验证数据。</p>',
    'multimodal-feedback',['A24'],['DIVE8','DIVE9','LOCAL'])
add('chapters/27.html','Q105','来源水印与事实正确率也不能混为一种置信度',
    '<p>文本水印研究通常检测某种生成统计特征；内容来源声明或签名则说明某个主体对某份数据作了声明。二者都不能直接证明文本中的每个事实为真，也不能因为没有检测到水印就断言文本一定由人写。</p><p>用一个独立基率例说明：10,000段文本中，真实带目标水印的占1%，共100段。假定检测灵敏度90%、无水印上的误报率1%，预期命中90段、误报99段。于是阳性结果里真正带水印的比例约<code>90/(90＋99)=47.6%</code>。这不是任何实际检测器成绩，而是说明“误报率低”仍须结合先验比例解读。</p><p>短文本、重复内容、改写与分布变化都应作为检测边界考察；不要将某历史实验的AUC或z-score阈值推广到所有模型、语言和文本长度。水印、隐写、授权和安全隔离分别解决不同问题，本课程仅在来源可信度这里说明区别，不把它们扩展成独立的隐写操作教程。</p>',
    'provenance-truth',['A25'],['DIVE5','DIVE7','LOCAL'])
add('chapters/28.html','如何阅读一篇新论文而不被结论牵着走','参考资料的年龄，应该怎样进入你的判断',
    '<p>旧资料可以解释仍然成立的机制，新资料也可能只有狭窄实验条件。先把主张拆成三类：数学或接口不变量、某版本实现、特定实验结果。第一类可重新推导，第二类要锁版本，第三类必须保留模型、数据、硬件和评分条件；不能只给整篇文章贴“新/旧”标签。</p>'+ 
    table(['例子','本课程吸收什么','不直接沿用什么'],[['CS2680公开作业','同一任务系统逐步接管与受控比较','课程私有资源、隐藏评测或账号要求'],['Dive微调/部署','数据到训练到部署的完整对象链','旧安装命令、历史模型名和硬件下限'],['Dive数学SFT','教师示范、标签、生成与评测衔接','版本打印错误、未经说明的数字答案过滤'],['知识编辑/水印研究','目标、非目标与失败条件的独立验证','某个方法“最好”或某组AUC作为普遍保证'],['官方框架文档','明确版本的输入输出与状态约定','把不同版本默认行为拼成同一实现']])+ 
    '<p>结论应能写成：“在这些任务、版本与资源下，改变X后指标Y如何变化；反例Z仍然存在。”没有足够证据时，保留待核验项，而不是为完整性补造结果。书内历史Codex源码与Claude文章继续保留其取得范围，本轮没有重新逐行审查它们的所有新版本。</p>',
    'source-aging',['A26','A29'],['CS2680-A4','CS336','DIVE-ROOT'])

# A single minimal handoff contract is reused by the five existing assignments.
assignments={
  1:('accept','观察结果交给下一作业之前，先固定这些身份',
     '保存任务ID、初始文件指纹、工具事件call_id、最终文件指纹与独立验收。模型自述不作成功标签；缺失轨迹不能补写成好看的过程。'),
  2:('baseline','循环的输出要能与观察基线直接比较',
     '沿用作业1的任务语义与验收规则，记录宿主版本、工具schema版本、失败/未知状态。加入真实模型适配器时，另标运行方式，不把脚本决策轨迹和LLM能力结果混为一组。'),
  3:('measure','黑盒对照必须保留未成功的尝试',
     '固定任务ID、模型快照、提示与工具版本、预算和评分器；记录输入/输出用量、等待和重试。脚本夹具的请求字节减少，不能直接换算为真实Token费用或模型成功率改善。'),
  4:('metrics','从黑盒换成自建服务，先验接口再谈加速',
     '首先核对模板、停止原因、工具调用结构和错误响应，再使用相同任务测质量及端到端耗时。CPU微型模型只是数值与协议验证；真实GPU引擎未运行的字段写NOT_RUN，不填估算值。'),
  5:('artifacts','最终报告只需要一条可被反例推翻的主张',
     '选一个具体瓶颈，固定基线与验收，先预测结果，再做一个主要干预和消融。把失败改动、预算耗尽、无法复现的差异一并保留；结论强度不能超过实测范围。')}
for n,(after,title,text) in assignments.items():
 page=f'labs/projects/assignment{n}.html'
 body='<p>'+text+'</p>'+table(['最小交接字段','含义'],[['task_set_revision','任务集合与拆分，不只任务数量'],['artifact_before / artifact_after','待处理与交付工件的版本'],['system_revision','代码、模型、模板、工具/检索设置'],['run_mode','script_fixture / local_numeric / live_model'],['budget / seed / environment','可控条件；不支持或未测写明'],['outcome / evidence','成功、失败、未知、未运行与对应原始记录']])
 body+='<p>这些字段用于对照，不要求为小练习搭建数据库或复杂平台。一份JSON和已有日志足够；没有改变的输入用同一版本，新增资料不要悄悄覆盖旧结果。</p>'
 add(page,after,title,body,f'assignment-{n}-handoff',['A27'],['CS2680-A3','CS2680-A4','LOCAL'])

# Correct stale forward references and misleading unqualified names in place.
text_replacements={
 '具体协议在F22以后展开':'具体协议可回看已经学习的F22—F25',
 'F14会先解释':'F10已经解释',
 'F14会解释':'F10已经解释',
}
for page in [f'foundations/{n:02}.html' for n in range(1,41)]+[f'chapters/{n:02}.html' for n in range(1,29)]:
 s=get(page)
 for node in list(s.select_one('article.article').find_all(string=True)):
  if node.parent.name in ['script','style']:continue
  old=str(node);new=old
  for a,b in text_replacements.items():new=new.replace(a,b)
  if new!=old:node.replace_with(new);record(page,'repair-sequence-reference','text',['A08'],old)
# A generic X is valid, but this particular answer must agree with N1 in the main example.
s=get('foundations/11.html')
for node in list(s.find_all(string=True)):
 if 'X乘Wq' in str(node):
  node.replace_with(str(node).replace('X乘Wq','本例的归一化输入N1乘Wq（泛写XWq时，X指投影入口）'))
  record('foundations/11.html','clarify-symbol','quiz',['A08'])

# Keep detailed independent experiments, but label their parameters before changing context.
for page,qid,blurb in [
 ('chapters/04.html','Q017','本章有两种验证层次：贯通主线使用236参数、两句训练数据；下方“16符号循环序列”是另一份18,320参数实验。两者的模型、loss与训练步数不能接成同一次运行。'),
 ('chapters/06.html','Q015','语言停止、响应结束与业务验收属于不同层次。下方七词表模型只是独立结构对照，不改变F18加载的八词表模型与其EOS编号。')]:
 h=findh(page,qid)
 insert_after(h,f'<p class="notice">{blurb}</p>');record(page,'label-experiment-scope',qid,['A08','A30'])

# Extract and reinsert a header's sibling run; existing IDs are remapped globally later.
def move_run(source,anchor,dest,target,reason):
    h=findh(source,anchor);level=int(h.name[1]);nodes=[h]
    for node in list(h.next_siblings):
        if isinstance(node,Tag) and re.fullmatch('h[1-6]',node.name) and int(node.name[1])<=level:break
        nodes.append(node)
    ids=[]
    for node in nodes:
        if isinstance(node,Tag):
            if node.get('id'):ids.append(node['id'])
            ids.extend(x['id'] for x in node.find_all(id=True))
    target_tag=findh(dest,target);last=end_of_section(target_tag)
    for node in nodes:
        node.extract();last.insert_after(node);last=node
    for ident in ids:moved[source+'#'+ident]=dest+'#'+ident
    record(dest,'move-with-anchors',anchor,['A31','A33'],reason+'；原位置 '+source)

# The full forward overview belongs with the full forward question, not just Q/K/V.
move_run('chapters/02.html','core-forward-trace-3--mc-section-3','chapters/02.html','把每个张量的身份固定下来','完整前向的数值总表紧随对象总表')
# Case A's projection should precede its mask and value mix.
move_run('chapters/02.html','integrated-bdc26289bfd4--walka-s3','chapters/02.html','integrated-04f63f2d4104--walka-s2','将A.3放回A.2与A.4之间')
# Independent generation/cache details are postponed until training has been learned.
prev='Q013'
for aid in ['integrated-b23ba8ef3872--walka-s7','integrated-71d97056a70b--walka-s8','integrated-b9baf105ff7e--walka-s9']:
    move_run('chapters/02.html',aid,'chapters/06.html',prev,'前向章不提前展开完整生成/缓存循环');prev=aid
move_run('chapters/02.html','integrated-49b10a554c24--walka-s11','chapters/07.html','Q025','缓存一致性检验归入缓存机制')
move_run('chapters/02.html','integrated-14bafdfec86b--walka-s12','chapters/08.html','Q032','迁到真实服务的边界归入服务与并行')
# Add precise scope at both halves of this independent case.
insert_after(findh('chapters/02.html','integrated-4ccb580343a6--walka-s1'),'<p class="notice">以下连续案例A是另一份固定权重的两层Decoder：词表8、宽度4、LayerNorm、固定正弦位置项，ID没有真实中文对应；不是236参数RMSNorm贯通模型。这里只保留输入与前向部分，生成续篇安排在训练之后的机制Q013。</p>')
h=findh('chapters/06.html','integrated-b23ba8ef3872--walka-s7')
insert_after(h,'<p class="notice">本组延续机制Q005中的独立两层Decoder（8词表、宽度4、LayerNorm和固定正弦位置项，输入[1,2,3]），不承接F18的“我爱”训练模型。参数和输出记录不同，ID6在本例是普通候选，不沿用另一模型的BOS含义。</p>')
# The two concrete backward steps now occur after loss/gradient foundations.
for title in ['反向时这里为什么出现两条贡献','用实际输出头U[0,3]计算十个位置的贡献']:
 h=findh('chapters/04.html',title)
 if h.find_parent('section',class_='mechanism-question').get('data-question')=='Q017':
  move_run('chapters/04.html',h['id'],'chapters/04.html','从输出投影一直走回Embedding','将输出头梯度示例移到参数更新问题')

# Write all edited pages; leave generated complete/search/markdown for the rebuild step.
for page,s in cache.items():
    (ROOT/page).write_text(str(s),encoding='utf-8')
(WORK/'audit/content-edits.json').write_text(json.dumps(edits,ensure_ascii=False,indent=2))
(WORK/'audit/moved-anchors.json').write_text(json.dumps(moved,ensure_ascii=False,indent=2))
print('edited pages',len(cache),'operations',len(edits),'moved anchors',len(moved))
