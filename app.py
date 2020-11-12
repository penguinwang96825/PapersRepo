import streamlit as st
import streamlit.components.v1 as components


def main():
    HtmlFile = open("index.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code)


if __name__ == "__main__":
    main()