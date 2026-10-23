    assert_eq!(summaries, ["prepared-summary"]);
    assert_eq!(request.requests().len(), 1);
    shutdown(&sess).await;
