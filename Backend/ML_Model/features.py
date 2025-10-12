"""Shared feature extraction utilities for the sensitive-info classifier.

Defines HandcraftedFeatures used inside the unified sklearn Pipeline.
Keeping it in a top-level module ensures pickled pipelines can be reloaded.
"""
from __future__ import annotations

import re
import math
from collections import Counter
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

RE_HAS_EMAIL = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
RE_HAS_URL = re.compile(r"https?://|www\.")
RE_API_PRE = re.compile(r"\b(AKIA|AIza|sk_test_|sk_live_|ghp_|gho_|ghs_)[A-Za-z0-9_-]{4,}\b")
RE_HEX = re.compile(r"\b[0-9a-fA-F]{8,}\b")
RE_PASS_KW = re.compile(r"(?i)\b(pass(word|wd)?|pwd|passwd)\b")
RE_SECRET_KW = re.compile(r"(?i)\b(secret|token|api[_-]?key|bearer)\b")
RE_CRED_KV = re.compile(r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key)\s*[:=]")
RE_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-~+/=]{10,}")
RE_JWT = re.compile(r"\beyJ[\w-]+\.[\w-]+\.[\w-]+\b")
RE_PEM = re.compile(r"-----BEGIN (?:RSA |EC |)PRIVATE KEY-----|-----BEGIN CERTIFICATE-----")
RE_BTC_BASE58 = re.compile(r"\b[13][1-9A-HJ-NP-Za-km-z]{25,34}\b")
RE_BTC_BECH32 = re.compile(r"\bbc1[ac-hj-np-z02-9]{11,71}\b")
RE_ETH_ADDR = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
RE_IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")
RE_IPV6 = re.compile(r"\b([0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}\b", re.IGNORECASE)
RE_IP_CONTEXT = re.compile(r"(?i)\b(host|login|ssh|admin|root|server|db|database|prod|staging|credential|password)\b")
RE_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
RE_DOB = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
RE_ROUTING = re.compile(r"(?i)\b(?:routing|aba|rtg)\s*(?:number|num|#)?\s*[:\-]?\s*\d{9}\b|\b\d{9}\b(?=\s*(?:routing|aba|rtg))")
RE_IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
RE_SWIFT = re.compile(r"(?i)\b(?:swift|bic)\s*(?:code)?\s*[:\-]?\s*[A-Z]{6}[A-Z0-9]{2,5}\b|\b[A-Z]{6}[A-Z0-9]{2,5}\b(?=\s*(?:swift|bic))")
RE_CC = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b")
RE_FINANCIAL_KW = re.compile(r"(?i)\b(account|card|credit|debit|bank|wire|transfer|payment|balance|deposit|withdraw)\b")
RE_SENSITIVE_KV = re.compile(r"(?i)\b(?:password|passwd|pwd|secret|token|key|api|auth|bearer|jwt|ssn|dob|passport|license|id)\s*[:=]\s*\S+")


def _char_entropy(s: str) -> float:
    if not isinstance(s, str) or not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    if length == 0:
        return 0.0
    probs = [c / length for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def _word_entropy(s: str) -> float:
    if not isinstance(s, str) or not s:
        return 0.0
    words = re.findall(r'\b\w+\b', s.lower())
    if not words:
        return 0.0
    counts = Counter(words)
    length = len(words)
    probs = [c / length for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def _key_value_score(s: str) -> float:
    if not isinstance(s, str) or not s:
        return 0.0
    # Count key=value or key: value patterns
    kv_matches = re.findall(r'\b\w+\s*[:=]\s*\S+', s)
    return min(1.0, len(kv_matches) / max(1, len(s.split())))


class HandcraftedFeatures(BaseEstimator, TransformerMixin):
    """Transform a sequence of texts into a rich numeric feature matrix.

        Output columns:
            [len, num_digits, digit_ratio, has_email, has_url, api_like, has_hex, char_entropy, word_entropy,
             has_password_kw, has_secret_kw, has_cred_kv, key_value_score, charset_mix,
             has_bearer, has_jwt, has_pem, has_btc58, has_btc32, has_eth, has_ipv4, has_ipv6, ip_context,
             has_ssn, has_dob, has_routing, has_iban, has_swift, has_cc, has_financial_kw, has_sensitive_kv]
    """

    def fit(self, X: Iterable[str], y=None):
        return self

    def transform(self, X: Iterable[str]):
        texts = pd.Series(list(X)).fillna("")
        L = texts.str.len().tolist()
        num_digits = [sum(1 for ch in t if ch.isdigit()) for t in texts]
        digit_ratio = [d / max(1, l) for d, l in zip(num_digits, L)]
        has_email = [int(bool(RE_HAS_EMAIL.search(t))) for t in texts]
        has_url = [int(bool(RE_HAS_URL.search(t))) for t in texts]
        api_like = [int(bool(RE_API_PRE.search(t))) for t in texts]
        has_hex = [int(bool(RE_HEX.search(t))) for t in texts]
        char_ent = [_char_entropy(t) for t in texts]
        word_ent = [_word_entropy(t) for t in texts]
        has_password_kw = [int(bool(RE_PASS_KW.search(t))) for t in texts]
        has_secret_kw = [int(bool(RE_SECRET_KW.search(t))) for t in texts]
        has_cred_kv = [int(bool(RE_CRED_KV.search(t))) for t in texts]
        kv_score = [_key_value_score(t) for t in texts]

        # Character class mix heuristic: 0..1 score for diversity of classes
        def mix_score(t: str) -> float:
            if not t:
                return 0.0
            u = any(c.isupper() for c in t)
            l = any(c.islower() for c in t)
            d = any(c.isdigit() for c in t)
            s = any((not c.isalnum()) for c in t)
            return (u + l + d + s) / 4.0

        charset_mix = [mix_score(t) for t in texts]
        has_bearer = [int(bool(RE_BEARER.search(t))) for t in texts]
        has_jwt = [int(bool(RE_JWT.search(t))) for t in texts]
        has_pem = [int(bool(RE_PEM.search(t))) for t in texts]
        has_btc58 = [int(bool(RE_BTC_BASE58.search(t))) for t in texts]
        has_btc32 = [int(bool(RE_BTC_BECH32.search(t))) for t in texts]
        has_eth = [int(bool(RE_ETH_ADDR.search(t))) for t in texts]
        has_ipv4 = [int(bool(RE_IPV4.search(t))) for t in texts]
        has_ipv6 = [int(bool(RE_IPV6.search(t))) for t in texts]
        ip_context = [int(bool(RE_IP_CONTEXT.search(t))) for t in texts]
        has_ssn = [int(bool(RE_SSN.search(t))) for t in texts]
        has_dob = [int(bool(RE_DOB.search(t))) for t in texts]
        has_routing = [int(bool(RE_ROUTING.search(t))) for t in texts]
        has_iban = [int(bool(RE_IBAN.search(t))) for t in texts]
        has_swift = [int(bool(RE_SWIFT.search(t))) for t in texts]
        has_cc = [int(bool(RE_CC.search(t))) for t in texts]
        has_financial_kw = [int(bool(RE_FINANCIAL_KW.search(t))) for t in texts]
        has_sensitive_kv = [int(bool(RE_SENSITIVE_KV.search(t))) for t in texts]

        M = np.column_stack([
            L,
            num_digits,
            digit_ratio,
            has_email,
            has_url,
            api_like,
            has_hex,
            char_ent,
            word_ent,
            has_password_kw,
            has_secret_kw,
            has_cred_kv,
            kv_score,
            charset_mix,
            has_bearer,
            has_jwt,
            has_pem,
            has_btc58,
            has_btc32,
            has_eth,
            has_ipv4,
            has_ipv6,
            ip_context,
            has_ssn,
            has_dob,
            has_routing,
            has_iban,
            has_swift,
            has_cc,
            has_financial_kw,
            has_sensitive_kv,
        ]).astype(float)
        return M
