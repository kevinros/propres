def compute_utility_metrics(ground_truths, predictions, t=2):
    
    """
    
    ground_truths is list of (timestep, doc_id) pairs
    predictions is a list of (timestep, doc_id) pairs
    note that for both ground_truths and predictions, multiple entries can have the same timestep
    
    want to measure
    
    Precision --> TP / TP + FP
    Recall --> TP / TP + FN
    Delay --> how long until first correct prediction? relative to t
    No predictions --> 1 if there are no predictions made in window, 0 otherwise (over all ground truths)
    
    No ground truth --> 1 if no match, 0 otherwise (over all predictions)
    
    TurbulenceFreq --> avg number of prediction switches (over everything)
    TurbulenceTime --> avg but over time delta of all predictions
    TurbulenceInterval --> avg of how much time between switches
    
    """

    
    # first compress gts into same idx
    gt_alignment_by_time = {}
    for gt in ground_truths:
        if gt[0] not in gt_alignment_by_time:
            gt_alignment_by_time[gt[0]] = {"ground_truths": [gt[1]], "predictions": []}
        else:
            if gt[1] not in gt_alignment_by_time[gt[0]]["ground_truths"]:
                gt_alignment_by_time[gt[0]]["ground_truths"].append(gt[1])
    
    # assign predictions to each GT time
    gt_time_list = sorted(list(gt_alignment_by_time.keys()))
    no_ground_truths = []
    
    


    for pred in predictions:
        pred_time = pred[0]
        is_matched = False
        for i,gt_time in enumerate(gt_time_list):
            delta = pred_time - gt_time
            
             # ignore any predictions made right before ground truth but within t
             # only forward-looking
            if delta <= t and delta >= 0:
                if "predictions" not in gt_alignment_by_time[gt_time]:
                    gt_alignment_by_time[gt_time]["predictions"] = [pred]
                else:
                    gt_alignment_by_time[gt_time]["predictions"].append(pred)
                is_matched = True
        if not is_matched:
             no_ground_truths.append(pred[1])
    

    window_metrics = {}
    for i, gt_time in enumerate(gt_time_list):
        window_metrics[gt_time] = {
            "Precision (+)": 0,
            "Recall (+)": 0,
            "Delay (-)": -1,
            "No Predictions (-)": 0
        }
        
        tp = []
        fp = []
        fn = []
        
        
        if len(gt_alignment_by_time[gt_time]["predictions"]) == 0:
            window_metrics[gt_time]["No Predictions (-)"] = 1
        
        # first calculate delay
        unique_pred_dids = set()
        for pred in gt_alignment_by_time[gt_time]["predictions"]:
            pred_did = pred[1]
            unique_pred_dids.add(pred_did)
            pred_time = pred[0]
            if pred_did in gt_alignment_by_time[gt_time]["ground_truths"]:
                if window_metrics[gt_time]["Delay (-)"] == -1:
                    window_metrics[gt_time]["Delay (-)"] = (pred_time - gt_time) / max(1,t)
                else:
                    window_metrics[gt_time]["Delay (-)"] = (min(pred_time - gt_time, window_metrics[gt_time]["Delay (-)"])) / max(1,t)
                    
        # second, calculate tps and fps (need unique result list)
        for pred_did in unique_pred_dids:
            if pred_did in gt_alignment_by_time[gt_time]["ground_truths"]:
                tp.append(pred_did)
            else:
                fp.append(pred_did)

        for gt in gt_alignment_by_time[gt_time]["ground_truths"]:
            if gt not in unique_pred_dids:
                fn.append(gt)

        precision = 0 if len(tp) == 0 else len(tp)/(len(tp) + len(fp))
        recall = 0 if len(tp) == 0 else len(tp) / (len(tp) + len(fn))

        window_metrics[gt_time]["Precision (+)"] = precision
        window_metrics[gt_time]["Recall (+)"] = recall
        

    sorted_predictions = {}
    for pred in predictions:
        timestep = pred[0]
        doc_id = pred[1]
        if timestep not in sorted_predictions:
            sorted_predictions[timestep] = []
        sorted_predictions[timestep].append(doc_id)
    sorted_predictions = sorted([(timestep, sorted_predictions[timestep]) for timestep in sorted_predictions], key=lambda x: x[0])
    turb_points = []
    turb_delta = []
    for i in range(1, len(sorted_predictions)):
        cur_pred = set(sorted_predictions[i][1])
        prev_pred = set(sorted_predictions[i-1][1])
        if cur_pred != prev_pred:
            turb_points.append(i)
            turb_delta.append(sorted_predictions[i][0] - sorted_predictions[i-1][0])
    turb_freq = 0 if len(sorted_predictions) == 0 else len(turb_points) / len(sorted_predictions)
    

    if len(sorted_predictions) == 0 or (sorted_predictions[-1][0] - sorted_predictions[0][0]) == 0:
        turb_time = 0
    else:
        turb_time = len(turb_points) / (sorted_predictions[-1][0] - sorted_predictions[0][0])
        
    turb_int = 0 if len(turb_points) == 0 else (1 / len(turb_points)) * sum(turb_delta)
        
    metrics = {
        "No Ground Truths (-)": 0 if len(predictions) == 0 else len(no_ground_truths) / len(predictions),
        "Turbulence Frequency (-)": turb_freq,
        "Turbulence Time (-)": turb_time,
        "Turbulence Interval (-)": turb_int
    }
    
    in_window_keys = ["Precision (+)", "Recall (+)", "Delay (-)", "No Predictions (-)"]
    for key in in_window_keys:
        metrics[key] = []
    for gt_time in window_metrics:
        for key in in_window_keys:
            if not isinstance(window_metrics[gt_time][key], str):
                metrics[key].append(window_metrics[gt_time][key])
    for key in in_window_keys:
        metrics[key] = 0 if len(metrics[key]) == 0 else sum(metrics[key]) / len(metrics[key])
        
    return metrics 