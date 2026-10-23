        // Full-history forks preserve the cached prompt prefix and can keep diffing
        // from the parent's durable baseline unless legacy compaction requires rebuilding it.
        RolloutItem::TurnContext(_) | RolloutItem::WorldState(_) => preserve_context_baselines,
        // Child threads inherit model context, not the parent's cumulative usage state.
        RolloutItem::TokenUsageRecord(_) => false,
