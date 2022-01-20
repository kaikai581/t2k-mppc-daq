# Calibration Factor from Charge Injection
From the circuit simulation results, the charge from integrating the output current should be used for calculating the conversion factor.  

## Measurement of Charge Input to FEB
The input voltage to FEB is measured with a scope and the data is exported to `20211102_data/20211102_ch_inj_*.csv`.  
Use `20211102_data/integrate_output_current.py` to get the charge input to FEB, which is  
```
mean: 5.942e-12 C
 std: 3.919e-15 C
```

## Obtain Channel-by-channel Conversion Factors
To obtain channel-by-cnahhel conversion factors, two steps are involved.  
1. Run through all root files and create a database under `process_taken_data`. For example,  
  ```./process_taken_data.py -i /cshare/vol2/users/shihkai/data/mppc/root/charge_injection_calib_data/20210625_new_pcb_without_t_feb428/*.root```  
  This will create a `.csv` file in the `processed_data` folder.
2. 
