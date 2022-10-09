import pprint
import numpy as np
import copy

data = [[100, 'Part', 'RIVET-60H453032-032'],
 [4356, 'Part', 'RIVET-60H453232A021'],
 [16, 'Part', 'RIVET-60H453232A052'],
 [1, 'Part', 'RM7922000201-126-GPU-TRAY-BASE'],
 [289, 'Part', 'RM7922000201-126-S01'],
 [1, 'Part', 'RM7922000201-126-S02'],
 [1, 'Part', 'RM7922000201-126-S04'],
 [4, 'Part', 'RM7922000201-126-S05'],
 [324, 'Part', 'RM7922000201-126-S06-RAIL-T-PIN'],
 [1, 'Part', 'RM7922000201-126-S07'],
 [4, 'Part', 'RM7922000201-126-S08'],
 [16, 'Part', 'RM7922000201-126-S09-T-PIN'],
 [4, 'Part', 'RM7922000201-126-S10-NUT'],
 [4, 'Part', 'RM7922000201-126-S11-FOR_SRING'],
 [4, 'Part', 'RM7922000201-128-K2-TRAY-SPRING'],
 [1, 'Part', 'RM7922000201-199-GPU-SUP-BKT-F'],
 [1, 'Part', 'RM7922000201-401-GPU-SUP-BKT'],
 [1, 'Part', 'RM7922000201-402-SUPPORT-BKT'],
 [2, 'Part', 'RM7922000201-404-GPU-BAR-HOLD']]

data_cp = copy.deepcopy(data)
data_cp[-1][0] = 5

np_data = np.array(data)
np_data_cp = np.array(data_cp)

np_data = np_data[np_data[:,2].argsort()]
np_data_cp = np_data_cp[np_data_cp[:,2].argsort()]

comparison = np_data == np_data_cp
equal_arrays = comparison.all()
print(equal_arrays)

# print(np_data)