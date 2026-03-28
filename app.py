import gradio as gr
from baseline import run_baseline

def run_ai(task_id):
    try:
        score = run_baseline(task_id.lower())
        return f"✅ The AI Baseline Agent completed the '{task_id}' task with a score of: {score:.4f}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

iface = gr.Interface(
    fn=run_ai,
    inputs=gr.Dropdown(choices=["easy", "medium", "hard"], label="Select Task Difficulty", value="easy"),
    outputs=gr.Textbox(label="Result"),
    title="Incident Triage OpenEnv Demo",
    description="Run the reference baseline AI agent against the incident triage environment to see its evaluation score."
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
