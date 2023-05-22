import numpy as np

from liana.method.sp._bivariate_funs import _vectorized_pearson, _vectorized_spearman, \
    _vectorized_cosine, _vectorized_jaccard, _masked_pearson, \
         _masked_spearman, _masked_cosine, _masked_jaccard, _local_morans

from scipy.sparse import csr_matrix


rng = np.random.default_rng(seed=0)

x_mat = rng.normal(size=(20, 5)).astype(np.float32)
y_mat = rng.normal(size=(20, 5)).astype(np.float32)
weight = csr_matrix(rng.uniform(size=(20, 20)).astype(np.float32))


def _assert_bivariate(function, desired, x_mat, y_mat, weight):
    actual = function(x_mat, y_mat, weight)
    assert actual.shape == (5, 20)
    np.testing.assert_almost_equal(actual[:,0], desired, decimal=5)
    

def test_pc_vectorized():
    pc_vec_truth = np.array([ 0.25005114,  0.04262733, -0.00130362,  0.2903336 , -0.1236529])
    _assert_bivariate(_vectorized_pearson, pc_vec_truth, x_mat, y_mat, weight)


def test_pc_masked():
    pc_masked_truth = np.array([ 0.25005117,  0.04262732, -0.00130363,  0.2903336 , -0.12365292])
    _assert_bivariate(_masked_pearson, pc_masked_truth, x_mat, y_mat, weight.A)  # NOTE the .A is to convert to dense


def test_sp_vectorized():
    sp_vec_truth = np.array([ 0.23636213,  0.16480759, -0.01487235,  0.22840601, -0.11492937])
    _assert_bivariate(_vectorized_spearman, sp_vec_truth, x_mat, y_mat, weight)

def test_sp_masked():
    sp_masked_truth = np.array([0.23636216, 0.16480756, -0.0148723, 0.22840606, -0.11492944])
    _assert_bivariate(_masked_spearman, sp_masked_truth, x_mat, y_mat, weight.A)  # NOTE the .A is to convert to dense


def test_costine_vectorized():
    cosine_vec_truth = np.array([ 0.33806977,  0.03215113,  0.0950243 ,  0.2957758 , -0.10259595 ])
    _assert_bivariate(_vectorized_cosine, cosine_vec_truth, x_mat, y_mat, weight)


def test_cosine_masked():
    cosine_masked_truth = np.array([ 0.3380698 ,  0.03215112,  0.09502427,  0.29577583, -0.10259596])
    _assert_bivariate(_masked_cosine, cosine_masked_truth, x_mat, y_mat, weight.A) # NOTE the .A is to convert to dense


def test_vectorized_jaccard():
    jaccard_vec_truth = np.array([0.34295967, 0.35367563, 0.39685577, 0.41780996, 0.30527356])
    _assert_bivariate(_vectorized_jaccard, jaccard_vec_truth, x_mat, y_mat, weight)


def test_masked_jaccard():
    def _binarize(mat):
       return (mat > 0).astype(np.float32)
        
    x_bin, y_bin = _binarize(x_mat), _binarize(y_mat)
    jac_masked_truth = np.array([0.34295967, 0.35367563, 0.39685577, 0.41780996, 0.30527356])
    _assert_bivariate(_masked_jaccard, jac_masked_truth, x_bin, y_bin, weight.A) # NOTE the .A is to convert to dense


# NOTE: spatialdm uses raw counts
def test_morans():
    sp_morans_truth = np.array([-1.54256,  0.64591,  1.30025,  0.55437, -0.77182])
    _assert_bivariate(_local_morans, sp_morans_truth, x_mat, y_mat, weight)
