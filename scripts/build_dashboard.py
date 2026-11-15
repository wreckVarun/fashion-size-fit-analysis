"""Step 6: build a single self-contained HTML dashboard from the CSVs in outputs/.

The page is written to docs/index.html. GitHub Pages serves the docs/ folder,
so pushing this file publishes the dashboard. Plotly's JavaScript is copied
into the page, so it works offline and needs no other files.
"""
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
PAGE_PATH = os.path.join(ROOT, "docs", "index.html")

# One colour per fit outcome, used the same way in every chart.
SMALL = "#2a78d6"   # blue: "runs small"
LARGE = "#eb6834"   # orange: "runs large"
FIT = "#a3a29b"     # gray: "fit"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"


def read(name):
    return pd.read_csv(os.path.join(OUT, name + ".csv"))


def base_layout(fig, height=400):
    """Apply the same clean look to every chart."""
    fig.update_layout(
        height=height,
        margin=dict(l=110, r=24, t=36, b=52),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=13, color=MUTED),
        hoverlabel=dict(bgcolor="white", font_color=INK, bordercolor=AXIS),
        legend=dict(orientation="h", x=0, y=1.08, xanchor="left", yanchor="bottom", traceorder="normal"),
        bargap=0.3,
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False)
    return fig


def stacked_small_large(df, label_col, title_hover):
    """Horizontal bars: % 'small' and % 'large' stacked, one bar per row of df."""
    fig = go.Figure()
    for col, name, colour in [("small_pct", "Runs small", SMALL), ("large_pct", "Runs large", LARGE)]:
        fig.add_bar(
            y=df[label_col],
            x=df[col],
            name=name,
            orientation="h",
            marker=dict(color=colour, line=dict(color=SURFACE, width=1)),
            customdata=df[["reviews", "misfit_pct"]],
            hovertemplate=(
                f"<b>%{{y}}</b><br>{name}: %{{x:.1f}}% of reviews"
                "<br>All misfits: %{customdata[1]:.1f}%<br>"
                f"{title_hover}: %{{customdata[0]:,}}<extra></extra>"
            ),
        )
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="% of reviews", ticksuffix="%")
    return fig


def chart_category():
    """Chart 1: misfit rate by category."""
    df = read("02_misfit_by_category").sort_values("misfit_pct")  # biggest at the top
    fig = base_layout(stacked_small_large(df, "category", "Reviews"), height=520)
    return fig


def chart_items():
    """Chart 2: every item with 30+ reviews, % small vs % large."""
    df = read("03_items_run_small_or_large")
    fig = go.Figure()
    for flag, colour, size in [("not flagged", FIT, 7), ("runs small", SMALL, 8), ("runs large", LARGE, 8)]:
        part = df[df["flag"] == flag]
        fig.add_scatter(
            x=part["small_pct"],
            y=part["large_pct"],
            mode="markers",
            name=f"{flag.capitalize()} ({len(part):,} items)",
            marker=dict(color=colour, size=size, opacity=0.75, line=dict(color=SURFACE, width=1)),
            customdata=part[["item_id", "category", "reviews"]],
            hovertemplate=(
                "<b>Item %{customdata[0]}</b> (%{customdata[1]})<br>"
                "Says small: %{x:.1f}%<br>Says large: %{y:.1f}%<br>"
                "Reviews: %{customdata[2]:,}<extra></extra>"
            ),
        )
    fig = base_layout(fig, height=480)
    fig.update_layout(margin=dict(l=64))
    fig.update_xaxes(title="% of the item's reviews that say it runs small", ticksuffix="%")
    fig.update_yaxes(title="% that say it runs large", ticksuffix="%")
    return fig


def chart_size():
    """Chart 3: % small and % large by ordered size."""
    df = read("04_misfit_by_size")
    df["size_label"] = "Size " + df["size"].astype(str)
    fig = go.Figure()
    for col, name, colour in [("small_pct", "Runs small", SMALL), ("large_pct", "Runs large", LARGE)]:
        fig.add_scatter(
            x=df["size_label"],
            y=df[col],
            name=name,
            mode="lines+markers",
            line=dict(color=colour, width=2),
            marker=dict(color=colour, size=8, line=dict(color=SURFACE, width=2)),
            customdata=df[["reviews"]],
            hovertemplate=f"{name}: %{{y:.1f}}%<extra></extra>",
        )
    fig = base_layout(fig)
    fig.update_layout(margin=dict(l=64), hovermode="x unified")
    fig.update_xaxes(title="Size ordered (RentTheRunway size code)")
    fig.update_yaxes(title="% of reviews", ticksuffix="%", rangemode="tozero")
    return fig


def chart_body_type():
    """Chart 4: misfit rate by body type."""
    df = read("05_misfit_by_body_type").sort_values("misfit_pct")
    fig = base_layout(stacked_small_large(df, "body_type", "Reviews"), height=360)
    return fig


def chart_rating():
    """Chart 5: share of 5-star ratings by fit outcome."""
    df = read("06_rating_gap")
    names = {"fit": "Fit", "small": "Runs small", "large": "Runs large"}
    colours = {"fit": FIT, "small": SMALL, "large": LARGE}
    df = df.set_index("fit").loc[["fit", "large", "small"]].reset_index()
    fig = go.Figure(go.Bar(
        x=df["fit"].map(names),
        y=df["five_star_pct"],
        marker=dict(color=df["fit"].map(colours), line=dict(color=SURFACE, width=1)),
        text=df["five_star_pct"].map(lambda v: f"{v:.1f}%"),
        textposition="outside",
        textfont=dict(color=INK),
        customdata=df[["avg_rating", "three_or_less_pct", "reviews"]],
        hovertemplate=(
            "<b>%{x}</b><br>5-star: %{y:.1f}%<br>Average: %{customdata[0]:.2f} stars"
            "<br>3 stars or less: %{customdata[1]:.1f}%<br>Reviews: %{customdata[2]:,}<extra></extra>"
        ),
        width=0.5,
    ))
    fig = base_layout(fig, height=380)
    fig.update_layout(margin=dict(l=64), showlegend=False)
    fig.update_yaxes(title="% of reviews rated 5 stars", ticksuffix="%", range=[0, 85])
    return fig


def headline_numbers():
    """The numbers shown in the tiles at the top of the page, all read from outputs/."""
    overall = read("01_misfit_rate_overall").iloc[0]
    total_reviews = int(overall["reviews"])
    reach = read("08_feature_reach")
    rating = read("06_rating_gap").set_index("fit")
    offenders = read("07_repeat_offenders").set_index("misfit_band")
    heavy = offenders.loc[["20-49", "50+"]]
    return [
        (f"{overall['misfit_pct']:.1f}%", f"of {total_reviews:,} reviews say the item ran small or large"),
        (f"{reach['items'].sum():,} items",
         f"flagged as running small or large hold {reach['share_of_all_misfits_pct'].sum():.1f}% of all misfit reviews"),
        (f"{heavy['items_pct'].sum():.1f}% of items",
         f"(those with 20+ misfit reviews) account for {heavy['misfit_share_pct'].sum():.1f}% of misfits"),
        (f"{rating.loc['fit', 'five_star_pct']:.0f}% vs {rating.loc['small', 'five_star_pct']:.0f}%",
         "5-star share when it fit vs when it ran small"),
    ]


SECTIONS = [
    ("Which categories fit worst?",
     "Share of reviews that say the item ran small or large. Categories with 500+ reviews.",
     chart_category),
    ("Which items run small or large?",
     "Each dot is an item with 30+ reviews. Flagged: 25%+ of reviews in one direction, and at least twice the other direction.",
     chart_items),
    ("Small sizes run large, large sizes run small",
     "Fit complaints by the size ordered, for the main sizes (3,000+ reviews each). "
     "The direction flips across the size range.",
     chart_size),
    ("Body type barely matters",
     "Misfit rate by the body type on the reviewer's profile. Every group sits within about 3 points.",
     chart_body_type),
    ("Misfits cost ratings",
     "Share of 5-star ratings by fit outcome. Hover for the average rating.",
     chart_rating),
]


def main():
    tiles = "".join(
        f'<div class="tile"><div class="big">{big}</div><div class="small">{small}</div></div>'
        for big, small in headline_numbers()
    )

    sections = ""
    for i, (title, subtitle, make_chart) in enumerate(SECTIONS, start=1):
        chart_html = make_chart().to_html(full_html=False, include_plotlyjs=False,
                                          config={"displayModeBar": False, "responsive": True})
        sections += f'<section><h2>{i}. {title}</h2><p class="sub">{subtitle}</p>{chart_html}</section>'

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fashion Size Fit Analysis</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ margin: 0; background: {SURFACE}; color: {INK};
         font-family: system-ui, -apple-system, Segoe UI, sans-serif; line-height: 1.5; }}
  main {{ max-width: 1040px; margin: 0 auto; padding: 32px 16px 64px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  h2 {{ font-size: 19px; margin: 0 0 2px; }}
  .intro, .sub, footer {{ color: {MUTED}; }}
  .sub {{ margin: 0 0 4px; font-size: 14px; }}
  .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 24px 0 8px; }}
  .tile {{ border: 1px solid {GRID}; border-radius: 8px; padding: 14px 16px; background: white; }}
  .big {{ font-size: 26px; font-weight: 650; }}
  .small {{ font-size: 14px; color: {MUTED}; }}
  section {{ margin-top: 36px; border-top: 1px solid {GRID}; padding-top: 20px; }}
  a {{ color: {SMALL}; }}
</style>
<script>{get_plotlyjs()}</script>
</head>
<body>
<main>
  <h1>Where do size problems concentrate?</h1>
  <p class="intro">{int(read("01_misfit_rate_overall").loc[0, "reviews"]):,} RentTheRunway reviews, each saying whether the item fit, ran small or ran large.
  Built from the SQL queries in the <a href="https://github.com/wreckVarun/fashion-size-fit-analysis">project repo</a>.</p>
  <div class="tiles">{tiles}</div>
  {sections}
  <footer><p>Data: Clothing Fit Dataset for Size Recommendation (RentTheRunway reviews), Misra et al., RecSys 2018.</p></footer>
</main>
</body>
</html>"""

    os.makedirs(os.path.dirname(PAGE_PATH), exist_ok=True)
    with open(PAGE_PATH, "w") as f:
        f.write(page)
    print(f"Saved {PAGE_PATH} ({os.path.getsize(PAGE_PATH) / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
