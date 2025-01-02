import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud
from pyecharts import options as opts
import streamlit.components.v1 as components
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np


def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        st.error(f"请求 URL 时出错: {e}")
        return ""


def analyze_word_frequency(text):
    words = jieba.lcut(text)
    word_freq = Counter(words)
    return word_freq


def create_wordcloud(word_freq):
    wc = WordCloud()
    wc.add("", [(word, freq) for word, freq in word_freq.items()], word_size_range=[20, 100])
    # 设置微软雅黑字体
    font_path = 'C:\Windows\Fonts\msyh.ttf' if os.name == 'nt' else 'Microsoft YaHei'
    wc.set_global_opts(
        title_opts=opts.TitleOpts(
            title="词云图",
            font_family=font_path
        )
    )
    return wc


def create_chart(word_freq, chart_type):
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    words = [item[0] for item in top_words]
    frequencies = [item[1] for item in top_words]
    if chart_type == "wordcloud":
        return create_wordcloud(word_freq)
    elif chart_type == "bar":
        return px.bar(x=words, y=frequencies, title="柱状图")
    elif chart_type == "line":
        return px.line(x=words, y=frequencies, title="折线图")
    elif chart_type == "pie":
        return px.pie(names=words, values=frequencies, title="饼图")
    elif chart_type == "scatter":
        return px.scatter(x=words, y=frequencies, title="散点图")
    elif chart_type == "heatmap":
        data = np.array([frequencies])
        return px.imshow(data,
                         labels=dict(x="Words", y="Frequency"),
                         x=words,
                         color_continuous_scale='Blues',
                         title="热力图")
    elif chart_type == "boxplot":
        frequencies = list(word_freq.values())
        fig, ax = plt.subplots()
        ax.boxplot(frequencies)
        ax.set_title("箱线图")
        ax.set_xlabel("词频")
        return fig


def main():
    st.title("文本词频分析工具")
    url = st.text_input("请输入 URL")
    if url:
        text = get_text_from_url(url)
        if text:
            word_freq = analyze_word_frequency(text)
            st.subheader("词频分析结果")
            st.write(f"总词数: {len(word_freq)}")

            chart_types = ["wordcloud", "bar", "line", "pie", "scatter", "heatmap", "boxplot"]
            selected_chart = st.selectbox("选择图表类型", chart_types)
            chart = create_chart(word_freq, selected_chart)
            if selected_chart == "wordcloud":
                components.html(chart.render_embed(), height=600)
            elif selected_chart == "boxplot":
                st.pyplot(chart)
            else:
                st.plotly_chart(chart)


if __name__ == "__main__":
    main()