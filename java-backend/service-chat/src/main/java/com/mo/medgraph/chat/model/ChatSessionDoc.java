package com.mo.medgraph.chat.model;
import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class ChatSessionDoc {
    private String id;
    private String sessionId;
    private String userId;
    private List<Map<String, Object>> messages;
    private long createdAt;
}
