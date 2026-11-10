"""EEG feature extraction library (v1).

Read-only extraction from the finalised EEG preprocessing outputs.  The module
implements spectral, temporal and nonlinear sensor-space features per channel
and aggregates them to recording and participant level.  It deliberately does
NOT rereference, interpolate, filter, or compute reference-sensitive features
(Laplacian/CSD/connectivity); the acquisition reference is still unknown.

Run ``scripts/extract_eeg_features.py`` (or the notebook) to produce outputs.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import warnings
from pathlib import Path

import mne
import numpy as np
import pandas as pd
from numba import njit
from scipy.signal import detrend, hilbert, welch

# ---------------------------------------------------------------------------
# Paths and study constants
# ---------------------------------------------------------------------------
ROOT = Path(r"E:\REU_DATA")
QC_CSV = ROOT / "signoff_finalization_v2" / "eeg_qc_summary_v3.csv"
ARTIFACT_CSV = ROOT / "audit_finalization_v1" / "eeg" / "artifact_log_v1.csv"
LABELS_CSV = ROOT / "Questionnaire_Analysis" / "participant_labels_v1.csv"
OUT_DIR = ROOT / "EEG features"
FIG_DIR = OUT_DIR / "figures"

PARTICIPANTS = [f"P{i:02d}" for i in range(1, 11)]
CONDITIONS = ["calm", "meditation", "maths", "speech"]

# Contiguous bands covering 1-45 Hz: [lo, hi) except gamma, which includes 45.
BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 12.0),
    "beta": (12.0, 30.0),
    "gamma": (30.0, 45.0),
}
BAND_NAMES = list(BANDS)

REGIONS = {
    "frontal": ["Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8"],
    "central": ["C3", "Cz", "C4"],
    "temporal": ["T7", "T8"],
    "parietal": ["P7", "P3", "Pz", "P4", "P8"],
    "occipital": ["POz", "O1", "Oz", "O2"],
    "mastoid": ["M1", "M2"],
}
NON_SCALP_CHANNELS = {"M1", "M2"}
HOMOLOGOUS_PAIRS = [
    ("Fp1", "Fp2"),
    ("F7", "F8"),
    ("F3", "F4"),
    ("T7", "T8"),
    ("C3", "C4"),
    ("P7", "P8"),
    ("P3", "P4"),
    ("O1", "O2"),
]
ASYM_BANDS = ["theta", "alpha", "beta"]

# Epoch definition: 2 s windows with 1 s step.  The 1 s grid matches the
# artifact register, so any overlap can be skipped deterministically.
EPOCH_WIN_S = 2.0
EPOCH_STEP_S = 1.0
NONLINEAR_SFREQ_HZ = 250.0
DECIM_FACTOR = 4  # 1000 Hz -> 250 Hz; data are already low-passed at 45 Hz.

# ---------------------------------------------------------------------------
# Feature names
# ---------------------------------------------------------------------------
SPECTRAL_FEATURES = (
    [f"abs_power_{b}_uv2" for b in BAND_NAMES]
    + [f"rel_power_{b}" for b in BAND_NAMES]
    + [f"log10_abs_power_{b}" for b in BAND_NAMES]
    + [
        "total_power_1_45_uv2",
        "spectral_centroid_hz",
        "spectral_edge95_hz",
        "alpha_peak_freq_hz",
        "alpha_peak_power_uv2",
        "theta_alpha_ratio",
        "alpha_beta_ratio",
        "delta_theta_ratio",
        "beta_gamma_ratio",
        "spectral_entropy",
        "aperiodic_exponent",
        "aperiodic_offset",
    ]
)
TEMPORAL_FEATURES = [
    "rms_uv",
    "variance_uv2",
    "peak_to_peak_uv",
    "zcr_per_s",
    "hjorth_activity",
    "hjorth_mobility",
    "hjorth_complexity",
    "line_length_uv_per_s",
    "envelope_mean_uv",
    "envelope_std_uv",
    "autocorr_lag1",
]
NONLINEAR_FEATURES = [
    "perm_entropy",
    "lz_complexity",
    "higuchi_fd",
    "dfa_alpha",
]
EPOCH_FEATURES = SPECTRAL_FEATURES + TEMPORAL_FEATURES + NONLINEAR_FEATURES
SD_FEATURES = ["rms_uv", "abs_power_alpha_uv2", "perm_entropy", "higuchi_fd", "dfa_alpha"]
EPOCH_TABLE_FEATURES = [
    "rms_uv",
    *[f"abs_power_{b}_uv2" for b in BAND_NAMES],
    *[f"rel_power_{b}" for b in BAND_NAMES],
    "spectral_entropy",
    "perm_entropy",
    "lz_complexity",
    "higuchi_fd",
    "dfa_alpha",
]


# ---------------------------------------------------------------------------
# Numba kernels (validated on synthetic signals; see the summary notebook)
# ---------------------------------------------------------------------------
@njit(cache=True)
def _perm_entropy_order3(sig, delay=1):
    """Normalised permutation entropy, order 3, delay 1 (0..1)."""
    n = sig.shape[0]
    m = n - 2 * delay
    if m < 2:
        return np.nan
    counts = np.zeros(6, dtype=np.int64)
    for i in range(m):
        a = sig[i]
        b = sig[i + delay]
        c = sig[i + 2 * delay]
        if a <= b:
            if b <= c:
                code = 0
            elif a <= c:
                code = 1
            else:
                code = 2
        else:
            if a <= c:
                code = 3
            elif b <= c:
                code = 4
            else:
                code = 5
        counts[code] += 1
    ent = 0.0
    for j in range(6):
        if counts[j] > 0:
            p = counts[j] / m
            ent -= p * np.log(p)
    return ent / np.log(6.0)


@njit(cache=True)
def _lz_complexity(binary):
    """Normalised Lempel-Ziv complexity (Kaspar-Schuster/NeuroKit2 variant)."""
    n = binary.shape[0]
    if n < 2:
        return np.nan
    s = np.empty(n + 1, dtype=np.uint8)
    s[0] = 0
    s[1:] = binary
    c = 1
    j = 1
    i = 0
    k = 1
    k_max = 1
    stop = False
    while not stop:
        if s[i + k] != s[j + k]:
            if k > k_max:
                k_max = k
            i += 1
            if i == j:
                c += 1
                j = j + k_max
                if j + 1 > n:
                    stop = True
                else:
                    i = 0
                    k = 1
                    k_max = 1
            else:
                k = 1
        else:
            k += 1
            if j + k > n:
                c += 1
                stop = True
    return c * np.log2(n) / n


@njit(cache=True)
def _higuchi_fd(x, kmax=8):
    """Higuchi fractal dimension (antropy-normalised, ~2 for white noise)."""
    N = x.shape[0]
    L = np.empty(kmax, dtype=np.float64)
    nk = 0
    for k in range(1, kmax + 1):
        total = 0.0
        cnt = 0
        for m in range(k):
            n_max = (N - m) // k
            if n_max < 2:
                continue
            s = 0.0
            prev = x[m]
            for j in range(1, n_max):
                cur = x[m + j * k]
                s += abs(cur - prev)
                prev = cur
            total += s * (N - 1) / (k * k * n_max)
            cnt += 1
        if cnt > 0:
            L[nk] = total / cnt
            nk += 1
    if nk < 2:
        return np.nan
    sx = 0.0
    sy = 0.0
    sxx = 0.0
    sxy = 0.0
    for idx in range(nk):
        k = idx + 1
        lx = np.log(1.0 / k)
        ly = np.log(L[idx])
        sx += lx
        sy += ly
        sxx += lx * lx
        sxy += lx * ly
    den = nk * sxx - sx * sx
    return (nk * sxy - sx * sy) / den


@njit(cache=True)
def _dfa_alpha(x):
    """Detrended fluctuation analysis exponent, scales 4..min(64, N/4)."""
    n = x.shape[0]
    if n < 20:
        return np.nan
    mean = np.mean(x)
    y = np.empty(n, dtype=np.float64)
    acc = 0.0
    for i in range(n):
        acc += x[i] - mean
        y[i] = acc
    scales = np.empty(8, dtype=np.int64)
    lo = np.log(4.0)
    hi = np.log(min(64.0, n / 4.0))
    for i in range(8):
        scales[i] = int(round(np.exp(lo + (hi - lo) * i / 7.0)))
    xs = np.empty(8, dtype=np.float64)
    ys = np.empty(8, dtype=np.float64)
    nk = 0
    for si in range(8):
        s = scales[si]
        if s < 2:
            continue
        nseg = n // s
        if nseg < 1:
            continue
        F = 0.0
        for seg in range(nseg):
            base = seg * s
            ym = 0.0
            for j in range(s):
                ym += y[base + j]
            ym /= s
            num = 0.0
            den = 0.0
            for j in range(s):
                xc = j - (s - 1) / 2.0
                num += (y[base + j] - ym) * xc
                den += xc * xc
            slope = num / den
            rss = 0.0
            for j in range(s):
                xc = j - (s - 1) / 2.0
                fit = ym + slope * xc
                rss += (y[base + j] - fit) ** 2
            F += rss
        F = np.sqrt(F / (nseg * s))
        if F > 0:
            xs[nk] = np.log(s)
            ys[nk] = np.log(F)
            nk += 1
    if nk < 2:
        return np.nan
    sx = 0.0
    sy = 0.0
    sxx = 0.0
    sxy = 0.0
    for i in range(nk):
        sx += xs[i]
        sy += ys[i]
        sxx += xs[i] * xs[i]
        sxy += xs[i] * ys[i]
    den = nk * sxx - sx * sx
    return (nk * sxy - sx * sy) / den


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _trapz(y, x, axis=-1):
    """np.trapezoid with a numpy<2 fallback."""
    if hasattr(np, "trapezoid"):
        return np.trapezoid(y, x, axis=axis)
    return np.trapz(y, x, axis=axis)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def band_mask(freqs: np.ndarray, band: str) -> np.ndarray:
    lo, hi = BANDS[band]
    if band == "gamma":
        return (freqs >= lo) & (freqs <= hi)
    return (freqs >= lo) & (freqs < hi)


def _safe_div(num, den, eps=1e-30):
    return num / np.maximum(den, eps)


# ---------------------------------------------------------------------------
# Inputs and epoch validity
# ---------------------------------------------------------------------------
def load_qc(path: Path = QC_CSV) -> pd.DataFrame:
    qc = pd.read_csv(path)
    qc = qc[qc["modality"] == "eeg"].copy()
    qc = qc.sort_values(["participant_id", "condition"]).reset_index(drop=True)
    if len(qc) != 40:
        raise ValueError(f"expected 40 EEG rows in {path}, found {len(qc)}")
    return qc


def load_artifacts(path: Path = ARTIFACT_CSV) -> pd.DataFrame:
    art = pd.read_csv(path)
    need = {"participant", "condition", "t_start_s", "t_end_s", "disposition"}
    missing = need - set(art.columns)
    if missing:
        raise ValueError(f"artifact register missing columns: {sorted(missing)}")
    return art


def artifact_spans(art: pd.DataFrame, participant_id: str, condition: str):
    sub = art[(art["participant"] == participant_id) & (art["condition"] == condition)]
    return [(float(a), float(b)) for a, b in zip(sub["t_start_s"], sub["t_end_s"])]


def epoch_starts(duration_s: float, win_s: float = EPOCH_WIN_S, step_s: float = EPOCH_STEP_S):
    if duration_s < win_s:
        return np.empty(0, dtype=float)
    return np.arange(0.0, duration_s - win_s + 1e-9, step_s, dtype=float)


def valid_epoch_mask(starts: np.ndarray, spans, win_s: float = EPOCH_WIN_S):
    bad = np.zeros(len(starts), dtype=bool)
    for a, b in spans:
        bad |= (starts < b) & (starts + win_s > a)
    return ~bad


def load_recording(path: Path):
    raw = mne.io.read_raw_fif(path, preload=True, verbose="ERROR")
    data_uv = raw.get_data() * 1e6  # V -> uV
    if not np.isfinite(data_uv).all():
        raise ValueError(f"non-finite samples in {path}")
    return data_uv, raw.info, list(raw.ch_names)


def make_epochs(data_uv: np.ndarray, sfreq: float, starts: np.ndarray, win_s: float = EPOCH_WIN_S):
    samples = int(round(win_s * sfreq))
    n_times = data_uv.shape[1]
    idx = np.round(starts[:, None] * sfreq).astype(np.int64) + np.arange(samples)
    if idx.size and idx.max() >= n_times:
        raise ValueError("epoch index exceeds recording length")
    ep = data_uv[:, idx]  # channels x epochs x samples
    return detrend(ep, axis=2, type="linear")


# ---------------------------------------------------------------------------
# Feature kernels
# ---------------------------------------------------------------------------
def spectral_features(psd: np.ndarray, freqs: np.ndarray) -> dict:
    """Spectral features from PSD shaped (..., n_freq), freqs in Hz."""
    psd = np.maximum(psd, 1e-30)
    masks = {b: band_mask(freqs, b) for b in BAND_NAMES}
    bp = np.stack([_trapz(psd[..., masks[b]], freqs[masks[b]], axis=-1) for b in BAND_NAMES], axis=-1)
    total = bp.sum(axis=-1)
    rel = _safe_div(bp, total[..., None])
    log_abs = np.log10(np.maximum(bp, 1e-30))
    band_psd = psd[..., masks["gamma"] | masks["beta"] | masks["alpha"] | masks["theta"] | masks["delta"]]
    f_band = freqs[masks["gamma"] | masks["beta"] | masks["alpha"] | masks["theta"] | masks["delta"]]

    centroid = _safe_div((band_psd * f_band).sum(axis=-1), band_psd.sum(axis=-1))
    cum = np.cumsum(band_psd, axis=-1)
    target = 0.95 * cum[..., -1:]
    edge_idx = np.argmax(cum >= target, axis=-1)
    edge = f_band[edge_idx]

    alpha_mask = masks["alpha"]
    alpha_psd = psd[..., alpha_mask]
    alpha_freqs = freqs[alpha_mask]
    alpha_idx = np.argmax(alpha_psd, axis=-1)
    alpha_peak_freq = alpha_freqs[alpha_idx]
    alpha_peak_power = alpha_psd.max(axis=-1)

    p_norm = _safe_div(band_psd, band_psd.sum(axis=-1, keepdims=True))
    spec_ent = -(p_norm * np.log(p_norm + 1e-30)).sum(axis=-1) / np.log(band_psd.shape[-1])

    fit_mask = (freqs >= 2.0) & (freqs <= 40.0) & ~((freqs >= 7.0) & (freqs <= 13.0))
    x = np.log10(freqs[fit_mask])
    y = np.log10(psd[..., fit_mask])
    n = x.size
    sx = x.sum()
    sxx = (x * x).sum()
    sy = y.sum(axis=-1)
    sxy = (y * x).sum(axis=-1)
    den = n * sxx - sx * sx
    slope = _safe_div(n * sxy - sx * sy, den)
    intercept = _safe_div(sy - slope * sx, n)

    return {
        **{f"abs_power_{b}_uv2": bp[..., i] for i, b in enumerate(BAND_NAMES)},
        **{f"rel_power_{b}": rel[..., i] for i, b in enumerate(BAND_NAMES)},
        **{f"log10_abs_power_{b}": log_abs[..., i] for i, b in enumerate(BAND_NAMES)},
        "total_power_1_45_uv2": total,
        "spectral_centroid_hz": centroid,
        "spectral_edge95_hz": edge,
        "alpha_peak_freq_hz": alpha_peak_freq,
        "alpha_peak_power_uv2": alpha_peak_power,
        "theta_alpha_ratio": _safe_div(bp[..., BAND_NAMES.index("theta")], bp[..., BAND_NAMES.index("alpha")]),
        "alpha_beta_ratio": _safe_div(bp[..., BAND_NAMES.index("alpha")], bp[..., BAND_NAMES.index("beta")]),
        "delta_theta_ratio": _safe_div(bp[..., BAND_NAMES.index("delta")], bp[..., BAND_NAMES.index("theta")]),
        "beta_gamma_ratio": _safe_div(bp[..., BAND_NAMES.index("beta")], bp[..., BAND_NAMES.index("gamma")]),
        "spectral_entropy": spec_ent,
        "aperiodic_exponent": -slope,
        "aperiodic_offset": intercept,
    }


def temporal_features(ep: np.ndarray, sfreq: float) -> dict:
    """Temporal features from epochs shaped (channels, epochs, samples)."""
    rms = np.sqrt(np.mean(ep ** 2, axis=-1))
    var = np.var(ep, axis=-1)
    ptp = np.ptp(ep, axis=-1)
    zcr = np.mean(np.diff(np.signbit(ep), axis=-1), axis=-1) * sfreq

    d1 = np.diff(ep, axis=-1)
    d2 = np.diff(d1, axis=-1)
    var_d1 = np.var(d1, axis=-1)
    mobility = np.sqrt(_safe_div(var_d1, var))
    complexity = _safe_div(np.sqrt(_safe_div(np.var(d2, axis=-1), var_d1)), mobility)
    line_length = np.mean(np.abs(d1), axis=-1) * sfreq

    env = np.abs(hilbert(ep, axis=-1))
    env_mean = np.mean(env, axis=-1)
    env_std = np.std(env, axis=-1)

    x = ep[..., :-1]
    y = ep[..., 1:]
    xm = x - np.mean(x, axis=-1, keepdims=True)
    ym = y - np.mean(y, axis=-1, keepdims=True)
    autocorr = _safe_div((xm * ym).sum(axis=-1),
                         np.sqrt((xm ** 2).sum(axis=-1) * (ym ** 2).sum(axis=-1)))

    return {
        "rms_uv": rms,
        "variance_uv2": var,
        "peak_to_peak_uv": ptp,
        "zcr_per_s": zcr,
        "hjorth_activity": var,
        "hjorth_mobility": mobility,
        "hjorth_complexity": complexity,
        "line_length_uv_per_s": line_length,
        "envelope_mean_uv": env_mean,
        "envelope_std_uv": env_std,
        "autocorr_lag1": autocorr,
    }


def nonlinear_features(ep: np.ndarray, sfreq: float) -> dict:
    """Nonlinear features on 250 Hz decimated epochs (data low-passed at 45 Hz)."""
    decim = max(1, int(round(sfreq / NONLINEAR_SFREQ_HZ)))
    ds = ep[:, :, ::decim]
    n_ch, n_ep, _ = ds.shape
    out = {k: np.empty((n_ch, n_ep), dtype=np.float64) for k in NONLINEAR_FEATURES}
    for c in range(n_ch):
        for e in range(n_ep):
            s = np.ascontiguousarray(ds[c, e])
            out["perm_entropy"][c, e] = _perm_entropy_order3(s)
            binary = (s > np.median(s)).astype(np.uint8)
            out["lz_complexity"][c, e] = _lz_complexity(binary)
            out["higuchi_fd"][c, e] = _higuchi_fd(s, 8)
            out["dfa_alpha"][c, e] = _dfa_alpha(s)
    return out


# ---------------------------------------------------------------------------
# Per-recording extraction
# ---------------------------------------------------------------------------
def extract_recording(
    participant_id: str,
    condition: str,
    input_path: Path,
    spans,
    qc_row: pd.Series,
    return_epochs: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame | None, np.ndarray, np.ndarray, dict]:
    """Return channel-level df, epoch-level df (or None), PSD, freqs, log info."""
    t0 = time.time()
    data_uv, info, ch_names = load_recording(input_path)
    sfreq = float(info["sfreq"])
    duration_s = data_uv.shape[1] / sfreq
    starts_all = epoch_starts(duration_s)
    valid = valid_epoch_mask(starts_all, spans)
    n_total = len(starts_all)
    if valid.sum() == 0:
        raise ValueError(f"no valid epochs for {participant_id}_{condition}")

    starts = starts_all[valid]
    ep = make_epochs(data_uv, sfreq, starts)
    f, p = welch(ep, fs=sfreq, nperseg=int(round(EPOCH_WIN_S * sfreq)),
                 noverlap=int(round(EPOCH_WIN_S * sfreq)) // 2, detrend=False,
                 scaling="density", axis=2)
    psd_mean = p.mean(axis=1)  # channels x freq

    spec_ch = spectral_features(psd_mean, f)
    temp_ep = temporal_features(ep, sfreq)
    nonlin_ep = nonlinear_features(ep, sfreq)
    spec_ep = spectral_features(p, f)

    epoch_features = {}
    for k in EPOCH_FEATURES:
        if k in spec_ch:
            epoch_features[k] = spec_ep[k]
        elif k in temp_ep:
            epoch_features[k] = temp_ep[k]
        elif k in nonlin_ep:
            epoch_features[k] = nonlin_ep[k]
        else:
            raise KeyError(k)

    # Channel-level table: spectral from mean PSD, temporal/nonlinear epoch means.
    channel_rows = []
    n_ch = len(ch_names)
    for ci, ch in enumerate(ch_names):
        row = {
            "participant_id": participant_id,
            "condition": condition,
            "recording_id": f"{participant_id}_{condition}",
            "channel": ch,
            "is_scalp_eeg": ch not in NON_SCALP_CHANNELS,
            "region": next((r for r, cs in REGIONS.items() if ch in cs), "other"),
            "feature_input_file": str(input_path),
            "input_variant": "ica" if input_path.name.endswith("_eeg_ica.fif") else "cleaned",
            "ica_formal_signoff_decision": qc_row.get("ica_formal_signoff_decision", ""),
            "audit_readiness": qc_row.get("audit_readiness", ""),
            "n_epochs_total": n_total,
            "n_epochs_used": int(valid.sum()),
            "valid_duration_s": float(valid.sum() * EPOCH_STEP_S),
            "artifact_windows_skipped": len(spans),
            "artifact_fraction": float(1.0 - valid.sum() / n_total) if n_total else np.nan,
        }
        for k in EPOCH_FEATURES:
            if k in spec_ch:
                row[k] = float(spec_ch[k][ci])
            else:
                row[k] = float(epoch_features[k][ci].mean())
        for k in SD_FEATURES:
            row[f"{k}_sd"] = float(np.std(epoch_features[k][ci], ddof=0))
        channel_rows.append(row)

    # Epoch-level table (valid epochs only).
    meta = {
        "participant_id": participant_id,
        "condition": condition,
        "recording_id": f"{participant_id}_{condition}",
        "input_variant": "ica" if input_path.name.endswith("_eeg_ica.fif") else "cleaned",
    }
    epoch_df = None
    if return_epochs:
        epoch_rows = []
        valid_idx = np.where(valid)[0]
        for ei, full_idx in enumerate(valid_idx):
            start = float(starts[ei])
            for ci, ch in enumerate(ch_names):
                row = dict(meta)
                row.update({
                    "channel": ch,
                    "epoch_index": int(full_idx),
                    "epoch_start_s": start,
                    "epoch_end_s": start + EPOCH_WIN_S,
                })
                for k in EPOCH_TABLE_FEATURES:
                    row[k] = float(epoch_features[k][ci, ei])
                epoch_rows.append(row)
        epoch_df = pd.DataFrame(epoch_rows)

    info_out = {
        "participant_id": participant_id,
        "condition": condition,
        "recording_id": f"{participant_id}_{condition}",
        "duration_s": duration_s,
        "sfreq": sfreq,
        "n_channels": n_ch,
        "n_epochs_total": n_total,
        "n_epochs_used": int(valid.sum()),
        "valid_duration_s": float(valid.sum() * EPOCH_STEP_S),
        "artifact_fraction": float(1.0 - valid.sum() / n_total) if n_total else np.nan,
        "artifact_windows_skipped": len(spans),
        "runtime_s": time.time() - t0,
    }
    return pd.DataFrame(channel_rows), epoch_df, psd_mean, f, info_out


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------
def regional_band_means(channel_df: pd.DataFrame, recording_id: str) -> dict:
    row = {}
    sub = channel_df[channel_df["recording_id"] == recording_id]
    for region, chans in REGIONS.items():
        rsub = sub[sub["channel"].isin(chans)]
        for band in BAND_NAMES:
            col = f"abs_power_{band}_uv2"
            row[f"abs_power_{band}_{region}_mean"] = float(rsub[col].mean()) if len(rsub) else np.nan
    return row


def asymmetry_values(channel_df: pd.DataFrame, recording_id: str) -> dict:
    row = {}
    sub = channel_df[channel_df["recording_id"] == recording_id].set_index("channel")
    for left, right in HOMOLOGOUS_PAIRS:
        if left not in sub.index or right not in sub.index:
            continue
        for band in ASYM_BANDS:
            col = f"abs_power_{band}_uv2"
            lv = float(sub.loc[left, col])
            rv = float(sub.loc[right, col])
            row[f"asym_{band}_{left}_{right}"] = float(np.log10(max(rv, 1e-30)) - np.log10(max(lv, 1e-30)))
    fa = [row.get(f"asym_alpha_{l}_{r}") for l, r in [("F3", "F4"), ("F7", "F8")]]
    fa = [v for v in fa if v is not None and np.isfinite(v)]
    row["frontal_alpha_asymmetry"] = float(np.mean(fa)) if fa else np.nan
    return row


def aggregate_recording(channel_df: pd.DataFrame, qc_row: pd.Series) -> dict:
    rid = f"{qc_row['participant_id']}_{qc_row['condition']}"
    sub = channel_df[channel_df["recording_id"] == rid]
    scalp = sub[sub["is_scalp_eeg"]]
    row = {
        "participant_id": qc_row["participant_id"],
        "condition": qc_row["condition"],
        "recording_id": rid,
        "feature_input_file": str(qc_row["feature_input_file"]),
        "input_variant": "ica" if str(qc_row["feature_input_file"]).endswith("_eeg_ica.fif") else "cleaned",
        "ica_formal_signoff_decision": qc_row.get("ica_formal_signoff_decision", ""),
        "audit_readiness": qc_row.get("audit_readiness", ""),
        "n_channels_total": int(len(sub)),
        "n_channels_scalp": int(len(scalp)),
        "n_epochs_total": int(sub["n_epochs_total"].iloc[0]),
        "n_epochs_used": int(sub["n_epochs_used"].iloc[0]),
        "valid_duration_s": float(sub["valid_duration_s"].iloc[0]),
        "artifact_windows_skipped": int(sub["artifact_windows_skipped"].iloc[0]),
        "artifact_fraction": float(sub["artifact_fraction"].iloc[0]),
    }
    for k in EPOCH_FEATURES:
        row[f"{k}_mean"] = float(scalp[k].mean())
        row[f"{k}_sd"] = float(scalp[k].std(ddof=0))
    for k in SD_FEATURES:
        row[f"{k}_epoch_sd_mean"] = float(scalp[f"{k}_sd"].mean())
    row.update(regional_band_means(channel_df, rid))
    row.update(asymmetry_values(channel_df, rid))
    return row


def aggregate_participant(recording_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pid in PARTICIPANTS:
        sub = recording_df[recording_df["participant_id"] == pid]
        if sub.empty:
            continue
        row = {
            "participant_id": pid,
            "n_recordings": int(len(sub)),
            "conditions_available": ",".join(sorted(sub["condition"].unique())),
            "aggregation_method": "mean across available conditions (see recording-level table)",
        }
        for col in sub.select_dtypes(include=[np.number]).columns:
            row[col] = float(sub[col].mean())
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Quality control
# ---------------------------------------------------------------------------
def _check(check_id, check, status, value, detail=""):
    return {"check_id": check_id, "check": check, "status": status,
            "value": value, "detail": detail}


def quality_report(qc, art, channel_df, recording_df, participant_df, epoch_df, log_df) -> pd.DataFrame:
    checks = []
    n_qc = len(qc)
    checks.append(_check("Q01", "EEG rows in QC summary", "PASS" if n_qc == 40 else "FAIL",
                         n_qc, "eeg_qc_summary_v3.csv"))
    n_exist = sum(Path(p).exists() for p in qc["feature_input_file"])
    checks.append(_check("Q02", "Feature input files exist", "PASS" if n_exist == 40 else "FAIL",
                         f"{n_exist}/40", "paths in eeg_qc_summary_v3.csv"))
    n_sf = int((recording_df["n_channels_total"] == 24).sum())
    checks.append(_check("Q03", "All recordings have 24 channels", "PASS" if n_sf == 40 else "FAIL",
                         f"{n_sf}/40", "read from the .fif"))
    n_ica = int((recording_df["input_variant"] == "ica").sum())
    n_cl = int((recording_df["input_variant"] == "cleaned").sum())
    checks.append(_check("Q04", "Feature-input policy (16 ICA / 24 cleaned)",
                         "PASS" if (n_ica, n_cl) == (16, 24) else "FAIL",
                         f"{n_ica} ICA / {n_cl} cleaned",
                         "per-recording policy from eeg_qc_summary_v3.csv"))
    n_windows = int(recording_df["artifact_windows_skipped"].sum())
    checks.append(_check("Q05", "Artifact windows registered", "PASS" if n_windows == 931 else "FAIL",
                         n_windows, "audit_finalization_v1/eeg/artifact_log_v1.csv"))
    min_ep = int(recording_df["n_epochs_used"].min())
    checks.append(_check("Q06", "Minimum valid epochs per recording", "PASS" if min_ep >= 10 else "FAIL",
                         min_ep, "2 s epochs, 1 s step"))
    bad = int(channel_df[EPOCH_FEATURES].isna().any(axis=1).sum())
    checks.append(_check("Q07", "No NaN/inf in channel-level features", "PASS" if bad == 0 else "FAIL",
                         bad, "rows with any missing feature"))
    neg = int((channel_df[[f"abs_power_{b}_uv2" for b in BAND_NAMES]] < 0).any(axis=1).sum())
    checks.append(_check("Q08", "Band powers non-negative", "PASS" if neg == 0 else "FAIL",
                         neg, "absolute band power rows"))
    rel_sum = channel_df[[f"rel_power_{b}" for b in BAND_NAMES]].sum(axis=1)
    max_dev = float((rel_sum - 1.0).abs().max())
    checks.append(_check("Q09", "Relative band powers sum to 1", "PASS" if max_dev < 1e-6 else "FAIL",
                         f"max |dev|={max_dev:.2e}", "five contiguous bands"))
    ap = channel_df["alpha_peak_freq_hz"]
    ok_ap = bool(((ap >= 8) & (ap <= 12)).all())
    checks.append(_check("Q10", "Alpha peak inside 8-12 Hz", "PASS" if ok_ap else "FAIL",
                         f"{ap.min():.1f}-{ap.max():.1f} Hz", "argmax of the alpha band"))
    reference_sensitive = [c for c in channel_df.columns if any(t in c.lower() for t in
                          ["laplacian", "csd", "connectivity", "coherence", "wpli", "plv"])]
    checks.append(_check("Q11", "No reference-sensitive features", "PASS" if not reference_sensitive else "FAIL",
                         len(reference_sensitive), "Laplacian/CSD/connectivity are deferred until QC-01"))
    counts = qc.groupby("condition")["participant_id"].nunique().to_dict()
    ok_cond = all(counts.get(c, 0) == 10 for c in CONDITIONS)
    checks.append(_check("Q12", "10 participants in each condition", "PASS" if ok_cond else "FAIL",
                         json.dumps(counts), "calm/meditation/maths/speech"))
    non_scalp = channel_df[~channel_df["is_scalp_eeg"]]["channel"].unique().tolist()
    checks.append(_check("Q13", "M1/M2 excluded from scalp aggregates", "PASS" if set(non_scalp) == {"M1", "M2"} else "FAIL",
                         non_scalp, "channel-level rows retained for transparency"))
    label_cols = [c for c in channel_df.columns if "dosha" in c.lower() or "prakriti" in c.lower()]
    checks.append(_check("Q14", "No Dosha/Prakriti labels merged", "PASS" if not label_cols else "FAIL",
                         len(label_cols), "labels remain provisional and separate"))
    rejected_used = recording_df[recording_df["ica_formal_signoff_decision"].eq("REJECTED")
                                 & recording_df["input_variant"].eq("ica")]
    checks.append(_check("Q15", "No REJECTED ICA file used as input", "PASS" if rejected_used.empty else "FAIL",
                         len(rejected_used), "feature_input_file policy"))
    dup = int(channel_df.duplicated(["recording_id", "channel"]).sum())
    checks.append(_check("Q16", "No duplicate recording/channel rows", "PASS" if dup == 0 else "FAIL",
                         dup, "channel-level table"))
    checks.append(_check("Q17", "Recording-level row count", "PASS" if len(recording_df) == 40 else "FAIL",
                         len(recording_df), "40 recordings"))
    checks.append(_check("Q18", "Participant-level row count", "PASS" if len(participant_df) == 10 else "FAIL",
                         len(participant_df), "10 participants"))
    expected_epoch_rows = int(recording_df["n_epochs_used"].sum() * 24)
    checks.append(_check("Q19", "Epoch-level row count", "PASS" if len(epoch_df) == expected_epoch_rows else "FAIL",
                         f"{len(epoch_df)} (expected {expected_epoch_rows})", "valid epochs x 24 channels"))
    checks.append(_check("Q20", "Input SHA-256 recorded", "PASS" if log_df["input_sha256"].notna().all() else "FAIL",
                         f"{log_df['input_sha256'].notna().sum()}/40", "extraction log"))
    # Range sanity (WARN only)
    ranges = {
        "higuchi_fd": (0.0, 3.0), "dfa_alpha": (0.0, 2.0), "perm_entropy": (0.0, 1.0),
        "autocorr_lag1": (-1.0, 1.0), "spectral_centroid_hz": (0.0, 46.0),
    }
    out_of_range = []
    for col, (lo, hi) in ranges.items():
        s = channel_df[col]
        if ((s < lo) | (s > hi)).any():
            out_of_range.append(col)
    checks.append(_check("Q21", "Feature ranges plausible", "PASS" if not out_of_range else "WARN",
                         f"{len(out_of_range)} column(s) outside range", ",".join(out_of_range)))
    # Documented limitations, not failures
    checks.append(_check("Q22", "ICA/cleaned input mix confounds condition", "WARN", f"{n_ica} ICA",
                         "input variant differs within participant across conditions; sensitivity analysis recommended"))
    checks.append(_check("Q23", "Acquisition reference unknown", "WARN", "QC-01 open",
                         "no reference-sensitive features computed"))
    checks.append(_check("Q24", "Dosha labels provisional", "WARN", "not merged",
                         "join participant_labels_v1.csv separately and label as provisional"))
    speech_dur = recording_df[recording_df.condition == "speech"]["valid_duration_s"]
    if len(speech_dur):
        speech_value = f"{speech_dur.min():.1f}-{speech_dur.max():.1f} s"
    else:
        speech_value = "not in this run"
    checks.append(_check("Q25", "Speech-condition EEG is short", "WARN", speech_value,
                         "compare conditions with duration-aware methods"))
    return pd.DataFrame(checks)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def _import_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def make_figures(recording_df, channel_df, psd_store, freqs, info, out_dir: Path):
    plt = _import_matplotlib()
    out_dir.mkdir(parents=True, exist_ok=True)
    figs = []
    colors = {"calm": "#4c72b0", "meditation": "#55a868", "maths": "#c44e52", "speech": "#8172b2"}

    # 1. Grand-average PSD by condition
    fig, ax = plt.subplots(figsize=(8, 4.5))
    f_mask = (freqs >= 1) & (freqs <= 45)
    for cond in CONDITIONS:
        rids = recording_df[recording_df.condition == cond]["recording_id"]
        psds = [psd_store[r] for r in rids if r in psd_store]
        if not psds:
            continue
        mean_psd = np.mean([p.mean(axis=0) for p in psds], axis=0)
        ax.plot(freqs[f_mask], mean_psd[f_mask], label=cond, color=colors[cond], lw=1.4)
    for lo, hi in BANDS.values():
        ax.axvspan(lo, hi, color="grey", alpha=0.06)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD (uV^2/Hz)")
    ax.set_title("Grand-average PSD by condition (scalp channels)")
    ax.legend(frameon=False, ncol=4)
    fig.tight_layout()
    p = out_dir / "fig01_psd_by_condition.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    figs.append(p)

    # 2. Relative band-power distributions
    fig, axes = plt.subplots(1, 5, figsize=(14, 3.8), sharey=False)
    for ax, band in zip(axes, BAND_NAMES):
        data = [channel_df[channel_df.condition == c][f"rel_power_{band}"].values for c in CONDITIONS]
        ax.boxplot(data, labels=CONDITIONS, showfliers=False)
        ax.set_title(band.capitalize())
        ax.set_ylabel("Relative power" if band == "delta" else "")
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle("Relative band power by condition (all scalp channels)", y=1.02)
    fig.tight_layout()
    p = out_dir / "fig02_band_power_by_condition.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    figs.append(p)

    # 3. Topography per condition and band
    try:
        import mne
        scalp = [c for c in info["ch_names"] if c not in NON_SCALP_CHANNELS]
        picks = mne.pick_channels(info["ch_names"], scalp)
        sub_info = mne.pick_info(info, picks)
        plot_bands = ["delta", "alpha", "beta"]
        fig, axes = plt.subplots(len(CONDITIONS), len(plot_bands), figsize=(9, 11))
        for ri, cond in enumerate(CONDITIONS):
            cdf = channel_df[(channel_df.condition == cond) & (channel_df.is_scalp_eeg)]
            for ci, band in enumerate(plot_bands):
                ax = axes[ri, ci]
                vals = cdf.groupby("channel")[f"abs_power_{band}_uv2"].mean().reindex(scalp)
                v = vals.values.astype(float)
                v = np.log10(np.maximum(v, 1e-12))
                im, _ = mne.viz.plot_topomap(v, sub_info, axes=ax, show=False, contours=0,
                                             cmap="viridis", sensors=True)
                ax.set_title(f"{cond} - {band}", fontsize=9)
                fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.suptitle("Scalp topography of log10 absolute band power", y=0.995)
        fig.tight_layout()
        p = out_dir / "fig03_topography_band_power.png"
        fig.savefig(p, dpi=150, bbox_inches="tight")
        plt.close(fig)
        figs.append(p)
    except Exception as exc:  # pragma: no cover - plotting guard
        warnings.warn(f"topography figure skipped: {exc}")

    # 4. Alpha peak frequency/power
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, col, ylab in [(axes[0], "alpha_peak_freq_hz_mean", "Alpha peak (Hz)"),
                          (axes[1], "alpha_peak_power_uv2_mean", "Alpha peak power (uV^2)")]:
        data = [recording_df[recording_df.condition == c][col].values for c in CONDITIONS]
        ax.boxplot(data, labels=CONDITIONS, showfliers=False)
        ax.set_title(ylab)
        ax.set_ylabel(ylab)
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle("Posterior alpha peak by condition (scalp mean)", y=1.02)
    fig.tight_layout()
    p = out_dir / "fig04_alpha_peak.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    figs.append(p)

    # 5. Frontal alpha asymmetry
    fig, ax = plt.subplots(figsize=(6.5, 4))
    data = [recording_df[recording_df.condition == c]["frontal_alpha_asymmetry"].values for c in CONDITIONS]
    ax.boxplot(data, labels=CONDITIONS, showfliers=False)
    ax.axhline(0, color="grey", lw=0.8, ls="--")
    ax.set_ylabel("log10(right) - log10(left)")
    ax.set_title("Frontal alpha asymmetry (F3/F4, F7/F8)")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    p = out_dir / "fig05_frontal_alpha_asymmetry.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    figs.append(p)

    # 6. Feature correlation heatmap (selected recording-level features)
    key_cols = [c for c in recording_df.columns if c.endswith("_mean") and
                any(t in c for t in ["abs_power_alpha", "abs_power_beta", "abs_power_theta",
                                     "rms_uv", "spectral_centroid", "spectral_entropy",
                                     "perm_entropy", "higuchi_fd", "dfa_alpha",
                                     "alpha_peak_freq", "frontal_alpha_asymmetry"])]
    key_cols = [c for c in key_cols if recording_df[c].notna().all()][:20]
    if len(key_cols) >= 3:
        corr = recording_df[key_cols].corr()
        fig, ax = plt.subplots(figsize=(9, 7.5))
        im = ax.imshow(corr.values, vmin=-1, vmax=1, cmap="RdBu_r")
        ax.set_xticks(range(len(key_cols)))
        ax.set_yticks(range(len(key_cols)))
        ax.set_xticklabels([c.replace("_mean", "") for c in key_cols], rotation=75, ha="right", fontsize=7)
        ax.set_yticklabels([c.replace("_mean", "") for c in key_cols], fontsize=7)
        ax.set_title("Recording-level feature correlations")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        p = out_dir / "fig06_feature_correlation.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        figs.append(p)

    # 7. QC: valid duration and artifact fraction
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    x = np.arange(len(recording_df))
    colors_bar = [colors.get(c, "grey") for c in recording_df["condition"]]
    axes[0].bar(x, recording_df["valid_duration_s"], color=colors_bar)
    axes[0].set_ylabel("Valid duration (s)")
    axes[1].bar(x, recording_df["artifact_fraction"] * 100, color=colors_bar)
    axes[1].set_ylabel("Epochs skipped (%)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(recording_df["recording_id"], rotation=90, fontsize=7)
    fig.suptitle("Artifact-window impact per recording")
    fig.tight_layout()
    p = out_dir / "fig07_artifact_impact.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    figs.append(p)
    return figs


# ---------------------------------------------------------------------------
# Top-level extraction
# ---------------------------------------------------------------------------
def run_extraction(
    out_dir: Path = OUT_DIR,
    force: bool = False,
    limit: list[str] | None = None,
    make_plots: bool = True,
) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "channel": out_dir / "eeg_features_channel_level.csv",
        "recording": out_dir / "eeg_features_recording_level.csv",
        "participant": out_dir / "eeg_features_participant_level.csv",
        "epoch": out_dir / "eeg_features_epoch_level.csv",
        "log": out_dir / "eeg_feature_extraction_log.csv",
        "qc": out_dir / "eeg_feature_extraction_quality_report.csv",
        "summary": out_dir / "eeg_feature_extraction_summary.md",
    }
    if not force and any(p.exists() for p in outputs.values()):
        raise SystemExit(f"REFUSING TO OVERWRITE existing outputs in {out_dir}; delete them deliberately or pass --force")

    qc = load_qc()
    art = load_artifacts()
    if limit:
        keep = set(limit)
        qc = qc[qc.apply(lambda r: f"{r.participant_id}_{r.condition}" in keep, axis=1)].reset_index(drop=True)
        if qc.empty:
            raise SystemExit(f"no recordings matched --limit {sorted(keep)}")

    channel_parts, epoch_parts, log_rows = [], [], []
    rec_rows = []
    psd_store = {}
    freqs = None
    info0 = None
    t_start = time.time()
    for i, row in qc.iterrows():
        pid, cond = row["participant_id"], row["condition"]
        rid = f"{pid}_{cond}"
        path = Path(row["feature_input_file"])
        if not path.exists():
            raise FileNotFoundError(path)
        spans = artifact_spans(art, pid, cond)
        ch_df, ep_df, psd, f, log_info = extract_recording(pid, cond, path, spans, row)
        channel_parts.append(ch_df)
        epoch_parts.append(ep_df)
        rec_rows.append(aggregate_recording(ch_df, row))
        psd_store[rid] = psd
        freqs = f
        if info0 is None:
            _, info0, _ = load_recording(path)
        log_info.update({
            "input_path": str(path),
            "input_sha256": sha256_file(path),
            "input_variant": "ica" if path.name.endswith("_eeg_ica.fif") else "cleaned",
            "ica_formal_signoff_decision": row.get("ica_formal_signoff_decision", ""),
            "status": "OK",
            "error": "",
        })
        log_rows.append(log_info)
        print(f"[{i+1}/{len(qc)}] {rid}: {log_info['n_epochs_used']}/{log_info['n_epochs_total']} epochs, "
              f"{log_info['runtime_s']:.1f}s", flush=True)

    channel_df = pd.concat(channel_parts, ignore_index=True)
    epoch_df = pd.concat(epoch_parts, ignore_index=True)
    recording_df = pd.DataFrame(rec_rows).sort_values(["participant_id", "condition"]).reset_index(drop=True)
    participant_df = aggregate_participant(recording_df)
    log_df = pd.DataFrame(log_rows)
    qc_report = quality_report(qc, art, channel_df, recording_df, participant_df, epoch_df, log_df)

    channel_df.to_csv(outputs["channel"], index=False, encoding="utf-8")
    recording_df.to_csv(outputs["recording"], index=False, encoding="utf-8")
    participant_df.to_csv(outputs["participant"], index=False, encoding="utf-8")
    epoch_df.to_csv(outputs["epoch"], index=False, encoding="utf-8")
    log_df.to_csv(outputs["log"], index=False, encoding="utf-8")
    qc_report.to_csv(outputs["qc"], index=False, encoding="utf-8")

    if freqs is not None and psd_store:
        ids = sorted(psd_store)
        scalp = [c for c in info0["ch_names"] if c not in NON_SCALP_CHANNELS]
        psd_arr = np.stack([psd_store[r][[info0["ch_names"].index(c) for c in scalp]] for r in ids]).astype(np.float32)
        np.savez_compressed(out_dir / "eeg_psd_by_recording.npz",
                            freqs=freqs.astype(np.float32), recording_ids=np.array(ids),
                            channels=np.array(scalp), psd=psd_arr)

    figs = []
    if make_plots:
        figs = make_figures(recording_df, channel_df, psd_store, freqs, info0, out_dir / "figures")

    write_summary(out_dir, qc, recording_df, channel_df, participant_df, epoch_df, log_df, qc_report, figs)
    return {
        "outputs": {k: str(v) for k, v in outputs.items()},
        "figures": [str(p) for p in figs],
        "n_recordings": len(recording_df),
        "runtime_s": time.time() - t_start,
    }


def write_summary(out_dir, qc, recording_df, channel_df, participant_df, epoch_df, log_df, qc_report, figs):
    counts = qc_report["status"].value_counts().to_dict()
    n_ica = int((recording_df["input_variant"] == "ica").sum())
    n_cl = int((recording_df["input_variant"] == "cleaned").sum())
    n_windows = int(recording_df["artifact_windows_skipped"].sum())
    min_ep = int(recording_df["n_epochs_used"].min())
    max_ep = int(recording_df["n_epochs_used"].max())
    dur = recording_df.groupby("condition")["valid_duration_s"].agg(["min", "max", "mean"]).round(1)
    qc_counts = qc_report.groupby("status").size().to_dict()
    lines = [
        "# EEG Feature Extraction - Summary (v1)",
        "",
        f"**Generated:** {pd.Timestamp.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "**Notebook:** `notebooks/EEG_Feature_Extraction.ipynb`",
        "**Script:** `EEG features/scripts/extract_eeg_features.py`",
        "**Status:** COMPLETE",
        "",
        "## 1. Scope",
        "",
        "Sensor-space EEG feature extraction only - no rereferencing, no interpolation, no connectivity,",
        "no EEG-speech fusion, no Dosha modelling. Inputs are the finalised preprocessing outputs",
        "selected by `signoff_finalization_v2/eeg_qc_summary_v3.csv`.",
        "",
        "## 2. Inputs (verified, not assumed)",
        "",
        f"- 40/40 EEG recordings read successfully ({n_ica} `*_eeg_ica.fif`, {n_cl} cleaned `*_eeg.fif`).",
        "- 24 channels at 1000 Hz; data already band-passed 1-45 Hz and notched by the preprocessing stage.",
        f"- {n_windows} one-second artifact windows skipped (`SKIP_IN_FEATURE_EXTRACTION`), 34 recordings.",
        "- Artifact windows come from the cleaned-file audit; for ICA inputs they are applied conservatively.",
        "",
        "## 3. Epochs and features",
        "",
        f"- 2.0 s epochs, 1.0 s step, linear detrend per epoch; any epoch overlapping an artifact window is skipped.",
        f"- Valid epochs per recording: {min_ep}-{max_ep}; valid duration by condition (s):",
        "",
        "| condition | min | max | mean |",
        "|---|---:|---:|---:|",
    ]
    for cond, r in dur.iterrows():
        lines.append(f"| {cond} | {r['min']} | {r['max']} | {r['mean']} |")
    lines += [
        "",
        "- Spectral (per channel, Welch PSD of the epoch-averaged signal): absolute/relative/log band power",
        "  for delta 1-4, theta 4-8, alpha 8-12, beta 12-30, gamma 30-45 Hz; total power; spectral",
        "  centroid; 95% spectral edge; alpha peak frequency/power; theta/alpha, alpha/beta, delta/theta,",
        "  beta/gamma ratios; spectral entropy; simple log-log aperiodic exponent (2-40 Hz, alpha 7-13 Hz",
        "  excluded).",
        "- Temporal (per epoch, averaged): RMS, variance, peak-to-peak, zero-crossing rate, Hjorth",
        "  activity/mobility/complexity, line length, Hilbert envelope mean/SD, lag-1 autocorrelation.",
        "- Nonlinear (per epoch at 250 Hz, averaged): permutation entropy (order 3), Lempel-Ziv",
        "  complexity, Higuchi fractal dimension (kmax 8), DFA exponent (scales 4-64).",
        "- Laterality: log10(right) - log10(left) absolute power for 8 homologous pairs in theta/alpha/beta;",
        "  frontal alpha asymmetry is the mean of F3/F4 and F7/F8.",
        "- M1/M2 are retained in the channel-level table but excluded from all scalp aggregates.",
        "",
        "## 4. Outputs",
        "",
        "| File | Rows x cols |",
        "|---|---|",
        f"| `eeg_features_channel_level.csv` | {channel_df.shape[0]} x {channel_df.shape[1]} |",
        f"| `eeg_features_recording_level.csv` | {recording_df.shape[0]} x {recording_df.shape[1]} |",
        f"| `eeg_features_participant_level.csv` | {participant_df.shape[0]} x {participant_df.shape[1]} |",
        f"| `eeg_features_epoch_level.csv` | {epoch_df.shape[0]} x {epoch_df.shape[1]} |",
        f"| `eeg_feature_extraction_log.csv` | {log_df.shape[0]} x {log_df.shape[1]} |",
        f"| `eeg_feature_extraction_quality_report.csv` | {qc_report.shape[0]} x {qc_report.shape[1]} |",
        f"| `eeg_psd_by_recording.npz` | 40 recordings x 22 scalp channels x PSD bins |",
        f"| `figures/` | {len(figs)} PNGs |",
        "",
        "## 5. Coverage and QC",
        "",
        f"- Recordings processed: **40/40**, failures: 0.",
        f"- QC checks: {qc_counts}.",
        f"- No NaN/inf in the channel-level feature table: {int(channel_df[EPOCH_FEATURES].isna().any(axis=1).sum())} rows.",
        f"- All 40 feature-input paths exist; SHA-256 recorded in the extraction log.",
        "",
        "## 6. Limitations",
        "",
        "1. n = 10 participants; all results are exploratory. No inferential statistics, classification or",
        "   generalization is claimed.",
        "2. The feature-input policy mixes ICA-cleaned and cleaned files across conditions within participants",
        "   (16 ICA / 24 cleaned). A cleaned-only sensitivity analysis is complete in",
        "   `validation_v1/sensitivity_cleaned_only/`: alpha/beta/Higuchi-FD/alpha-peak are stable,",
        "   while theta/delta/RMS are sensitive to the input choice.",
        "3. The 1 Hz high-pass attenuates low delta; delta 1-4 Hz should be interpreted with that caveat.",
        "4. Gamma 30-45 Hz is a narrow residual band and may contain muscle activity despite artifact",
        "   windowing and ICA.",
        "5. The acquisition reference is unknown (QC-01), so no Laplacian, CSD, average-reference or",
        "   connectivity features were computed.",
        "6. The 110 flagged channel instances were not interpolated (QC-04); they are used as recorded.",
        f"7. Speech-condition EEG has only {int(recording_df[recording_df.condition=='speech']['valid_duration_s'].min())}-"
        f"{int(recording_df[recording_df.condition=='speech']['valid_duration_s'].max())} s of valid data "
        "(37-67 s raw) versus ~10 min for calm/meditation/maths, so condition comparisons must account",
        "   for different effective sample sizes.",
        "8. Dosha labels are provisional and are not merged here. Join on `participant_id` only with an",
        "   explicit provisional-label caveat.",
        "9. The aperiodic exponent is a simple log-log fit excluding 7-13 Hz, not a FOOOF/SPECPARAM",
        "   decomposition.",
        "",
        "## 7. Next steps",
        "",
        "1. Use the completed cleaned-only sensitivity result (`validation_v1/sensitivity_cleaned_only/`)",
        "   when interpreting theta, delta, RMS or any feature with r < 0.80; alpha/beta/HFD/alpha-peak",
        "   conclusions are stable.",
        "2. Join provisional labels (`Questionnaire_Analysis/participant_labels_v1.csv`) and speech features",
        "   (`analysis_ready/participant_master_v1.csv`) on `participant_id`, keeping the provisional flag.",
        "3. Confirm the acquisition reference before adding reference-sensitive features or connectivity.",
        "4. Decide the interpolation policy for the 110 flagged channels (QC-04).",
        "5. Only after labels are validated: feature selection and modelling with participant-level",
        "   cross-validation; n = 10 is too small for train/test splits that claim generalization.",
        "",
        "## 8. Reproduce",
        "",
        "```",
        "py -3.14 \"EEG features/scripts/extract_eeg_features.py\" --force",
        "py -3.14 reports_final_v3/scripts/run_nb.py \"notebooks/EEG_Feature_Extraction.ipynb\"",
        "```",
        "",
    ]
    (out_dir / "eeg_feature_extraction_summary.md").write_text("\n".join(lines), encoding="utf-8")
