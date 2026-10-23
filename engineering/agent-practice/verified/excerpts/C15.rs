                if still_owns_lock {
                    if let Err(err) = reset_memory_workspace_baseline(&memory_root).await {
                        tracing::error!("failed resetting memory workspace baseline: {err}");
                        job::failed(context.as_ref(), &db, &claim, "failed_workspace_commit").await;
                    } else if !job::succeed(
                        context.as_ref(),
                        &db,
                        &claim,
                        new_watermark,
                        &selected_outputs,
                        "succeeded",
                    )
                    .await
                    {
                        tracing::error!(
                            "failed marking global memory consolidation job succeeded after resetting workspace baseline"
                        );
                    } else {
                        drop(phase_two_e2e_timer);
                        context.record_storage_size(&memory_root).await;
                    }
                }
