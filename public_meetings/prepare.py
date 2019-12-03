#!/usr/bin/env python
import os
import pickle
import numpy as np
import public_meetings


def rm_tags(seqs):
    words = []

    for word in seqs.split():
        if not (word.startswith("<") and word.endswith(">")):
            words.append(word)
    return " ".join(words)


def fix_tags(seqs):
    seqs.replace("<", "[")
    seqs.replace(">", "]")
    return seqs


sen_break = [".", "?", "!", "</h>", "</p>", "</nom>"]


def split_sentences(seq):
    prev_break = False
    result = [[]]
    for word in seq.split():
        if word in sen_break:
            prev_break = True
        else:
            if prev_break:
                result += [[]]
            prev_break = False
        result[-1] += [word]
    return [" ".join(s) for s in result]


def count_words(seq): return len([_ for _ in seq.split()
                                  if _ not in sen_break
                                  and not _.startswith("<")
                                  and not _.endswith(">")])


def filter_min_words(seq, n): return count_words(seq) >= n


def filter_max_words(seq, n): return count_words(seq) <= n


def filter_min_sentences(sen, n): return sen >= n


def filter_max_sentences(sen, n): return sen <= n


def prepare(dir_path, min_w=30, max_w=1000, min_s=3, max_s=50, overlap_prct=0,
            n_draw=0, output=None, verbose=False, remove_tags=False,
            remove_unks=True, sentence_tags=False, rm_names=False,
            rm_headers=False, rm_p=False):
    """
        Preparing meeting data for neural models (either for training
        or inference).

        It reads all meetings from `dir_path` and writes transcription
        text (i.e. the `ctm` side) to a *.src.txt file
        and the report (i.e. `doc` side) to a *.tgt.txt file.

        Output files have the following format:
            [output]_[parameters].[src|tgt].txt
            w/ parameters=
                [min_w]_[max_w]_[min_s]_[max_s]_[o_prct]_[n_draw]
    """
    def log(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    aligned_path = [os.path.join(dir_path, _)
                    for _ in os.listdir(dir_path)
                    if _.endswith(".aligned.pckl")
                    or _.endswith(".align.pt")]

    if output is not None:
        output = "%s_%d_%d_%d_%d_%d_%d" % (
            output, min_w, max_w, min_s, max_s, overlap_prct, n_draw)
        out_src_path = "%s.src.txt" % output
        out_tgt_path = "%s.tgt.txt" % output

        out_src = open(out_src_path, 'w')
        out_tgt = open(out_tgt_path, 'w')

    def to_output(src, tgt):
        if output is not None:
            print(src, file=out_src)
            print(tgt, file=out_tgt)

    min_n_word = min_w
    max_n_word = max_w

    min_n_sentences = min_s
    max_n_sentences = max_s

    tot_n_ctm = 0
    tot_w_ctm = 0

    tot_n_doc = 0
    tot_w_doc = 0

    filtered_n_ctm = 0
    filtered_w_ctm = 0

    filtered_n_doc = 0
    filtered_w_doc = 0

    dropped_ctm = 0
    dropped_w_ctm = 0

    def process_docx_sentences(sentences):
        final_sentences = []

        for s in sentences:
            if remove_tags:
                s = rm_tags(s)
            if rm_p:
                s = s.replace('<p> ', '').replace(' </p>', '')

            if s.startswith("<nom>") and s.endswith("</nom>"):
                if rm_names:
                    continue
            else:
                # fix case where <nom> may wrap multiple sentences
                s = s.replace('<nom> ', '').replace(' </nom>', '')

            if rm_headers:
                if s.startswith("<h>") and s.endswith("</h>"):
                    continue

            if sentence_tags:
                s = "<t> %s </t>" % s
            final_sentences.append(s)
        return final_sentences

    for path in aligned_path:
        doc_ids = {}
        doc_texts = []
        alignment = []
        ctm_texts = []

        if path.endswith('.pt'):
            # Automatic Alignment outputs:
            # `autoalign` serilialize files using torch
            # https://github.com/pltrdy/autoalign
            import torch
            d = torch.load(path)
            n_ctm = 0
            for i, pair in enumerate(d):
                text = pair["doc"]
                if remove_tags:
                    text = rm_tags(text)
                sentences = process_docx_sentences(split_sentences(text))

                otext = text
                text = " ".join(sentences)
                doc_texts.append(sentences)
                tot_n_doc += 1
                tot_w_doc += count_words(text)
                if "<nom>" in text:
                    raise ValueError(
                        "OTEXT:%s\nTEXT:%s\nFound <nom> in %s, pair %d"
                        % (otext, text, path, i))

                segments = pair["ctm"]
                if remove_unks:
                    segments = [_.replace("<unk>", "") for _ in segments]
                w_ctm = count_words(" ".join(segments))

                alignment.append([])
                for s in segments:
                    sentences = split_sentences(s)
                    ctm_texts.append(sentences)
                    alignment[i].append(n_ctm)
                    n_ctm += 1
                tot_n_ctm += n_ctm
                tot_w_ctm += w_ctm

        elif path.endswith('.pckl'):
            # Gold references: looking for d["final"]
            with open(path, 'rb') as f:
                d = pickle.load(f)

            doc_ids = {}
            doc_texts = []
            for i, doc in enumerate(d["final"]["doc"]):
                doc_id = doc["id"]
                if doc_id in doc_ids.keys():
                    raise ValueError(
                        "Error with redundant doc id '%s'" % doc_id)
                doc_ids[doc_id] = i

                text = doc["text"]
                if remove_tags:
                    text = rm_tags(text)

                sentences = process_docx_sentences(split_sentences(text))

                doc_texts.append(sentences)
                tot_n_doc += 1
                tot_w_doc += count_words(doc["text"])

            # alignment[i] is the list of ctm_id aligned with doc#i
            alignment = [[] for i in range(len(doc_texts))]
            ctm_texts = []
            for i, ctm in enumerate(d["final"]["ctm"]):
                aligned = ctm["aligned"]
                text = ctm["text"]

                if remove_unks:
                    text = text.replace("<unk>", "")

                w_ctm = count_words(text)

                ctm_texts.append(split_sentences(text))
                if aligned == "":
                    dropped_ctm += 1
                    dropped_w_ctm += w_ctm
                    continue

                assert aligned in doc_ids.keys()
                alignment[doc_ids[aligned]].append(i)
                tot_n_ctm += 1
                tot_w_ctm += w_ctm
        else:
            raise ValueError("Invalid extension for '%s'" % path)

        for doc, i_ctms in zip(doc_texts, alignment):
            w_doc = count_words(" ".join(doc))
            s_doc = len(doc)

            ctm = [ctm_texts[i] for i in i_ctms]
            ctm_sentences = sum(ctm, [])
            w_ctm = count_words(" ".join(ctm_sentences))
            s_ctm = len(ctm_sentences)
            if not min_n_word < w_doc < max_n_word:
                continue

            if not s_doc < max_n_sentences:
                continue

            if min_n_word <= w_ctm <= max_n_word:
                if min_n_sentences <= s_ctm <= max_n_sentences:
                    filtered_n_ctm += len(ctm)
                    filtered_w_ctm += w_ctm
                    filtered_n_doc += 1
                    filtered_w_doc += count_words(" ".join(doc))

                    # the right alignment (no overlap)
                    src = " ".join(ctm_sentences)
                    tgt = " ".join(doc)
                    to_output(src, tgt)
                    log("Right alignment:\n\t'%s ... %s'\n\t'%s ... %s'" %
                        (src[:20], src[-20:], tgt[:20], tgt[-20:]))

                    # overlap
                    for k in range(n_draw):
                        overlap_before_prct = np.random.random() * overlap_prct
                        overlap_before_sen = round(
                            s_ctm * (overlap_before_prct / 100))

                        overlap_after_prct = np.random.random() * overlap_prct
                        overlap_after_sen = round(
                            s_ctm * (overlap_after_prct / 100))

                        src = ctm_sentences

                        # before overlap
                        j_ctm = i_ctms[0] - 1
                        overlap_len = 0
                        while overlap_len < overlap_before_sen:
                            remaining = overlap_before_sen - overlap_len

                            overlap = ctm_texts[j_ctm][-remaining:]
                            overlap_len += len(overlap)
                            src = overlap + src
                            j_ctm -= 1

                        # after overlap
                        j_ctm = i_ctms[-1] + 1
                        overlap_len = 0
                        while (overlap_len < overlap_before_sen
                               and j_ctm < len(ctm_texts)):
                            remaining = overlap_before_sen - overlap_len
                            try:
                                overlap = ctm_texts[j_ctm][:remaining]
                            except IndexError as e:
                                print("IndexError: j_ctm: %d, len: %d" %
                                      (j_ctm, len(ctm_texts)))
                                raise e
                            overlap_len += len(overlap)
                            src = src + overlap
                            j_ctm += 1

                        log("Overlap: before: %d(%.3f), after: %d(%.3f)"
                            % (overlap_before_sen, overlap_before_prct,
                               overlap_after_sen, overlap_after_prct))
                        log("Before: %s"
                            % "|".join(src[:overlap_before_sen+1]))
                        log("After: %s" % "|".join(src[overlap_after_sen-1:]))
                        to_output(" ".join(src), tgt)

    print("ctm: tot: %d | f: %d | r: %.3f%%" %
          (tot_n_ctm, filtered_n_ctm, 100*filtered_n_ctm/tot_n_ctm))
    print("doc: tot: %d | f: %d | r: %.3f%%" %
          (tot_n_doc, filtered_n_doc, 100*filtered_n_doc/tot_n_doc))
    print("ctm/doc: tot: %.3f | f: %.3f" %
          (tot_n_ctm/tot_n_doc, filtered_n_ctm/filtered_n_doc))
    print("---")
    print("wdoc: tot: %d | f: %d | r: %.3f%%" %
          (tot_w_doc, filtered_w_doc, 100*filtered_w_doc/tot_w_doc))
    print("wctm: tot: %d | f: %d | r: %.3f%%" %
          (tot_w_ctm, filtered_w_ctm, 100*filtered_w_ctm/tot_w_ctm))
    print("ctm/doc: tot: %.3f | f: %.3f" %
          (tot_w_ctm/tot_w_doc, filtered_w_ctm/filtered_w_doc))


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "-d", default=public_meetings.data_root,
                        help="Aligned meeting root")
    parser.add_argument("-mw", type=int, default=30,
                        help="Min #words")
    parser.add_argument("-Mw", type=int, default=1000,
                        help="Max #words")
    parser.add_argument("-ms", type=int, default=3,
                        help="Min #sentences")
    parser.add_argument("-Ms", type=int, default=50,
                        help="Max #sentences")

    parser.add_argument("-remove_tags", action="store_true",
                        help="Remove every tags i.e. <*>")
    parser.add_argument("-remove_unks", action="store_true",
                        help="Remove unknown tags i.e. <unk>")
    parser.add_argument("-remove_names", action="store_true",
                        help="Remove names i.e. <nom>*</nom>")
    parser.add_argument("-remove_headers", action="store_true",
                        help="Remove headers i.e. <h>*</h>")
    parser.add_argument("-remove_p", action="store_true",
                        help="Remove paragraph tags i.e. <p> and </p>")
    parser.add_argument("-sentence_tags", action="store_true",
                        help="And sentence separators <t> and </t>")

    parser.add_argument("-overlap_prct", "-oprct", type=float, default=0)
    parser.add_argument("-n_draw", type=int, default=0)

    parser.add_argument("-output", type=str, default="public_meetings",
                        help="Output path prefix")

    parser.add_argument("-verbose", "-v", action="store_true")
    args = parser.parse_args()
    prepare(args.dir,
            args.mw,
            args.Mw,
            args.ms,
            args.Ms,
            args.overlap_prct,
            args.n_draw,
            args.output,
            args.verbose,
            args.remove_tags,
            args.remove_unks,
            args.sentence_tags,
            args.remove_names,
            args.remove_headers,
            args.remove_p
            )


if __name__ == "__main__":
    main()
