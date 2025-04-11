import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Medidor de Peixe", layout="centered")
st.title("📏 Medidor de Peixe por Imagem")

uploaded_file = st.file_uploader("Envie a imagem da pescaria:", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    st.markdown("---")
    st.subheader("1. Marque a referência (ex: 5 cm entre dois dedos)")
    canvas_ref = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",
        stroke_width=3,
        stroke_color="#FFFF00",
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="line",
        key="canvas_ref"
    )

    st.markdown("---")
    st.subheader("2. Marque o traçado do peixe")
    canvas_peixe = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",
        stroke_width=2,
        stroke_color="#000000",
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="freedraw",
        key="canvas_peixe"
    )

    ref_cm = st.number_input("Tamanho da linha de referência em cm", value=5.0)

    if st.button("Calcular medida") and canvas_ref.json_data and canvas_peixe.json_data:
        try:
            ref_line = canvas_ref.json_data["objects"][0]["path"]
            x1, y1 = ref_line[0]
            x2, y2 = ref_line[-1]
            px_ref = np.linalg.norm([x2 - x1, y2 - y1])
            escala = ref_cm / px_ref

            peixe_path = canvas_peixe.json_data["objects"][0]["path"]
            pontos = [(int(x), int(y)) for x, y in peixe_path]

            comprimento_px = 0
            for i in range(1, len(pontos)):
                p1, p2 = pontos[i - 1], pontos[i]
                comprimento_px += np.linalg.norm([p2[0] - p1[0], p2[1] - p1[1]])

            comprimento_cm = comprimento_px * escala
            st.success(f"📐 Comprimento estimado do peixe: {comprimento_cm:.2f} cm")

            # Desenha imagem com resultado
            img_result = image.copy()
            draw = ImageDraw.Draw(img_result)
            draw.line([ref_line[0], ref_line[-1]], fill="yellow", width=3)
            draw.line(pontos, fill="black", width=2)
            meio = pontos[len(pontos)//2]
            draw.text((meio[0]+10, meio[1]), f"{comprimento_cm:.1f} cm", fill="red")

            st.image(img_result, caption="Resultado com medição", use_column_width=True)

        except Exception as e:
            st.error("Erro ao processar os pontos. Tente novamente com marcações mais simples.")
