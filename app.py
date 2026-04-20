import streamlit as st
import os
import random
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from dotenv import load_dotenv
import nav_algorithm

# Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="WSO2 Unitree Go2 Nav Simulator", layout="wide")

st.title("Dynamic Quadruped Navigation (Nav2) Simulator")
st.markdown("*Simulating ROS 2 Global Path Planning & WSO2 AI Gateway Integration*")

# --- SESSION STATE SETUP ---
if "start_node" not in st.session_state:
    st.session_state.start_node = 0
if "goal_node" not in st.session_state:
    st.session_state.goal_node = 35
if "barriers" not in st.session_state:
    all_nodes = set(range(36)) - {0, 35}
    st.session_state.barriers = set(random.sample(list(all_nodes), 6))
if "path" not in st.session_state:
    st.session_state.path = []
if "llm_response" not in st.session_state:
    st.session_state.llm_response = ""

# --- LLM DEBUGGING AGENT (WSO2 AI GATEWAY SIMULATION) ---
def get_llm_explanation(path_length, nodes_visited, start, goal):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY not found in .env file."
    
    prompt = (
        f"Act as the internal diagnostic AI of a Unitree Go2 robot dog. "
        f"You just navigated a grid from node {start} to {goal}. "
        f"Your A* algorithm explored {nodes_visited} nodes to find an optimal path of {path_length} steps. "
        f"Explain your pathing logic in 2 short, technical sentences to the WSO2 engineering team."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama-3.1-8b-instant", # FIXED: Updated to Groq's current active model
        "temperature": 0.7
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        # Better error logging to see exactly what went wrong
        error_msg = response.text if response else str(e)
        return f"Error contacting AI Gateway: {error_msg}"

# --- UI CONTROLS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Control Panel")
    
    if st.button("Calculate A* Path"):
        path, visited = nav_algorithm.a_star_search(
            st.session_state.start_node, 
            st.session_state.goal_node, 
            st.session_state.barriers
        )
        st.session_state.path = path
        
        if path:
            st.success(f"Path found! Length: {len(path)} steps.")
            with st.spinner("Querying WSO2 AI Gateway..."):
                st.session_state.llm_response = get_llm_explanation(
                    len(path), len(visited), st.session_state.start_node, st.session_state.goal_node
                )
        else:
            st.error("No path available! The robot is trapped.")
            st.session_state.llm_response = "Diagnostic: Route blocked. Initiating obstacle avoidance failure protocols."

    if st.button("Simulate LiDAR (Drop Obstacle)"):
        available = list(set(range(36)) - st.session_state.barriers - {st.session_state.start_node, st.session_state.goal_node})
        if available:
            new_barrier = random.choice(available)
            st.session_state.barriers.add(new_barrier)
            st.session_state.path = [] 
            st.rerun()

    st.subheader("WSO2 AI Gateway Log")
    st.info(st.session_state.llm_response if st.session_state.llm_response else "Awaiting navigation data...")

# --- ROS 2 COSTMAP VISUALIZATION (MATPLOTLIB) ---
with col2:
    st.subheader("Live Telemetry & Occupancy Grid")
    
    # 0: Empty(White), 1: Path(Cyan), 2: Start(Green), 3: Goal(Red), 4: Barrier(Black)
    grid = np.zeros((nav_algorithm.GRID_SIZE, nav_algorithm.GRID_SIZE))
    
    for b in st.session_state.barriers:
        x, y = nav_algorithm.node_to_xy(b)
        grid[y, x] = 4
        
    for p in st.session_state.path:
        if p != st.session_state.start_node and p != st.session_state.goal_node:
            x, y = nav_algorithm.node_to_xy(p)
            grid[y, x] = 1
            
    sx, sy = nav_algorithm.node_to_xy(st.session_state.start_node)
    grid[sy, sx] = 2
    
    gx, gy = nav_algorithm.node_to_xy(st.session_state.goal_node)
    grid[gy, gx] = 3

    # Create the visual plot
    fig, ax = plt.subplots(figsize=(6, 6))
    cmap = mcolors.ListedColormap(['#f0f2f6', '#00d2ff', '#00ff00', '#ff0000', '#31333F'])
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    ax.imshow(grid, cmap=cmap, norm=norm)
    
    # Draw gridlines to make perfect squares
    ax.grid(which='major', axis='both', linestyle='-', color='gray', linewidth=1)
    ax.set_xticks(np.arange(-0.5, nav_algorithm.GRID_SIZE, 1))
    ax.set_yticks(np.arange(-0.5, nav_algorithm.GRID_SIZE, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    st.pyplot(fig)