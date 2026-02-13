import math

def compute_ndcg(predictions, targets):
    # i + 2 because the range starts at 0, but we need it to start at 1
    dcg = 0
    for i in range(len(predictions)):
        pred_did = predictions[i]
        if pred_did in targets:
            dcg += 1/math.log(i+2, 2)
    
    idcg = 0
    for i in range(len(targets)):
        idcg += 1/math.log(i+2, 2)
    
    ndcg = dcg / idcg
    return ndcg



def compute_discovery_metrics(ground_truths, predictions, start_did, end_did, perspective="forward"):
    """
    ground_truths: list of (transcript_idx, doc_id) pairs
    predictions: list of (transcript_idx, [(doc_id, score), (doc_id, score) ...]) pairs

    perspective
        bidirectional - consider time window on both sides of gt
        forward - consider time window at or after gt
        backward - consider time window at or before gt
    """

    # first compress gts into same idx
    gt_alignment_by_time = {}
    for gt in ground_truths:
        if gt[0] not in gt_alignment_by_time:
            gt_alignment_by_time[gt[0]] = [gt[1]]
        else:
            gt_alignment_by_time[gt[0]].append(gt[1])

    
    ### Recall@K within T - T defines the "time" window around a ground truth
    ###				 		K is number of results, all sorted by score

    ### MRR@K within T     same as above

    ### nDCG@K within T - same as above

    ### PaperPrecision@K within T - how many predictions are in the correct paper

    recall = {}
    paper_precision = {}
    mrr = {}
    ndcg = {}

    for t in [0, 10, 30]:
        recall[t] = {}
        paper_precision[t] = {}
        mrr[t] = {}
        ndcg[t] = {}
        for k in [10,50,100]:
            recall[t][k] = []
            paper_precision[t][k] = []
            mrr[t][k] = []
            ndcg[t][k] = []
        for timestep in gt_alignment_by_time:
            timestep_gt_dids = gt_alignment_by_time[timestep]
            pred_dids = {}
            for pred in predictions:
                pred_time = pred[0]
                pred_docs = pred[1]

                include = False
                if perspective == "bidirectional":
                    include = abs(pred_time - timestep) <= t
                elif perspective == "forward":
                    include = pred_time >= timestep and (pred_time - timestep) <= t
                elif perspective == "backward":
                    include = pred_time <= timestep and (timestep - pred_time) <= t

                if include:
                    for pred_did in pred_docs:
                        if pred_did[0] not in pred_dids:
                            pred_dids[pred_did[0]] = pred_did[1]
                        else:
                            pred_dids[pred_did[0]] = max(pred_did[1], pred_dids[pred_did[0]]) # take highest score
            pred_dids = [(x, pred_dids[x]) for x in pred_dids]
            pred_dids = sorted(pred_dids, reverse=True, key=lambda x: x[1])
            pred_dids = [x[0] for x in pred_dids]

            for k in [10,50,100]:
                pred_dids_cutoff = pred_dids[:k]
                recall_k_t_timestep = 0
                paper_recall_k_t_timestep = 0


                # get the recall, but so that it is averaged over all gt at timestep
                for gt_did in timestep_gt_dids:
                    if gt_did in pred_dids_cutoff:
                        recall_k_t_timestep += 1
                
                
                # going to be slightly different than wandb because we compute this averaged over all GT
                for gt_did in timestep_gt_dids:
                    rank = 0
                    for i,pred_did in enumerate(pred_dids_cutoff):
                        if pred_did == gt_did:
                            rank = 1 / (i+1)
                            break
                    mrr[t][k].append((timestep, rank))


                # compute ndcg
                ndcg[t][k].append((timestep, compute_ndcg(pred_dids_cutoff, timestep_gt_dids)))
                        
                for pred_did in pred_dids_cutoff:
                    if pred_did >= start_did and pred_did <= end_did:
                        paper_recall_k_t_timestep += 1



                recall_k_t_timestep = 0 if len(timestep_gt_dids) == 0 else recall_k_t_timestep / min(k, len(timestep_gt_dids))
                paper_recall_k_t_timestep = 0 if len(timestep_gt_dids) == 0 else paper_recall_k_t_timestep / k
                recall[t][k].append((timestep, recall_k_t_timestep))
                paper_precision[t][k].append((timestep, paper_recall_k_t_timestep))

                

    return recall, paper_precision, mrr, ndcg