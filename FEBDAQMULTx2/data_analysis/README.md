# Welcome to Join the Fun of MPPC Data Analysis
There are so many topics about the MPPC characterization that different subtopics have dedicated folders for them.  
This README serves as the index to get to the right folder.

## Dark Rate vs Threshold
Analysis scripts reside in `6_rate_and_threshold`.  
Here is an example command if you want to draw rate vs. threshold:  
```$ for b in {0..1}; do for c in {0..31}; do time ./dark_rate_vs_threshold.py -i /cshare/vol2/users/shihkai/data/mppc/root/dark/20211106_volt57_gain56_ch0-63_feb136_feb428_temp20/20211106_170440_dark_rate_feb${b}_ch${c}_thr2*.root -o plots/20211106_volt57_gain56_ch0-63_feb136_feb428_temp20; done; done```  
Here is an example command if you want to draw rate vs. PE:  
```$ for b in {0..1}; do for c in {0..31}; do time ./dark_rate_vs_pe_calibration.py -i /cshare/vol2/users/shihkai/data/mppc/root/dark/20211106_volt57_gain56_ch0-63_feb136_feb428_temp20/20211106_170440_dark_rate_feb${b}_ch${c}_thr2*.root -l /cshare/vol2/users/shihkai/data/mppc/root/led/20211105_203742_64chpcb_thr225_gain56_temp20_trig0-63_feb136_feb428/20211105_204519_mppc_volt57.0_thr225_gain56_temp20.1.root; done; done```  
