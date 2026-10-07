import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import Pitch
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM CSS (DYNAMIC ANIMATION EFFECTS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pro Football Performance & Scouting Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Styling */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Moving Media Card Animation */
    .media-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.6);
        animation: floatCard 3s ease-in-out infinite alternate;
        transition: transform 0.3s ease;
    }
    
    @keyframes floatCard {
        0% { transform: translateY(0px); border-color: #3b82f6; }
        100% { transform: translateY(-8px); border-color: #10b981; }
    }
    
    .media-card img {
        border-radius: 8px;
        width: 100%;
        max-height: 220px;
        object-fit: cover;
    }
    
    /* Metric Card Customization */
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA GENERATION & ANONYMIZATION LAYER
# -----------------------------------------------------------------------------
@st.cache_data
def load_annotated_football_data():
    """
    Generates a realistic, multi-match tactical and athletic dataset.
    Player names and Club IDs are anonymized for data privacy compliance.
    """
    np.random.seed(42)
    players = [
        {"id": "PLR_01", "alias": "Striker Alpha", "pos": "FW", "animated_media": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Zydms1ZGgxOGo2Ynh2cGppbzZ3dnh6dzM5NndxYjE5bmJybndmZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKSx0g7Rq1sAp3y/giphy.gif"},
        {"id": "PLR_02", "alias": "Winger Beta", "pos": "AM", "animated_media": "https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif"},
        {"id": "PLR_03", "alias": "Playmaker Gamma", "pos": "CM", "animated_media": "https://media.giphy.com/media/26n6Wywq41KAzdK80/giphy.gif"},
        {"id": "PLR_04", "alias": "Fullback Delta", "pos": "DF", "animated_media": "https://media.giphy.com/media/xT1XGzAnABSyI46448/giphy.gif"},
        {"id": "PLR_05", "alias": "Anchor Epsilon", "pos": "DM", "animated_media": "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif"}
    ]
    
    perf_records = []
    for p in players:
        perf_records.append({
            "Player_ID": p["id"],
            "Alias": p["alias"],
            "Position": p["pos"],
            "Media_URL": p["animated_media"],
            "Matches_Played": np.random.randint(15, 25),
            "Minutes_90s": round(np.random.uniform(12.0, 22.0), 1),
            "xG": round(np.random.uniform(0.1, 0.85), 2),       # per 90
            "xA": round(np.random.uniform(0.05, 0.60), 2),      # per 90
            "Prog_Passes": np.random.randint(2, 9),             # per 90
            "Prog_Carries": np.random.randint(1, 8),            # per 90
            "Sprint_Distance_m": np.random.randint(800, 1400), # per 90
            "High_Intensity_Runs": np.random.randint(30, 75),
            "Pressures_Successful": round(np.random.uniform(3.5, 12.0), 1)
        })
    df_perf = pd.DataFrame(perf_records)

    events = []
    for p in players:
        n_events = np.random.randint(80, 150)
        for _ in range(n_events):
            x = np.random.uniform(60, 118) if p["pos"] in ["FW", "AM"] else np.random.uniform(20, 100)
            y = np.random.uniform(10, 70)
            event_type = np.random.choice(["Shot", "Pass", "Dribble", "Tackle"], p=[0.15, 0.55, 0.18, 0.12])
            xg_val = round(np.random.beta(1, 5), 2) if event_type == "Shot" else 0.0
            is_goal = True if event_type == "Shot" and xg_val > 0.35 and np.random.rand() > 0.5 else False
            
            events.append({
                "Player_ID": p["id"],
                "Alias": p["alias"],
                "X": x,
                "Y": y,
                "Type": event_type,
                "xG": xg_val,
                "Is_Goal": is_goal
            })
    df_events = pd.DataFrame(events)

    return df_perf, df_events

df_perf, df_events = load_annotated_football_data()

# Helper function to compute radar/pizza values
def get_radar_values(row):
    return [
        row['xG'] * 100,
        row['xA'] * 100,
        row['Prog_Passes'] * 10,
        row['Prog_Carries'] * 10,
        (row['Sprint_Distance_m'] / 1400) * 100,
        row['Pressures_Successful'] * 8
    ]

# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.title("⚽ Tactical Intelligence")
st.sidebar.caption("Secured & Anonymized Dataset v2.4")

nav_option = st.sidebar.radio(
    "Select Module:",
    [
        "1. Player Profile & Moving Visuals", 
        "2. Tactical & Event Analysis", 
        "3. Squad Recruitment Matrix",
        "4. Side-by-Side Comparison"
    ]
)

st.sidebar.markdown("---")

# -----------------------------------------------------------------------------
# 4. MODULE 1: PLAYER PROFILE & MOVING VISUALS
# -----------------------------------------------------------------------------
if nav_option == "1. Player Profile & Moving Visuals":
    selected_player_alias = st.sidebar.selectbox("Select Player:", df_perf["Alias"].unique())
    selected_player_data = df_perf[df_perf["Alias"] == selected_player_alias].iloc[0]

    st.title("🏃 Player Performance Profile")
    st.markdown("Combines physical output, expected metrics (xG/xA), and real-time animation clips.")

    col_media, col_stats = st.columns([1, 2])

    with col_media:
        st.markdown(f"""
            <div class="media-card">
                <img src="{selected_player_data['Media_URL']}" alt="Player Action Clip">
                <h3 style="margin-top:10px; color:#10b981;">{selected_player_data['Alias']}</h3>
                <p style="margin:0; color:#9ca3af;">ID: {selected_player_data['Player_ID']} | Pos: {selected_player_data['Position']}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_stats:
        m1, m2, m3 = st.columns(3)
        m1.metric("xG per 90", f"{selected_player_data['xG']}")
        m2.metric("xA per 90", f"{selected_player_data['xA']}")
        m3.metric("Successful Pressures", f"{selected_player_data['Pressures_Successful']}")

        m4, m5, m6 = st.columns(3)
        m4.metric("Sprint Distance (m)", f"{selected_player_data['Sprint_Distance_m']} m")
        m5.metric("High Intensity Runs", f"{selected_player_data['High_Intensity_Runs']}")
        m6.metric("Prog. Pass + Carry", f"{selected_player_data['Prog_Passes'] + selected_player_data['Prog_Carries']}")

    st.markdown("---")
    st.subheader("Attributes Pizza Radar Chart")
    
    categories = ['xG p90', 'xA p90', 'Prog Passes', 'Prog Carries', 'Sprint Dist', 'Pressures']
    player_values = get_radar_values(selected_player_data)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=player_values,
        theta=categories,
        fill='toself',
        name=selected_player_data['Alias'],
        line_color='#10b981'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. MODULE 2: TACTICAL & EVENT ANALYSIS
# -----------------------------------------------------------------------------
elif nav_option == "2. Tactical & Event Analysis":
    selected_player_alias = st.sidebar.selectbox("Select Player:", df_perf["Alias"].unique())
    
    st.title("🎯 Pitch Location & Event Spatial Analysis")
    st.markdown("Visualizing tactical actions on pitch geometry using mplsoccer.")

    player_events = df_events[df_events["Alias"] == selected_player_alias]

    col_pitch1, col_pitch2 = st.columns(2)

    with col_pitch1:
        st.subheader("Shot Map & Chance Quality (xG)")
        shots = player_events[player_events["Type"] == "Shot"]
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#111827', line_color='#374151')
        fig, ax = pitch.draw(figsize=(6, 4))

        if not shots.empty:
            no_goals = shots[shots["Is_Goal"] == False]
            pitch.scatter(no_goals.X, no_goals.Y, s=no_goals.xG * 600,
                          color='#ef4444', alpha=0.6, ax=ax, label='Miss/Saved')
            goals = shots[shots["Is_Goal"] == True]
            pitch.scatter(goals.X, goals.Y, s=goals.xG * 600,
                          color='#10b981', marker='*', ax=ax, label='Goal')

        ax.legend(facecolor='#111827', labelcolor='white', loc='lower left')
        st.pyplot(fig)

    with col_pitch2:
        st.subheader("Spatial Heatmap (Positional Occupancy)")
        pitch_kde = Pitch(pitch_type='statsbomb', pitch_color='#111827', line_color='#374151')
        fig_kde, ax_kde = pitch_kde.draw(figsize=(6, 4))
        
        if len(player_events) > 5:
            pitch_kde.kdeplot(player_events.X, player_events.Y, ax=ax_kde,
                              cmap='hot', fill=True, levels=100, alpha=0.7)
        st.pyplot(fig_kde)

# -----------------------------------------------------------------------------
# 6. MODULE 3: SQUAD RECRUITMENT MATRIX
# -----------------------------------------------------------------------------
elif nav_option == "3. Squad Recruitment Matrix":
    st.title("📊 Multi-Player Tactical & Recruitment Scouting")
    st.markdown("Compare squad targets across offensive output and pressing metrics.")

    fig_scatter = px.scatter(
        df_perf,
        x="xA",
        y="xG",
        size="Sprint_Distance_m",
        color="Position",
        hover_name="Alias",
        text="Alias",
        title="Offensive Output Matrix (xG vs xA | Size = Sprint Distance)",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Anonymized Squad Metrics")
    st.dataframe(
        df_perf.drop(columns=["Media_URL"]),
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# 7. MODULE 4: SIDE-BY-SIDE PLAYER COMPARISON
# -----------------------------------------------------------------------------
elif nav_option == "4. Side-by-Side Comparison":
    st.title("⚔️ Side-by-Side Player Head-to-Head")
    st.markdown("Direct comparison across profile, physical work, expected metrics, and shot profiles.")

    # Player Selectors in Sidebar
    player_options = list(df_perf["Alias"].unique())
    p1_alias = st.sidebar.selectbox("Select Player 1:", player_options, index=0)
    
    # Ensure Player 2 defaults to a different player
    p2_default_idx = 1 if len(player_options) > 1 else 0
    p2_alias = st.sidebar.selectbox("Select Player 2:", player_options, index=p2_default_idx)

    p1_data = df_perf[df_perf["Alias"] == p1_alias].iloc[0]
    p2_data = df_perf[df_perf["Alias"] == p2_alias].iloc[0]

    # --- 1. MEDIA CARDS ---
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown(f"""
            <div class="media-card" style="border-color: #10b981;">
                <img src="{p1_data['Media_URL']}" alt="Player 1 Clip">
                <h3 style="margin-top:10px; color:#10b981;">{p1_data['Alias']}</h3>
                <p style="margin:0; color:#9ca3af;">ID: {p1_data['Player_ID']} | Pos: {p1_data['Position']}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown(f"""
            <div class="media-card" style="border-color: #3b82f6;">
                <img src="{p2_data['Media_URL']}" alt="Player 2 Clip">
                <h3 style="margin-top:10px; color:#3b82f6;">{p2_data['Alias']}</h3>
                <p style="margin:0; color:#9ca3af;">ID: {p2_data['Player_ID']} | Pos: {p2_data['Position']}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- 2. STATISTICAL COMPARISON TABLE ---
    st.subheader("📊 Key Metrics Breakdown")
    
    metrics = [
        ("xG per 90", "xG"),
        ("xA per 90", "xA"),
        ("Progressive Passes / 90", "Prog_Passes"),
        ("Progressive Carries / 90", "Prog_Carries"),
        ("Sprint Distance (m)", "Sprint_Distance_m"),
        ("High Intensity Runs", "High_Intensity_Runs"),
        ("Successful Pressures", "Pressures_Successful")
    ]

    comp_rows = []
    for label, col_key in metrics:
        v1 = p1_data[col_key]
        v2 = p2_data[col_key]
        diff = round(v1 - v2, 2)
        winner = p1_data['Alias'] if v1 > v2 else (p2_data['Alias'] if v2 > v1 else "Tie")
        
        comp_rows.append({
            "Metric": label,
            f"{p1_alias}": v1,
            f"{p2_alias}": v2,
            "Difference": diff,
            "Advantage": winner
        })

    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True)

    # --- 3. OVERLAY RADAR CHART ---
    st.markdown("---")
    st.subheader("🕸️ Attribute Overlay Radar Chart")

    categories = ['xG p90', 'xA p90', 'Prog Passes', 'Prog Carries', 'Sprint Dist', 'Pressures']
    p1_vals = get_radar_values(p1_data)
    p2_vals = get_radar_values(p2_data)

    fig_comp_radar = go.Figure()

    fig_comp_radar.add_trace(go.Scatterpolar(
        r=p1_vals,
        theta=categories,
        fill='toself',
        name=p1_alias,
        line_color='#10b981',
        opacity=0.6
    ))

    fig_comp_radar.add_trace(go.Scatterpolar(
        r=p2_vals,
        theta=categories,
        fill='toself',
        name=p2_alias,
        line_color='#3b82f6',
        opacity=0.6
    ))

    fig_comp_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig_comp_radar, use_container_width=True)

    # --- 4. SHOT MAP COMPARISON ---
    st.markdown("---")
    st.subheader("🎯 Shot Location Comparison")

    col_shot1, col_shot2 = st.columns(2)

    p1_shots = df_events[(df_events["Alias"] == p1_alias) & (df_events["Type"] == "Shot")]
    p2_shots = df_events[(df_events["Alias"] == p2_alias) & (df_events["Type"] == "Shot")]

    with col_shot1:
        st.markdown(f"**{p1_alias} Shot Map**")
        pitch1 = Pitch(pitch_type='statsbomb', pitch_color='#111827', line_color='#374151')
        fig1, ax1 = pitch1.draw(figsize=(5, 3.5))

        if not p1_shots.empty:
            no_goals1 = p1_shots[p1_shots["Is_Goal"] == False]
            pitch1.scatter(no_goals1.X, no_goals1.Y, s=no_goals1.xG * 500, color='#ef4444', alpha=0.6, ax=ax1, label='Miss/Saved')
            goals1 = p1_shots[p1_shots["Is_Goal"] == True]
            pitch1.scatter(goals1.X, goals1.Y, s=goals1.xG * 500, color='#10b981', marker='*', ax=ax1, label='Goal')

        ax1.legend(facecolor='#111827', labelcolor='white', loc='lower left')
        st.pyplot(fig1)

    with col_shot2:
        st.markdown(f"**{p2_alias} Shot Map**")
        pitch2 = Pitch(pitch_type='statsbomb', pitch_color='#111827', line_color='#374151')
        fig2, ax2 = pitch2.draw(figsize=(5, 3.5))

        if not p2_shots.empty:
            no_goals2 = p2_shots[p2_shots["Is_Goal"] == False]
            pitch2.scatter(no_goals2.X, no_goals2.Y, s=no_goals2.xG * 500, color='#ef4444', alpha=0.6, ax=ax2, label='Miss/Saved')
            goals2 = p2_shots[p2_shots["Is_Goal"] == True]
            pitch2.scatter(goals2.X, goals2.Y, s=goals2.xG * 500, color='#3b82f6', marker='*', ax=ax2, label='Goal')

        ax2.legend(facecolor='#111827', labelcolor='white', loc='lower left')
        st.pyplot(fig2)