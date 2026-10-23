        if self.persist_rollout_items(&rollout_items).await
            && let Some(revision) = mcp_revision
        {
            self.services
                .executed_tool_calls
                .mark_mcp_attribution_persisted(revision);
        }
        {
            let mut state = self.state.lock().await;
            state.queue_pending_session_start_source(codex_hooks::SessionStartSource::Compact);
        }
        true
