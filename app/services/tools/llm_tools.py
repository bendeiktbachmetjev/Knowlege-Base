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

def auto_score(options, criteria, with_explanations=False):
    """
    Use LLM to estimate scores for each option by each criterion (1-5 scale) for objective criteria.
    For subjective criteria, assign all options a score of 1.
    If with_explanations=True, returns (scores, explanations)
    """
    typical_objective_criteria = {
        "salary", "income", "pay", "money", "earnings", "wage",
        "schedule", "shift", "hours", "workload", "physical", "prestige",
        "demand", "job market", "employment", "growth", "stability",
        "difficulty", "training", "education", "competition"
    }
    scores = []
    explanations = []
    for criterion in criteria:
        if any(obj in criterion.lower() for obj in typical_objective_criteria):
            prompt = (
                f"Evaluate the options by the criterion '{criterion}' on a scale from 1 to 5. "
                f"Options: {', '.join(options)}. "
                "Return only JSON: {\"scores\": [score1, score2, ...], \"explanations\": [\"explanation1\", ...]}"
            )
            response = llm.invoke(prompt)
            import json
            try:
                data = json.loads(response.content)
                crit_scores = data.get("scores", [3 for _ in options])
                crit_expls = data.get("explanations", ["No explanation" for _ in options])
                if not isinstance(crit_scores, list) or len(crit_scores) != len(options):
                    crit_scores = [3 for _ in options]
                if not isinstance(crit_expls, list) or len(crit_expls) != len(options):
                    crit_expls = ["No explanation" for _ in options]
            except Exception:
                crit_scores = [3 for _ in options]
                crit_expls = ["No explanation" for _ in options]
        else:
            crit_scores = [1 for _ in options]
            crit_expls = ["Subjective criterion, all options are equally important" for _ in options]
        scores.append(crit_scores)
        explanations.append(crit_expls)
    # scores: [criterion][option] -> [option][criterion]
    scores_t = [[scores[j][i] for j in range(len(criteria))] for i in range(len(options))]
    explanations_t = [[explanations[j][i] for j in range(len(criteria))] for i in range(len(options))]
    if with_explanations:
        return scores_t, explanations_t
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
        # If user did not specify weights, assign equal weights
        if weights is None or len(weights) != len(criteria):
            weights = [10 for _ in criteria]
        # If user did not specify scores, let GPT generate them
        explanations = None
        if scores is None:
            scores, explanations = auto_score(options, criteria, with_explanations=True)
        result = calculate_decision_matrix(
            options=options,
            criteria=criteria,
            weights=weights,
            scores=scores
        )
        best_option = max(result, key=result.get)
        # Build plain text table with alignment
        col_widths = [max(len(str(x)) for x in ["Option"] + options)]
        for j, crit in enumerate(criteria):
            col_widths.append(max(len(str(crit)), max(len(str(scores[i][j])) for i in range(len(options)))))
        col_widths.append(max(len("Total"), max(len(str(result[opt])) for opt in options)))
        # Header
        header = "Option".ljust(col_widths[0]) + "  "
        for idx, crit in enumerate(criteria):
            header += crit.ljust(col_widths[idx+1]) + "  "
        header += "Total".ljust(col_widths[-1])
        # Rows
        rows = []
        for i, option in enumerate(options):
            row = option.ljust(col_widths[0]) + "  "
            for j in range(len(criteria)):
                row += str(scores[i][j]).ljust(col_widths[j+1]) + "  "
            row += str(result[option]).ljust(col_widths[-1])
            rows.append(row)
        table = header + "\n" + "\n".join(rows)
        # Build explanations
        explanation_text = ""
        if explanations:
            explanation_text = "\nExplanations for each score by criterion and option:\n"
            for j, crit in enumerate(criteria):
                explanation_text += f"- {crit}:\n"
                for i, option in enumerate(options):
                    explanation_text += f"    {option}: {explanations[i][j]}\n"
        return (
            f"Best option: {best_option}\n"
            f"Below is the full decision matrix with numbers for each option and criterion, and the total scores.\n"
            f"{table}\n"
            f"{explanation_text}"
            f"(Always show this table and explanations in the answer!)"
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