import streamlit as st

def force_sidebar():
    st.markdown(
        """
    <style>
        [data-testid="baseButton-header"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True)
    
def remove_header():
    st.markdown(
        """
    <style>
        [data-testid="stHeader"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True)

def remove_top_padding():
    st.markdown(
        """
    <style>
        [data-testid="block-container"] {
            top: -120px;
        }
        
    </style>
    """,
        unsafe_allow_html=True)
    
def remove_manage_app():
    st.markdown(
        """
    <style>
        [data-testid="manage-app-button"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True)

def remove_footer():
    st.markdown(
        """
    <style>
        footer {
            display: none;
        }
    </style>
    """,
        unsafe_allow_html=True)

def remove_toolbar():
    st.markdown(
        """
    <style>
        [data-testid="stToolbar"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True)
    
def change_header_background():
    st.markdown("""
    <style>
        [data-testid="stHeader"] {
            background-image: url('https://i.ibb.co/N2gvrns/headerlogo.png'); /* Substitua pelo caminho da sua imagem */
            background-size: 70% auto; /* Isso ajustará a imagem para cobrir toda a área do header */
            background-repeat: no-repeat;
            background-position: right; /* Isso centralizará a imagem no header */
            height: 150px; 
        }
    </style>
    """,
        unsafe_allow_html=True)

def remove_streamlit_elements():
    """
    Remove the Streamlit elements of the page that are not desired.
    Uses the CSS hack of the [data-testid=""] elements of the rendered page.
    Internal functions:
        - remove_footer()
        - remove_header()
        - remove_top_padding()
    """
    remove_footer()
    remove_header()
    remove_top_padding()
    return None

def sticky_header():
    """
    Make the page header became sticky, not scrolling when scrolling the page.
    Uses a CSS hack inside a st.markdown
    """
    st.markdown(
    """
        <style>
            div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                position: sticky;
                top: 0rem;
                background-color: white;
                z-index: 999;
            }
            .fixed-header {
                border-bottom: 1px solid #2A4B80;
            }
        </style>
    """,
    unsafe_allow_html=True
)