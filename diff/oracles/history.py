from pathlib import Path
import json

LineCoverageHistory = dict[str,dict[str,list[int]]]
BranchCoverageHistory = dict[str,dict[str,list[list[int]]]]
McdcHistory = dict[str,dict[str,list[list[bool]]]]

with open(Path(__file__).resolve().parent.parent / 'config.json') as f:
    repeat = json.load(f)['repeat']
