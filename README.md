# `public_meetings`: a meeting corpus of aligned pairs of transcriptions and reports.
**paper review ongoing, contact <pltrdy@gmail.com> for more information**

*see also https://github.com/pltrdy/autoalign*


## Getting started
- *from pip:*
```
pip install public_meetings
```

- *from sources:*
```
git clone https://github.com/pltrdy/public_meetings.git
cd public_meetings
pip install .
```

## Usage
`public_meetings` utility functions from a single entry point:
```
public_meetings [command]
```

Commands are listed in the following sections.


#### `prepare`: process all meetings to src/tgt files.
The `prepare` command is meant to prepare meetings for summarization models (either for training or inference).    
It basically load every meetings and write the transcription side in a `[prefix].src.txt` file and the report side in a `[prefix].tgt.txt`. Many parameters can be set to filter segments, on their number of words/sentences (both min and max values).   

*Example from the paper:*
```
./prepare.py \
    -mw 10 -Mw 1000 \
    -ms 3 -Ms 50 \
    -overlap_prct 0 -n_draw 0 \
    -remove_unk \
    -sentence_tag \
    -remove_names \
    -remove_headers \
    -remove_p
```
     
*full usage:*
```
public_meetings prepare -h
usage: prepare [-h] [-dir DIR] [-mw MW] [-Mw MW] [-ms MS] [-Ms MS]
               [-remove_tags] [-remove_unks] [-remove_names] [-remove_headers]
               [-remove_p] [-sentence_tags] [-overlap_prct OVERLAP_PRCT]
               [-n_draw N_DRAW] [-output OUTPUT] [-verbose]

optional arguments:
  -h, --help            show this help message and exit
  -dir DIR, -d DIR      Aligned meeting root
  -mw MW                Min #words
  -Mw MW                Max #words
  -ms MS                Min #sentences
  -Ms MS                Max #sentences
  -remove_tags          Remove every tags i.e. <*>
  -remove_unks          Remove unknown tags i.e. <unk>
  -remove_names         Remove names i.e. <nom>*</nom>
  -remove_headers       Remove headers i.e. <h>*</h>
  -remove_p             Remove paragraph tags i.e. <p> and </p>
  -sentence_tags        And sentence separators <t> and </t>
  -overlap_prct OVERLAP_PRCT, -oprct OVERLAP_PRCT
  -n_draw N_DRAW
  -output OUTPUT        Output path prefix
  -verbose, -v
```

#### `segmentation`: process the transcription side in a linear segmentation fashion.
We use this before running linear segmentation experiments. It only considers transcription side of meetings, and write it to source (one segment per line) and reference (one segment per line + segmentation separator `==========`).

You just have to set an `output_root` directory to recieve the text files, and, optionnally a different `meeting_root`

*Example:*
```
public_meetings segmentation -o ./public_meetings_txt
```
*Full usage:*
```
public_meetings segmentation -h
usage: segmentation [-h] [-meeting_root MEETING_ROOT] -output_root OUTPUT_ROOT

optional arguments:
  -h, --help            show this help message and exit
  -meeting_root MEETING_ROOT, -m MEETING_ROOT
                        Meeting root directory
  -output_root OUTPUT_ROOT, -o OUTPUT_ROOT
                        Output root directory

```
