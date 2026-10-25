"""Assertions for the new illustrations and canonical course. No vendor/API capability is tested."""
from pathlib import Path
import json,math,re,unittest
from html.parser import HTMLParser
R=Path(__file__).resolve().parent.parent
D=json.loads((R/'labs/model/data/run.json').read_text())
T=D['initial_trace'];P=D['initial_parameters']
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def matvec(x,W):return [sum(x[i]*W[i][j] for i in range(len(x))) for j in range(len(W[0]))]
def softmax(xs):
 ys=[math.exp(x-max(xs)) for x in xs];z=sum(ys);return [y/z for y in ys]
class FigureCalculations(unittest.TestCase):
 def test_query_projection(self):self.assertLess(max(abs(x-y) for x,y in zip(matvec(T['n1'][0][2],P['Wq']),T['q'][0][2])),1e-12)
 def test_key_projection(self):self.assertLess(max(abs(x-y) for x,y in zip(matvec(T['n1'][0][2],P['Wk']),T['k'][0][2])),1e-12)
 def test_value_projection(self):self.assertLess(max(abs(x-y) for x,y in zip(matvec(T['n1'][0][2],P['Wv']),T['v'][0][2])),1e-12)
 def test_attention_distribution(self):
  a=softmax([dot(T['q'][0][2],k)/2 for k in T['k'][0][:3]])
  self.assertLess(max(abs(x-y) for x,y in zip(a,T['A'][0][2][:3])),1e-12)
 def test_attention_mix(self):
  result=[sum(T['A'][0][2][j]*T['v'][0][j][f] for j in range(5)) for f in range(4)]
  self.assertLess(max(abs(x-y) for x,y in zip(result,T['mix'][0][2])),1e-12)
 def test_attention_future_zero(self):self.assertEqual(T['A'][0][2][3:],[0,0])
 def test_embedding_shared_row(self):self.assertEqual(P['E'][2],[-.3,.8,.1,.5])
 def test_training_shift(self):
  self.assertEqual(D['input'],[s[:-1] for s in D['sequences']]);self.assertEqual(D['target'],[s[1:] for s in D['sequences']])
 def test_training_denominator(self):self.assertEqual(sum(len(x) for x in D['target']),10)
 def test_cache_selected_not_processed(self):
  steps=D['generation']['steps'];self.assertEqual([s['cache_after'] for s in steps],[3,4,5])
  self.assertEqual([s['selected'] for s in steps],[3,5,7]);self.assertEqual(steps[1]['input'],[steps[0]['selected']])
 def test_cache_ends_before_eos_processing(self):
  last=D['generation']['steps'][-1];self.assertEqual(last['selected_text'],'EOS');self.assertNotIn(7,last['input'])
 def test_rectangular_mask(self):
  correct=[[j<=q for j in range(5)] for q in [3,4]];wrong=[[j<=q for j in range(5)] for q in [0,1]]
  self.assertEqual([sum(r) for r in correct],[4,5]);self.assertEqual([sum(r) for r in wrong],[1,2])
  average=lambda m:[sum((j+1) for j,v in enumerate(r) if v)/sum(r) for r in m]
  self.assertEqual(average(correct),[2.5,3]);self.assertEqual(average(wrong),[1,1.5])
 def test_residual_derivative(self):
  x,w=2.,.5;y=x+w*x;eps=1e-6;L=lambda xx:.5*(xx+w*xx)**2
  self.assertEqual(.5*y*y,4.5);self.assertAlmostEqual((L(x+eps)-L(x-eps))/(2*eps),y+y*w,places=7)
  self.assertEqual(y*x,6.)
 def test_parallel_path(self):
  self.assertEqual(40+max(20,60)+30,130);self.assertEqual(sum([40,20,60,30]),150);self.assertEqual(40+max(10,60)+30,130)
 def test_first_probability_lesson(self):self.assertEqual(1-.5**3,.875);self.assertEqual(.5**3,.125)
 def test_bm25_inserted_steps(self):
  idf=math.log(1+(100-10+.5)/(10+.5));self.assertAlmostEqual(idf,2.2637452596777816)
  self.assertAlmostEqual((2*2.2)/(2+1.2*(.25+.75))*idf,3.1126497321241318)
class CourseStructure(unittest.TestCase):
 def test_questions_have_single_home(self):
  counts={f'Q{i:03}':0 for i in range(1,113)}
  for p in (R/'chapters').glob('*.html'):
   for q in re.findall(r'data-question="(Q\d{3})"',p.read_text()):counts[q]+=1
  self.assertTrue(all(n==1 for n in counts.values()),counts)
 def test_backward_follows_prerequisites(self):
  a=(R/'chapters/03.html').read_text();b=(R/'chapters/04.html').read_text()
  self.assertNotIn('data-question="Q012"',a);self.assertIn('data-question="Q012"',b)
  self.assertLess(b.index('id="Q017"'),b.index('id="Q012"'))
 def test_retrieval_training_after_math(self):
  self.assertNotIn('id="worked-Q059"',(R/'chapters/15.html').read_text());self.assertIn('id="worked-Q059"',(R/'chapters/04.html').read_text())
 def test_no_parallel_learning_pages(self):
  c=json.loads((R/'editorial/canonical-pages.json').read_text());paths=[x['path'] for x in c]
  self.assertFalse(any(p.startswith(('visual/','visuals/','mechanisms/','studies/chapters/')) for p in paths))
 def test_ten_necessary_figures(self):self.assertEqual(len(json.loads((R/'editorial/necessary-figures.json').read_text())),10)
 def test_answers_open(self):
  class Parser(HTMLParser):
   def __init__(self):super().__init__();self.bad=[];self.answers=0
   def handle_starttag(self,t,attrs):
    a=dict(attrs)
    if t=='details' and 'quiz-answer' in a.get('class',''):
     self.answers+=1
     if 'open' not in a:self.bad.append(a)
  total=0
  for e in json.loads((R/'editorial/canonical-pages.json').read_text()):
   p=R/e['path'];s=Parser();s.feed(p.read_text());total+=s.answers
   self.assertFalse(s.bad,e['path'])
  self.assertGreater(total,0)
 def test_no_old_images(self):
  self.assertFalse([p for p in R.rglob('*') if p.suffix.lower() in {'.png','.jpg','.webp','.svg'} and 'assets/figures' not in str(p)])
 def test_source_method_mapping(self):
  rows=json.loads((R/'editorial/content-disposition.json').read_text());self.assertEqual(sum(x['kind']=='source-method' for x in rows),206)
if __name__=='__main__':unittest.main(verbosity=2)
