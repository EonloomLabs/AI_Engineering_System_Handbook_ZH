                    // Validate immediately before slicing and replacing the captured prefix.
                    if state.history.history_version() != prefix.generation
                        || state.history.annotated_items().len() < prefix.len
                        || self.services.model_client.auth_owner_generation()
                            != prefix.auth_owner_generation
                    {
                        return false;
                    }
                    let current = state.history.annotated_items();
                    let suffix = &current[prefix.len..];
