from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

SPECIALIST_POSITIONS = ("K", "DST")

def _read_json(path):
    return json.loads(Path(path).read_text())

def build_specialist_rows(source_path, model_path):
    source = pd.read_csv(source_path, low_memory=False)
    model = _read_json(model_path)
    scfg = model["specialists"]
    mcfg = model["draft_market"]
    season_games = float(model["latent_value"]["season_games"])
    df = source[source["position"].isin(SPECIALIST_POSITIONS)].copy()
    if len(df) == 0:
        return df
    for c in ["espn_id","espn_adp","espn_rank","espn_proj_points"]:
        if c in df.columns:
            df[c]=pd.to_numeric(df[c], errors="coerce")
    df["projection_ppg"] = pd.to_numeric(df.get("espn_proj_points"), errors="coerce") / season_games
    df["latent_mean_ppg"] = df["projection_ppg"]
    sentinel=float(mcfg["adp_sentinel_floor"])
    rank_max=float(mcfg["general_max_rank"])
    sigma=float(scfg["market_sigma_pick"])
    eligible=[]; reasons=[]; centers=[]; center_sources=[]
    for _,row in df.iterrows():
        team=str(row.get("nfl_team") or "").upper()
        proj=row.get("espn_proj_points"); adp=row.get("espn_adp"); rank=row.get("espn_rank")
        has_proj=pd.notna(proj) and float(proj)>0
        credible_adp=pd.notna(adp) and float(adp)<sentinel
        credible_rank=pd.notna(rank) and float(rank)<=rank_max
        ok=True; reason="eligible_specialist"
        if team in {"","NAN","FA"}:
            ok=False; reason="no_current_nfl_team"
        elif not (has_proj or credible_adp or credible_rank):
            ok=False; reason="no_current_market_signal"
        if credible_adp:
            center=float(adp); csrc="adp"
        elif credible_rank:
            center=float(rank); csrc="rank"
        else:
            center=np.nan; csrc=None
        eligible.append(ok); reasons.append(reason); centers.append(center); center_sources.append(csrc)
    df["draft_eligible"]=eligible
    df["draft_eligibility_reason"]=reasons
    df["market_pick_mean"]=centers
    df["market_pick_sigma"]=sigma
    df["market_center_source"]=center_sources
    df["model_status"]="specialist_projection"
    replacement={}
    for pos in SPECIALIST_POSITIONS:
        g=df[df["position"].eq(pos)&df["draft_eligible"].astype(bool)&df["projection_ppg"].notna()].sort_values("projection_ppg",ascending=False)
        wanted=int(scfg["replacement_rank"][pos])
        replacement[pos]=float(g.iloc[min(max(wanted-1,0),len(g)-1)]["projection_ppg"]) if len(g) else 0.0
    df["dynamic_replacement_ppg"]=df["position"].map(replacement)
    df["replacement_ppg"]=df["dynamic_replacement_ppg"]
    df["dynamic_vorp_ppg"]=(df["projection_ppg"]-df["dynamic_replacement_ppg"]).clip(lower=0.0)
    df["vorp_ppg"]=df["dynamic_vorp_ppg"]
    df["dynamic_scarcity_gap_ppg"]=0.0
    df["scarcity_gap_next_n_ppg"]=0.0
    df["dynamic_draft_value"]=df["dynamic_vorp_ppg"]
    df["draft_value_score"]=df["dynamic_draft_value"]
    sig={k:float(v) for k,v in scfg["epistemic_sigma_ppg"].items()}
    df["latent_mean_sd_ppg"]=df["position"].map(sig)
    df["predictive_weekly_sd_ppg"]=df["latent_mean_sd_ppg"]
    df["weekly_aleatoric_sd_ppg"]=df["latent_mean_sd_ppg"]
    df["tier"]=pd.Series(pd.NA,index=df.index,dtype="Int64")
    for pos in SPECIALIST_POSITIONS:
        g=df[df["position"].eq(pos)&df["projection_ppg"].notna()].sort_values("projection_ppg",ascending=False)
        if len(g):
            for rank,idx in enumerate(g.index,start=1):
                df.loc[idx,"tier"] = 1 if rank<=6 else 2 if rank<=12 else 3
    return df

def ensure_specialists_in_live_board(live_board_path, source_path, model_path):
    live_board_path=Path(live_board_path); source_path=Path(source_path)
    if not live_board_path.exists() or not source_path.exists():
        return 0
    board=pd.read_csv(live_board_path,low_memory=False)
    spec=build_specialist_rows(source_path,model_path)
    if len(spec)==0:
        return 0
    board=board[~board["position"].isin(SPECIALIST_POSITIONS)].copy()
    cols=list(dict.fromkeys(list(board.columns)+list(spec.columns)))
    for c in cols:
        if c not in board.columns: board[c]=np.nan
        if c not in spec.columns: spec[c]=np.nan
    out=pd.concat([board[cols],spec[cols]],ignore_index=True,sort=False)
    out.to_csv(live_board_path,index=False)
    return int(len(spec))
