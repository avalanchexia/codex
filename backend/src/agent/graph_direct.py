import os
import logging
import json

from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from google.genai import Client

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from agent.direct_genai_client import DirectGenAIClient
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
    run_with_timeout,
)

load_dotenv()

# 检查必需的环境变量
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key is None:
    logger.error("GEMINI_API_KEY 环境变量未设置")
    raise ValueError("GEMINI_API_KEY is not set")
else:
    logger.info("GEMINI_API_KEY 已正确设置")

# 检查 API 密钥格式
if not gemini_api_key.startswith("AIza"):
    logger.warning("GEMINI_API_KEY 格式可能不正确，应以 'AIza' 开头")

# Used for Google Search API
genai_client = Client(api_key=os.getenv("GEMINI_API_KEY"))

def parse_structured_output(text: str, output_type: str):
    """解析结构化输出"""
    try:
        # 尝试从文本中提取 JSON
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            json_text = text[json_start:json_end].strip()
        elif "{" in text and "}" in text:
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            json_text = text[json_start:json_end]
        else:
            raise ValueError("未找到 JSON 格式的输出")
        
        parsed = json.loads(json_text)
        
        if output_type == "SearchQueryList":
            return SearchQueryList(
                query=parsed.get("query", []),
                rationale=parsed.get("rationale", "生成的搜索查询")
            )
        elif output_type == "Reflection":
            return Reflection(
                is_sufficient=parsed.get("is_sufficient", False),
                knowledge_gap=parsed.get("knowledge_gap", ""),
                follow_up_queries=parsed.get("follow_up_queries", [])
            )
        else:
            return parsed
            
    except Exception as e:
        logger.error(f"解析结构化输出失败: {e}")
        logger.error(f"原始文本: {text}")
        # 返回默认值
        if output_type == "SearchQueryList":
            return SearchQueryList(query=["搜索相关信息"], rationale="默认搜索查询")
        elif output_type == "Reflection":
            return Reflection(is_sufficient=True, knowledge_gap="", follow_up_queries=[])
        else:
            return {}

# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """使用直接 GenAI 客户端生成搜索查询"""
    configurable = Configuration.from_runnable_config(config)

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # 使用直接 GenAI 客户端
    llm = DirectGenAIClient(model=configurable.query_generator_model)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    
    # 添加结构化输出指令
    structured_prompt = f"""{formatted_prompt}

请以 JSON 格式返回结果，格式如下：
{{
    "query": ["查询1", "查询2", "查询3"],
    "rationale": "为什么选择这些查询的简要说明"
}}
"""

    # Generate the search queries with a timeout to avoid hanging
    try:
        logger.info("开始生成搜索查询...")
        response_text = run_with_timeout(llm.invoke, structured_prompt, temperature=1.0)
        result = parse_structured_output(response_text, "SearchQueryList")
        logger.info(f"成功生成 {len(result.query)} 个搜索查询")
        return {"query_list": result.query}
    except TimeoutError as e:
        logger.error(f"生成搜索查询超时: {e}")
        raise
    except Exception as e:
        logger.error(f"生成搜索查询时发生错误: {e}")
        raise


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node."""
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """使用直接 GenAI 客户端进行网络搜索"""
    # Configure
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )

    # Uses the google genai client as the langchain client doesn't return grounding metadata
    try:
        logger.info(f"开始网络搜索，查询: {state['search_query']}")
        response = run_with_timeout(
            genai_client.models.generate_content,
            model=configurable.query_generator_model,
            contents=formatted_prompt,
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0,
            },
        )
        logger.info("网络搜索完成")
    except TimeoutError as e:
        logger.error(f"网络搜索超时: {e}")
        raise
    except Exception as e:
        logger.error(f"网络搜索时发生错误: {e}")
        raise
    
    # resolve the urls to short urls for saving tokens and time
    resolved_urls = resolve_urls(
        response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
    )
    # Gets the citations and adds them to the generated text
    citations = get_citations(response, resolved_urls)
    modified_text = insert_citation_markers(response.text, citations)
    sources_gathered = [item for citation in citations for item in citation["segments"]]

    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [modified_text],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """使用直接 GenAI 客户端进行反思分析"""
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model") or configurable.reflection_model

    # 使用直接 GenAI 客户端
    llm = DirectGenAIClient(model=reasoning_model)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
        research_loop_count=state["research_loop_count"],
    )
    
    # 添加结构化输出指令
    structured_prompt = f"""{formatted_prompt}

请以 JSON 格式返回结果，格式如下：
{{
    "is_sufficient": true/false,
    "knowledge_gap": "缺失信息的描述",
    "follow_up_queries": ["后续查询1", "后续查询2"]
}}
"""

    try:
        logger.info("开始反思分析...")
        response_text = run_with_timeout(llm.invoke, structured_prompt, temperature=0)
        result = parse_structured_output(response_text, "Reflection")
        logger.info(f"反思分析完成，是否充分: {result.is_sufficient}, 后续查询: {result.follow_up_queries}")
        return {
            "follow_up_queries": result.follow_up_queries, 
            "is_sufficient": result.is_sufficient,
            "knowledge_gap": result.knowledge_gap,
            "research_loop_count": state["research_loop_count"],
            "number_of_ran_queries": len(state.get("search_query", [])),
        }
    except TimeoutError as e:
        logger.error(f"反思分析超时: {e}")
        raise
    except Exception as e:
        logger.error(f"反思分析时发生错误: {e}")
        raise


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
):
    """Evaluates whether to continue research or finalize the answer."""
    configurable = Configuration.from_runnable_config(config)
    
    # Check if we've reached the maximum number of research loops
    if state.get("research_loop_count", 0) >= configurable.max_research_loops:
        logger.info(f"已达到最大研究循环次数 ({configurable.max_research_loops})，结束研究")
        return "finalize_answer"
    
    # Check if research is sufficient
    if state.get("is_sufficient", False):
        logger.info("研究已充分，结束研究")
        return "finalize_answer"
    
    # Check if there are follow-up queries
    follow_up_queries = state.get("follow_up_queries", [])
    if follow_up_queries and any(q.strip() for q in follow_up_queries):
        logger.info(f"发现 {len(follow_up_queries)} 个后续查询，继续研究")
        # Return Send objects for each follow-up query
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state.get("number_of_ran_queries", 0) + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(follow_up_queries)
        ]
    else:
        logger.info("无后续查询，结束研究")
        return "finalize_answer"


def finalize_answer(state: OverallState, config: RunnableConfig):
    """使用直接 GenAI 客户端生成最终答案"""
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model
    
    # 使用直接 GenAI 客户端
    llm = DirectGenAIClient(model=reasoning_model)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )

    try:
        logger.info("开始生成最终答案...")
        response_text = run_with_timeout(llm.invoke, formatted_prompt, temperature=0)
        logger.info("最终答案生成完成")
        
        return {
            "messages": [
                AIMessage(
                    content=response_text,
                    name="researcher",
                )
            ]
        }
    except TimeoutError as e:
        logger.error(f"生成最终答案超时: {e}")
        raise
    except Exception as e:
        logger.error(f"生成最终答案时发生错误: {e}")
        raise


# Define the graph
def create_graph():
    """创建研究图"""
    graph = StateGraph(OverallState)

    # Add nodes
    graph.add_node("generate_query", generate_query)
    graph.add_node("web_research", web_research)
    graph.add_node("reflection", reflection)
    graph.add_node("finalize_answer", finalize_answer)

    # Add edges
    graph.add_edge(START, "generate_query")
    graph.add_conditional_edges(
        "generate_query",
        continue_to_web_research,
        ["web_research"],
    )
    graph.add_edge("web_research", "reflection")
    graph.add_conditional_edges(
        "reflection",
        evaluate_research,
        ["web_research", "finalize_answer"],
    )
    graph.add_edge("finalize_answer", END)

    return graph.compile() 