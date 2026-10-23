            // Keep unloaded delivery atomic with publication of a reloaded session.
            let threads = state.threads.read().await;
            if !communication.trigger_turn && !threads.contains_key(&agent_id) {
                let _membership = self.runtime.admit_start()?;
                self.runtime.ensure_agent_known(agent_id)?;
                let submission_id = uuid::Uuid::now_v7().to_string();
                self.runtime.mailboxes.enqueue(
                    agent_id,
                    Some(submission_id.clone()),
                    vec![crate::PendingAgentMessage::new(communication, delivery)],
                )?;
