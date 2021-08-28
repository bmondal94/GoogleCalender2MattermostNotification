#!/home/bmondal/anaconda3/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 19 17:40:29 2021

@author: bmondal
"""

from datetime import datetime

x = datetime.now()

with open("/home/bmondal/TestCron.txt",'a') as f:
    f.write(x.strftime('%Y-%m-%d  %H:%M:%S\n'))
    
    