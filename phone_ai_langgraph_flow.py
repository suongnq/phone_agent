import json
import warnings
from typing import TypedDict, List
from langgraph.graph import StateGraph

from phone_ai.query_processing_agent import QueryProcessingAgent
from crawler.crawl_item_detail import ItemDetailCrawler
from utilis.mongo_services import MongoDBServices
from phone_ai.fallback_agent import FallbackAgent
from config import (
    MONGO_URI,
    PG_COLLECTION_NAME,
    PG_CONNECTION_STRING,
    MONGO_URI,
    API_KEY,
    API_MODEL,
    EMBEDDING_MODEL,
    TOP_K_SIMILAR,
    TAVILY_API_KEY,
    DOMAINS,
    MAX_RESEARCH,
)


import warnings
warnings.simplefilter("ignore")

class AgentState(TypedDict):
    question: str
    pre_agent_output: str
    item_name_output: str
    embedding_matcher_agent_output: List[str]
    resp_agent_output: str
    search_urls_output: List[str]
    success_count_output: int
    resp_visit: int


class PhoneAIFlow:
    def __init__(self):
        self.prompts = self._load_prompts()
        self.db_configs, self.selectors = self._load_configs()

        self.query_processing_agent = QueryProcessingAgent(
            API_KEY,
            EMBEDDING_MODEL,
            API_MODEL,
            PG_CONNECTION_STRING,
            PG_COLLECTION_NAME,
            self.prompts["pre_agent_prompt"],
            TOP_K_SIMILAR,
            self.prompts["outlier_prompt"],
            self.prompts["resp_prompt"],
            TAVILY_API_KEY,
            MAX_RESEARCH,
            DOMAINS,
        )

        self.fallback_agent = FallbackAgent(
            API_KEY,
            EMBEDDING_MODEL,
            PG_COLLECTION_NAME,
            PG_CONNECTION_STRING,
            ItemDetailCrawler(),
            MongoDBServices(MONGO_URI),
            self.db_configs,
            self.selectors,
        )

    def _load_prompts(self):
        with open("./config/system_prompts.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_configs(self):
        with open("./config/selectors_config.json", "r") as f:
            selectors = json.load(f)
        with open("config/monggo_db_config.json", "r") as f:
            db_configs = json.load(f)
        return db_configs, selectors

    def _route_from_pre_agent(self, state):
        return "resp_agent" if state.get("pre_agent_output") == "no" else "embedding_matcher_agent"

    def _route_from_resp_agent(self, state):
        return "tavily_search_agent" if (state.get("resp_agent_output") == "incorrect"
                                         and state.get("resp_visit") <= 1) else "response"

    def _route_from_crawl_embed_store_agent(self, state):
        return "response" if state.get("success_count_output") == 0  else "embedding_matcher_agent"

    def main(self, question: str):
        workflow = StateGraph(state_schema=AgentState)

        # Define nodes
        workflow.add_node("pre_agent", self.query_processing_agent.pre_agent)
        workflow.add_node("embedding_matcher_agent", self.query_processing_agent.embedding_matcher_agent)
        workflow.add_node("resp_agent", self.query_processing_agent.resp_agent)
        workflow.add_node("tavily_search_agent", self.query_processing_agent.tavily_search_agent)
        workflow.add_node("crawl_embed_store_agent", self.fallback_agent.crawl_embed_store_agent)
        workflow.add_node("response", self.query_processing_agent.response)

        # Routing logic
        workflow.add_conditional_edges(
            "pre_agent",
            self._route_from_pre_agent,
            {
                "resp_agent": "resp_agent",
                "embedding_matcher_agent": "embedding_matcher_agent",
            },
        )
        workflow.add_edge("embedding_matcher_agent", "resp_agent")
        workflow.add_conditional_edges("resp_agent", self._route_from_resp_agent)
        workflow.add_edge("tavily_search_agent", "crawl_embed_store_agent")
        workflow.add_conditional_edges(
            "crawl_embed_store_agent",
            self._route_from_crawl_embed_store_agent,
            {
                "response": "response",
                "embedding_matcher_agent": "embedding_matcher_agent",
            },
        )


        workflow.set_entry_point("pre_agent")
        graph_app = workflow.compile()

        # Run
        state = {"question": question, "resp_visit": 0}
        result = graph_app.invoke(state)

        print("Answer:")
        print(result.get("resp_agent_output", ""))
        return result.get("resp_agent_output", "")


