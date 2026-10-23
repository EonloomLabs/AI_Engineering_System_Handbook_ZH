        let post_tool_use_payload = if success {
            result
                .as_ref()
                .ok()
                .and_then(|result| result.post_tool_use_payload.clone())
        } else {
            None
        };
