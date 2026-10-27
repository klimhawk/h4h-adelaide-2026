"""Battery Race: who is winning South Australia's home-battery boom?

Local one-page Streamlit app built to APP-SPEC.md. Reads only the files in data/ and
GEMINI_API_KEY from .env. Nothing is fetched from Snowflake while the app runs.
"""

import html
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

HERE = Path(__file__).parent
DATA = HERE / "data"
JOINED_CSV = DATA / "sa_postcode_battery_seifa.csv"
MONTHLY_CSV = DATA / "sa_battery_monthly.csv"
SHAPES_GEOJSON = DATA / "sa_postal_areas_simplified.geojson"

GEMMA_MODEL = "gemma-4-26b-a4b-it"
GEMMA_UNAVAILABLE = "Gemma is not available right now, try again in a minute"
BAD_INPUT = "Please enter a 4-digit postcode"
NO_DATA = "no data"

# Two colours plus grey: a blue sequential scale (colour-blind safe) and an orange accent.
BLUES = [[0.0, "#deebf7"], [0.5, "#6baed6"], [1.0, "#08306b"]]
ACCENT = "#e6550d"
GREY = "#bdbdbd"
BAR_BLUE = "#2171b5"

PROMPT = (
    "You explain home-battery data for one South Australian postcode to a local resident. "
    "Use only these facts: postcode {postcode}; batteries installed since July 2025: {batteries}; "
    "rank {rank} of {n} SA postcodes; batteries per 100 solar homes: {rate} (SA median {median}); "
    "disadvantage decile {decile} (1 = most disadvantaged, 10 = least; \"no data\" if missing). "
    "Write two or three plain sentences. Do not name suburbs, give advice, or add any fact not listed."
)

st.set_page_config(page_title="Battery Race", layout="wide")
st.markdown(
    """
    <style>
      html, body, [class*="css"], .stMarkdown p, .stCaption, label { font-size: 20px; }
      h1 { font-size: 2.3rem !important; }
      h2 { font-size: 1.7rem !important; }
      [data-testid="stMetricValue"] { font-size: 2.6rem; }
      [data-testid="stMetricLabel"] p { font-size: 1.1rem; }
      .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 100%; }
      .card { border: 2px solid #08306b; border-radius: 8px; padding: 0.7rem 1rem; margin-top: 0.5rem; }
      .card div { font-size: 1.15rem; line-height: 1.6; }
      .gemma { border: 2px solid #e6550d; border-radius: 8px; padding: 0.7rem 1rem; margin-top: 0.8rem; }
      .gemma .note { color: #777; font-size: 0.85rem; margin-top: 0.3rem; }
      .gemma .label { color: #e6550d; font-weight: 700; font-size: 1rem; margin-bottom: 0.3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- data ----------

@st.cache_data
def load_data():
    joined = pd.read_csv(JOINED_CSV, dtype=str, keep_default_na=False)
    joined.columns = [c.lower() for c in joined.columns]
    joined["batteries"] = joined["batteries_since_jul2025"].astype(int)
    joined["solar"] = joined["solar_total"].astype(int)
    # Rate recomputed per the data rules: NaN ("no data") where solar is 0.
    joined["rate"] = np.where(joined["solar"] > 0, joined["batteries"] / joined["solar"].where(joined["solar"] > 0) * 100, np.nan)
    # Blank decile = no SEIFA value; blank population = no postal area. Keep as NaN, never 0.
    joined["decile"] = pd.to_numeric(joined["irsd_decile_aus"].replace("", np.nan))
    joined["population"] = pd.to_numeric(joined["population"].replace("", np.nan))
    joined["rank"] = joined["batteries"].rank(ascending=False, method="min").astype(int)
    joined = joined.set_index("postcode", drop=False).rename_axis(None)

    monthly = pd.read_csv(MONTHLY_CSV, dtype=str, keep_default_na=False)
    monthly.columns = [c.lower() for c in monthly.columns]
    monthly["installations"] = monthly["installations"].astype(int)
    months = sorted(monthly["month"].unique())
    # SA postcodes missing from the monthly file have 0 batteries in every month.
    wide = (monthly.pivot(index="postcode", columns="month", values="installations")
            .reindex(index=joined.index, columns=months).fillna(0).astype(int))
    cumulative = wide.cumsum(axis=1)

    with open(SHAPES_GEOJSON) as f:
        shapes = json.load(f)
    for feat in shapes["features"]:
        feat["id"] = str(feat["properties"]["postcode"])
    return joined, cumulative, months, shapes


joined, cumulative, months, shapes = load_data()
N = len(joined)
MEDIAN_RATE = float(np.nanmedian(joined["rate"]))
leader = joined.sort_values(["batteries", "postcode"], ascending=[False, True]).iloc[0]
near_median = (joined[joined["rate"].notna() & (joined["postcode"] != leader["postcode"])]
               .assign(gap=lambda d: (d["rate"] - MEDIAN_RATE).abs())
               .sort_values(["gap", "postcode"]).iloc[0])
no_data_example = joined[joined["match_status"] == "NO_POSTAL_AREA"].iloc[0]


def fmt_rate(v):
    return NO_DATA if pd.isna(v) else f"{v:.1f}"


def fmt_decile(v):
    return NO_DATA if pd.isna(v) else str(int(v))


def ordinal(n):
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def month_label(m):
    return pd.Timestamp(m + "-01").strftime("%B %Y")


# ---------- Gemma ----------

def retry_gemma(pc):
    st.session_state.setdefault("gemma_failed", {}).pop(pc, None)


def ask_gemma(row):
    """One call per new postcode; answers cached for the session.

    A failure is remembered too, so reruns do not call again; only the "Try again"
    button (retry_gemma) clears it. Returns (text, status note).
    """
    cache = st.session_state.setdefault("gemma_cache", {})
    failed = st.session_state.setdefault("gemma_failed", {})
    pc = row["postcode"]
    if pc in cache:
        return cache[pc]
    if pc in failed:
        return GEMMA_UNAVAILABLE, failed[pc]
    load_dotenv(HERE / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        failed[pc] = "No Gemini API key found in .env"
        return GEMMA_UNAVAILABLE, failed[pc]
    prompt = PROMPT.format(
        postcode=pc, batteries=f"{row['batteries']:,}", rank=int(row["rank"]), n=N,
        rate=fmt_rate(row["rate"]), median=f"{MEDIAN_RATE:.1f}", decile=fmt_decile(row["decile"]),
    )
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        started = time.perf_counter()
        st.session_state["gemma_calls"] = st.session_state.get("gemma_calls", 0) + 1
        # Gemma 4 thinks by default (900 to 3,100 hidden tokens, 22 to 69 s per answer in tests);
        # "minimal" brings it to about 3 s. The prompt itself is unchanged.
        resp = client.models.generate_content(
            model=GEMMA_MODEL, contents=prompt,
            config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="minimal")))
        text = (resp.text or "").strip()
        if not text:
            failed[pc] = "Gemma returned an empty answer"
            return GEMMA_UNAVAILABLE, failed[pc]
    except Exception as e:
        # Server console only; the key is redacted and never shown on the page.
        print(f"Gemma call failed: {type(e).__name__}: {str(e).replace(api_key, '<KEY>')[:300]}", file=sys.stderr)
        code = getattr(e, "code", None)
        if code == 429:
            failed[pc] = "Google rate limit reached (429)"
        elif isinstance(code, int) and code >= 500:
            failed[pc] = f"Google returned a server error ({code})"
        else:
            failed[pc] = f"Request failed ({type(e).__name__})"
        return GEMMA_UNAVAILABLE, failed[pc]
    cache[pc] = (text, f"Answered in {time.perf_counter() - started:.1f} s")
    return cache[pc]


# ---------- 1. header ----------

st.title("Battery Race: who is winning South Australia's home-battery boom?")
st.markdown("Home batteries installed since July 2025, by postcode")
h1, h2, h3 = st.columns(3)
h1.metric("SA batteries since July 2025", f"{joined['batteries'].sum():,}")
h2.metric("Postcodes in the race", f"{N:,}")
h3.metric("Leading postcode", f"{leader['postcode']}: {leader['batteries']:,}")

# ---------- 2. your postcode / 3. map ----------

if "pc_input" not in st.session_state:
    st.session_state["pc_input"] = ""
    st.session_state["selected"] = None


def choose(pc):
    st.session_state["pc_input"] = pc
    st.session_state["selected"] = pc


def submit():
    st.session_state["selected"] = st.session_state["pc_input"]


left, right = st.columns([1, 2], gap="large")
highlight = None

with left:
    st.subheader("Your postcode")
    st.text_input("Type your postcode", key="pc_input", on_change=submit, max_chars=10)
    st.markdown("Or try an example:")
    st.button(f"{leader['postcode']}: the leader", on_click=choose, args=(leader["postcode"],), width="stretch")
    st.button(f"{near_median['postcode']}: near the SA median", on_click=choose, args=(near_median["postcode"],), width="stretch")
    st.button(f"{no_data_example['postcode']}: no data", on_click=choose, args=(no_data_example["postcode"],), width="stretch")

    raw = st.session_state.get("selected")
    if raw is not None:
        pc = raw.strip()
        if not re.fullmatch(r"\d{4}", pc):
            st.warning(BAD_INPUT)
        elif pc not in joined.index:
            st.info(f"Postcode {pc} is not in the South Australian data.")
        else:
            row = joined.loc[pc]
            highlight = pc
            st.markdown(
                f"""<div class="card">
                <div><b>Postcode {pc}</b></div>
                <div>Batteries since July 2025: <b>{row['batteries']:,}</b></div>
                <div>Batteries per 100 solar homes: <b>{fmt_rate(row['rate'])}</b></div>
                <div>Rank in SA: <b>{ordinal(int(row['rank']))} of {N}</b></div>
                <div>Disadvantage decile: <b>{fmt_decile(row['decile'])}</b> <span style="font-size:0.9rem;color:#555">(1 = most disadvantaged, 10 = least)</span></div>
                </div>""",
                unsafe_allow_html=True,
            )
            note = None
            if row["match_status"] == "NO_POSTAL_AREA":
                answer = (f"Postcode {pc} has no ABS postal area, so there is no disadvantage decile "
                          "or map shape for it. Gemma is not asked about postcodes without data.")
            else:
                with st.spinner("Asking Gemma 4...", show_time=True):
                    answer, note = ask_gemma(row)
            note_html = f'<div class="note">{html.escape(note)}</div>' if note else ""
            st.markdown(
                f'<div class="gemma"><div class="label">Explained by Gemma 4</div><div>{html.escape(answer)}</div>{note_html}</div>',
                unsafe_allow_html=True,
            )
            if answer == GEMMA_UNAVAILABLE:
                st.button("Try again", on_click=retry_gemma, args=(pc,), key=f"retry_{pc}")
    st.caption(f"Gemma calls this session: {st.session_state.get('gemma_calls', 0)}")

with right:
    st.subheader("Map: batteries per 100 solar homes")
    shape_ids = [f["id"] for f in shapes["features"]]
    m = joined.reindex(shape_ids)
    m["postcode"] = shape_ids
    has = m["rate"].notna()
    hover = "<b>%{customdata[0]}</b><br>Batteries: %{customdata[1]}<br>Per 100 solar homes: %{customdata[2]}<br>Disadvantage decile: %{customdata[3]}<extra></extra>"

    def custom(df):
        return np.stack([
            df["postcode"],
            df["batteries"].map(lambda v: NO_DATA if pd.isna(v) else f"{int(v):,}"),
            df["rate"].map(fmt_rate),
            df["decile"].map(fmt_decile),
        ], axis=-1)

    fig_map = go.Figure()
    if (~has).any():
        nd = m[~has]
        fig_map.add_trace(go.Choroplethmap(
            geojson=shapes, locations=nd["postcode"], z=np.zeros(len(nd)),
            colorscale=[[0, GREY], [1, GREY]], showscale=False, marker_line_width=0.5,
            marker_line_color="white", customdata=custom(nd), hovertemplate=hover, name="no data"))
    v = m[has]
    fig_map.add_trace(go.Choroplethmap(
        geojson=shapes, locations=v["postcode"], z=v["rate"], colorscale=BLUES,
        zmin=0, zmax=float(np.nanpercentile(v["rate"], 98)), marker_line_width=0.5,
        marker_line_color="white", customdata=custom(v), hovertemplate=hover,
        colorbar=dict(title=dict(text="Per 100<br>solar homes"), thickness=18, len=0.8)))
    if highlight is not None and highlight in shape_ids:
        fig_map.add_trace(go.Choroplethmap(
            geojson=shapes, locations=[highlight], z=[0],
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
            marker_line_width=4, marker_line_color=ACCENT, hoverinfo="skip"))
    fig_map.update_layout(
        map=dict(style="carto-positron", center=dict(lat=-34.93, lon=138.60), zoom=8.3),
        margin=dict(l=0, r=0, t=0, b=0), height=470,
        annotations=[dict(text="Grey = no data", x=0.01, y=0.01, xref="paper", yref="paper",
                          showarrow=False, bgcolor="white", font=dict(size=14))])
    st.plotly_chart(fig_map, width="stretch", config={"scrollZoom": True})

# ---------- 4. the race ----------

st.subheader("The race: top 15 postcodes by cumulative batteries since July 2025")
TOP = 15


def frame_data(month):
    col = cumulative[month].reset_index()
    col.columns = ["postcode", "total"]
    top = col.sort_values(["total", "postcode"], ascending=[False, True]).head(TOP).reset_index(drop=True)
    top["pos"] = np.arange(TOP, 0, -1)  # rank 1 at the top
    top["label"] = top["postcode"] + "  " + top["total"].map("{:,}".format)
    top["colour"] = np.where(top["postcode"] == highlight, ACCENT, BAR_BLUE)
    return top


def bar(top):
    return go.Bar(x=top["total"], y=top["pos"], orientation="h", text=top["label"],
                  textposition="outside", cliponaxis=False, marker_color=top["colour"],
                  hovertemplate="%{text}<extra></extra>", textfont=dict(size=16))


xmax = float(cumulative[months[-1]].max()) * 1.18
first = frame_data(months[0])
frames = [go.Frame(data=[bar(frame_data(mo))], name=mo,
                   layout=go.Layout(title=dict(text=month_label(mo), font=dict(size=24), x=0.02))) for mo in months]
fig_race = go.Figure(data=[bar(first)], frames=frames)
fig_race.update_layout(
    title=dict(text=month_label(months[0]), font=dict(size=24), x=0.02),
    xaxis=dict(range=[0, xmax], title="Cumulative batteries", tickfont=dict(size=15)),
    yaxis=dict(range=[0.4, TOP + 0.6], showticklabels=False),
    height=560, margin=dict(l=10, r=30, t=60, b=10), showlegend=False,
    updatemenus=[dict(type="buttons", direction="left", x=0.0, y=-0.14, xanchor="left",
                      buttons=[
                          dict(label="Play", method="animate",
                               args=[None, dict(frame=dict(duration=700, redraw=True),
                                                transition=dict(duration=300), fromcurrent=True)]),
                          dict(label="Pause", method="animate",
                               args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
                      ], font=dict(size=16))],
    sliders=[dict(active=0, x=0.16, y=-0.08, len=0.84, currentvalue=dict(prefix="Month: ", font=dict(size=16)),
                  steps=[dict(label=pd.Timestamp(mo + "-01").strftime("%b %y"), method="animate",
                              args=[[mo], dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                               transition=dict(duration=0))]) for mo in months])],
)
st.plotly_chart(fig_race, width="stretch")

# ---------- 5. is it the well-off? ----------

st.subheader("Is it the well-off?")
st.markdown(
    "Each dot is a postcode. The **disadvantage decile** ranks Australian areas from 1 (most "
    "disadvantaged 10%) to 10 (least), using the ABS 2021 Index of Relative Socio-economic "
    "Disadvantage (part of SEIFA)."
)
sc = joined[joined["decile"].notna() & joined["rate"].notna()]
slope, intercept = np.polyfit(sc["decile"], sc["rate"], 1)
xs = np.array([1, 10])
hi_avg = sc.loc[sc["decile"] >= 8, "rate"].mean()
lo_avg = sc.loc[sc["decile"] <= 3, "rate"].mean()
jitter = np.random.default_rng(0).uniform(-0.18, 0.18, len(sc))
fig_sc = go.Figure([
    go.Scatter(x=sc["decile"] + jitter, y=sc["rate"], mode="markers",
               marker=dict(color=BAR_BLUE, size=9, opacity=0.65),
               customdata=np.stack([sc["postcode"], sc["decile"].astype(int), sc["rate"].round(1)], axis=-1),
               hovertemplate="<b>%{customdata[0]}</b><br>Disadvantage decile %{customdata[1]}<br>%{customdata[2]} per 100 solar homes<extra></extra>",
               name="postcode"),
    go.Scatter(x=xs, y=slope * xs + intercept, mode="lines", line=dict(color=ACCENT, width=4),
               hoverinfo="skip", name="trend"),
])
fig_sc.update_layout(
    xaxis=dict(title="Disadvantage decile (1 = most disadvantaged, 10 = least)", tickmode="linear", dtick=1,
               range=[0.5, 10.5], tickfont=dict(size=15)),
    yaxis=dict(title="Batteries per 100 solar homes", tickfont=dict(size=15)),
    height=440, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
st.plotly_chart(fig_sc, width="stretch")
st.markdown(
    f"Postcodes in the least disadvantaged deciles 8 to 10 average **{hi_avg:.1f}** batteries per 100 solar homes, "
    f"against **{lo_avg:.1f}** in the most disadvantaged deciles 1 to 3. The trend line rises by {slope:.2f} per decile "
    f"across the {len(sc)} postcodes with data. This shows a pattern, not a cause."
)

# ---------- glossary ----------

st.subheader("What the terms mean")
st.markdown(
    """
- **Disadvantage decile**: how disadvantaged an area is compared with the rest of Australia.
  The ABS scores every postal area from 2021 Census answers about things like low income,
  unemployment, low education and low-skilled jobs, ranks them, and splits them into ten equal
  groups. **1** is the most disadvantaged tenth of areas, **10** the least. It describes the
  area, not any one household.
- **SEIFA**: Socio-Economic Indexes for Areas, the ABS family of indexes this decile comes from
  (here, the Index of Relative Socio-economic Disadvantage).
- **Batteries per 100 solar homes**: batteries installed since July 2025 for every 100 solar
  installations ever recorded in the postcode. A rough measure of how quickly solar homes
  are adding batteries.
- **Rank**: position among South Australian postcodes by batteries installed since July 2025
  (1 = most).
- **Postcode and postal area**: battery data comes by postcode; the decile and map shapes come
  by ABS postal area, which closely follows postcodes. A few postcodes (for example PO box
  only ones) have no postal area, so they show "no data".
"""
)

# ---------- 6. footer ----------

st.divider()
st.caption(
    "Battery data starts 1 July 2025, when batteries joined the Small-scale Renewable Energy Scheme; "
    "recent months exclude applications still pending. "
    "Data: Clean Energy Regulator small-scale installations (CC BY 4.0); ABS SEIFA 2021 and ABS "
    "postal-area boundaries via Data Army Intel on Snowflake Marketplace. Snowflake Marketplace rows are not "
    "redistributed. AI: Gemma 4 through the Gemini API."
)
