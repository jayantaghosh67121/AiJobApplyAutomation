"""Streamlit dashboard for Job Automation Bot"""

import streamlit as st
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Job Automation Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    """Main dashboard function"""
    st.title("🤖 Job Automation Bot")
    st.markdown("AI-powered job application automation system")

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            [
                "📊 Dashboard",
                "📋 Review Queue",
                "🔄 Pipeline",
                "📈 Analytics",
                "⚙️ Settings",
            ],
        )

    # Dashboard page
    if page == "📊 Dashboard":
        st.header("Dashboard")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Applications Sent", "0", "+0")
        with col2:
            st.metric("Replies Received", "0", "+0")
        with col3:
            st.metric("Interview Invites", "0", "+0")
        with col4:
            st.metric("Avg Match Score", "0.00", "0.00")

        st.subheader("Recent Applications")
        st.info("No applications yet. Configure your profile and settings to get started.")

    # Review Queue page
    elif page == "📋 Review Queue":
        st.header("Application Review Queue")
        st.info(
            "Review and approve applications before they are submitted automatically."
        )
        st.write("No pending applications.")

    # Pipeline page
    elif page == "🔄 Pipeline":
        st.header("Application Pipeline")
        st.info("Kanban-style view of all applications by status.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Applied")
            st.write("0")
        with col2:
            st.subheader("Replied")
            st.write("0")
        with col3:
            st.subheader("Interview")
            st.write("0")

    # Analytics page
    elif page == "📈 Analytics":
        st.header("Analytics")
        st.info("Charts and metrics about your job applications.")
        st.write("No data yet.")

    # Settings page
    elif page == "⚙️ Settings":
        st.header("Settings")

        st.subheader("Profile Information")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Full Name", placeholder="Your Name")
            st.text_input("Email", placeholder="your.email@example.com")
        with col2:
            st.text_input("Phone", placeholder="+1-XXX-XXX-XXXX")
            st.text_input("Location", placeholder="Remote")

        st.subheader("Application Preferences")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Minimum Salary", value=100000, step=10000)
            st.checkbox("Remote Only", value=True)
        with col2:
            st.text_area(
                "Blacklisted Companies",
                placeholder="CompanyA, CompanyB, CompanyC",
                height=100,
            )

        st.subheader("Automation Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Auto-Apply Threshold", 0.0, 1.0, 0.75, step=0.05)
        with col2:
            st.slider("Max Applications per Day", 1, 50, 15, step=1)

        st.checkbox("Enable Auto-Submit", value=False)

        if st.button("Save Settings", type="primary"):
            st.success("Settings saved successfully!")

    # Footer
    st.divider()
    st.markdown(
        """
        <center>
        Job Automation Bot v0.1.0 | Last updated: """
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + """
        </center>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
