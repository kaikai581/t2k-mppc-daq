#!/usr/bin/env python

import matplotlib.pyplot as plt

bdvs_20c = [51.75, 51.52, 50.94, 51.44, 52.07, 50.65]
bdvs_20c_err = [0.159, 0.298, 0.439, 0.111, 0.773, 0.3]
bdvs_20c_temp = [20.19, 20.18, 20.46, 20.47, 20.43, 20.56]
bdvs_20c_scaled = [bdvs_20c[i]+54e-3*(25-bdvs_20c_temp[i]) for i in range(len(bdvs_20c))]
bdvs_20c_err_scaled = [bdvs_20c_err[i] for i in range(len(bdvs_20c))]

bdvs_25c = [51.44, 51.76, 51.79, 52.04, 51.76, 51.31]
bdvs_25c_err = [0.146, 0.149, 0.228, 0.115, 0.359, 0.495]
bdvs_25c_temp = [24.97, 25.09, 24.76, 25.09, 25.11, 25.16]
bdvs_25c_scaled = [bdvs_25c[i]+54e-3*(25-bdvs_25c_temp[i]) for i in range(len(bdvs_25c))]
bdvs_25c_err_scaled = [bdvs_25c_err[i] for i in range(len(bdvs_25c))]

ch_lbls = ['PCB1CH20', 'PCB1CH24', 'PCB2CH20', 'PCB2CH24', 'PCB3CH20', 'PCB3CH24']
chs = [1, 2, 3, 4, 5, 6]

plt.errorbar(chs, bdvs_20c, bdvs_20c_err, linestyle='None', marker='o', label='$\sim$20°C')
plt.errorbar(chs, bdvs_25c, bdvs_25c_err, linestyle='None', marker='o', label='$\sim$25°C')
plt.xticks(chs, ch_lbls)
plt.ylabel('breakdonw voltage (V)')
plt.legend(loc='upper left')
plt.savefig('breakdown_vs_channel_raw.png')

plt.close()

plt.errorbar(chs, bdvs_20c_scaled, bdvs_20c_err_scaled, linestyle='None', marker='o', label='scaled from $\sim$20°C')
plt.errorbar(chs, bdvs_25c_scaled, bdvs_25c_err_scaled, linestyle='None', marker='o', label='scaled from $\sim$25°C')
plt.xticks(chs, ch_lbls)
plt.title('scaled to 25°C')
plt.ylabel('breakdonw voltage (V)')
plt.legend(loc='upper left')
plt.savefig('breakdown_vs_channel_scaled.png')

