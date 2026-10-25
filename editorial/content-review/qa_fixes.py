from pathlib import Path
from bs4 import BeautifulSoup
import json,html
W=Path('/mnt/data/_content_audit_20261024'); R=W/'build/AI_Systems_Engineering_Textbook_ZH'
D=json.loads((R/'labs/model/data/run.json').read_text())
def load(p):return BeautifulSoup((R/p).read_text(),'lxml')
def save(p,s):(R/p).write_text(str(s),encoding='utf-8')
def insert_after(s,anchor,frag):
 t=s.find(id=anchor);assert t,anchor
 t.insert_after(BeautifulSoup(frag,'html.parser'))
def vec(v):return '['+', '.join(f'{x:.6f}' for x in v)+']'
# Explicit per-position K/V values are necessary to reproduce the next attention step.
p='foundations/11.html';s=load(p)
h=s.find(id='core-qkv-5--mc-section-5')
if h is None:
 h=next(x for x in s.find_all(['h2','h3']) if x.get_text(strip=True)=='一行与整张表的区别')
rows=[]
for t,token in enumerate(['BOS','我','爱','学习','！']):
 rows.append('<tr><td>'+str(t)+' · '+token+'</td>'+''.join('<td><code>'+vec(D['initial_trace'][k][0][t])+'</code></td>' for k in ['q','k','v'])+'</tr>')
frag='''<p>把第0条样本的五个位置一起列出，就能看出矩阵Q/K/V不是只有“爱”这一行。每行都使用各自的N1，但共享同一张Wq、Wk或Wv；下面只取b=0，不能把b=1的行混入这次读取。</p><div class="table-wrap"><table><thead><tr><th>位置与片段</th><th>Q：该位置的提问表示</th><th>K：该位置的匹配表示</th><th>V：该位置提供的内容</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><p>例如当前t=2的“爱”用第三行Q，依次与第0、1、2行K打分，再混合第0、1、2行V。第3、4行虽然在训练的同一次批量前向中也被算出了，却被因果掩码禁止参与这一行；“已经算出”不等于“当前位置允许读取”。数值显示到小数后6位，后续计算使用原始完整精度。</p>'''
# place after the existing paragraph and before the adjacent evidence note
last=h
for n in h.next_siblings:
 if getattr(n,'name',None) in ['h2','h3']:break
 if getattr(n,'name',None) and 'core-evidence' not in n.get('class',[]):last=n
last.insert_after(BeautifulSoup(frag,'html.parser'));save(p,s)
# Correct ambiguous wording in the original timing example, not only in a later explanation.
p='chapters/08.html';s=load(p)
for t in s.select('article p,article td'):
 if '随后第1个Token还需20ms' in t.get_text():
  for n in list(t.find_all(string=True)):
   if '随后第1个Token还需20ms' in n:
    n.replace_with(str(n).replace('随后第1个Token还需20ms','随后首项采样、编码和发送合计20ms（不是额外一次完整Decode）'))
save(p,s)
# A28: explicit scope at first relevant examples. Don't expand already complete explanations.
notes={
'foundations/02.html':('core-tensor-notation-2--mc-section-2','<p>后续引用资料有时用N表示Token总数、用V表示词表大小；本书贯通模型固定用T表示单条安排的位置数、Vocab表示词表大小，V留给Value矩阵。引用公式保留原作者写法时，会在同一小节重新定义，不把相同字母自动当作相同对象。</p>'),
'foundations/06.html':('foundations-06-s3','<p>以下字节计算针对一份<strong>连续、未压缩、没有共享重叠的密集数据本体</strong>。它不是GPU已预留显存、峰值显存或训练全状态。物理分配还可能含对齐、工作区和空闲缓存；共享视图则不能把每个逻辑张量的字节数全部相加当成独立存储。</p>'),
'foundations/08.html':('foundations-08-s5','<p>独立地址例：连续2×3矩阵在存储中为[1,2,3,4,5,6]，以“元素”为单位的步长是(3,1)。转置视图形状变为3×2、步长变为(1,3)，元素仍可共用原来的6格；视图[1,0]读到原矩阵[0,1]=2。逻辑位置改变不代表复制了6个数，随后强制连续化才可能产生新副本。具体是否共享，要用框架接口检查，不能只从shape判断。</p>'),
'foundations/20.html':('foundations-20-s2','<p>这里比较的是<strong>可训练参数数</strong>，而不是总参数或每次前向的运算数。独立8×8、r=2例中，基础W仍有64个固定参数，A和B合计32个可训练参数，未合并时总计96个参数。合并增量后可以按64个参数的W′做前向，但合并需要兼容精度与实现；训练阶段仍不能据32这个数直接断言显存或延迟减半。</p>')}
for p,(anchor,frag) in notes.items():
 s=load(p);insert_after(s,anchor,frag);save(p,s)
# Extend executed numeric regression, not just textual claims.
p=R/'labs/test_content_contracts.py';text=p.read_text()
extra='''\nclass ScopeAndStorage(unittest.TestCase):
    def test_all_five_qkv_rows(self):
        p=RUN['initial_parameters']; t=RUN['initial_trace']
        for pos in range(5):
            for k,w in [('q','Wq'),('k','Wk'),('v','Wv')]:
                got=[sum(a*b for a,b in zip(t['n1'][0][pos],col)) for col in zip(*p[w])]
                self.assertLess(max(abs(a-b) for a,b in zip(got,t[k][0][pos])),1e-12)
    def test_dense_storage_bytes(self): self.assertEqual(2*128*4096*2,2*1024**2)
    def test_transpose_address(self):
        storage=[1,2,3,4,5,6]
        self.assertEqual(storage[1*1+0*3],2)
        self.assertEqual([[storage[i+j*3] for j in range(2)] for i in range(3)],[[1,4],[2,5],[3,6]])
    def test_lora_trainable_vs_total(self):
        d,r=8,2; base=d*d; adapters=d*r+r*d
        self.assertEqual((base,adapters,base+adapters),(64,32,96))
'''
text=text.replace("if __name__=='__main__':unittest.main(verbosity=2)",extra+"\nif __name__=='__main__':unittest.main(verbosity=2)")
p.write_text(text)
# Copy an explicit record of follow-up fixes.
(R/'editorial/content-review/qa-fixes.json').write_text(json.dumps({'A03':'补齐b=0全部5个位置Q/K/V，不仅当前行','A18':'原计时例中同步改掉模糊的额外20ms','A28':'局部补明符号约定、逻辑与物理存储、LoRA训练与总参数，数值回归4项'},ensure_ascii=False,indent=2))
print('QA content fixes complete')
