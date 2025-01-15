import streamlit as st 
import base64

st.set_page_config(
   page_title="River Monitoring System",
   page_icon="🖥️",
   layout="wide",
   initial_sidebar_state="collapsed",
)



def set_bg_hack(main_bg):
   
    # set bg name
    main_bg_ext = "jpg"
        
    st.markdown(
         f"""
         <style>
         [data-testid=stHeader]{{
             background-color: rgba(0,0,0,0);
         }}
         [data-testid=stAppViewContainer]>.main{{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-position:top right;
             background-blend-mode: saturation;
             background-size: 130%;
             background-repeat:no-repeat;   
             filter: grayscale(0%);          
             
         }}
         [data-testid="stSidebarNavLink"],[data-testid="stMarkdown"]{{
            background-color: rgba(255,255,255,0.0);
         }}
         [data-testid=stSidebarContent] {{
             
              }}
         </style>
         """,
         unsafe_allow_html=True
     )



set_bg_hack("image/fondo2.jpg")

st.title("River Monitoring System")
#st.subheader("Dirección Nacional de Política Hídrica y Coordinación Federal")
st.sidebar.markdown("# 🌎 Home")




footer="""<style>


.footer {
position: fixed;
left: 0;
bottom: 0;
width: 18vw;
background-color: transparent;
display:flex;
justify-content: center;
align-items:end;
color: black;
text-align: center;
font-size: 8px;
}
</style>
<div class="footer">
<p>by <a style='display: block; text-align: center;' href="mailto:" target="_blank">Iván Hellwig</a></p>
</div>
"""
st.sidebar.markdown(footer,unsafe_allow_html=True)







