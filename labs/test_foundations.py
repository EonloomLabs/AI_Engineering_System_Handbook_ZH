"""基础课手算、边界条件和常见错误的确定性测试。不是LLM质量评测。"""
import math
import unittest
from foundation_lab import (E,shape,pad,lookup,matmul,transpose,reshape_flat,softmax,
                            attention,causal_mask,layernorm,rotate,scalar_training,
                            rrf,finite_difference,build_results)

class FoundationTests(unittest.TestCase):
    def assertVector(self,a,b,places=10):
        self.assertEqual(len(a),len(b))
        for x,y in zip(a,b): self.assertAlmostEqual(x,y,places=places)
    def test_scalar_shape(self): self.assertEqual(shape(7),())
    def test_matrix_shape(self): self.assertEqual(shape([[1,2,3],[4,5,6]]),(2,3))
    def test_ragged_rejected(self):
        with self.assertRaises(ValueError): shape([[1,2],[3]])
    def test_pad_ids(self): self.assertEqual(pad([[1,2,3],[4,2]])[0],[[1,2,3],[4,2,0]])
    def test_pad_valid(self): self.assertEqual(pad([[1,2,3],[4,2]])[1],[[1,1,1],[1,1,0]])
    def test_padding_does_not_truncate(self):
        with self.assertRaises(ValueError): pad([[1,2,3]],2)
    def test_embedding_shape(self): self.assertEqual(shape(lookup([[1,2,3],[4,2,0]])),(2,3,4))
    def test_embedding_exact_row(self): self.assertEqual(lookup(4),[0,1,1,0])
    def test_same_token_same_initial_row(self): self.assertEqual(lookup([[1,2],[4,2]])[0][1],lookup(2))
    def test_invalid_id_rejected(self):
        for v in [-1,6,1.5,True]:
            with self.assertRaises(ValueError): lookup(v)
    def test_lookup_does_not_modify_parameter(self):
        a=lookup(1); a[0]=999; self.assertEqual(E[1][0],1)
    def test_independent_batch(self):
        h=lookup([[1,2,3],[4,2,0]]); other=lookup([[5,5,5],[4,2,0]])
        self.assertEqual(h[1],other[1])
    def test_matrix_product(self): self.assertEqual(matmul([[1,2,3],[4,5,6]],[[1,0],[0,1],[1,1]]),[[4,5],[10,11]])
    def test_matrix_bad_dimensions(self):
        with self.assertRaises(ValueError): matmul([[1,2]],[[1,2]])
    def test_transpose_not_reshape(self): self.assertNotEqual(transpose([[1,2,3],[4,5,6]]),reshape_flat([1,2,3,4,5,6],3,2))
    def test_softmax_hand_calculation(self): self.assertVector(softmax([0,math.log(2),math.log(3)]),[1/6,1/3,.5])
    def test_softmax_translation(self): self.assertVector(softmax([1,2,3]),softmax([1001,1002,1003]))
    def test_softmax_sum_one(self): self.assertAlmostEqual(sum(softmax([-1000,0,1000])),1)
    def test_all_masked_rejected(self):
        with self.assertRaises(ValueError): softmax([-math.inf,-math.inf])
    def test_attention_hand_calculation(self):
        d=attention([1,0],[[1,0],[0,1]],[[10,0],[0,20]])
        a=1/(1+math.exp(-1/math.sqrt(2)))
        self.assertVector(d['weights'],[a,1-a]); self.assertVector(d['output'],[10*a,20*(1-a)])
    def test_mask_eliminates_value(self): self.assertVector(attention([1,0],[[1,0],[0,1]],[[10,0],[0,20]],[True,False])['output'],[10,0])
    def test_causal_triangle(self): self.assertEqual(causal_mask(0,3),[[True,False,False],[True,True,False],[True,True,True]])
    def test_cached_non_square_mask(self): self.assertEqual(causal_mask(3,2),[[True]*4+[False],[True]*5])
    def test_cached_wrong_top_left_mask_detected(self): self.assertNotEqual(causal_mask(3,2),[[True,False,False,False,False],[True,True,False,False,False]])
    def test_padding_key_excluded(self): self.assertEqual(causal_mask(0,3,[1,1,0])[-1],[True,True,False])
    def test_rotation_preserves_norm(self):
        r=rotate([2,3],math.pi/2); self.assertVector(r,[-3,2]); self.assertAlmostEqual(sum(x*x for x in r),13)
    def test_layernorm(self): self.assertVector(layernorm([1,3],0),[-1,1])
    def test_layernorm_constant_with_epsilon(self): self.assertVector(layernorm([2,2]),[0,0])
    def test_gradient_finite_difference(self): self.assertAlmostEqual(finite_difference(),-4,places=6)
    def test_training_decreases_loss(self):
        d=scalar_training(); self.assertAlmostEqual(d['new_w'],1.8); self.assertAlmostEqual(d['new_loss'],.08)
    def test_logits_to_token(self): self.assertEqual(build_results()['next_token_greedy'],3)
    def test_large_shape_memory(self): self.assertEqual(build_results()['shape_scale']['output_MiB'],2)
    def test_kv_memory(self): self.assertEqual(build_results()['kv_toy']['bytes'],192)
    def test_dpo(self): self.assertAlmostEqual(build_results()['dpo_example']['sigmoid'],2/3)
    def test_kl(self): self.assertAlmostEqual(build_results()['kl_example'],.14384103622589042)
    def test_rrf(self):
        s=rrf([['A','B','C'],['B','C','A']]); self.assertGreater(s['B'],s['A'])
    def test_pass_distinction(self):
        d=build_results()['pass_independent_p08_k3'];self.assertAlmostEqual(d['at_least_once'],.992);self.assertAlmostEqual(d['all_three'],.512)
    def test_dag_overhead(self):
        d=build_results()['dag']; self.assertGreater(d['parallel_overhead4'],d['serial'])
    def test_image_patch_count(self): self.assertEqual(build_results()['image_patches']['count'],196)

if __name__=='__main__': unittest.main(verbosity=2)
