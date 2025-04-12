import json
import openai
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_community.tools import TavilySearchResults

# import warnings
# warnings.simplefilter("ignore")

class QueryProcessingAgent:
    def __init__(
        self,
        api_key,
        embedding_model,
        api_model,
        pg_connection_string,
        pg_collection_name,
        pre_agent_prompt,
        top_k_similar,
        outlier_prompt,
        resp_prompt,
        tavily_api_key,
        max_research,
        domains
    ):
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.api_model = api_model
        self.pg_connection_string = pg_connection_string
        self.pg_collection_name = pg_collection_name
        self.pre_agent_prompt = pre_agent_prompt
        self.top_k_similar = top_k_similar
        self.outlier_prompt = outlier_prompt
        self.resp_prompt = resp_prompt
        self.tavily_api_key = tavily_api_key
        self.max_research = max_research
        self.domains = domains


    def pre_agent(self, state):
        question = state.get("question", "")
        print(f"Question: {question}")
        response = openai.ChatCompletion.create(
            model=self.api_model,
            messages=[
                {"role": "system", "content": self.pre_agent_prompt},
                {"role": "user", "content": question},
            ],
            api_key=self.api_key,
        )

        results = response.choices[0].message.content.strip()
        results = json.loads(results)

        return {
            "pre_agent_output": results.get("output", ""),
            "item_name_output": results.get("item_name", "")
        }

        # return {"pre_agent_output": response.choices[0].message.content.strip()}

    def embedding_matcher_agent(self, state):
        query = state.get("pre_agent_output", "")

        db = PGVector(
            connection_string=self.pg_connection_string,
            collection_name=self.pg_collection_name,
            embedding_function=OpenAIEmbeddings(
                model= self.embedding_model, openai_api_key=self.api_key
            ),
        )

        similar = db.similarity_search_with_score(query, k=self.top_k_similar)
        page_contents = [doc.page_content for doc, _ in similar]

        return {"embedding_matcher_agent_output": page_contents}

    def resp_agent(self, state):
        resp_visit = state.get("resp_visit", "") +1
        question = state.get("pre_agent_output", "")
        if question == "no":
            return {"resp_agent_output": self.outlier_prompt}
        else:
            info = state.get("embedding_matcher_agent_output", "")
            system_prompt = self.resp_prompt
            user_prompt = f"""Câu hỏi: {question}
            Thông tin tham khảo: {info}

            Hãy kiểm tra xem tên sản phẩm ở câu hỏi và tên sản phẩm ở thông tin tham khảo có liên quan đến nhau không.

            - Nếu rõ ràng không liên quan, chỉ trả về đúng chuỗi: "incorrect"
            - Nếu có liên quan hoặc nghi ngờ có liên quan, hãy đưa ra phản hồi phù hợp dựa trên thông tin tham khảo. Không thêm lời giải thích."""

            # user_prompt = f"Câu hỏi: {question}\nThông tin tham khảo: {info}\n\nHãy kiểm tra xem tên sản phẩm ở câu hỏi và tên sản phẩm ở thông tin tham khảo có liên quan đến nhau không.\n\n- Nếu không liên quan, chỉ trả về đúng chuỗi: \"incorrect\"\n- Nếu liên quan, hãy đưa ra phản hồi phù hợp dựa trên thông tin tham khảo. Không thêm lời giải thích."
            response = openai.ChatCompletion.create(
                model=self.api_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                api_key=self.api_key,
            )
            return {"resp_agent_output": response.choices[0].message["content"].strip(),
                    "resp_visit" : resp_visit}

    def tavily_search_agent(self, state):
        item_name = state.get("item_name_output", "")
        search_tool = TavilySearchResults(max_results=self.max_research, include_domains=self.domains)
        search_results = search_tool.run(f"Hãy cung cấp url của sản phẩm: {item_name}")
        urls = []
        for i, item in enumerate(search_results, 1):
            urls.append(item.get('url', 'N/A'))

        return {"search_urls_output": urls}

    def response(self, state):
        if state.get("resp_agent_output") != "incorrect":
            output = state.get("resp_agent_output", "")
        else:
            output = None

        return {"resp_agent_output": output}

