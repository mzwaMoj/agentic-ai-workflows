# Import plotly libraries
import ast
import traceback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import time
import ast
from IPython.display import HTML

def execute_plot_code(code, df=None, height=700, width=1000, use_preloaded_data=True):
    """
    Execute the generated Python code and display the interactive Plotly visualization.
    
    Args:
        code (str): Python code to execute (should use Plotly for visualization)
        df (pandas.DataFrame, optional): Custom DataFrame to use in the visualization
        height (int): Height of the plot in pixels
        width (int): Width of the plot in pixels
        use_preloaded_data (bool): Whether to make preloaded data available in the execution context
        
    Returns:
        IPython.display.HTML: Interactive Plotly visualization
    """
    try:
        # Clean the code (remove markdown code block syntax if present)
        if "```python" in code:
            code = code.strip().split("```python", 1)[1]
        elif "```" in code:
            code = code.split("```", 1)[1]
        if "```" in code:  # Handle closing backticks if present
            code = code.split("```", 1)[0]
        code = code.strip()
        
        # Replace fig.show() with a placeholder that we'll handle later
        # This avoids nbformat errors and ensures proper rendering
        code = code.replace("fig.show()", "# fig will be returned instead")
        code = code.replace("fig.show", "# fig.show")
        code = code.replace("plt.show()", "# plt.show() removed")
        code = code.replace("plt.show", "# plt.show")
        
        # Create execution environment with necessary libraries
        exec_globals = {
            "pd": pd,
            "np": np,
            "px": px,
            "go": go,
            "make_subplots": make_subplots,
            "plt": None,
            "pio": pio,
            "HTML": HTML
        }
        
        # Add dataframes to execution environment
        if df is not None:
            exec_globals["df"] = df
        
        # Make preloaded data available if requested
        if use_preloaded_data:
            global_vars = globals()
            if 'df_customer_info' in global_vars:
                exec_globals["df_customer_info"] = global_vars['df_customer_info']
                exec_globals["customer_df"] = global_vars['df_customer_info']
            
            if 'df_transactions' in global_vars:
                exec_globals["df_transactions"] = global_vars['df_transactions']
                exec_globals["transaction_df"] = global_vars['df_transactions']
                exec_globals["df"] = global_vars['df_transactions']
        
        # Execute the code
        exec(compile(code, filename="<string>", mode="exec"), exec_globals)
        
        # Find the figure object
        fig = None
        if 'fig' in exec_globals:
            fig = exec_globals['fig']
        else:
            # Look for any plotly figure
            for var_name, var_value in exec_globals.items():
                if var_name not in ["pd", "np", "px", "go", "make_subplots", "plt", "pio", "HTML",
                                    "df_customer_info", "df_transactions", "customer_df", "transaction_df", "df"]:
                    if hasattr(var_value, 'update_layout'):
                        fig = var_value
                        break
        
        if fig is None:
            return HTML("<div style='color:red; font-weight:bold'>No Plotly figure found. Make sure your code creates a figure named 'fig'.</div>")
        
        # Update layout for consistent sizing
        fig.update_layout(
            height=height,
            width=width,
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        # Configure for notebook display with enhanced interactivity options
        config = {
            'displayModeBar': True,
            'responsive': True,
            'scrollZoom': True,
            'showTips': True,
            'editable': True,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'plot',
                'height': height,
                'width': width,
                'scale': 2
            },
            'modeBarButtonsToAdd': [
                'drawline',
                'drawopenpath',
                'drawclosedpath',
                'drawcircle',
                'drawrect',
                'eraseshape'
            ]
        }
        
        # Convert to HTML with full interactive capabilities
        # Using full_html=False to avoid conflicts with notebook environment
        # include_plotlyjs='cdn' ensures latest Plotly version is used
        html_str = fig.to_html(
            include_plotlyjs='cdn', 
            full_html=False, 
            config=config,
            include_mathjax='cdn'  # Support for mathematical expressions
        )
        
        # Include custom CSS to ensure proper rendering in the notebook
        custom_css = """
        <style>
        .plotly-graph-div .modebar {
            opacity: 0.3;
            transition: opacity 0.3s ease-in-out;
        }
        .plotly-graph-div .modebar:hover {
            opacity: 1;
        }
        .plotly-graph-div {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        </style>
        """
        
        return HTML(f"{custom_css}<div style='width:{width}px; margin:0 auto;'>{html_str}</div>")
        
    except SyntaxError as e:
        return HTML(f"<div style='color:red; font-weight:bold'>Syntax Error: {str(e)}</div><pre>{traceback.format_exc()}</pre>")
    except Exception as e:
        traceback.print_exc()
        return HTML(f"<div style='color:red; font-weight:bold'>Error executing code: {str(e)}</div><pre>{traceback.format_exc()}</pre>")