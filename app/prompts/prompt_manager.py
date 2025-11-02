import mlflow
from app.prompts import (
   prompt_agent_router,
   prompt_agent_sql_analysis, 
   prompt_agent_final_response,
   prompt_agent_plot,
   prompt_agent_table_router,
   prompt_agent_products
)

# system_prompt_router = mlflow.genai.register_prompt(
#     name="prompt_agent_router",
#     template=prompt_agent_router(),
#     commit_message="added banking products agent",
# )
# system_prompt_sql_analysis = mlflow.genai.register_prompt(
#     name="prompt_agent_sql_analysis",
#     template=prompt_agent_sql_analysis(),
#     commit_message="Initial version of prompt_agent_sql_analysis",
# )
# system_prompt_final_response = mlflow.genai.register_prompt(
#     name="prompt_agent_final_response",
#     template=prompt_agent_final_response(),
#     commit_message="Initial version of prompt_agent_final_response",
# )
# system_prompt_plot = mlflow.genai.register_prompt(
#     name="prompt_agent_plot",
#     template=prompt_agent_plot(),
#     commit_message="Initial version of prompt_agent_plot",
# )
# system_prompt_table_router = mlflow.genai.register_prompt(
#     name="prompt_agent_table_router",
#     template=prompt_agent_table_router(),
#     commit_message="Initial version of prompt_agent_table_router",
# )

system_prompt_products = mlflow.genai.register_prompt(
    name="prompt_agent_products",
    template=prompt_agent_products(),
    commit_message="Added products directly into prompts",
)

# then run the following to load the prompts into the MLflow model registry:
# & "..\venv\Scripts\python.exe" -m app.prompts.prompt_manager