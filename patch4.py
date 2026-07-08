import sys

with open('src/awr2944_dca/mmws/failure_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = '''            elif state.current_stage == "failed":
                report.detected_failure_type = "guided_workflow_failed"'''

new_logic = '''            elif state.current_stage == "failed":
                report.detected_failure_type = "guided_workflow_failed"
                # Check for OptionInfo summary bug
                if any("OptionInfo" in err for err in state.errors):
                    report.detected_failure_type = "guided_summary_failed"
                    report.likely_root_cause = "CLI OptionInfo leak into internal implementation."
                    report.recommended_next_action = "run summarize-session/record-validation after fixing CLI OptionInfo leak; do not rerun firmware/config blindly."
                # Check for watch_run mismatch
                elif any("timed out" in err for err in state.errors):
                    # Check if actual result json says success
                    from .post_connect import load_run_result
                    if report.run_id:
                        res = load_run_result(report.run_id, probe_dir=probe_dir)
                        if res.exists and res.success:
                            report.detected_failure_type = "guided_watch_result_mismatch"'''

content = content.replace(old_logic, new_logic)

with open('src/awr2944_dca/mmws/failure_report.py', 'w', encoding='utf-8') as f:
    f.write(content)