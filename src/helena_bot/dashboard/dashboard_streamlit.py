import glob
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from fpdf import FPDF

FONT_DIR = "./data/fonts/dejavu-fonts-ttf-2.37/ttf"
IMG_DIR = "pdf_imgs"
os.makedirs(IMG_DIR, exist_ok=True)


def register_fonts_fpdf2(pdf: FPDF, font_dir: str = ".") -> None:
    regular_path = os.path.join(font_dir, "DejaVuSans.ttf")
    bold_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    if not os.path.exists(regular_path):
        raise FileNotFoundError(f"Fonte regular não encontrada: {regular_path}")
    if not os.path.exists(bold_path):
        raise FileNotFoundError(f"Fonte em negrito não encontrada: {bold_path}")
    pdf.add_font("DejaVu", "", regular_path, uni=True)
    pdf.add_font("DejaVu", "B", bold_path, uni=True)


def load_latest_results():
    result_files = sorted(
        glob.glob("resultados.csv"), key=os.path.getmtime, reverse=True
    )
    if result_files:
        return pd.read_csv(result_files[0])
    return None


def save_plot_as_image(fig, name):
    path = os.path.join(IMG_DIR, f"{name}.png")
    fig.savefig(path, bbox_inches="tight")
    return path


def export_pdf(df: pd.DataFrame):
    filename = f"relatorio_rag_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    register_fonts_fpdf2(pdf, font_dir=FONT_DIR)
    pdf.set_font("DejaVu", size=12)
    pdf.cell(200, 10, txt="📊 Relatório de Avaliação - HelenaBot", ln=True, align="C")
    pdf.ln(10)

    for _, row in df.iterrows():
        pdf.set_font("DejaVu", "B", 12)
        pdf.multi_cell(190, 8, f"❓ Pergunta: {row['question']}")
        pdf.set_font("DejaVu", size=11)
        pdf.multi_cell(190, 8, f"🤖 Resposta: {row['response']}")
        pdf.multi_cell(190, 8, f"💬 Justificativa: {row['reasoning']}")
        pdf.cell(
            0,
            8,
            f"📈 Métricas → Hit Rate: {row['hit_rate']} | MRR: {row['mrr']} | MAP: {row['map']} | nDCG: {row['ndcg']} | 🧠 Faithfulness: {row['faithfulness']}",
            ln=True,
        )
        pdf.ln(5)

    for img_file in sorted(glob.glob(os.path.join(IMG_DIR, "*.png"))):
        pdf.add_page()
        pdf.image(img_file, x=10, y=20, w=180)

    pdf.output(filename)
    return filename


def main():
    st.set_page_config(layout="wide")
    st.title("🧠 HelenaBot - Dashboard Profissional de Avaliação RAG")
    df = load_latest_results()
    if df is None:
        st.warning("Nenhum arquivo de resultados encontrado.")
        return

    with st.sidebar:
        st.header("📘 Métricas")
        st.markdown(
            """
        - **Hit Rate**: Pelo menos um documento relevante foi retornado.
        - **MRR**: Recíproco da posição do primeiro documento relevante.
        - **MAP**: Média das precisões cumulativas.
        - **nDCG**: Avalia a ordem dos documentos relevantes.
        - **Faithfulness**: Fidelidade da resposta ao contexto.
        """
        )
        st.divider()
        st.header("🎚️ Filtros")
        pergunta = st.selectbox(
            "Filtrar por pergunta",
            ["Todas"] + df["question"].dropna().unique().tolist(),
        )
        min_faith = st.slider("Nota mínima de Faithfulness", 0.0, 1.0, 0.0, 0.01)

    if pergunta != "Todas":
        df = df[df["question"] == pergunta]
    df = df[df["faithfulness"] >= min_faith]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📋 Resultados",
            "📈 Gráficos Comparativos",
            "📊 Correlações",
            "📦 Estatísticas",
            "🧠 Justificativas",
        ]
    )

    with tab1:
        st.subheader("📋 Tabela de Resultados")
        st.dataframe(df, use_container_width=True)
        # if st.button("📥 Exportar relatório para PDF com gráficos"):
        #   st.info("Gerando relatório com gráficos...")
        #  export_pdf(df)
        # st.success("Relatório exportado com sucesso!")

    with tab2:
        st.subheader("📊 Comparação de Métricas por Pergunta")

        # Reestruturação para gráfico
        melted = df.melt(
            id_vars=["question"],
            value_vars=["hit_rate", "mrr", "map", "ndcg", "faithfulness"],
            var_name="Métrica",
            value_name="Valor",
        )

        # Geração do gráfico
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.barplot(data=melted, x="question", y="Valor", hue="Métrica", ax=ax)

        # Ajustes visuais
        ax.set_title(
            "Comparação de Métricas por Pergunta",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("Perguntas")
        ax.set_ylabel("Valor")
        plt.xticks(rotation=30, ha="right")
        ax.legend(
            title="Métrica", loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=True
        )

        # Layout final
        plt.tight_layout()
        st.pyplot(fig)
        save_plot_as_image(fig, "barplot_metricas")

        st.subheader("📉 Desempenho Geral (Linhas)")
        plt.style.use("seaborn-v0_8-whitegrid")

        pivoted = df[
            ["question", "hit_rate", "mrr", "map", "ndcg", "faithfulness"]
        ].set_index("question")
        fig_line, ax_line = plt.subplots(figsize=(12, 5))
        pivoted.T.plot(kind="line", ax=ax_line, marker="o")
        ax_line.set_title("Desempenho por Métrica")
        ax_line.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        for line in ax_line.lines:
            for x, y in zip(line.get_xdata(), line.get_ydata()):
                ax_line.text(x, y, f"{y:.2f}", fontsize=8, ha="center", va="bottom")
        fig_line.tight_layout()
        st.pyplot(fig_line)
        save_plot_as_image(fig_line, "linhas_metricas")

    with tab3:
        st.subheader("📦 Distribuição das Métricas")
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.boxplot(data=df[["hit_rate", "mrr", "map", "ndcg", "faithfulness"]], ax=ax2)
        ax2.set_title("Distribuição Geral das Métricas")
        st.pyplot(fig2)
        save_plot_as_image(fig2, "boxplot_metricas")

        st.subheader("📍 Correlação nDCG vs Faithfulness")
        fig3, ax3 = plt.subplots()
        sns.scatterplot(data=df, x="ndcg", y="faithfulness", hue="question", ax=ax3)
        ax3.set_title("nDCG x Faithfulness")
        ax3.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        st.pyplot(fig3)
        save_plot_as_image(fig3, "scatter_ndcg_faith")

        st.subheader("🔥 Matriz de Correlação")
        fig_corr, ax_corr = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            df[["hit_rate", "mrr", "map", "ndcg", "faithfulness"]].corr(),
            annot=True,
            cmap="coolwarm",
            ax=ax_corr,
        )
        st.pyplot(fig_corr)
        save_plot_as_image(fig_corr, "heatmap_correlacao")

    with tab4:
        st.subheader("📈 Estatísticas Descritivas")
        st.write(df[["hit_rate", "mrr", "map", "ndcg", "faithfulness"]].describe().T)

        st.subheader("📊 Histograma das Métricas")
        fig_hist, ax_hist = plt.subplots(figsize=(10, 4))
        df[["hit_rate", "mrr", "map", "ndcg", "faithfulness"]].plot.hist(
            alpha=0.6, ax=ax_hist, bins=10
        )
        ax_hist.set_title("Distribuição Histórica das Métricas")
        st.pyplot(fig_hist)
        save_plot_as_image(fig_hist, "histogramas")

        st.subheader("📈 Densidade das Métricas (KDE)")
        fig_kde, ax_kde = plt.subplots(figsize=(10, 4))
        df[["hit_rate", "mrr", "map", "ndcg", "faithfulness"]].plot.kde(ax=ax_kde)
        ax_kde.set_title("Curvas de Densidade Estimada")
        st.pyplot(fig_kde)
        save_plot_as_image(fig_kde, "kde_metricas")

    with tab5:
        st.subheader("🧠 Justificativas do FaithfulnessEvaluator")
        for _, row in df.iterrows():
            with st.expander(f"❓ {row['question']}"):
                st.markdown(f"**🤖 Resposta:** {row['response']}")
                st.markdown(f"**💬 Justificativa:** {row['reasoning']}")
                st.markdown("---")


if __name__ == "__main__":
    main()
