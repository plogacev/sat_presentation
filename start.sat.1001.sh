#!/bin/bash
SUBJ=1001

# 1152, 864
RUN="/usr/bin/python2.7 RTExp/runSAT.py -j $SUBJ Experimente"
$RUN Intro
$RUN RaceArg_Block1a
$RUN RaceArg_Block2a
$RUN RaceArg_Block3a
$RUN RaceArg_Block4a
