# -*- coding: utf-8 -*-
import os, re, codecs,  string
from trial_sat import SATTrial
from trial_spr import SPRTrial
from text_display import InstructionsDisplay
from tc import *

# TODO: convert "RSVP" to "SAT" or some such, a stimulus should have several parameters eventually: (a) presentation mode (moving window / centered), (b) window size in phrases/words, (c) self- or auto-paced, (d) SAT / other

regexpSPRQuestion_ID = re.compile("^\s*(\w+)\s+(\w+)\s+(\w+)\s+SPR\s+([MC][WN])\s+(.+)\s+/\?\s+(.+)\s*$")
regexpSPRNoQuestion_ID = re.compile("^\s*(\w+)\s+(\w+)\s+(\w+)\s+SPR\s+([MC][WN])\s+(.*)$")
regexpRSVP_ID          = re.compile("^\s*(\w+)\s+(\w+)\s+(\w+)\s+RSVP\s+([MC][WN])\s+([YN?!s])\s+([RL12])\s+(.*)$")
instructionMarker = "---"
commentMarker = "#"



def debug(string, level=1):
	if level < 2:
		print ("STIMULI(%s): "%get_time())+string

def split_stimulus(string):
	string = re.sub(" ", "/", string)
	string = re.sub("_", " ", string)
	string = string.split("/")
	stimulus = []
	for s in string:
		if s:
			stimulus.append(s)
	return stimulus


def apply_macros(macros, line):
	for name, content in macros:
		line = line.replace('$'+name, content)
	return line

def read_stimuli(filename, config):
	#f = open(filename, "r")
	f = codecs.open(filename, "r", "utf-8")
	stimuli = []
	macros = []
	expectingInstructions = False
	instructionsText = ""
	linenum = -1
	lines = f.readlines()
	while linenum < (len(lines)-1):
		linenum = linenum +1
		debug("linenum <%s>" % linenum)
		line = lines[linenum]
		debug("line <%s>" % line)

		if(len(line) < 2):
			continue

		if re.match(commentMarker, line):
			continue

		if (line.startswith("%include") or line.startswith("%INCLUDE")): 
			fname_include = line[8:].strip()
			fname_include = os.path.dirname(filename)+'/'+ fname_include
			fname_lines = open(fname_include, "r").readlines()
			lines.insert(linenum+1, fname_lines)
			new_lines = lines[0:linenum+1]+fname_lines+lines[(linenum+2):]
			lines = new_lines
			debug("%s"%lines)
			continue

		if (line[0] == "!"): # TODO: implement detection of undefined macros
			line = apply_macros(macros, line)
			split_line = string.split(line[1:], " ", 1)
			debug("SPLIT_LINE: %s" % split_line)
			assert(len(split_line)==2)
			macro = (split_line[0].strip(), split_line[1].strip())
			macros.append(macro)
			continue

		line = apply_macros(macros, line)

		# in instructions mode
		if expectingInstructions:
			if re.match(instructionMarker, line):
				expectingInstructions = False
				stimuli.append(InstructionsDisplay(config, instructionsText))
				instructionsText = ""
			else:
				instructionsText = instructionsText + line
			continue 

		# in stimulus mode
		m = regexpRSVP_ID.match(line)
		if m:
			exp, item, cond, mode, grammatical, start_button, stimulus = m.groups()
			debug("Processing RSVP stimulus.")
			s = SATTrial(config, exp, item, cond, mode, 
				     split_stimulus(stimulus), grammatical, 
				     start_button)
			stimuli.append(s)
			continue

		m= regexpSPRQuestion_ID.match(line)
		if m:
			exp, item, cond, mode, stimulus, question = m.groups()
			debug("Processing SPR stimulus, with question: <%s>" % line)
			question,  answers = string.split(question,  "? ")
			answers = string.split(string.strip(answers),  " ")
			assert(len(answers)==2)
			answers[0] = re.sub("_", " ", answers[0])
			answers[1] = re.sub("_", " ", answers[1])

			if answers[0][-1] == "!":
				answers[0] = answers[0][:-1]  
				correct = answers[0]
			elif answers[1][-1] == "!":
				answers[1] = answers[1][:-1]  
				correct = answers[1]
			else:
				raise BaseException("One answer needs to be marked as correct.")
				# TODO: Ensure that only one answer is marked as correct.
				# TODO: Add diagnostic for left/right balance.

			question = {'question': question+'?',  'answers': answers, 'correct': correct }
			s = SPRTrial(config, exp, item, cond, mode, split_stimulus(stimulus), question )
			stimuli.append(s)
			continue

		m= regexpSPRNoQuestion_ID.match(line)
		if m:
			exp, item, cond, mode, stimulus = m.groups()
			debug("Processing SPR stimulus, no question.")
			s = SPRTrial(config, exp, item, cond, split_stimulus(stimulus))
			stimuli.append(s)
			continue

		line = line.strip()
		if len(line) == 0:
			debug("Ignoring empty line.")
			continue

		if (line[0] == "{") and (line[-1] == "}"):
			debug("Evaluating line: <%s>" % line)
			arg = eval(line)
			if arg['expmode'] == 'SAT' or arg['expmode'] == 'MR-SAT':
				debug("Processing RSVP stimulus.")
				s = SATTrial(arg['expmode'], config, split_stimulus(unicode(arg['stimulus'])), arg)
				stimuli.append(s)
				continue

		if re.match(instructionMarker, line):
			expectingInstructions = True
			processed = False

		else:
			print(line)
			raise(BaseException("Can't parse <%s>" % line))

	return stimuli

