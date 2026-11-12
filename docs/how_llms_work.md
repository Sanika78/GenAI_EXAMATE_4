

\# How Large Language Models (LLMs) Work



\## 1. What is an LLM?



A Large Language Model (LLM) is an Artificial Intelligence model that understands and generates human-like text.



It is trained using a large amount of text data such as books, articles, websites and documents.



Examples of LLMs include GPT, Gemini and Llama.



\## 2. How does an LLM work?



An LLM works by learning patterns in language and predicting the next most likely token.



A token can be a word, part of a word or a punctuation mark.



The basic process is:



1\. Input: The user enters a question or instruction.

2\. Tokenization: The input is divided into smaller tokens.

3\. Embeddings: Tokens are converted into numerical representations.

4\. Attention: The model identifies relationships between different tokens and understands their context.

5\. Prediction: The model predicts the next token based on what it has learned.

6\. Output: Predicted tokens are combined to generate a response.



\## 3. LLM Workflow Diagram



```mermaid

flowchart TD

&#x20;   A\[User Question] --> B\[Tokenization]

&#x20;   B --> C\[Token Embeddings]

&#x20;   C --> D\[Transformer and Attention]

&#x20;   D --> E\[Next Token Prediction]

&#x20;   E --> F\[Generated Response]

&#x20;   F --> G\[User]

```



\## 4. What is a Transformer?



A Transformer is a neural network architecture used by many modern LLMs.



It uses an attention mechanism to understand relationships between words and their context.



For example:



"The student deposited money in the bank."



Here, the context helps the model understand that bank refers to a financial institution.



\## 5. What is Attention?



Attention helps the model focus on the most relevant words when processing a sentence.



For example:



"Riya gave her book to Priya because she needed it."



Attention helps the model identify relationships between words instead of processing each word independently.



\## 6. What is Prompt Engineering?



Prompt engineering means writing clear instructions or questions to get more relevant responses from an LLM.



Example:



Weak prompt:

"What is Article 21?"



Better prompt:

"Explain Article 21 of the Indian Constitution in simple language with one real-life example."



\## 7. What is RAG?



RAG stands for Retrieval-Augmented Generation.



It combines information retrieval with an LLM.



Instead of answering only from its training knowledge, the application first retrieves relevant information from its own knowledge source and provides it to the LLM.



\### RAG workflow



1\. User asks a question.

2\. The system searches its document collection.

3\. Relevant information is retrieved.

4\. Retrieved information is passed to the LLM.

5\. The LLM generates an answer using that context.



\## 8. How LLMs are useful in SamvidhanSathi



SamvidhanSathi is designed to help users understand the Indian Constitution.



For example:



\- A user asks about Article 21.

\- The application searches its Constitution records.

\- Relevant Article 21 information is retrieved.

\- The LLM can explain the retrieved information in simple language.

\- The application can show the source article to the user.



\## 9. What are Hallucinations?



An LLM hallucination happens when a model generates information that sounds correct but is incorrect or unsupported.



For example, if SamvidhanSathi does not contain information about a particular court case, it should not invent the case details.



To reduce hallucinations, SamvidhanSathi should use relevant retrieved Constitution information and clearly state when the available data cannot answer a question.



\## 10. Conclusion



LLMs help applications understand questions and generate natural-language responses.



In SamvidhanSathi, LLMs can help make constitutional information easier to understand. Combining an LLM with document retrieval can make responses more relevant and grounded in the available Constitution data.



