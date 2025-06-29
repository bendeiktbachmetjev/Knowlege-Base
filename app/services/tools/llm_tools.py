from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from app.services.core.retrieval import AdvancedRetriever
from app.services.core.bmi import calculate_bmi
from app.services.core.quote import get_quote
from app.services.core.decision_matrix import calculate_decision_matrix
from langchain_openai import ChatOpenAI
import os

# Retrieval Tool
class RetrievalInput(BaseModel):
    query: str = Field(..., description="User's question for knowledge base search.")

def retrieval_tool_func(input: RetrievalInput = None, **kwargs) -> str:
    # Support both input object and direct keyword arguments
    if input is not None:
        query = input.query
    else:
        query = kwargs.get("query")
    retriever = AdvancedRetriever()
    result = retriever.retrieve(query)
    if result.not_found or not result.chunks:
        return "No relevant information found in the knowledge base."
    return '\n\n'.join([f"Source: {chunk.source}, Page: {chunk.page}\n{chunk.text}" for chunk in result.chunks])

retrieval_tool = StructuredTool.from_function(
    func=retrieval_tool_func,
    name="knowledge_base_search",
    description="Use this tool to answer questions that require information from the knowledge base (PDF books). Returns relevant excerpts with sources and pages.",
    args_schema=RetrievalInput
)

# BMI Tool
class BMIInput(BaseModel):
    weight_kg: float = Field(..., description="Weight in kilograms.")
    height_cm: float = Field(..., description="Height in centimeters.")

def bmi_tool_func(input: BMIInput) -> str:
    try:
        bmi = calculate_bmi(input.weight_kg, input.height_cm)
        return f"BMI: {bmi}"
    except Exception as e:
        return f"Error: {str(e)}"

bmi_tool = StructuredTool.from_function(
    func=bmi_tool_func,
    name="bmi_calculator",
    description="Calculate BMI. Provide weight_kg and height_cm. Returns BMI value.",
    args_schema=BMIInput
)

# Quote Tool
class QuoteInput(BaseModel):
    pass  # No input required

def quote_tool_func(input: QuoteInput = None) -> str:
    return get_quote()

quote_tool = StructuredTool.from_function(
    func=quote_tool_func,
    name="motivational_quote",
    description="Get a random motivational quote. No input required.",
    args_schema=QuoteInput
)

# Decision Matrix Tool
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

class DecisionMatrixInput(BaseModel):
    options: list[str] = Field(..., description="List of options to choose from.")
    criteria: list[str] = Field(..., description="List of criteria for evaluation.")
    weights: list[float] = Field(..., description="List of weights for each criterion.")
    scores: list[list[float]] | None = Field(None, description="Matrix of scores: each row is an option, each column is a criterion. If not provided, the agent will estimate scores automatically.")

def auto_score(options, criteria):
    """
    Use LLM to estimate scores for each option by each criterion (1-5 scale) for objective criteria.
    For subjective criteria, assign all options a score of 1.
    """
    typical_objective_criteria = {
        "salary", "income", "pay", "money", "earnings", "wage",
        "schedule", "shift", "hours", "workload", "physical", "prestige",
        "demand", "job market", "employment", "growth", "stability",
        "difficulty", "training", "education", "competition"
    }
    scores = []
    for criterion in criteria:
        # Определяем, объективный ли критерий
        if any(obj in criterion.lower() for obj in typical_objective_criteria):
            # Objective: спросить LLM оценки для всех опций по этому критерию
            prompt = (
                f"Оцени специальности по критерию '{criterion}' по шкале от 1 до 5. "
                f"Варианты: {', '.join(options)}. "
                "Верни только JSON: [score1, score2, ...] — по порядку опций."
            )
            response = llm.invoke(prompt)
            import json
            try:
                crit_scores = json.loads(response.content)
                if not isinstance(crit_scores, list) or len(crit_scores) != len(options):
                    crit_scores = [3 for _ in options]
            except Exception:
                crit_scores = [3 for _ in options]
        else:
            # Subjective: всем по 1
            crit_scores = [1 for _ in options]
        scores.append(crit_scores)
    # scores: [criterion][option] -> нужно транспонировать в [option][criterion]
    scores_t = [[scores[j][i] for j in range(len(criteria))] for i in range(len(options))]
    return scores_t

def decision_matrix_tool_func(input: DecisionMatrixInput = None, **kwargs) -> str:
    try:
        if input is not None:
            options = input.options
            criteria = input.criteria
            weights = input.weights
            scores = input.scores
        else:
            options = kwargs.get("options")
            criteria = kwargs.get("criteria")
            weights = kwargs.get("weights")
            scores = kwargs.get("scores")
        if weights is None or len(weights) != len(criteria):
            weights = [10 for _ in criteria]
        if scores is None:
            scores = auto_score(options, criteria)
        result = calculate_decision_matrix(
            options=options,
            criteria=criteria,
            weights=weights,
            scores=scores
        )
        best_option = max(result, key=result.get)
        # Формируем подробную таблицу с заголовками
        table = "| Option | " + " | ".join(criteria) + " | Total |\n"
        table += "|" + "---|" * (len(criteria) + 2) + "\n"
        for i, option in enumerate(options):
            score_list = scores[i]
            total = result[option]
            table += f"| {option} | " + " | ".join(str(s) for s in score_list) + f" | {total} |\n"
        # Явная инструкция для LLM: не убирай таблицу!
        return (
            f"Best option: {best_option}\n"
            f"Below is the full decision matrix with numbers for each option and criterion, and the total scores.\n"
            f"{table}"
            f"(Always show this table in the answer!)"
        )
    except Exception as e:
        return f"Error: {str(e)}"

decision_matrix_tool = StructuredTool.from_function(
    func=decision_matrix_tool_func,
    name="decision_matrix",
    description="Calculate a weighted decision matrix. Provide options, criteria, weights, and scores. Returns the best option(s) based on your criteria.",
    args_schema=DecisionMatrixInput
)

# List of all tools for the agent
all_tools = [retrieval_tool, bmi_tool, quote_tool, decision_matrix_tool] 