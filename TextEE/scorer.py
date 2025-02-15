import ipdb
from copy import deepcopy 

def compute_scores(preds, golds, task):
    if task == "ED":
        return compute_ED_scores(preds, golds, metrics={"trigger_id", "trigger_cls"})
    elif task == "EAE":
        '''
        This will currently break anything thats not RAMs 
        '''
        return compute_EAE_scores(preds, golds, metrics={"argument_id", "argument_cls", "argument_attached_id", "argument_attached_cls", "argument_cross_sent_cls_score"})
    elif task == "EARL":
        return compute_EARL_scores(preds, golds, metrics={"argument_id", "argument_cls", "argument_attached_id", "argument_attached_cls"})
    elif task == "E2E":
        return compute_E2E_scores(preds, golds, metrics={"trigger_id", "trigger_cls", "argument_id", "argument_cls", "argument_attached_id", "argument_attached_cls"})

def print_scores(scores):
    print("------------------------------------------------------------------------------")
    if "trigger_id" in scores:
        print('Tri-I            - P: {:6.2f} ({:5d}/{:5d}), R: {:6.2f} ({:5d}/{:5d}), F: {:6.2f}'.format(
            scores["trigger_id"]["precision"], scores["trigger_id"]["match_num"], scores["trigger_id"]["pred_num"],
            scores["trigger_id"]["recall"], scores["trigger_id"]["match_num"], scores["trigger_id"]["gold_num"], scores["trigger_id"]["f1"]))
    if "trigger_cls" in scores:
        print('Tri-C            - P: {:6.2f} ({:5d}/{:5d}), R: {:6.2f} ({:5d}/{:5d}), F: {:6.2f}'.format(
            scores["trigger_cls"]["precision"], scores["trigger_cls"]["match_num"], scores["trigger_cls"]["pred_num"],
            scores["trigger_cls"]["recall"], scores["trigger_cls"]["match_num"], scores["trigger_cls"]["gold_num"], scores["trigger_cls"]["f1"]))
    if "argument_id" in scores:
        print('Arg-I            - P: {:6.2f} ({:5d}/{:5d}), R: {:6.2f} ({:5d}/{:5d}), F: {:6.2f}'.format(
            scores["argument_id"]["precision"], scores["argument_id"]["match_num"], scores["argument_id"]["pred_num"],
            scores["argument_id"]["recall"], scores["argument_id"]["match_num"], scores["argument_id"]["gold_num"], scores["argument_id"]["f1"]))
    if "argument_cls" in scores:
        print('Arg-C            - P: {:6.2f} ({:5d}/{:5d}), R: {:6.2f} ({:5d}/{:5d}), F: {:6.2f}'.format(
            scores["argument_cls"]["precision"], scores["argument_cls"]["match_num"], scores["argument_cls"]["pred_num"],
            scores["argument_cls"]["recall"], scores["argument_cls"]["match_num"], scores["argument_cls"]["gold_num"], scores["argument_cls"]["f1"]))
    if "argument_attached_id" in scores:
        print('Arg-I (attached) - P: {:6.2f} ({:5d}/{:5d}), R: {:6.2f} ({:5d}/{:5d}), F: {:6.2f}'.format(
            scores["argument_attached_id"]["precision"], scores["argument_attached_id"]["match_num"], scores["argument_attached_id"]["pred_num"],
            scores["argument_attached_id"]["recall"], scores["argument_attached_id"]["match_num"], scores["argument_attached_id"]["gold_num"], scores["argument_attached_id"]["f1"]))
    if "argument_attached_cls" in scores:
        print('Arg-C (attached) - P: {:6.2f} ({:5d}/{:5d}), R: {:6.2f} ({:5d}/{:5d}), F: {:6.2f}'.format(
            scores["argument_attached_cls"]["precision"], scores["argument_attached_cls"]["match_num"], scores["argument_attached_cls"]["pred_num"],
            scores["argument_attached_cls"]["recall"], scores["argument_attached_cls"]["match_num"], scores["argument_attached_cls"]["gold_num"], scores["argument_attached_cls"]["f1"]))
        
    if "argument_cross_sent_cls_score" in scores:
      print('*Cross Sentence Arg-C-F1 (matched/gold)*\n(-2): {:6.2f} ({}/{})\n(-1): {:6.2f} ({}/{})\n(0): {:6.2f} ({}/{})\n(1): {:6.2f} ({}/{})\n(2): {:6.2f} ({}/{})'.format(
            scores["argument_cross_sent_cls_score"][-2]["f1"], scores["argument_cross_sent_cls_score"][-2]["match_num"], scores["argument_cross_sent_cls_score"][-2]["gold_num"],
            scores["argument_cross_sent_cls_score"][-1]["f1"], scores["argument_cross_sent_cls_score"][-1]["match_num"], scores["argument_cross_sent_cls_score"][-1]["gold_num"],
            scores["argument_cross_sent_cls_score"][-0]["f1"], scores["argument_cross_sent_cls_score"][0]["match_num"], scores["argument_cross_sent_cls_score"][0]["gold_num"],
            scores["argument_cross_sent_cls_score"][1]["f1"], scores["argument_cross_sent_cls_score"][1]["match_num"], scores["argument_cross_sent_cls_score"][1]["gold_num"],
            scores["argument_cross_sent_cls_score"][2]["f1"], scores["argument_cross_sent_cls_score"][2]["match_num"], scores["argument_cross_sent_cls_score"][2]["gold_num"],))

    print("------------------------------------------------------------------------------")


from copy import deepcopy
def compute_EAE_scores(preds, golds, metrics={"argument_id", "argument_cls", "argument_attached_id", "argument_attached_cls"}):
    assert len(preds) == len(golds)
    scores = {}
    if "argument_id" in metrics:
        scores["argument_id"] = compute_EAE_argument_id_score(preds, golds)
    if "argument_cls" in metrics:
        scores["argument_cls"] = compute_EAE_argument_cls_score(preds, golds)
    if "argument_attached_id" in metrics:
        scores["argument_attached_id"] = compute_EAE_argument_attached_id_score(preds, golds)
    if "argument_attached_cls" in metrics:
        scores["argument_attached_cls"] = compute_EAE_argument_attached_cls_score(preds, golds)
    if "argument_cross_sent_cls_score" in metrics:
      scores["argument_cross_sent_cls_score"] = compute_EAE_argument_cross_sent_cls_score(deepcopy(preds), deepcopy(golds))
    return scores



def compute_EAE_argument_id_score(preds, golds):
    gold_arg_id, pred_arg_id = [], []
    for pred, gold in zip(preds, golds):
        assert pred["doc_id"] == gold["doc_id"] and pred["wnd_id"] == gold["wnd_id"]
        assert pred["trigger"][0] == gold["trigger"][0]
        assert pred["trigger"][1] == gold["trigger"][1]
        assert pred["trigger"][2] == gold["trigger"][2]
        gold_arg_id_ = [(gold["doc_id"], gold["wnd_id"], gold["trigger"][2], r[0], r[1]) for r in gold["arguments"]]
        pred_arg_id_ = [(pred["doc_id"], pred["wnd_id"], pred["trigger"][2], r[0], r[1]) for r in pred["arguments"]]
        gold_arg_id.extend(gold_arg_id_)
        pred_arg_id.extend(pred_arg_id_)

    gold_arg_id = set(gold_arg_id)
    pred_arg_id = set(pred_arg_id)
    arg_id_f1 = compute_f1(len(pred_arg_id), len(gold_arg_id), len(gold_arg_id & pred_arg_id))
    scores = {
        "pred_num": len(pred_arg_id),
        "gold_num": len(gold_arg_id),
        "match_num": len(gold_arg_id & pred_arg_id),
        "precision": arg_id_f1[0],
        "recall": arg_id_f1[1],
        "f1": arg_id_f1[2],
    }
    return scores

def compute_EAE_argument_cls_score(preds, golds):
    gold_arg_cls, pred_arg_cls = [], []
    for pred, gold in zip(preds, golds):
        assert pred["doc_id"] == gold["doc_id"] and pred["wnd_id"] == gold["wnd_id"]
        assert pred["trigger"][0] == gold["trigger"][0]
        assert pred["trigger"][1] == gold["trigger"][1]
        assert pred["trigger"][2] == gold["trigger"][2]
        gold_arg_cls_ = [(gold["doc_id"], gold["wnd_id"], gold["trigger"][2], r[0], r[1], r[2]) for r in gold["arguments"]]
        pred_arg_cls_ = [(pred["doc_id"], pred["wnd_id"], pred["trigger"][2], r[0], r[1], r[2]) for r in pred["arguments"]]
        gold_arg_cls.extend(gold_arg_cls_)
        pred_arg_cls.extend(pred_arg_cls_)

    gold_arg_cls = set(gold_arg_cls)
    pred_arg_cls = set(pred_arg_cls)
    arg_cls_f1 = compute_f1(len(pred_arg_cls), len(gold_arg_cls), len(gold_arg_cls & pred_arg_cls))
    scores = {
        "pred_num": len(pred_arg_cls),
        "gold_num": len(gold_arg_cls),
        "match_num": len(gold_arg_cls & pred_arg_cls),
        "precision": arg_cls_f1[0],
        "recall": arg_cls_f1[1],
        "f1": arg_cls_f1[2],
    }
    return scores


def compute_EAE_argument_cls_score(preds, golds):
    gold_arg_cls, pred_arg_cls = [], []
    for pred, gold in zip(preds, golds):
        assert pred["doc_id"] == gold["doc_id"] and pred["wnd_id"] == gold["wnd_id"]
        assert pred["trigger"][0] == gold["trigger"][0]
        assert pred["trigger"][1] == gold["trigger"][1]
        assert pred["trigger"][2] == gold["trigger"][2]

        gold_arg_cls_ = [(gold["doc_id"], gold["wnd_id"], gold["trigger"][2], r[0], r[1], r[2]) for r in gold["arguments"]]
        pred_arg_cls_ = [(pred["doc_id"], pred["wnd_id"], pred["trigger"][2], r[0], r[1], r[2]) for r in pred["arguments"]]
        gold_arg_cls.extend(gold_arg_cls_)
        pred_arg_cls.extend(pred_arg_cls_)

    gold_arg_cls = set(gold_arg_cls)
    pred_arg_cls = set(pred_arg_cls)
    arg_cls_f1 = compute_f1(len(pred_arg_cls), len(gold_arg_cls), len(gold_arg_cls & pred_arg_cls))
    scores = {
        "pred_num": len(pred_arg_cls),
        "gold_num": len(gold_arg_cls),
        "match_num": len(gold_arg_cls & pred_arg_cls),
        "precision": arg_cls_f1[0],
        "recall": arg_cls_f1[1],
        "f1": arg_cls_f1[2],
    }
    return scores



def compute_EAE_argument_attached_id_score(preds, golds):
    gold_arg_id, pred_arg_id = [], []
    for pred, gold in zip(preds, golds):
        assert pred["doc_id"] == gold["doc_id"] and pred["wnd_id"] == gold["wnd_id"]
        assert pred["trigger"][0] == gold["trigger"][0]
        assert pred["trigger"][1] == gold["trigger"][1]
        assert pred["trigger"][2] == gold["trigger"][2]
        gold_arg_id_ = [(gold["doc_id"], gold["wnd_id"], gold["trigger"][0], gold["trigger"][1], gold["trigger"][2], r[0], r[1]) for r in gold["arguments"]]
        pred_arg_id_ = [(pred["doc_id"], pred["wnd_id"], pred["trigger"][0], pred["trigger"][1], pred["trigger"][2], r[0], r[1]) for r in pred["arguments"]]
        gold_arg_id.extend(gold_arg_id_)
        pred_arg_id.extend(pred_arg_id_)

    gold_arg_id = set(gold_arg_id)
    pred_arg_id = set(pred_arg_id)
    arg_id_f1 = compute_f1(len(pred_arg_id), len(gold_arg_id), len(gold_arg_id & pred_arg_id))
    scores = {
        "pred_num": len(pred_arg_id),
        "gold_num": len(gold_arg_id),
        "match_num": len(gold_arg_id & pred_arg_id),
        "precision": arg_id_f1[0],
        "recall": arg_id_f1[1],
        "f1": arg_id_f1[2],
    }
    return scores

def compute_EAE_argument_attached_cls_score(preds, golds):
    gold_arg_cls, pred_arg_cls = [], []
    for pred, gold in zip(preds, golds):
        assert pred["doc_id"] == gold["doc_id"] and pred["wnd_id"] == gold["wnd_id"]
        assert pred["trigger"][0] == gold["trigger"][0]
        assert pred["trigger"][1] == gold["trigger"][1]
        assert pred["trigger"][2] == gold["trigger"][2]
        gold_arg_cls_ = [(gold["doc_id"], gold["wnd_id"], gold["trigger"][0], gold["trigger"][1], gold["trigger"][2], r[0], r[1], r[2]) for r in gold["arguments"]]
        pred_arg_cls_ = [(pred["doc_id"], pred["wnd_id"], pred["trigger"][0], pred["trigger"][1], pred["trigger"][2], r[0], r[1], r[2]) for r in pred["arguments"]]
        gold_arg_cls.extend(gold_arg_cls_)
        pred_arg_cls.extend(pred_arg_cls_)

    gold_arg_cls = set(gold_arg_cls)
    pred_arg_cls = set(pred_arg_cls)
    arg_cls_f1 = compute_f1(len(pred_arg_cls), len(gold_arg_cls), len(gold_arg_cls & pred_arg_cls))
    scores = {
        "pred_num": len(pred_arg_cls),
        "gold_num": len(gold_arg_cls),
        "match_num": len(gold_arg_cls & pred_arg_cls),
        "precision": arg_cls_f1[0],
        "recall": arg_cls_f1[1],
        "f1": arg_cls_f1[2],
    }
    return scores

from pprint import pprint 
def compute_EAE_argument_cross_sent_cls_score(preds, golds):

    cross_sentence_scores = {}

    for distance in [-2,-1,0,1,2]:
    
      gold_arg_cls, pred_arg_cls = [], []
      for pred, gold in zip(preds, golds):
          pred, gold = deepcopy(pred), deepcopy(gold)
          assert pred["doc_id"] == gold["doc_id"] and pred["wnd_id"] == gold["wnd_id"]
          assert pred["trigger"][0] == gold["trigger"][0]
          assert pred["trigger"][1] == gold["trigger"][1]
          assert pred["trigger"][2] == gold["trigger"][2]

          trigger_start = gold['trigger'][0]
          trig_snt_loc = gold['token_snt_map'][trigger_start]

          gold_args = []
          for arg in gold['arguments']:
            arg_snt_loc = gold['token_snt_map'][arg[0]]
            if arg_snt_loc - trig_snt_loc == distance:    
              gold_args.append(arg)
              
          gold['arguments'] = gold_args
           

          pred_args = []
          for arg in pred['arguments']:
            arg_snt_loc = gold['token_snt_map'][arg[0]]
            if arg_snt_loc - trig_snt_loc == distance:
              pred_args.append(arg)
          pred['arguments'] = pred_args

          gold_arg_cls_ = [(gold["doc_id"], gold["wnd_id"], gold["trigger"][2], r[0], r[1], r[2]) for r in gold["arguments"]]
          pred_arg_cls_ = [(pred["doc_id"], pred["wnd_id"], pred["trigger"][2], r[0], r[1], r[2]) for r in pred["arguments"]]
          gold_arg_cls.extend(gold_arg_cls_)
          pred_arg_cls.extend(pred_arg_cls_)

      gold_arg_cls = set(gold_arg_cls)
      pred_arg_cls = set(pred_arg_cls)
      arg_cls_f1 = compute_f1(len(pred_arg_cls), len(gold_arg_cls), len(gold_arg_cls & pred_arg_cls))
      scores = {
          "pred_num": len(pred_arg_cls),
          "gold_num": len(gold_arg_cls),
          "match_num": len(gold_arg_cls & pred_arg_cls),
          "precision": arg_cls_f1[0],
          "recall": arg_cls_f1[1],
          "f1": arg_cls_f1[2],
      }

      cross_sentence_scores[distance] = scores

    return cross_sentence_scores


def safe_div(num, denom):
    return num / denom if denom > 0 else 0.0

def compute_f1(predicted, gold, matched):
    precision = safe_div(matched, predicted)
    recall = safe_div(matched, gold)
    f1 = safe_div(2 * precision * recall, precision + recall)
    return precision*100.0, recall*100.0, f1*100.0
