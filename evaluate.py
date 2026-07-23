from review_graph import context_node, agent_node, llm
from eval_dataset import EVAL_CASES
import json

def run_agent_on_case(case, use_context=True):
    state = {"diff": case["diff"], "changed_symbol": case.get("changed_symbol", "")}
    if use_context:
        state.update(context_node(state))
    final_state = agent_node(state)
    return final_state["review_comment"]

def judge_review(true_label, agent_comment, has_bug):
    judge_prompt = f"""You are a code review judge. You are evaluating a code reviewer's comment against a known ground truth.

    True Label: {true_label}
    Reviewer's Comment: {agent_comment}
    Does Change Have Bug: {has_bug}

    Please provide two judgments:
    1. caught_bug: Does the reviewer's comment correctly identify the bug or lack thereof? (true/false)
    2. false_positive: If the change has no bug, does the reviewer's comment incorrectly suggest there is a bug? Minor style suggestions do NOT count as false positives (true/false)

    Respond with ONLY a JSON object and nothing else
    """
    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0.0
    )
    text = response.choices[0].message.content
    
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        json_text = text[start:end]
        return json.loads(json_text)
    except Exception as e:
        return {"caught_bug": False, "false_positive": False, "parse_error": True, "raw_response": text, "error": str(e)}

def run_eval(cases, use_context=True):
    results = []
    for case in cases:
        agent_comment = run_agent_on_case(case, use_context=use_context)
        verdict = judge_review(case["true_label"], agent_comment, case["has_bug"])
        results.append({
            "case_name": case["name"],
            "has_bug": case["has_bug"],
            "agent_comment": agent_comment,
            "verdict": verdict
        })
    recall = sum(1 for r in results if r["has_bug"] and r["verdict"].get("caught_bug")) / sum(1 for c in cases if c["has_bug"])
    false_positive_rate = sum(1 for r in results if not r["has_bug"] and r["verdict"].get("false_positive")) / sum(1 for c in cases if not c["has_bug"])
    return results, recall, false_positive_rate

if __name__ == "__main__":
    results, recall, false_positive_rate = run_eval(EVAL_CASES, use_context=True)
    print("Evaluation Results:")
    for result in results:
        print(f"Case: {result['case_name']}")
        print(f"Agent Comment: {result['agent_comment']}")
        print(f"Verdict: {result['verdict']}")
        print("-" * 40)
   
    results_no_context, recall_no_context, false_positive_rate_no_context = run_eval(EVAL_CASES, use_context=False)
    print("\nEvaluation Results without Context:")
    for result in results_no_context:
        print(f"Case: {result['case_name']}")
        print(f"Agent Comment: {result['agent_comment']}")
        print(f"Verdict: {result['verdict']}")
        print("-" * 40)
    
    print(f"{'Condition':<15}{'Recall':<10}{'FP Rate':<10}")
    print("-" * 35)
    print(f"{'Context ON':<15}{recall:<10.2f}{false_positive_rate:<10.2f}")
    print(f"{'Context OFF':<15}{recall_no_context:<10.2f}{false_positive_rate_no_context:<10.2f}")