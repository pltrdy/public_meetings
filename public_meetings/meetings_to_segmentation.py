#!/usr/bin/env python
import os

from public_meetings import data_root, file_ext, load_meeting


def meetings_to_segmentation(output_root, meeting_root=data_root,
                             file_ext=file_ext):
    """
        Read meetings from `meeting_root` and writes transcription side
        in a segmentation format i.e.:
            - a [prefix].txt source file w/ one transcription segment per line
            - a [prefix].seg.ref reference with segmentation separators
              `==========`
    """
    for filename in os.listdir(meeting_root):
        if not filename.endswith(file_ext):
            continue

        print("Processing '%s'" % filename)
        path = os.path.join(meeting_root, filename)
        out_path = os.path.join(output_root, filename + ".txt")
        aligned_to_ctm_text(path, out_path)


def aligned_to_ctm_text(algned_path, out_path):
    positive_only = False
    algned = load_meeting(algned_path)

    final_ctms = algned["final"]["ctm"]
    out = open(out_path, "w")
    ref_path = out_path+".seg.ref"
    out_ref = open(ref_path, "w")

    prev_aligned = None
    if not positive_only:
        print("==========", file=out_ref)

    for ctm in final_ctms:
        if (ctm["aligned"] == '' or ctm["aligned"] == '-1'
                or ctm["aligned"] == -1):
            if positive_only:
                continue
        if prev_aligned is not None and ctm["aligned"] != prev_aligned:
            print("==========", file=out_ref)
        print(ctm["text"], file=out)
        print(ctm["text"], file=out_ref)
        prev_aligned = ctm["aligned"]
    print("==========", file=out_ref)
    print("Wrote to: '%s'" % out_path)
    print("Wrote to: '%s'" % ref_path)
    print("Done.")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-meeting_root", "-m", default=data_root,
                        help="Meeting root directory")
    parser.add_argument("-output_root", "-o", required=True,
                        help="Output root directory")

    args = parser.parse_args()

    meetings_to_segmentation(args.output_root, args.meeting_root)
