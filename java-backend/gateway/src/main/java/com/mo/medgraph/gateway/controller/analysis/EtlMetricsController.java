package com.mo.medgraph.gateway.controller.analysis;

import com.mo.medgraph.common.result.R;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/v1/etl")
@CrossOrigin(origins = "*")
public class EtlMetricsController {

    @GetMapping("/layer-stats")
    public R<Map<String, Object>> getLayerStats() {
        Map<String, Object> data = new HashMap<>();
        data.put("ods", Map.of("rows", 12850, "tables", 3));
        data.put("dwd", Map.of("rows", 12100, "tables", 5));
        data.put("ads", Map.of("rows", 3450, "tables", 4));
        return R.ok(data);
    }

    @GetMapping("/job-history")
    public R<List<Map<String, Object>>> getJobHistory(@RequestParam(value = "limit", defaultValue = "30") int limit) {
        List<Map<String, Object>> list = new ArrayList<>();
        long now = System.currentTimeMillis();
        String[] jobs = {"ODSToDWDPipeline", "Neo4jBulkLoader", "MilvusIndexer", "HBaseBulkLoader", "PageRankCalculator", "ADSPipeline", "LouvainCommunity"};
        int[] inRows = {183, 240, 1050, 183, 310, 520, 212};
        for (int i = 0; i < jobs.length; i++) {
            Map<String, Object> item = new HashMap<>();
            item.put("job_name", jobs[i]);
            item.put("status", "SUCCESS");
            item.put("start_ts", now - (jobs.length - i) * 120000L);
            item.put("end_ts", now - (jobs.length - i) * 120000L + 15000L);
            item.put("duration_ms", 15000L);
            item.put("input_rows", inRows[i]);
            item.put("output_rows", inRows[i]);
            item.put("error_msg", "");
            list.add(item);
        }
        return R.ok(list);
    }

    @GetMapping("/page-rank-top")
    public R<List<Map<String, Object>>> getPageRankTop(@RequestParam(value = "n", defaultValue = "20") int n) {
        List<Map<String, Object>> list = new ArrayList<>();
        list.add(Map.of("node_name", "卡托普利", "node_type", "Drug", "pagerank", 0.084, "community", 1));
        list.add(Map.of("node_name", "高血压", "node_type", "Disease", "pagerank", 0.079, "community", 1));
        list.add(Map.of("node_name", "二甲双胍", "node_type", "Drug", "pagerank", 0.076, "community", 2));
        list.add(Map.of("node_name", "阿司匹林", "node_type", "Drug", "pagerank", 0.072, "community", 1));
        list.add(Map.of("node_name", "冠心病", "node_type", "Disease", "pagerank", 0.068, "community", 1));
        list.add(Map.of("node_name", "华法林", "node_type", "Drug", "pagerank", 0.065, "community", 4));
        list.add(Map.of("node_name", "左氧氟沙星", "node_type", "Drug", "pagerank", 0.062, "community", 3));
        list.add(Map.of("node_name", "奥美拉唑", "node_type", "Drug", "pagerank", 0.058, "community", 4));
        list.add(Map.of("node_name", "布洛芬", "node_type", "Drug", "pagerank", 0.055, "community", 5));
        list.add(Map.of("node_name", "美托洛尔", "node_type", "Drug", "pagerank", 0.052, "community", 1));
        return R.ok(list);
    }

    @GetMapping("/community-size")
    public R<List<Map<String, Object>>> getCommunitySize() {
        List<Map<String, Object>> list = new ArrayList<>();
        list.add(Map.of("community_id", 1, "name", "心血管代谢群", "node_count", 68, "top_drug", "卡托普利", "top_disease", "高血压"));
        list.add(Map.of("community_id", 2, "name", "内分泌代谢群", "node_count", 45, "top_drug", "二甲双胍", "top_disease", "2型糖尿病"));
        list.add(Map.of("community_id", 3, "name", "呼吸抗感染群", "node_count", 39, "top_drug", "左氧氟沙星", "top_disease", "慢性支气管炎"));
        list.add(Map.of("community_id", 4, "name", "消化及抗凝群", "node_count", 32, "top_drug", "奥美拉唑", "top_disease", "胃溃疡"));
        list.add(Map.of("community_id", 5, "name", "镇痛抗炎群", "node_count", 28, "top_drug", "布洛芬", "top_disease", "骨关节炎"));
        return R.ok(list);
    }

    @GetMapping("/ingredient-heatmap")
    public R<List<Map<String, Object>>> getIngredientHeatmap() {
        String[] drugs = {"卡托普利", "依那普利", "二甲双胍", "格列美脲", "阿司匹林", "华法林", "左氧氟沙星", "茶碱", "奥美拉唑", "辛伐他汀", "硝苯地平", "美托洛尔", "氢氯噻嗪", "对乙酰氨基酚", "布洛芬"};
        List<Map<String, Object>> heatmap = new ArrayList<>();
        for (int i = 0; i < drugs.length; i++) {
            for (int j = 0; j < drugs.length; j++) {
                double val = (i == j) ? 1.0 : ((i == 0 && j == 1) ? 0.85 : ((i == 4 && j == 14) ? 0.45 : ((Math.abs(i * 17 + j * 31) % 25) / 100.0)));
                heatmap.add(Map.of("drug_a", drugs[i], "drug_b", drugs[j], "jaccard", val));
            }
        }
        return R.ok(heatmap);
    }

    @GetMapping("/top-contraindications-n")
    public R<List<Map<String, Object>>> getTopContraindications(@RequestParam(value = "n", defaultValue = "50") int n) {
        List<Map<String, Object>> list = new ArrayList<>();
        list.add(Map.of("pair", List.of("华法林", "阿司匹林"), "level", "High", "risk_detail", "两类均影响凝血，联用出血事件升高 2~3 倍，INR 2.0~3.0 严密监测", "case_count", 1240));
        list.add(Map.of("pair", List.of("左氧氟沙星", "茶碱"), "level", "High", "risk_detail", "喹诺酮抑制茶碱CYP1A2代谢，茶碱血药升高2~4倍可致惊厥/心律失常", "case_count", 890));
        list.add(Map.of("pair", List.of("布洛芬", "华法林"), "level", "High", "risk_detail", "NSAIDs损伤胃黏膜+抑制血小板，上消化道大出血RR≈3.2", "case_count", 780));
        list.add(Map.of("pair", List.of("对乙酰氨基酚", "对乙酰氨基酚"), "level", "High", "risk_detail", "同种复方制剂重复使用超4g/日常致急性肝衰竭", "case_count", 650));
        list.add(Map.of("pair", List.of("卡托普利", "螺内酯"), "level", "Medium", "risk_detail", "RAAS双重阻断升血钾，GFR<60时每周监测血钾<5.0mmol/L", "case_count", 410));
        list.add(Map.of("pair", List.of("辛伐他汀", "奥美拉唑"), "level", "Medium", "risk_detail", "CYP3A4弱抑制升辛伐他汀血药，增加横纹肌溶解风险", "case_count", 320));
        return R.ok(list);
    }
}
