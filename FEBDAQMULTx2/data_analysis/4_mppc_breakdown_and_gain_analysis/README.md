# Analysis Procedure

Update: 2021/11/13  

Since the number of revisions of the analysis scripts is getting large, I am writing down the scripts and commands used for extracting relevant physics parameters.  

There are two kinds of data that are most likely to be taken and examined. They are LED and dark rate runs.

## LED Runs

With LED runs, we can extract the breakdown voltage and MPPC gain. Besides, we can determine the pedestal ADC.  

The first task is to determine the breakdown voltage. To use the analysis scripts, all ROOT files from bias voltage scan have to be put in one folder. As of writing, all data files are stored on the LSU cluster at `/cshare/vol2/users/shihkai/data/mppc/root/led` for LED runs.  

### Breakdown Voltage and Uncalibrated Gain

Then one can run the command to calculate the breakdown voltages and uncalibrated gains for all channels. Note that the uncalibrated gain means the number of ADC channels per overvoltage.  
```
./v2_breakdown_loop_two_febs.py --fit_spectrum_shape -i <data_folder>/*.root
```
Calculated parameters are stored in the folder `processed_data`, in which `gain_database*.csv` stores parameters obtained for one bias voltage while `breakdown_database*.csv` stores parameters obtained with a voltage scan.  

To summarize the breakdown voltage over all PCB channels, refer to the following example command.
```
./v2_plot_breakdown_vs_channel.py -m 20211106_154951_64chpcb_thr225_gain56_temp20_trig0-63_feb136_feb428
```

To summarize the uncalibrated gains over all PCB channels, use the following example command.
```
./v3_plot_gain_vs_channel.py -m 20211106_154951_64chpcb_thr225_gain56_temp20_trig0-63_feb136_feb428
```
Here, the `-m` option is followed by the folder name holding the ROOT files of the dataset.  
