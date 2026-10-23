pub(crate) fn build_prompt(
    input: Vec<ResponseItem>,
    step_context: &StepContext,
    base_instructions: BaseInstructions,
    incremental_tools: bool,
) -> Prompt {
    let turn_context = &step_context.turn;
    Prompt {
        input,
        tools: if incremental_tools {
            Arc::default()
        } else {
            step_context.tool_router.model_visible_specs()
        },
        parallel_tool_calls: true,
        base_instructions: if incremental_tools {
            BaseInstructions {
                text: String::new(),
                provenance: None,
            }
        } else {
            base_instructions
        },
        output_schema: turn_context.final_output_json_schema.clone(),
        output_schema_strict: !crate::guardian::is_basic_session_source(
            &turn_context.session_source,
        ),
        cyber_access_program: turn_context.cyber_access_program,
    }
}
