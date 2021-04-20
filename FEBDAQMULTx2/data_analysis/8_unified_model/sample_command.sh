for i in {0..31}; do time ./dark_rate_in_pe.py -f calib_paths/thr220_ch0-31.txt -b 1 --output_path plots/dark_rate_in_pe/calib_thr220 -d 20210204_volt58_ch0-31_feb170 -ph 0 -p 100 -c ${i}; done
