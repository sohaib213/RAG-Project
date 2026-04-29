system_prompt = """
You are a helpful assistant that answers questions based only on the documents provided to you.
If the answer is not in the documents, say you don't know.
Do not make up any information.
"""

document_prompt = """
## Document No: {doc_num}
### Content:
{text}
"""

footer_prompt = """
Based only on the documents above, please answer the following question clearly and concisely.
"""