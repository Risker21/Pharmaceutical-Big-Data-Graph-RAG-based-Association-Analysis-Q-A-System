package com.mo.medgraph.common.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.MediaType;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SseEventBuilder {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final ExecutorService EXECUTOR = Executors.newCachedThreadPool();

    public static SseEmitter createEmitter() {
        return new SseEmitter(60_000L);
    }

    public static SseEmitter createEmitter(long timeoutMs) {
        return new SseEmitter(timeoutMs);
    }

    public static void sendEvent(SseEmitter emitter, String eventName, Object data) {
        try {
            String json = (data instanceof String) ? (String) data : OBJECT_MAPPER.writeValueAsString(data);
            emitter.send(SseEmitter.event()
                    .name(eventName)
                    .data(json, MediaType.APPLICATION_JSON));
        } catch (IOException e) {
            throw new RuntimeException("Failed to send SSE event", e);
        }
    }

    public static void sendTrace(SseEmitter emitter, Object data) {
        sendEvent(emitter, "trace", data);
    }

    public static void sendToken(SseEmitter emitter, String delta) {
        try {
            String wrapped = "{\"delta\":" + OBJECT_MAPPER.writeValueAsString(delta) + "}";
            emitter.send(SseEmitter.event()
                    .name("token")
                    .data(wrapped, MediaType.APPLICATION_JSON));
        } catch (IOException e) {
            throw new RuntimeException("Failed to send token", e);
        }
    }

    public static void sendDone(SseEmitter emitter, Object data) {
        sendEvent(emitter, "done", data);
    }

    public static void complete(SseEmitter emitter) {
        emitter.complete();
    }

    public static void completeWithError(SseEmitter emitter, Throwable t) {
        emitter.completeWithError(t);
    }

    public static ExecutorService getExecutor() {
        return EXECUTOR;
    }
}
