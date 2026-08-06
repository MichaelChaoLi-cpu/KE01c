"""Consistent English reader-facing labels for eligible fire bases."""

from __future__ import annotations

import pandas as pd

from table_municipality_fire_consequence_and_accessibility_summary import (
    ENGLISH_MUNICIPALITY,
)


VERIFIED_LABELS = {
    "熊本市消防局東消防署託麻出張所": "Kumamoto East FS — Takuma branch",
    "熊本市消防局中央消防署出水出張所": "Kumamoto Central FS — Izumi branch",
    "熊本市消防局東消防署小山出張所": "Kumamoto East FS — Oyama branch",
    "八代広域行政事務組合八代消防署": "Yatsushiro Fire Station",
    "熊本市消防局中央消防署楠出張所": "Kumamoto Central FS — Kusu branch",
    "熊本市消防局東消防署": "Kumamoto East Fire Station",
    "熊本市消防局中央消防署": "Kumamoto Central Fire Station",
    "熊本市消防局中央消防署清水出張所": "Kumamoto Central FS — Shimizu branch",
    "熊本市消防局中央消防署南熊本庁舎": "Kumamoto Central FS — South Kumamoto office",
    "八代広域行政事務組合八代消防署新開分署": "Yatsushiro FS — Shinkai branch",
    "菊池広域連合泉ヶ丘消防署": "Izumigaoka Fire Station",
    "熊本市消防局西消防署": "Kumamoto West Fire Station",
    "熊本市消防局西消防署池田庁舎": "Kumamoto West FS — Ikeda office",
    "八代広域行政事務組合鏡消防署": "Kagami Fire Station",
    "有明広域行政事務組合玉名消防署西分署": "Tamana FS — West branch",
    "熊本市消防局西消防署平田出張所": "Kumamoto West FS — Hirata branch",
    "熊本市消防局西消防署田崎出張所": "Kumamoto West FS — Tasaki branch",
    "熊本市消防局西消防署川尻出張所": "Kumamoto West FS — Kawashiri branch",
    "宇城広域連合北消防署": "Uki Regional North Fire Station",
    "熊本市消防局中央消防署北部出張所": "Kumamoto Central FS — North branch",
    "有明広域行政事務組合荒尾消防署": "Arao Fire Station",
    "有明広域行政事務組合荒尾消防署緑丘分署": "Arao FS — Midorigaoka branch",
    "阿蘇広域行政事務組合中部消防署": "Aso Central Fire Station",
    "宇城広域連合南消防署": "Uki Regional South Fire Station",
    "上球磨消防組合上球磨消防署": "Kamikuma Fire Station",
    "有明広域行政事務組合玉名消防署": "Tamana Fire Station",
    "有明広域行政事務組合荒尾消防署長洲分署": "Arao FS — Nagasu branch",
    "菊池広域連合南消防署": "Kikuchi Regional South Fire Station",
    "人吉下球磨消防組合中央消防署": "Hitoyoshi–Shimokuma Central Fire Station",
    "天草広域連合中央消防署": "Amakusa Central Fire Station",
    "菊池広域連合北消防署": "Kikuchi Regional North Fire Station",
}


def fire_base_label_table(values: pd.DataFrame) -> pd.DataFrame:
    """Return one stable English label and label status per source base name."""
    identity = values[
        ["Fire Base Name", "Municipality Code"]
    ].drop_duplicates().copy()
    if identity["Fire Base Name"].duplicated().any():
        raise ValueError("A fire-base name maps to multiple municipality codes")
    identity["Municipality Code"] = identity["Municipality Code"].astype("string")
    identity["Municipality"] = identity["Municipality Code"].map(ENGLISH_MUNICIPALITY)
    if identity["Municipality"].isna().any():
        missing = identity.loc[identity["Municipality"].isna(), "Municipality Code"].unique()
        raise ValueError(f"Missing English municipality labels: {missing.tolist()}")
    identity = identity.sort_values(
        ["Municipality Code", "Fire Base Name"], kind="stable"
    ).reset_index(drop=True)
    identity["Municipality Base Number"] = (
        identity.groupby("Municipality Code", sort=False).cumcount() + 1
    )
    verified = identity["Fire Base Name"].map(VERIFIED_LABELS)
    generated = (
        identity["Municipality"]
        + " — response base "
        + identity["Municipality Base Number"].astype(str)
    )
    identity["Fire Base"] = verified.fillna(generated)
    identity["Label Status"] = verified.notna().map(
        {True: "Verified project translation", False: "Generated geographic label"}
    )
    return identity[
        ["Fire Base Name", "Municipality", "Fire Base", "Label Status"]
    ]
