                    items.extend_from_slice(suffix);
                    // The unchanged suffix already contains updates through this baseline.
                    if let Some(checkpoint) = state.history.world_state_checkpoint() {
                        world_state_baseline = WorldStateSnapshot::from(&checkpoint.state);
                    }
