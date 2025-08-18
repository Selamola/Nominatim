import pandas as pd
from app.matching import apply_composite_score


def test_composite_scoring_order_changes():
    df = pd.DataFrame([
        {"last_name_sim":0.9,"first_name_sim":0.1,"dob_match":1,"sex_match":1,"address_sim":0.5,"phone_match":0},
        {"last_name_sim":0.1,"first_name_sim":0.9,"dob_match":1,"sex_match":1,"address_sim":0.5,"phone_match":0},
    ])
    weights1 = {
        "last_name_sim":0.35,"first_name_sim":0.30,"dob_match":0.20,
        "sex_match":0.05,"address_sim":0.05,"phone_match":0.05
    }
    apply_composite_score(df, weights1)
    order1 = df.sort_values('composite_score', ascending=False).index.tolist()
    assert order1 == [0, 1]
    weights2 = {
        "last_name_sim":0.10,"first_name_sim":0.70,"dob_match":0.10,
        "sex_match":0.05,"address_sim":0.05,"phone_match":0.0
    }
    df2 = df.copy()
    apply_composite_score(df2, weights2)
    order2 = df2.sort_values('composite_score', ascending=False).index.tolist()
    assert order2 == [1, 0]
