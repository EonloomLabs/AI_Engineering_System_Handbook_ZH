fn response_item_may_include_external_context(item: &ResponseItem) -> bool {
    matches!(
        item,
        ResponseItem::ToolSearchCall { .. }
            | ResponseItem::ToolSearchOutput { .. }
            | ResponseItem::WebSearchCall { .. }
            | ResponseItem::FunctionCallOutput { call_id: None, .. }
    )
}

pub(crate) async fn mark_thread_memory_mode_polluted_if_external_context(
    sess: &Session,
    turn_context: &TurnContext,
    item: &ResponseItem,
) {
    if !turn_context.config.memories.disable_on_external_context
        || !response_item_may_include_external_context(item)
    {
        return;
    }
    state_db::mark_thread_memory_mode_polluted(
        sess.services.state_db.as_deref(),
        sess.thread_id,
        "record_completed_response_item",
    )
    .await;
}
