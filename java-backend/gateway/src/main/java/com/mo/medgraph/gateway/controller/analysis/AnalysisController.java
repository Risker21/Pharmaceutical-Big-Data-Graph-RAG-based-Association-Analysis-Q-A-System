package com.mo.medgraph.gateway.controller.analysis;

import com.mo.medgraph.common.result.R;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/v1/analysis")
@CrossOrigin(origins = "*")
public class AnalysisController {

    @GetMapping("/chat-full")
    public R<Map<String, Object>> getChatFull(
            @RequestParam(value = "from", required = false) String from,
            @RequestParam(value = "to", required = false) String to) {
        
        Map<String, Object> data = new HashMap<>();
        data.put("total_sessions", 1280);
        data.put("total_messages", 4860);
        data.put("total_tokens_used", 1720000);
        data.put("avg_response_ms", 680);
        data.put("cache_hit_rate", 0.38);
        data.put("rate_limit_blocked", 18);
        data.put("avg_hop_count_per_trace", 1.85);
        data.put("avg_chunks_per_retrieval", 2.6);

        List<Map<String, Object>> trend = new ArrayList<>();
        trend.add(Map.of("date", "2026-09-10", "sessions", 120, "tokens", 156000));
        trend.add(Map.of("date", "2026-09-11", "sessions", 145, "tokens", 182000));
        trend.add(Map.of("date", "2026-09-12", "sessions", 160, "tokens", 215000));
        trend.add(Map.of("date", "2026-09-13", "sessions", 190, "tokens", 258000));
        trend.add(Map.of("date", "2026-09-14", "sessions", 210, "tokens", 290000));
        trend.add(Map.of("date", "2026-09-15", "sessions", 245, "tokens", 334000));
        data.put("daily_trend", trend);

        List<Map<String, Object>> intents = new ArrayList<>();
        intents.add(Map.of("intent", "配伍禁忌核验", "count", 1850));
        intents.add(Map.of("intent", "不良反应咨询", "count", 1240));
        intents.add(Map.of("intent", "指南方案推荐", "count", 980));
        intents.add(Map.of("intent", "用法用量核查", "count", 520));
        intents.add(Map.of("intent", "通用医学问诊", "count", 270));
        data.put("intent_distribution", intents);

        List<Map<String, Object>> topQuestions = new ArrayList<>();
        topQuestions.add(Map.of("query", "卡托普利引起干咳能吃吗", "count", 320));
        topQuestions.add(Map.of("query", "华法林和阿司匹林能一起吃吗", "count", 290));
        topQuestions.add(Map.of("query", "左氧氟沙星和茶碱有冲突吗", "count", 240));
        topQuestions.add(Map.of("query", "二甲双胍降糖用量注意", "count", 190));
        topQuestions.add(Map.of("query", "布洛芬与降压药同服风险", "count", 160));
        topQuestions.add(Map.of("query", "高血压合并糖尿病选什么药", "count", 140));
        data.put("top_asked_questions", topQuestions);

        List<Map<String, Object>> qpsData = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            qpsData.add(Map.of("time", "19:" + (20 + i), "passed_qps", 18 + (i % 5), "blocked_qps", (i % 3 == 0) ? 2 : 0));
        }
        data.put("qps_timeline", qpsData);

        List<Map<String, Object>> recentLogs = new ArrayList<>();
        recentLogs.add(Map.of(
            "time", "19:28:10", "user", "admin", "query", "高血压合并干咳能吃卡托普利吗？",
            "intent", "ADVERSE_REACTION", "response_ms", 620, "tokens", 345, "cache_hit", true,
            "entities", List.of("高血压", "干咳", "卡托普利"),
            "graph_paths", List.of("卡托普利 -> 常见副作用 -> 干咳")
        ));
        recentLogs.add(Map.of(
            "time", "19:26:45", "user", "user", "query", "华法林与阿司匹林同服有何风险？",
            "intent", "DRUG_INTERACTION", "response_ms", 710, "tokens", 412, "cache_hit", false,
            "entities", List.of("华法林", "阿司匹林"),
            "graph_paths", List.of("华法林 -> 高危相互作用 -> 阿司匹林")
        ));
        recentLogs.add(Map.of(
            "time", "19:24:12", "user", "admin", "query", "2型糖尿病初发患者用药方案",
            "intent", "TREATMENT_PLAN", "response_ms", 580, "tokens", 380, "cache_hit", true,
            "entities", List.of("2型糖尿病", "二甲双胍"),
            "graph_paths", List.of("二甲双胍 -> 一线治疗 -> 2型糖尿病")
        ));
        data.put("recent_logs", recentLogs);

        return R.ok(data);
    }

    @PostMapping("/generate-demo")
    public R<Map<String, Object>> generateDemo() {
        return R.ok(Map.of("status", "SUCCESS", "msg", "已成功注入 1 个月模拟问答与数仓监控演示数据"));
    }
}
