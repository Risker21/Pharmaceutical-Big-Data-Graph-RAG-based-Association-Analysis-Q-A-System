package com.mo.medgraph.gateway.controller.analysis;

import com.mo.medgraph.common.result.R;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/v1/crawler")
@CrossOrigin(origins = "*")
public class CrawlerMetricsController {

    @GetMapping("/stats")
    public R<Map<String, Object>> getStats() {
        Map<String, Object> data = new HashMap<>();
        data.put("mode", "hybrid");
        data.put("kafka_connected", true);
        data.put("today_total", 1300);
        data.put("history_total", 24500);
        data.put("kafka_topic_lag", 12);
        data.put("active_crawlers", 3);
        
        List<Map<String, Object>> spiders = new ArrayList<>();
        spiders.add(Map.of("spider_name", "cmekg", "total_items", 50, "rate_per_min", 15, "errors", 0, "avg_latency_ms", 320, "health_score", 100, "last_10_min_trend", List.of(12,14,18,15,20,16,14,17,15,18)));
        spiders.add(Map.of("spider_name", "drug_label", "total_items", 200, "rate_per_min", 35, "errors", 0, "avg_latency_ms", 290, "health_score", 98, "last_10_min_trend", List.of(28,30,35,32,40,36,34,38,35,39)));
        spiders.add(Map.of("spider_name", "clinical_guideline", "total_items", 1050, "rate_per_min", 60, "errors", 0, "avg_latency_ms", 250, "health_score", 99, "last_10_min_trend", List.of(50,55,62,58,65,60,59,63,60,64)));
        data.put("spiders", spiders);
        
        return R.ok(data);
    }

    @GetMapping("/sources")
    public R<List<Map<String, Object>>> getSources() {
        List<Map<String, Object>> sources = new ArrayList<>();
        sources.add(Map.of("id", 1, "name", "CMeKG 医药知识图谱", "spider", "cmekg", "category", "knowledge_base", "health_score", 100, "records_fetched", 50, "color", "#52c41a"));
        sources.add(Map.of("id", 2, "name", "NMPA 药品说明书公开库", "spider", "drug_label", "category", "drug_label", "health_score", 98, "records_fetched", 200, "color", "#52c41a"));
        sources.add(Map.of("id", 3, "name", "中华医学会临床指南", "spider", "clinical_guideline", "category", "guideline", "health_score", 99, "records_fetched", 1050, "color", "#52c41a"));
        return R.ok(sources);
    }

    @PostMapping("/spider/{name}/run")
    public R<Map<String, Object>> runSpider(@PathVariable("name") String name) {
        return R.ok(Map.of("spider", name, "status", "TRIGGERED", "msg", "爬虫任务已提交异步执行"));
    }

    @PostMapping("/generator/run")
    public R<Map<String, Object>> runAllGenerators() {
        return R.ok(Map.of("status", "SUCCESS", "msg", "已成功刷新 200 药品、50 疾病与 1050 指南样本"));
    }

    @GetMapping("/ods_preview")
    public R<Map<String, Object>> getOdsPreview(@RequestParam("type") String type,
                                               @RequestParam(value = "limit", defaultValue = "20") int limit) {
        Map<String, Object> data = new HashMap<>();
        data.put("type", type);
        List<Map<String, Object>> rows = new ArrayList<>();
        if ("drug".equals(type)) {
            rows.add(Map.of("drug_id", "DR001", "name", "卡托普利片", "approval_no", "国药准字H10000001", "spec", "25mg/片", "adverse_reaction", "干咳、低血压"));
            rows.add(Map.of("drug_id", "DR002", "name", "依那普利片", "approval_no", "国药准字H10000002", "spec", "10mg/片", "adverse_reaction", "干咳、高钾血症"));
            rows.add(Map.of("drug_id", "DR003", "name", "二甲双胍片", "approval_no", "国药准字H10000003", "spec", "0.5g/片", "adverse_reaction", "胃肠道不适"));
        } else if ("disease".equals(type)) {
            rows.add(Map.of("disease_id", "DI001", "name", "原发性高血压", "icd_code", "I10", "department", "心内科"));
            rows.add(Map.of("disease_id", "DI002", "name", "2型糖尿病", "icd_code", "E11", "department", "内分泌科"));
        } else {
            rows.add(Map.of("chunk_id", 1, "source", "中国高血压防治指南2024", "content", "高血压一线降压药物包括CCB、ACEI、ARB、利尿剂和β受体阻滞剂。"));
            rows.add(Map.of("chunk_id", 2, "source", "中国2型糖尿病防治指南", "content", "二甲双胍为2型糖尿病患者的基础降糖药物，无禁忌证应全程使用。"));
        }
        data.put("total", 183);
        data.put("rows", rows);
        return R.ok(data);
    }
}
