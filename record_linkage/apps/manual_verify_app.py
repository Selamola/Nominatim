"""Streamlit app for manual verification of record linkage."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

SAMPLE_PATH = Path("data/outputs/sample_for_verification.csv")
PARTIAL_PATH = Path("data/temp/partial_verified_matches.csv")
FINISHED_PATH = Path("data/outputs/verified_matches.csv")


def load_sample() -> pd.DataFrame:
    if SAMPLE_PATH.exists():
        return pd.read_csv(SAMPLE_PATH)
    uploaded = st.file_uploader("Upload sample CSV", type="csv")
    if uploaded:
        return pd.read_csv(uploaded)
    st.stop()


def save_partial(df: pd.DataFrame) -> None:
    PARTIAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PARTIAL_PATH, index=False)


def main() -> None:
    st.title("Manual Verification")
    df = load_sample()
    if PARTIAL_PATH.exists():
        labels = pd.read_csv(PARTIAL_PATH)
    else:
        labels = pd.DataFrame(columns=["df1_index", "df2_index", "label"])

    st.sidebar.write(f"Total records: {len(df)}")
    mode = st.sidebar.selectbox("Mode", ["Single", "Batch"])
    min_score, max_score = st.sidebar.slider("Score range", 0.0, 1.0, (0.0, 1.0), 0.01)
    search = st.sidebar.text_input("Search REC_CODE or report_id")
    df_filtered = df[(df["final_score"].between(min_score, max_score))]
    if search:
        df_filtered = df_filtered[
            df_filtered["left_REC_CODE"].astype(str).str.contains(search)
            | df_filtered["right_report_id"].astype(str).str.contains(search)
        ]

    if mode == "Single":
        st.write(f"Remaining: {len(df_filtered)}")
        if df_filtered.empty:
            st.success("No records to verify.")
            return
        idx = st.session_state.get("idx", 0)
        row = df_filtered.iloc[idx]
        col1, col2 = st.columns(2)
        col1.write("### Left")
        col1.json(row[[c for c in row.index if c.startswith("left_")]].to_dict())
        col2.write("### Right")
        col2.json(row[[c for c in row.index if c.startswith("right_")]].to_dict())
        st.write(f"Score: {row['final_score']:.3f}")

        def mark(label: int) -> None:
            nonlocal idx
            labels.loc[len(labels)] = [row.df1_index, row.df2_index, label]
            save_partial(labels)
            if len(labels) % 10 == 0:
                save_partial(labels)
            idx += 1
            st.session_state["idx"] = idx

        colm, coln, colu = st.columns(3)
        colm.button("Match (M)", on_click=mark, args=(1,), key="match")
        coln.button("Non-match (N)", on_click=mark, args=(0,), key="nonmatch")
        colu.button("Uncertain (U)", on_click=mark, args=(-1,), key="uncertain")

    else:  # Batch mode
        st.write("Select labels for each record")
        df_batch = df_filtered.head(10).copy()
        for i, row in df_batch.iterrows():
            st.write(f"Pair {i} - Score {row['final_score']:.3f}")
            choice = st.radio(
                f"Label {i}", ["Unlabeled", "Match", "Non-match", "Uncertain"], index=0, key=f"lab_{i}"
            )
            if choice != "Unlabeled":
                label_map = {"Match": 1, "Non-match": 0, "Uncertain": -1}
                labels = labels.append({
                    "df1_index": row.df1_index,
                    "df2_index": row.df2_index,
                    "label": label_map[choice],
                }, ignore_index=True)
        if st.button("Save batch"):
            save_partial(labels)
            st.success("Saved")

    progress = len(labels) / len(df) if len(df) else 0
    st.progress(progress)
    if st.button("Finish"):
        labels = labels[labels["label"] != -1]
        labels.to_csv(FINISHED_PATH, index=False)
        st.success("Final labels saved.")
    st.download_button("Download partial CSV", data=labels.to_csv(index=False), file_name="partial_verified_matches.csv")


if __name__ == "__main__":
    main()
