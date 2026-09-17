package com.mo.medgraph.gateway.controller.chat;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import java.io.IOException;
import java.util.concurrent.Executors;

@RestController
@RequestMapping("/api/v1/chat")
@CrossOrigin(origins = "*")
public class ChatStreamController {

    private final WebClient webClient = WebClient.builder().baseUrl("http://localhost:8000").build();

    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamChat(@RequestParam("query") String query,
                                 @RequestParam(value = "sessionId", required = false) String sessionId) {
        SseEmitter emitter = new SseEmitter(180000L);
        
        Executors.newSingleThreadExecutor().execute(() -> {
            try {
                webClient.get()
                    .uri(uriBuilder -> uriBuilder
                        .path("/api/v1/chat/stream")
                        .queryParam("query", query)
                        .queryParam("sessionId", sessionId != null ? sessionId : "default")
                        .build())
                    .accept(MediaType.TEXT_EVENT_STREAM)
                    .retrieve()
                    .bodyToFlux(String.class)
                    .doOnNext(data -> {
                        try {
                            emitter.send(SseEmitter.event().data(data));
                        } catch (IOException e) {
                            emitter.completeWithError(e);
                        }
                    })
                    .doOnComplete(emitter::complete)
                    .doOnError(emitter::completeWithError)
                    .subscribe();
            } catch (Exception e) {
                // Mock Fallback if RAG Python service is not running
                try {
                    emitter.send(SseEmitter.event().name("trace").data("{\"entities\":[\"高血压\",\"卡托普利\"],\"graph_edges\":[{\"from\":\"卡托普利\",\"to\":\"高血压\",\"rel\":\"治疗\"}]}"));
                    emitter.send(SseEmitter.event().name("token").data("{\"delta\":\"根据知识图谱与临床指南检索结果：针对您的咨询，卡托普利适用于高血压治疗，需遵医嘱规范用药。\"}"));
                    emitter.send(SseEmitter.event().name("done").data("{\"status\":\"success\",\"total_tokens\":45}"));
                    emitter.complete();
                } catch (IOException ex) {
                    emitter.completeWithError(ex);
                }
            }
        });
        
        return emitter;
    }
}
