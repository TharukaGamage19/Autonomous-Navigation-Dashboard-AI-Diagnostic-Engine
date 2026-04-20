import streamlit as st
import requests
import os
from dotenv import load_dotenv
from nav_algorithm import calculate_path

# -----------------------------------------
# 1. ENTERPRISE CLOUD CONFIGURATION
# -----------------------------------------
load_dotenv()
GATEWAY_URL = os.getenv("WSO2_GATEWAY_URL")
BEARER_TOKEN = os.getenv("WSO2_BEARER_TOKEN")

# -----------------------------------------
# 2. UI SETUP & GRID DEFINITION
# -----------------------------------------
st.set_page_config(page_title="Robotics Path Planner", page_icon="🤖", layout="wide")

st.title("🤖 Robotics Path-Planning Dashboard")
st.markdown("---")

# Define a 10x10 Grid (0 = Open Space, 1 = Obstacle)
GRID = [
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 0]
]

START_NODE = (0, 0)
END_NODE = (9, 9)

# -----------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------
def render_grid_html(grid, path, start, end):
    """Renders an emoji grid for Streamlit without external libraries."""
    grid_display = ""
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) == start:
                grid_display += "🟢" # Start
            elif (r, c) == end:
                grid_display += "🔴" # Target
            elif path and (r, c) in path:
                grid_display += "🟦" # Path
            elif grid[r][c] == 1:
                grid_display += "⬛" # Obstacle
            else:
                grid_display += "⬜" # Open Space
        grid_display += "<br>"
    return grid_display

def get_ai_report(path_length, total_obstacles):
    """Calls the Groq LLM securely through the WSO2 API Gateway."""
    if not GATEWAY_URL or not BEARER_TOKEN:
        return "⚠️ Cloud Authentication Error: WSO2 Gateway URL or Bearer Token is missing."

    prompt = (
        f"You are a Senior Robotics Engineer. I just ran an A* pathfinding algorithm on a 10x10 grid. "
        f"The grid has {total_obstacles} obstacles. The robot successfully found a path taking {path_length} steps. "
        f"Give me a short, professional 3-sentence operational report analyzing this route efficiency."
    )

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(GATEWAY_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "⚠️ Error 401: Invalid Credentials. Your WSO2 Bearer Token might have expired."
        else:
            return f"⚠️ API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"⚠️ Network Error contacting the WSO2 Gateway: {str(e)}"

# -----------------------------------------
# 4. DASHBOARD INTERFACE
# -----------------------------------------
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Map Layout")
    st.write("🟢 Start | 🔴 Target | ⬛ Obstacle | 🟦 Route")
    
    # Calculate the total obstacles just for our AI context
    total_obstacles = sum(row.count(1) for row in GRID)

    if st.button("🚀 Calculate Optimal Route", type="primary"):
        with st.spinner("Running A* Algorithm..."):
            # Execute backend navigation logic
            computed_path = calculate_path(GRID, START_NODE, END_NODE)
            
            if computed_path:
                st.success(f"Route Found! Total Steps: {len(computed_path)}")
                
                # Render the map
                map_html = render_grid_html(GRID, computed_path, START_NODE, END_NODE)
                st.markdown(f"<div style='font-size: 24px; line-height: 1.2;'>{map_html}</div>", unsafe_allow_html=True)
                
                st.session_state['path_length'] = len(computed_path)
                st.session_state['obstacles'] = total_obstacles
            else:
                st.error("No valid route exists!")
                map_html = render_grid_html(GRID, None, START_NODE, END_NODE)
                st.markdown(f"<div style='font-size: 24px; line-height: 1.2;'>{map_html}</div>", unsafe_allow_html=True)
    else:
        # Just show the empty map before running
        map_html = render_grid_html(GRID, None, START_NODE, END_NODE)
        st.markdown(f"<div style='font-size: 24px; line-height: 1.2;'>{map_html}</div>", unsafe_allow_html=True)

with col2:
    st.subheader("📡 Senior Engineer AI Report")
    
    if 'path_length' in st.session_state:
        st.info("Querying Groq LLM via WSO2 API Gateway...")
        with st.spinner("Generating AI Report..."):
            # Generate the report based on the algorithm's output
            report = get_ai_report(st.session_state['path_length'], st.session_state['obstacles'])
            st.write(report)
    else:
        st.write("Run the algorithm to generate the telemetry report.")
