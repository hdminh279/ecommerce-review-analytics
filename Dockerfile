FROM bitnamilegacy/spark:3.5.0

USER root

# Set folder HOME to /tmp
ENV HOME=/tmp
ENV XDG_CACHE_HOME=/tmp/hf_cache

# Set folder hugging face
ENV HF_HOME=/tmp/hf_cache
ENV TRANSFORMERS_CACHE=/tmp/hf_cache

RUN pip install --no-cache-dir \
    numpy \
    nltk \
    transformers \
    torch \
    groq \
    scikit-learn \
    pandas \
    spacy \
    datasets \
    accelerate \
    dbt-duckdb

RUN python3 -c "from transformers import pipeline; pipeline('text-classification', model='bhadresh-savani/bert-base-uncased-emotion')" \
    && chmod -R 777 /tmp/hf_cache /tmp

RUN python3 -m spacy download en_core_web_sm

RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data punkt punkt_tab averaged_perceptron_tagger averaged_perceptron_tagger_eng

USER 1001
