import openturns as ot
import otlm
from math import log

description = ["BIO", "SAL", "pH", "K", "Na", "Zn"]
data = [[676, 33, 5, 1441.67, 35185.5, 16.4524],
        [516, 35, 4.75, 1299.19, 28170.4, 13.9852],
        [1052, 32, 4.2, 1154.27, 26455, 15.3276],
        [868, 30, 4.4, 1045.15, 25072.9, 17.3128],
        [1008, 33, 5.55, 521.62, 31664.2, 22.3312],
        [436, 33, 5.05, 1273.02, 25491.7, 12.2778],
        [544, 36, 4.25, 1346.35, 20877.3, 17.8225],
        [680, 30, 4.45, 1253.88, 25621.3, 14.3516],
        [640, 38, 4.75, 1242.65, 27587.3, 13.6826],
        [492, 30, 4.6, 1281.95, 26511.7, 11.7566],
        [984, 30, 4.1, 553.69, 7886.5, 9.882],
        [1400, 37, 3.45, 494.74, 14596, 16.6752],
        [1276, 33, 3.45, 525.97, 9826.8, 12.373],
        [1736, 36, 4.1, 571.14, 11978.4, 9.4058],
        [1004, 30, 3.5, 408.64, 10368.6, 14.9302],
        [396, 30, 3.25, 646.65, 17307.4, 31.2865],
        [352, 27, 3.35, 514.03, 12822, 30.1652],
        [328, 29, 3.2, 350.73, 8582.6, 28.5901],
        [392, 34, 3.35, 496.29, 12369.5, 19.8795],
        [236, 36, 3.3, 580.92, 14731.9, 18.5056],
        [392, 30, 3.25, 535.82, 15060.6, 22.1344],
        [268, 28, 3.25, 490.34, 11056.3, 28.6101],
        [252, 31, 3.2, 552.39, 8118.9, 23.1908],
        [236, 31, 3.2, 661.32, 13009.5, 24.6917],
        [340, 35, 3.35, 672.15, 15003.7, 22.6758],
        [2436, 29, 7.1, 528.65, 10225, 0.3729],
        [2216, 35, 7.35, 563.13, 8024.2, 0.2703],
        [2096, 35, 7.45, 497.96, 10393, 0.3205],
        [1660, 30, 7.45, 458.38, 8711.6, 0.2648],
        [2272, 30, 7.4, 498.25, 10239.6, 0.2105],
        [824, 26, 4.85, 936.26, 20436, 18.9875],
        [1196, 29, 4.6, 894.79, 12519.9, 20.9687],
        [1960, 25, 5.2, 941.36, 18979, 23.9841],
        [2080, 26, 4.75, 1038.79, 22986.1, 19.9727],
        [1764, 26, 5.2, 898.05, 11704.5, 21.3864],
        [412, 25, 4.55, 989.87, 17721, 23.7063],
        [416, 26, 3.95, 951.28, 16485.2, 30.5589],
        [504, 26, 3.7, 939.83, 17101.3, 26.8415],
        [492, 27, 3.75, 925.42, 17849, 27.7292],
        [636, 27, 4.15, 954.11, 16949.6, 21.5699],
        [1756, 24, 5.6, 720.72, 11344.6, 19.6531],
        [1232, 27, 5.35, 782.09, 14752.4, 20.3295],
        [1400, 26, 5.5, 773.3, 13649.8, 19.588],
        [1620, 28, 5.5, 829.26, 14533, 20.1328],
        [1560, 28, 5.4, 856.96, 16892.2, 19.242]]

sample = ot.Sample(data)
sample.setDescription(description)

X = sample[:, 1:6]
Y = sample[:, 0]

#
# Build a model BIO~SAL+pH+K+Na+Zn
dim = X.getDimension()
enumerateFunction = ot.EnumerateFunction(dim)
factory = ot.OrthogonalProductPolynomialFactory(
    [otlm.MonomialFactory()] * dim, enumerateFunction)

# Build 'interactions' as a list of list [a1,a2,a3,a4,a5], and we will generate tensorized
# polynomials SAL^a1*pH^a2*K^a3*Na^a4*Zn^a5.

# BIO~SAL+pH+K+Na+Zn
interactions = []
interactions.append([0] * dim)
for i in range(dim):
    indices = [0] * dim
    indices[i] = 1
    # Y ~ I(Xi)^1
    interactions.append(indices[:])

funcs = [factory.build(enumerateFunction.inverse(indices))
         for indices in interactions]
description = X.getDescription()
description.add('f')
[f.setDescription(description) for f in funcs]


basis = ot.Basis(funcs)
#

i_min = [interactions.index([0, 0, 0, 0, 0])]
i_0 = i_min[:]

#---------------- Forward / Backward-------------------
#   X: input sample
#   basis : Basis
#   Y: output sample
#   i_min:  indices of minimal model
#   direction: Boolean (True FORWARD, False BACKWARD)
#   penalty: multiplier of number of degrees of freedom
#   maxiteration: maximum number of iterations

#---------------- Both-------------------
#   X: input sample
#   basis : Basis
#   Y: output sample
#   i_min : indices of minimal model
#   i_0   : indices of start model
#   penalty: multiplier of number of degrees of freedom
#   maxiteration: maximum number of iterations

penalty_BIC = log(X.getSize())
penalty_AIC = 2.
maxiteration = 1000

for k in [penalty_AIC, penalty_BIC]:
    # Forward / Backward
    if k == penalty_AIC:
        IC = " AIC "
    if k == penalty_BIC:
        IC = " BIC "
    for forward in [True, False]:
        algo = otlm.LinearModelStepwiseAlgorithm(
            X, basis, Y, i_min, forward, k, maxiteration)
        algo_result = otlm.LinearModelAnalysis(algo.getResult())
        print("{0:~^60s}".format(""))
        if forward == True:
            print(" Forward " + IC)
        else:
            print(" Backward " + IC)
        print("{0:~^60s}".format(""))
        print(algo_result)
    # Both
    algo = otlm.LinearModelStepwiseAlgorithm(
        X, basis, Y, i_min, i_0, k, maxiteration)
    algo_result = otlm.LinearModelAnalysis(algo.getResult())
    print("{0:~^60s}".format(""))
    print(" Both " + IC)
    print("{0:~^60s}".format(""))
    print(algo_result)
