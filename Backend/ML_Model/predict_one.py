"""predict_one.py

Load saved models and thresholds, pick the model with best recall on a held-out split,
and expose a function/CLI to predict a single text (returns prediction and probability).

Usage:
    from predict_one import predict_text
    predict_text('some text')

Or via CLI:
    python3 predict_one.py "some text to classify"

"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from math import exp

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(HERE, 'models')
# merged train moved to data/processed during conservative reorganization
MERGED = os.path.join(HERE, 'data', 'processed', 'merged_train.csv')

# small helper: API-like regex to boost explainability
import re
RE_API = re.compile(r"\b(AKIA|AIza|sk_test_|sk_live_|ghp_|gho_|ghs_)[A-Za-z0-9_-]{4,}\b")
RE_IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")
RE_IPV6 = re.compile(r"\b([0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}\b", re.IGNORECASE)
RE_IP_CONTEXT = re.compile(r"(?i)\b(host|login|ssh|admin|root|server|db|database|prod|staging|credential|password)\b")
RE_BTC58 = re.compile(r"\b[13][1-9A-HJ-NP-Za-km-z]{25,34}\b")


def _load_artifacts(models_dir=MODELS_DIR):
    # Load artifacts defensively and return helpful errors when something can't be loaded.
    def load_pickle(p):
        if not os.path.exists(p):
            raise FileNotFoundError(f'Artifact not found: {p}')
        try:
            with open(p, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            raise RuntimeError(f'Failed to load pickle {p}: {e}')

    # Prefer unified final model if available
    final_pkl = os.path.join(models_dir, 'final_model.pkl')
    if os.path.exists(final_pkl):
        final_model = load_pickle(final_pkl)
        thr = {}
        thr_path = os.path.join(models_dir, 'thresholds.json')
        if os.path.exists(thr_path):
            try:
                with open(thr_path, 'r') as f:
                    thr = json.load(f)
            except Exception:
                thr = {}
        return ('final', final_model, thr)

    # Legacy multi-artifact path
    tfidf = load_pickle(os.path.join(models_dir, 'tfidf_model.pkl'))
    scaler = load_pickle(os.path.join(models_dir, 'scaler_model.pkl'))
    svm = load_pickle(os.path.join(models_dir, 'svm_model.pkl'))
    gb = load_pickle(os.path.join(models_dir, 'gb_model.pkl'))

    thr = {}
    thr_path = os.path.join(models_dir, 'thresholds.json')
    if os.path.exists(thr_path):
        try:
            with open(thr_path, 'r') as f:
                thr = json.load(f)
        except Exception:
            thr = {}
    return tfidf, scaler, svm, gb, thr


def _load_policy(models_dir=MODELS_DIR):
    pol_path = os.path.join(models_dir, 'policy.json')
    if os.path.exists(pol_path):
        try:
            with open(pol_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _sigmoid(x):
    # numerically stable sigmoid for scalars/ndarrays
    try:
        return 1.0 / (1.0 + np.exp(-x))
    except Exception:
        # fallback for Python floats
        return 1.0 / (1.0 + exp(-x))


def safe_predict_proba(clf, X):
    """Return an array of probabilities for the positive class when possible.
    Fallback order:
      - clf.predict_proba
      - clf.decision_function mapped through a sigmoid
      - None if neither available
    """
    if clf is None or X is None:
        return None
    try:
        if hasattr(clf, 'predict_proba'):
            probs = clf.predict_proba(X)
            # handle multiclass vs binary; expect second column
            if probs.ndim == 2 and probs.shape[1] >= 2:
                return probs[:, 1]
            # otherwise return flattened
            return probs.ravel()
        elif hasattr(clf, 'decision_function'):
            df = clf.decision_function(X)
            # decision_function may return shape (n,) or (n, k)
            # for binary classifiers it's usually (n,)
            if hasattr(df, 'ravel'):
                return _sigmoid(df).ravel()
            else:
                return _sigmoid(df)
        else:
            return None
    except Exception:
        return None


def validate_feature_shapes(clf, X):
    """Attempt to validate that X has the number of features the classifier expects.
    Returns tuple (ok:bool, message:str).
    """
    try:
        if hasattr(clf, 'n_features_in_'):
            expected = int(clf.n_features_in_)
            got = int(X.shape[1])
            if expected != got:
                return False, f'feature count mismatch: classifier expects {expected}, got {got}'
        return True, 'ok'
    except Exception as e:
        # Could not validate; return ok but include message
        return True, f'validation skipped: {e}'


def _prepare_features(texts, tfidf, scaler):
    X_tfidf = tfidf.transform(texts)
    # Use handcrafted features from legacy model pipeline
    from model import extract_handcrafted_df
    X_hand = extract_handcrafted_df(pd.Series(texts))
    X_hand_s = scaler.transform(X_hand)
    return hstack([X_tfidf, X_hand_s])


def pick_best_model(models_dir=MODELS_DIR, merged_path=MERGED, random_state=42):
    """Evaluate both saved models on an 80/20 held-out split and return the name of the model
    with higher recall on the positive (sensitive) class. Also return artifacts needed for prediction.
    """
    # If unified model exists, use it directly
    loaded = _load_artifacts(models_dir)
    if isinstance(loaded, tuple) and len(loaded) == 3 and loaded[0] == 'final':
        _, final_model, thr = loaded
        return 'final', (final_model, thr)

    tfidf, scaler, svm, gb, thr = loaded

    # load merged data and do same split
    if not os.path.exists(merged_path):
        # fallback: just return svm by default
        return 'svm', (tfidf, scaler, svm, thr)

    df = pd.read_csv(merged_path)
    X = df['text'].fillna("")
    y = df['label'].astype(int).values

    from sklearn.model_selection import train_test_split
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=random_state, stratify=y if len(np.unique(y))>1 else None)

    X_te_feat = _prepare_features(X_te.tolist(), tfidf, scaler)

    # get probs
    p_svm = svm.predict_proba(X_te_feat)[:,1] if hasattr(svm, 'predict_proba') else None
    p_gb = gb.predict_proba(X_te_feat.toarray() if hasattr(X_te_feat, 'toarray') else X_te_feat)[:,1]

    # default thresholds
    thr_svm = float(thr.get('svm', 0.5)) if thr else 0.5
    thr_gb = float(thr.get('gb', 0.5)) if thr else 0.5

    # predictions using thresholds
    if p_svm is not None:
        pred_svm = (p_svm >= thr_svm).astype(int)
    else:
        pred_svm = svm.predict(X_te_feat)
    pred_gb = (p_gb >= thr_gb).astype(int)

    from sklearn.metrics import recall_score
    rec_svm = recall_score(y_te, pred_svm, zero_division=0)
    rec_gb = recall_score(y_te, pred_gb, zero_division=0)

    # pick the one with higher positive recall; tie-breaker: higher mean prob
    if rec_gb > rec_svm:
        return 'gb', (tfidf, scaler, gb, thr)
    elif rec_svm > rec_gb:
        return 'svm', (tfidf, scaler, svm, thr)
    else:
        # tie-break using ROC AUC on probs if available
        from sklearn.metrics import roc_auc_score
        auc_svm = roc_auc_score(y_te, p_svm) if (p_svm is not None and len(np.unique(y_te))>1) else 0.0
        auc_gb = roc_auc_score(y_te, p_gb) if (p_gb is not None and len(np.unique(y_te))>1) else 0.0
        if auc_gb >= auc_svm:
            return 'gb', (tfidf, scaler, gb, thr)
        else:
            return 'svm', (tfidf, scaler, svm, thr)


def predict_text(text, models_dir=MODELS_DIR, threshold_override=None):
    """Predict a single text. Returns dict: {model, pred, prob, threshold, explanation}

    threshold_override: optional float in [0,1]. If provided, use this threshold instead of
    the stored model threshold for converting probabilities into binary predictions.
    """
    model_name, artifacts = pick_best_model(models_dir=models_dir)

    # Unified model path
    if model_name == 'final':
        final_model, thr = artifacts
        # direct pipeline transform
        prob = None
        try:
            prob = float(final_model.predict_proba([text])[:, 1][0])
        except Exception:
            try:
                df = final_model.decision_function([text])
                # convert to pseudo-probability via logistic
                prob = float(1.0 / (1.0 + np.exp(-df[0])))
            except Exception:
                prob = None

        threshold = 0.5
        if isinstance(thr, dict) and 'final' in thr:
            try:
                threshold = float(thr.get('final', 0.5))
            except Exception:
                threshold = 0.5
        if threshold_override is not None:
            try:
                threshold = float(threshold_override)
            except Exception:
                pass

        # Optional policy-based nudges (small probability adjustments)
        policy = _load_policy(models_dir)
        if prob is not None and policy:
            # IP adjustment: if require_context and text has IP but no context, nudge down
            if policy.get('ip', {}).get('require_context', False):
                if (RE_IPV4.search(text) or RE_IPV6.search(text)) and not RE_IP_CONTEXT.search(text):
                    # If force_non_sensitive_without_context is set, clamp prob to 0
                    if policy.get('ip', {}).get('force_non_sensitive_without_context', False):
                        prob = 0.0
                    else:
                        factor = float(policy.get('ip', {}).get('downscale_no_context_factor', 0.5))
                        prob = max(0.0, float(prob) * factor)
            # Bitcoin legacy boost if enabled
            if policy.get('bitcoin', {}).get('enable_legacy', False):
                if RE_BTC58.search(text):
                    boost = float(policy.get('bitcoin', {}).get('legacy_boost', 0.1))
                    prob = min(1.0, float(prob) + boost)
            # API key force sensitive if enabled
            if policy.get('api_key', {}).get('force_sensitive', False):
                if RE_API.search(text):
                    prob = 1.0

        pred = None
        if prob is not None:
            pred = int(prob >= threshold)
        else:
            pred = int(final_model.predict([text])[0])

        explanation = {
            'api_like_match': bool(RE_API.search(text)),
        }
        return {
            'model': model_name,
            'prediction': int(pred),
            'probability': float(prob) if prob is not None else None,
            'threshold': threshold,
            'explanation': explanation,
        }

    # Legacy multi-model path
    tfidf, scaler, clf, thr = artifacts
    X_feat = _prepare_features([text], tfidf, scaler)

    prob = None
    if hasattr(clf, 'predict_proba'):
        inp = X_feat.toarray() if hasattr(X_feat, 'toarray') else X_feat
        prob = clf.predict_proba(inp)[:,1][0]
    else:
        prob = float(clf.decision_function(X_feat)[0]) if hasattr(clf, 'decision_function') else None

    # determine threshold: priority -> threshold_override arg -> thresholds.json -> default 0.5
    threshold = 0.5
    if thr and model_name in thr:
        try:
            threshold = float(thr.get(model_name, 0.5))
        except Exception:
            threshold = 0.5
    if threshold_override is not None:
        try:
            threshold = float(threshold_override)
        except Exception:
            pass

    # Optional policy nudges for legacy path too (use original text)
    if prob is not None:
        policy = _load_policy(models_dir)
        if policy:
            t = text
            if policy.get('ip', {}).get('require_context', False):
                if (RE_IPV4.search(t) or RE_IPV6.search(t)) and not RE_IP_CONTEXT.search(t):
                    if policy.get('ip', {}).get('force_non_sensitive_without_context', False):
                        prob = 0.0
                    else:
                        factor = float(policy.get('ip', {}).get('downscale_no_context_factor', 0.5))
                        prob = max(0.0, float(prob) * factor)
            if policy.get('bitcoin', {}).get('enable_legacy', False):
                if RE_BTC58.search(t):
                    boost = float(policy.get('bitcoin', {}).get('legacy_boost', 0.1))
                    prob = min(1.0, float(prob) + boost)

    pred = int(prob >= threshold) if prob is not None else int(clf.predict(X_feat)[0])

    explanation = {
        'api_like_match': bool(RE_API.search(text)),
    }

    return {
        'model': model_name,
        'prediction': int(pred),
        'probability': float(prob) if prob is not None else None,
        'threshold': threshold,
        'explanation': explanation,
    }


def predict_boolean(text, models_dir=MODELS_DIR, threshold_override=None):
    """Return True/False for a single text prediction (True == sensitive)."""
    out = predict_text(text, models_dir=models_dir, threshold_override=threshold_override)
    return bool(int(out.get('prediction', 0)))


def predict_many(texts, models_dir=MODELS_DIR, threshold_override=None):
    """Predict a list of texts efficiently by loading the model once.

    Returns a list of dicts like predict_text.
    """
    if not texts:
        return []

    # Prefer unified model if available
    loaded = _load_artifacts(models_dir)
    results = []
    if isinstance(loaded, tuple) and len(loaded) == 3 and loaded[0] == 'final':
        _, final_model, thr = loaded
        # Compute probabilities vectorized when possible
        prob = None
        try:
            prob = final_model.predict_proba(texts)[:, 1]
        except Exception:
            try:
                df = final_model.decision_function(texts)
                prob = _sigmoid(df)
            except Exception:
                prob = None
        threshold = 0.5
        if isinstance(thr, dict) and 'final' in thr:
            try:
                threshold = float(thr.get('final', 0.5))
            except Exception:
                threshold = 0.5
        if threshold_override is not None:
            try:
                threshold = float(threshold_override)
            except Exception:
                pass
        # Apply policy adjustments per text when probabilities are available
        policy = _load_policy(models_dir)
        adjusted_probs = []
        for i, t in enumerate(texts):
            p = float(prob[i]) if prob is not None else None
            if p is not None and policy:
                if policy.get('ip', {}).get('require_context', False):
                    if (RE_IPV4.search(t) or RE_IPV6.search(t)) and not RE_IP_CONTEXT.search(t):
                        if policy.get('ip', {}).get('force_non_sensitive_without_context', False):
                            p = 0.0
                        else:
                            factor = float(policy.get('ip', {}).get('downscale_no_context_factor', 0.5))
                            p = max(0.0, float(p) * factor)
                if policy.get('bitcoin', {}).get('enable_legacy', False):
                    if RE_BTC58.search(t):
                        boost = float(policy.get('bitcoin', {}).get('legacy_boost', 0.1))
                        p = min(1.0, float(p) + boost)
            adjusted_probs.append(p)
        for i, t in enumerate(texts):
            p = adjusted_probs[i] if prob is not None else None
            pred = int(p >= threshold) if p is not None else int(final_model.predict([t])[0])
            results.append({
                'model': 'final',
                'prediction': pred,
                'probability': p,
                'threshold': threshold,
                'explanation': {
                    'api_like_match': bool(RE_API.search(t)),
                },
            })
        return results

    # Legacy model path (load once)
    tfidf, scaler, clf, thr = loaded
    X_feat = _prepare_features(texts, tfidf, scaler)
    if hasattr(clf, 'predict_proba'):
        inp = X_feat.toarray() if hasattr(X_feat, 'toarray') else X_feat
        probs = clf.predict_proba(inp)[:, 1]
    elif hasattr(clf, 'decision_function'):
        probs = _sigmoid(clf.decision_function(X_feat))
    else:
        probs = None

    model_name, _ = pick_best_model(models_dir=models_dir)
    threshold = 0.5
    if thr and model_name in thr:
        try:
            threshold = float(thr.get(model_name, 0.5))
        except Exception:
            threshold = 0.5
    if threshold_override is not None:
        try:
            threshold = float(threshold_override)
        except Exception:
            pass

    if probs is None:
        preds = clf.predict(X_feat)
        for t, pr in zip(texts, preds):
            results.append({
                'model': model_name,
                'prediction': int(pr),
                'probability': None,
                'threshold': threshold,
                'explanation': {
                    'api_like_match': bool(RE_API.search(t)),
                },
            })
    else:
        for t, p in zip(texts, probs):
            pred = int(p >= threshold)
            results.append({
                'model': model_name,
                'prediction': pred,
                'probability': float(p),
                'threshold': threshold,
                'explanation': {
                    'api_like_match': bool(RE_API.search(t)),
                },
            })
    return results


if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description='Predict whether text is sensitive')
    parser.add_argument('text', type=str, nargs='*', help='one or more texts to classify (wrap each in quotes)')
    parser.add_argument('--file', type=str, help='path to a file with one input per line')
    parser.add_argument('--stdin', action='store_true', help='read inputs from stdin, one per line')
    parser.add_argument('--boolean', action='store_true', help='print only boolean true/false (one per line if multiple inputs)')
    parser.add_argument('--json', action='store_true', help='print JSON object/array instead of Python dict')
    parser.add_argument('--threshold', type=float, help='optional override probability threshold (0-1)')
    args = parser.parse_args()
    try:
        inputs = []
        if args.file:
            with open(args.file, 'r') as f:
                inputs.extend([ln.rstrip('\n') for ln in f])
        if args.stdin:
            inputs.extend([ln.rstrip('\n') for ln in sys.stdin])
        if args.text:
            inputs.extend(args.text)

        if not inputs:
            raise SystemExit('No input provided. Pass text arguments, --file, or --stdin.')

        # Single vs multiple
        if len(inputs) == 1:
            out = predict_text(inputs[0], threshold_override=args.threshold)
            if args.boolean:
                print('true' if int(out.get('prediction', 0)) else 'false')
            elif args.json:
                print(json.dumps(out))
            else:
                print(out)
        else:
            outs = predict_many(inputs, threshold_override=args.threshold)
            if args.boolean:
                for o in outs:
                    print('true' if int(o.get('prediction', 0)) else 'false')
            elif args.json:
                print(json.dumps(outs))
            else:
                for o in outs:
                    print(o)
    except Exception as e:
        err = {'error': str(e)}
        try:
            print(json.dumps(err))
        except Exception:
            print(str(err))
        raise SystemExit(1)
