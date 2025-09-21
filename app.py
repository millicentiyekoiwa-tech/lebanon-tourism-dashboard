import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Lebanon Tourism Infrastructure Analysis",
    page_icon="🇱🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced dark styling
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e2329;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    .main-header {
        font-size: 3.5rem;
        color: #d4af37;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(212,175,55,0.3);
    }
    
    .sub-header {
        font-size: 2rem;
        color: #fafafa;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #d4af37;
        padding-bottom: 0.5rem;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #1e2329 0%, #2d3748 100%);
        border-left: 5px solid #d4af37;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(212,175,55,0.2);
        color: #fafafa;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(212,175,55,0.15);
        text-align: center;
        border: 2px solid #d4af37;
        color: #fafafa;
    }
    
    .context-section {
        background-color: #1a202c;
        border: 2px solid #d4af37;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        color: #fafafa;
    }
    
    .visualization-container {
        background-color: #1a202c;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 6px 12px rgba(212,175,55,0.1);
        margin: 2rem 0;
        border: 1px solid #4a5568;
    }
    
    .download-section {
        background-color: #1e2329;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #48bb78;
        color: #fafafa;
    }
    
    /* Streamlit elements styling */
    .stSelectbox > div > div > div {
        background-color: #2d3748;
        color: #fafafa;
    }
    
    .stMultiSelect > div > div > div {
        background-color: #2d3748;
        color: #fafafa;
    }
    
    .stSlider > div > div > div {
        color: #fafafa;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #1a202c;
        border: 1px solid #d4af37;
        padding: 1rem;
        border-radius: 8px;
        color: #fafafa;
    }
    
    [data-testid="metric-container"] > div {
        color: #fafafa;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #1a202c;
    }
    
    /* Text elements */
    .stMarkdown {
        color: #fafafa;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background-color: #2d3748;
        color: #fafafa;
        border: 1px solid #d4af37;
    }
    
    .stDownloadButton > button:hover {
        background-color: #4a5568;
        color: #d4af37;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the Lebanon tourism data"""
    url = "https://linked.aub.edu.lb/pkgcube/data/df6527f0de0990b7237dbcef186a3d52_20240904_215117.csv"
    try:
        response = requests.get(url)
        data = pd.read_csv(StringIO(response.text))
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def create_download_buttons(fig, chart_name):
    """Create download buttons for Plotly charts"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            img_bytes = pio.to_image(fig, format="png", width=1200, height=800, scale=2)
            st.download_button(
                label="📥 Download PNG",
                data=img_bytes,
                file_name=f"{chart_name}.png",
                mime="image/png",
                help="Download high-quality PNG image"
            )
        except:
            st.info("PNG download requires kaleido package")
    
    with col2:
        html_str = pio.to_html(fig, include_plotlyjs='cdn')
        st.download_button(
            label="📥 Download HTML",
            data=html_str,
            file_name=f"{chart_name}.html",
            mime="text/html",
            help="Download interactive HTML file"
        )
    
    with col3:
        try:
            svg_bytes = pio.to_image(fig, format="svg")
            st.download_button(
                label="📥 Download SVG",
                data=svg_bytes,
                file_name=f"{chart_name}.svg",
                mime="image/svg+xml",
                help="Download scalable vector graphic"
            )
        except:
            st.info("SVG download requires kaleido package")

def process_infrastructure_data(df):
    """Process data for infrastructure availability analysis"""
    # Define infrastructure categories
    infrastructure_mapping = {
        'Hotels': ('Existence of hotels - exists', 'Existence of hotels - does not exist'),
        'Restaurants': ('Existence of restaurants - exists', 'Existence of restaurants - does not exist'),
        'Cafes': ('Existence of cafes - exists', 'Existence of cafes - does not exist'),
        'Guest Houses': ('Existence of guest houses - exists', 'Existence of guest houses - does not exist'),
        'Tourist Attractions': ('Existence of touristic attractions prone to be exploited and developed - exists', 
                               'Existence of touristic attractions that can be expolited and developed - does not exist')
    }
    
    infrastructure_data = []
    for category, (exists_col, not_exists_col) in infrastructure_mapping.items():
        exists_count = df[exists_col].sum() if exists_col in df.columns else 0
        not_exists_count = df[not_exists_col].sum() if not_exists_col in df.columns else 0
        total = exists_count + not_exists_count
        percentage = (exists_count / total * 100) if total > 0 else 0
        
        infrastructure_data.append({
            'Category': category,
            'Towns_With': exists_count,
            'Towns_Without': not_exists_count,
            'Total_Towns': total,
            'Availability_Percentage': percentage
        })
    
    return pd.DataFrame(infrastructure_data)

def process_facility_counts(df):
    """Process data for facility count analysis"""
    # Calculate totals for each town
    df_processed = df.copy()
    df_processed['Total_Hotels'] = pd.to_numeric(df_processed['Total number of hotels'], errors='coerce').fillna(0)
    df_processed['Total_Restaurants'] = pd.to_numeric(df_processed['Total number of restaurants'], errors='coerce').fillna(0)
    df_processed['Total_Cafes'] = pd.to_numeric(df_processed['Total number of cafes'], errors='coerce').fillna(0)
    df_processed['Total_Guest_Houses'] = pd.to_numeric(df_processed['Total number of guest houses'], errors='coerce').fillna(0)
    
    # Calculate combined totals
    df_processed['Total_Facilities'] = (df_processed['Total_Hotels'] + 
                                       df_processed['Total_Restaurants'] + 
                                       df_processed['Total_Cafes'] + 
                                       df_processed['Total_Guest_Houses'])
    
    # Filter towns with facilities
    df_with_facilities = df_processed[df_processed['Total_Facilities'] > 0].copy()
    
    return df_with_facilities

def create_infrastructure_availability_chart(df, selected_categories, chart_style):
    """Create Visualization 1: Infrastructure Availability with subtle animations"""
    
    filtered_df = df[df['Category'].isin(selected_categories)]
    
    if chart_style == "Horizontal Bar Chart":
        fig = go.Figure()
        
        # Add bars with subtle hover animations
        fig.add_trace(go.Bar(
            name='Towns With Infrastructure',
            y=filtered_df['Category'],
            x=filtered_df['Towns_With'],
            orientation='h',
            marker=dict(
                color='#2ecc71', 
                opacity=0.8,
                line=dict(color='#27ae60', width=2)
            ),
            text=filtered_df['Towns_With'],
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>Towns with infrastructure: %{x}<br>Percentage: %{customdata:.1f}%<extra></extra>',
            customdata=filtered_df['Availability_Percentage'],
            # Subtle animation on load
            marker_line_width=2,
            textfont_size=12
        ))
        
        fig.add_trace(go.Bar(
            name='Towns Without Infrastructure',
            y=filtered_df['Category'],
            x=filtered_df['Towns_Without'],
            orientation='h',
            marker=dict(
                color='#e74c3c', 
                opacity=0.6,
                line=dict(color='#c0392b', width=2)
            ),
            text=filtered_df['Towns_Without'],
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>Towns without infrastructure: %{x}<extra></extra>',
            textfont_size=12
        ))
        
        fig.update_layout(
            title=dict(
                text='Tourism Infrastructure Availability Across Lebanese Towns',
                font=dict(size=20, color='#fafafa'),
                x=0.5
            ),
            xaxis_title='Number of Towns',
            yaxis_title='Infrastructure Type',
            barmode='stack',
            height=500,
            font=dict(size=12, color='#fafafa'),
            template='plotly_dark',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#fafafa')),
            # Add subtle transitions
            transition={'duration': 800, 'easing': 'cubic-in-out'},
            hovermode='y unified',
            paper_bgcolor='rgba(26,32,44,1)',
            plot_bgcolor='rgba(26,32,44,1)'
        )
        
        # Add subtle grid animations
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.2)')
        fig.update_yaxes(showgrid=False)
        
    else:  # Donut Chart with subtle rotation animation
        labels = []
        values = []
        colors = []
        
        color_map = {
            'Hotels': '#3498db', 'Restaurants': '#e67e22', 'Cafes': '#9b59b6', 
            'Guest Houses': '#1abc9c', 'Tourist Attractions': '#f39c12'
        }
        
        for _, row in filtered_df.iterrows():
            labels.extend([f"{row['Category']} (Available)", f"{row['Category']} (Not Available)"])
            values.extend([row['Towns_With'], row['Towns_Without']])
            base_color = color_map.get(row['Category'], '#95a5a6')
            colors.extend([base_color, base_color + '40'])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(
                colors=colors,
                line=dict(color='#FFFFFF', width=2)
            ),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Towns: %{value}<br>Percentage: %{percent}<extra></extra>',
            # Add subtle pull effect on hover
            pull=[0.05 if 'Available' in label and not 'Not' in label else 0 for label in labels],
            textfont_size=11
        )])
        
        fig.update_layout(
            title=dict(
                text='Distribution of Tourism Infrastructure Availability',
                font=dict(size=20, color='#fafafa'),
                x=0.5
            ),
            height=600,
            annotations=[dict(
                text='Infrastructure<br>Distribution', 
                x=0.5, y=0.5, 
                font=dict(size=16, color='#fafafa'), 
                showarrow=False
            )],
            template='plotly_dark',
            # Smooth transitions
            transition={'duration': 600, 'easing': 'cubic-in-out'},
            paper_bgcolor='rgba(26,32,44,1)',
            plot_bgcolor='rgba(26,32,44,1)'
        )
    
    return fig

def create_facility_correlation_chart(df, min_facilities, facility_types, show_correlation):
    """Create Visualization 2: Facility Count Correlation with hover animations"""
    
    # Filter data based on minimum facilities
    filtered_df = df[df['Total_Facilities'] >= min_facilities].copy()
    
    # Filter by selected facility types for size calculation
    size_column = 0
    if 'Hotels' in facility_types:
        size_column += filtered_df['Total_Hotels']
    if 'Restaurants' in facility_types:
        size_column += filtered_df['Total_Restaurants']
    if 'Cafes' in facility_types:
        size_column += filtered_df['Total_Cafes']
    if 'Guest Houses' in facility_types:
        size_column += filtered_df['Total_Guest_Houses']
    
    filtered_df['Selected_Facilities'] = size_column
    
    # Create scatter plot with subtle animations
    fig = go.Figure()
    
    # Add scatter points with hover animations
    fig.add_trace(go.Scatter(
        x=filtered_df['Total_Hotels'],
        y=filtered_df['Total_Restaurants'],
        mode='markers',
        marker=dict(
            size=filtered_df['Selected_Facilities'] * 3 + 8,
            color=filtered_df['Total_Facilities'],
            colorscale='Viridis',
            colorbar=dict(title="Total Facilities"),
            opacity=0.7,
            line=dict(width=2, color='white'),
            # Subtle size increase on hover
            sizemode='diameter'
        ),
        text=filtered_df['Town'],
        hovertemplate='<b>%{text}</b><br>' +
                     'Hotels: %{x}<br>' +
                     'Restaurants: %{y}<br>' +
                     'Total Facilities: %{marker.color}<br>' +
                     '<extra></extra>',
        name='Towns',
        # Add subtle hover effects
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
    ))
    
    # Add trend line with animation if requested
    if show_correlation and len(filtered_df) > 1:
        correlation = np.corrcoef(filtered_df['Total_Hotels'], filtered_df['Total_Restaurants'])[0,1]
        
        # Calculate trend line
        z = np.polyfit(filtered_df['Total_Hotels'], filtered_df['Total_Restaurants'], 1)
        p = np.poly1d(z)
        
        x_trend = np.linspace(filtered_df['Total_Hotels'].min(), filtered_df['Total_Hotels'].max(), 50)
        y_trend = p(x_trend)
        
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=y_trend,
            mode='lines',
            line=dict(color='#e74c3c', width=3, dash='dash'),
            name=f'Trend Line (r={correlation:.3f})',
            hovertemplate='Correlation: %{text}<extra></extra>',
            text=[f'{correlation:.3f}'] * len(x_trend),
            opacity=0.8
        ))
        
        # Add correlation annotation with subtle fade-in
        fig.add_annotation(
            x=0.02, y=0.98,
            xref="paper", yref="paper",
            text=f"<b>Correlation: {correlation:.3f}</b>",
            showarrow=False,
            bgcolor="rgba(26,32,44,0.9)",
            bordercolor="#d4af37",
            borderwidth=2,
            font=dict(size=14, color='#fafafa')
        )
    
    fig.update_layout(
        title=dict(
            text='Hotel vs Restaurant Distribution: Infrastructure Correlation Analysis',
            font=dict(size=20, color='#fafafa'),
            x=0.5
        ),
        xaxis_title='Number of Hotels',
        yaxis_title='Number of Restaurants',
        height=600,
        template='plotly_dark',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color='#fafafa')),
        # Add subtle hover animations
        hovermode='closest',
        # Smooth transitions
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        paper_bgcolor='rgba(26,32,44,1)',
        plot_bgcolor='rgba(26,32,44,1)'
    )
    
    # Add subtle grid with animations
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255,255,255,0.2)',
        zeroline=True,
        zerolinecolor='rgba(255,255,255,0.4)',
        title_font=dict(color='#fafafa')
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255,255,255,0.2)',
        zeroline=True,
        zerolinecolor='rgba(255,255,255,0.4)',
        title_font=dict(color='#fafafa')
    )
    
    return fig, filtered_df

def main():
    # Header
    st.markdown('<div class="main-header">🇱🇧 Lebanon Tourism Infrastructure Analysis</div>', unsafe_allow_html=True)
    
    # Introduction and Context
    st.markdown("""
    <div class="context-section">
    <h2>📖 Analysis Overview</h2>
    <p style="font-size: 1.1rem; line-height: 1.6;">
    This comprehensive analysis explores Lebanon's tourism infrastructure through two complementary visualizations 
    that reveal critical insights about the country's tourism readiness and development patterns.
    </p>
    
    <h3>🎯 Research Questions:</h3>
    <ul style="font-size: 1rem; line-height: 1.5;">
    <li><strong>Infrastructure Distribution:</strong> How evenly distributed are tourism facilities across Lebanese towns?</li>
    <li><strong>Facility Correlation:</strong> Do towns with more hotels also have more restaurants, indicating integrated tourism development?</li>
    <li><strong>Tourism Readiness:</strong> Which towns are best equipped to handle tourists with comprehensive infrastructure?</li>
    </ul>
    
    <h3>📊 Data Source:</h3>
    <p style="font-size: 1rem;">
    American University of Beirut (AUB) Lebanon Tourism Infrastructure Dataset - A comprehensive survey of 
    tourism facilities and attractions across Lebanese municipalities.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("🔄 Loading Lebanon tourism data..."):
        raw_data = load_data()
    
    if raw_data is None:
        st.error("❌ Failed to load data. Please check your internet connection.")
        return
    
    # Process data
    infrastructure_df = process_infrastructure_data(raw_data)
    facility_counts_df = process_facility_counts(raw_data)
    
    # Sidebar controls
    st.sidebar.markdown("## 🎛️ Interactive Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Dataset overview
    st.sidebar.markdown("### 📊 Dataset Overview")
    st.sidebar.metric("Total Towns Analyzed", len(raw_data))
    st.sidebar.metric("Towns with Facilities", len(facility_counts_df))
    st.sidebar.metric("Infrastructure Categories", len(infrastructure_df))
    
    st.sidebar.markdown("---")
    
    # Controls for Visualization 1
    st.sidebar.markdown("### 🏗️ Infrastructure Analysis Controls")
    
    all_categories = infrastructure_df['Category'].tolist()
    selected_categories = st.sidebar.multiselect(
        "Select Infrastructure Types:",
        options=all_categories,
        default=all_categories,
        help="Choose which infrastructure types to analyze"
    )
    
    chart_style = st.sidebar.selectbox(
        "Visualization Style:",
        ["Horizontal Bar Chart", "Donut Chart"],
        help="Choose how to display infrastructure availability"
    )
    
    st.sidebar.markdown("---")
    
    # Controls for Visualization 2
    st.sidebar.markdown("### 🔍 Correlation Analysis Controls")
    
    min_facilities = st.sidebar.slider(
        "Minimum Total Facilities:",
        min_value=0,
        max_value=int(facility_counts_df['Total_Facilities'].max()),
        value=1,
        help="Filter towns with at least this many total facilities"
    )
    
    facility_types = st.sidebar.multiselect(
        "Facility Types for Size Scaling:",
        options=['Hotels', 'Restaurants', 'Cafes', 'Guest Houses'],
        default=['Hotels', 'Restaurants'],
        help="Select which facilities determine bubble size"
    )
    
    show_correlation = st.sidebar.checkbox(
        "Show Correlation Trend Line",
        value=True,
        help="Display correlation coefficient and trend line"
    )
    
    # Main content validation
    if not selected_categories:
        st.warning("⚠️ Please select at least one infrastructure category to display visualizations.")
        return
    
    if not facility_types:
        st.warning("⚠️ Please select at least one facility type for correlation analysis.")
        return
    
    # Key Metrics Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_towns_with_hotels = infrastructure_df[infrastructure_df['Category'] == 'Hotels']['Towns_With'].iloc[0]
        hotel_percentage = infrastructure_df[infrastructure_df['Category'] == 'Hotels']['Availability_Percentage'].iloc[0]
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Towns with Hotels", f"{total_towns_with_hotels}", f"{hotel_percentage:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        total_towns_with_restaurants = infrastructure_df[infrastructure_df['Category'] == 'Restaurants']['Towns_With'].iloc[0]
        restaurant_percentage = infrastructure_df[infrastructure_df['Category'] == 'Restaurants']['Availability_Percentage'].iloc[0]
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Towns with Restaurants", f"{total_towns_with_restaurants}", f"{restaurant_percentage:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        total_towns_with_attractions = infrastructure_df[infrastructure_df['Category'] == 'Tourist Attractions']['Towns_With'].iloc[0]
        attraction_percentage = infrastructure_df[infrastructure_df['Category'] == 'Tourist Attractions']['Availability_Percentage'].iloc[0]
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Towns with Attractions", f"{total_towns_with_attractions}", f"{attraction_percentage:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        avg_facilities = facility_counts_df['Total_Facilities'].mean()
        max_facilities = facility_counts_df['Total_Facilities'].max()
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Avg Facilities/Town", f"{avg_facilities:.1f}", f"Max: {max_facilities:.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # VISUALIZATION 1: Infrastructure Availability
    st.markdown('<div class="sub-header">📊 Visualization 1: Tourism Infrastructure Availability Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-box">
    <h4>🔍 What This Shows:</h4>
    This visualization reveals how tourism infrastructure is distributed across Lebanese towns, 
    showing which types of facilities are most commonly available and identifying gaps in tourism readiness.
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
        
        viz1_fig = create_infrastructure_availability_chart(infrastructure_df, selected_categories, chart_style)
        st.plotly_chart(viz1_fig, use_container_width=True, config={
            'displayModeBar': True,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'lebanon_infrastructure_availability',
                'height': 800,
                'width': 1200,
                'scale': 2
            }
        })
        
        # Download buttons for Visualization 1
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.markdown("**📥 Download Options:**")
        create_download_buttons(viz1_fig, "lebanon_infrastructure_availability")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Insights for Visualization 1
    filtered_infra_df = infrastructure_df[infrastructure_df['Category'].isin(selected_categories)]
    best_infrastructure = filtered_infra_df.loc[filtered_infra_df['Availability_Percentage'].idxmax()]
    worst_infrastructure = filtered_infra_df.loc[filtered_infra_df['Availability_Percentage'].idxmin()]
    
    st.markdown(f"""
    <div class="insight-box">
    <h4>💡 Key Insights from Infrastructure Analysis:</h4>
    <ul>
    <li><strong>Best Available:</strong> {best_infrastructure['Category']} are available in {best_infrastructure['Availability_Percentage']:.1f}% of towns ({best_infrastructure['Towns_With']} towns)</li>
    <li><strong>Biggest Gap:</strong> {worst_infrastructure['Category']} are only available in {worst_infrastructure['Availability_Percentage']:.1f}% of towns ({worst_infrastructure['Towns_With']} towns)</li>
    <li><strong>Development Opportunity:</strong> {'High restaurant availability suggests strong local dining culture' if best_infrastructure['Category'] == 'Restaurants' else 'Infrastructure development needed for tourism growth'}</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # VISUALIZATION 2: Facility Correlation
    st.markdown('<div class="sub-header">🔗 Visualization 2: Hotel-Restaurant Correlation & Tourism Integration</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-box">
    <h4>🔍 What This Shows:</h4>
    This scatter plot analysis reveals the relationship between hotel and restaurant availability across towns, 
    indicating whether tourism infrastructure develops in an integrated manner. Bubble sizes represent total facilities, 
    helping identify comprehensive tourism hubs.
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
        
        viz2_fig, correlation_df = create_facility_correlation_chart(facility_counts_df, min_facilities, facility_types, show_correlation)
        st.plotly_chart(viz2_fig, use_container_width=True, config={
            'displayModeBar': True,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'lebanon_hotel_restaurant_correlation',
                'height': 800,
                'width': 1200,
                'scale': 2
            }
        })
        
        # Download buttons for Visualization 2
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.markdown("**📥 Download Options:**")
        create_download_buttons(viz2_fig, "lebanon_hotel_restaurant_correlation")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Insights for Visualization 2
    if len(correlation_df) > 1 and show_correlation:
        correlation_coeff = np.corrcoef(correlation_df['Total_Hotels'], correlation_df['Total_Restaurants'])[0,1]
        
        # Find top tourism hubs
        top_hubs = correlation_df.nlargest(3, 'Total_Facilities')[['Town', 'Total_Hotels', 'Total_Restaurants', 'Total_Facilities']]
        
        correlation_interpretation = ""
        if correlation_coeff > 0.7:
            correlation_interpretation = "Strong positive correlation - towns with more hotels consistently have more restaurants, indicating integrated tourism development."
        elif correlation_coeff > 0.3:
            correlation_interpretation = "Moderate positive correlation - some tendency for hotels and restaurants to develop together."
        elif correlation_coeff > -0.3:
            correlation_interpretation = "Weak correlation - hotels and restaurants develop somewhat independently across towns."
        else:
            correlation_interpretation = "Negative correlation - unusual pattern suggesting specialized tourism functions."
        
        st.markdown(f"""
        <div class="insight-box">
        <h4>🔗 Correlation Analysis Insights:</h4>
        <ul>
        <li><strong>Correlation Strength:</strong> {correlation_coeff:.3f} - {correlation_interpretation}</li>
        <li><strong>Towns Analyzed:</strong> {len(correlation_df)} towns with {min_facilities}+ facilities</li>
        <li><strong>Top Tourism Hub:</strong> {top_hubs.iloc[0]['Town']} ({int(top_hubs.iloc[0]['Total_Hotels'])} hotels, {int(top_hubs.iloc[0]['Total_Restaurants'])} restaurants)</li>
        <li><strong>Tourism Integration:</strong> {'High' if correlation_coeff > 0.5 else 'Moderate' if correlation_coeff > 0.3 else 'Low'} level of integrated tourism infrastructure development</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Comprehensive Analysis Summary
    st.markdown('<div class="sub-header">🎯 Comprehensive Tourism Infrastructure Assessment</div>', unsafe_allow_html=True)
    
    # Calculate comprehensive metrics
    total_towns = len(raw_data)
    towns_with_both = len(correlation_df[(correlation_df['Total_Hotels'] > 0) & (correlation_df['Total_Restaurants'] > 0)])
    comprehensive_hubs = len(correlation_df[correlation_df['Total_Facilities'] >= 10])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h4>🏆 Tourism Readiness Summary</h4>
        <ul>
        <li><strong>Comprehensive Tourism Hubs:</strong> Towns with 10+ total facilities</li>
        <li><strong>Integrated Development:</strong> Towns with both hotels and restaurants</li>
        <li><strong>Infrastructure Gaps:</strong> Areas needing development focus</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Tourism-Ready Towns", f"{comprehensive_hubs}", f"{comprehensive_hubs/total_towns*100:.1f}% of all towns")
        st.metric("Integrated Infrastructure", f"{towns_with_both}", f"{towns_with_both/total_towns*100:.1f}% have both hotels & restaurants")
    
    with col2:
        # Top 5 most comprehensive tourism destinations
        if not correlation_df.empty:
            top_destinations = correlation_df.nlargest(5, 'Total_Facilities')[['Town', 'Total_Hotels', 'Total_Restaurants', 'Total_Cafes', 'Total_Guest_Houses', 'Total_Facilities']].copy()
            
            # Only convert numeric columns to integers
            numeric_columns = ['Total_Hotels', 'Total_Restaurants', 'Total_Cafes', 'Total_Guest_Houses', 'Total_Facilities']
            for col in numeric_columns:
                if col in top_destinations.columns:
                    top_destinations[col] = top_destinations[col].round(0).astype(int)
            
            st.markdown("### 🌟 Top Tourism Destinations")
            st.dataframe(
                top_destinations,
                use_container_width=True,
                hide_index=True
            )
    
    # Final Recommendations
    st.markdown("""
    <div class="context-section">
    <h3>📋 Strategic Recommendations</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
        <div>
            <h4>🎯 For Tourism Development:</h4>
            <ul>
            <li>Focus on towns with attractions but limited infrastructure</li>
            <li>Develop integrated hotel-restaurant complexes</li>
            <li>Support infrastructure in high-potential areas</li>
            </ul>
        </div>
        <div>
            <h4>📊 For Further Analysis:</h4>
            <ul>
            <li>Geographic clustering analysis of facilities</li>
            <li>Seasonal capacity vs. demand analysis</li>
            <li>Infrastructure quality assessment</li>
            </ul>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**📊 Data Source:** American University of Beirut - Lebanon Tourism Infrastructure Study")
    st.markdown("**✨ Enhanced Features:** Interactive filtering, dynamic visualizations, correlation analysis, and download capabilities")

if __name__ == "__main__":
    main()
